"""
TD2 Watchdog — a Discord bot for Train Driver 2 (td2.info.pl).

A user picks a currently occupied dispatcher station via /watch and the bot
sends them a DM as soon as that station drops off the "online" list, i.e. the
dispatcher seat becomes free.

API used:
  https://api.td2.info.pl/?method=getStationsOnline
      -> list of dispatcher stations currently online / occupied.

The bot only needs to track whether a chosen station still appears as online.
"""

import asyncio
import json
import logging
import os
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "https://api.td2.info.pl/?method=getStationsOnline"

# How often (seconds) to poll the API.
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "30"))

# A station must be missing this many consecutive polls before we notify.
# Guards against brief API hiccups producing false "now free" alerts.
MISS_THRESHOLD = int(os.getenv("MISS_THRESHOLD", "2"))

# Treat a station as occupied only when isOnline == 1. If it is in the list
# but isOnline == 0, it is considered effectively free.
REQUIRE_IS_ONLINE = os.getenv("REQUIRE_IS_ONLINE", "true").lower() == "true"

# Discord dropdowns allow at most 25 options.
MAX_SELECT_OPTIONS = 25

# Where to store the watches file. Override with DATA_DIR (e.g. a Docker volume).
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).parent))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATA_FILE = DATA_DIR / "watches.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("td2-watchdog")


# --------------------------------------------------------------------------- #
# Persistent watch storage
# --------------------------------------------------------------------------- #
class WatchStore:
    """In-memory list of watches, persisted to a JSON file.

    A watch is a dict:
        {
            "user_id": int,
            "station_hash": str,
            "station_name": str,
            "region": str,
            "misses": int,        # consecutive polls the station was absent
        }
    """

    def __init__(self, path: Path):
        self.path = path
        self.watches: list[dict] = []
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self.watches = json.loads(self.path.read_text(encoding="utf-8"))
                for w in self.watches:
                    w.setdefault("misses", 0)
                log.info("Loaded %d watch(es) from %s", len(self.watches), self.path.name)
            except (json.JSONDecodeError, OSError) as exc:
                log.warning("Could not read %s: %s", self.path.name, exc)
                self.watches = []

    def save(self) -> None:
        try:
            self.path.write_text(
                json.dumps(self.watches, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            log.warning("Could not write %s: %s", self.path.name, exc)

    def add(self, user_id: int, station_hash: str, station_name: str, region: str) -> bool:
        """Add a watch. Returns False if the user already watches this station."""
        for w in self.watches:
            if w["user_id"] == user_id and w["station_hash"] == station_hash:
                return False
        self.watches.append({
            "user_id": user_id,
            "station_hash": station_hash,
            "station_name": station_name,
            "region": region,
            "misses": 0,
        })
        self.save()
        return True

    def remove(self, user_id: int, station_hash: str) -> bool:
        before = len(self.watches)
        self.watches = [
            w for w in self.watches
            if not (w["user_id"] == user_id and w["station_hash"] == station_hash)
        ]
        changed = len(self.watches) != before
        if changed:
            self.save()
        return changed

    def for_user(self, user_id: int) -> list[dict]:
        return [w for w in self.watches if w["user_id"] == user_id]


# --------------------------------------------------------------------------- #
# API helpers
# --------------------------------------------------------------------------- #
async def fetch_stations(session: aiohttp.ClientSession) -> list[dict]:
    """Return the raw list of station dicts from the API."""
    async with session.get(API_URL, timeout=aiohttp.ClientTimeout(total=20)) as resp:
        resp.raise_for_status()
        data = await resp.json(content_type=None)
    if not data.get("success"):
        raise RuntimeError(f"API returned success=false: {data!r}")
    return data.get("message", [])


def is_occupied(station: dict) -> bool:
    """Whether a station entry counts as currently occupied."""
    if REQUIRE_IS_ONLINE:
        return station.get("isOnline") == 1
    return True


def occupied_stations(raw: list[dict]) -> list[dict]:
    """Filter + sort the occupied stations for display."""
    occ = [s for s in raw if is_occupied(s)]
    occ.sort(key=lambda s: (s.get("stationName") or "").lower())
    return occ


def active_hashes(raw: list[dict]) -> set[str]:
    """Set of station hashes that are currently occupied."""
    return {s["stationHash"] for s in raw if is_occupied(s)}


# --------------------------------------------------------------------------- #
# Discord UI components
# --------------------------------------------------------------------------- #
class StationSelect(discord.ui.Select):
    def __init__(self, stations: list[dict]):
        options = [
            discord.SelectOption(
                label=(s.get("stationName") or "Unknown")[:100],
                value=s["stationHash"],
                description=(
                    f"{s.get('currentUsers', 0)}/{s.get('maxUsers', 0)} players"
                    f" · {s.get('region', '?')}"
                )[:100],
            )
            for s in stations[:MAX_SELECT_OPTIONS]
        ]
        super().__init__(
            placeholder="Select a station to watch…",
            min_values=1,
            max_values=1,
            options=options,
        )
        # hash -> (name, region) lookup for the chosen option
        self._lookup = {
            s["stationHash"]: (s.get("stationName") or "Unknown", s.get("region", "?"))
            for s in stations
        }

    async def callback(self, interaction: discord.Interaction):
        station_hash = self.values[0]
        name, region = self._lookup[station_hash]
        added = interaction.client.store.add(
            interaction.user.id, station_hash, name, region
        )
        if added:
            msg = (
                f"✅ Now watching **{name}**.\n"
                f"I'll send you a DM as soon as this station becomes free.\n"
                f"_Make sure your DMs are open so I can reach you._"
            )
        else:
            msg = f"ℹ️ You're already watching **{name}**."
        await interaction.response.edit_message(content=msg, view=None)


class StationSelectView(discord.ui.View):
    def __init__(self, stations: list[dict], timeout: float = 120):
        super().__init__(timeout=timeout)
        self.add_item(StationSelect(stations))


class UnwatchSelect(discord.ui.Select):
    def __init__(self, watches: list[dict]):
        options = [
            discord.SelectOption(
                label=(w["station_name"])[:100],
                value=w["station_hash"],
                description=f"region: {w.get('region', '?')}"[:100],
            )
            for w in watches[:MAX_SELECT_OPTIONS]
        ]
        super().__init__(
            placeholder="Select a station to stop watching…",
            min_values=1,
            max_values=1,
            options=options,
        )
        self._names = {w["station_hash"]: w["station_name"] for w in watches}

    async def callback(self, interaction: discord.Interaction):
        station_hash = self.values[0]
        name = self._names.get(station_hash, "that station")
        removed = interaction.client.store.remove(interaction.user.id, station_hash)
        msg = (
            f"🗑️ Stopped watching **{name}**."
            if removed
            else f"ℹ️ You weren't watching **{name}**."
        )
        await interaction.response.edit_message(content=msg, view=None)


class UnwatchView(discord.ui.View):
    def __init__(self, watches: list[dict], timeout: float = 120):
        super().__init__(timeout=timeout)
        self.add_item(UnwatchSelect(watches))


# --------------------------------------------------------------------------- #
# Bot
# --------------------------------------------------------------------------- #
class WatchdogBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()  # slash commands need no privileged intents
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.store = WatchStore(DATA_FILE)
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        await self.tree.sync()
        self.poll_loop.start()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await super().close()

    async def on_ready(self):
        log.info("Logged in as %s (id: %s)", self.user, self.user.id)
        log.info("Polling every %ss · miss threshold %s", POLL_INTERVAL, MISS_THRESHOLD)

    # ----------------------------------------------------------------- #
    # Background polling
    # ----------------------------------------------------------------- #
    @tasks.loop(seconds=1)  # interval set dynamically in before_loop
    async def poll_loop(self):
        if not self.store.watches:
            return
        try:
            raw = await fetch_stations(self.session)
        except Exception as exc:  # noqa: BLE001 — keep the loop alive
            log.warning("Poll failed: %s", exc)
            return

        active = active_hashes(raw)
        freed = []  # (watch, ) entries to notify and remove

        for w in self.store.watches:
            if w["station_hash"] in active:
                w["misses"] = 0
            else:
                w["misses"] += 1
                if w["misses"] >= MISS_THRESHOLD:
                    freed.append(w)

        for w in freed:
            await self._notify_free(w)
            self.store.remove(w["user_id"], w["station_hash"])

        if freed:
            self.store.save()

    @poll_loop.before_loop
    async def before_poll(self):
        await self.wait_until_ready()
        self.poll_loop.change_interval(seconds=POLL_INTERVAL)

    async def _notify_free(self, watch: dict):
        try:
            user = self.get_user(watch["user_id"]) or await self.fetch_user(watch["user_id"])
            await user.send(
                f"🟢 **{watch['station_name']}** is now free!\n"
                f"The dispatcher seat is no longer occupied — it's yours to take."
            )
            log.info("Notified user %s that %s is free", watch["user_id"], watch["station_name"])
        except discord.Forbidden:
            log.warning("Cannot DM user %s (DMs closed)", watch["user_id"])
        except Exception as exc:  # noqa: BLE001
            log.warning("Failed to notify user %s: %s", watch["user_id"], exc)


bot = WatchdogBot()


# --------------------------------------------------------------------------- #
# Slash commands
# --------------------------------------------------------------------------- #
@bot.tree.command(name="watch", description="Watch a currently occupied station and get a DM when it's free.")
@app_commands.describe(search="Optional: filter the station list by name.")
async def watch(interaction: discord.Interaction, search: str | None = None):
    await interaction.response.defer(ephemeral=True, thinking=True)
    try:
        raw = await fetch_stations(bot.session)
    except Exception as exc:  # noqa: BLE001
        await interaction.followup.send(f"⚠️ Couldn't reach the TD2 API: {exc}", ephemeral=True)
        return

    stations = occupied_stations(raw)
    if search:
        s = search.lower()
        stations = [st for st in stations if s in (st.get("stationName") or "").lower()]

    if not stations:
        hint = " matching your search" if search else ""
        await interaction.followup.send(
            f"No occupied stations found{hint} right now.", ephemeral=True
        )
        return

    note = ""
    if len(stations) > MAX_SELECT_OPTIONS:
        note = (
            f"\n_Showing the first {MAX_SELECT_OPTIONS} of {len(stations)} stations. "
            f"Use `/watch search:<name>` to narrow it down._"
        )

    await interaction.followup.send(
        content=f"**{len(stations)}** station(s) currently occupied. Pick one:{note}",
        view=StationSelectView(stations),
        ephemeral=True,
    )


@bot.tree.command(name="watching", description="Show the stations you're currently watching.")
async def watching(interaction: discord.Interaction):
    watches = bot.store.for_user(interaction.user.id)
    if not watches:
        await interaction.response.send_message(
            "You're not watching any stations. Use `/watch` to add one.", ephemeral=True
        )
        return
    lines = "\n".join(f"• **{w['station_name']}** ({w.get('region', '?')})" for w in watches)
    await interaction.response.send_message(
        f"You're watching **{len(watches)}** station(s):\n{lines}", ephemeral=True
    )


@bot.tree.command(name="unwatch", description="Stop watching one of your stations.")
async def unwatch(interaction: discord.Interaction):
    watches = bot.store.for_user(interaction.user.id)
    if not watches:
        await interaction.response.send_message(
            "You're not watching any stations.", ephemeral=True
        )
        return
    await interaction.response.send_message(
        content="Which station should I stop watching?",
        view=UnwatchView(watches),
        ephemeral=True,
    )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main():
    if not TOKEN:
        raise SystemExit(
            "DISCORD_TOKEN is not set. Copy .env.example to .env and add your bot token."
        )
    bot.run(TOKEN)


if __name__ == "__main__":
    main()

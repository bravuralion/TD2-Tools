# TD2 Watchdog

A Discord bot for **Train Driver 2** (td2.info.pl). Pick a dispatcher station
that is currently occupied, and the bot will DM you the moment that station
becomes free.

## How it works

The bot polls the public API every 30 seconds:

```
https://api.td2.info.pl/?method=getStationsOnline
```

This returns every dispatcher station that is currently online/occupied. When a
station you're watching no longer appears as occupied, the bot sends you a
direct message. To avoid false alarms from brief API hiccups, a station must be
absent for two consecutive polls (configurable) before you're notified.

## Commands

| Command | Description |
|---------|-------------|
| `/watch [search]` | Shows a dropdown of currently occupied stations. Pick one to watch. Optional `search` filters by name. |
| `/watching` | Lists the stations you're currently watching. |
| `/unwatch` | Pick one of your watched stations to stop watching. |

The bot notifies you via **direct message**, so keep your DMs open for this
server (Privacy Settings → "Allow direct messages from server members").

## Setup

1. **Create the bot application**
   - Go to <https://discord.com/developers/applications> → *New Application*.
   - Under *Bot*, click *Add Bot* and copy the **token**.
   - No privileged intents are required (the bot only uses slash commands).

2. **Invite the bot to your server**
   - Under *OAuth2 → URL Generator*, select scopes `bot` and
     `applications.commands`.
   - Bot permissions: `Send Messages` is enough. Open the generated URL and
     add the bot to your server.

3. **Install and configure**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate

   pip install -r requirements.txt
   cp .env.example .env        # then edit .env and paste your token
   ```

4. **Run**
   ```bash
   python bot.py
   ```

   Slash commands are registered globally on startup and may take a few minutes
   to appear in Discord the first time.

## Run with Docker

The bot ships with a `Dockerfile` and `docker-compose.yml`. Watches are stored
in a named volume so they survive restarts and image rebuilds.

1. Create your `.env` (only `DISCORD_TOKEN` is required):
   ```bash
   cp .env.example .env   # then edit and paste your token
   ```

2. Build and start:
   ```bash
   docker compose up -d --build
   ```

3. View logs / stop:
   ```bash
   docker compose logs -f
   docker compose down
   ```

`DATA_DIR` is set to `/data` inside the container and is backed by the
`watchdog-data` volume — that's where `watches.json` lives.

To run without compose:
```bash
docker build -t td2-watchdog .
docker run -d --name td2-watchdog --restart unless-stopped \
  --env-file .env -v td2-watchdog-data:/data td2-watchdog
```

## Configuration

All settings are optional and live in `.env`:

| Variable | Default | Meaning |
|----------|---------|---------|
| `DISCORD_TOKEN` | — | **Required.** Your bot token. |
| `POLL_INTERVAL` | `30` | Seconds between API polls. |
| `MISS_THRESHOLD` | `2` | Consecutive missed polls before notifying. |
| `REQUIRE_IS_ONLINE` | `true` | Count a station as occupied only when `isOnline == 1`. |

## Files

- `bot.py` — the bot.
- `watches.json` — auto-created; stores active watches so they survive restarts.
- `.env` — your token and config (not committed).

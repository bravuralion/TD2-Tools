using System;
using HarmonyLib;
using MelonLoader;
using Il2CppUI; // TextClock

[assembly: MelonInfo(typeof(TD2PolandClock.PolandClockMod), "TD2 Poland Clock", "1.0.0", "Sebastian")]
[assembly: MelonGame(null, null)]

namespace TD2PolandClock
{
    public class PolandClockMod : MelonMod
    {
        public override void OnInitializeMelon()
        {
            // Eigene Harmony-Instanz anlegen und alle [HarmonyPatch]-Attribute in dieser
            // Assembly automatisch anwenden (z.B. den TextClock-Patch weiter unten).
            // Voll qualifiziert (HarmonyLib.Harmony) statt nur "Harmony", weil neuere
            // Harmony-Versionen zusätzlich einen Kompatibilitäts-Namespace "Harmony" mitbringen,
            // der sonst mit dem Klassennamen kollidiert (CS0118).
            var harmony = new HarmonyLib.Harmony("td2.polandclock");
            harmony.PatchAll();

            LoggerInstance.Msg("=== TD2 Poland Clock geladen - Uhr zeigt jetzt polnische Zeitzone ===");
        }
    }

    // Patcht die private Methode UpdateTextClock() der Klasse UI.TextClock (Interop: Il2CppUI.TextClock).
    // Postfix statt Prefix: die Original-Methode läuft normal durch (falls sie noch andere interne
    // Dinge tut, die wir nicht kennen), und direkt danach überschreiben wir den angezeigten Text
    // mit der Uhrzeit in der polnischen Zeitzone.
    [HarmonyPatch(typeof(TextClock), "UpdateTextClock")]
    public static class TextClock_UpdateTextClock_Patch
    {
        // Zeitzonen-ID unterscheidet sich zwischen Windows und Linux/macOS - wir probieren beide
        // Schreibweisen und fallen im Notfall auf UTC zurück, damit der Mod nie eine Exception wirft.
        private static readonly TimeZoneInfo PolandTimeZone = ResolvePolandTimeZone();

        private static TimeZoneInfo ResolvePolandTimeZone()
        {
            try
            {
                // Windows-Bezeichnung
                return TimeZoneInfo.FindSystemTimeZoneById("Central European Standard Time");
            }
            catch
            {
                try
                {
                    // IANA-Bezeichnung (falls TD2 z.B. via Proton/Linux läuft)
                    return TimeZoneInfo.FindSystemTimeZoneById("Europe/Warsaw");
                }
                catch
                {
                    return TimeZoneInfo.Utc;
                }
            }
        }

        // Format an die im Screenshot beobachtete Anzeige angepasst: "13:11:29" -> 24h mit Sekunden
        private const string ClockFormat = "HH:mm:ss";

        static void Postfix(TextClock __instance)
        {
            try
            {
                DateTime utcNow = DateTime.UtcNow;
                DateTime polandTime = TimeZoneInfo.ConvertTimeFromUtc(utcNow, PolandTimeZone);

                var textComponent = __instance.Text;
                if (textComponent != null)
                {
                    textComponent.text = polandTime.ToString(ClockFormat);
                }
            }
            catch (Exception ex)
            {
                MelonLogger.Error("[TD2 Poland Clock] Fehler beim Setzen der polnischen Uhrzeit: " + ex);
            }
        }
    }
}

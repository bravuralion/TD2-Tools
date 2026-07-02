using System;
using MelonLoader;
using UnityEngine;
using Il2CppEnviro;
using Il2CppAssets.Scripts.Serialization;

[assembly: MelonInfo(typeof(TD2PolandWeatherTime.PolandWeatherTimeMod), "TD2 Poland Weather Time", "1.0.0", "Sebastian")]
[assembly: MelonGame(null, null)]

namespace TD2PolandWeatherTime
{
    // Sorgt dafür, dass das Enviro-3-Tag/Nacht- und Wettersystem als Basis die
    // polnische Zeitzone (Europe/Warsaw, CET/CEST) nimmt, statt der lokalen
    // Systemzeit des Spielers. Der "Daily Cycle Offset"-Regler im Settings-Menü
    // bleibt dabei voll funktionsfähig: er verschiebt weiterhin die Anzeige,
    // nur eben relativ zur polnischen Zeit statt zur eigenen Systemzeit.
    // Endgültige Spielzeit = polnische Zeit + Offset-Regler-Wert (in Stunden).
    public class PolandWeatherTimeMod : MelonMod
    {
        // Einmal pro Sekunde reicht völlig - die sichtbare Tag/Nacht-Bewegung ist
        // ohnehin träge, ein häufigeres Update würde nur unnötig Rechenzeit kosten.
        private const float UpdateIntervalSeconds = 1f;

        private EnviroManager cachedManager;
        private float timer;

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
                    // IANA-Bezeichnung (z.B. falls TD2 unter Linux/Proton läuft)
                    return TimeZoneInfo.FindSystemTimeZoneById("Europe/Warsaw");
                }
                catch
                {
                    return TimeZoneInfo.Utc;
                }
            }
        }

        public override void OnUpdate()
        {
            timer += Time.deltaTime;
            if (timer < UpdateIntervalSeconds)
            {
                return;
            }
            timer = 0f;

            try
            {
                // Enviro-Manager ist in "DontDestroyOnLoad", einmaliges Finden reicht -
                // wir versuchen es aber erneut, falls die Referenz doch mal null wird
                // (z.B. nach einem harten Szenenwechsel).
                if (cachedManager == null)
                {
                    cachedManager = UnityEngine.Object.FindObjectOfType<EnviroManager>();
                    if (cachedManager == null)
                    {
                        return;
                    }
                }

                var timeModule = cachedManager.Time;
                if (timeModule == null)
                {
                    return;
                }

                DateTime utcNow = DateTime.UtcNow;
                DateTime polandNow = TimeZoneInfo.ConvertTimeFromUtc(utcNow, PolandTimeZone);

                // Den vom Spieler im Settings-Menü eingestellten Offset (ganze Stunden,
                // Regler-Range laut UnityExplorer: -11 bis +12) weiterhin respektieren -
                // er wird einfach auf die polnische Zeit aufaddiert statt auf die lokale.
                int offsetHours = 0;
                try
                {
                    offsetHours = Settings.dailyCycleOffset;
                }
                catch
                {
                    // Falls die Settings-Klasse in diesem Moment noch nicht initialisiert
                    // ist (z.B. ganz am Spielstart), einfach ohne Offset weitermachen.
                }

                DateTime finalTime = polandNow.AddHours(offsetHours);

                // Direkte Feldzuweisung statt einer SetDateTime(...)-Methode, weil die
                // Feldnamen (years/months/days/hours/minutes/seconds) über UnityExplorer
                // eindeutig bestätigt sind - keine Unklarheit über Parameter-Reihenfolge.
                timeModule.years = finalTime.Year;
                timeModule.months = finalTime.Month;
                timeModule.days = finalTime.Day;
                timeModule.hours = finalTime.Hour;
                timeModule.minutes = finalTime.Minute;
                timeModule.seconds = finalTime.Second;
            }
            catch (Exception ex)
            {
                MelonLogger.Error("[TD2 Poland Weather Time] Fehler beim Setzen der Enviro-Zeit: " + ex);
            }
        }
    }
}


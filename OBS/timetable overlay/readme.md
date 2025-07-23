# 🚆 TD2 Timetable Overlay für OBS

Ein simples HTML-Overlay für **Train Driver 2**, das deinen aktuellen Fahrplan von [stacjownik.spythere.eu](https://stacjownik.spythere.eu) holt und in OBS darstellt – inkl. Fortschrittsbalken, Lok & Waggons und mehrsprachiger Anzeige.

> 🟢 Kompatibel mit OBS (Browser Source)  
> 🔄 Automatische Aktualisierung alle 1 Sekunde  
> 🌍 Unterstützt Deutsch & Englisch  
> ✏️ Leicht konfigurierbar – kein Programmierwissen nötig

---

## ✅ Features

- Zeigt deinen aktuellen Fahrplanfortschritt an (in Kilometern)
- Lok + Waggons animieren sich entlang eines Fortschrittsbalkens
- Farbverlauf: rot → gelb → grün je nach Fortschritt
- Unterstützt Deutsch & Englisch (umschaltbar)
- Super einfach zu konfigurieren

---

## ⚙️ Konfiguration

Öffne die HTML-Datei in einem Texteditor und passe ganz oben den folgenden Abschnitt an:

```js
const config = {
  username: "BravuraLion",        // TD2-Fahrernamen hier eintragen
  language: "de",                 // "de" für Deutsch, "en" für Englisch
  lokImage: "https://.../lok.png", // Lok-URL
  wagonImages: [                   // 1–n Waggons
    "https://.../wagen1.png",
    "https://.../wagen2.png"
  ]
};
```

Du kannst beliebige andere Bilder verwenden – z. B. deine Lieblingslok oder eigene Icons.

---

## 🖥️ Nutzung in OBS

1. Öffne OBS
2. Füge **eine neue Browser-Quelle** hinzu
3. Wähle die HTML-Datei auf deiner Festplatte oder gib eine lokale URL an (`file:///C:/...`)
4. Setze die Größe auf `600x90`
5. Optional: **Chroma Key** oder **Transparenz aktivieren**, wenn du es in deine Szene einbauen willst

---

## 🌐 Vorschau im Browser

Du kannst das Overlay auch einfach im Browser testen:  
Doppelklick auf die HTML-Datei oder Rechtsklick → Öffnen mit → Browser deiner Wahl.

---

## 📸 Vorschau

![Vorschau](https://via.placeholder.com/600x90.png?text=TD2+Overlay+Vorschau)  
*(Du kannst hier gern ein echtes Screenshot einfügen)*

---

## 💡 Tipps

- Das Overlay zeigt immer den **zuletzt gestarteten Fahrplan** an (auch wenn er bereits abgeschlossen ist)
- Die API liefert alle 5 Sekunden neue Daten – das Overlay holt sie jede Sekunde
- Für bessere Optik → nutze transparente Bilder mit gleichen Abmessungen

---

## ❓ Fragen oder Probleme?

Erstelle ein Issue oder kontaktiere mich via GitHub.  
Pull Requests willkommen!

---

## 🛠 Credits

- Overlay-Script: [Bravura](https://github.com/bravuralion)
- Datenquelle: [Stacjownik TD2](https://stacjownik.spythere.eu)
- Icons: Font Awesome / Wikipedia Commons

---

## 🧡 Viel Spaß beim Zugfahren!

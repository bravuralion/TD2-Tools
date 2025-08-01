# 🚆 TD2 Timetable Overlay für OBS / for OBS

Ein simples HTML-Overlay für **Train Driver 2**, das deinen aktuellen Fahrplan von [stacjownik.spythere.eu](https://stacjownik.spythere.eu) holt und in OBS darstellt – inkl. Fortschrittsbalken, Lok & Waggons und mehrsprachiger Anzeige.  
A simple HTML overlay for **Train Driver 2** that fetches your current timetable from [stacjownik.spythere.eu](https://stacjownik.spythere.eu) and displays it in OBS – including progress bar, train animation, and multilingual support.

> 🟢 Kompatibel mit OBS (Browser Source)  
> 🔄 Automatische Aktualisierung alle 5 Sekunden  
> 🌍 Unterstützt Deutsch & Englisch  

> 🟢 Compatible with OBS (Browser Source)  
> 🔄 Automatic update every 5 seconds  
> 🌍 Supports German & English

---

## ✅ Features / Funktionen

- Fortschrittsanzeige des aktuellen Fahrplans (in Kilometern)  
  Shows your current timetable progress (in kilometers)
- Lok + Waggons fahren entlang des Fortschrittsbalkens  
  Train + wagons move along a progress bar
- Farbverlauf: rot → gelb → grün  
  Color gradient: red → yellow → green
- Sprache umschaltbar (de/en)  
  Language switchable (de/en)

---

## ⚙️ Konfiguration / Configuration

Öffne die HTML-Datei in einem Texteditor und passe den folgenden Abschnitt an:  
Open the HTML file in a text editor and adjust the following section:

```js
    const config = {
      username: "MiKoLaS",
      language: "de"
    };
```

---

## 🖥️ Nutzung in OBS / Using in OBS

1. Öffne OBS / Open OBS  
2. Füge **eine neue Browser-Quelle** hinzu / Add a **new browser source**  
3. Wähle die HTML-Datei oder gib eine lokale URL an (`file:///C:/...`)  
4. Setze die Größe auf `600x200` / Set size to `600x200`

---

## 🌐 Vorschau im Browser / Browser Preview

Du kannst das Overlay auch einfach im Browser testen:  
You can also test the overlay in your browser:  
Doppelklick → Öffnen mit → Browser deiner Wahl  
Double-click → Open with → browser of your choice

---

## 📸 Vorschau / Preview

![Vorschau 1](https://github.com/bravuralion/TD2-Tools/blob/main/OBS/timetable%20overlay/IMG/2025-07-23%2017_36_10-Projector%20-%20Preview.jpg)
![Vorschau 2](https://github.com/bravuralion/TD2-Tools/blob/main/OBS/timetable%20overlay/IMG/2025-07-23%2017_54_42-Projector%20-%20Preview.jpg)
![Vorschau 3](https://github.com/bravuralion/TD2-Tools/blob/main/OBS/timetable%20overlay/IMG/2025-07-23%2018_00_48-Projector%20-%20Preview.jpg)
![Vorschau 4](https://github.com/bravuralion/TD2-Tools/blob/main/OBS/timetable%20overlay/IMG/2025-07-23%2018_06_54-Projector%20-%20Preview.jpg)
![Vorschau 5](https://github.com/bravuralion/TD2-Tools/blob/main/OBS/timetable%20overlay/IMG/2025-07-23%2018_11_31-Projector%20-%20Preview.jpg)

---

## 💡 Tipps / Tips

- Zeigt immer den **zuletzt gestarteten Fahrplan** (auch wenn abgeschlossen)  
  Always shows the **last started timetable** (even if finished)
- Die Progressbar geht erst weiter wenn der Fahrplan vom FDL bestätigt wurde
  The progress bar only continues once the timetable has been confirmed by the FDL

---

## ❓ Fragen oder Probleme? / Questions or Issues?

Erstelle ein GitHub-Issue oder kontaktiere mich.  
Create a GitHub issue or contact me.  
Pull Requests willkommen! / Pull requests welcome!

---

## 🛠 Credits

- Overlay-Script: [Bravura](https://github.com/bravuralion)
- Datenquelle / Data Source: [Stacjownik TD2](https://stacjownik.spythere.eu)
- Icons: Font Awesome / Wikipedia Commons

---

## 🚂 Viel Spaß beim Zugfahren! / Enjoy the ride!

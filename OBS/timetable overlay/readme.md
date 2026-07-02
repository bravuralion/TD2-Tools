# 🚆 TD2 Timetable Overlay for OBS

A simple HTML overlay for **Train Driver 2** that fetches your current timetable from [stacjownik.spythere.eu](https://stacjownik.spythere.eu) and displays it in OBS – including a progress bar, locomotive & carriages, and multilingual display.

> 🟢 Compatible with OBS (Browser Source)  
> 🔄 Automatic updates
> 🌍 Supports German & English
> 
---

## ✅ Features

- Displays your current timetable progress (in kilometres)
- Locomotive + carriages animate along a progress bar
- Colour gradient: red → yellow → green depending on progress
- Supports German & English (switchable)

---

## ⚙️ Configuration

Open the HTML file in a text editor and customise the following section at the very top:

```js
const config = {  username: ‘BravuraLion’,        // Enter your TD2 driver name here
  language: ‘de’,                 // “de” for German, ‘en’ for English
};
```

---

## 🖥️ Using in OBS

1. Open OBS
2. Add **a new browser source**
3. Select the HTML file on your hard drive or enter a local URL (`file:///C:/...`)
4. Set the size to `600x90`
5. Optional: **Enable Chroma Key** or **Transparency** if you want to integrate it into your scene

---

## 🌐 Preview in the browser

You can also simply test the overlay in your browser:  
Double-click the HTML file or right-click → Open with → your browser of choice.

---

## 💡 Tips

- The overlay always displays the **most recently started timetable** (even if it has already finished)
- The API provides new data every 5 seconds

---

## 🛠 Credits

- Overlay script: [Bravura](https://github.com/deinProfil)
- Data source: [Stacjownik TD2](https://stacjownik.spythere.eu)
- Icons: Font Awesome / Wikipedia Commons


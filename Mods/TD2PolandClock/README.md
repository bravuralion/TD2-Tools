# TD2 Poland Clock

Ein [MelonLoader](https://github.com/LavaGang/MelonLoader)-Mod für **Train Driver 2**, der die Ingame-Uhr im Führerstand-HUD dauerhaft auf die **polnische Zeitzone** (Europe/Warsaw, CET/CEST) umstellt – unabhängig davon, in welcher Zeitzone dein PC/System eingestellt ist.

## Warum?

TD2-Fahrpläne sind in polnischer Zeit erstellt. Wenn du nicht in Polen/Mitteleuropa spielst (z.B. aus Nordamerika), zeigt die Ingame-Uhr standardmäßig deine lokale Systemzeit an – das passt dann nicht zum Fahrplan. Dieser Mod sorgt dafür, dass die Uhr im Spiel immer die polnische Zeit zeigt, egal wo du dich befindest.

## Installation (für Spieler)

**Voraussetzung:** [MelonLoader](https://melonwiki.xyz/) muss bereits für Train Driver 2 installiert sein (Version mit **Il2CppInterop**-Unterstützung, nicht die ältere Unhollower-basierte Variante).

1. Lade die aktuellste `TD2PolandClock.dll` aus den [Releases](../../releases) dieses Repos herunter.
2. Kopiere die Datei in den `Mods`-Ordner deiner TD2-Installation:
   ```
   <TD2-Installationsordner>\Mods\TD2PolandClock.dll
   ```
3. Spiel starten. Im MelonLoader-Konsolenfenster sollte beim Laden folgende Meldung erscheinen:
   ```
   === TD2 Poland Clock geladen - Uhr zeigt jetzt polnische Zeitzone ===
   ```
4. Fertig – die Uhr im Cockpit-HUD (oben rechts) zeigt jetzt immer `HH:mm:ss` in polnischer Zeit an.

Kein weiteres Setup, keine Konfigurationsdatei nötig.

## Für Entwickler – aus dem Quellcode selbst bauen

### Voraussetzungen

- Visual Studio 2022 (oder VS Code mit .NET SDK)
- [.NET 6.0 SDK](https://dotnet.microsoft.com/download/dotnet/6.0)
- MelonLoader bereits einmal für TD2 gestartet, damit die Il2Cpp-Assemblies generiert wurden (liegen danach unter `MelonLoader\Il2CppAssemblies\`)

### Projekt einrichten

1. Repo klonen bzw. Projektordner öffnen.
2. In `TD2PolandClock.csproj` den Pfad zu deiner TD2-Installation eintragen:
   ```xml
   <TD2GameDir>C:\Pfad\zu\TrainDriver2</TD2GameDir>
   ```
3. Alle benötigten Referenzen sind bereits als `<Reference>`-Einträge in der `.csproj` hinterlegt und zeigen relativ zu `TD2GameDir` auf:
   - `MelonLoader\net6\MelonLoader.dll`
   - `MelonLoader\net6\0Harmony.dll`
   - `MelonLoader\net6\Il2CppInterop.Runtime.dll`
   - `MelonLoader\Il2CppAssemblies\Il2Cppmscorlib.dll`
   - `MelonLoader\Il2CppAssemblies\Assembly-CSharp.dll`
   - `MelonLoader\Il2CppAssemblies\UnityEngine.CoreModule.dll`
   - `MelonLoader\Il2CppAssemblies\UnityEngine.UI.dll`

   Falls einzelne Dateinamen bei dir abweichen (unterschiedliche MelonLoader-Version), passe die `HintPath`-Einträge entsprechend an.

### Bauen

```bash
dotnet build -c Release
```

Die fertige DLL liegt danach unter `bin\Release\net6.0\TD2PolandClock.dll`.

### Bekannte Stolperfallen beim Bauen

- **CS0246 (Typ/Namespace nicht gefunden) für mehrere Namespaces gleichzeitig:** Referenzen fehlen komplett – siehe Liste oben, alle 7 DLLs müssen eingebunden sein.
- **"Verweis ist ungültig oder nicht unterstützt"** im Visual-Studio-Dialog: Den `Add-Reference`-Dialog umgehen und die `.csproj` stattdessen direkt bearbeiten (Rechtsklick aufs Projekt → *Projektdatei bearbeiten*) und die `<Reference>`-Einträge von Hand einfügen.
- **CS0118 ("Harmony" ist Namespace, wird aber wie Typ verwendet):** Neuere Harmony-Versionen bringen einen Kompatibilitäts-Namespace `Harmony` mit, der mit der Klasse `HarmonyLib.Harmony` kollidiert. Der Code in diesem Repo nutzt daher bewusst die volle Qualifizierung `HarmonyLib.Harmony`.
- **MSB3270 (Architektur-Warnung):** Zielplattform des Projekts auf **x64** stellen, da `MelonLoader.dll` x64-spezifisch ist.
- **"Nicht sicheren Code zulassen"**: In der `.csproj` bereits über `<AllowUnsafeBlocks>true</AllowUnsafeBlocks>` gesetzt, keine zusätzliche Handlung nötig.

## Wie es technisch funktioniert

Der Mod patcht per [Harmony](https://github.com/pardeike/Harmony) die private Methode `UpdateTextClock()` der Ingame-Klasse `UI.TextClock` (Postfix-Patch). Nach jedem Original-Update der Uhr wird der angezeigte Text zusätzlich mit der aktuellen Uhrzeit in der Zeitzone `Central European Standard Time` (Fallback: `Europe/Warsaw`, dann UTC) überschrieben. Zeitumstellungen (CET/CEST) werden dabei automatisch korrekt berücksichtigt.

## Lizenz

Nutzung auf eigene Gefahr. Kein offizieller Bestandteil von Train Driver 2.

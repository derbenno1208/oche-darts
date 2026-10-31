# Oche Darts

Dart-Zähler für Android und Browser: 12 Spielmodi, Bots in 6 Stärken, Profi-Caller, Online-Spiel ohne eigenen Server mit Einladungslink, Turniere (auch online), Statistiken mit Erfolgen und Tagesaufgabe, helles und dunkles Design, Deutsch und Englisch.

**Web-Version:** https://derbenno1208.github.io/oche-darts/ (sobald GitHub Pages aktiviert ist, siehe unten)

## Aufbau

| Pfad | Inhalt |
|---|---|
| `src/oche.html` | Die komplette App (HTML, CSS, JavaScript in einer Datei) |
| `android/` | Android-Hülle: WebView-Activity (`src/de/oche/dart/MainActivity.java`), Manifest, Icons, Build-Skript |
| `android/www/` | Eingebaute Dateien: Schriften, PeerJS, Caller-Ansagen (`caller/en.*`, `caller/de.*`) |
| `tools/caller/` | Skripte, mit denen die Caller-Ansagen erzeugt wurden (Piper bzw. Google Gemini TTS) |
| `docs/` | Web-Version für GitHub Pages, erzeugt mit `python3 tools/build_web.py` |
| `tests/` | Browser-Tests mit Playwright |

## APK bauen

Voraussetzungen: Java (JDK 17 oder neuer), Python 3, Android SDK mit `platforms/android-34` und `build-tools 34`, dazu D8 aus R8 8.5 als `r8.jar`.

```bash
cd android
SDK=/pfad/zum/android-sdk ./build.sh
```

Das Skript erwartet `$SDK/bt/android-14` (Build-Tools), `$SDK/pf/android-34/android.jar` und `$SDK/r8.jar`. Die fertige APK landet als `OcheDarts.apk` im Hauptordner.

**Signierschlüssel:** `android/oche-release.jks` gehört nicht ins Repository. Lege die Datei aus deinem Backup in den Ordner `android/`, sonst erzeugt das Skript einen neuen Schlüssel, und die neue APK lässt sich nicht mehr über die alte installieren.

## Web-Version und Einladungslinks

Einladungslinks haben die Form `https://derbenno1208.github.io/oche-darts/#join-CODE`. Im Browser öffnet sich die Web-Version und tritt dem Raum bei; die Android-App fängt solche Links ebenfalls ab (und `oche://join/CODE`).

Einmalig einrichten: Repository öffentlich stellen (GitHub Pages ist bei kostenlosen Konten nur für öffentliche Repositorys verfügbar), dann unter *Settings → Pages* als Quelle „Deploy from a branch“, Branch `main`, Ordner `/docs` wählen. Nach Änderungen an `src/oche.html` die Web-Version neu erzeugen und committen:

```bash
python3 tools/build_web.py 1.9 10 "Neuerung 1" "Neuerung 2"
```

Das Skript legt die aktuelle `OcheDarts.apk` (aus dem Hauptordner) und `version.json` in `docs/`. Die App fragt `version.json` regelmäßig ab und zeigt einen Update-Hinweis, sobald dort eine höhere Version steht. Die Web-Version ist installierbar (Manifest und Service Worker) und funktioniert nach dem ersten Laden offline.

## Tests

```bash
python3 tools/make_test_page.py
(cd android/www && python3 -m http.server 8765) &
node tests/alle_modi_bots.js
```

Weitere Tests: `summe_statistik.js`, `turnier_backup.js`, `hell_trefferbild.js`, `online_host_ausfall.js`, `online_turnier.js` (die Online-Tests brauchen Internet für den PeerJS-Vermittlungsdienst). Benötigt Node.js und Playwright mit Chromium.

## Quellen und Lizenzen

- Englische Caller-Stimme: erzeugt mit Google Gemini TTS (Stimme „en-gb-concierge-10“), Gratis-Zugang. Vor einer Veröffentlichung im Play Store die Nutzungsbedingungen prüfen.
- Deutsche Caller-Stimme: Piper TTS mit Thorsten-Voice von Thorsten Müller (CC0).
- Schriften: Big Shoulders Display, Barlow, Barlow Condensed (SIL Open Font License).
- Online-Spiel: PeerJS (MIT) mit dem öffentlichen PeerJS-Vermittlungsdienst.

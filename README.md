# Oche Darts

Dart-Zähler für Android und Browser: 12 Spielmodi, Bots in 6 Stärken, Profi-Caller, Online-Spiel ohne eigenen Server mit Einladungslink, Turniere (auch online), Statistiken mit Erfolgen und Tagesaufgabe, helles und dunkles Design, 8 Sprachen (Englisch, Deutsch, Spanisch, Französisch, Italienisch, Niederländisch, Polnisch, Portugiesisch).

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

## App bauen

Der Android-Teil ist ein Gradle-Projekt mit zwei Fassungen:

| Fassung | Ergebnis | Besonderheiten |
|---|---|---|
| `github` | `OcheDarts.apk` | werbefrei, eigener Update-Hinweis über `docs/version.json` |
| `play` | `OcheDarts.aab` | Werbung nach dem Spiel (AdMob, mit DSGVO-Einwilligung), Einmalkauf „Werbung entfernen“ (`remove_ads`), Updates nur über Google Play |

Voraussetzungen: JDK 17 oder neuer, Python 3, Gradle 8.14 und ein Android-SDK im Standardaufbau (`platforms/android-36`, `build-tools/36.1.0`). Fehlende SDK-Teile lädt Gradle selbst nach.

```bash
cd android
SDK=/pfad/zum/android-sdk VERSION_CODE=13 VERSION_NAME=2.2 ./build.sh both   # oder: ./build.sh (nur APK), ./build.sh play (nur AAB)
```

AdMob-IDs stehen in `android/gradle.properties` (voreingestellt sind Googles Test-IDs). Wie die App in den Play Store kommt und wie Werbung und Freikauf eingerichtet werden, steht in [PLAYSTORE.md](PLAYSTORE.md); die Store-Grafiken erzeugt `node tools/store_assets.js` nach `store/`.

**Signierschlüssel:** `android/app/oche-release.jks` gehört nicht ins Repository. Lege die Datei aus deinem Backup dorthin; ohne sie bricht `build.sh` ab.

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

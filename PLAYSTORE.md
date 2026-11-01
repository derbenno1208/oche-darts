# Oche Darts im Google Play Store veröffentlichen

Alles, was du in der Play Console brauchst. Texte zum Kopieren stehen weiter unten.

## Was du hochlädst

| Was | Datei |
|---|---|
| App Bundle | `OcheDarts.aab` (gebaut mit `FLAVOR=play ./build.sh` im Ordner `android/`) |
| App-Symbol 512 × 512 | `store/icon-512.png` |
| Vorstellungsgrafik 1024 × 500 | `store/feature-graphic-de.png` bzw. `-en.png` |
| Handy-Screenshots 1080 × 1920 | `store/screenshots/de/` bzw. `en/` (je 6) |
| Datenschutzerklärung | https://derbenno1208.github.io/oche-darts/datenschutz.html |

Die Play-Fassung hat **keinen eigenen Update-Hinweis und keinen APK-Download**, weil Google Play verbietet, dass sich Apps am Store vorbei aktualisieren. Updates kommen dort über den Play Store.

## Schritt für Schritt

1. **App erstellen** (Play Console → „App erstellen“)
   - App-Name: `Oche Darts – Dart-Zähler`
   - Standardsprache: Deutsch (de-DE)
   - App oder Spiel: **App**
   - Kostenlos
   - Erklärungen zu Richtlinien und Exportbestimmungen bestätigen.

2. **App einrichten** (Dashboard → „App einrichten“), die Fragen der Reihe nach:
   - **Datenschutzerklärung:** URL von oben.
   - **App-Zugriff:** „Alle Funktionen sind ohne besonderen Zugriff verfügbar.“
   - **Anzeigen:** „Nein, meine App enthält keine Anzeigen.“
   - **Einstufung des Inhalts (IARC):** Kategorie „Alle anderen App-Typen“. Gewalt, Sexualität, Sprache, Drogen, Glücksspiel: jeweils **Nein**. „Können Nutzer miteinander interagieren oder Inhalte austauschen?“ → **Ja** (im Online-Modus sehen Mitspielende den gewählten Spielernamen). Standortweitergabe: Nein. Digitale Käufe: Nein.
   - **Zielgruppe:** **13 Jahre und älter** (also nicht „für Kinder“, sonst gelten die strengeren Familien-Richtlinien).
   - **Datensicherheit:** siehe eigener Abschnitt unten.
   - **Behörden-Apps, Finanzfunktionen, Gesundheit:** jeweils Nein.
   - **App-Kategorie:** Sport. **Kontaktdaten:** eine E-Mail-Adresse, die im Store öffentlich angezeigt wird.

3. **Store-Eintrag** (Wachstum → Store-Präsenz → Haupteintrag): Texte von unten, Symbol, Vorstellungsgrafik, Screenshots. Unter „Übersetzungen verwalten“ Englisch hinzufügen und die englischen Texte und Bilder eintragen.

4. **Geschlossener Test** (Pflicht für neue private Entwicklerkonten):
   - Testen → Geschlossene Tests → Track erstellen → `OcheDarts.aab` hochladen, Versionshinweis eintragen.
   - Tester: mindestens **12 Personen** mit Google-Konto (E-Mail-Liste oder Google-Gruppe). Die Tester müssen über den **Opt-in-Link** zustimmen und die App installieren.
   - Mindestens **14 Tage am Stück** dabeibleiben. Wer zwischendurch austritt, zählt erst nach 14 neuen Tagen.
   - Danach unter Dashboard → „Zugriff auf Produktion beantragen“. Google stellt dort Fragen zum Test.

5. **Produktion:** Nach der Freigabe eine Produktionsversion mit dem gleichen oder einem neueren App Bundle erstellen und zur Prüfung einreichen. Die erste Prüfung dauert meist einige Tage.

## Signatur: wichtig

- `android/oche-release.jks` ist dein **Upload-Schlüssel**. Google signiert die App im Store mit einem eigenen Schlüssel („Play App Signing“, bei neuen Apps Standard). Den Upload-Schlüssel gut sichern; geht er verloren, kann man ihn über den Play-Support zurücksetzen lassen.
- Die APK von GitHub und die Play-Store-App haben dadurch **unterschiedliche Signaturen**. Wer von der GitHub-APK zur Play-Store-Version wechseln will, muss die App einmal deinstallieren. Vorher unter Optionen → „Daten sichern“ ein Backup machen, danach wiederherstellen.
- Der Paketname `de.oche.dart` lässt sich nach der Veröffentlichung nicht mehr ändern.

## Datensicherheit (Vorschlag)

Diese Angaben verantwortest du; sie passen zum aktuellen Stand der App:

- **Werden Nutzerdaten erhoben oder weitergegeben?** Ja (nur für den Online-Modus).
- **Datentyp:** Persönliche Daten → **Name** (der selbst gewählte Spielername).
  - Erhoben, nicht weitergegeben an Dritte zu deren Zwecken.
  - Zweck: **App-Funktionalität**.
  - **Optional** (nur wenn man online spielt), **flüchtige Verarbeitung** (wird nicht gespeichert).
- **Verschlüsselung bei der Übertragung:** Ja (WebRTC ist immer verschlüsselt).
- **Löschung beantragen:** Die App speichert nichts auf Servern; alle Daten liegen auf dem Gerät und verschwinden beim Deinstallieren.
- Mikrofon-Aufnahmen, Statistiken und Einstellungen bleiben auf dem Gerät und gelten deshalb nicht als „erhoben“.

## Berechtigungen

| Berechtigung | Wofür |
|---|---|
| Internet, Netzwerkstatus | Online-Spiel |
| Mikrofon | nur für eigene Caller-Aufnahmen, wird erst beim Aufnehmen abgefragt |
| Vibration | Vibration bei der Eingabe |

## Vorher prüfen

- **Caller-Stimme:** Die englischen Ansagen wurden mit dem Gratis-Zugang der Google Gemini API erzeugt. Lies vor der Veröffentlichung die Nutzungsbedingungen der Gemini API (insbesondere zur Nutzung erzeugter Inhalte), oder schalte die Stimme notfalls auf die freie deutsche Thorsten-Stimme bzw. die Handystimme um.
- **App-Name:** Prüfe kurz im Play Store, ob es schon eine App mit sehr ähnlichem Namen gibt.

---

## Texte für den Store-Eintrag

### Deutsch

**App-Name** (max. 30 Zeichen)

```
Oche Darts – Dart-Zähler
```

**Kurzbeschreibung** (max. 80 Zeichen)

```
Dart-Zähler mit 12 Spielmodi, Profi-Caller, Bots, Turnieren und Online-Spiel
```

**Vollständige Beschreibung** (max. 4000 Zeichen)

```
Oche ist der Dart-Zähler für dein Board zu Hause, in der Kneipe oder im Verein. Trag deine Würfe ein, Oche rechnet, sagt an und führt Statistik.

12 SPIELMODI
• X01 (101 bis 2001, Double In/Out, Master Out, Legs und Sets)
• Cricket und Cut-Throat Cricket
• Around the Clock, Shanghai, Killer, Halve-It, High Score
• Training: Bob's 27, 121 Checkout-Training, Doppel-Training
• Party: Gotcha und Scram für zwei

PROFI-CALLER
Echte Hallen-Atmosphäre: jede Punktzahl angesagt, „You require 141“, „Game shot, and the leg!“ und natürlich die gedehnte „One hundred and eighty!“ mit jubelndem Publikum. Auf Englisch oder Deutsch, oder mit deinen eigenen Aufnahmen.

SCHNELL EINGEBEN
Einzelne Darts per Tasten, per Tipp auf die Dartscheibe oder als Aufnahme-Summe. Checkout-Vorschläge wie bei den Profis, mit deinem Lieblingsdoppel.

GEGEN BOTS
Sechs Stärken von Anfänger (Ø 20–30) bis Weltklasse (Ø 85–105).

ONLINE MIT FREUNDEN
Raum erstellen, Einladungslink teilen, zusammen spielen, auch an verschiedenen Orten. Bis zu 8 Spieler und 16 Zuschauer. Fällt das Handy des Gastgebers aus, übernimmt automatisch ein anderes.

TURNIERE
K.-o.-System oder Liga, mit Turnierbaum und Tabelle, auch online.

STATISTIK
Average-Verlauf, First-9-Average, 180er, Checkout-Quote nach Rest, Doppelquote je Feld, Trefferbild, Bilanz gegen deine Gegner, 22 Erfolge und eine tägliche Trainingsaufgabe.

UND MEHR
Großanzeige für Tablet oder Fernseher, helles und dunkles Design, Deutsch und Englisch, Daten sichern und wiederherstellen.

Keine Werbung, kein Konto, kein Tracking.
```

### English

**App name** (max. 30 characters)

```
Oche Darts – Dart Scorer
```

**Short description** (max. 80 characters)

```
Dart scorer with 12 game modes, pro caller, bots, tournaments and online play
```

**Full description** (max. 4000 characters)

```
Oche is the dart scorer for your board at home, at the pub or at the club. Enter your darts, Oche does the maths, calls the scores and keeps your stats.

12 GAME MODES
• X01 (101 to 2001, double in/out, master out, legs and sets)
• Cricket and cut-throat cricket
• Around the Clock, Shanghai, Killer, Halve-It, High Score
• Practice: Bob's 27, 121 checkout practice, doubles practice
• Party: Gotcha and Scram for two

PRO CALLER
Real arena atmosphere: every score called, "You require 141", "Game shot, and the leg!" and of course the long "One hundred and eighty!" with a roaring crowd. In English or German, or with your own recordings.

FAST INPUT
Single darts on the keypad, by tapping the dartboard, or as a visit total. Checkout suggestions like the pros, with your favourite double.

PLAY THE BOTS
Six levels from beginner (avg 20–30) to world class (avg 85–105).

ONLINE WITH FRIENDS
Create a room, share the invite link and play together, even in different places. Up to 8 players and 16 spectators. If the host's phone drops out, another device takes over automatically.

TOURNAMENTS
Knockout or league, with bracket and table, online too.

STATS
Average history, first-9 average, 180s, checkout rate by score left, doubles rate per field, hit map, head-to-head records, 22 achievements and a daily practice challenge.

AND MORE
Big screen mode for tablets or TVs, light and dark theme, English and German, backup and restore.

No ads, no account, no tracking.
```

### Versionshinweis für die erste Version

```
Erste Version von Oche Darts im Play Store.
```

## Quellen

- [Target API level requirements for Google Play apps](https://support.google.com/googleplay/android-developer/answer/11926878)
- [App testing requirements for new personal developer accounts](https://support.google.com/googleplay/android-developer/answer/14151465)
- [Play Console: Get started](https://support.google.com/googleplay/android-developer/answer/6112435)

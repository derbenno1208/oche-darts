#!/bin/bash
# Baut Oche Darts mit Gradle.
#   ./build.sh          → OcheDarts.apk  (Fassung "github": werbefrei, eigener Update-Hinweis)
#   ./build.sh play     → OcheDarts.aab  (Fassung "play": Werbung nach dem Spiel, Freikauf über Google Play)
#   ./build.sh both     → APK und AAB
#   ./build.sh tv       → OcheDarts-FireTV.apk (Fassung "firetv": Fernseher-Anzeige für den Amazon Appstore)
# Umgebungsvariablen: SDK (Android-SDK-Ordner, Standardaufbau mit platforms/ und build-tools/),
#                     VERSION_CODE, VERSION_NAME, HTML (Pfad zur App-Datei, Standard ../src/oche.html)
set -e
cd "$(dirname "$0")"
SDK=${SDK:?Bitte SDK=/pfad/zum/android-sdk setzen (siehe README)}
HTML=${HTML:-../src/oche.html}
WHAT=${1:-apk}
echo "sdk.dir=$SDK" > local.properties
[ -f app/oche-release.jks ] || { echo "Signierschlüssel app/oche-release.jks fehlt (aus dem Backup kopieren)."; exit 1; }

# Web-App einbauen: lokale Schriften und PeerJS statt Google Fonts/CDN (siehe tools/app_html.py)
OUT=app/build/generated/oche-assets/www
rm -rf app/build/generated/oche-assets && mkdir -p $OUT
python3 ../tools/app_html.py android "$OUT/index.html" "$HTML"
cp www/peerjs.min.js www/fonts.css $OUT/ && cp -r www/fonts www/caller $OUT/

PROPS=""
[ -n "$VERSION_CODE" ] && PROPS="$PROPS -PocheVersionCode=$VERSION_CODE"
[ -n "$VERSION_NAME" ] && PROPS="$PROPS -PocheVersionName=$VERSION_NAME"
TASKS=""
[ "$WHAT" = "apk" -o "$WHAT" = "both" ] && TASKS="$TASKS :app:assembleGithubRelease"
[ "$WHAT" = "play" -o "$WHAT" = "both" ] && TASKS="$TASKS :app:bundlePlayRelease"
[ "$WHAT" = "tv" ] && TASKS="$TASKS :app:assembleFiretvRelease"
gradle --console=plain -q $PROPS $TASKS
# Ergebnisse in den Hauptordner kopieren
if [ "$WHAT" = "apk" -o "$WHAT" = "both" ]; then cp app/build/outputs/apk/github/release/app-github-release.apk ../OcheDarts.apk && echo "→ OcheDarts.apk"; fi
if [ "$WHAT" = "play" -o "$WHAT" = "both" ]; then cp app/build/outputs/bundle/playRelease/app-play-release.aab ../OcheDarts.aab && echo "→ OcheDarts.aab"; fi
if [ "$WHAT" = "tv" ]; then cp app/build/outputs/apk/firetv/release/app-firetv-release.apk ../OcheDarts-FireTV.apk && echo "→ OcheDarts-FireTV.apk"; fi

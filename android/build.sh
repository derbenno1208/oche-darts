#!/bin/bash
# Baut Oche Darts.
#   ./build.sh             → OcheDarts.apk  (Direkt-Download/GitHub, mit eigenem Update-Hinweis)
#   FLAVOR=play ./build.sh → OcheDarts.aab  (Google Play, Updates nur über den Play Store)
# Umgebungsvariablen: SDK (Android-SDK-Ordner), VERSION_CODE, VERSION_NAME, HTML (Pfad zur App-Datei)
set -e
cd "$(dirname "$0")"
SDK=${SDK:?Bitte SDK=/pfad/zum/android-sdk setzen (siehe README)}
BT=$SDK/bt36/android-16
JAR=$SDK/pf36/android-36/android.jar
R8=$SDK/r8.jar
BUNDLETOOL=$SDK/bundletool.jar
HTML=${HTML:-../src/oche.html}
FLAVOR=${FLAVOR:-apk}
VC=${VERSION_CODE:-1}; VN=${VERSION_NAME:-1.0}
KS=oche-release.jks; KP=ochedarts; KA=oche
rm -rf build && mkdir -p build/gen build/classes build/dex build/assets/www build/res

# Web-App einbauen: lokale Schriften und PeerJS statt Google Fonts/CDN
HTML="$HTML" python3 - <<'PY'
import os,re
s=open(os.environ["HTML"]).read()
s=re.sub(r'<link rel="preconnect"[^>]*>\n','',s)
s=re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n','',s)
s=s.replace('<!--APP-HEAD-->','<link rel="stylesheet" href="fonts.css">\n<script src="peerjs.min.js"></script>')
head='<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">\n<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}button,a{-webkit-tap-highlight-color:transparent}</style>\n'
i=s.index('<div class="wrap"')
open('build/assets/www/index.html','w').write(head+s[:i]+'</head><body>\n'+s[i:]+'</body></html>\n')
PY
cp www/peerjs.min.js www/fonts.css build/assets/www/ && cp -r www/fonts www/caller build/assets/www/

# Ressourcen mit Kennung der Fassung
cp -r res/* build/res/
[ "$FLAVOR" = "play" ] && sed -i 's#<bool name="play_store">false</bool>#<bool name="play_store">true</bool>#' build/res/values/flavor.xml
$BT/aapt2 compile --dir build/res -o build/res.zip
LINK="-I $JAR --manifest AndroidManifest.xml -A build/assets --java build/gen --min-sdk-version 24 --target-sdk-version 36 --version-code $VC --version-name $VN build/res.zip"

# Java übersetzen und in DEX umwandeln
$BT/aapt2 link -o build/base.apk $LINK
javac -source 8 -target 8 -nowarn -Xlint:-options -classpath $JAR -d build/classes $(find src build/gen -name '*.java')
(cd build/classes && jar cf ../classes.jar .)
java -cp $R8 com.android.tools.r8.D8 --release --min-api 24 --lib $JAR --output build/dex build/classes.jar

if [ ! -f $KS ]; then
  keytool -genkeypair -keystore $KS -storepass $KP -keypass $KP -alias $KA \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Oche Darts, O=Oche, C=DE" >/dev/null 2>&1
fi

if [ "$FLAVOR" = "play" ]; then
  # App Bundle: Ressourcen im Proto-Format, Modul "base" zusammensetzen, mit bundletool bauen, signieren
  $BT/aapt2 link --proto-format -o build/proto.zip $LINK
  rm -rf build/module && mkdir -p build/module/manifest build/module/dex
  (cd build/module && unzip -q ../proto.zip && mv AndroidManifest.xml manifest/)
  cp build/dex/classes.dex build/module/dex/
  (cd build/module && zip -q -r -D ../base.zip .)
  rm -f ../OcheDarts.aab
  java -jar $BUNDLETOOL build-bundle --modules=build/base.zip --output=../OcheDarts.aab
  jarsigner -keystore $KS -storepass $KP -keypass $KP -sigalg SHA256withRSA -digestalg SHA-256 ../OcheDarts.aab $KA >/dev/null
  jarsigner -verify ../OcheDarts.aab | head -1
  ls -la ../OcheDarts.aab
else
  cp build/base.apk build/unsigned.apk
  (cd build/dex && zip -q -u ../unsigned.apk classes.dex)
  $BT/zipalign -f -p 4 build/unsigned.apk build/aligned.apk
  $BT/apksigner sign --ks $KS --ks-pass pass:$KP --key-pass pass:$KP --out ../OcheDarts.apk build/aligned.apk
  $BT/apksigner verify ../OcheDarts.apk && ls -la ../OcheDarts.apk
fi

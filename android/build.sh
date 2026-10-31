#!/bin/bash
# Baut Oche Darts als signierte APK. Aufruf: ./build.sh
set -e
cd "$(dirname "$0")"
SDK=${SDK:?Bitte SDK=/pfad/zum/android-sdk setzen (siehe README)}
BT=$SDK/bt/android-14
JAR=$SDK/pf/android-34/android.jar
VC=${VERSION_CODE:-1}; VN=${VERSION_NAME:-1.0}
rm -rf build && mkdir -p build/gen build/classes build/dex build/assets/www
# Web-App einbauen: lokale Schriften und PeerJS statt Google Fonts/CDN
python3 - <<'PY'
s=open('../src/oche.html').read()
import re
s=re.sub(r'<link rel="preconnect"[^>]*>\n','',s)
s=re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n','',s)
s=s.replace('<!--APP-HEAD-->','<link rel="stylesheet" href="fonts.css">\n<script src="peerjs.min.js"></script>')
head='<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">\n<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}button,a{-webkit-tap-highlight-color:transparent}</style>\n'
i=s.index('<div class="wrap"')
open('build/assets/www/index.html','w').write(head+s[:i]+'</head><body>\n'+s[i:]+'</body></html>\n')
PY
cp www/peerjs.min.js www/fonts.css build/assets/www/ && cp -r www/fonts www/caller build/assets/www/
$BT/aapt2 compile --dir res -o build/res.zip
$BT/aapt2 link -o build/base.apk -I $JAR --manifest AndroidManifest.xml -A build/assets --java build/gen \
  --min-sdk-version 24 --target-sdk-version 34 --version-code $VC --version-name $VN build/res.zip
javac -source 8 -target 8 -nowarn -Xlint:-options -classpath $JAR -d build/classes $(find src build/gen -name '*.java')
java -cp $SDK/r8.jar com.android.tools.r8.D8 --release --min-api 24 --lib $JAR --output build/dex $(find build/classes -name '*.class')
cp build/base.apk build/unsigned.apk
(cd build/dex && zip -q -u ../unsigned.apk classes.dex)
$BT/zipalign -f -p 4 build/unsigned.apk build/aligned.apk
if [ ! -f oche-release.jks ]; then
  keytool -genkeypair -keystore oche-release.jks -storepass ochedarts -keypass ochedarts -alias oche \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Oche Darts, O=Oche, C=DE" >/dev/null 2>&1
fi
$BT/apksigner sign --ks oche-release.jks --ks-pass pass:ochedarts --key-pass pass:ochedarts --out ../OcheDarts.apk build/aligned.apk
$BT/apksigner verify --print-certs ../OcheDarts.apk | head -2
ls -la ../OcheDarts.apk

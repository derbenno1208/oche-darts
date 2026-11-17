"""Macht aus src/oche.html die ausgelieferten Seiten.

Die App ist eine einzige Datei (HTML, CSS, JavaScript). Sie enthält weder <html> noch <body>,
dafür die Marke <!--APP-HEAD-->. Je nach Ziel kommen hier Kopf, lokale Schriften und PeerJS dazu:

    android  eingebaute Seite der Android-App          (android/build.sh)
    web      Web-Version für GitHub Pages              (tools/build_web.py)
    test     Testseite für die Browser-Tests           (tools/make_test_page.py)

Aufruf: python3 tools/app_html.py android|web|test ZIELDATEI [QUELLDATEI]
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "oche.html")
SITE = "https://derbenno1208.github.io/oche-darts/"

BASE_STYLE = ('<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
              'body{margin:0;font-size:14px}img{max-width:100%}[hidden]{display:none!important}'
              'button,a{-webkit-tap-highlight-color:transparent}</style>\n')


def read_source(path=None):
    return open(path or SRC, encoding="utf-8").read()


def mode_count(s):
    """Zahl der Spielmodi, direkt aus dem Quelltext gezählt (für Beschreibungstexte)."""
    return len(re.findall(r'^[a-z0-9]+:\{\n  name:"', s, re.M))


def description(s):
    return f"Dart-Zähler mit {mode_count(s)} Spielmodi, Online-Spiel, Turnieren und Profi-Caller."


def _local(s, head_extra):
    """Google Fonts durch die mitgelieferten Schriften ersetzen und den Kopf ergänzen."""
    s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
    s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', s)
    return s.replace('<!--APP-HEAD-->', head_extra)


def _page(s, viewport):
    head = ('<!doctype html>\n<html lang="de"><head><meta charset="utf-8">\n'
            f'<meta name="viewport" content="{viewport}">\n' + BASE_STYLE)
    i = s.index('<div class="wrap"')
    return head + s[:i] + '</head><body>\n' + s[i:] + '</body></html>\n'


def android_page(s):
    s = _local(s, '<link rel="stylesheet" href="fonts.css">\n<script src="peerjs.min.js"></script>')
    return _page(s, "width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no")


def web_page(s):
    s = _local(s, '\n'.join([
        '<link rel="stylesheet" href="fonts.css">', '<link rel="manifest" href="manifest.webmanifest">',
        '<link rel="icon" href="icon-192.png">', '<link rel="apple-touch-icon" href="icon-192.png">',
        '<meta name="theme-color" content="#0d1512">', '<meta name="mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-capable" content="yes">',
        '<meta name="apple-mobile-web-app-title" content="Oche">',
        f'<meta name="description" content="Oche Darts: {description(s)}">',
        '<script src="peerjs.min.js"></script>']))
    return _page(s, "width=device-width,initial-scale=1,viewport-fit=cover")


def test_page(s):
    """Wie im Browser geöffnet, mit lokalem PeerJS. Die Einführung für neue Nutzer bleibt aus,
    damit sie die Tests nicht verdeckt; mit ?intro in der Adresse erscheint sie."""
    skip_intro = ('<script>try{if(!/[?&]intro\\b/.test(location.search))localStorage.setItem("oche.intro","1")}catch(e){}</script>\n'
                  '<script src="peerjs.min.js"></script>')
    s = s.replace('<!--APP-HEAD-->', skip_intro)
    return ('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<style>[hidden]{display:none!important}body{margin:0}</style>' + s + '</html>')


BUILDERS = {"android": android_page, "web": web_page, "test": test_page}


def write(kind, target, source=None):
    os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(BUILDERS[kind](read_source(source)))


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in BUILDERS:
        sys.exit(__doc__)
    write(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)

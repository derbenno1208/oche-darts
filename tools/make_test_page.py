"""Erzeugt android/www/test.html aus src/oche.html für die Browser-Tests (mit lokalem PeerJS)."""
import os
from app_html import ROOT, write

target = os.path.join(ROOT, "android", "www", "test.html")
write("test", target)
print("android/www/test.html erzeugt")

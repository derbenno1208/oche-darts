# Oche Darts: R8-Regeln
# Die Web-App ruft diese Methoden per Name auf (window.AndroidTTS.*), sie dürfen nicht umbenannt oder entfernt werden.
-keepattributes JavascriptInterface
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
-keep class de.oche.dart.MainActivity$Bridge { *; }
# Für lesbare Absturzberichte in der Play Console
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

package de.oche.dart;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.view.View;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import android.speech.tts.TextToSpeech;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import java.io.InputStream;
import java.util.Locale;

public class MainActivity extends Activity {
    static final String HOST = "appassets.androidplatform.net";
    static final int REQ_MIC = 7, REQ_FILE = 9, REQ_SAVE = 11;
    String pendingSave;
    WebView web;
    TextToSpeech tts;
    volatile boolean ttsReady = false;
    PermissionRequest pendingPermission;
    ValueCallback<Uri[]> fileCallback;

    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0d1512"));
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setUserAgentString(s.getUserAgentString() + " OcheApp/1.1");

        web.setWebViewClient(new Client());
        web.setWebChromeClient(new Chrome());
        tts = new TextToSpeech(this, new TtsInit());
        web.addJavascriptInterface(new Bridge(), "AndroidTTS");

        if (saved != null) web.restoreState(saved);
        else web.loadUrl("https://" + HOST + "/index.html");
    }

    /* Liefert die Web-App aus den Assets unter einer https-Adresse aus */
    class Client extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
            Uri u = req.getUrl();
            if (!HOST.equals(u.getHost())) return null;
            String path = u.getPath();
            if (path == null || path.equals("/") || path.isEmpty()) path = "/index.html";
            try {
                InputStream in = getAssets().open("www" + path);
                return new WebResourceResponse(mime(path), "UTF-8", in);
            } catch (Exception e) {
                return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", null, null);
            }
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
            Uri u = req.getUrl();
            if (HOST.equals(u.getHost())) return false;
            try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) { }
            return true;
        }
    }

    /* Mikrofon für eigene Caller-Aufnahmen, Dateiauswahl für Audiodateien */
    class Chrome extends WebChromeClient {
        @Override
        public void onPermissionRequest(PermissionRequest request) {
            boolean wantsMic = false;
            for (String r : request.getResources()) if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) wantsMic = true;
            if (!wantsMic) { request.deny(); return; }
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                request.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
            } else {
                pendingPermission = request;
                requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_MIC);
            }
        }

        @Override
        public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (fileCallback != null) fileCallback.onReceiveValue(null);
            fileCallback = callback;
            Intent i = new Intent(Intent.ACTION_GET_CONTENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            String type = "*/*";
            String[] acc = params.getAcceptTypes();
            if (acc != null && acc.length > 0 && acc[0] != null && acc[0].startsWith("audio")) type = "audio/*";
            i.setType(type);
            try {
                startActivityForResult(Intent.createChooser(i, "Audiodatei wählen"), REQ_FILE);
            } catch (Exception e) {
                fileCallback = null;
                return false;
            }
            return true;
        }
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] results) {
        super.onRequestPermissionsResult(code, perms, results);
        if (code != REQ_MIC || pendingPermission == null) return;
        if (results.length > 0 && results[0] == PackageManager.PERMISSION_GRANTED)
            pendingPermission.grant(new String[]{PermissionRequest.RESOURCE_AUDIO_CAPTURE});
        else pendingPermission.deny();
        pendingPermission = null;
    }

    @Override
    protected void onActivityResult(int code, int result, Intent data) {
        super.onActivityResult(code, result, data);
        if (code == REQ_SAVE) {
            boolean ok = false;
            if (result == RESULT_OK && data != null && data.getData() != null && pendingSave != null) {
                try (OutputStream os = getContentResolver().openOutputStream(data.getData())) {
                    os.write(pendingSave.getBytes(StandardCharsets.UTF_8)); ok = true;
                } catch (Exception ignored) { }
            }
            pendingSave = null;
            web.evaluateJavascript("window.ocheSaved&&window.ocheSaved(" + ok + ")", null);
            return;
        }
        if (code != REQ_FILE || fileCallback == null) return;
        Uri[] uris = null;
        if (result == RESULT_OK && data != null && data.getData() != null) uris = new Uri[]{data.getData()};
        fileCallback.onReceiveValue(uris);
        fileCallback = null;
    }

    class TtsInit implements TextToSpeech.OnInitListener {
        @Override
        public void onInit(int status) {
            ttsReady = status == TextToSpeech.SUCCESS;
            if (ttsReady) tts.setLanguage(Locale.GERMANY);
        }
    }

    class BackCallback implements ValueCallback<String> {
        @Override
        public void onReceiveValue(String v) {
            if (v == null || !v.contains("y")) finish();
        }
    }

    class SaveTask implements Runnable {
        final String name, mime, content;
        SaveTask(String n, String m, String c) { name = n; mime = m; content = c; }
        @Override
        public void run() {
            pendingSave = content;
            Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType(mime);
            i.putExtra(Intent.EXTRA_TITLE, name);
            try { startActivityForResult(i, REQ_SAVE); }
            catch (Exception e) { pendingSave = null; web.evaluateJavascript("window.ocheSaved&&window.ocheSaved(false)", null); }
        }
    }

    class BarsTask implements Runnable {
        final boolean light;
        BarsTask(boolean l) { light = l; }
        @Override
        public void run() {
            int c = Color.parseColor(light ? "#eef1ec" : "#0d1512");
            getWindow().setStatusBarColor(c);
            getWindow().setNavigationBarColor(c);
            web.setBackgroundColor(c);
            View d = getWindow().getDecorView();
            int f = d.getSystemUiVisibility();
            if (light) { f |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR; if (Build.VERSION.SDK_INT >= 26) f |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR; }
            else { f &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR; if (Build.VERSION.SDK_INT >= 26) f &= ~View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR; }
            d.setSystemUiVisibility(f);
        }
    }

    @Override
    public void onConfigurationChanged(Configuration c) {
        super.onConfigurationChanged(c);
        if (web != null) web.evaluateJavascript("window.ocheThemeChanged&&window.ocheThemeChanged()", null);
    }

    class ShareTask implements Runnable {
        final String text;
        ShareTask(String t) { text = t; }
        @Override
        public void run() {
            Intent i = new Intent(Intent.ACTION_SEND);
            i.setType("text/plain");
            i.putExtra(Intent.EXTRA_TEXT, text);
            try { startActivity(Intent.createChooser(i, "Raumcode teilen")); } catch (Exception ignored) { }
        }
    }

    /* Von JavaScript aufrufbar: window.AndroidTTS.* */
    class Bridge {
        @JavascriptInterface
        public void speak(String text, String lang) { speak2(text, lang, 1.0f, 0.9f); }

        @JavascriptInterface
        public void speak2(String text, String lang, float rate, float pitch) {
            if (!ttsReady || text == null) return;
            Locale loc = (lang != null && lang.startsWith("en")) ? Locale.UK : Locale.GERMANY;
            synchronized (MainActivity.this) {
                tts.setLanguage(loc);
                tts.setSpeechRate(Math.max(0.2f, Math.min(2.5f, rate)));
                tts.setPitch(Math.max(0.5f, Math.min(2.0f, pitch)));
                tts.speak(text, TextToSpeech.QUEUE_ADD, null, "oche" + System.nanoTime());
            }
        }

        @JavascriptInterface
        public void stop() { if (ttsReady) tts.stop(); }

        @JavascriptInterface
        public boolean isNight() {
            return (getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES;
        }

        @JavascriptInterface
        public void setBars(boolean light) { runOnUiThread(new BarsTask(light)); }

        @JavascriptInterface
        public void share(String text) { runOnUiThread(new ShareTask(text)); }

        @JavascriptInterface
        public void vibrate(int ms) {
            try {
                Vibrator v = (Vibrator) getSystemService(VIBRATOR_SERVICE);
                if (v == null || !v.hasVibrator()) return;
                if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createOneShot(Math.max(5, Math.min(800, ms)), VibrationEffect.DEFAULT_AMPLITUDE));
                else v.vibrate(Math.max(5, Math.min(800, ms)));
            } catch (Exception ignored) { }
        }

        @JavascriptInterface
        public void saveFile(String name, String mime, String content) { runOnUiThread(new SaveTask(name, mime, content)); }
    }

    static String mime(String p) {
        if (p.endsWith(".html")) return "text/html";
        if (p.endsWith(".js")) return "application/javascript";
        if (p.endsWith(".css")) return "text/css";
        if (p.endsWith(".woff2")) return "font/woff2";
        if (p.endsWith(".png")) return "image/png";
        if (p.endsWith(".svg")) return "image/svg+xml";
        if (p.endsWith(".json")) return "application/json";
        return "application/octet-stream";
    }

    @Override
    public void onBackPressed() {
        web.evaluateJavascript("(window.ocheBack&&window.ocheBack())?'y':'n'", new BackCallback());
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    protected void onDestroy() {
        if (tts != null) tts.shutdown();
        if (web != null) web.destroy();
        super.onDestroy();
    }
}

package de.oche.dart;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;
import android.webkit.WebView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;

/**
 * Spracheingabe über die Spracherkennung des Geräts. Ergebnisse gehen als
 * window.ocheSpeech({type:"result",alts:[...]}) / {type:"end"} / {type:"error",code} an die Web-App.
 */
class Speech implements RecognitionListener {
    static final int REQ_SPEECH = 13;
    final Activity act;
    final WebView web;
    SpeechRecognizer rec;
    String pendingLang;

    Speech(Activity a, WebView w) { act = a; web = w; }

    boolean available() {
        try { return SpeechRecognizer.isRecognitionAvailable(act); } catch (Exception e) { return false; }
    }

    /** Muss im UI-Thread laufen. */
    void start(String lang) {
        if (act.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            pendingLang = lang;
            act.requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQ_SPEECH);
            return;
        }
        if (rec == null) {
            if (!available()) { send("error", "not-available", null); return; }
            rec = SpeechRecognizer.createSpeechRecognizer(act);
            rec.setRecognitionListener(this);
        }
        Intent i = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        i.putExtra(RecognizerIntent.EXTRA_LANGUAGE, lang);
        i.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5);
        i.putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false);
        i.putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, act.getPackageName());
        try { rec.startListening(i); } catch (Exception e) { send("error", "client", null); }
    }

    void permissionResult(boolean granted) {
        if (pendingLang == null) return;
        String l = pendingLang;
        pendingLang = null;
        if (granted) start(l); else send("error", "not-allowed", null);
    }

    void stop() {
        pendingLang = null;
        if (rec != null) { try { rec.cancel(); } catch (Exception ignored) { } }
    }

    void destroy() {
        if (rec != null) { try { rec.destroy(); } catch (Exception ignored) { } rec = null; }
    }

    void send(String type, String code, ArrayList<String> alts) {
        try {
            JSONObject o = new JSONObject();
            o.put("type", type);
            if (code != null) o.put("code", code);
            if (alts != null) o.put("alts", new JSONArray(alts));
            final String js = "window.ocheSpeech&&window.ocheSpeech(" + JSONObject.quote(o.toString()) + ")";
            act.runOnUiThread(() -> web.evaluateJavascript(js, null));
        } catch (Exception ignored) { }
    }

    @Override public void onResults(Bundle b) {
        ArrayList<String> r = b != null ? b.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION) : null;
        send("result", null, r != null ? r : new ArrayList<>());
        send("end", null, null);
    }

    @Override public void onError(int e) {
        String c;
        if (e == SpeechRecognizer.ERROR_NO_MATCH) c = "no-match";
        else if (e == SpeechRecognizer.ERROR_SPEECH_TIMEOUT) c = "no-speech";
        else if (e == SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS) c = "not-allowed";
        else c = "err" + e;
        send("error", c, null);
    }

    @Override public void onReadyForSpeech(Bundle params) { }
    @Override public void onBeginningOfSpeech() { }
    @Override public void onRmsChanged(float rmsdB) { }
    @Override public void onBufferReceived(byte[] buffer) { }
    @Override public void onEndOfSpeech() { }
    @Override public void onPartialResults(Bundle partialResults) { }
    @Override public void onEvent(int eventType, Bundle params) { }
}

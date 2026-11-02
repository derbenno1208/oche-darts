package de.oche.dart;

import android.app.Activity;
import android.webkit.WebView;

/** GitHub-Fassung: werbefrei, ohne Käufe. Gleiche Schnittstelle wie in der Play-Fassung. */
public class Monetization {
    public Monetization(Activity a, WebView w) { }
    public void init() { }
    public void showAfterGame() { }
    public void showPrivacyOptions() { }
    public void askReview() { }
    public void buy() { }
    public String stateJson() { return "{\"enabled\":false}"; }
}

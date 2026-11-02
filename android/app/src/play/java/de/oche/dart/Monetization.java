package de.oche.dart;

import android.app.Activity;
import android.content.SharedPreferences;
import android.webkit.WebView;

import androidx.annotation.NonNull;

import com.android.billingclient.api.AcknowledgePurchaseParams;
import com.android.billingclient.api.BillingClient;
import com.android.billingclient.api.BillingClientStateListener;
import com.android.billingclient.api.BillingFlowParams;
import com.android.billingclient.api.BillingResult;
import com.android.billingclient.api.PendingPurchasesParams;
import com.android.billingclient.api.ProductDetails;
import com.android.billingclient.api.Purchase;
import com.android.billingclient.api.QueryProductDetailsParams;
import com.android.billingclient.api.QueryPurchasesParams;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.ump.ConsentInformation;
import com.google.android.ump.ConsentRequestParameters;
import com.google.android.ump.UserMessagingPlatform;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;

import java.util.Collections;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Play-Fassung: Vollbild-Werbung nach einem Spiel (AdMob), Einwilligung nach DSGVO (UMP)
 * und Einmalkauf "Werbung entfernen" über Google Play Billing.
 */
public class Monetization {
    static final String PRODUCT = "remove_ads";
    final Activity act;
    final WebView web;
    final SharedPreferences prefs;
    BillingClient billing;
    ProductDetails product;
    ConsentInformation consent;
    InterstitialAd interstitial;
    boolean adsRemoved;
    final AtomicBoolean adsStarted = new AtomicBoolean(false);

    public Monetization(Activity a, WebView w) {
        act = a; web = w;
        prefs = a.getSharedPreferences("oche_monetization", Activity.MODE_PRIVATE);
        adsRemoved = prefs.getBoolean("ads_removed", false);
    }

    public void init() {
        startBilling();
        if (!adsRemoved) requestConsent();
    }

    /* ---------- Einwilligung und Werbung ---------- */
    void requestConsent() {
        consent = UserMessagingPlatform.getConsentInformation(act);
        ConsentRequestParameters params = new ConsentRequestParameters.Builder().build();
        consent.requestConsentInfoUpdate(act, params,
                () -> UserMessagingPlatform.loadAndShowConsentFormIfRequired(act, err -> {
                    if (consent.canRequestAds()) startAds();
                    push();
                }),
                err -> { if (consent.canRequestAds()) startAds(); });
        if (consent.canRequestAds()) startAds();
    }

    void startAds() {
        if (adsRemoved || adsStarted.getAndSet(true)) return;
        new Thread(() -> MobileAds.initialize(act, status -> act.runOnUiThread(this::loadAd))).start();
    }

    void loadAd() {
        if (adsRemoved) return;
        InterstitialAd.load(act, BuildConfig.ADMOB_INTERSTITIAL, new AdRequest.Builder().build(), new InterstitialAdLoadCallback() {
            @Override public void onAdLoaded(@NonNull InterstitialAd ad) { interstitial = ad; }
            @Override public void onAdFailedToLoad(@NonNull LoadAdError e) { interstitial = null; }
        });
    }

    /** Wird nach einem beendeten Spiel aufgerufen. Ist keine Werbung geladen, passiert nichts. */
    public void showAfterGame() {
        if (adsRemoved) return;
        if (interstitial == null) { if (adsStarted.get()) loadAd(); return; }
        InterstitialAd ad = interstitial;
        interstitial = null;
        ad.setFullScreenContentCallback(new FullScreenContentCallback() {
            @Override public void onAdDismissedFullScreenContent() { loadAd(); }
            @Override public void onAdFailedToShowFullScreenContent(@NonNull AdError e) { loadAd(); }
        });
        ad.show(act);
    }

    /** Googles Bewertungsfenster (In-App Review). Google entscheidet selbst, ob und wie oft es erscheint. */
    public void askReview() {
        try {
            ReviewManager m = ReviewManagerFactory.create(act);
            m.requestReviewFlow().addOnCompleteListener(t -> {
                if (t.isSuccessful()) m.launchReviewFlow(act, t.getResult());
            });
        } catch (Exception ignored) { }
    }

    public void showPrivacyOptions() {
        if (consent != null) UserMessagingPlatform.showPrivacyOptionsForm(act, err -> push());
    }

    boolean privacyRequired() {
        return consent != null && consent.getPrivacyOptionsRequirementStatus() == ConsentInformation.PrivacyOptionsRequirementStatus.REQUIRED;
    }

    /* ---------- Einmalkauf "Werbung entfernen" ---------- */
    void startBilling() {
        billing = BillingClient.newBuilder(act)
                .setListener(this::onPurchases)
                .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
                .enableAutoServiceReconnection()
                .build();
        billing.startConnection(new BillingClientStateListener() {
            @Override public void onBillingSetupFinished(@NonNull BillingResult r) {
                if (r.getResponseCode() != BillingClient.BillingResponseCode.OK) return;
                queryProduct();
                billing.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build(),
                        (res, list) -> onPurchases(res, list));
            }
            @Override public void onBillingServiceDisconnected() { }
        });
    }

    void queryProduct() {
        QueryProductDetailsParams p = QueryProductDetailsParams.newBuilder().setProductList(Collections.singletonList(
                QueryProductDetailsParams.Product.newBuilder().setProductId(PRODUCT).setProductType(BillingClient.ProductType.INAPP).build())).build();
        billing.queryProductDetailsAsync(p, (res, result) -> {
            List<ProductDetails> list = result.getProductDetailsList();
            if (res.getResponseCode() == BillingClient.BillingResponseCode.OK && list != null && !list.isEmpty()) { product = list.get(0); push(); }
        });
    }

    public void buy() {
        if (product == null) { toast("Der Kauf ist gerade nicht verfügbar. Bitte später erneut versuchen."); queryProduct(); return; }
        BillingFlowParams params = BillingFlowParams.newBuilder().setProductDetailsParamsList(Collections.singletonList(
                BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(product).build())).build();
        billing.launchBillingFlow(act, params);
    }

    void onPurchases(BillingResult r, List<Purchase> purchases) {
        if (r.getResponseCode() != BillingClient.BillingResponseCode.OK || purchases == null) return;
        boolean owned = false;
        for (Purchase p : purchases) {
            if (!p.getProducts().contains(PRODUCT)) continue;
            if (p.getPurchaseState() == Purchase.PurchaseState.PURCHASED) {
                owned = true;
                if (!p.isAcknowledged())
                    billing.acknowledgePurchase(AcknowledgePurchaseParams.newBuilder().setPurchaseToken(p.getPurchaseToken()).build(), res -> { });
            } else if (p.getPurchaseState() == Purchase.PurchaseState.PENDING) {
                toast("Zahlung ausstehend. Die Werbung verschwindet, sobald sie bestätigt ist.");
            }
        }
        if (owned && !adsRemoved) toast("Danke! Die Werbung ist jetzt ausgeschaltet.");
        setAdsRemoved(owned);
    }

    void setAdsRemoved(boolean v) {
        adsRemoved = v;
        prefs.edit().putBoolean("ads_removed", v).apply();
        if (v) interstitial = null;
        push();
    }

    /* ---------- Zustand an die Web-App melden ---------- */
    public String stateJson() {
        String price = null;
        if (product != null && product.getOneTimePurchaseOfferDetails() != null) price = product.getOneTimePurchaseOfferDetails().getFormattedPrice();
        return "{\"enabled\":true,\"adsRemoved\":" + adsRemoved + ",\"privacy\":" + privacyRequired()
                + ",\"price\":" + (price == null ? "null" : "\"" + price.replace("\"", "") + "\"") + "}";
    }

    void push() {
        act.runOnUiThread(() -> web.evaluateJavascript("window.ocheMon&&window.ocheMon(" + stateJson() + ")", null));
    }

    void toast(String t) {
        act.runOnUiThread(() -> web.evaluateJavascript("window.ocheToast&&window.ocheToast(" + org.json.JSONObject.quote(t) + ")", null));
    }
}

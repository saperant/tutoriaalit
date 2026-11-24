package fi.tutoriaalit.palveluturva.salaisuudet;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;

/**
 * Jaettu salaisuus (esim. API-avain tai webhook-allekirjoituksen avain),
 * jonka voi kiertää ilman katkoa: kierron jälkeen sekä uusi että
 * edellinen avain kelpaavat siirtymäajan, jona asiakkaat ottavat uuden
 * käyttöön. Sen jälkeen vanha lakkaa kelpaamasta.
 */
public final class KierrettavaAvain {

    private final Clock kello;
    private final Duration siirtyma;
    private String nykyinen;
    private String edellinen;
    private Instant edellinenVanhenee = Instant.MIN;

    public KierrettavaAvain(String alku, Duration siirtyma, Clock kello) {
        this.nykyinen = alku;
        this.siirtyma = siirtyma;
        this.kello = kello;
    }

    // @alku kierra
    public synchronized void kierra(String uusi) {
        edellinen = nykyinen;
        edellinenVanhenee = kello.instant().plus(siirtyma);
        nykyinen = uusi;
    }

    public synchronized boolean kelpaa(String annettu) {
        if (vakioaikainen(annettu, nykyinen)) {
            return true;
        }
        return edellinen != null
                && kello.instant().isBefore(edellinenVanhenee)
                && vakioaikainen(annettu, edellinen);
    }
    // @loppu kierra

    private static boolean vakioaikainen(String a, String b) {
        return MessageDigest.isEqual(a.getBytes(StandardCharsets.UTF_8),
                b.getBytes(StandardCharsets.UTF_8));
    }
}

package fi.tutoriaalit.palveluturva.luottamus.reuna;

import java.time.Clock;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

/**
 * Kiinteän ikkunan nopeusrajoitin avaimittain (esim. käyttäjä tai
 * palvelu). Yksinkertaisin toimiva rajoitin; liukuva ikkuna ja
 * merkkiämpäri tasoittavat ikkunan rajan purskeet.
 */
public final class Nopeusrajoitin {

    private record Ikkuna(long alku, int maara) {}

    private final int raja;
    private final Duration pituus;
    private final Clock kello;
    private final Map<String, Ikkuna> ikkunat = new HashMap<>();

    public Nopeusrajoitin(int raja, Duration pituus, Clock kello) {
        this.raja = raja;
        this.pituus = pituus;
        this.kello = kello;
    }

    public synchronized boolean salli(String avain) {
        long ikkuna = kello.millis() / pituus.toMillis();
        Ikkuna nyt = ikkunat.get(avain);
        if (nyt == null || nyt.alku() != ikkuna) {
            nyt = new Ikkuna(ikkuna, 0);
        }
        if (nyt.maara() >= raja) {
            return false;
        }
        ikkunat.put(avain, new Ikkuna(ikkuna, nyt.maara() + 1));
        return true;
    }
}

package fi.tutoriaalit.palvelut.kauppa.laskutus;

import fi.tutoriaalit.palvelut.kauppa.laskutus.sisainen.LaskuTaulu;
import org.springframework.stereotype.Service;

/** Laskutuksen julkinen rajapinta. */
@Service
public class Laskut {
    private final LaskuTaulu taulu;

    Laskut(LaskuTaulu taulu) {
        this.taulu = taulu;
    }

    public int asiakkaanLaskuja(String asiakas) {
        return taulu.maara(asiakas);
    }
}

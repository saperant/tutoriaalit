package fi.tutoriaalit.palvelut.kauppa.myynti;

import fi.tutoriaalit.palvelut.kauppa.myynti.sisainen.TilausTaulu;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// @alku tilaukset
/** Myynnin julkinen rajapinta. Myynti ei tunne varastoa eikä
 *  laskutusta: se kertoo tapahtumalla, mitä tapahtui. */
@Service
public class Tilaukset {
    private final TilausTaulu taulu;
    private final ApplicationEventPublisher tapahtumat;

    Tilaukset(TilausTaulu taulu, ApplicationEventPublisher tapahtumat) {
        this.taulu = taulu;
        this.tapahtumat = tapahtumat;
    }

    @Transactional
    public long tilaa(String asiakas, String tuote, int maara) {
        long id = taulu.lisaa(asiakas, tuote, maara);
        tapahtumat.publishEvent(
                new TilausTehty(id, asiakas, tuote, maara));
        return id;
    }
    // @loppu tilaukset

    public int maara() {
        return taulu.maara();
    }
}

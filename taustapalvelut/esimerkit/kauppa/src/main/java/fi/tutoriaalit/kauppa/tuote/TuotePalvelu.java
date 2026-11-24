package fi.tutoriaalit.kauppa.tuote;

import fi.tutoriaalit.kauppa.virheet.EiLoydy;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

// @alku palvelu
/**
 * Sovelluslogiikka. Ohjain ei tunne tietokantaa eikä repository
 * HTTP:tä; palvelu omistaa transaktiorajan.
 */
@Service
public class TuotePalvelu {

    private final TuoteRepository tuotteet;

    // Konstruktori-injektio: riippuvuudet ovat näkyvissä ja lopullisia,
    // ja luokkaa voi testata ilman Springiä.
    public TuotePalvelu(TuoteRepository tuotteet) {
        this.tuotteet = tuotteet;
    }

    @Transactional(readOnly = true)
    public Page<Tuote> sivu(int sivu, int koko) {
        return tuotteet.findAll(
                PageRequest.of(sivu, koko, Sort.by("nimi").ascending()));
    }

    @Transactional(readOnly = true)
    public Tuote hae(long id) {
        return tuotteet.findById(id)
                .orElseThrow(() -> new EiLoydy("tuote", id));
    }

    @Transactional
    public Tuote lisaa(String nimi, long hintaSentteina, int saldo) {
        return tuotteet.save(Tuote.uusi(nimi, hintaSentteina, saldo));
    }

    /**
     * Muuttaa hinnan, jos asiakas on nähnyt tuotteen uusimman version.
     * Muuten joku muu on muuttanut tuotetta välissä (kadonnut päivitys).
     */
    @Transactional
    public Tuote muutaHinta(long id, long odotettuVersio, long uusiHinta) {
        Tuote nykyinen = hae(id);
        if (nykyinen.versio() != odotettuVersio) {
            throw new OptimisticLockingFailureException("versio muuttui");
        }
        return tuotteet.save(nykyinen.hinnalla(uusiHinta));
    }
}
// @loppu palvelu

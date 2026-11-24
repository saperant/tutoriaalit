package fi.tutoriaalit.palvelut.viestit.myynti;

import fi.tutoriaalit.palvelut.viestit.yhteinen.Viesti;
import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Myynnin julkinen toiminto: tilauksen aloittaminen. */
@Service
public class Tilaukset {
    private final JdbcClient jdbc;
    private final Lahtevat lahtevat;

    Tilaukset(JdbcClient jdbc, Lahtevat lahtevat) {
        this.jdbc = jdbc;
        this.lahtevat = lahtevat;
    }

    // @alku aloita
    /** Tallentaa tilauksen ja ensimmäisen komennon. Palauttaa heti:
     *  tilaus etenee taustalla, ja asiakas näkee tilan ALOITETTU. */
    @Transactional
    public long aloita(String asiakas, String tuote, int maara,
                       BigDecimal summa) {
        var avain = new GeneratedKeyHolder();
        jdbc.sql("""
                INSERT INTO myynti.tilaus (asiakas, tuote, maara, summa, tila)
                VALUES (?, ?, ?, ?, 'ALOITETTU')""")
            .params(asiakas, tuote, maara, summa).update(avain, "id");
        long id = avain.getKeyAs(Long.class);
        lahtevat.lisaa("varasto.komennot", "VARAA", id,
                Viesti.json(Map.of("tuote", tuote, "maara", maara)));
        return id;
    }
    // @loppu aloita

    public Optional<Tila> tila(long id) {
        return jdbc.sql("SELECT tila FROM myynti.tilaus WHERE id = ?")
            .param(id).query(Tila.class).optional();
    }
}

package fi.tutoriaalit.kauppa.raportti;

import java.util.List;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

// @alku raportti
/**
 * Raportit ovat kyselyitä, eivät aggregaatteja: JdbcClient ja SQL
 * suoraan, tulos suoraan tietueeksi (sarake myynti_sentteina →
 * kenttä myyntiSentteina).
 */
@Repository
public class MyyntiRaportti {

    public record Myynti(String nimi, long kappaleet, long myyntiSentteina) {
    }

    private final JdbcClient jdbc;

    public MyyntiRaportti(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public List<Myynti> parhaat(int montako) {
        return jdbc.sql("""
                SELECT t.nimi,
                       SUM(r.maara) AS kappaleet,
                       SUM(r.maara * r.hinta_sentteina) AS myynti_sentteina
                  FROM tilaus_rivi r
                  JOIN tuote t ON t.id = r.tuote_id
                 GROUP BY t.nimi
                 ORDER BY myynti_sentteina DESC, t.nimi
                 LIMIT :montako
                """)
                .param("montako", montako)
                .query(Myynti.class)
                .list();
    }

    /** Tilausten summat yhdellä kyselyllä (vrt. N+1 luvussa 5). */
    public List<Long> tilaustenSummat() {
        return jdbc.sql("""
                SELECT SUM(r.maara * r.hinta_sentteina)
                  FROM tilaus_rivi r
                 GROUP BY r.tilaus
                 ORDER BY r.tilaus
                """)
                .query(Long.class)
                .list();
    }
}
// @loppu raportti

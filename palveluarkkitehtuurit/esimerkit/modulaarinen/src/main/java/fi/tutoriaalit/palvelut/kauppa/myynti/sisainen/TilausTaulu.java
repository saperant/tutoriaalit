package fi.tutoriaalit.palvelut.kauppa.myynti.sisainen;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jdbc.support.GeneratedKeyHolder;
import org.springframework.stereotype.Repository;

/** Myynnin oma taulu. Luokan on oltava julkinen, jotta moduulin
 *  juuripaketti voi käyttää sitä; muut moduulit eivät saa. */
@Repository
public class TilausTaulu {
    private final JdbcClient jdbc;

    TilausTaulu(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public long lisaa(String asiakas, String tuote, int maara) {
        var avain = new GeneratedKeyHolder();
        jdbc.sql("""
                INSERT INTO myynti_tilaus (asiakas, tuote, maara)
                VALUES (?, ?, ?)""")
            .params(asiakas, tuote, maara)
            .update(avain, "id");
        return avain.getKeyAs(Long.class);
    }

    public int maara() {
        return jdbc.sql("SELECT count(*) FROM myynti_tilaus")
            .query(Integer.class).single();
    }
}

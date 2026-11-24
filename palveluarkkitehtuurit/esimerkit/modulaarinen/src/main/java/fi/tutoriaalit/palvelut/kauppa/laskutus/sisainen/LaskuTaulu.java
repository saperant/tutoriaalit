package fi.tutoriaalit.palvelut.kauppa.laskutus.sisainen;

import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Repository;

@Repository
public class LaskuTaulu {
    private final JdbcClient jdbc;

    LaskuTaulu(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    public void lisaa(long tilausId, String asiakas) {
        jdbc.sql("""
                INSERT INTO laskutus_lasku (tilaus_id, asiakas)
                VALUES (?, ?)""")
            .params(tilausId, asiakas).update();
    }

    public int maara(String asiakas) {
        return jdbc.sql(
                "SELECT count(*) FROM laskutus_lasku WHERE asiakas = ?")
            .param(asiakas).query(Integer.class).single();
    }
}

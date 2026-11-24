package fi.tutoriaalit.palvelut.viestit;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.palvelut.viestit.myynti.Tilaukset;
import fi.tutoriaalit.palvelut.viestit.yhteinen.Lahettaja;
import java.math.BigDecimal;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.jms.core.JmsTemplate;
import org.springframework.transaction.support.TransactionTemplate;

@SpringBootTest
class ViestitTest {
    @Autowired Lahettaja lahettaja;
    @Autowired JmsTemplate jms;
    @Autowired JdbcClient jdbc;
    @Autowired Tilaukset tilaukset;
    @Autowired TransactionTemplate transaktio;

    int saldo(String tuote) {
        return jdbc.sql("SELECT saldo FROM varasto.saldo WHERE tuote = ?")
            .param(tuote).query(Integer.class).single();
    }

    // @alku toisto
    @Test
    void toistettuKomentoKasitellaanKerran() {
        String runko = "{\"tuote\": \"leivanpaahdin\", \"maara\": 1}";
        for (int i = 0; i < 2; i++) {       // sama viestiId kahdesti
            lahettaja.laheta("varasto.komennot", "varaa-77", "VARAA",
                    "77", runko);
        }
        // Jonolla on yksi kuluttaja, joten viestit käsitellään
        // järjestyksessä: kun merkkiviesti on käsitelty, on toistokin.
        lahettaja.laheta("varasto.komennot", "merkki-78", "VARAA", "78",
                "{\"tuote\": \"tehosekoitin\", \"maara\": 0}");
        Odota.kunnes(() -> kasiteltyja("merkki-78") == 1);
        assertThat(kasiteltyja("varaa-77")).isEqualTo(1);
        assertThat(saldo("leivanpaahdin")).isEqualTo(4);   // ei 3
    }

    int kasiteltyja(String viestiId) {
        return jdbc.sql(
                "SELECT count(*) FROM varasto.saapuneet WHERE viesti_id = ?")
            .param(viestiId).query(Integer.class).single();
    }
    // @loppu toisto

    // @alku myrkky
    @Test
    void kasittelematonViestiPaatyyKuolleidenKirjeidenJonoon()
            throws Exception {
        lahettaja.laheta("varasto.komennot", "myrkky-1", "TUNTEMATON",
                "0", "{}");
        jms.setReceiveTimeout(10_000);
        var kuollut = jms.receive("DLQ");
        assertThat(kuollut).isNotNull();
        assertThat(kuollut.getStringProperty("viestiId"))
            .isEqualTo("myrkky-1");
        // Välittäjä kertoo, mistä jonosta viesti tuli.
        assertThat(kuollut.getStringProperty("_AMQ_ORIG_ADDRESS"))
            .isEqualTo("varasto.komennot");
    }
    // @loppu myrkky

    // @alku outbox
    @Test
    void peruttuTransaktioEiLahetaMitaan() {
        int ennen = lahtevia();
        transaktio.executeWithoutResult(tila -> {
            tilaukset.aloita("aino", "tehosekoitin", 1,
                    new BigDecimal("40.00"));
            tila.setRollbackOnly();        // jokin muu meni pieleen
        });
        // Tilaus ja sen VARAA-komento katosivat yhdessä.
        assertThat(lahtevia()).isEqualTo(ennen);
        assertThat(saldo("tehosekoitin")).isEqualTo(5);
    }

    int lahtevia() {
        return jdbc.sql("SELECT count(*) FROM myynti.lahtevat")
            .query(Integer.class).single();
    }
    // @loppu outbox
}

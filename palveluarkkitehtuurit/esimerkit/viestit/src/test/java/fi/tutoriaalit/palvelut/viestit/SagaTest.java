package fi.tutoriaalit.palvelut.viestit;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.palvelut.viestit.myynti.Tila;
import fi.tutoriaalit.palvelut.viestit.myynti.Tilaukset;
import java.math.BigDecimal;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.simple.JdbcClient;

@SpringBootTest
class SagaTest {
    @Autowired Tilaukset tilaukset;
    @Autowired JdbcClient jdbc;

    int saldo(String tuote) {
        return jdbc.sql("SELECT saldo FROM varasto.saldo WHERE tuote = ?")
            .param(tuote).query(Integer.class).single();
    }

    boolean loytyy(String taulu, long tilaus) {
        return jdbc.sql("SELECT count(*) FROM " + taulu
                + " WHERE tilaus_id = ?").param(String.valueOf(tilaus))
            .query(Integer.class).single() == 1;
    }

    void odotaTila(long id, Tila tila) {
        Odota.kunnes(() -> tilaukset.tila(id).equals(Optional.of(tila)));
    }

    // @alku onnistuu
    @Test
    void onnistunutTilausVahvistetaanJaTapahtumaJulkaistaan() {
        long id = tilaukset.aloita("aino", "kahvinkeitin", 2,
                new BigDecimal("98.00"));
        odotaTila(id, Tila.VAHVISTETTU);
        assertThat(saldo("kahvinkeitin")).isEqualTo(3);
        // Julkaise–tilaa: sekä toimitus että laskutus saivat tapahtuman.
        Odota.kunnes(() -> loytyy("toimitus.lahetys", id)
                && loytyy("laskutus.lasku", id));
    }
    // @loppu onnistuu

    // @alku kompensaatio
    @Test
    void hylattyMaksuPeruuVarauksen() {
        long id = tilaukset.aloita("eero", "vedenkeitin", 3,
                new BigDecimal("900.00"));       // yli luottorajan
        odotaTila(id, Tila.PERUTTU);
        assertThat(saldo("vedenkeitin")).isEqualTo(5);   // palautettu
        assertThat(loytyy("maksut.veloitus", id)).isFalse();
        assertThat(loytyy("toimitus.lahetys", id)).isFalse();
    }

    @Test
    void loppunutTuotePerutaanEnnenVeloitusta() {
        long id = tilaukset.aloita("eero", "mikroaaltouuni", 2,
                new BigDecimal("150.00"));
        odotaTila(id, Tila.PERUTTU);
        assertThat(saldo("mikroaaltouuni")).isEqualTo(1);
        assertThat(loytyy("maksut.veloitus", id)).isFalse();
    }
    // @loppu kompensaatio
}

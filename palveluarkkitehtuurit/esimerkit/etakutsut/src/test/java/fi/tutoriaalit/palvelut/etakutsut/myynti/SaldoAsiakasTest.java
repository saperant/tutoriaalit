package fi.tutoriaalit.palvelut.etakutsut.myynti;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import fi.tutoriaalit.palvelut.etakutsut.Valepalvelin;
import fi.tutoriaalit.palvelut.etakutsut.Valepalvelin.Vastaus;
import fi.tutoriaalit.palvelut.etakutsut.kestavyys.Uudelleenyritys;
import io.github.resilience4j.circuitbreaker.CallNotPermittedException;
import java.time.Duration;
import java.util.Random;
import org.junit.jupiter.api.Test;

class SaldoAsiakasTest {
    static final String SALDO = "{\"tuote\": \"kahvinkeitin\", \"saldo\": 3}";

    static SaldoAsiakas asiakas(Valepalvelin vale, int yrityksia) {
        var uudelleen = new Uudelleenyritys(yrityksia,
                Duration.ofMillis(10), Duration.ofMillis(100),
                new Random(42));
        return new SaldoAsiakas(vale.palvelin().osoite(),
                Duration.ofMillis(200), uudelleen,
                Katkaisijat.varastolle(Duration.ofMinutes(1)));
    }

    // @alku aikaraja
    @Test
    void aikarajaKatkaiseeHitaanVastauksen() {
        try (var vale = new Valepalvelin(
                n -> Vastaus.hidas(Duration.ofSeconds(2)))) {
            long alku = System.nanoTime();
            assertThatThrownBy(() -> asiakas(vale, 1).saldo("kahvinkeitin"))
                .isInstanceOf(PalveluEiVastaa.class);
            // Odotettiin aikarajan verran, ei kahta sekuntia.
            assertThat(Duration.ofNanos(System.nanoTime() - alku))
                .isLessThan(Duration.ofSeconds(1));
        }
    }
    // @loppu aikaraja

    // @alku uudelleen
    @Test
    void uudelleenyritysYlittaaOhimenevanVirheen() {
        try (var vale = new Valepalvelin(
                n -> n <= 2 ? Vastaus.virhe(503) : Vastaus.ok(SALDO))) {
            assertThat(asiakas(vale, 3).saldo("kahvinkeitin")).isEqualTo(3);
            assertThat(vale.kutsuja()).isEqualTo(3);
        }
    }

    @Test
    void pysyvaaVirhettaEiYritetaUudelleen() {
        try (var vale = new Valepalvelin(n -> Vastaus.virhe(404))) {
            assertThatThrownBy(() -> asiakas(vale, 3).saldo("teekeitin"))
                .isInstanceOf(TuntematonTuote.class);
            assertThat(vale.kutsuja()).isEqualTo(1);
        }
    }
    // @loppu uudelleen

    // @alku katkaisija
    @Test
    void katkaisijaLopettaaKutsutKaatuneeseenPalveluun() {
        try (var vale = new Valepalvelin(n -> Vastaus.virhe(503))) {
            var asiakas = asiakas(vale, 2);
            // Kaksi saldokyselyä, kumpikin kaksi yritystä: neljä
            // epäonnistunutta kutsua avaa katkaisijan.
            for (int i = 0; i < 2; i++) {
                assertThatThrownBy(() -> asiakas.saldo("kahvinkeitin"))
                    .isInstanceOf(PalveluEiVastaa.class);
            }
            assertThat(vale.kutsuja()).isEqualTo(4);
            // Nyt kutsu epäonnistuu heti lähtemättä verkkoon.
            assertThatThrownBy(() -> asiakas.saldo("kahvinkeitin"))
                .isInstanceOf(CallNotPermittedException.class);
            assertThat(vale.kutsuja()).isEqualTo(4);
        }
    }
    // @loppu katkaisija
}

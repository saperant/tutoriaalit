package fi.tutoriaalit.palvelut.etakutsut.sopimus;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import fi.tutoriaalit.palvelut.etakutsut.kestavyys.Uudelleenyritys;
import fi.tutoriaalit.palvelut.etakutsut.myynti.Katkaisijat;
import fi.tutoriaalit.palvelut.etakutsut.myynti.SaldoAsiakas;
import fi.tutoriaalit.palvelut.etakutsut.myynti.TuntematonTuote;
import fi.tutoriaalit.palvelut.etakutsut.varasto.VarastoPalvelin;
import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;
import org.junit.jupiter.api.Test;

class SopimusTest {
    static Sopimus sopimus() {
        return Sopimus.lue(SopimusTest.class.getResourceAsStream(
                "/sopimukset/myynti-varasto.json"));
    }

    // @alku kuluttaja
    /** Kuluttajan puoli: myynnin asiakas toimii sopimuksen vastauksilla. */
    @Test
    void kuluttajaToimiiSopimuksenVastauksilla() {
        try (var vale = SopimusPalvelin.kaynnista(sopimus())) {
            var asiakas = new SaldoAsiakas(vale.osoite(),
                    Duration.ofSeconds(1),
                    new Uudelleenyritys(1, Duration.ZERO, Duration.ZERO,
                            new Random()),
                    Katkaisijat.varastolle(Duration.ofMinutes(1)));
            assertThat(asiakas.saldo("kahvinkeitin")).isEqualTo(3);
            assertThatThrownBy(() -> asiakas.saldo("teekeitin"))
                .isInstanceOf(TuntematonTuote.class);
        }
    }
    // @loppu kuluttaja

    // @alku tuottaja
    /** Tuottajan puoli: oikea varastopalvelu täyttää sopimuksen. */
    @Test
    void tuottajaTayttaaSopimuksen() throws Exception {
        Map<String, Integer> saldot = new HashMap<>();
        try (var varasto = VarastoPalvelin.kaynnista(saldot)) {
            var poikkeamat = SopimusTarkistin.tarkista(sopimus(),
                    varasto.osoite(), Map.of(
                        "kahvinkeittimiä on kolme",
                        () -> saldot.put("kahvinkeitin", 3),
                        "teekeitintä ei ole",
                        () -> saldot.remove("teekeitin")));
            assertThat(poikkeamat).isEmpty();
        }
    }

    /** Tuottaja nimeää kentän uudelleen: sopimustesti huomaa sen ennen
     *  kuin myynti hajoaa tuotannossa. */
    @Test
    void kentanUudelleennimeaminenRikkooSopimuksen() throws Exception {
        try (Palvelin muutettu = Palvelin.kaynnista(vaihto -> {
            Palvelin.vastaa(vaihto, 200,
                    "{\"tuote\": \"kahvinkeitin\", \"maara\": 3}");
        })) {
            var poikkeamat = SopimusTarkistin.tarkista(sopimus(),
                    muutettu.osoite(), Map.of());
            assertThat(poikkeamat).containsExactly(
                    "tunnetun tuotteen saldo: kenttä puuttuu: saldo",
                    "tuntematon tuote: tila 200");
        }
    }
    // @loppu tuottaja
}

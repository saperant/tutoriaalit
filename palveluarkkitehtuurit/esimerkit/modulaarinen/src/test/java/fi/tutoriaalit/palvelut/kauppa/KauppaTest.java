package fi.tutoriaalit.palvelut.kauppa;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import fi.tutoriaalit.palvelut.kauppa.laskutus.Laskut;
import fi.tutoriaalit.palvelut.kauppa.myynti.Tilaukset;
import fi.tutoriaalit.palvelut.kauppa.varasto.SaldoEiRiita;
import fi.tutoriaalit.palvelut.kauppa.varasto.Varasto;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class KauppaTest {
    @Autowired Tilaukset tilaukset;
    @Autowired Varasto varasto;
    @Autowired Laskut laskut;

    // @alku testit
    @Test
    void tilausVaraaTuotteetJaLaskuttaa() {
        int ennen = varasto.saldo("vedenkeitin");
        tilaukset.tilaa("aino", "vedenkeitin", 2);
        assertThat(varasto.saldo("vedenkeitin")).isEqualTo(ennen - 2);
        assertThat(laskut.asiakkaanLaskuja("aino")).isEqualTo(1);
    }

    @Test
    void liianSuuriTilausPerutaanKokonaan() {
        int tilauksia = tilaukset.maara();
        assertThatThrownBy(
                () -> tilaukset.tilaa("eero", "kahvinkeitin", 99))
            .isInstanceOf(SaldoEiRiita.class);
        // Yksi transaktio yli moduulien: mitään ei jäänyt kesken.
        assertThat(tilaukset.maara()).isEqualTo(tilauksia);
        assertThat(varasto.saldo("kahvinkeitin")).isEqualTo(3);
        assertThat(laskut.asiakkaanLaskuja("eero")).isZero();
    }
    // @loppu testit
}

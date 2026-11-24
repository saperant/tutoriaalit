package fi.tutoriaalit.palvelut.uudistus.uusi;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import fi.tutoriaalit.palvelut.uudistus.Http;
import fi.tutoriaalit.palvelut.uudistus.vanha.Asiakasrekisteri;
import java.time.LocalDate;
import java.util.Map;
import org.junit.jupiter.api.Test;

class KorruptionestokerrosTest {
    // @alku kaanna
    @Test
    void vanhaRiviKaannetaanUudenMallinAsiakkaaksi() {
        Asiakas a = Korruptionestokerros.kaanna(
                "1001;VIRTANEN AINO;A;20230115");
        assertThat(a).isEqualTo(new Asiakas("1001", "Aino", "Virtanen",
                Asiakas.Tila.AKTIIVINEN, LocalDate.of(2023, 1, 15)));
    }

    @Test
    void tuntematonTilakoodiEiValuUuteenMalliin() {
        assertThatThrownBy(() -> Korruptionestokerros.kaanna(
                "1002;KORHONEN EERO;X;20240301"))
            .isInstanceOf(IllegalArgumentException.class);
    }
    // @loppu kaanna

    @Test
    void uusiPalveluLukeeVanhaaDataaKerroksenKautta() {
        var vanha = Asiakasrekisteri.kaynnista(Map.of(
                "1001", "1001;VIRTANEN AINO;K;20230115"));
        var uusi = Asiakaspalvelu.kaynnista(
                new Korruptionestokerros(Http.osoite(vanha)));
        try {
            var vastaus = Http.hae(Http.osoite(uusi)
                    .resolve("/asiakkaat/1001"));
            assertThat(vastaus.runko())
                .contains("\"sukunimi\": \"Virtanen\"")
                .contains("\"tila\": \"ESTETTY\"")
                .contains("\"asiakkaanaAlkaen\": \"2023-01-15\"");
            assertThat(Http.hae(Http.osoite(uusi)
                    .resolve("/asiakkaat/9999")).tila()).isEqualTo(404);
        } finally {
            uusi.stop(0);
            vanha.stop(0);
        }
    }
}

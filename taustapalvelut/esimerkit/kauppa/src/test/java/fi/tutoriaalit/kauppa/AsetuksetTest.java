package fi.tutoriaalit.kauppa;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.boot.context.properties.*;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.context.annotation.Configuration;

// @alku asetukset
/** ApplicationContextRunner käynnistää pienen kontekstin nopeasti. */
class AsetuksetTest {

    @Configuration
    @EnableConfigurationProperties(KauppaAsetukset.class)
    static class Kokoonpano {
    }

    private final ApplicationContextRunner konteksti =
            new ApplicationContextRunner()
                    .withUserConfiguration(Kokoonpano.class)
                    .withPropertyValues(
                            "kauppa.sallitut-alkuperat=https://k.example",
                            "kauppa.sivun-enimmaiskoko=50");

    @Test
    void kelvollisetArvotSidotaanTietueeseen() {
        konteksti.withPropertyValues("kauppa.maksimirivit=10")
                .run(k -> assertThat(k.getBean(KauppaAsetukset.class))
                        .extracting(KauppaAsetukset::maksimirivit)
                        .isEqualTo(10));
    }

    @Test
    void virheellinenArvoEstaaKaynnistyksen() {
        konteksti.withPropertyValues("kauppa.maksimirivit=0")
                .run(k -> assertThat(k).hasFailed()
                        .getFailure().rootCause()
                        .hasMessageContaining("maksimirivit"));
    }
}
// @loppu asetukset

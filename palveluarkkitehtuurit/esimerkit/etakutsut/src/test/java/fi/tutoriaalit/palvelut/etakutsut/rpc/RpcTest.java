package fi.tutoriaalit.palvelut.etakutsut.rpc;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.io.UncheckedIOException;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;
import org.junit.jupiter.api.Test;

class RpcTest {
    static final Duration SEKUNTI = Duration.ofSeconds(1);

    static class PaikallinenHinnasto implements Hinnasto {
        final Map<String, Integer> hinnat =
            Map.of("kahvinkeitin", 49, "vedenkeitin", 29);

        @Override
        public int hinta(String tuote) {
            return hinnat.get(tuote);
        }

        @Override
        public List<String> tuotteet() {
            return hinnat.keySet().stream().sorted().toList();
        }
    }

    // @alku sama
    @Test
    void etakutsuNayttaaPaikalliselta() {
        Hinnasto paikallinen = new PaikallinenHinnasto();
        try (var palvelin = Rpc.julkaise(Hinnasto.class, paikallinen)) {
            Hinnasto eta = Rpc.asiakas(Hinnasto.class, palvelin.osoite(),
                    SEKUNTI);
            assertThat(eta.hinta("kahvinkeitin")).isEqualTo(49);
            assertThat(eta.tuotteet())
                .isEqualTo(paikallinen.tuotteet());
        }
    }
    // @loppu sama

    // @alku hinta
    @Test
    void etakutsuOnKertaluokkiaHitaampi() {
        Hinnasto paikallinen = new PaikallinenHinnasto();
        try (var palvelin = Rpc.julkaise(Hinnasto.class, paikallinen)) {
            Hinnasto eta = Rpc.asiakas(Hinnasto.class, palvelin.osoite(),
                    SEKUNTI);
            long paikallisesti = kutsunKesto(paikallinen, 100_000);
            long etana = kutsunKesto(eta, 300);
            // Saman koneen sisälläkin ero on tuhatkertainen tai enemmän.
            assertThat(etana).isGreaterThan(100 * paikallisesti);
        }
    }

    /** Keskimääräinen kesto nanosekunteina (paras kolmesta). */
    static long kutsunKesto(Hinnasto hinnasto, int kertaa) {
        long paras = Long.MAX_VALUE;
        long summa = 0;
        for (int kierros = 0; kierros < 3; kierros++) {
            long alku = System.nanoTime();
            for (int i = 0; i < kertaa; i++) {
                summa += hinnasto.hinta("kahvinkeitin");
            }
            paras = Math.min(paras, (System.nanoTime() - alku) / kertaa);
        }
        assertThat(summa).isPositive();      // ei saa optimoitua pois
        return Math.max(paras, 1);
    }
    // @loppu hinta

    // @alku viat
    @Test
    void kaatunutPalvelinNakyyKutsujalle() {
        var palvelin = Rpc.julkaise(Hinnasto.class,
                new PaikallinenHinnasto());
        Hinnasto eta = Rpc.asiakas(Hinnasto.class, palvelin.osoite(),
                SEKUNTI);
        palvelin.close();
        assertThatThrownBy(() -> eta.hinta("kahvinkeitin"))
            .isInstanceOf(UncheckedIOException.class);
    }

    @Test
    void aikakatkaisuJattaaLopputuloksenAuki() throws Exception {
        var tehdyt = new AtomicInteger();
        Tilauspalvelu hidas = tuote -> {
            tehdyt.incrementAndGet();        // tilaus tallennettiin...
            nuku(Duration.ofMillis(500));    // ...mutta vastaus viipyy
        };
        try (var palvelin = Rpc.julkaise(Tilauspalvelu.class, hidas)) {
            Tilauspalvelu eta = Rpc.asiakas(Tilauspalvelu.class,
                    palvelin.osoite(), Duration.ofMillis(100));
            assertThatThrownBy(() -> eta.tilaa("kahvinkeitin"))
                .isInstanceOf(UncheckedIOException.class);
            // Kutsuja sai virheen, mutta tilaus tehtiin silti.
            Thread.sleep(600);
            assertThat(tehdyt).hasValue(1);
        }
    }
    // @loppu viat

    static void nuku(Duration aika) {
        try {
            Thread.sleep(aika);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

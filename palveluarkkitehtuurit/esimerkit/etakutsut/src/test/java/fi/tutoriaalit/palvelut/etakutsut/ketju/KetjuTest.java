package fi.tutoriaalit.palvelut.etakutsut.ketju;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.within;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.Test;

class KetjuTest {
    static final Duration TYO = Duration.ofMillis(40);

    // @alku viive
    @Test
    void kutsuketjunViiveetLaskevatYhteen() {
        List<Palvelin> ketju = Ketju.rakenna(4, TYO);
        try {
            Ketju.hae(ketju.getFirst().osoite());      // lämmittely
            long alku = System.nanoTime();
            Ketju.hae(ketju.getFirst().osoite());
            var kesto = Duration.ofNanos(System.nanoTime() - alku);
            // Neljä palvelua peräkkäin: vähintään 4 x 40 ms.
            assertThat(kesto).isGreaterThanOrEqualTo(TYO.multipliedBy(4));
        } finally {
            ketju.forEach(Palvelin::close);
        }
    }

    @Test
    void rinnakkaisetKutsutMaksavatHitaimmanVerran() throws Exception {
        // Neljä toisistaan riippumatonta palvelua kutsutaan yhtä aikaa.
        List<Palvelin> palvelut = List.of(Ketju.rakenna(1, TYO).getFirst(),
                Ketju.rakenna(1, TYO).getFirst(),
                Ketju.rakenna(1, TYO).getFirst(),
                Ketju.rakenna(1, TYO).getFirst());
        try (var saikeet = Executors.newVirtualThreadPerTaskExecutor()) {
            palvelut.forEach(p -> Ketju.hae(p.osoite()));  // lämmittely
            long alku = System.nanoTime();
            var tulokset = palvelut.stream()
                .map(p -> saikeet.submit(() -> Ketju.hae(p.osoite())))
                .toList();
            for (var t : tulokset) {
                t.get();
            }
            var kesto = Duration.ofNanos(System.nanoTime() - alku);
            assertThat(kesto).isLessThan(TYO.multipliedBy(3));
        } finally {
            palvelut.forEach(Palvelin::close);
        }
    }
    // @loppu viive

    // @alku saatavuus
    @Test
    void ketjunSaatavuusOnTulo() {
        // Viisi palvelua, kukin toiminnassa 99 % ajasta.
        double ketju = Saatavuus.ketjun(0.99, 5, 1_000_000, 1);
        assertThat(ketju).isCloseTo(Math.pow(0.99, 5), within(0.001));
        assertThat(ketju).isLessThan(0.952);   // 4,9 % pyynnöistä kaatuu
    }
    // @loppu saatavuus
}

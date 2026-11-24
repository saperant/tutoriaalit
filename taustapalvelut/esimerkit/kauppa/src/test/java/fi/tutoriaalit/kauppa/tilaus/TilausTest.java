package fi.tutoriaalit.kauppa.tilaus;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;

// @alku yksikko
/** Yksikkötesti: ei Springiä, ei tietokantaa – millisekunteja. */
class TilausTest {

    @Test
    void summaLasketaanRivienHinnoistaSentteina() {
        var tilaus = new Tilaus(null, "aino", Instant.EPOCH, List.of(
                new TilausRivi(1, 3, 1290),
                new TilausRivi(2, 1, 590)));
        assertThat(tilaus.summaSentteina()).isEqualTo(3 * 1290 + 590);
    }
}
// @loppu yksikko

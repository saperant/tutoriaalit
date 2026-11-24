package fi.tutoriaalit.kauppa.raportti;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.kauppa.tilaus.Tilaus;
import fi.tutoriaalit.kauppa.tilaus.TilausRepository;
import fi.tutoriaalit.kauppa.tilaus.TilausRivi;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jdbc.test.autoconfigure.DataJdbcTest;
import org.springframework.boot.jdbc.test.autoconfigure.*;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

// @alku nplus1
@DataJdbcTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@ActiveProfiles("test")
@Import({KyselyLaskuri.class, MyyntiRaportti.class})
class NPlusYksiTest {

    @Autowired
    TilausRepository tilaukset;

    @Autowired
    MyyntiRaportti raportti;

    @Autowired
    KyselyLaskuri laskuri;

    @Test
    void aggregaattienLatausOnYksiPlusNKyselyaRaporttiYksi() {
        for (int i = 0; i < 20; i++) {
            tilaukset.save(new Tilaus(null, "aino", Instant.EPOCH,
                    List.of(new TilausRivi(1, 1, 1290),
                            new TilausRivi(2, 2, 590))));
        }

        laskuri.nollaa();
        long summa = tilaukset.findAll().stream()
                .mapToLong(Tilaus::summaSentteina).sum();
        int aggregaateilla = laskuri.lauseet();

        laskuri.nollaa();
        long summa2 = raportti.tilaustenSummat().stream()
                .mapToLong(Long::longValue).sum();
        int kyselylla = laskuri.lauseet();

        assertThat(summa2).isEqualTo(summa);
        assertThat(aggregaateilla).isEqualTo(1 + 20);  // juuret + rivit
        assertThat(kyselylla).isEqualTo(1);
    }
}
// @loppu nplus1

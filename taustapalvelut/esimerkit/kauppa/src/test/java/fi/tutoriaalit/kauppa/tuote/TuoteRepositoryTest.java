package fi.tutoriaalit.kauppa.tuote;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jdbc.test.autoconfigure.DataJdbcTest;
import org.springframework.boot.jdbc.test.autoconfigure.*;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.test.context.ActiveProfiles;

// @alku viipale
/**
 * Viipaletesti: vain tietokantakerros (DataSource, Flyway, Spring Data
 * JDBC). Jokainen testi ajetaan transaktiossa, joka perutaan lopuksi.
 * Replace.NONE: käytetään sovelluksen omaa tietokanta-asetusta eikä
 * Springin generoimaa upotettua kantaa.
 */
@DataJdbcTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@ActiveProfiles("test")
class TuoteRepositoryTest {

    @Autowired
    TuoteRepository tuotteet;

    @Test
    void migraatiotJaTestiaineistoOvatPaikallaan() {
        assertThat(tuotteet.findByNimi("Kahvikuppi"))
                .hasValueSatisfying(t -> assertThat(t.saldo()).isEqualTo(3));
    }
    // @loppu viipale

    @Test
    void sivutusJaJarjestys() {
        var sivu = tuotteet.findBySaldoGreaterThan(5,
                PageRequest.of(0, 2, Sort.by("hintaSentteina")));
        assertThat(sivu.getTotalElements()).isEqualTo(3);
        assertThat(sivu.getContent()).extracting(Tuote::nimi)
                .containsExactly("Vihreä tee", "Kahvipavut 500 g");
    }

    // @alku optimistinen
    @Test
    void optimistinenLukitusHylkaaVanhentuneenKopion() {
        Tuote anna = tuotteet.findByNimi("Vihreä tee").orElseThrow();
        Tuote pekka = tuotteet.findByNimi("Vihreä tee").orElseThrow();

        Tuote tallennettu = tuotteet.save(anna.hinnalla(650));
        assertThat(tallennettu.versio()).isEqualTo(anna.versio() + 1);

        // Pekan kopio on vanhan version pohjalta: UPDATE ... WHERE
        // versio = ? ei osu yhteenkään riviin.
        assertThatThrownBy(() -> tuotteet.save(pekka.hinnalla(550)))
                .isInstanceOf(OptimisticLockingFailureException.class);
    }
    // @loppu optimistinen
}

package fi.esimerkki.toimitus;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

/** Toimitusmaksun testit: rajatapaukset ja virheellinen syöte. */
class ToimitusTest {
    @Test
    void perusmaksuMantereelle() {
        // @start region="kaytto"
        int maksu = Toimitus.maksu("manner", 800, 0);
        assertEquals(590, maksu);
        // @end
    }

    @Test
    void ilmainenToimitusRajalla() {
        int raja = Toimitus.ILMAINEN_ALKAEN_SNT;
        assertEquals(590, Toimitus.maksu("manner", 800, raja - 1));
        assertEquals(0, Toimitus.maksu("manner", 800, raja));
    }

    /** Sama testi usealla syötteellä: alue, paino, ostokset, odotettu. */
    @ParameterizedTest
    @CsvSource({
        "manner,      5000,    0,  590",
        "manner,      5001,    0,  690",
        "ahvenanmaa,  7500,    0, 1290",
        "manner,     20001, 9999, 2190"})
    void lisakilot(String alue, int painoG, int ostoksetSnt, int odotettu) {
        assertEquals(odotettu, Toimitus.maksu(alue, painoG, ostoksetSnt));
    }

    @Test
    void tuntematonAlue() {
        var e = assertThrows(IllegalArgumentException.class,
                () -> Toimitus.maksu("kuu", 100, 0));
        assertEquals("tuntematon alue: kuu", e.getMessage());
    }
}

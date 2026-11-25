package fi.esimerkki.toimitus;

import java.util.Map;

/**
 * Toimitusmaksun laskenta alueen, painon ja ostosten summan mukaan.
 *
 * <p>Maksu on alueen perusmaksu, johon sisältyy viisi kiloa. Jokainen
 * alkava lisäkilo maksaa {@value #LISAKILO_SNT} senttiä. Käyttö:
 *
 * {@snippet class="fi.esimerkki.toimitus.ToimitusTest" region="kaytto"}
 */
public final class Toimitus {
    /** Ostosten summa sentteinä, josta alkaen toimitus on ilmainen. */
    public static final int ILMAINEN_ALKAEN_SNT = 5000;

    /** Yhden alkavan lisäkilon hinta sentteinä. */
    public static final int LISAKILO_SNT = 100;

    private static final Map<String, Integer> PERUSMAKSU =
            Map.of("manner", 590, "ahvenanmaa", 990);

    private Toimitus() {
    }

    /**
     * Laskee lähetyksen toimitusmaksun.
     *
     * <p>Yli 20 kilon lähetys ei ole koskaan ilmainen.
     *
     * @param alue toimitusalue: {@code "manner"} tai {@code "ahvenanmaa"}
     * @param painoG lähetyksen paino grammoina, suurempi kuin nolla
     * @param ostoksetSnt ostosten summa sentteinä
     * @return toimitusmaksu sentteinä; 0, jos toimitus on ilmainen
     * @throws IllegalArgumentException jos alue on tuntematon tai paino
     *         ei ole positiivinen
     * @see #ILMAINEN_ALKAEN_SNT
     */
    public static int maksu(String alue, int painoG, int ostoksetSnt) {
        Integer perus = PERUSMAKSU.get(alue);
        if (perus == null) {
            throw new IllegalArgumentException("tuntematon alue: " + alue);
        }
        if (painoG <= 0) {
            throw new IllegalArgumentException("paino <= 0");
        }
        if (ostoksetSnt >= ILMAINEN_ALKAEN_SNT && painoG <= 20_000) {
            return 0;
        }
        int lisakilot = Math.max(0, (painoG - 1) / 1000 - 4);
        return perus + lisakilot * LISAKILO_SNT;
    }
}

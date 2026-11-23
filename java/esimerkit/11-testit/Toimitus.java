import java.util.Map;

/** Testattava yksikkö: toimitusmaksu painon ja alueen mukaan. */
final class Toimitus {
    static final int ILMAINEN_ALKAEN_SNT = 5000;
    private static final Map<String, Integer> PERUSMAKSU =
            Map.of("manner", 590, "ahvenanmaa", 990);

    private Toimitus() {
    }

    static int maksu(String alue, int painoG, int ostoksetSnt) {
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
        return perus + lisakilot * 100;
    }
}

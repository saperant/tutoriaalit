import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.EnumMap;
import java.util.Map;

// @alku enum
/** Toimitustavat: jokaisella arvolla on hinta ja toimitusaika. */
enum Toimitustapa {
    NOUTO(0, 0),
    POSTI(590, 3),
    KURIIRI(1290, 1);

    private final int hintaSnt;
    private final int paivia;

    Toimitustapa(int hintaSnt, int paivia) {
        this.hintaSnt = hintaSnt;
        this.paivia = paivia;
    }

    int hintaSnt() {
        return hintaSnt;
    }

    boolean ehtii(int paivassa) {
        return paivia <= paivassa;
    }
}
// @loppu enum

/** enum on luokka, jolla on kiinteä joukko olioita. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        for (Toimitustapa tapa : Toimitustapa.values()) {
            System.out.println(tapa + " " + tapa.hintaSnt() + " snt, "
                    + "ehtii huomiseksi: " + tapa.ehtii(1));
        }
        Toimitustapa valittu = Toimitustapa.valueOf("POSTI");
        System.out.println(valittu == Toimitustapa.POSTI);
        System.out.println(valittu.name() + " " + valittu.ordinal());

        Map<Toimitustapa, Integer> tilauksia =
                new EnumMap<>(Toimitustapa.class);
        tilauksia.merge(Toimitustapa.POSTI, 1, Integer::sum);
        tilauksia.merge(Toimitustapa.NOUTO, 1, Integer::sum);
        tilauksia.merge(Toimitustapa.POSTI, 1, Integer::sum);
        System.out.println(tilauksia);
        // @loppu kaytto
    }
}

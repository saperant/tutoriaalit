import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Function;

/** Rajattu LRU-välimuisti: rajaton välimuisti on muistivuoto. */
final class Main {
    private Main() {
    }

    // @alku lru
    /** Välimuisti, joka poistaa pisimpään käyttämättömän alkion. */
    static final class Lru<K, V> {
        private final Map<K, V> alkiot;
        private final Function<K, V> laske;
        private int laskettu;

        Lru(int koko, Function<K, V> laske) {
            this.laske = laske;
            // accessOrder = true: get siirtää alkion jonon loppuun.
            this.alkiot = new LinkedHashMap<>(16, 0.75f, true) {
                private static final long serialVersionUID = 1L;

                @Override
                protected boolean removeEldestEntry(Map.Entry<K, V> e) {
                    return size() > koko;
                }
            };
        }

        V hae(K avain) {
            V arvo = alkiot.get(avain);
            if (arvo == null) {
                arvo = laske.apply(avain);
                laskettu++;
                alkiot.put(avain, arvo);
            }
            return arvo;
        }

        @Override
        public String toString() {
            return alkiot.keySet() + ", laskettu " + laskettu + " kertaa";
        }
    }
    // @loppu lru

    public static void main(String[] args) {
        // @alku kaytto
        var hinnat = new Lru<String, Integer>(2, tuote -> tuote.length());
        for (String t : new String[] {"kahvi", "tee", "kahvi", "kaakao",
                "kahvi", "tee"}) {
            hinnat.hae(t);
        }
        System.out.println(hinnat);
        // @loppu kaytto
    }
}

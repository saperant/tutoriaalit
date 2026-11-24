package fi.tutoriaalit.palvelut.etakutsut;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.IntFunction;

/** Testien valepalvelu: vastaus määräytyy kutsun järjestysnumerosta. */
public final class Valepalvelin implements AutoCloseable {
    public record Vastaus(int tila, String runko, Duration viive) {
        public static Vastaus ok(String runko) {
            return new Vastaus(200, runko, Duration.ZERO);
        }

        public static Vastaus virhe(int tila) {
            return new Vastaus(tila, "{}", Duration.ZERO);
        }

        public static Vastaus hidas(Duration viive) {
            return new Vastaus(200, "{}", viive);
        }
    }

    private final AtomicInteger kutsut = new AtomicInteger();
    private final Palvelin palvelin;

    public Valepalvelin(IntFunction<Vastaus> vastaukset) {
        palvelin = Palvelin.kaynnista(vaihto -> {
            var v = vastaukset.apply(kutsut.incrementAndGet());
            try {
                Thread.sleep(v.viive());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            Palvelin.vastaa(vaihto, v.tila(), v.runko());
        });
    }

    public Palvelin palvelin() {
        return palvelin;
    }

    public int kutsuja() {
        return kutsut.get();
    }

    @Override
    public void close() {
        palvelin.close();
    }
}

import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.LongAdder;

/** Jaetun laskurin kolme oikeaa toteutusta. */
final class Main {
    private static final int SAIKEITA = 4;
    private static final int KERTOJA = 100_000;

    private Main() {
    }

    // @alku laskurit
    static final class Lukittu {
        private long arvo;

        synchronized void kasvata() {
            arvo++;
        }

        synchronized long arvo() {
            return arvo;
        }
    }

    static final Lukittu LUKITTU = new Lukittu();
    static final AtomicLong ATOMINEN = new AtomicLong();
    static final LongAdder SUMMAIN = new LongAdder();
    // @loppu laskurit

    public static void main(String[] args) throws InterruptedException {
        // @alku kaytto
        Thread[] saikeet = new Thread[SAIKEITA];
        for (int s = 0; s < SAIKEITA; s++) {
            saikeet[s] = Thread.ofPlatform().start(() -> {
                for (int i = 0; i < KERTOJA; i++) {
                    LUKITTU.kasvata();
                    ATOMINEN.incrementAndGet();
                    SUMMAIN.increment();
                }
            });
        }
        for (Thread t : saikeet) {
            t.join(); // join takaa näkyvyyden: happens-before
        }
        System.out.println("synchronized: " + LUKITTU.arvo());
        System.out.println("AtomicLong:   " + ATOMINEN.get());
        System.out.println("LongAdder:    " + SUMMAIN.sum());
        // @loppu kaytto
    }
}

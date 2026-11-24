package fi.tutoriaalit.palvelut.viestit;

import java.time.Duration;
import java.util.function.BooleanSupplier;

/** Odottaa, kunnes ehto täyttyy: viestit etenevät taustalla. */
public final class Odota {
    private Odota() {
    }

    public static void kunnes(BooleanSupplier ehto) {
        long raja = System.nanoTime() + Duration.ofSeconds(10).toNanos();
        while (!ehto.getAsBoolean()) {
            if (System.nanoTime() > raja) {
                throw new AssertionError("ehto ei täyttynyt ajoissa");
            }
            try {
                Thread.sleep(20);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new AssertionError(e);
            }
        }
    }
}

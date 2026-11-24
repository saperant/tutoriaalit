package fi.tutoriaalit.palvelut.etakutsut.kestavyys;

import java.time.Duration;
import java.util.Random;
import java.util.function.Predicate;
import java.util.function.Supplier;

// @alku uudelleenyritys
/**
 * Uudelleenyritys eksponentiaalisella odotuksella ja täydellä
 * satunnaisuudella (full jitter): yrityksen n jälkeen odotetaan
 * satunnainen aika väliltä [0, min(enintään, perus * 2^n)]. Satunnaisuus
 * hajauttaa yhtä aikaa epäonnistuneiden asiakkaiden uudet yritykset,
 * jotta ne eivät iske toipuvaan palveluun samalla hetkellä.
 */
public record Uudelleenyritys(int yrityksia, Duration perus,
                              Duration enintaan, Random satunnainen) {

    public <T> T aja(Supplier<T> kutsu, Predicate<RuntimeException> ohimeno) {
        for (int n = 0; ; n++) {
            try {
                return kutsu.get();
            } catch (RuntimeException e) {
                if (n + 1 >= yrityksia || !ohimeno.test(e)) {
                    throw e;
                }
                odota(n);
            }
        }
    }

    private void odota(int n) {
        long katto = Math.min(enintaan.toMillis(),
                perus.toMillis() << Math.min(n, 20));
        try {
            Thread.sleep(satunnainen.nextLong(katto + 1));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }
}
// @loppu uudelleenyritys

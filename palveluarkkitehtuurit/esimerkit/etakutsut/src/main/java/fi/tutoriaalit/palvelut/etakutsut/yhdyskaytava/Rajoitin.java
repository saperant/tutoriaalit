package fi.tutoriaalit.palvelut.etakutsut.yhdyskaytava;

import java.util.HashMap;
import java.util.Map;
import java.util.function.LongSupplier;

// @alku rajoitin
/**
 * Pyyntörajoitin, avainkohtainen merkkiämpäri (token bucket): ämpärissä
 * on enintään {@code kapasiteetti} merkkiä, jokainen pyyntö kuluttaa
 * yhden, ja merkkejä tulee lisää {@code sekunnissa} sekunnissa. Sallii
 * lyhyet purskeet mutta rajoittaa keskimääräisen tahdin.
 */
public final class Rajoitin {
    private final double kapasiteetti;
    private final double sekunnissa;
    private final LongSupplier kello;        // nanosekunteja
    private final Map<String, double[]> amparit = new HashMap<>();

    public Rajoitin(int kapasiteetti, double sekunnissa,
                    LongSupplier kello) {
        this.kapasiteetti = kapasiteetti;
        this.sekunnissa = sekunnissa;
        this.kello = kello;
    }

    public synchronized boolean salli(String avain) {
        long nyt = kello.getAsLong();
        // [merkit, edellinen täyttöhetki]
        double[] a = amparit.computeIfAbsent(avain,
                k -> new double[] {kapasiteetti, nyt});
        double kulunut = (nyt - a[1]) / 1e9;
        a[0] = Math.min(kapasiteetti, a[0] + kulunut * sekunnissa);
        a[1] = nyt;
        if (a[0] < 1) {
            return false;
        }
        a[0] -= 1;
        return true;
    }
}
// @loppu rajoitin

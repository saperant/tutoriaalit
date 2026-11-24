package fi.tutoriaalit.palvelut.etakutsut.ketju;

import java.util.Random;

/** Monte Carlo -arvio palveluketjun saatavuudesta. */
public final class Saatavuus {
    private Saatavuus() {
    }

    // @alku saatavuus
    /** Osuus pyynnöistä, jotka onnistuvat, kun jokainen ketjun n
     *  palvelusta on toiminnassa todennäköisyydellä p toisistaan
     *  riippumatta. */
    public static double ketjun(double p, int n, int kierroksia,
                                long siemen) {
        var satunnainen = new Random(siemen);
        int onnistui = 0;
        for (int k = 0; k < kierroksia; k++) {
            boolean kaikki = true;
            for (int i = 0; i < n && kaikki; i++) {
                kaikki = satunnainen.nextDouble() < p;
            }
            if (kaikki) {
                onnistui++;
            }
        }
        return (double) onnistui / kierroksia;
    }
    // @loppu saatavuus
}

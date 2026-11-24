// Biquad-ketju: 4. asteen Butterworth ja korostus, DF1 ja DF2T.
#include <complex.h>
#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#include "biquad.h"

#define FS 48000.0
#define PITUUS 9600

int main(void)
{
    // @alku suunnittelu
    // 4. asteen Butterworth = kaksi 2. asteen lohkoa, Q = 1 / (2 cos t),
    // t = pi/8 ja 3 pi/8. Peraan +6 dB:n korostus 1 kHz:iin.
    biquad_t lohkot[3];
    if (biquad_alipaasto(&lohkot[0], 8000.0, 0.541196, FS) != 0
        || biquad_alipaasto(&lohkot[1], 8000.0, 1.306563, FS) != 0
        || biquad_korostus(&lohkot[2], 1000.0, 1.0, 6.0, FS) != 0) {
        fputs("virheellinen suunnitteluparametri\n", stderr);
        return 1;
    }
    for (int j = 0; j < 3; j++) {
        const biquad_t *k = &lohkot[j];
        printf("lohko %d: b = %9.6f %9.6f %9.6f  a = %9.6f %9.6f\n", j,
               k->b0, k->b1, k->b2, k->a1, k->a2);
    }
    for (int j = 0; j < 4; j++) {
        static const double f[] = {100.0, 1000.0, 8000.0, 16000.0};
        double complex H = sos_vaste(lohkot, 3, f[j], FS);
        printf("%6.0f Hz: %7.2f dB\n", f[j], 20.0 * log10(cabs(H)));
    }
    // @loppu suunnittelu

    // @alku muodot
    static double x[PITUUS], y1[PITUUS], y2[PITUUS], y3[PITUUS];
    unsigned tila_lcg = 1;
    for (size_t i = 0; i < PITUUS; i++) {        // tasajakautunut kohina
        tila_lcg = tila_lcg * 1103515245u + 12345u;
        x[i] = (double)(tila_lcg >> 8) / 16777216.0 - 0.5;
    }
    double t1[12], t2[12];
    sos_t df1, df2t;
    if (sos_alusta(&df1, lohkot, 3, t1, SOS_DF1) != 0
        || sos_alusta(&df2t, lohkot, 3, t2, SOS_DF2T) != 0) {
        return 1;
    }
    sos_kasittele(&df1, x, y1, PITUUS);
    sos_kasittele(&df2t, x, y2, PITUUS);
    sos_nollaa(&df2t);
    for (size_t i = 0; i < PITUUS; i += 480) {   // 10 ms:n lohkot
        sos_kasittele(&df2t, x + i, y3 + i, 480);
    }
    double ero = 0.0;
    bool samat = true;
    for (size_t i = 0; i < PITUUS; i++) {
        ero = fmax(ero, fabs(y1[i] - y2[i]));
        samat = samat && y2[i] == y3[i];
    }
    printf("DF1 ja DF2T, ero alle 1e-12: %s\n", ero < 1e-12 ? "kylla" : "EI");
    printf("lohkoittain == kerralla: %s\n", samat ? "kylla" : "EI");
    // @loppu muodot
    return 0;
}

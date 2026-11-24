// FIR-suodin virtarajapinnoilla: näyte sisään ja tulos ulos joka
// jaksolla. Viivelinja on jaettu rekistereiksi.
// @alku ydin
#include "virta.hpp"

#define T 8
#define PITUUS 32

void fir(virta<int>& x, virta<int>& y) {
    const int c[T] = {-3, 12, 37, 82, 82, 37, 12, -3};
    int z[T];
#pragma HLS array_partition variable=z type=complete
alustus:
    for (int k = 0; k < T; k++) {
#pragma HLS unroll
        z[k] = 0;
    }
naytteet:
    for (int n = 0; n < PITUUS; n++) {
#pragma HLS pipeline II=1
        for (int k = T - 1; k > 0; k--) {
            z[k] = z[k - 1];
        }
        z[0] = x.read();
        int s = 0;
        for (int k = 0; k < T; k++) {
            s += c[k] * z[k];
        }
        y.write(s >> 8);
    }
}
// @loppu ydin

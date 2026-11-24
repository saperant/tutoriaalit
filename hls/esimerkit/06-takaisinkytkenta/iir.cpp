// Ensimmäisen kertaluvun IIR-alipäästösuodin kiintopisteessä:
// tila seuraa syötettä kertoimella K / 256.
// @alku ydin
#define N 16
#define K 77

void iir(const int x[N], int y[N]) {
    int tila = 0;
suodatus:
    for (int n = 0; n < N; n++) {
#pragma HLS pipeline II=1
        tila += ((x[n] - tila) * K) >> 8;
        y[n] = tila;
    }
}
// @loppu ydin

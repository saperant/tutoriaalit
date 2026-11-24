// Sama suodin uudelleen kirjoitettuna: takaisinkytkennässä on vain
// kertolasku ja yhteenlasku. Tulokset ovat bitilleen samat, koska
// t + ((x - t) * K >> 8) = (t * (256 - K) + x * K) >> 8.
#define N 16
#define K 77

void iir(const int x[N], int y[N]) {
    int tila = 0;
suodatus:
    for (int n = 0; n < N; n++) {
#pragma HLS pipeline II=1
// @alku rivi
        tila = (tila * (256 - K) + x[n] * K) >> 8;
// @loppu rivi
        y[n] = tila;
    }
}

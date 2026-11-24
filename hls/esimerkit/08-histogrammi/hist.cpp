// Histogrammi: luokan laskuri luetaan, kasvatetaan ja kirjoitetaan
// takaisin. Peräkkäisten kierrosten luokka voi olla sama.
// @alku ydin
#define N 256
#define B 16

void hist(const int x[N], int h[B]) {
laskenta:
    for (int i = 0; i < N; i++) {
#pragma HLS pipeline II=1
        h[x[i]] += 1;
    }
}
// @loppu ydin

// Histogrammi kahdella osahistogrammilla: parilliset ja parittomat
// alkiot päivittävät eri muistia, joten kumpikin riippuvuusketju saa
// kaksi jaksoa ja kierros käsittelee kaksi alkiota.
// @alku ydin
#define N 256
#define B 16

void hist(const int x[N], int h[B]) {
#pragma HLS array_partition variable=x type=cyclic factor=2
    int p[B];
    int q[B];
nollaus:
    for (int k = 0; k < B; k++) {
#pragma HLS pipeline II=1
        p[k] = 0;
        q[k] = 0;
    }
laskenta:
    for (int i = 0; i < N; i += 2) {
#pragma HLS pipeline II=1
        p[x[i]] += 1;
        q[x[i + 1]] += 1;
    }
yhdistys:
    for (int k = 0; k < B; k++) {
#pragma HLS pipeline II=1
        h[k] += p[k] + q[k];
    }
}
// @loppu ydin

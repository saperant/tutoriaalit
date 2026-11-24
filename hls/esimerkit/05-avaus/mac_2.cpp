// Pistetulo avattuna kahdella: kierros laskee kaksi tuloa.
#define N 8

int mac(const int a[N], const int b[N]) {
    int s = 0;
kertolasku:
    for (int i = 0; i < N; i++) {
// @alku pragma
#pragma HLS unroll factor=2
// @loppu pragma
        s += a[i] * b[i];
    }
    return s;
}

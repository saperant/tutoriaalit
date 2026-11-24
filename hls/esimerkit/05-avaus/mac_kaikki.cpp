// Pistetulo avattuna kokonaan: silmukka katoaa.
#define N 8

int mac(const int a[N], const int b[N]) {
    int s = 0;
kertolasku:
    for (int i = 0; i < N; i++) {
// @alku pragma
#pragma HLS unroll
// @loppu pragma
        s += a[i] * b[i];
    }
    return s;
}

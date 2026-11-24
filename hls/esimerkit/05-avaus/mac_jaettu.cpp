// Pistetulo avattuna kokonaan ja taulukot jaettuina.
#define N 8

int mac(const int a[N], const int b[N]) {
#pragma HLS array_partition variable=a type=cyclic factor=8
#pragma HLS array_partition variable=b type=cyclic factor=8
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

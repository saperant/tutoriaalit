// Pistetulo liukuhihnoitettuna: uusi kierros joka jaksolla.
#define N 8

int mac(const int a[N], const int b[N]) {
    int s = 0;
kertolasku:
    for (int i = 0; i < N; i++) {
// @alku pragma
#pragma HLS pipeline II=1
// @loppu pragma
        s += a[i] * b[i];
    }
    return s;
}

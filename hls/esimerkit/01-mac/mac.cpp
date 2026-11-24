// Pistetulo: kertolasku ja summa (multiply-accumulate).
// @alku ydin
#define N 8

int mac(const int a[N], const int b[N]) {
    int s = 0;
kertolasku:
    for (int i = 0; i < N; i++) {
        s += a[i] * b[i];
    }
    return s;
}
// @loppu ydin

// Taulukon alkioiden summa: silmukka ja indeksointi.
long taulukon_summa(const long *t, long n) {
    long s = 0;
    for (long i = 0; i < n; i++) {
        s += t[i];
    }
    return s;
}

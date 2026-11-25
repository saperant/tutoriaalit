// Häntäkutsu ja sisällytys: kutsu voi muuttua hypyksi tai kadota.
long tarkista(long x);

static long kaksinkertainen(long x) {
    return 2 * x;
}

long valita(long x) {
    return tarkista(kaksinkertainen(x) + 1);
}

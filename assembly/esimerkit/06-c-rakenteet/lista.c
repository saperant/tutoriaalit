// Linkitetyn listan läpikäynti: osoittimen seuraaminen.
struct solmu {
    long arvo;
    struct solmu *seuraava;
};

long listan_summa(const struct solmu *s) {
    long summa = 0;
    while (s != 0) {
        summa += s->arvo;
        s = s->seuraava;
    }
    return summa;
}

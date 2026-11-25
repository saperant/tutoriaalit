// Tietueen kentät ovat vakiosiirtymiä tietueen alusta.
struct tilaus {
    char tila;      // siirtymä 0, perässä 3 tavua täytettä
    int maara;      // siirtymä 4
    double hinta;   // siirtymä 8
    long asiakas;   // siirtymä 16
};

double tilauksen_arvo(const struct tilaus *t) {
    return t->maara * t->hinta;
}

long tilauksen_asiakas(const struct tilaus *t) {
    return t->asiakas;
}

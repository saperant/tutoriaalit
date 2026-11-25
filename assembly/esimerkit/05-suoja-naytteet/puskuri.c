// Paikallinen taulukko, jonka osoite annetaan toiselle funktiolle:
// kääntäjä lisää pinosuojan (-fstack-protector-strong).
void tayta(char *puskuri, long n);

long ensimmainen(void) {
    char puskuri[24];
    tayta(puskuri, sizeof puskuri);
    return puskuri[0];
}

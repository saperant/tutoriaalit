// Silmukka, jonka kierrosmäärä riippuu datasta.
int bitteja(int x) {
    int n = 0;
    while (x != 0) {
        x = x & (x - 1);
        n++;
    }
    return n;
}

// Keskiarvo jakolaskulla: minihls ei tue jakolaskua.
int keskiarvo(const int x[8]) {
    int s = 0;
    for (int i = 0; i < 8; i++) {
        s += x[i];
    }
    return s / 8;
}

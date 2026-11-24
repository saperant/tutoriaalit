// Sama kertoma C:llä. GCC:n koodia verrataan Kiden tuottamaan.
long kertoma(long n) {
    if (n <= 1) {
        return 1;
    }
    return n * kertoma(n - 1);
}

// Kutsukonventio: rekursio, pinoargumentit ja takaisinkutsu C:hen.
#include <stdio.h>

long kertoma(long n);
long summa9(long a, long b, long c, long d, long e, long f, long g,
            long h, long i);
long kay_lapi(const long *t, long n, long (*f)(long));

// @alku takaisinkutsu
// printf liukuluvulla vaatii, että pino on tasattu 16 tavuun: väärin
// tasattu pino kaataisi ohjelman x86-64:llä.
static long nelio(long x) {
    printf("  %ld^2 = %.1f\n", x, (double)(x * x));
    return x * x;
}
// @loppu takaisinkutsu

int main(void) {
    for (long n = 0; n <= 20; n += 5) {
        printf("%ld! = %ld\n", n, kertoma(n));
    }
    printf("summa9(1..9) = %ld\n", summa9(1, 2, 3, 4, 5, 6, 7, 8, 9));
    const long t[] = {3, -1, 4};
    printf("kay_lapi:\n");
    printf("neliöiden summa = %ld\n", kay_lapi(t, 3, nelio));
    return 0;
}

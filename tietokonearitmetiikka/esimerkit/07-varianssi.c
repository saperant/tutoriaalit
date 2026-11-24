// Anturin keskihajonta: oppikirjan kaava vs. Welfordin algoritmi.
#include <math.h>
#include <stdio.h>

int main(void)
{
    // Aikaleimat mikrosekunteina vuoden 2026 alusta: suuri vakio-osa,
    // pieni vaihtelu (0, 1000 tai 2000 µs). Oikea hajonta on 816,5 µs.
    const double perus = 1.7672256e15;
    double s = 0.0, s2 = 0.0;
    double ka = 0.0, m2 = 0.0;
    const int n = 3000;
    for (int i = 0; i < n; i++) {
        double x = perus + (double)(i % 3) * 1000.0;
        // @alku naiivi
        s += x;
        s2 += x * x;
        // @loppu naiivi
        // @alku welford
        double ero = x - ka;
        ka += ero / (i + 1);
        m2 += ero * (x - ka);
        // @loppu welford
    }
    double naiivi = s2 / n - (s / n) * (s / n);
    printf("naiivi varianssi %g\n", naiivi);
    printf("Welford: hajonta %.1f µs\n", sqrt(m2 / n));
    return 0;
}

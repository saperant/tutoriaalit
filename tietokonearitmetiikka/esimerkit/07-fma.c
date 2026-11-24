// fma laskee a*b+c yhdellä pyöristyksellä. Sillä saa tulon virheen.
#include <math.h>
#include <stdio.h>

int main(void)
{
    volatile double va = 0.1, vb = 10.0;
    double a = va, b = vb;
    // @alku virhe
    double tulo = a * b;                 // pyöristetty tulo
    double virhe = fma(a, b, -tulo);     // tarkka a*b miinus tulo
    printf("a*b = %.17g, pyöristysvirhe %.17g\n", tulo, virhe);
    // @loppu virhe
    // @alku pistetulo
    // Kompensoitu pistetulo: tulon ja summan virheet talteen.
    const double x[] = {1e8, 1.0, -1e8, 1e-8};
    const double y[] = {1e8 + 1, 1.0, 1e8, 1e8};
    double s = 0.0, c = 0.0, naiivi = 0.0;
    for (int i = 0; i < 4; i++) {
        double p = x[i] * y[i];
        double pv = fma(x[i], y[i], -p);
        double t = s + p;
        double z = t - s;
        double sv = (s - (t - z)) + (p - z);   // TwoSum
        s = t;
        c += pv + sv;
        naiivi += x[i] * y[i];
    }
    printf("naiivi %.17g, kompensoitu %.17g\n", naiivi, s + c);
    // @loppu pistetulo
    return 0;
}

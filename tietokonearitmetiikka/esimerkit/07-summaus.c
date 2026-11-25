// Mittausten summa: järjestyksen ja kompensoinnin vaikutus.
#include <math.h>
#include <stdio.h>

enum { N = 10000000 };

// @alku kahan
static float kahan(const float *x, int n)
{
    float summa = 0.0f, korjaus = 0.0f;
    for (int i = 0; i < n; i++) {
        float y = x[i] - korjaus;
        float t = summa + y;
        korjaus = (t - summa) - y;     // mitä t:stä jäi pois
        summa = t;
    }
    return summa;
}
// @loppu kahan

// @alku parittain
static float parittain(const float *x, int n)
{
    if (n <= 8) {
        float s = 0.0f;
        for (int i = 0; i < n; i++) {
            s += x[i];
        }
        return s;
    }
    return parittain(x, n / 2) + parittain(x + n / 2, n - n / 2);
}
// @loppu parittain

static float data[N];

// Virhe lukemien määrän funktiona; kuvat/piirra.py piirtää tästä kuvan.
static void kayra(void)
{
    float naiivi = 0.0f;
    int tehty = 0;
    for (long m = 10; tehty < N; m = m * 5 / 2) {
        int n = m < N ? (int)m : N;
        for (; tehty < n; tehty++) {
            naiivi += data[tehty];
        }
        double tarkka = (double)0.1f * n;
        printf("%d %.3e %.3e %.3e\n", n,
               fabs(naiivi - tarkka) / tarkka,
               fabs(kahan(data, n) - tarkka) / tarkka,
               fabs(parittain(data, n) - tarkka) / tarkka);
    }
}

int main(int argc, char **argv)
{
    for (int i = 0; i < N; i++) {
        data[i] = 0.1f;               // 10 miljoonaa 0.1 kWh:n lukemaa
    }
    if (argc > 1 && argv[1][0] == 'k') {   // ./07-summaus kayra
        kayra();
        return 0;
    }
    // Tarkka summa: lukema on float-arvo 0.100000001490116...
    double tarkka = (double)0.1f * N;
    // @alku naiivi
    float naiivi = 0.0f;
    for (int i = 0; i < N; i++) {
        naiivi += data[i];
    }
    // @loppu naiivi
    const char *nimet[] = {"naiivi", "Kahan", "parittain"};
    float tulos[] = {naiivi, kahan(data, N), parittain(data, N)};
    for (int i = 0; i < 3; i++) {
        printf("%-10s %12.1f  suhteellinen virhe %.0e\n", nimet[i],
               (double)tulos[i], fabs(tulos[i] - tarkka) / tarkka);
    }
    return 0;
}

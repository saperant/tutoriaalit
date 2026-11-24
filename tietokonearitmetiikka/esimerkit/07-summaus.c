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

int main(void)
{
    for (int i = 0; i < N; i++) {
        data[i] = 0.1f;               // 10 miljoonaa 0.1 kWh:n lukemaa
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

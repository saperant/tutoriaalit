#include <assert.h>
#include <stdio.h>

static_assert(sizeof(int) >= 4, "int on liian pieni");   // käännösaikana

double keskiarvo(const double *t, int n)
{
    assert(t != nullptr && n > 0);   // esiehto, tarkistetaan ajon aikana
    double s = 0.0;
    for (int i = 0; i < n; ++i) {
        s += t[i];
    }
    return s / n;
}

int main(void)
{
    double luvut[] = {1.0, 2.0};
    fprintf(stderr, "%.1f\n", keskiarvo(luvut, 2));
    fprintf(stderr, "%.1f\n", keskiarvo(luvut, 0));   // rikkoo esiehdon
}

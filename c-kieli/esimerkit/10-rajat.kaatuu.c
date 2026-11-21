#include <stdio.h>

int summa(const int *t, int n)
{
    int s = 0;
    for (int i = 0; i <= n; ++i) {   // virhe: pitäisi olla i < n
        s += t[i];
    }
    return s;
}

int main(void)
{
    int luvut[4] = {1, 2, 3, 4};
    printf("%d\n", summa(luvut, 4));
}

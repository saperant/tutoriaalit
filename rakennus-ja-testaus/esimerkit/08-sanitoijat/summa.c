// Etumerkillisen kokonaisluvun ylivuoto: määrittelemätöntä käytöstä.
#include <stdio.h>

static int kesto_ms(const int *vaiheet_ms, int n)
{
    int summa = 0;
    for (int i = 0; i < n; i++)
        summa += vaiheet_ms[i];
    return summa;
}

int main(void)
{
    int vaiheet[] = {2000000000, 200000000};
    printf("kesto %d ms\n", kesto_ms(vaiheet, 2));
    return 0;
}

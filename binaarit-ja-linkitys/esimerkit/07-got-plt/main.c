#include <stdio.h>

int mittaa(int raaka);

int main(void)
{
    fputs("ennen ensimmäistä kutsua\n", stderr);
    int a = mittaa(14);
    fputs("ensimmäisen kutsun jälkeen\n", stderr);
    printf("%d %d\n", a, mittaa(20));
    return 0;
}

#include <stdio.h>

#ifndef KORJATTU
int *laskuri(void)
{
    int n = 0;          // paikallinen: tuhoutuu, kun funktio palaa
    return &n;          // virhe: osoitin tuhoutuvaan muuttujaan
}
#else
int *laskuri(void)
{
    static int n = 0;   // staattinen: on olemassa koko ohjelman ajan
    return &n;
}
#endif

int main(void)
{
    int *p = laskuri();
    *p += 1;
    printf("%d\n", *p);
}

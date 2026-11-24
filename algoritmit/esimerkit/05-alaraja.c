// Vertailuperusteisen lajittelun alaraja: n alkiolla on n! järjestystä,
// ja jokainen vertailu jakaa jäljellä olevat vaihtoehdot korkeintaan
// kahtia. Pahimmassa tapauksessa tarvitaan ainakin ceil(log2 n!)
// vertailua, mikä on noin n log2 n - 1,44 n.
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    printf("%8s %14s %14s\n", "n", "ceil(log2 n!)", "n log2 n");
    for (int n = 10; n <= 1000000; n *= 10) {
        // log2(n!) = lgamma(n + 1) / ln 2
        double alaraja = ceil(lgamma(n + 1.0) / log(2.0));
        double nlogn = n * log2((double)n);
        printf("%8d %14.0f %14.0f\n", n, alaraja, nlogn);
    }
    return EXIT_SUCCESS;
}

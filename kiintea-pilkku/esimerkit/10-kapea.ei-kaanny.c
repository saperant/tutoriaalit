// Kertymän saturaatioraja vakiona: lauseke lasketaan int-tyypissä.
#include <stdint.h>
#include <stdio.h>

// @alku raja
// Kertymä on Q2.30-yksiköissä 64-bittinen; raja on 3,0.
#ifndef KORJATTU
static const int64_t RAJA = 3 * (1 << 30);         // int: ylivuoto
#else
static const int64_t RAJA = 3 * (INT64_C(1) << 30);
#endif
// @loppu raja

int main(void)
{
    printf("raja %lld = %.1f\n", (long long)RAJA,
           (double)RAJA / (1 << 30));
    return 0;
}

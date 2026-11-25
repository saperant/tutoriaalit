#include "raportti.h"

int main(void)
{
    double x[] = {21.5, 22.0, 21.8};
    return kirjoita_raportti(stdout, x, 3) == 0 ? 0 : 1;
}

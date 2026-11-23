#include <stdio.h>

#ifdef KORJATTU
double keskiarvo(double a, double b);   // prototyyppi ennen käyttöä
#endif

int main(void)
{
    printf("%.1f\n", keskiarvo(2.0, 5.0));   // virhe ilman prototyyppiä
}

double keskiarvo(double a, double b)
{
    return (a + b) / 2.0;
}

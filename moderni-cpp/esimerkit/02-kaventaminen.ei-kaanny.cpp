#include <print>

int main()
{
    double d = 3.7;
    int a = d;      // sallittu: desimaalit katkeavat hiljaa
#ifndef KORJATTU
    int b{d};       // käännösvirhe: kaventava muunnos
    std::println("{}", b);
#endif
    std::println("{}", a);
}

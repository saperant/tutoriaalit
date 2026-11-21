#include <print>

[[nodiscard]] int laske_summa(int a, int b)
{
    return a + b;
}

int main()
{
#ifndef KORJATTU
    laske_summa(2, 3);  // varoitus: paluuarvo jätetään käyttämättä
#endif
    int summa = laske_summa(2, 3);
    std::println("{}", summa);
}

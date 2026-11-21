#include <print>

consteval int kilotavuja(int n)
{
    return n * 1024;
}

int main()
{
#ifndef KORJATTU
    int n = 4;             // tavallinen muuttuja: arvo vasta ajoaikana
#else
    constexpr int n = 4;   // vakio: arvo tunnetaan käännösaikana
#endif
    std::println("{}", kilotavuja(n));
}

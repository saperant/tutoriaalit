#include <memory>
#include <print>
#include <utility>

int main()
{
    auto a = std::make_unique<int>(42);
#ifndef KORJATTU
    auto b = a;              // virhe: unique_ptr:ää ei voi kopioida
#else
    auto b = std::move(a);   // siirto on sallittu
#endif
    std::println("{}", *b);
}

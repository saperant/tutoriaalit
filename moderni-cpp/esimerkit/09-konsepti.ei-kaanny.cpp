#include <concepts>
#include <list>
#include <print>
#include <vector>

template <typename Sailio>
    requires std::random_access_iterator<typename Sailio::iterator>
auto keskimmainen(const Sailio& s)
{
    return s[s.size() / 2];
}

int main()
{
    std::vector<int> v{1, 2, 3};
    std::println("{}", keskimmainen(v));
#ifndef KORJATTU
    std::list<int> l{1, 2, 3};
    std::println("{}", keskimmainen(l));   // virhe: ei hajasaantia
#endif
}

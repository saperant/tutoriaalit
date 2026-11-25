#include <concepts>
#include <list>
#include <print>
#include <string>
#include <vector>

// @alku vakio
template <std::integral T>
T puolita(T x)
{
    return x / 2;
}

template <std::floating_point T>
T puolita(T x)
{
    return x / 2.0;
}
// @loppu vakio

// @alku oma
template <typename T>
concept Mitattava = requires(const T& x) {
    { x.size() } -> std::convertible_to<std::size_t>;
    x.empty();
};

std::size_t yhteispituus(const Mitattava auto& a, const Mitattava auto& b)
{
    return a.size() + b.size();
}
// @loppu oma

// @alku requires
template <typename Sailio>
    requires std::random_access_iterator<typename Sailio::iterator>
auto keskimmainen(const Sailio& s)
{
    return s[s.size() / 2];
}
// @loppu requires

int main()
{
    // @alku kaytto
    std::println("{} {}", puolita(7), puolita(7.0));

    std::vector<int> v{1, 2, 3};
    std::string s = "kissa";
    std::list<double> l{1.0, 2.0};
    std::println("{} {}", yhteispituus(v, s), yhteispituus(s, l));

    std::println("{} {}", keskimmainen(v), keskimmainen(s));
    // @loppu kaytto
}

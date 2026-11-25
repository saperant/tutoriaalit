#include <print>
#include <vector>

// @alku tyypit
struct Laskurit {
    static inline int kopiot = 0;
    static inline int siirrot = 0;
};

struct Turvallinen {
    Turvallinen() = default;
    Turvallinen(const Turvallinen&) { ++Laskurit::kopiot; }
    Turvallinen(Turvallinen&&) noexcept { ++Laskurit::siirrot; }
};

struct Epavarma {
    Epavarma() = default;
    Epavarma(const Epavarma&) { ++Laskurit::kopiot; }
    Epavarma(Epavarma&&) { ++Laskurit::siirrot; }   // ei noexcept
};
// @loppu tyypit

// @alku kasvatus
template <typename T>
void kasvata()
{
    Laskurit::kopiot = 0;
    Laskurit::siirrot = 0;
    std::vector<T> v(3);
    v.reserve(100);   // pakottaa siirtämään alkiot uuteen muistiin
    std::println("kopioita {}, siirtoja {}",
                 Laskurit::kopiot, Laskurit::siirrot);
}
// @loppu kasvatus

int main()
{
    // @alku kaytto
    kasvata<Turvallinen>();
    kasvata<Epavarma>();
    // @loppu kaytto
}

// seuranta.hpp: tyyppi, joka laskee rakentamisensa, kopionsa ja siirtonsa.
#ifndef SEURANTA_HPP
#define SEURANTA_HPP

#include <cstdio>
#include <string>
#include <utility>

// @alku seurattava
struct Seurattava {
    static inline int rakennettu = 0;
    static inline int kopioitu = 0;
    static inline int siirretty = 0;

    std::string arvo;

    explicit Seurattava(std::string a = {}) : arvo{std::move(a)}
    {
        ++rakennettu;
    }
    Seurattava(const Seurattava& m) : arvo{m.arvo} { ++kopioitu; }
    Seurattava(Seurattava&& m) noexcept : arvo{std::move(m.arvo)}
    {
        ++siirretty;
    }
    Seurattava& operator=(const Seurattava& m)
    {
        arvo = m.arvo;
        ++kopioitu;
        return *this;
    }
    Seurattava& operator=(Seurattava&& m) noexcept
    {
        arvo = std::move(m.arvo);
        ++siirretty;
        return *this;
    }
    ~Seurattava() = default;

    // Tulostaa laskurit ja nollaa ne.
    static void raportoi(const char* tapaus)
    {
        std::printf("  %-28s rakennettu %d, kopioitu %d, siirretty %d\n",
                    tapaus, rakennettu, kopioitu, siirretty);
        rakennettu = kopioitu = siirretty = 0;
    }
};
// @loppu seurattava

#endif

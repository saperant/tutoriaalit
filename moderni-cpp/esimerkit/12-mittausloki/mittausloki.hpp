// mittausloki.hpp: julkinen rajapinta. Toteutuksen tietorakenteet eivät
// näy tänne, joten niiden muuttaminen ei pakota käyttäjiä kääntämään
// koodiaan uudelleen (pimpl-malli).
#pragma once

#include <cstddef>
#include <memory>
#include <string>
#include <string_view>

namespace tutoriaali::mittaus {

struct Yhteenveto {
    std::size_t maara;
    double pienin;
    double suurin;
    double keskiarvo;
};

inline constexpr std::size_t oletuskapasiteetti = 64;

class Mittausloki {
public:
    explicit Mittausloki(std::string_view nimi);
    ~Mittausloki();                                   // määritellään .cpp:ssä
    Mittausloki(Mittausloki&&) noexcept;
    Mittausloki& operator=(Mittausloki&&) noexcept;

    void lisaa(double arvo);
    const std::string& nimi() const;
    Yhteenveto yhteenveto() const;   // edellyttää vähintään yhden arvon

private:
    struct Toteutus;
    std::unique_ptr<Toteutus> t_;
};

}  // namespace tutoriaali::mittaus

/// @file mittausloki.hpp
/// @brief Mittauslokin julkinen rajapinta.
///
/// Toteutuksen tietorakenteet eivät näy tänne, joten niiden muuttaminen
/// ei pakota käyttäjiä kääntämään koodiaan uudelleen (pimpl-malli).
#pragma once

#include <cstddef>
#include <memory>
#include <string>
#include <string_view>

namespace tutoriaali::mittaus {

/// @brief Lokin arvojen tunnusluvut.
struct Yhteenveto {
    std::size_t maara;   ///< Arvojen lukumäärä.
    double pienin;       ///< Pienin arvo.
    double suurin;       ///< Suurin arvo.
    double keskiarvo;    ///< Aritmeettinen keskiarvo.
};

/// @brief Alkioiden määrä, jolle uusi loki varaa tilan etukäteen.
inline constexpr std::size_t oletuskapasiteetti = 64;

/// @brief Nimetty sarja mittausarvoja.
///
/// Olio on siirrettävä mutta ei kopioitava. Siirron jälkeen lähdeolion
/// voi vain tuhota, tai siihen voi sijoittaa toisen lokin. Luokka ei
/// ole säieturvallinen: samaa oliota ei saa käyttää useasta säikeestä
/// ilman lukitusta.
class Mittausloki {
public:
    /// @brief Luo tyhjän lokin.
    /// @param nimi Lokin nimi; merkkijono kopioidaan.
    explicit Mittausloki(std::string_view nimi);
    ~Mittausloki();   // määritellään .cpp:ssä

    /// @brief Siirtää lokin sisällön; lähdeolio jää tyhjäksi.
    Mittausloki(Mittausloki&&) noexcept;
    /// @brief Korvaa sisällön siirtämällä; lähdeolio jää tyhjäksi.
    /// @return Viittaus tähän olioon.
    Mittausloki& operator=(Mittausloki&&) noexcept;

    /// @brief Lisää arvon lokin loppuun.
    /// @param arvo Mittausarvo.
    /// @throws std::invalid_argument jos arvo ei ole äärellinen (NaN
    ///         tai ääretön). Loki säilyy tällöin muuttumattomana.
    void lisaa(double arvo);

    /// @brief Lokin nimi.
    /// @return Viittaus, joka on voimassa olion elinajan.
    const std::string& nimi() const;

    /// @brief Laskee lokin tunnusluvut.
    /// @pre Lokissa on vähintään yksi arvo.
    /// @return Arvojen määrä, pienin, suurin ja keskiarvo.
    /// @throws std::logic_error jos loki on tyhjä.
    Yhteenveto yhteenveto() const;

private:
    struct Toteutus;
    std::unique_ptr<Toteutus> t_;
};

}  // namespace tutoriaali::mittaus

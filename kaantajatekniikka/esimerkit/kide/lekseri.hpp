// Leksikaalinen analyysi: lähdeteksti tokeneiksi.
#pragma once

#include <cstdint>
#include <string>
#include <string_view>
#include <vector>

#include "diagnostiikka.hpp"

namespace kide {

// @alku laji
enum class Laji {
    // Literaalit ja nimet
    Luku, Tunniste,
    // Avainsanat
    Fn, Var, If, Else, While, Return, Print, True, False, Int, Bool,
    // Operaattorit
    Plus, Miinus, Tahti, Kautta, Prosentti,
    Yhtasuuri, Erisuuri, Pienempi, PienempiYhta, Suurempi, SuurempiYhta,
    Ja, Tai, Ei, Sijoitus,
    // Välimerkit
    Nuoli, Kaksoispiste, Pilkku, Puolipiste,
    VasenSulku, OikeaSulku, VasenAalto, OikeaAalto,
    Loppu,
};

struct Tokeni {
    Laji laji;
    std::string teksti;      // lähdetekstin lekseemi
    Sijainti sijainti;
    std::int64_t arvo = 0;   // kokonaisluvun arvo
};
// @loppu laji

// Tokenin lajin nimi virheilmoituksiin, esim. "'+'" tai "tunniste".
std::string kuvaus(Laji laji);

// Selaa lähdetekstin. Virheelliset merkit raportoidaan ja ohitetaan;
// lista päättyy aina Loppu-tokeniin.
std::vector<Tokeni> selaa(std::string_view lahde, Diagnostiikka& diag);

}  // namespace kide

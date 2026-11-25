// mittausloki.cpp: toteutus. Vain tämä tiedosto tuntee Toteutus-rakenteen.
#include "mittausloki.hpp"

#include <algorithm>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <vector>

namespace tutoriaali::mittaus {

namespace {   // nimetön nimiavaruus: näkyy vain tässä käännösyksikössä

bool kelvollinen(double arvo)
{
    return std::isfinite(arvo);
}

}  // namespace

struct Mittausloki::Toteutus {
    std::string nimi;
    std::vector<double> arvot;
};

Mittausloki::Mittausloki(std::string_view nimi)
    : t_{std::make_unique<Toteutus>()}
{
    t_->nimi = nimi;
    t_->arvot.reserve(oletuskapasiteetti);
}

// Hajotin ja siirrot määritellään täällä, missä Toteutus on täydellinen
// tyyppi; unique_ptr tarvitsee sen tuhotessaan olion.
Mittausloki::~Mittausloki() = default;
Mittausloki::Mittausloki(Mittausloki&&) noexcept = default;
Mittausloki& Mittausloki::operator=(Mittausloki&&) noexcept = default;

void Mittausloki::lisaa(double arvo)
{
    if (!kelvollinen(arvo)) {
        throw std::invalid_argument{"mittausarvon on oltava äärellinen"};
    }
    t_->arvot.push_back(arvo);
}

const std::string& Mittausloki::nimi() const
{
    return t_->nimi;
}

Yhteenveto Mittausloki::yhteenveto() const
{
    const auto& a = t_->arvot;
    if (a.empty()) {
        throw std::logic_error{"yhteenveto tyhjästä lokista"};
    }
    auto [pienin, suurin] = std::ranges::minmax(a);
    double summa = std::accumulate(a.begin(), a.end(), 0.0);
    return {a.size(), pienin, suurin, summa / static_cast<double>(a.size())};
}

}  // namespace tutoriaali::mittaus

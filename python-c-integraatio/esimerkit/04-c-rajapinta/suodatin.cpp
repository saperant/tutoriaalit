// C++-toteutus C-rajapinnan takana. Poikkeukset eivät saa ylittää
// C-rajaa: ne napataan ja muutetaan virhekoodeiksi.
#include "suodatin.h"

#include <new>
#include <span>
#include <stdexcept>
#include <vector>

// @alku luokka
namespace {

class LiukuvaKeskiarvo {
public:
    explicit LiukuvaKeskiarvo(std::size_t ikkuna) : puskuri_(ikkuna)
    {
        if (ikkuna == 0)
            throw std::invalid_argument("ikkuna on 0");
    }

    double syota(double x)
    {
        summa_ += x - puskuri_[indeksi_];
        puskuri_[indeksi_] = x;
        indeksi_ = (indeksi_ + 1) % puskuri_.size();
        if (maara_ < puskuri_.size())
            ++maara_;
        return summa_ / static_cast<double>(maara_);
    }

private:
    std::vector<double> puskuri_;
    std::size_t indeksi_ = 0;
    std::size_t maara_ = 0;
    double summa_ = 0.0;
};

}  // namespace

struct suodatin {
    LiukuvaKeskiarvo toteutus;
};
// @loppu luokka

// @alku raja
extern "C" int suodatin_api_versio(void) { return SUODATIN_API_VERSIO; }

extern "C" suodatin_tila suodatin_luo(std::size_t ikkuna, suodatin **tulos)
{
    if (tulos == nullptr)
        return SUODATIN_VIRHEELLINEN_ARGUMENTTI;
    try {
        *tulos = new suodatin{LiukuvaKeskiarvo(ikkuna)};
        return SUODATIN_OK;
    } catch (const std::invalid_argument &) {
        return SUODATIN_VIRHEELLINEN_ARGUMENTTI;
    } catch (const std::bad_alloc &) {
        return SUODATIN_MUISTI_LOPPUI;
    } catch (...) {
        return SUODATIN_SISAINEN_VIRHE;
    }
}

extern "C" suodatin_tila suodatin_syota(suodatin *s, const double *sisaan,
                                        double *ulos, std::size_t n)
{
    if (s == nullptr || (n > 0 && (sisaan == nullptr || ulos == nullptr)))
        return SUODATIN_VIRHEELLINEN_ARGUMENTTI;
    std::span<const double> x(sisaan, n);
    std::span<double> y(ulos, n);
    for (std::size_t i = 0; i < n; ++i)
        y[i] = s->toteutus.syota(x[i]);
    return SUODATIN_OK;
}

extern "C" void suodatin_tuhoa(suodatin *s) { delete s; }
// @loppu raja

extern "C" const char *suodatin_virheviesti(suodatin_tila tila)
{
    switch (tila) {
    case SUODATIN_OK: return "ok";
    case SUODATIN_VIRHEELLINEN_ARGUMENTTI: return "virheellinen argumentti";
    case SUODATIN_MUISTI_LOPPUI: return "muisti loppui";
    case SUODATIN_SISAINEN_VIRHE: return "sisäinen virhe";
    }
    return "tuntematon virhe";
}

#include "tulkki.hpp"

#include <optional>
#include <ostream>
#include <stdexcept>
#include <unordered_map>

#include "semantiikka.hpp"

namespace kide {

namespace {

namespace s = semantiikka;

constexpr int kKutsujaEnintaan = 1000;

class Tulkki {
public:
    Tulkki(const Ohjelma& o, std::ostream& u) : ulos_(u) {
        for (const auto& f : o.funktiot) funktiot_[f.nimi] = &f;
    }
    std::int64_t kutsu(const std::string& nimi,
                       const std::vector<std::int64_t>& argumentit);

private:
    using Kehys = std::vector<std::int64_t>;   // muuttujat numeroittain
    // Paluuarvo, jos lause suoritti return-lauseen.
    using Tulos = std::optional<std::int64_t>;

    Tulos lauseet(const Lauseet& ls, Kehys& k);
    Tulos lause(const Lause& l, Kehys& k);
    std::int64_t arvo(const Lauseke& l, Kehys& k);
    std::int64_t binaari(const Binaari& b, Kehys& k);

    std::unordered_map<std::string, const Funktio*> funktiot_;
    std::ostream& ulos_;
    int syvyys_ = 0;
};

// @alku kehys
std::int64_t Tulkki::kutsu(const std::string& nimi,
                           const std::vector<std::int64_t>& argumentit) {
    if (++syvyys_ > kKutsujaEnintaan) {
        throw std::runtime_error("kutsupino täyttyi");
    }
    const Funktio& f = *funktiot_.at(nimi);
    Kehys kehys(f.muuttujat.size(), 0);
    std::copy(argumentit.begin(), argumentit.end(), kehys.begin());
    Tulos t = lauseet(f.runko, kehys);
    --syvyys_;
    return t.value_or(0);   // tarkistin takaa, että return suoritetaan
}
// @loppu kehys

Tulkki::Tulos Tulkki::lauseet(const Lauseet& ls, Kehys& k) {
    for (const auto& l : ls) {
        if (Tulos t = lause(*l, k)) return t;
    }
    return std::nullopt;
}

// @alku lause
Tulkki::Tulos Tulkki::lause(const Lause& l, Kehys& k) {
    return std::visit(Kaikki{
        [&](const Esittely& x) -> Tulos {
            k[x.muuttuja] = arvo(*x.arvo, k);
            return std::nullopt;
        },
        [&](const Sijoitus& x) -> Tulos {
            k[x.muuttuja] = arvo(*x.arvo, k);
            return std::nullopt;
        },
        [&](const Jos& x) -> Tulos {
            return lauseet(arvo(*x.ehto, k) ? x.tosi : x.epatosi, k);
        },
        [&](const Kun& x) -> Tulos {
            while (arvo(*x.ehto, k)) {
                if (Tulos t = lauseet(x.runko, k)) return t;
            }
            return std::nullopt;
        },
        [&](const Palauta& x) -> Tulos { return arvo(*x.arvo, k); },
        [&](const Tulosta& x) -> Tulos {
            ulos_ << arvo(*x.arvo, k) << '\n';
            return std::nullopt;
        },
        [&](const LausekeLause& x) -> Tulos {
            arvo(*x.lauseke, k);
            return std::nullopt;
        },
        [&](const Lohko& x) -> Tulos { return lauseet(x.lauseet, k); },
    }, l.v);
}
// @loppu lause

// @alku arvo
std::int64_t Tulkki::arvo(const Lauseke& l, Kehys& k) {
    return std::visit(Kaikki{
        [](const Luku& x) { return x.arvo; },
        [](const Totuus& x) -> std::int64_t { return x.arvo; },
        [&](const Nimi& x) { return k[x.muuttuja]; },
        [&](const Unaari& x) {
            std::int64_t a = arvo(*x.a, k);
            return x.op == Laji::Miinus ? s::vastaluku(a)
                                        : std::int64_t{a == 0};
        },
        [&](const Binaari& x) { return binaari(x, k); },
        [&](const Kutsu& x) {
            std::vector<std::int64_t> argumentit;
            for (const auto& a : x.argumentit) {
                argumentit.push_back(arvo(*a, k));
            }
            return kutsu(x.funktio, argumentit);
        },
    }, l.v);
}

std::int64_t Tulkki::binaari(const Binaari& b, Kehys& k) {
    // && ja || laskevat oikean puolen vain tarvittaessa (oikosulku).
    if (b.op == Laji::Ja) return arvo(*b.vasen, k) && arvo(*b.oikea, k);
    if (b.op == Laji::Tai) return arvo(*b.vasen, k) || arvo(*b.oikea, k);
    std::int64_t x = arvo(*b.vasen, k);
    std::int64_t y = arvo(*b.oikea, k);
    switch (b.op) {
    case Laji::Plus: return s::summa(x, y);
    case Laji::Miinus: return s::erotus(x, y);
    case Laji::Tahti: return s::tulo(x, y);
    case Laji::Kautta: return s::osamaara(x, y);
    case Laji::Prosentti: return s::jakojaannos(x, y);
    case Laji::Yhtasuuri: return x == y;
    case Laji::Erisuuri: return x != y;
    case Laji::Pienempi: return x < y;
    case Laji::PienempiYhta: return x <= y;
    case Laji::Suurempi: return x > y;
    case Laji::SuurempiYhta: return x >= y;
    default: throw std::logic_error("tuntematon operaattori");
    }
}
// @loppu arvo

}  // namespace

std::int64_t tulkitse(const Ohjelma& ohjelma, std::ostream& ulos) {
    return Tulkki(ohjelma, ulos).kutsu("main", {});
}

}  // namespace kide

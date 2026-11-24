// Vartijan tekoäly tilakoneena: tilat ovat tyyppejä, ja kunkin tilan
// data elää vain tilan ajan (std::variant).
#include <cmath>
#include <print>
#include <type_traits>
#include <variant>

// @alku tilat
struct Partio {
    int suunta = 1;  // +1 oikealle, -1 vasemmalle
};
struct TakaaAjo {
    double nakyi_viimeksi = 0.0;  // pelaajan viimeisin tunnettu paikka
};
struct Etsinta {
    int ruutuja_jaljella = 0;
};
using Tila = std::variant<Partio, TakaaAjo, Etsinta>;
// @loppu tilat

constexpr double NAKO = 5.0;

struct Vartija {
    double x = 0.0;
    Tila tila = Partio{};

    // @alku siirtymat
    void paivita(double pelaaja) {
        const bool nakee = std::abs(pelaaja - x) < NAKO;
        Tila uusi = std::visit(
            [&](auto& t) -> Tila {
                using T = std::decay_t<decltype(t)>;
                if constexpr (std::is_same_v<T, Partio>) {
                    x += 0.5 * t.suunta;
                    if (std::abs(x) >= 4.0) {
                        t.suunta = -t.suunta;
                    }
                    if (nakee) {
                        return TakaaAjo{pelaaja};
                    }
                } else if constexpr (std::is_same_v<T, TakaaAjo>) {
                    if (nakee) {
                        t.nakyi_viimeksi = pelaaja;
                    }
                    x += (t.nakyi_viimeksi > x) ? 1.0 : -1.0;
                    if (!nakee) {
                        return Etsinta{3};
                    }
                } else {
                    if (nakee) {
                        return TakaaAjo{pelaaja};
                    }
                    if (--t.ruutuja_jaljella == 0) {
                        return Partio{};
                    }
                }
                return t;
            },
            tila);
        tila = uusi;
    }
    // @loppu siirtymat
};

const char* nimi(const Tila& t) {
    constexpr const char* NIMET[] = {"partio", "takaa-ajo", "etsintä"};
    return NIMET[t.index()];
}

int main() {
    Vartija v;
    const double pelaaja[] = {9, 9, 7, 6, 6, 4, 20, 20, 20, 20, 20, 20};
    const char* edellinen = nimi(v.tila);
    for (int ruutu = 0; double p : pelaaja) {
        v.paivita(p);
        if (nimi(v.tila) != edellinen) {
            std::println("ruutu {:2}: {} -> {} (x = {:.1f})", ruutu,
                         edellinen, nimi(v.tila), v.x);
            edellinen = nimi(v.tila);
        }
        ++ruutu;
    }
}

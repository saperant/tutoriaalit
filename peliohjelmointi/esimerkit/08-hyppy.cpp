// Hypyn suunnittelu: painovoima ja alkunopeus lasketaan halutusta
// korkeudesta ja ajasta, ei kokeilemalla. Napin vapautus lyhentää
// hyppyä, ja putoaminen on nousua nopeampaa.
#include <algorithm>
#include <print>
#include <vector>

// @alku parametrit
struct Hyppyparametrit {
    double painovoima;    // m/s², nousun aikana
    double alkunopeus;    // m/s
};

// Huippu korkeudella h ajassa t: h = v t - g t²/2 ja v = g t.
constexpr Hyppyparametrit parametrit(double korkeus, double aika) {
    return {2.0 * korkeus / (aika * aika), 2.0 * korkeus / aika};
}
// @loppu parametrit

struct Tulos {
    double huippu;
    int ruutuja;
};

// @alku simulointi
Tulos hyppaa(Hyppyparametrit p, int pidetaan_ruutuja,
             double putoamiskerroin, std::vector<double>* rata = nullptr) {
    constexpr double dt = 1.0 / 60.0;
    double y = 0.0, vy = p.alkunopeus, huippu = 0.0;
    int ruutu = 0;
    do {
        double g = p.painovoima;
        if (vy < 0.0) {
            g *= putoamiskerroin;  // raskaampi putoaminen
        } else if (ruutu >= pidetaan_ruutuja) {
            vy = std::min(vy, p.alkunopeus * 0.4);  // nappi vapautettu
        }
        vy -= g * dt;
        y += vy * dt;
        huippu = std::max(huippu, y);
        ++ruutu;
        if (rata != nullptr) {
            rata->push_back(y);  // korkeus ruuduittain kuvaajaa varten
        }
    } while (y > 0.0);
    return {huippu, ruutu};
}
// @loppu simulointi

int main(int argc, char**) {
    constexpr auto p = parametrit(3.0, 0.4);  // 3 m, huippu 0,4 s:ssa
    if (argc > 1) {  // käyrätila kuvitusta varten
        int n = 0;
        for (auto [pito, kerroin] : {std::pair{1000, 1.0},
                                     std::pair{6, 1.0},
                                     std::pair{1000, 2.0}}) {
            std::vector<double> rata;
            hyppaa(p, pito, kerroin, &rata);
            for (std::size_t i = 0; i < rata.size(); ++i) {
                std::println("{} {} {:.5f}", n, i + 1, rata[i]);
            }
            ++n;
        }
        return 0;
    }
    std::println("painovoima {:.1f} m/s², alkunopeus {:.1f} m/s",
                 p.painovoima, p.alkunopeus);
    for (auto [nimi, pito, kerroin] :
         {std::tuple{"pitkä painallus", 1000, 1.0},
          std::tuple{"lyhyt painallus", 6, 1.0},
          std::tuple{"pitkä, raskas pudotus", 1000, 2.0}}) {
        const Tulos t = hyppaa(p, pito, kerroin);
        std::println("{:22} huippu {:.2f} m, ilmassa {} ruutua", nimi,
                     t.huippu, t.ruutuja);
    }
}

// Muiden pelaajien näyttäminen: uusin vedos sellaisenaan, interpolointi
// kahden vedoksen välillä pienellä puskuriviiveellä tai ekstrapolointi
// uusimmasta eteenpäin. Palvelin lähettää 20 vedosta sekunnissa.
#include <cstdint>
#include <cstdlib>
#include <optional>
#include <print>
#include <vector>

#include "yhteinen/verkko.hpp"

// Todellinen liike: edestakaisin 1 metrin matkaa sekunnissa (mm).
std::int64_t tosi_x(std::int64_t t) {
    const std::int64_t v = t % 2000;
    return v < 1000 ? v : 2000 - v;
}

struct Vedos {
    std::int64_t aika, x;
};

// @alku interpoloi
// Etsii vedokset, joiden väliin näyttöhetki osuu, ja interpoloi.
// Jos uudempaa vedosta ei vielä ole, puskuri on tyhjentynyt.
std::optional<std::int64_t> interpoloi(const std::vector<Vedos>& v,
                                       std::int64_t hetki) {
    for (std::size_t i = 1; i < v.size(); ++i) {
        if (v[i - 1].aika <= hetki && hetki <= v[i].aika) {
            const std::int64_t kesto = v[i].aika - v[i - 1].aika;
            return v[i - 1].x +
                   (v[i].x - v[i - 1].x) * (hetki - v[i - 1].aika) / kesto;
        }
    }
    return std::nullopt;
}
// @loppu interpoloi

int main() {
    const Linkki linkki{.viive_ms = 50, .varina_ms = 40,
                        .havio_promille = 30};
    for (int tapa = 0; tapa < 5; ++tapa) {
        Kanava<Vedos> kanava(linkki, 21);
        std::vector<Vedos> saadut;  // aikajärjestyksessä
        const std::int64_t puskuri = tapa == 2 ? 50 : tapa == 3 ? 100 : 150;
        std::int64_t virhe = 0, kuvia = 0, tyhjana = 0;
        for (std::int64_t t = 0; t < 20'000; ++t) {
            if (t % 50 == 0) {
                kanava.laheta(t, {t, tosi_x(t)});
            }
            for (const Vedos& v : kanava.vastaanota(t)) {
                if (saadut.empty() || v.aika > saadut.back().aika) {
                    saadut.push_back(v);  // vanhentunut hylätään
                }
            }
            if (t % 16 != 0 || t < 1000 || saadut.size() < 2) {
                continue;  // piirretään noin 60 kertaa sekunnissa
            }
            ++kuvia;
            const Vedos& uusin = saadut.back();
            const Vedos& edellinen = saadut[saadut.size() - 2];
            // @alku tavat
            std::int64_t naytetty, esittaa;
            if (tapa == 0) {  // uusin sellaisenaan
                naytetty = uusin.x;
                esittaa = t;
            } else if (tapa == 1) {  // ekstrapolointi nykyhetkeen
                const std::int64_t nopeus_x1000 =
                    (uusin.x - edellinen.x) * 1000 /
                    (uusin.aika - edellinen.aika);
                naytetty = uusin.x + nopeus_x1000 * (t - uusin.aika) / 1000;
                esittaa = t;
            } else {  // interpolointi puskuriviiveellä
                esittaa = t - puskuri;
                const auto x = interpoloi(saadut, esittaa);
                if (!x) {
                    ++tyhjana;  // pidetään viimeisin paikka
                }
                naytetty = x.value_or(uusin.x);
            }
            // @loppu tavat
            virhe += std::abs(naytetty - tosi_x(esittaa));
        }
        const char* nimet[] = {"uusin vedos", "ekstrapolointi",
                               "interp. 50 ms", "interp. 100 ms",
                               "interp. 150 ms"};
        std::println("{:<15} virhe ka. {:>3} mm, puskuri tyhjä {:>3} %",
                     nimet[tapa], virhe / kuvia, tyhjana * 100 / kuvia);
    }
}

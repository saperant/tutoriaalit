// Moninpeliesimerkkien yhteiset osat: PCG32-generaattori ja simuloitu
// verkkoyhteys. Aika on kokonaislukuina millisekunteina, jotta kaikki
// esimerkit ovat deterministisiä kaikilla alustoilla.
#pragma once
#include <algorithm>
#include <cstdint>
#include <format>
#include <print>
#include <utility>
#include <vector>

// @alku pcg
// PCG32 (O'Neill 2014), sama kuin tutoriaalissa Peliohjelmointi.
class Pcg32 {
public:
    explicit Pcg32(std::uint64_t siemen, std::uint64_t virta = 54)
        : lisays_((virta << 1u) | 1u) {
        seuraava();
        tila_ += siemen;
        seuraava();
    }
    std::uint32_t seuraava() {
        const std::uint64_t vanha = tila_;
        tila_ = vanha * 6364136223846793005ULL + lisays_;
        const auto x =
            static_cast<std::uint32_t>(((vanha >> 18u) ^ vanha) >> 27u);
        const auto k = static_cast<std::uint32_t>(vanha >> 59u);
        return (x >> k) | (x << ((32u - k) & 31u));
    }
    // Tasainen kokonaisluku välillä [0, raja) ilman vinoumaa.
    std::uint32_t valilta(std::uint32_t raja) {
        const std::uint32_t kynnys = (0u - raja) % raja;
        for (;;) {
            const std::uint32_t r = seuraava();
            if (r >= kynnys) {
                return r % raja;
            }
        }
    }

private:
    std::uint64_t tila_ = 0;
    std::uint64_t lisays_;
};
// @loppu pcg

// @alku linkki
// Yhden suunnan verkkoyhteyden ominaisuudet.
struct Linkki {
    int viive_ms = 50;       // perusviive (puolet kiertoviiveestä)
    int varina_ms = 0;       // lisäviive tasaisesti välillä [0, varina]
    int havio_promille = 0;  // hukattujen pakettien osuus tuhannesosina
};

// Simuloitu yhteys: lähetetty viesti saapuu perusviiveen ja satunnaisen
// värinän jälkeen tai katoaa. Värinä voi muuttaa järjestystä.
template <class T>
class Kanava {
public:
    Kanava(Linkki linkki, std::uint64_t siemen)
        : linkki_(linkki), satunnainen_(siemen) {}

    void laheta(std::int64_t nyt, T viesti) {
        ++lahetetty_;
        const auto h = static_cast<int>(satunnainen_.valilta(1000));
        if (h < linkki_.havio_promille) {
            ++hukattu_;
            return;
        }
        const auto varina = static_cast<std::int64_t>(
            satunnainen_.valilta(
                static_cast<std::uint32_t>(linkki_.varina_ms) + 1u));
        matkalla_.push_back(
            {nyt + linkki_.viive_ms + varina, juokseva_++,
             std::move(viesti)});
    }

    // Palauttaa saapuneet viestit saapumisjärjestyksessä.
    std::vector<T> vastaanota(std::int64_t nyt) {
        std::stable_sort(matkalla_.begin(), matkalla_.end(),
                         [](const auto& a, const auto& b) {
                             return a.saapuu < b.saapuu;
                         });
        std::vector<T> saapuneet;
        auto it = matkalla_.begin();
        while (it != matkalla_.end() && it->saapuu <= nyt) {
            saapuneet.push_back(std::move(it->viesti));
            ++it;
        }
        matkalla_.erase(matkalla_.begin(), it);
        return saapuneet;
    }

    int lahetetty() const { return lahetetty_; }
    int hukattu() const { return hukattu_; }

private:
    struct Matkalla {
        std::int64_t saapuu;
        std::uint64_t jarjestys;
        T viesti;
    };
    Linkki linkki_;
    Pcg32 satunnainen_;
    std::vector<Matkalla> matkalla_;
    std::uint64_t juokseva_ = 0;
    int lahetetty_ = 0;
    int hukattu_ = 0;
};
// @loppu linkki

// Tapahtumaloki kuvitusta varten: lokirivit tulostuvat vain, kun
// esimerkki käynnistetään argumentilla (ks. kuvat/piirra.py). Testit
// ajavat esimerkit ilman argumenttia.
inline bool loki_paalla = false;

template <class... A>
void loki(std::format_string<A...> muoto, A&&... a) {
    if (loki_paalla) {
        std::print("@ ");
        std::println(muoto, std::forward<A>(a)...);
    }
}

// Haarautumisen ennustimet testiohjelmilla: tarkkuus ja CPI.
#include <algorithm>
#include <array>
#include <format>
#include <memory>
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "yhteinen/kone.hpp"
#include "yhteinen/liukuhihna.hpp"
#include "yhteinen/ohjelmat.hpp"

// @alku gshare
// Globaali historia: viimeisten h haaran suunnat bitteinä. Taulukon
// indeksi on historia XOR osoite, joten sama haara saa eri laskurin
// eri historioilla, ja toistuvat kuviot opitaan.
class Gshare final : public rv::Ennustin {
public:
    explicit Gshare(int h) : h_(h), tilat_(std::size_t{1} << h, 1) {}
    std::string nimi() const override {
        return std::format("gshare ({})", tilat_.size());
    }
    bool ennusta(rv::u32 pc, rv::u32) override {
        return tilat_[indeksi(pc)] >= 2;
    }
    void paivita(rv::u32 pc, bool otettu) override {
        auto& t = tilat_[indeksi(pc)];
        t = static_cast<std::uint8_t>(otettu ? std::min(t + 1, 3)
                                             : std::max(t - 1, 0));
        historia_ = (historia_ << 1 | otettu) & ((1u << h_) - 1);
    }

private:
    std::size_t indeksi(rv::u32 pc) const { return (pc >> 2 ^ historia_)
                                                   & ((1u << h_) - 1); }
    int h_;
    rv::u32 historia_ = 0;
    std::vector<std::uint8_t> tilat_;
};
// @loppu gshare

int main() {
    // @alku vertailu
    const std::array<std::pair<std::string_view, std::string_view>, 5>
        testit{{{"summa", ohjelmat::summa}, {"kupla", ohjelmat::kupla},
                {"matriisi", ohjelmat::matriisi}, {"fib", ohjelmat::fib},
                {"lista", ohjelmat::lista}}};
    std::vector<std::vector<rv::Tapahtuma>> jaljet;
    for (const auto& [nimi, lahde] : testit) {
        rv::Kone kone(rv::koota(lahde));
        jaljet.push_back(kone.aja());
    }
    // Jokainen ohjelma saa uuden ennustimen, jonka tila on alkutila.
    auto tee = [](int i) -> std::unique_ptr<rv::Ennustin> {
        switch (i) {
        case 0: return std::make_unique<rv::AinaEi>();
        case 1: return std::make_unique<rv::Taaksepain>();
        case 2: return std::make_unique<rv::Laskuri>(1, 64);
        case 3: return std::make_unique<rv::Laskuri>(2, 64);
        case 4: return std::make_unique<rv::Laskuri>(2, 1);
        default: return std::make_unique<Gshare>(8);
        }
    };
    for (const bool cpi : {false, true}) {
        std::print("{:<18}", cpi ? "CPI" : "tarkkuus (%)");
        for (const auto& [nimi, lahde] : testit) std::print("{:>9}", nimi);
        std::println();
        for (int i = 0; i < 6; ++i) {
            std::print("{:<18}", tee(i)->nimi());
            for (const auto& jalki : jaljet) {
                const auto e = tee(i);
                const rv::Tulos t = rv::simuloi(jalki, {.ennustin = e.get()});
                if (cpi) std::print("{:>9.2f}", t.cpi());
                else std::print("{:>9.1f}", 100 * t.tarkkuus());
            }
            std::println();
        }
        std::println();
    }
    // @loppu vertailu
    // @alku haarat
    // Montako eri haarakäskyä ohjelmissa on ja kuinka usein ne toteutuvat.
    for (std::size_t i = 0; i < jaljet.size(); ++i) {
        std::vector<rv::u32> eri;
        long haarat = 0, otetut = 0;
        for (const rv::Tapahtuma& t : jaljet[i]) {
            if (!t.haara) continue;
            ++haarat;
            otetut += t.otettu;
            if (std::ranges::find(eri, t.pc) == eri.end())
                eri.push_back(t.pc);
        }
        std::println("{:<9} {} haarakäskyä, {:5} suoritusta, {:4.1f} % "
                     "toteutuu", testit[i].first, eri.size(), haarat,
                     100.0 * static_cast<double>(otetut) /
                         static_cast<double>(haarat));
    }
    // @loppu haarat
}

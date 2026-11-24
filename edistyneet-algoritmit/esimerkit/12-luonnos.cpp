// Tietovirran tiivistelmät: Count-Min-luonnos esiintymien arvioimiseen
// ja säiliöotanta tasaiseen otokseen tuntemattoman pituisesta virrasta.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <print>
#include <vector>

#include "testaus.hpp"

// @alku countmin
// d riviä, kullakin oma hajautusfunktio ja w laskuria. Arvio on rivien
// pienin laskuri: törmäykset voivat vain kasvattaa laskuria, joten
// arvio ei ole koskaan liian pieni. Kun w = ceil(e / eps) ja
// d = ceil(ln(1 / delta)), virhe on <= eps N todennäköisyydellä
// vähintään 1 - delta (N = virran pituus).
class CountMin {
public:
    CountMin(std::size_t leveys, std::size_t syvyys, std::uint64_t siemen)
        : leveys_{leveys}, laskurit_(leveys * syvyys, 0)
    {
        Satunnainen s{siemen};
        for (std::size_t i = 0; i < syvyys; ++i) {
            suolat_.push_back(s.seuraava());
        }
    }

    void lisaa(std::uint64_t x)
    {
        for (std::size_t r = 0; r < suolat_.size(); ++r) {
            ++laskurit_[r * leveys_ + sarake(x, r)];
        }
    }

    long arvio(std::uint64_t x) const
    {
        long pienin = laskurit_[sarake(x, 0)];
        for (std::size_t r = 1; r < suolat_.size(); ++r) {
            pienin = std::min(pienin, laskurit_[r * leveys_ + sarake(x, r)]);
        }
        return pienin;
    }

private:
    std::size_t sarake(std::uint64_t x, std::size_t r) const
    {
        std::uint64_t z = x ^ suolat_[r];
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9u;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBu;
        return (z ^ (z >> 31)) % leveys_;
    }

    std::size_t leveys_;
    std::vector<long> laskurit_;
    std::vector<std::uint64_t> suolat_;
};
// @loppu countmin

// @alku sailio
// Säiliöotanta (algoritmi R): k ensimmäistä alkiota säiliöön, sen
// jälkeen alkio i (0-pohjainen) korvaa satunnaisen säiliön alkion
// todennäköisyydellä k / (i + 1). Induktiolla jokainen tähän asti
// nähty alkio on säiliössä todennäköisyydellä k / (i + 1).
template <std::size_t K>
class Sailio {
public:
    void nae(int x, Satunnainen& s)
    {
        if (nahty_ < K) {
            otos_[nahty_] = x;
        } else if (auto j = s.alle(nahty_ + 1); j < K) {
            otos_[j] = x;
        }
        ++nahty_;
    }
    const std::array<int, K>& otos() const { return otos_; }

private:
    std::array<int, K> otos_{};
    std::uint64_t nahty_ = 0;
};
// @loppu sailio

int main()
{
    // @alku virta
    // Zipfin jakauma: tuotteen r osuus on verrannollinen lukuun 1 / r,
    // kuten verkkokaupan katseluissa. Arvonta käänteisellä kertymällä.
    constexpr int tuotteita = 100000, n = 200000;
    std::vector<double> kertyma(tuotteita);
    double summa = 0;
    for (int r = 0; r < tuotteita; ++r) {
        summa += 1.0 / (r + 1);
        kertyma[static_cast<std::size_t>(r)] = summa;
    }
    Satunnainen s{21};
    constexpr double eps = 0.002, delta = 0.01;
    auto w = static_cast<std::size_t>(std::ceil(std::exp(1.0) / eps));
    auto d = static_cast<std::size_t>(std::ceil(std::log(1 / delta)));
    CountMin luonnos{w, d, 5};
    std::vector<long> tarkka(tuotteita, 0);
    for (int i = 0; i < n; ++i) {
        double u = s.yksikko() * summa;
        auto r = static_cast<std::size_t>(
            std::ranges::upper_bound(kertyma, u) - kertyma.begin());
        r = std::min(r, kertyma.size() - 1);
        ++tarkka[r];
        luonnos.lisaa(r);
    }
    int ylittaa = 0;
    long suurin_virhe = 0;
    for (std::size_t r = 0; r < tarkka.size(); ++r) {
        long virhe = luonnos.arvio(r) - tarkka[r];
        vaadi(virhe >= 0, "arvio on liian pieni");
        suurin_virhe = std::max(suurin_virhe, virhe);
        ylittaa += virhe > eps * n ? 1 : 0;
    }
    std::println("Count-Min {} x {} = {} laskuria {} tuotteelle", d, w,
                 d * w, tuotteita);
    std::println("raja eps N = {:.0f}: ylittää {} / {}, suurin virhe {}",
                 eps * n, ylittaa, tuotteita, suurin_virhe);
    for (std::size_t r : {0, 1, 9, 99, 999, 9999}) {
        std::println("  tuote {:5}: tarkka {:5}, arvio {:5}", r + 1,
                     tarkka[r], luonnos.arvio(r));
    }
    // @loppu virta

    // @alku otanta
    // 30 000 kertaa otos 4 alkiota 20 alkion virrasta: jokaisen alkion
    // pitäisi esiintyä 6 000 otoksessa.
    std::array<int, 20> kertoja{};
    for (int koe = 0; koe < 30000; ++koe) {
        Sailio<4> sailio;
        for (int x = 0; x < 20; ++x) {
            sailio.nae(x, s);
        }
        for (int x : sailio.otos()) {
            ++kertoja[static_cast<std::size_t>(x)];
        }
    }
    double khii = 0;
    for (int k : kertoja) {
        khii += (k - 6000.0) * (k - 6000.0) / 6000.0;
    }
    // Khii toiseen -testi, 19 vapausastetta: 95 %:n raja on 30,1.
    std::println("otanta: {} ... {} kertaa, khii^2 = {:.1f}",
                 std::ranges::min(kertoja), std::ranges::max(kertoja), khii);
    // @loppu otanta
}

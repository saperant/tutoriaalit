// Testivektorit C/RTL-yhteissimulaatiota varten.
//
// C-testipenkki kirjaa jokaisen tapauksen syötteet ja odotetut tulokset.
// tallenna() kirjoittaa ne tiedostoihin nimi.in.hex ja nimi.out.hex
// (32-bittisinä heksalukuina, yksi rivillä) sekä tapausten määrän
// tiedostoon tapaukset.hex. minihls:n testipenkki lukee samat tiedostot.
#pragma once
#include <cstdint>
#include <cstdio>
#include <map>
#include <span>
#include <string>
#include <vector>

namespace vektorit {

class Tallennin {
public:
    // @alku tallennin
    void syote(const std::string& nimi, std::span<const int> arvot) {
        lisaa(syotteet_[nimi], arvot);
    }
    void syote(const std::string& nimi, int arvo) {
        syotteet_[nimi].push_back(arvo);
    }
    void odotettu(const std::string& nimi, std::span<const int> arvot) {
        lisaa(odotetut_[nimi], arvot);
    }
    void paluu(int arvo) { odotetut_["paluu"].push_back(arvo); }
    void tapaus_valmis() { ++tapauksia_; }
    // @loppu tallennin

    int tapauksia() const { return tapauksia_; }

    bool tallenna() const {
        bool ok = kirjoita("tapaukset.hex", {tapauksia_});
        for (const auto& [nimi, arvot] : syotteet_)
            ok = kirjoita(nimi + ".in.hex", arvot) && ok;
        for (const auto& [nimi, arvot] : odotetut_)
            ok = kirjoita(nimi + ".out.hex", arvot) && ok;
        return ok;
    }

private:
    static void lisaa(std::vector<int>& kohde, std::span<const int> arvot) {
        kohde.insert(kohde.end(), arvot.begin(), arvot.end());
    }
    static bool kirjoita(const std::string& nimi,
                         const std::vector<int>& arvot) {
        std::FILE* f = std::fopen(nimi.c_str(), "w");
        if (f == nullptr) return false;
        for (int arvo : arvot)
            std::fprintf(f, "%08x\n", static_cast<std::uint32_t>(arvo));
        return std::fclose(f) == 0;
    }

    std::map<std::string, std::vector<int>> syotteet_, odotetut_;
    int tapauksia_ = 0;
};

// Toistettava näennäissatunnaisluku (xorshift32): sama siemen antaa
// samat testivektorit kaikilla koneilla ja kääntäjillä.
class Satunnainen {
public:
    explicit Satunnainen(std::uint32_t siemen) : tila_(siemen) {}
    int vali(int pienin, int suurin) {
        tila_ ^= tila_ << 13;
        tila_ ^= tila_ >> 17;
        tila_ ^= tila_ << 5;
        auto leveys = static_cast<std::uint32_t>(suurin - pienin + 1);
        return pienin + static_cast<int>(tila_ % leveys);
    }

private:
    std::uint32_t tila_;
};

}  // namespace vektorit

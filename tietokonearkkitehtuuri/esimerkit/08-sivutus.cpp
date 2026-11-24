// Sv32-sivutus: kaksitasoinen sivutaulu fyysisessä muistissa,
// osoitteenmuunnos askel askeleelta ja sivuvirheet.
#include <cstdint>
#include <map>
#include <optional>
#include <print>
#include <string>

using u32 = std::uint32_t;
using u64 = std::uint64_t;

// @alku pte
// Sivutaulun alkion (PTE) bitit (U = 16 ja G = 32 jätetään pois).
constexpr u32 V = 1, R = 2, W = 4, X = 8, A = 64, D = 128;

// Fyysinen muisti harvana: sana-osoite -> arvo.
struct Muisti {
    std::map<u64, u32> sanat;
    u32 lue(u64 a) const {
        const auto i = sanat.find(a);
        return i == sanat.end() ? 0 : i->second;
    }
    void kirjoita(u64 a, u32 v) { sanat[a] = v; }
};

constexpr u32 pte(u64 fyysinen, u32 bitit) {
    return static_cast<u32>(fyysinen >> 12 << 10) | bitit;  // PPN | liput
}
// @loppu pte

// @alku kaanna
enum class Paasy { nouto, lataus, talletus };

// Palauttaa fyysisen osoitteen tai sivuvirheen syykoodin (12, 13, 15).
struct Tulos { std::optional<u64> fyysinen; u32 syy = 0; };

Tulos kaanna(Muisti& m, u64 juuri, u32 va, Paasy p, bool tulosta) {
    const u32 syy = p == Paasy::nouto ? 12 : p == Paasy::lataus ? 13 : 15;
    u64 taulu = juuri;
    for (int taso = 1; taso >= 0; --taso) {
        const u32 vpn = va >> (12 + 10 * taso) & 0x3ff;
        const u64 osoite = taulu + 4 * vpn;
        const u32 e = m.lue(osoite);
        if (tulosta)
            std::println("  taso {}: VPN[{}] = {:3}, PTE @0x{:05x} = "
                         "0x{:08x}", taso, taso, vpn, osoite, e);
        if (!(e & V) || (!(e & R) && (e & W))) return {std::nullopt, syy};
        if (e & (R | X)) {  // lehti
            const bool sallittu = p == Paasy::nouto     ? (e & X)
                                  : p == Paasy::lataus ? (e & R)
                                                       : (e & W);
            if (!sallittu) return {std::nullopt, syy};
            // Megasivu (taso 1): alemman VPN:n on oltava osa siirtymää.
            const u64 ppn = static_cast<u64>(e >> 10);
            if (taso == 1 && (ppn & 0x3ff)) return {std::nullopt, syy};
            m.kirjoita(osoite, e | A | (p == Paasy::talletus ? D : 0));
            const u32 siirto_bitit = 12 + 10 * static_cast<u32>(taso);
            const u64 siirto = va & ((u64{1} << siirto_bitit) - 1);
            return {(ppn << 12 & ~((u64{1} << siirto_bitit) - 1)) | siirto,
                    0};
        }
        taulu = static_cast<u64>(e >> 10) << 12;  // seuraava taso
    }
    return {std::nullopt, syy};
}
// @loppu kaanna

int main() {
    // @alku kartta
    Muisti m;
    const u64 juuri = 0x10000, toinen = 0x11000;
    // Koodi 0x0040'0000 -> 0x8000'0000 (R X), data 0x0040'1000 ->
    // 0x8000'5000 (R W), 4 MiB:n megasivu 0xc000'0000 -> 0x4000'0000.
    m.kirjoita(juuri + 4 * 1, pte(toinen, V));          // ei lehti
    m.kirjoita(toinen + 4 * 0, pte(0x8000'0000, V | R | X));
    m.kirjoita(toinen + 4 * 1, pte(0x8000'5000, V | R | W));
    m.kirjoita(juuri + 4 * 768, pte(0x4000'0000, V | R | W));
    const struct { u32 va; Paasy p; const char* kuvaus; } kokeet[] = {
        {0x0040'0010, Paasy::nouto, "käskyn nouto"},
        {0x0040'1234, Paasy::talletus, "talletus dataan"},
        {0xc012'3456, Paasy::lataus, "lataus megasivulta"},
        {0x0040'0010, Paasy::talletus, "talletus koodiin"},
        {0x0040'2000, Paasy::lataus, "kuvaamaton sivu"}};
    for (const auto& k : kokeet) {
        std::println("{} 0x{:08x}:", k.kuvaus, k.va);
        const Tulos t = kaanna(m, juuri, k.va, k.p, true);
        if (t.fyysinen) std::println("  -> fyysinen 0x{:09x}", *t.fyysinen);
        else std::println("  -> sivuvirhe, mcause = {}", t.syy);
    }
    std::println("data-PTE nyt 0x{:08x} (A ja D asetettu)",
                 m.lue(toinen + 4));
    // @loppu kartta
    // @alku sv39
    // Sv39: kolme 9-bittistä VPN-kenttää; bittien 63..39 on oltava
    // bitin 38 kopioita (kanoninen osoite).
    for (const u64 va : {u64{0x0000'0012'3456'7abc},
                         u64{0xffff'ffc0'0000'1000},
                         u64{0x0000'0080'0000'0000}}) {
        const bool kanoninen =
            static_cast<std::int64_t>(va << 25) >> 25 ==
            static_cast<std::int64_t>(va);
        std::println("0x{:016x}: VPN {:3} {:3} {:3} siirtymä 0x{:03x}{}",
                     va, va >> 30 & 0x1ff, va >> 21 & 0x1ff,
                     va >> 12 & 0x1ff, va & 0xfff,
                     kanoninen ? "" : "  ei kanoninen");
    }
    // @loppu sv39
}

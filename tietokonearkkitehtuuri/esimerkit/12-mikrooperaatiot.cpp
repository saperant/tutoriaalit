// CISC-käskyjen purku mikro-operaatioiksi (µop). Lelumalli x86-tyylisille
// käskyille: muistioperandi tuottaa latauksen, muistikohde lisäksi
// talletuksen (osoite + data), ja cmp + ehdollinen hyppy sulautuvat.
#include <print>
#include <string>
#include <string_view>
#include <vector>

#include "yhteinen/rv32i.hpp"

// @alku purku
struct Kasky {
    std::string_view teksti;
    int tavut;  // todellisen x86-koodauksen pituus (32-bittinen tila)
};

bool muisti(std::string_view operandi) {
    return operandi.find('[') != std::string_view::npos;
}

std::vector<std::string> mikro(std::string_view k, bool& sulautuu) {
    const auto valit = k.find(' ');
    const std::string_view op = k.substr(0, valit);
    const std::string_view loput =
        valit == std::string_view::npos ? "" : k.substr(valit + 1);
    const auto pilkku = loput.find(',');
    const std::string_view kohde = loput.substr(0, pilkku);
    const std::string_view lahde =
        pilkku == std::string_view::npos ? "" : loput.substr(pilkku + 2);
    if (op == "cmp" || op == "test") { sulautuu = true; return {"alu"}; }
    if (op.starts_with("j")) {
        if (sulautuu) { sulautuu = false; return {"(sulautui)"}; }
        return {"hyppy"};
    }
    sulautuu = false;
    if (op == "push") return {"tal-os", "tal-data"};
    if (op == "pop") return {"lataus"};
    if (op == "call") return {"tal-os", "tal-data", "hyppy"};
    if (op == "ret") return {"lataus", "hyppy"};
    if (op == "mov") {
        if (muisti(lahde)) return {"lataus"};
        if (muisti(kohde)) return {"tal-os", "tal-data"};
        return {"alu"};
    }
    // Laskutoimitus: add, sub, inc, and, ...
    if (muisti(kohde)) return {"lataus", "alu", "tal-os", "tal-data"};
    if (muisti(lahde)) return {"lataus", "alu"};
    return {"alu"};
}
// @loppu purku

int main() {
    // @alku taulu
    const std::vector<Kasky> x86{
        {"add eax, [esi+ecx*4]", 3},  // 03 04 8e
        {"inc ecx", 1},               // 41
        {"cmp ecx, edx", 2},          // 39 d1
        {"jl silmukka", 2},           // 7c f8
        {"add [ebx+8], eax", 3},      // 01 43 08
        {"mov [edi], eax", 2},        // 89 07
        {"push eax", 1},              // 50
        {"call tulosta", 5},          // e8 rel32
        {"ret", 1}};                  // c3
    bool sulautuu = false;
    std::println("{:<22} {:>5}  µop:t", "x86-käsky", "tavua");
    for (const Kasky& k : x86) {
        std::string s;
        for (const auto& x : mikro(k.teksti, sulautuu))
            s += (s.empty() ? "" : " + ") + x;
        std::println("{:<22} {:>5}  {}", k.teksti, k.tavut, s);
    }
    // @loppu taulu
    // @alku silmukka
    // Taulukon summan silmukka: neljä ensimmäistä x86-käskyä yllä ja
    // sama RISC-V:llä (luvun 4 osoitinversio).
    int tavut = 0, uopit = 0;
    sulautuu = false;
    for (int i = 0; i < 4; ++i) {
        tavut += x86[i].tavut;
        const auto u = mikro(x86[i].teksti, sulautuu);
        if (u[0] != "(sulautui)") uopit += static_cast<int>(u.size());
    }
    const rv::Ohjelma r = rv::koota(R"(
silmukka:
        lw   t1, 0(t2)
        addi t2, t2, 4
        add  a0, a0, t1
        blt  t2, t3, silmukka)");
    std::println("\nkierros    käskyjä tavuja µop:ja");
    std::println("x86              4 {:6} {:6}", tavut, uopit);
    std::println("RISC-V           4 {:6} {:6}", r.kuva.size(), 4);
    // @loppu silmukka
}

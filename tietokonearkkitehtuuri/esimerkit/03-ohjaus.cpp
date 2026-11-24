// Ohjausyksikkö: opcode -> ohjaussignaalit yksijaksoiselle datapolulle,
// ja monijaksoisen toteutuksen CPI todellisista käskysekoituksista.
#include <array>
#include <print>
#include <string_view>
#include <utility>

#include "yhteinen/kone.hpp"
#include "yhteinen/liukuhihna.hpp"
#include "yhteinen/ohjelmat.hpp"

// @alku signaalit
enum class A { rs1, pc, nolla };          // ALU:n A-operandi
enum class Wb { alu, muisti, pc4 };       // mitä rekisteriin kirjoitetaan
enum class Imm { ei, I, S, B, U, J };     // välittömän arvon muoto
enum class AluOp { add, funct, vertailu };  // ALU-ohjauksen karkea taso

struct Ohjaus {
    bool reg_kirj;   // tulos rekisteritiedostoon
    A a;
    bool b_imm;      // ALU:n B-operandi = välitön (muuten rs2)
    bool muisti_luku, muisti_kirj;
    Wb wb;
    bool haara, hyppy;
    Imm imm;
    AluOp alu;
};

constexpr Ohjaus ohjaus(rv::u32 opcode) {
    using enum A;
    using enum Wb;
    switch (opcode) {
    case 0x33: return {true, rs1, false, false, false, alu,
                       false, false, Imm::ei, AluOp::funct};     // R
    case 0x13: return {true, rs1, true, false, false, alu,
                       false, false, Imm::I, AluOp::funct};      // OP-IMM
    case 0x03: return {true, rs1, true, true, false, muisti,
                       false, false, Imm::I, AluOp::add};        // lw
    case 0x23: return {false, rs1, true, false, true, alu,
                       false, false, Imm::S, AluOp::add};        // sw
    case 0x63: return {false, rs1, false, false, false, alu,
                       true, false, Imm::B, AluOp::vertailu};    // beq
    case 0x37: return {true, nolla, true, false, false, alu,
                       false, false, Imm::U, AluOp::add};        // lui
    case 0x17: return {true, pc, true, false, false, alu,
                       false, false, Imm::U, AluOp::add};        // auipc
    case 0x6f: return {true, pc, true, false, false, pc4,
                       false, true, Imm::J, AluOp::add};         // jal
    case 0x67: return {true, rs1, true, false, false, pc4,
                       false, true, Imm::I, AluOp::add};         // jalr
    default:   return {};
    }
}
// @loppu signaalit

// @alku jaksot
// Monijaksoinen toteutus: jokainen käsky käyttää vain tarvitsemansa
// vaiheet. IF ja ID aina; sitten EX; lataus MEM ja WB; talletus MEM.
int jaksoja(const rv::Tapahtuma& t) {
    if (t.lataus) return 5;
    if (t.talletus || t.hyppy) return 4;
    if (t.haara) return 3;
    return 4;  // laskenta: IF ID EX WB
}
// @loppu jaksot

int main() {
    // @alku taulu
    const std::array<std::pair<std::string_view, rv::u32>, 9> luokat{{
        {"R", 0x33}, {"OP-IMM", 0x13}, {"lataus", 0x03},
        {"talletus", 0x23}, {"haara", 0x63}, {"lui", 0x37},
        {"auipc", 0x17}, {"jal", 0x6f}, {"jalr", 0x67}}};
    std::println("{:<9} rk  a  b ml mk wb ha hy imm  alu", "luokka");
    for (const auto& [nimi, op] : luokat) {
        const Ohjaus c = ohjaus(op);
        std::println("{:<9} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} {:>2} "
                     "{:>2} {:>3} {:>4}",
                     nimi, int{c.reg_kirj}, "rp0"[static_cast<int>(c.a)],
                     c.b_imm ? 'i' : 'r', int{c.muisti_luku},
                     int{c.muisti_kirj}, "amp"[static_cast<int>(c.wb)],
                     int{c.haara}, int{c.hyppy},
                     "-ISBUJ"[static_cast<int>(c.imm)],
                     c.alu == AluOp::add     ? "add"
                     : c.alu == AluOp::funct ? "f3f7"
                                             : "cmp");
    }
    // @loppu taulu
    // @alku vertailu
    // Rautalaki: aika = käskyt x CPI x jakson aika.
    // Vaiheiden viiveet (ps): IF 200, ID 100, EX 200, MEM 200, WB 100.
    constexpr double yksi_t = 800, moni_t = 200, liuku_t = 220;
    std::println("\n{:<9} {:>6} {:>10} {:>10} {:>10}", "ohjelma",
                 "käskyt", "yksi (ns)", "moni (ns)", "liuku (ns)");
    const std::array<std::pair<std::string_view, std::string_view>, 3>
        testit{{{"summa", ohjelmat::summa}, {"kupla", ohjelmat::kupla},
                {"fib", ohjelmat::fib}}};
    for (const auto& [nimi, lahde] : testit) {
        rv::Kone kone(rv::koota(lahde));
        const auto jalki = kone.aja();
        double moni = 0;
        for (const rv::Tapahtuma& t : jalki) moni += jaksoja(t);
        const rv::Tulos l = rv::simuloi(jalki, {});
        const double n = static_cast<double>(jalki.size());
        std::println("{:<9} {:>6} {:>10.0f} {:>10.0f} {:>10.0f}", nimi,
                     jalki.size(), n * yksi_t / 1000, moni * moni_t / 1000,
                     static_cast<double>(l.syklit) * liuku_t / 1000);
        std::println("{:<9} {:>6} {:>10} {:>10.2f} {:>10.2f}", "  CPI", "",
                     "1.00", moni / n, l.cpi());
    }
    // @loppu vertailu
}

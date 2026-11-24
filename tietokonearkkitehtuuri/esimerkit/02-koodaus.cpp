// Käskyjen koodaus: kootaan yksi käsky kustakin muodosta, puretaan
// konekoodi takaisin kentiksi ja tarkistetaan, että koodaus ja purku
// ovat toistensa käänteiset.
#include <print>
#include <string>

#include "yhteinen/rv32i.hpp"

int main() {
    // @alku kentat
    const char* lahde = R"(
alku:   add  a0, a1, a2
        addi t0, t0, -1
        lw   a0, 8(sp)
        sw   ra, -4(sp)
        beq  a0, zero, loppu
        lui  a5, 0x12345
        jal  ra, alku
loppu:
    )";
    const rv::Ohjelma o = rv::koota(lahde);
    using rv::Muoto;
    // Kenttä näytetään vain, jos muodossa on se.
    auto kentta = [](bool on, rv::u32 v) {
        return on ? std::to_string(v) : std::string("-");
    };
    std::println("{:<10} {:<5} {:>2} {:>3} {:>3} {:>3} {:>3} {:>10}",
                 "konekoodi", "muoto", "op", "rd", "rs1", "rs2", "f3",
                 "imm");
    for (rv::u32 pc = 0; pc < o.kuva.size(); pc += 4) {
        rv::u32 k = 0;
        for (int b = 3; b >= 0; --b) k = k << 8 | o.kuva[pc + b];
        const rv::Kentat f = rv::pura(k);
        const Muoto m = f.muoto;
        const bool rd = m != Muoto::S && m != Muoto::B;
        const bool rs1 = m != Muoto::U && m != Muoto::J;
        const bool rs2 = m == Muoto::R || m == Muoto::S || m == Muoto::B;
        std::println("{:08x}   {:<5} {:02x} {:>3} {:>3} {:>3} {:>3} {:>10}",
                     k, "RISBUJ"[static_cast<int>(m)], f.opcode,
                     kentta(rd, f.rd), kentta(rs1, f.rs1),
                     kentta(rs2, f.rs2), kentta(rs1, f.funct3),
                     m == Muoto::R ? "-" : std::to_string(f.imm));
    }
    // @loppu kentat
    // @alku takaisin
    // Kierros: koodaa siirtymä, pura se ja vertaa alkuperäiseen.
    int virheet = 0, kokeillut = 0;
    for (rv::i32 imm = -4096; imm < 4096; imm += 2, ++kokeillut)
        if (rv::pura(rv::koodaa_b(0, 10, 11, imm)).imm != imm) ++virheet;
    for (rv::i32 imm = -(1 << 20); imm < (1 << 20); imm += 2, ++kokeillut)
        if (rv::pura(rv::koodaa_j(1, imm)).imm != imm) ++virheet;
    std::println("siirtymiä kokeiltu {}, virheitä {}", kokeillut, virheet);
    // @loppu takaisin
}

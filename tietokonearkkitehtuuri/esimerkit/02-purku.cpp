// Disassembler: konekoodi takaisin luettavaksi assemblyksi.
// Pseudokäskyt (li, la, call, ret, mv) näkyvät todellisina käskyinä.
#include <print>

#include "yhteinen/ohjelmat.hpp"
#include "yhteinen/rv32i.hpp"

int main() {
    const rv::Ohjelma o = rv::koota(ohjelmat::fib);
    const rv::u32 loppu = o.nimiot.at("pieni") + 4;
    for (rv::u32 pc = 0; pc < loppu; pc += 4) {
        rv::u32 k = 0;
        for (int b = 3; b >= 0; --b) k = k << 8 | o.kuva[pc + b];
        std::println("{:04x}:  {:08x}  {}", pc, k, rv::pura_teksti(k, pc));
    }
}

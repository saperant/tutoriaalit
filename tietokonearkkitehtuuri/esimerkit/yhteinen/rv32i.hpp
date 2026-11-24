// RV32I-käskyjen koodaus ja purku sekä pieni assembler ja disassembler.
// Tukee RV32I:n kokonaislukukäskyt, M-laajennuksen mul-käskyn sekä
// muutamat CSR- ja ansakäskyt (csrrw, csrrs, ecall, mret). Tarkoitettu
// opetukseen: virheilmoitukset ovat lyhyitä ja käskyjoukko rajattu.
#pragma once
#include <array>
#include <cstdint>
#include <format>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace rv {

using u32 = std::uint32_t;
using i32 = std::int32_t;

// @alku kentat
// @alku bitit
// Bitit ylin..alin (molemmat mukaan lukien) oikealle siirrettyinä.
constexpr u32 bitit(u32 x, int ylin, int alin) {
    const int n = ylin - alin + 1;
    const u32 maski = n == 32 ? ~0u : (1u << n) - 1;
    return (x >> alin) & maski;
}

// Etumerkkilaajennus: n-bittinen kahden komplementin luku 32 bittiin.
constexpr i32 laajenna(u32 x, int n) {
    const u32 m = 1u << (n - 1);
    return static_cast<i32>((x ^ m) - m);
}
// @loppu bitit

enum class Muoto { R, I, S, B, U, J };

struct Kentat {
    Muoto muoto;
    u32 opcode, rd, funct3, rs1, rs2, funct7;
    i32 imm;  // välitön arvo valmiiksi koottuna ja laajennettuna
};

constexpr Muoto muoto(u32 opcode) {
    switch (opcode) {
    case 0x33: return Muoto::R;                       // OP
    case 0x23: return Muoto::S;                       // STORE
    case 0x63: return Muoto::B;                       // BRANCH
    case 0x37: case 0x17: return Muoto::U;            // LUI, AUIPC
    case 0x6f: return Muoto::J;                       // JAL
    default: return Muoto::I;  // OP-IMM, LOAD, JALR, SYSTEM
    }
}

constexpr Kentat pura(u32 k) {
    Kentat f{muoto(bitit(k, 6, 0)), bitit(k, 6, 0), bitit(k, 11, 7),
             bitit(k, 14, 12), bitit(k, 19, 15), bitit(k, 24, 20),
             bitit(k, 31, 25), 0};
    switch (f.muoto) {
    case Muoto::R: break;
    case Muoto::I: f.imm = laajenna(bitit(k, 31, 20), 12); break;
    case Muoto::S:
        f.imm = laajenna(bitit(k, 31, 25) << 5 | bitit(k, 11, 7), 12);
        break;
    case Muoto::B:
        f.imm = laajenna(bitit(k, 31, 31) << 12 | bitit(k, 7, 7) << 11 |
                         bitit(k, 30, 25) << 5 | bitit(k, 11, 8) << 1, 13);
        break;
    case Muoto::U: f.imm = static_cast<i32>(k & 0xfffff000u); break;
    case Muoto::J:
        f.imm = laajenna(bitit(k, 31, 31) << 20 | bitit(k, 19, 12) << 12 |
                         bitit(k, 20, 20) << 11 | bitit(k, 30, 21) << 1,
                         21);
        break;
    }
    return f;
}
// @loppu kentat

// @alku koodaus
constexpr u32 koodaa_r(u32 op, u32 rd, u32 f3, u32 rs1, u32 rs2, u32 f7) {
    return f7 << 25 | rs2 << 20 | rs1 << 15 | f3 << 12 | rd << 7 | op;
}
constexpr u32 koodaa_i(u32 op, u32 rd, u32 f3, u32 rs1, i32 imm) {
    return (static_cast<u32>(imm) & 0xfff) << 20 | rs1 << 15 | f3 << 12 |
           rd << 7 | op;
}
constexpr u32 koodaa_s(u32 op, u32 f3, u32 rs1, u32 rs2, i32 imm) {
    const u32 i = static_cast<u32>(imm);
    return bitit(i, 11, 5) << 25 | rs2 << 20 | rs1 << 15 | f3 << 12 |
           bitit(i, 4, 0) << 7 | op;
}
constexpr u32 koodaa_b(u32 f3, u32 rs1, u32 rs2, i32 imm) {
    const u32 i = static_cast<u32>(imm);
    return bitit(i, 12, 12) << 31 | bitit(i, 10, 5) << 25 | rs2 << 20 |
           rs1 << 15 | f3 << 12 | bitit(i, 4, 1) << 8 |
           bitit(i, 11, 11) << 7 | 0x63;
}
constexpr u32 koodaa_u(u32 op, u32 rd, u32 ylaosa) {
    return (ylaosa & 0xfffff000u) | rd << 7 | op;
}
constexpr u32 koodaa_j(u32 rd, i32 imm) {
    const u32 i = static_cast<u32>(imm);
    return bitit(i, 20, 20) << 31 | bitit(i, 10, 1) << 21 |
           bitit(i, 11, 11) << 20 | bitit(i, 19, 12) << 12 | rd << 7 |
           0x6f;
}
// @loppu koodaus

inline const std::array<std::string_view, 32> abi_nimet{
    "zero", "ra", "sp", "gp", "tp", "t0", "t1", "t2",
    "s0",   "s1", "a0", "a1", "a2", "a3", "a4", "a5",
    "a6",   "a7", "s2", "s3", "s4", "s5", "s6", "s7",
    "s8",   "s9", "s10", "s11", "t3", "t4", "t5", "t6"};

// Käskyn nimi purettujen kenttien perusteella ("?" = tuntematon).
inline std::string nimi(const Kentat& f) {
    static const std::map<u32, std::string> alu{
        {0, "add"}, {1, "sll"}, {2, "slt"}, {3, "sltu"},
        {4, "xor"}, {5, "srl"}, {6, "or"},  {7, "and"}};
    static const std::array<std::string, 8> haara{
        "beq", "bne", "?", "?", "blt", "bge", "bltu", "bgeu"};
    static const std::array<std::string, 8> lataus{
        "lb", "lh", "lw", "?", "lbu", "lhu", "?", "?"};
    static const std::array<std::string, 8> talletus{
        "sb", "sh", "sw", "?", "?", "?", "?", "?"};
    switch (f.opcode) {
    case 0x33:
        if (f.funct7 == 1 && f.funct3 == 0) return "mul";
        if (f.funct7 == 0x20)
            return f.funct3 == 0 ? "sub" : f.funct3 == 5 ? "sra" : "?";
        return alu.at(f.funct3);
    case 0x13:
        if (f.funct3 == 5 && f.funct7 == 0x20) return "srai";
        if (f.funct3 == 0) return "addi";
        return alu.at(f.funct3) + "i";
    case 0x03: return lataus[f.funct3];
    case 0x23: return talletus[f.funct3];
    case 0x63: return haara[f.funct3];
    case 0x37: return "lui";
    case 0x17: return "auipc";
    case 0x6f: return "jal";
    case 0x67: return "jalr";
    case 0x73:
        if (f.funct3 == 1) return "csrrw";
        if (f.funct3 == 2) return "csrrs";
        if (f.imm == 0) return "ecall";
        if (f.imm == 0x302) return "mret";
        return "?";
    default: return "?";
    }
}

// Disassembler: yksi käsky tekstiksi (osoite tarvitaan hyppykohteisiin).
inline std::string pura_teksti(u32 k, u32 pc = 0) {
    const Kentat f = pura(k);
    const std::string n = nimi(f);
    auto r = [](u32 i) { return std::string(abi_nimet[i]); };
    switch (f.muoto) {
    case Muoto::R:
        return std::format("{} {}, {}, {}", n, r(f.rd), r(f.rs1), r(f.rs2));
    case Muoto::S:
        return std::format("{} {}, {}({})", n, r(f.rs2), f.imm, r(f.rs1));
    case Muoto::B:
        return std::format("{} {}, {}, 0x{:x}", n, r(f.rs1), r(f.rs2),
                           pc + static_cast<u32>(f.imm));
    case Muoto::U:
        return std::format("{} {}, 0x{:x}", n, r(f.rd),
                           static_cast<u32>(f.imm) >> 12);
    case Muoto::J:
        return std::format("{} {}, 0x{:x}", n, r(f.rd),
                           pc + static_cast<u32>(f.imm));
    case Muoto::I:
        if (f.opcode == 0x03 || f.opcode == 0x67)
            return std::format("{} {}, {}({})", n, r(f.rd), f.imm,
                               r(f.rs1));
        if (f.opcode == 0x73)
            return n == "ecall" || n == "mret"
                       ? n
                       : std::format("{} {}, 0x{:x}, {}", n, r(f.rd),
                                     static_cast<u32>(f.imm) & 0xfff,
                                     r(f.rs1));
        if (n == "slli" || n == "srli" || n == "srai")
            return std::format("{} {}, {}, {}", n, r(f.rd), r(f.rs1),
                               f.imm & 0x1f);
        return std::format("{} {}, {}, {}", n, r(f.rd), r(f.rs1), f.imm);
    }
    return "?";
}

// ---------------------------------------------------------------------
// Assembler. Kaksivaiheinen: ensimmäinen kierros laskee nimiöiden
// osoitteet, toinen koodaa. Tukee nimiöitä, kommentteja (#),
// direktiivejä .word N ja .zero N sekä pseudokäskyjä li, la, mv, j,
// call, ret, nop, beqz, bnez, bgt, ble, csrr ja csrw.

struct Ohjelma {
    std::vector<std::uint8_t> kuva;        // konekoodi ja data
    std::map<std::string, u32> nimiot;     // nimiö -> osoite
};

namespace yksityiskohdat {

inline std::vector<std::string> pilko(std::string_view rivi) {
    std::vector<std::string> osat;
    std::string nyt;
    for (char c : rivi) {
        if (c == ',' || c == ' ' || c == '\t') {
            if (!nyt.empty()) osat.push_back(nyt), nyt.clear();
        } else {
            nyt += c;
        }
    }
    if (!nyt.empty()) osat.push_back(nyt);
    return osat;
}

inline u32 rekisteri(const std::string& s) {
    if (s.size() > 1 && s[0] == 'x') return static_cast<u32>(std::stoi(
        s.substr(1)));
    if (s == "fp") return 8;
    for (u32 i = 0; i < 32; ++i)
        if (abi_nimet[i] == s) return i;
    throw std::runtime_error("tuntematon rekisteri: " + s);
}

inline const std::map<std::string, u32> csr_nimet{
    {"mstatus", 0x300}, {"mie", 0x304}, {"mtvec", 0x305},
    {"mepc", 0x341},    {"mcause", 0x342}, {"mtval", 0x343},
    {"mip", 0x344}};

}  // namespace yksityiskohdat

inline Ohjelma koota(std::string_view lahde, u32 alku = 0) {
    using namespace yksityiskohdat;
    // Rivit ilman kommentteja; nimiöt omiksi riveikseen.
    std::vector<std::vector<std::string>> rivit;
    std::istringstream sisaan{std::string(lahde)};
    for (std::string rivi; std::getline(sisaan, rivi);) {
        if (auto p = rivi.find('#'); p != std::string::npos)
            rivi.resize(p);
        auto osat = pilko(rivi);
        while (!osat.empty() && osat[0].back() == ':') {
            rivit.push_back({osat[0]});
            osat.erase(osat.begin());
        }
        if (!osat.empty()) rivit.push_back(osat);
    }
    auto koko = [](const std::vector<std::string>& o) -> u32 {
        if (o[0] == ".word") return 4 * static_cast<u32>(o.size() - 1);
        if (o[0] == ".zero") return static_cast<u32>(std::stoul(o[1]));
        if (o[0] == "la" || o[0] == "call") return 8;
        if (o[0] == "li") {
            const long long v = std::stoll(o[2], nullptr, 0);
            return v >= -2048 && v < 2048 ? 4 : 8;
        }
        return 4;
    };
    Ohjelma tulos;
    u32 osoite = alku;
    for (const auto& o : rivit) {
        if (o[0].back() == ':')
            tulos.nimiot[o[0].substr(0, o[0].size() - 1)] = osoite;
        else
            osoite += koko(o);
    }
    auto arvo = [&](const std::string& s) -> i32 {
        if (auto it = tulos.nimiot.find(s); it != tulos.nimiot.end())
            return static_cast<i32>(it->second);
        return static_cast<i32>(std::stoll(s, nullptr, 0));
    };
    auto lisaa = [&](u32 k) {
        for (int i = 0; i < 4; ++i)
            tulos.kuva.push_back(static_cast<std::uint8_t>(k >> (8 * i)));
    };
    // Muistiosoite muodossa "siirto(rekisteri)".
    auto muisti = [&](const std::string& s) {
        const auto sulku = s.find('(');
        const i32 siirto = sulku == 0 ? 0 : arvo(s.substr(0, sulku));
        return std::pair{siirto,
                         rekisteri(s.substr(sulku + 1,
                                            s.size() - sulku - 2))};
    };
    // Suuri vakio kahdeksi käskyksi: lui + addi (addi laajentaa
    // etumerkin, joten yläosaan lisätään 0x800).
    auto lui_addi = [&](u32 rd, i32 v, bool pc_suht, u32 pc) {
        const u32 x = static_cast<u32>(v) - (pc_suht ? pc : 0);
        lisaa(koodaa_u(pc_suht ? 0x17 : 0x37, rd, x + 0x800));
        lisaa(koodaa_i(0x13, rd, 0, rd, laajenna(x & 0xfff, 12)));
    };
    static const std::map<std::string, std::pair<u32, u32>> r_kaskyt{
        {"add", {0, 0}},  {"sub", {0, 0x20}}, {"sll", {1, 0}},
        {"slt", {2, 0}},  {"sltu", {3, 0}},   {"xor", {4, 0}},
        {"srl", {5, 0}},  {"sra", {5, 0x20}}, {"or", {6, 0}},
        {"and", {7, 0}},  {"mul", {0, 1}}};
    static const std::map<std::string, u32> i_kaskyt{
        {"addi", 0}, {"slti", 2}, {"sltiu", 3}, {"xori", 4},
        {"ori", 6},  {"andi", 7}};
    static const std::map<std::string, std::pair<u32, u32>> siirrot{
        {"slli", {1, 0}}, {"srli", {5, 0}}, {"srai", {5, 0x20}}};
    static const std::map<std::string, u32> lataukset{
        {"lb", 0}, {"lh", 1}, {"lw", 2}, {"lbu", 4}, {"lhu", 5}};
    static const std::map<std::string, u32> talletukset{
        {"sb", 0}, {"sh", 1}, {"sw", 2}};
    static const std::map<std::string, u32> haarat{
        {"beq", 0}, {"bne", 1}, {"blt", 4}, {"bge", 5},
        {"bltu", 6}, {"bgeu", 7}};
    osoite = alku;
    for (const auto& o : rivit) {
        const std::string& m = o[0];
        if (m.back() == ':') continue;
        const u32 pc = osoite;
        osoite += koko(o);
        auto suht = [&](const std::string& s) {
            return arvo(s) - static_cast<i32>(pc);
        };
        if (m == ".word") {
            for (std::size_t i = 1; i < o.size(); ++i)
                lisaa(static_cast<u32>(arvo(o[i])));
        } else if (m == ".zero") {
            tulos.kuva.resize(tulos.kuva.size() + std::stoul(o[1]), 0);
        } else if (auto r = r_kaskyt.find(m); r != r_kaskyt.end()) {
            lisaa(koodaa_r(0x33, rekisteri(o[1]), r->second.first,
                           rekisteri(o[2]), rekisteri(o[3]),
                           r->second.second));
        } else if (auto i = i_kaskyt.find(m); i != i_kaskyt.end()) {
            lisaa(koodaa_i(0x13, rekisteri(o[1]), i->second,
                           rekisteri(o[2]), arvo(o[3])));
        } else if (auto s = siirrot.find(m); s != siirrot.end()) {
            lisaa(koodaa_i(0x13, rekisteri(o[1]), s->second.first,
                           rekisteri(o[2]),
                           arvo(o[3]) | static_cast<i32>(
                                            s->second.second << 5)));
        } else if (auto l = lataukset.find(m); l != lataukset.end()) {
            auto [siirto, rs1] = muisti(o[2]);
            lisaa(koodaa_i(0x03, rekisteri(o[1]), l->second, rs1, siirto));
        } else if (auto t = talletukset.find(m); t != talletukset.end()) {
            auto [siirto, rs1] = muisti(o[2]);
            lisaa(koodaa_s(0x23, t->second, rs1, rekisteri(o[1]), siirto));
        } else if (auto h = haarat.find(m); h != haarat.end()) {
            lisaa(koodaa_b(h->second, rekisteri(o[1]), rekisteri(o[2]),
                           suht(o[3])));
        } else if (m == "beqz" || m == "bnez") {
            lisaa(koodaa_b(m == "beqz" ? 0 : 1, rekisteri(o[1]), 0,
                           suht(o[2])));
        } else if (m == "bgt" || m == "ble") {  // operandit vaihdettuina
            lisaa(koodaa_b(m == "bgt" ? 4 : 5, rekisteri(o[2]),
                           rekisteri(o[1]), suht(o[3])));
        } else if (m == "jal") {
            const bool kaksi = o.size() == 3;
            lisaa(koodaa_j(kaksi ? rekisteri(o[1]) : 1,
                           suht(o[kaksi ? 2 : 1])));
        } else if (m == "j") {
            lisaa(koodaa_j(0, suht(o[1])));
        } else if (m == "jalr") {
            if (o.size() == 2) {
                lisaa(koodaa_i(0x67, 1, 0, rekisteri(o[1]), 0));
            } else {
                auto [siirto, rs1] = muisti(o[2]);
                lisaa(koodaa_i(0x67, rekisteri(o[1]), 0, rs1, siirto));
            }
        } else if (m == "ret") {
            lisaa(koodaa_i(0x67, 0, 0, 1, 0));
        } else if (m == "call") {  // auipc ra + jalr ra
            const u32 x = static_cast<u32>(arvo(o[1])) - pc;
            lisaa(koodaa_u(0x17, 1, x + 0x800));
            lisaa(koodaa_i(0x67, 1, 0, 1, laajenna(x & 0xfff, 12)));
        } else if (m == "lui" || m == "auipc") {
            lisaa(koodaa_u(m == "lui" ? 0x37 : 0x17, rekisteri(o[1]),
                           static_cast<u32>(arvo(o[2])) << 12));
        } else if (m == "li") {
            const i32 v = arvo(o[2]);
            if (koko(o) == 4)
                lisaa(koodaa_i(0x13, rekisteri(o[1]), 0, 0, v));
            else
                lui_addi(rekisteri(o[1]), v, false, pc);
        } else if (m == "la") {
            lui_addi(rekisteri(o[1]), arvo(o[2]), true, pc);
        } else if (m == "mv") {
            lisaa(koodaa_i(0x13, rekisteri(o[1]), 0, rekisteri(o[2]), 0));
        } else if (m == "nop") {
            lisaa(koodaa_i(0x13, 0, 0, 0, 0));
        } else if (m == "ecall") {
            lisaa(0x00000073);
        } else if (m == "mret") {
            lisaa(0x30200073);
        } else if (m == "csrw" || m == "csrr") {
            const u32 csr = csr_nimet.at(m == "csrw" ? o[1] : o[2]);
            const bool w = m == "csrw";
            lisaa(koodaa_i(0x73, w ? 0 : rekisteri(o[1]), w ? 1 : 2,
                           w ? rekisteri(o[2]) : 0,
                           static_cast<i32>(csr)));
        } else {
            throw std::runtime_error("tuntematon käsky: " + m);
        }
    }
    return tulos;
}

}  // namespace rv

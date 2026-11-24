#include "koodigen.hpp"

#include <ostream>
#include <string>

namespace kide {

namespace {

class Generaattori {
public:
    Generaattori(const IrFunktio& f, const Varaus& v, std::ostream& u)
        : f_(f), v_(v), u_(u) {}
    void funktio();

private:
    void kasky(const std::string& nimi, const std::string& operandit = "") {
        u_ << "    " << nimi;
        if (!operandit.empty()) {
            u_ << std::string(nimi.size() < 8 ? 8 - nimi.size() : 1, ' ')
               << operandit;
        }
        u_ << '\n';
    }
    std::string nimio(int lohko) const {
        return ".L" + f_.nimi + "_" + std::to_string(lohko);
    }
    std::string muisti(int siirto);
    std::string lue(Vreg r, const char* apu);
    std::string kohde(Vreg r) const;
    void kirjoita(Vreg r, const std::string& reg);
    void siirra(const std::string& kohde, const std::string& lahde) {
        if (kohde != lahde) kasky("mv", kohde + ", " + lahde);
    }
    void prologi();
    void epilogi();
    void ir_kasky(const Kasky& k, int lohko);

    const IrFunktio& f_;
    const Varaus& v_;
    std::ostream& u_;
};

// @alku kehys
// Pinokehys, s0 osoittaa kehyksen yläreunaan (sp funktioon tultaessa):
//
//     -8(s0)    paluuosoite ra
//    -16(s0)    kutsujan s0
//    -24(s0)    tallennetut s-rekisterit, 8 tavua kukin
//      ...      pinopaikat, 8 tavua kukin
//
// sp pidetään 16:lla jaollisena, kuten RISC-V:n psABI vaatii.
int tallennusalue(const Varaus& v) {
    return 16 + 8 * static_cast<int>(v.kaytetyt.size());
}

int kehyksen_koko(const Varaus& v) {
    int koko = tallennusalue(v) + 8 * v.pinopaikkoja;
    return (koko + 15) / 16 * 16;
}

// Osoite s0-suhteellisena. Välitön siirtymä on 12-bittinen
// (-2048..2047); suuremmille lasketaan osoite apurekisteriin t6.
std::string Generaattori::muisti(int siirto) {
    if (siirto >= -2048) return std::to_string(siirto) + "(s0)";
    kasky("li", "t6, " + std::to_string(siirto));
    kasky("add", "t6, s0, t6");
    return "0(t6)";
}
// @loppu kehys

int siirto(const Varaus& v, Vreg r) {
    return -tallennusalue(v) - 8 - 8 * v.paikat[r].pinopaikka;
}

// @alku operandit
// Operandin rekisteri: varattu s-rekisteri tai pinosta ladattu apu.
std::string Generaattori::lue(Vreg r, const char* apu) {
    const Paikka& p = v_.paikat[r];
    if (p.rekisteri > 0) return "s" + std::to_string(p.rekisteri);
    kasky("ld", std::string(apu) + ", " + muisti(siirto(v_, r)));
    return apu;
}

// Tuloksen rekisteri; pinoon menevä tulos lasketaan ensin t0:aan.
std::string Generaattori::kohde(Vreg r) const {
    const Paikka& p = v_.paikat[r];
    return p.rekisteri > 0 ? "s" + std::to_string(p.rekisteri) : "t0";
}

void Generaattori::kirjoita(Vreg r, const std::string& reg) {
    if (v_.paikat[r].rekisteri > 0) return;
    kasky("sd", reg + ", " + muisti(siirto(v_, r)));
}
// @loppu operandit

// @alku prologi
void Generaattori::prologi() {
    u_ << "    .globl  k_" << f_.nimi << "\n"
       << "    .type   k_" << f_.nimi << ", @function\n"
       << "k_" << f_.nimi << ":\n";
    kasky("addi", "sp, sp, -16");
    kasky("sd", "ra, 8(sp)");
    kasky("sd", "s0, 0(sp)");
    kasky("addi", "s0, sp, 16");
    int loput = kehyksen_koko(v_) - 16;
    if (loput > 0 && loput <= 2048) {
        kasky("addi", "sp, sp, " + std::to_string(-loput));
    } else if (loput > 0) {
        kasky("li", "t0, " + std::to_string(loput));
        kasky("sub", "sp, sp, t0");
    }
    for (std::size_t i = 0; i < v_.kaytetyt.size(); ++i) {
        kasky("sd", "s" + std::to_string(v_.kaytetyt[i]) + ", "
                        + std::to_string(-24 - 8 * static_cast<int>(i))
                        + "(s0)");
    }
    // Parametrit saapuvat rekistereissä a0-a7.
    for (Vreg p = 0; p < f_.parametreja; ++p) {
        if (v_.paikat[p].rekisteri < 0 && v_.paikat[p].pinopaikka < 0) {
            continue;                    // parametria ei käytetä
        }
        std::string a = "a" + std::to_string(p);
        if (v_.paikat[p].rekisteri > 0) siirra(kohde(p), a);
        kirjoita(p, a);
    }
}
// @loppu prologi

void Generaattori::epilogi() {
    u_ << ".L" << f_.nimi << "_loppu:\n";
    for (std::size_t i = 0; i < v_.kaytetyt.size(); ++i) {
        kasky("ld", "s" + std::to_string(v_.kaytetyt[i]) + ", "
                        + std::to_string(-24 - 8 * static_cast<int>(i))
                        + "(s0)");
    }
    kasky("addi", "sp, s0, -16");
    kasky("ld", "ra, 8(sp)");
    kasky("ld", "s0, 0(sp)");
    kasky("addi", "sp, sp, 16");
    kasky("ret");
}

const char* kaskyn_nimi(Op op) {
    switch (op) {
    case Op::Add: return "add";
    case Op::Sub: return "sub";
    case Op::Mul: return "mul";
    case Op::Div: return "div";
    case Op::Rem: return "rem";
    case Op::Lt: return "slt";
    default: return nullptr;
    }
}

void Generaattori::ir_kasky(const Kasky& k, int lohko) {
    // Hyppyä ei tarvita, jos kohde on heti seuraava lohko.
    auto putoaa = [&](int kohde) { return kohde == lohko + 1; };
    switch (k.op) {
    case Op::Vakio: {
        std::string d = kohde(k.kohde);
        kasky("li", d + ", " + std::to_string(k.vakio));
        kirjoita(k.kohde, d);
        return;
    }
    case Op::Kopio: {
        std::string a = lue(k.lahteet[0], "t1");
        std::string d = kohde(k.kohde);
        siirra(d, a);
        kirjoita(k.kohde, d);
        return;
    }
    case Op::Neg:
    case Op::Not: {
        std::string a = lue(k.lahteet[0], "t1");
        std::string d = kohde(k.kohde);
        if (k.op == Op::Neg) {
            kasky("neg", d + ", " + a);
        } else {
            kasky("xori", d + ", " + a + ", 1");     // totuusarvo on 0 tai 1
        }
        kirjoita(k.kohde, d);
        return;
    }
    case Op::Kutsu:
    case Op::Tulosta: {
        // Argumentit a-rekistereihin. Varatut arvot ovat s-rekistereissä
        // tai pinossa, joten siirrot eivät voi ylikirjoittaa toisiaan.
        for (std::size_t i = 0; i < k.lahteet.size(); ++i) {
            std::string a = "a" + std::to_string(i);
            const Paikka& p = v_.paikat[k.lahteet[i]];
            if (p.rekisteri > 0) {
                siirra(a, "s" + std::to_string(p.rekisteri));
            } else {
                kasky("ld", a + ", " + muisti(siirto(v_, k.lahteet[i])));
            }
        }
        kasky("call", k.op == Op::Kutsu ? "k_" + k.funktio : "kide_tulosta");
        if (k.op == Op::Kutsu) {
            std::string d = kohde(k.kohde);
            siirra(d, "a0");
            kirjoita(k.kohde, d);
        }
        return;
    }
    case Op::Hyppy:
        if (!putoaa(k.lohkot[0])) kasky("j", nimio(k.lohkot[0]));
        return;
    // @alku haara
    case Op::Haara: {
        std::string c = lue(k.lahteet[0], "t0");
        if (putoaa(k.lohkot[1])) {
            kasky("bnez", c + ", " + nimio(k.lohkot[0]));
        } else if (putoaa(k.lohkot[0])) {
            kasky("beqz", c + ", " + nimio(k.lohkot[1]));
        } else {
            kasky("bnez", c + ", " + nimio(k.lohkot[0]));
            kasky("j", nimio(k.lohkot[1]));
        }
        return;
    }
    // @loppu haara
    case Op::Palauta:
        siirra("a0", lue(k.lahteet[0], "a0"));
        if (lohko + 1 < static_cast<int>(f_.lohkot.size())) {
            kasky("j", ".L" + f_.nimi + "_loppu");   // epilogiin
        }
        return;
    default:
        break;
    }
// @alku vertailut
    // Binäärioperaatiot. Vertailuista vain slt on käsky; muut johdetaan.
    std::string a = lue(k.lahteet[0], "t1");
    std::string b = lue(k.lahteet[1], "t2");
    std::string d = kohde(k.kohde);
    if (const char* nimi = kaskyn_nimi(k.op)) {
        kasky(nimi, d + ", " + a + ", " + b);
    } else if (k.op == Op::Gt) {                  // a > b  <=>  b < a
        kasky("slt", d + ", " + b + ", " + a);
    } else if (k.op == Op::Le) {                  // a <= b <=> !(b < a)
#ifndef KIDE_VIKA
        kasky("slt", d + ", " + b + ", " + a);
        kasky("xori", d + ", " + d + ", 1");
#else
        kasky("slt", d + ", " + a + ", " + b);    // väärin, kun a == b
#endif
    } else if (k.op == Op::Ge) {                  // a >= b <=> !(a < b)
        kasky("slt", d + ", " + a + ", " + b);
        kasky("xori", d + ", " + d + ", 1");
    } else {                                      // a == b <=> a - b == 0
        kasky("sub", d + ", " + a + ", " + b);
        kasky(k.op == Op::Eq ? "seqz" : "snez", d + ", " + d);
    }
    kirjoita(k.kohde, d);
}
// @loppu vertailut

void Generaattori::funktio() {
    prologi();
    for (std::size_t b = 0; b < f_.lohkot.size(); ++b) {
        u_ << nimio(static_cast<int>(b)) << ":\n";
        for (const Kasky& k : f_.lohkot[b].kaskyt) {
            ir_kasky(k, static_cast<int>(b));
        }
    }
    epilogi();
    u_ << "    .size   k_" << f_.nimi << ", .-k_" << f_.nimi << "\n";
}

}  // namespace

void generoi(const IrFunktio& f, const Varaus& v, std::ostream& u) {
    Generaattori(f, v, u).funktio();
}

}  // namespace kide

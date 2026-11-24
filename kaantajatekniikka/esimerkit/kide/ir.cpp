#include "ir.hpp"

#include <ostream>

namespace kide {

bool paattava(Op op) {
    return op == Op::Hyppy || op == Op::Haara || op == Op::Palauta;
}

bool puhdas(Op op) {
    return !paattava(op) && op != Op::Kutsu && op != Op::Tulosta;
}

void laske_reunat(IrFunktio& f) {
    for (auto& b : f.lohkot) {
        b.edeltajat.clear();
        b.seuraajat.clear();
    }
    for (int i = 0; i < static_cast<int>(f.lohkot.size()); ++i) {
        const Kasky& viim = f.lohkot[i].kaskyt.back();
        if (viim.op == Op::Palauta) continue;
        for (int s : viim.lohkot) {
            f.lohkot[i].seuraajat.push_back(s);
            f.lohkot[s].edeltajat.push_back(i);
        }
    }
}

std::string rekisteri(const IrFunktio& f, Vreg r) {
    if (r < 0) return "undef";
    return f.nimet[r];
}

namespace {

const char* nimi(Op op) {
    switch (op) {
    case Op::Neg: return "neg";
    case Op::Not: return "not";
    case Op::Add: return "add";
    case Op::Sub: return "sub";
    case Op::Mul: return "mul";
    case Op::Div: return "div";
    case Op::Rem: return "rem";
    case Op::Eq: return "eq";
    case Op::Ne: return "ne";
    case Op::Lt: return "lt";
    case Op::Le: return "le";
    case Op::Gt: return "gt";
    case Op::Ge: return "ge";
    default: return "?";
    }
}

}  // namespace

void tulosta_ir(const IrFunktio& f, std::ostream& u) {
    auto r = [&](Vreg v) { return rekisteri(f, v); };
    u << "fn " << f.nimi << '(';
    for (int i = 0; i < f.parametreja; ++i) u << (i ? ", " : "") << r(i);
    u << ")\n";
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        u << "L" << b << ':';
        if (!f.lohkot[b].edeltajat.empty()) {
            u << "                      ; edeltäjät:";
            for (int e : f.lohkot[b].edeltajat) u << " L" << e;
        }
        u << '\n';
        for (const Kasky& k : f.lohkot[b].kaskyt) {
            u << "    ";
            if (k.kohde >= 0) u << r(k.kohde) << " = ";
            switch (k.op) {
            case Op::Vakio: u << k.vakio; break;
            case Op::Kopio: u << r(k.lahteet[0]); break;
            case Op::Kutsu:
                u << "call " << k.funktio << '(';
                for (std::size_t i = 0; i < k.lahteet.size(); ++i) {
                    u << (i ? ", " : "") << r(k.lahteet[i]);
                }
                u << ')';
                break;
            case Op::Tulosta: u << "print " << r(k.lahteet[0]); break;
            case Op::Phi:
                u << "phi";
                for (std::size_t i = 0; i < k.lahteet.size(); ++i) {
                    u << (i ? ", " : " ") << '[' << r(k.lahteet[i])
                      << ", L" << k.lohkot[i] << ']';
                }
                break;
            case Op::Hyppy: u << "jmp L" << k.lohkot[0]; break;
            case Op::Haara:
                u << "br " << r(k.lahteet[0]) << ", L" << k.lohkot[0]
                  << ", L" << k.lohkot[1];
                break;
            case Op::Palauta: u << "ret " << r(k.lahteet[0]); break;
            default:
                u << nimi(k.op);
                for (std::size_t i = 0; i < k.lahteet.size(); ++i) {
                    u << (i ? ", " : " ") << r(k.lahteet[i]);
                }
            }
            u << '\n';
        }
    }
}

void tulosta_ir(const IrOhjelma& o, std::ostream& u) {
    for (std::size_t i = 0; i < o.funktiot.size(); ++i) {
        if (i > 0) u << '\n';
        tulosta_ir(o.funktiot[i], u);
    }
}

}  // namespace kide

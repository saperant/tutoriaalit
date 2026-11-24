#include "ast.hpp"

#include <ostream>

namespace kide {

std::string nimi(Tyyppi t) {
    switch (t) {
    case Tyyppi::Int: return "int";
    case Tyyppi::Bool: return "bool";
    case Tyyppi::Tuntematon: break;
    }
    return "?";
}

namespace {

// Operaattorin teksti ilman lainausmerkkejä.
std::string op(Laji laji) {
    std::string k = kuvaus(laji);
    return k.substr(1, k.size() - 2);
}

// @alku tulosta
void lauseke(const Lauseke& l, std::ostream& u) {
    std::visit(Kaikki{
        [&](const Luku& x) { u << x.arvo; },
        [&](const Totuus& x) { u << (x.arvo ? "true" : "false"); },
        [&](const Nimi& x) { u << x.nimi; },
        [&](const Unaari& x) {
            u << '(' << op(x.op) << ' ';
            lauseke(*x.a, u);
            u << ')';
        },
        [&](const Binaari& x) {
            u << '(' << op(x.op) << ' ';
            lauseke(*x.vasen, u);
            u << ' ';
            lauseke(*x.oikea, u);
            u << ')';
        },
        [&](const Kutsu& x) {
            u << '(' << x.funktio;
            for (const auto& a : x.argumentit) {
                u << ' ';
                lauseke(*a, u);
            }
            u << ')';
        },
    }, l.v);
}
// @loppu tulosta

void lauseet(const Lauseet& ls, int syvyys, std::ostream& u);

void lause(const Lause& l, int syvyys, std::ostream& u) {
    u << std::string(2 * syvyys, ' ');
    std::visit(Kaikki{
        [&](const Esittely& x) {
            u << "(var " << x.nimi << ' ';
            lauseke(*x.arvo, u);
            u << ')';
        },
        [&](const Sijoitus& x) {
            u << "(= " << x.nimi << ' ';
            lauseke(*x.arvo, u);
            u << ')';
        },
        [&](const Jos& x) {
            u << "(if ";
            lauseke(*x.ehto, u);
            lauseet(x.tosi, syvyys + 1, u);
            if (!x.epatosi.empty()) {
                u << '\n' << std::string(2 * syvyys + 1, ' ') << "else";
                lauseet(x.epatosi, syvyys + 1, u);
            }
            u << ')';
        },
        [&](const Kun& x) {
            u << "(while ";
            lauseke(*x.ehto, u);
            lauseet(x.runko, syvyys + 1, u);
            u << ')';
        },
        [&](const Palauta& x) {
            u << "(return ";
            lauseke(*x.arvo, u);
            u << ')';
        },
        [&](const Tulosta& x) {
            u << "(print ";
            lauseke(*x.arvo, u);
            u << ')';
        },
        [&](const LausekeLause& x) { lauseke(*x.lauseke, u); },
        [&](const Lohko& x) {
            u << "(block";
            lauseet(x.lauseet, syvyys + 1, u);
            u << ')';
        },
    }, l.v);
}

void lauseet(const Lauseet& ls, int syvyys, std::ostream& u) {
    for (const auto& l : ls) {
        u << '\n';
        lause(*l, syvyys, u);
    }
}

}  // namespace

void tulosta_ast(const Ohjelma& ohjelma, std::ostream& u) {
    for (const auto& f : ohjelma.funktiot) {
        u << "(fn " << f.nimi << " (";
        for (std::size_t i = 0; i < f.parametrit.size(); ++i) {
            if (i > 0) u << ' ';
            u << f.parametrit[i].nimi << ':' << nimi(f.parametrit[i].tyyppi);
        }
        u << ") " << nimi(f.paluutyyppi);
        lauseet(f.runko, 1, u);
        u << ")\n";
    }
}

}  // namespace kide

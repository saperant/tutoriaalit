#include "irluku.hpp"

#include <cctype>
#include <istream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

namespace kide {

namespace {

const std::map<std::string, Op> kOperaatiot = {
    {"neg", Op::Neg}, {"not", Op::Not}, {"add", Op::Add}, {"sub", Op::Sub},
    {"mul", Op::Mul}, {"div", Op::Div}, {"rem", Op::Rem}, {"eq", Op::Eq},
    {"ne", Op::Ne},   {"lt", Op::Lt},   {"le", Op::Le},   {"gt", Op::Gt},
    {"ge", Op::Ge},
};

// Rivi sanoiksi: kommentti (; ...) pois ja välimerkit erottimiksi.
std::vector<std::string> sanat(std::string rivi) {
    rivi = rivi.substr(0, rivi.find(';'));
    for (char& c : rivi) {
        if (c == ',' || c == '[' || c == ']' || c == '(' || c == ')') c = ' ';
    }
    std::istringstream virta(rivi);
    std::vector<std::string> tulos;
    for (std::string s; virta >> s;) tulos.push_back(s);
    return tulos;
}

bool on_luku(const std::string& s) {
    return std::isdigit(static_cast<unsigned char>(s[0]))
           || (s[0] == '-' && s.size() > 1);
}

// @alku lukija
class Lukija {
public:
    explicit Lukija(IrFunktio& f) : f_(f) {}
    void kasky(const std::vector<std::string>& s);
    Vreg reg(const std::string& nimi) {
        if (nimi == "undef") return -1;
        auto [paikka, uusi] = numerot_.try_emplace(
            nimi, static_cast<Vreg>(f_.nimet.size()));
        if (uusi) f_.nimet.push_back(nimi);
        return paikka->second;
    }
    static int lohko(const std::string& nimi) {
        if (nimi.size() < 2 || nimi[0] != 'L') {
            throw std::runtime_error("odotettiin lohkoa, saatiin " + nimi);
        }
        return std::stoi(nimi.substr(1));
    }

private:
    IrFunktio& f_;
    std::map<std::string, Vreg> numerot_;
};

void Lukija::kasky(const std::vector<std::string>& s) {
    Kasky k;
    std::size_t i = 0;                       // operaation paikka rivillä
    if (s.size() >= 3 && s[1] == "=") {
        k.kohde = reg(s[0]);
        i = 2;
    }
    const std::string& op = s[i];
    auto loput = [&](std::size_t alku) {
        for (std::size_t j = alku; j < s.size(); ++j) {
            k.lahteet.push_back(reg(s[j]));
        }
    };
    if (i == 2 && s.size() == 3) {           // x = 5 tai x = y
        if (on_luku(op)) {
            k.op = Op::Vakio;
            k.vakio = std::stoll(op);
        } else {
            k.op = Op::Kopio;
            loput(2);
        }
    } else if (auto o = kOperaatiot.find(op); o != kOperaatiot.end()) {
        k.op = o->second;
        loput(i + 1);
    } else if (op == "phi") {                // x = phi [a, L0], [b, L4]
        k.op = Op::Phi;
        for (std::size_t j = i + 1; j + 1 < s.size(); j += 2) {
            k.lahteet.push_back(reg(s[j]));
            k.lohkot.push_back(lohko(s[j + 1]));
        }
    } else if (op == "call") {
        k.op = Op::Kutsu;
        k.funktio = s.at(i + 1);
        loput(i + 2);
    } else if (op == "print" || op == "ret") {
        k.op = op == "print" ? Op::Tulosta : Op::Palauta;
        loput(i + 1);
    } else if (op == "jmp") {
        k.op = Op::Hyppy;
        k.lohkot = {lohko(s.at(i + 1))};
    } else if (op == "br") {
        k.op = Op::Haara;
        k.lahteet = {reg(s.at(i + 1))};
        k.lohkot = {lohko(s.at(i + 2)), lohko(s.at(i + 3))};
    } else {
        throw std::runtime_error("tuntematon käsky " + op);
    }
    f_.lohkot.back().kaskyt.push_back(std::move(k));
}
// @loppu lukija

void viimeistele(IrFunktio& f) {
    for (std::size_t b = 0; b < f.lohkot.size(); ++b) {
        const auto& ks = f.lohkot[b].kaskyt;
        if (ks.empty() || !paattava(ks.back().op)) {
            throw std::runtime_error("funktion " + f.nimi + " lohko L"
                                     + std::to_string(b)
                                     + " ei pääty hyppyyn tai paluuseen");
        }
        for (const Kasky& k : ks) {
            for (int kohde : k.lohkot) {
                if (kohde < 0 || kohde >= static_cast<int>(f.lohkot.size())) {
                    throw std::runtime_error("funktiossa " + f.nimi
                                             + " ei ole lohkoa L"
                                             + std::to_string(kohde));
                }
            }
        }
    }
    laske_reunat(f);
}

}  // namespace

IrOhjelma lue_ir(std::istream& syote) {
    IrOhjelma ohjelma;
    IrFunktio f;                             // rakenteilla oleva funktio
    std::optional<Lukija> lukija;
    auto valmis = [&] {
        if (!lukija) return;
        viimeistele(f);
        ohjelma.funktiot.push_back(std::move(f));
    };
    int rivinumero = 0;
    try {
        for (std::string rivi; std::getline(syote, rivi);) {
            ++rivinumero;
            std::vector<std::string> s = sanat(rivi);
            if (s.empty()) continue;
            if (s[0] == "fn") {              // fn nimi(a, b)
                valmis();
                f = IrFunktio{.nimi = s.at(1),
                              .parametreja = static_cast<int>(s.size()) - 2};
                lukija.emplace(f);
                // Parametrit ovat rekisterit 0 .. n-1.
                for (std::size_t p = 2; p < s.size(); ++p) lukija->reg(s[p]);
                continue;
            }
            if (!lukija) {
                throw std::runtime_error("odotettiin riviä fn nimi(...)");
            }
            if (s.size() == 1 && s[0].back() == ':') {          // Lk:
                if (Lukija::lohko(s[0].substr(0, s[0].size() - 1))
                    != static_cast<int>(f.lohkot.size())) {
                    throw std::runtime_error("lohkojen on oltava "
                                             "järjestyksessä L0, L1, ...");
                }
                f.lohkot.emplace_back();
                continue;
            }
            if (f.lohkot.empty()) {
                throw std::runtime_error("käsky lohkon ulkopuolella");
            }
            lukija->kasky(s);
        }
        if (!lukija) throw std::runtime_error("ei yhtään funktiota");
        valmis();
    } catch (const std::logic_error&) {      // at() ja stoi()
        throw std::runtime_error("rivi " + std::to_string(rivinumero)
                                 + ": virheellinen käsky");
    } catch (const std::runtime_error& e) {
        throw std::runtime_error("rivi " + std::to_string(rivinumero) + ": "
                                 + e.what());
    }
    return ohjelma;
}

}  // namespace kide

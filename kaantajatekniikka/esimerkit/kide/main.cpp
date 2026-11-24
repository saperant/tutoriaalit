// kide: Kide-kielen kääntäjä RISC-V:lle.
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "alennus.hpp"
#include "elavyys.hpp"
#include "jasennin.hpp"
#include "koodigen.hpp"
#include "optimointi.hpp"
#include "rekisterit.hpp"
#include "ssa.hpp"
#include "tarkistin.hpp"
#include "tulkki.hpp"

namespace {

// @alku kaytto
const char* const kKaytto =
    "käyttö: kide [valinnat] tiedosto.kide\n"
    "  --vaihe=V          tokenit, ast, aja, ir, passit, elavyys,\n"
    "                     dominanssi, ssa, valit tai asm (oletus)\n"
    "  -O0, -O1           optimoinnit pois tai päälle (oletus -O1)\n"
    "  --varaus=V         pino tai lineaarinen (oletus)\n"
    "  --rekistereita=N   varattavia s-rekistereitä 1-11 (oletus 11)\n"
    "  --funktio=F        tulosta vain funktio F\n";

struct Valinnat {
    std::string vaihe = "asm";
    bool optimoi = true;
    bool lineaarinen = true;
    int rekistereita = kide::kRekistereita;
    std::string funktio;
    std::string tiedosto;
};
// @loppu kaytto

bool jasenna_valinnat(int argc, char** argv, Valinnat& v) {
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a.starts_with("--vaihe=")) {
            v.vaihe = a.substr(8);
        } else if (a == "-O0" || a == "-O1") {
            v.optimoi = a == "-O1";
        } else if (a == "--varaus=pino" || a == "--varaus=lineaarinen") {
            v.lineaarinen = a == "--varaus=lineaarinen";
        } else if (a.starts_with("--rekistereita=")) {
            v.rekistereita = std::atoi(a.c_str() + 15);
            if (v.rekistereita < 1 || v.rekistereita > kide::kRekistereita) {
                return false;
            }
        } else if (a.starts_with("--funktio=")) {
            v.funktio = a.substr(10);
        } else if (!a.starts_with("-") && v.tiedosto.empty()) {
            v.tiedosto = a;
        } else {
            return false;
        }
    }
    const char* vaiheet[] = {"tokenit", "ast", "aja", "ir", "passit",
                             "elavyys", "dominanssi", "ssa", "valit", "asm"};
    bool tunnettu = false;
    for (const char* n : vaiheet) tunnettu |= v.vaihe == n;
    return tunnettu && !v.tiedosto.empty();
}

}  // namespace

// @alku main
int main(int argc, char** argv) {
    using namespace kide;
    Valinnat v;
    if (!jasenna_valinnat(argc, argv, v)) {
        std::cerr << kKaytto;
        return 2;
    }
    std::ifstream syote(v.tiedosto);
    if (!syote) {
        std::cerr << "kide: tiedostoa " << v.tiedosto << " ei voi avata\n";
        return 2;
    }
    std::stringstream lahde;
    lahde << syote.rdbuf();
    std::string teksti = lahde.str();

    // Etuosa: selaus, jäsennys ja semanttinen analyysi.
    Diagnostiikka diag(v.tiedosto);
    std::vector<Tokeni> tokenit = selaa(teksti, diag);
    if (v.vaihe == "tokenit") {
        for (const Tokeni& t : tokenit) {
            std::cout << t.sijainti.rivi << ':' << t.sijainti.sarake << ' '
                      << kuvaus(t.laji);
            if (t.laji == Laji::Tunniste || t.laji == Laji::Luku) {
                std::cout << ' ' << t.teksti;
            }
            std::cout << '\n';
        }
        return diag.virheita() ? 1 : 0;
    }
    // Jokainen vaihe ajetaan vain, jos edelliset onnistuivat: rikkinäisestä
    // syötteestä saataisiin muuten lähinnä seurannaisvirheitä.
    Ohjelma ohjelma;
    if (diag.virheita() == 0) ohjelma = jasenna(tokenit, diag);
    if (diag.virheita() == 0) tarkista(ohjelma, diag);
    if (diag.virheita() > 0) {
        std::cerr << diag.virheita() << " virhettä\n";
        return 1;
    }
    if (v.vaihe == "ast") {
        tulosta_ast(ohjelma, std::cout);
        return 0;
    }
    if (v.vaihe == "aja") {
        try {
            return static_cast<int>(tulkitse(ohjelma, std::cout) & 0xff);
        } catch (const std::runtime_error& e) {
            std::cout.flush();
            std::cerr << "kide: ajonaikainen virhe: " << e.what() << '\n';
            return 3;
        }
    }

    // Keskiosa: välikieli ja optimoinnit.
    IrOhjelma ir = alenna(ohjelma);
    if (!v.funktio.empty()) {
        std::erase_if(ir.funktiot, [&](const IrFunktio& f) {
            return f.nimi != v.funktio;
        });
    }
    for (IrFunktio& f : ir.funktiot) {
        if (v.vaihe == "passit") {
            tulosta_ir(f, std::cout);
            optimoi(f, &std::cout);
        } else if (v.optimoi) {
            optimoi(f);
        } else {
            poista_saavuttamattomat(f);
        }
    }
    if (v.vaihe == "passit") return 0;
    if (v.vaihe == "ir") {
        tulosta_ir(ir, std::cout);
        return 0;
    }

    // Takaosa: rekisterien varaus ja koodingenerointi.
    if (v.vaihe == "asm") std::cout << "    .text\n";
    for (std::size_t i = 0; i < ir.funktiot.size(); ++i) {
        const IrFunktio& f = ir.funktiot[i];
        if (i > 0) std::cout << '\n';
        if (v.vaihe == "elavyys") {
            tulosta_elavyys(f, laske_elavyys(f), std::cout);
            continue;
        }
        if (v.vaihe == "dominanssi") {
            tulosta_dominanssi(f, std::cout);
            continue;
        }
        if (v.vaihe == "ssa") {
            tulosta_ir(ssa_muotoon(f), std::cout);
            continue;
        }
        Varaus varaus = v.lineaarinen
                            ? varaa_lineaarisesti(f, v.rekistereita)
                            : varaa_pinoon(f);
        if (v.vaihe == "valit") {
            tulosta_varaus(f, varaus, std::cout);
        } else {
            generoi(f, varaus, std::cout);
        }
    }
    return 0;
}
// @loppu main

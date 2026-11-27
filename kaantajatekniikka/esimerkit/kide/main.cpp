// kide: Kide-kielen kääntäjä RISC-V:lle.
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

#include "alennus.hpp"
#include "elavyys.hpp"
#include "irluku.hpp"
#include "jasennin.hpp"
#include "koodigen.hpp"
#include "optimointi.hpp"
#include "rekisterit.hpp"
#include "ssa.hpp"
#include "ssaopt.hpp"
#include "ssapois.hpp"
#include "tarkistin.hpp"
#include "tulkki.hpp"

namespace {

// @alku kaytto
const char* const kKaytto =
    "käyttö: kide [valinnat] tiedosto.kide | tiedosto.ir\n"
    "  --vaihe=V          tokenit, ast, aja, ir, passit, elavyys,\n"
    "                     dominanssi, ssa, ssapassit, valit tai asm\n"
    "                     (oletus)\n"
    "  -O0, -O1, -O2      ei optimointeja, paikalliset passit (oletus)\n"
    "                     tai lisäksi optimoinnit SSA-muodossa\n"
    "  --varaus=V         pino tai lineaarinen (oletus)\n"
    "  --rekistereita=N   varattavia s-rekistereitä 1-11 (oletus 11)\n"
    "  --funktio=F        tulosta vain funktio F\n"
    "  --laske            käännetty ohjelma laskee suoritetut käskynsä\n"
    "  --passit=P,...     välikielitiedostolle (.ir) ajettavat passit:\n"
    "                     vakiot, arvot, kuollut, kaaret, pura,\n"
    "                     pura-naiivi, sulauta, paikalliset\n";

struct Valinnat {
    std::string vaihe = "asm";
    int taso = 1;                // -O0, -O1 tai -O2
    bool lineaarinen = true;
    int rekistereita = kide::kRekistereita;
    bool laske = false;
    std::string funktio;
    std::string passit;
    std::string tiedosto;
};
// @loppu kaytto

bool jasenna_valinnat(int argc, char** argv, Valinnat& v) {
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        if (a.starts_with("--vaihe=")) {
            v.vaihe = a.substr(8);
        } else if (a == "-O0" || a == "-O1" || a == "-O2") {
            v.taso = a[2] - '0';
        } else if (a == "--laske") {
            v.laske = true;
        } else if (a.starts_with("--passit=")) {
            v.passit = a.substr(9);
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
    const char* vaiheet[] = {"tokenit", "ast",   "aja",       "ir",
                             "passit",  "elavyys", "dominanssi", "ssa",
                             "ssapassit", "valit", "asm"};
    bool tunnettu = false;
    for (const char* n : vaiheet) tunnettu |= v.vaihe == n;
    return tunnettu && !v.tiedosto.empty();
}

// @alku putki
// -O2: paikallisten passien jälkeen funktio viedään SSA-muotoon,
// optimoidaan siinä ja tuodaan takaisin tavalliseksi välikieleksi.
void optimoi_ssa_muodossa(kide::IrFunktio& f, std::ostream* loki) {
    using namespace kide;
    auto vaihe = [&](const char* nimi) {
        if (!loki) return;
        *loki << "; " << nimi << '\n';
        tulosta_ir(f, *loki);
    };
    f = ssa_muotoon(f);
    vaihe("SSA-muoto");
    optimoi_ssa(f, loki);
    jaa_kriittiset_kaaret(f);
    pura_phit(f);
    vaihe("phit purettu kopioiksi");
    sulauta_kopiot(f);
    vaihe("kopiot sulautettu");
    optimoi(f);                  // tyhjät lohkot ja jääneet kopiot
    vaihe("paikallinen siivous");
}
// @loppu putki

// Välikielitiedostolle ajetaan vain valinnalla --passit nimetyt passit,
// jotta jokaista passia voi testata yksin.
void aja_passit(kide::IrFunktio& f, const std::string& passit) {
    using namespace kide;
    std::stringstream nimet(passit);
    for (std::string nimi; std::getline(nimet, nimi, ',');) {
        bool ssa = nimi == "vakiot" || nimi == "arvot" || nimi == "kuollut";
        if (std::string virhe = ssa ? tarkista_ssa(f) : ""; !virhe.empty()) {
            throw std::runtime_error("funktio " + f.nimi
                                     + " ei ole SSA-muodossa: " + virhe);
        }
        if (nimi == "vakiot") {
            etene_vakiot(f);
        } else if (nimi == "arvot") {
            numeroi_arvot_ssa(f);
        } else if (nimi == "kuollut") {
            poista_kuollut_ssa(f);
        } else if (nimi == "kaaret") {
            jaa_kriittiset_kaaret(f);
        } else if (nimi == "pura") {
            pura_phit(f);
        } else if (nimi == "pura-naiivi") {
            pura_phit(f, Kopiointi::Perakkain);
        } else if (nimi == "sulauta") {
            sulauta_kopiot(f);
        } else if (nimi == "paikalliset") {
            optimoi(f);
        } else {
            throw std::runtime_error("tuntematon passi " + nimi);
        }
        if (std::string virhe = ssa ? tarkista_ssa(f) : ""; !virhe.empty()) {
            throw std::logic_error("passi " + nimi + " rikkoi SSA-muodon: "
                                   + virhe);
        }
    }
}

// Etuosa: selaus, jäsennys ja semanttinen analyysi sekä alentaminen
// välikieleksi. Palauttaa paluuarvon, jos käännös päättyy etuosaan
// (virhe tai pyydetty vaihe), muuten täyttää välikielen.
std::optional<int> etuosa(const Valinnat& v, const std::string& teksti,
                          kide::IrOhjelma& ir) {
    using namespace kide;
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
    ir = alenna(ohjelma);
    return std::nullopt;
}

// @alku main
int kaanna(const Valinnat& v) {
    using namespace kide;
    std::ifstream syote(v.tiedosto);
    if (!syote) {
        std::cerr << "kide: tiedostoa " << v.tiedosto << " ei voi avata\n";
        return 2;
    }
    IrOhjelma ir;
    if (v.tiedosto.ends_with(".ir")) {
        // Välikielitiedosto: vain pyydetyt passit, ei etuosaa.
        ir = lue_ir(syote);
        for (IrFunktio& f : ir.funktiot) aja_passit(f, v.passit);
    } else {
        std::stringstream lahde;
        lahde << syote.rdbuf();
        if (auto paluu = etuosa(v, lahde.str(), ir)) return *paluu;
    }
    if (!v.funktio.empty()) {
        std::erase_if(ir.funktiot, [&](const IrFunktio& f) {
            return f.nimi != v.funktio;
        });
    }

    // Keskiosa: optimoinnit tason mukaan.
    bool passiloki = v.vaihe == "passit" || v.vaihe == "ssapassit";
    for (IrFunktio& f : ir.funktiot) {
        if (v.tiedosto.ends_with(".ir")) break;
        if (v.vaihe == "passit") {
            tulosta_ir(f, std::cout);
            optimoi(f, &std::cout);
        } else if (v.taso == 0) {
            poista_saavuttamattomat(f);
        } else {
            optimoi(f);
        }
        if (v.vaihe == "ssa") {
            f = ssa_muotoon(f);
            if (v.taso >= 2) optimoi_ssa(f);
        } else if (v.vaihe == "ssapassit") {
            optimoi_ssa_muodossa(f, &std::cout);
        } else if (v.taso >= 2 && !passiloki) {
            optimoi_ssa_muodossa(f, nullptr);
        }
    }
    if (passiloki) return 0;
    if (v.vaihe == "ir" || v.vaihe == "ssa") {
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
        for (const Peruslohko& l : f.lohkot) {
            if (l.kaskyt.front().op == Op::Phi) {
                throw std::runtime_error(
                    "funktio " + f.nimi
                    + " on SSA-muodossa: pura phit ennen takaosaa");
            }
        }
        Varaus varaus = v.lineaarinen
                            ? varaa_lineaarisesti(f, v.rekistereita)
                            : varaa_pinoon(f);
        if (v.vaihe == "valit") {
            tulosta_varaus(f, varaus, std::cout);
        } else {
            generoi(f, varaus, std::cout, v.laske);
        }
    }
    return 0;
}
// @loppu main

}  // namespace

int main(int argc, char** argv) {
    Valinnat v;
    if (!jasenna_valinnat(argc, argv, v)) {
        std::cerr << kKaytto;
        return 2;
    }
    try {
        return kaanna(v);
    } catch (const std::runtime_error& e) {
        std::cerr << "kide: " << v.tiedosto << ": " << e.what() << '\n';
        return 1;
    } catch (const std::logic_error& e) {
        std::cerr << "kide: sisäinen virhe: " << e.what() << '\n';
        return 4;
    }
}

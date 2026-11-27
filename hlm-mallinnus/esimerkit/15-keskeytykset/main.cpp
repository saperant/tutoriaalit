// Keskeytykset virtuaaliprototyypissä: ajastin antaa tikkejä, sarjaportti
// vastaanottaa merkkejä, ja prosessori joko nukkuu (wfi) tai pyörii
// silmukassa niiden välissä.
//
// Käyttö: ohjelma KVANTTI_NS wfi|kysely [loki] [ei-synkronointia]
#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/tlm_quantumkeeper.h>

#include "../14-prototyyppi/lataaja.hpp"
#include "../mallit/muisti.hpp"
#include "../mallit/vayla.hpp"
#include "keskeytysprosessori.hpp"
#include "laitteet.hpp"
#include "rv32csr.hpp"

using namespace sc_core;
using namespace rv32;

// Ajastimen jakso kellojaksoina: 17,33 us. Jakso ei ole kokeiltavien
// kvanttien monikerta, jotta tikit osuvat kvantin eri kohtiin.
constexpr int JAKSO = 1733;
constexpr int TIKKEJA = 10;   // ohjelma lopettaa näin monen tikin jälkeen

// @alku ohjelma
// Pääohjelma alustaa keskeytykset ja odottaa, kunnes käsittelijä on
// laskenut TIKKEJA tikkiä. Odotus on joko wfi tai pelkkä silmukka.
std::vector<unsigned char> ohjelma(bool nuku) {
    KeskeytysKokoaja k;
    k.lui(sp, 0x10);              // pino RAM-muistin lopusta alaspäin
    k.la(t0, "kasittelija");
    k.csrw(csr::mtvec, t0);
    k.lui(s0, 0x10001);           // ajastin
    k.addi(t0, zero, JAKSO);
    k.sw(t0, 4, s0);              // JAKSO: tikit alkavat
    k.lui(t0, 1);                 // 0x880 = MTI | MEI
    k.addi(t0, t0, -0x780);
    k.csrw(csr::mie, t0);
    k.addi(t0, zero, 8);          // mstatus.MIE
    k.csrs(csr::mstatus, t0);
    k.addi(s1, zero, TIKKEJA);
    k.nimio("odota");
    if (nuku) k.wfi();            // nukutaan seuraavaan keskeytykseen
    k.la(t0, "tikit");
    k.lw(t1, 0, t0);
    k.bge(t1, s1, "valmis");
    k.jal(zero, "odota");
    k.nimio("valmis");
    k.sw(zero, 4, s0);            // JAKSO = 0: ajastin seis
    k.addi(a0, t1, 0);            // paluuarvo: lasketut tikit
    k.ecall();
    // @loppu ohjelma

    // @alku kasittelija
    // Käsittelijä tallentaa käyttämänsä rekisterit pinoon, koska
    // keskeytys voi osua mihin tahansa pääohjelman kohtaan.
    k.nimio("kasittelija");
    k.addi(sp, sp, -8);
    k.sw(t0, 0, sp);
    k.sw(t1, 4, sp);
    k.csrr(t0, csr::mcause);
    k.andi(t0, t0, 15);
    k.addi(t1, zero, 11);
    k.beq(t0, t1, "ulkoinen");
    k.lui(t0, 0x10001);           // ajastin: kuitataan ja lasketaan tikki
    k.addi(t1, zero, 1);
    k.sw(t1, 8, t0);
    k.la(t0, "tikit");
    k.lw(t1, 0, t0);
    k.addi(t1, t1, 1);
    k.sw(t1, 0, t0);
    k.jal(zero, "paluu");
    k.nimio("ulkoinen");          // sarjaportti: luku kuittaa, kaiutetaan
    k.lui(t0, 0x10000);
    k.lw(t1, 0, t0);
    k.sw(t1, 0, t0);
    k.nimio("paluu");
    k.lw(t0, 0, sp);
    k.lw(t1, 4, sp);
    k.addi(sp, sp, 8);
    k.mret();
    k.nimio("tikit");
    k.data(0);
    return k.valmis();
}
// @loppu kasittelija

// @alku paate
// Testipenkin pääte: kirjoittaa sarjaporttiin kolme merkkiä. Keskimmäinen
// saapuu juuri ennen ajastimen kolmatta tikkiä.
SC_MODULE(Paate) {
    Paateuart* uart = nullptr;

    SC_CTOR(Paate) { SC_THREAD(aja); }

    void aja() {
        if (uart == nullptr) return;
        wait(30, SC_US);
        uart->vastaanota('o');
        wait(22, SC_US);
        uart->vastaanota('k');
        wait(23, SC_US);
        uart->vastaanota('\n');
    }
};
// @loppu paate

namespace {

long long ns(const sc_time& t) {
    return static_cast<long long>(t / sc_time(1, SC_NS));
}

struct Tapahtuma {
    sc_time aika;
    int jarjestys;  // samanaikaisten järjestys: nousu, otto, lasku, paluu
    std::string teksti;
};

}  // namespace

int sc_main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "käyttö: ohjelma KVANTTI_NS wfi|kysely [loki] "
                     "[ei-synkronointia]\n";
        return 2;
    }
    const int kvantti_ns = std::atoi(argv[1]);
    const std::string tila = argv[2];
    bool loki = false, synkronoi = true;
    for (int i = 3; i < argc; ++i) {
        const std::string valitsin = argv[i];
        if (valitsin == "loki") loki = true;
        else if (valitsin == "ei-synkronointia") synkronoi = false;
    }
    // sc_stop() tulostaa oletuksena ilmoituksen; vaimennetaan se.
    sc_report_handler::set_actions("/OSCI/SystemC", SC_INFO, SC_DO_NOTHING);

    // @alku jarjestelma
    tlm_utils::tlm_quantumkeeper::set_global_quantum(
        sc_time(kvantti_ns, SC_NS));
    KeskeytysProsessori cpu("cpu");
    cpu.synkronoi_palatessa = synkronoi;
    Lataaja lataaja("lataaja", ohjelma(tila == "wfi"));
    Vayla vayla("vayla", sc_time(5, SC_NS));
    Muisti ram("ram", 64 * 1024, sc_time(20, SC_NS), sc_time(20, SC_NS));
    Paateuart uart("uart");
    Tikkiajastin ajastin("ajastin");
    Paate paate("paate");
    if (loki) paate.uart = &uart;
    cpu.socket.bind(vayla.kohde);
    lataaja.socket.bind(vayla.kohde);
    vayla.liita(ram.socket, 0x0000'0000, 64 * 1024);
    vayla.liita(uart.socket, 0x1000'0000, 0x8);
    vayla.liita(ajastin.socket, 0x1000'1000, 0xC);
    // @alku linjat
    // Keskeytykset kulkevat väylän ohi omia johtimiaan.
    sc_signal<bool> ajastin_irq("ajastin_irq"), uart_irq("uart_irq");
    ajastin.irq.bind(ajastin_irq);
    cpu.ajastin_irq.bind(ajastin_irq);
    uart.irq.bind(uart_irq);
    cpu.ulkoinen_irq.bind(uart_irq);
    // @loppu linjat
    sc_start();
    // @loppu jarjestelma

    // Jokaiselle otetulle keskeytykselle haetaan linjan nousu, johon se
    // vastaa. Jos uutta nousua ei ole, keskeytys oli aiheeton.
    std::vector<Tapahtuma> tapahtumat;
    for (const sc_time& t : ajastin.nousut) {
        tapahtumat.push_back({t, 0, "ajastin: linja ylös"});
    }
    for (const sc_time& t : ajastin.laskut) {
        tapahtumat.push_back({t, 2, "ajastin: kuitattu, linja alas"});
    }
    for (const sc_time& t : uart.nousut) {
        tapahtumat.push_back({t, 0, "uart: merkki saapui, linja ylös"});
    }
    for (const sc_time& t : uart.laskut) {
        tapahtumat.push_back({t, 2, "uart: luettu, linja alas"});
    }
    for (const sc_time& t : cpu.paluut) {
        tapahtumat.push_back({t, 3, "prosessori: paluu (mret)"});
    }
    std::size_t ajastimen = 0, uartin = 0;
    unsigned aiheettomia = 0;
    long long pienin = -1, suurin = -1;
    for (const KeskeytysProsessori::Otto& o : cpu.otot) {
        const std::vector<sc_time>& nousut =
            o.syy == 7 ? ajastin.nousut : uart.nousut;
        std::size_t& seuraava = o.syy == 7 ? ajastimen : uartin;
        std::string teksti = "prosessori: keskeytys " +
                             std::to_string(o.syy);
        if (seuraava < nousut.size() && nousut[seuraava] <= o.aika) {
            const long long viive = ns(o.aika - nousut[seuraava]);
            ++seuraava;
            if (o.syy == 7) {
                pienin = pienin < 0 ? viive : std::min(pienin, viive);
                suurin = std::max(suurin, viive);
            }
            teksti += ", viive " + std::to_string(viive) + " ns";
        } else {
            ++aiheettomia;
            teksti += ", aiheeton";
        }
        tapahtumat.push_back({o.aika, 1, teksti});
    }

    if (loki) {
        std::stable_sort(tapahtumat.begin(), tapahtumat.end(),
                         [](const Tapahtuma& a, const Tapahtuma& b) {
                             if (a.aika != b.aika) return a.aika < b.aika;
                             return a.jarjestys < b.jarjestys;
                         });
        std::cout << "aika (ns)  tapahtuma\n";
        for (const Tapahtuma& t : tapahtumat) {
            std::cout << std::setw(9) << ns(t.aika) << "  " << t.teksti
                      << "\n";
        }
        std::cout << "ohjelma laski " << cpu.paluuarvo << " tikkiä, käskyjä "
                  << cpu.kaskyja << ", nukuttu " << ns(cpu.nukuttu)
                  << " ns / " << ns(sc_time_stamp()) << " ns\n";
        return 0;
    }
    if (!synkronoi) {
        std::cout << "ilman synkronointia: ohjelma laski " << cpu.paluuarvo
                  << " tikkiä, ajastin antoi " << ajastin.nousut.size()
                  << "\naiheettomia keskeytyksiä " << aiheettomia
                  << ", aika " << ns(sc_time_stamp()) << " ns\n";
        return 0;
    }
    const std::string viive =
        std::to_string(pienin) + ".." + std::to_string(suurin);
    std::cout << std::setw(7) << kvantti_ns << "  " << std::left
              << std::setw(7) << tila << std::right << "  " << std::setw(5)
              << cpu.paluuarvo << "  " << std::setw(9)
              << ajastin.menetetyt << "  " << std::setw(12) << viive << "  "
              << std::setw(7) << cpu.kaskyja << "  " << std::setw(6)
              << cpu.synkronointeja << "  " << std::setw(7)
              << ns(sc_time_stamp()) / 1000 << "\n";
    return 0;
}

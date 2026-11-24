// Sama muistijärjestelmä kolmella tarkkuustasolla: LT-malli ilman
// kilpailua, tapahtumapohjainen varausmalli ja syklipohjainen malli.
//
// Käyttö:  ohjelma MALLI YTIMIÄ [KVANTTI_NS]
//          MALLI on lt, varaus tai sykli
//
// K ydintä tekee kukin PYYNTOJA hutipyyntöä. Pyyntöjen välissä ydin
// laskee 1-199 ns (keskiarvo 100 ns), ja sillä on yksi pyyntö kerrallaan
// kesken. Pyyntö kulkee väylän läpi (4 ns) muistiohjaimelle, joka
// palvelee yhden pyynnön kerrallaan (10 ns), ja DRAM-käyttö kestää vielä
// 40 ns. Ilman jonoa viive on siis 54 ns.
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>

#include <systemc>
#include <tlm>
#include <tlm_utils/simple_initiator_socket.h>
#include <tlm_utils/simple_target_socket.h>
#include <tlm_utils/tlm_quantumkeeper.h>

#include "../mallit/muisti.hpp"
#include "../mallit/vayla.hpp"

using namespace sc_core;

constexpr int PYYNTOJA = 1000;
constexpr int VAYLA_NS = 4, PALVELU_NS = 10, DRAM_NS = 40;

// Prosessien heräämiset: simuloinnin työmäärän mittari, joka ei riipu
// koneen nopeudesta.
static unsigned long aktivointeja = 0;

// @alku kuorma
// Ytimen laskenta-ajat kiinteällä siemenellä: sama jono kaikissa
// malleissa.
class Kuorma {
public:
    explicit Kuorma(int ydin)
        : tila_(0x9E3779B97F4A7C15ULL * static_cast<unsigned>(ydin + 1)) {}
    int laskenta_ns() {
        tila_ ^= tila_ << 13;
        tila_ ^= tila_ >> 7;
        tila_ ^= tila_ << 17;
        return 1 + static_cast<int>(tila_ % 199);
    }

private:
    std::uint64_t tila_;
};
// @loppu kuorma

struct Tulos {
    double viive_ns = 0;  // pyyntöjen viiveiden summa
    int valmiita = 0;     // ytimiä, jotka ovat tehneet kaikki pyynnöt
};
static Tulos tulos;
static int ytimia = 0;

// @alku ydin
// TLM-ydin: laskee paikallisessa ajassaan ja lähettää lukupyynnön.
// Kvantti 0 synkronoi jokaisen pyynnön jälkeen.
SC_MODULE(Ydin) {
    SC_HAS_PROCESS(Ydin);
    tlm_utils::simple_initiator_socket<Ydin> socket{"socket"};
    tlm_utils::tlm_quantumkeeper qk;
    Kuorma kuorma;

    Ydin(sc_module_name nimi, int id) : sc_module(nimi), kuorma(id) {
        SC_THREAD(aja);
    }

    void aja() {
        unsigned char rivi[64] = {};
        tlm::tlm_generic_payload gp;
        qk.reset();
        for (int i = 0; i < PYYNTOJA; ++i) {
            qk.inc(sc_time(kuorma.laskenta_ns(), SC_NS));
            if (qk.need_sync()) {  // kvantti 0: pyyntö lähtee ajallaan
                qk.sync();
                ++aktivointeja;
            }
            gp.set_command(tlm::TLM_READ_COMMAND);
            gp.set_address(0);
            gp.set_data_ptr(rivi);
            gp.set_data_length(64);
            gp.set_streaming_width(64);
            gp.set_response_status(tlm::TLM_INCOMPLETE_RESPONSE);
            sc_time t = qk.get_local_time();
            const sc_time ennen = t;
            socket->b_transport(gp, t);
            tulos.viive_ns += (t - ennen).to_seconds() * 1e9;
            qk.set(t);
            if (qk.need_sync()) {
                qk.sync();
                ++aktivointeja;
            }
        }
        qk.sync();
        if (++tulos.valmiita == ytimia) sc_stop();
    }
};
// @loppu ydin

// @alku varaus
// Muistiohjain varausmallina: ohjain muistaa, milloin se vapautuu, ja
// pyyntö alkaa aikaisintaan silloin. Malli on oikein vain, jos pyynnöt
// saapuvat aikajärjestyksessä (kvantti 0).
class Ohjain : public sc_module {
public:
    tlm_utils::simple_target_socket<Ohjain> socket{"socket"};

    explicit Ohjain(sc_module_name nimi) : sc_module(nimi) {
        socket.register_b_transport(this, &Ohjain::b_transport);
    }

private:
    void b_transport(tlm::tlm_generic_payload& gp, sc_time& viive) {
        const sc_time saapuu = sc_time_stamp() + viive;
        const sc_time alku = std::max(saapuu, vapaa_);
        vapaa_ = alku + sc_time(PALVELU_NS, SC_NS);
        viive += (alku - saapuu) + sc_time(PALVELU_NS + DRAM_NS, SC_NS);
        gp.set_response_status(tlm::TLM_OK_RESPONSE);
    }
    sc_time vapaa_ = SC_ZERO_TIME;
};
// @loppu varaus

// @alku sykli
// Syklipohjainen malli: jokainen komponentti on SC_METHOD, joka ajetaan
// joka kellojaksolla (1 ns), ja komponentit viestivät signaaleilla.
// Signaalin arvo näkyy vastaanottajalle seuraavalla jaksolla.
SC_MODULE(SykliYdin) {
    SC_HAS_PROCESS(SykliYdin);
    sc_in<bool> kello;
    sc_out<bool> pyynto;
    sc_in<bool> valmis;
    Kuorma kuorma;
    int laskenta = 0, tehty = 0;
    bool aloitettu = false;
    long lahti = 0;  // jakso, jolla pyyntö lähti

    SykliYdin(sc_module_name nimi, int id) : sc_module(nimi), kuorma(id) {
        SC_METHOD(jakso);
        sensitive << kello.pos();
        dont_initialize();
    }

    void jakso() {
        ++aktivointeja;
        const long nyt = static_cast<long>(sc_time_stamp().value() / 1000);
        pyynto.write(false);
        if (laskenta > 0 && --laskenta == 0) {  // laskenta valmis
            pyynto.write(true);
            lahti = nyt;
        }
        if (!aloitettu) {
            aloitettu = true;
            laskenta = kuorma.laskenta_ns();
        } else if (valmis.read()) {  // vastaus saapui
            tulos.viive_ns += static_cast<double>(nyt - lahti);
            if (++tehty == PYYNTOJA) {
                if (++tulos.valmiita == ytimia) sc_stop();
                return;
            }
            laskenta = kuorma.laskenta_ns();
        }
    }
};

SC_MODULE(SykliOhjain) {
    SC_HAS_PROCESS(SykliOhjain);
    sc_in<bool> kello;
    sc_vector<sc_in<bool>> pyynto;
    sc_vector<sc_out<bool>> valmis;
    struct Pyynto {
        int ydin;
        long hetki;  // saapuu ohjaimelle / vastaus valmis
    };
    std::vector<Pyynto> jono, vastaukset;
    long vapaa = 0;

    SykliOhjain(sc_module_name nimi, int n)
        : sc_module(nimi), pyynto("pyynto", n), valmis("valmis", n) {
        SC_METHOD(jakso);
        sensitive << kello.pos();
        dont_initialize();
    }

    void jakso() {
        ++aktivointeja;
        const long nyt = static_cast<long>(sc_time_stamp().value() / 1000);
        for (auto& v : valmis) v.write(false);
        // Pyyntö lähti edellisellä jaksolla; väylä vie VAYLA_NS.
        for (int i = 0; i < static_cast<int>(pyynto.size()); ++i) {
            if (pyynto[i].read()) jono.push_back({i, nyt - 1 + VAYLA_NS});
        }
        if (!jono.empty() && jono.front().hetki <= nyt && vapaa <= nyt) {
            const Pyynto p = jono.front();
            jono.erase(jono.begin());
            vapaa = nyt + PALVELU_NS;
            // Ydin näkee valmis-signaalin seuraavalla jaksolla.
            vastaukset.push_back({p.ydin, nyt + PALVELU_NS + DRAM_NS - 1});
        }
        for (auto it = vastaukset.begin(); it != vastaukset.end();) {
            if (it->hetki == nyt) {
                valmis[it->ydin].write(true);
                it = vastaukset.erase(it);
            } else {
                ++it;
            }
        }
    }
};
// @loppu sykli

int sc_main(int argc, char* argv[]) {
    if (argc < 3) {
        std::fprintf(stderr, "käyttö: %s lt|varaus|sykli YTIMIÄ [KVANTTI]\n",
                     argv[0]);
        return 2;
    }
    const std::string malli = argv[1];
    ytimia = std::atoi(argv[2]);
    const int kvantti = argc > 3 ? std::atoi(argv[3]) : 0;
    sc_report_handler::set_actions(SC_INFO, SC_DO_NOTHING);  // sc_stop

    // @alku kokoonpano
    std::vector<std::unique_ptr<sc_module>> osat;
    std::vector<std::unique_ptr<sc_signal<bool>>> signaalit;
    sc_clock kello("kello", 1, SC_NS);
    tlm_utils::tlm_quantumkeeper::set_global_quantum(
        sc_time(kvantti, SC_NS));
    if (malli == "lt" || malli == "varaus") {
        auto* vayla = new Vayla("vayla", sc_time(VAYLA_NS, SC_NS));
        osat.emplace_back(vayla);
        if (malli == "lt") {  // kiinteä viive, ei kilpailua
            auto* m = new Muisti("dram", 64, sc_time(PALVELU_NS + DRAM_NS,
                                                     SC_NS), SC_ZERO_TIME);
            osat.emplace_back(m);
            vayla->liita(m->socket, 0, 64);
        } else {
            auto* o = new Ohjain("ohjain");
            osat.emplace_back(o);
            vayla->liita(o->socket, 0, 64);
        }
        for (int i = 0; i < ytimia; ++i) {
            auto* y = new Ydin(("ydin" + std::to_string(i)).c_str(), i);
            osat.emplace_back(y);
            y->socket.bind(vayla->kohde);
        }
    } else {
        auto* o = new SykliOhjain("ohjain", ytimia);
        osat.emplace_back(o);
        o->kello(kello);
        for (int i = 0; i < ytimia; ++i) {
            auto* y = new SykliYdin(("ydin" + std::to_string(i)).c_str(), i);
            osat.emplace_back(y);
            signaalit.emplace_back(new sc_signal<bool>);
            signaalit.emplace_back(new sc_signal<bool>);
            y->kello(kello);
            y->pyynto(*signaalit[signaalit.size() - 2]);
            o->pyynto[i](*signaalit[signaalit.size() - 2]);
            y->valmis(*signaalit.back());
            o->valmis[i](*signaalit.back());
        }
    }
    sc_start();
    // @loppu kokoonpano

    const double aika_ns = sc_time_stamp().to_seconds() * 1e9;
    const double n = static_cast<double>(ytimia) * PYYNTOJA;
    std::printf("%-7s %2d %4d %9.1f %6.2f %7.1f %8lu\n", malli.c_str(),
                ytimia, kvantti, aika_ns / 1000, 64 * n / aika_ns,
                tulos.viive_ns / n, aktivointeja);
    return 0;
}

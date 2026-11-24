// Tapahtumat: ilmoitustavat, aikaraja ja dynaaminen herkkyys.
#include <iostream>
#include <systemc>

using namespace sc_core;

static std::ostream& loki() {
    return std::cout << sc_time_stamp() << ": ";
}

// @alku ilmoitukset
// Kolme ilmoitustapaa samalla hetkellä: välitön, delta ja ajastettu.
SC_MODULE(Ilmoitukset) {
    sc_event heti, delta, ajastettu;
    sc_dt::uint64 d0 = 0;  // delta-laskuri ilmoitushetkellä

    SC_CTOR(Ilmoitukset) {
        SC_THREAD(ilmoita);
        SC_METHOD(kuuntele);
        sensitive << heti << delta << ajastettu;
        dont_initialize();
    }

    void ilmoita() {
        wait(10, SC_NS);
        loki() << "ilmoitetaan\n";
        d0 = sc_delta_count();
        ajastettu.notify(5, SC_NS);    // 5 ns:n päästä
        delta.notify(SC_ZERO_TIME);    // seuraavassa delta-syklissä
        heti.notify();                 // tässä arviointivaiheessa
    }

    void kuuntele() {
        const char* mika = heti.triggered()    ? "heti"
                           : delta.triggered() ? "delta"
                                               : "ajastettu";
        loki() << mika << ", delta-syklejä ilmoituksesta "
               << sc_delta_count() - d0 << '\n';
    }
};
// @loppu ilmoitukset

// @alku valvoja
// Työ valmistuu vaihtelevassa ajassa; valvoja odottaa kutakin työtä
// enintään aikarajan verran: wait(aika, tapahtuma).
SC_MODULE(Valvonta) {
    sc_event valmis;

    SC_CTOR(Valvonta) {
        SC_THREAD(tyontekija);
        SC_THREAD(valvoja);
    }

    void tyontekija() {
        for (int kesto : {20, 35, 60}) {
            wait(kesto, SC_NS);
            valmis.notify(SC_ZERO_TIME);
        }
    }

    void valvoja() {
        const sc_time aikaraja(50, SC_NS);
        for (int i = 0; i < 4; ++i) {
            wait(aikaraja, valmis);
            if (valmis.triggered()) {
                loki() << "työ valmis\n";
            } else {
                loki() << "aikaraja ylittyi\n";
            }
        }
    }
};
// @loppu valvoja

// @alku hukattu
// Tapahtumalla ei ole muistia: ilmoitus ennen odotuksen alkua hukkuu.
SC_MODULE(Hukattu) {
    sc_event lahetetty;

    SC_CTOR(Hukattu) {
        SC_THREAD(lahettaja);
        SC_THREAD(vastaanottaja);
    }

    void lahettaja() {
        wait(200, SC_NS);
        loki() << "lähetetään\n";
        lahetetty.notify();
    }

    void vastaanottaja() {
        wait(201, SC_NS);  // ehtii odottamaan vasta myöhemmin
        wait(sc_time(10, SC_NS), lahetetty);
        loki() << (lahetetty.triggered() ? "vastaanotettu\n"
                                         : "ilmoitus hukkui\n");
    }
};
// @loppu hukattu

// @alku seuraaja
// SC_METHOD ei voi odottaa, mutta next_trigger() vaihtaa sen
// herkkyyden seuraavaa kutsua varten: tässä vuorotellen kello ja tauko.
SC_MODULE(Vilkku) {
    sc_in<bool> clk;
    int vaihe = 0;

    SC_CTOR(Vilkku) {
        SC_METHOD(vilkuta);
        sensitive << clk.pos();  // staattinen herkkyys
        dont_initialize();
    }

    void vilkuta() {
        loki() << "vilkku " << vaihe << '\n';
        if (++vaihe % 2 == 0) {
            next_trigger(25, SC_NS);  // pidempi tauko, ohittaa kellon
        }                             // ilman kutsua: staattinen
    }
};
// @loppu seuraaja

int sc_main(int, char*[]) {
    Ilmoitukset ilmoitukset("ilmoitukset");
    Valvonta valvonta("valvonta");
    Hukattu hukattu("hukattu");

    sc_clock clk("clk", 10, SC_NS, 0.5, 250, SC_NS);  // alkaa 250 ns
    Vilkku vilkku("vilkku");
    vilkku.clk(clk);

    sc_start(300, SC_NS);
    return 0;
}

// Delta-syklit: signaalin päivitys, vaihto ja kombinaatioketju.
#include <iostream>
#include <systemc>

using namespace sc_core;

// @alku vaihto
// Kaksi rekisteriä vaihtaa arvonsa joka kellojaksolla. Signaalien
// kautta vaihto onnistuu, koska kaikki lukevat vanhan arvon ja uudet
// arvot päivittyvät vasta arviointivaiheen jälkeen. Tavallisten
// jäsenmuuttujien kautta tulos riippuu prosessien ajojärjestyksestä.
SC_MODULE(Vaihto) {
    sc_in<bool> clk;
    sc_signal<int> sa{"sa", 1}, sb{"sb", 2};
    int ma = 1, mb = 2;

    SC_CTOR(Vaihto) {
        SC_METHOD(rekisteri_a);
        sensitive << clk.pos();
        dont_initialize();
        SC_METHOD(rekisteri_b);
        sensitive << clk.pos();
        dont_initialize();
    }

    void rekisteri_a() {
        sa.write(sb.read());
        ma = mb;
    }
    void rekisteri_b() {
        sb.write(sa.read());
        mb = ma;
    }
};
// @loppu vaihto

// @alku ketju
// Kolmen invertterin ketju: x -> y1 -> y2 -> y3. Jokainen aste on oma
// prosessinsa, joten muutos etenee yhden delta-syklin asteelta toiselle.
SC_MODULE(Ketju) {
    sc_signal<bool> x{"x"}, y1{"y1"}, y2{"y2"}, y3{"y3"};
    sc_dt::uint64 d0 = 0;

    SC_CTOR(Ketju) {
        SC_METHOD(aste1);
        sensitive << x;
        SC_METHOD(aste2);
        sensitive << y1;
        SC_METHOD(aste3);
        sensitive << y2;
        SC_METHOD(nayta);
        sensitive << x << y1 << y2 << y3;
        dont_initialize();
        SC_THREAD(heratteet);
    }

    void aste1() { y1.write(!x.read()); }
    void aste2() { y2.write(!y1.read()); }
    void aste3() { y3.write(!y2.read()); }

    void nayta() {
        std::cout << sc_time_stamp() << " +" << sc_delta_count() - d0
                  << ": x=" << x.read() << " y1=" << y1.read()
                  << " y2=" << y2.read() << " y3=" << y3.read() << '\n';
    }

    void heratteet() {
        wait(10, SC_NS);
        d0 = sc_delta_count();
        x.write(true);
        // Kirjoitettu arvo näkyy vasta päivitysvaiheen jälkeen.
        std::cout << "heti kirjoituksen jälkeen x=" << x.read() << '\n';
        wait(SC_ZERO_TIME);  // odotetaan yksi delta-sykli
        std::cout << "deltan jälkeen x=" << x.read() << '\n';
    }
};
// @loppu ketju

int sc_main(int, char*[]) {
    // @alku main
    sc_clock clk("clk", 10, SC_NS, 0.5, 25, SC_NS);  // reunat 25, 35, ...
    Vaihto vaihto("vaihto");
    vaihto.clk(clk);
    Ketju ketju("ketju");

    sc_start(20, SC_NS);  // alustus ja ketjun herätteet
    for (int jakso = 1; jakso <= 3; ++jakso) {
        sc_start(10, SC_NS);
        std::cout << "jakso " << jakso << ": signaalit " << vaihto.sa
                  << " " << vaihto.sb << ", muuttujat " << vaihto.ma
                  << " " << vaihto.mb << '\n';
    }
    // @loppu main
    return 0;
}

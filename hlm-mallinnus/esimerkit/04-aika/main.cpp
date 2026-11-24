// Simulaatioaika: tarkkuus, pyöristys ja laskutoimitukset.
#include <iomanip>
#include <iostream>
#include <systemc>

using namespace sc_core;

// @alku reunat
// Tulostaa kellon neljä ensimmäistä jaksoa.
SC_MODULE(Reunat) {
    sc_in<bool> clk;

    SC_CTOR(Reunat) { SC_THREAD(seuraa); }

    void seuraa() {
        for (int i = 0; i < 4; ++i) {
            wait(clk.posedge_event());
            std::cout << "nouseva " << sc_time_stamp();
            wait(clk.negedge_event());
            std::cout << ", laskeva " << sc_time_stamp() << '\n';
        }
    }
};
// @loppu reunat

int sc_main(int, char*[]) {
    // @alku tarkkuus
    // Tarkkuus asetetaan ennen ensimmäistäkään nollasta poikkeavaa
    // aikaa. Oletus on 1 ps; tässä 10 ps.
    sc_set_time_resolution(10, SC_PS);
    std::cout << "tarkkuus " << sc_get_time_resolution() << '\n';

    const sc_time jakso(2.5, SC_NS);
    const sc_time pieni(14, SC_PS);    // pyöristyy 10 ps:iin
    const sc_time liian(4, SC_PS);     // pyöristyy nollaan
    std::cout << "jakso " << jakso << " = " << jakso.value()
              << " tarkkuusyksikköä\n"
              << "14 ps -> " << pieni << ", 4 ps -> " << liian << '\n';
    // @loppu tarkkuus

    // @alku laskenta
    // Aika on kokonaisluku tarkkuusyksikköinä, joten summat ovat
    // tarkkoja. Liukulukujen summa ei ole.
    sc_time summa = SC_ZERO_TIME;
    double sekunnit = 0.0;
    for (int i = 0; i < 10; ++i) {
        summa += sc_time(0.1, SC_NS);
        sekunnit += 0.1e-9;
    }
    std::cout << std::setprecision(17)
              << "10 x 0,1 ns: sc_time " << summa
              << (summa == sc_time(1, SC_NS) ? " (tasan)" : "")
              << ", double " << sekunnit << " s\n"
              << std::setprecision(6);
    std::cout << "kerroin: " << jakso * 4 << ", suhde: "
              << sc_time(1, SC_US) / jakso << " jaksoa\n";
    // @loppu laskenta

    // @alku kello
    // Kellon jakso 25 ns, pulssisuhde 40 %, ensimmäinen nouseva reuna
    // 5 ns:n kohdalla.
    sc_clock clk("clk", sc_time(25, SC_NS), 0.4, sc_time(5, SC_NS));
    Reunat reunat("reunat");
    reunat.clk(clk);
    sc_start(100, SC_NS);
    // @loppu kello

    // @alku myohassa
    // Tarkkuutta ei voi enää vaihtaa.
    try {
        sc_set_time_resolution(1, SC_FS);
    } catch (const sc_report& virhe) {
        std::cout << virhe.get_msg_type() << ": " << virhe.get_msg()
                  << '\n';
    }
    // @loppu myohassa
    return 0;
}

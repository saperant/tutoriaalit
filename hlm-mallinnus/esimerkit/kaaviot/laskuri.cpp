// Kirjan ajoituskaavio laskurista: esimerkin 01-laskuri moduulit ja
// herätteet sellaisinaan, ja lisäksi signaalit kirjoitetaan
// VCD-tiedostoon sc_trace-kutsuilla. Esimerkin oma sc_main nimetään
// uudelleen, jotta tämä tiedosto voi määritellä omansa.
#define sc_main esimerkin_sc_main
#include "../01-laskuri/main.cpp"
#undef sc_main

// SystemC kutsuu sc_mainia C-linkityksellä; otsakkeen esittely
// nimettiin yllä uudelleen, joten se esitellään tässä uudestaan.
extern "C" int sc_main(int, char*[]);

int sc_main(int, char*[]) {
    sc_clock clk("clk", 10, SC_NS);
    sc_signal<bool> nollaus("nollaus");
    sc_signal<bool> laske("laske");
    sc_signal<sc_dt::sc_uint<4>> arvo("arvo");
    sc_signal<bool> ylivuoto("ylivuoto");

    Laskuri laskuri("laskuri");
    laskuri.clk(clk);
    laskuri.nollaus(nollaus);
    laskuri.laske(laske);
    laskuri.arvo(arvo);
    laskuri.ylivuoto(ylivuoto);

    Heratteet heratteet("heratteet");
    heratteet.clk(clk);
    heratteet.nollaus(nollaus);
    heratteet.laske(laske);

    sc_trace_file* vcd = sc_create_vcd_trace_file("kaavio");
    vcd->set_time_unit(1, SC_NS);
    sc_trace(vcd, clk, "clk");
    sc_trace(vcd, nollaus, "nollaus");
    sc_trace(vcd, laske, "laske");
    sc_trace(vcd, arvo, "arvo");
    sc_trace(vcd, ylivuoto, "ylivuoto");

    sc_start();
    sc_close_vcd_trace_file(vcd);
    return 0;
}

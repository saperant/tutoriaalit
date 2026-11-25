// Bittitarkat tietotyypit: kokonaisluvut, bittivektorit ja kiinteä pilkku.
#define SC_INCLUDE_FX  // sc_fixed-tyypit eivät tule mukaan ilman tätä
#include <iostream>
#include <systemc>

using namespace sc_dt;

void kokonaisluvut() {
    // @alku kokonaisluvut
    sc_uint<4> laskuri = 15;
    laskuri += 1;                      // kiertää: 4 bittiä
    sc_int<8> lampotila = 127;
    lampotila = lampotila + 1;         // etumerkillinen kierto
    sc_uint<12> rekisteri = 0xA5C;
    std::cout << "sc_uint<4> 15+1 = " << laskuri << '\n'
              << "sc_int<8> 127+1 = " << lampotila << '\n'
              << "kentät: [11:8]=" << rekisteri.range(11, 8)
              << " [7:4]=" << rekisteri.range(7, 4)
              << " bitti 2=" << rekisteri[2] << '\n';
    rekisteri.range(7, 4) = 0x3;       // kentän kirjoitus
    const sc_uint<16> kehys = (sc_uint<4>(0x9), rekisteri);  // liitos
    std::cout << std::hex << "uusi rekisteri 0x" << rekisteri.to_uint()
              << ", kehys 0x" << kehys.to_uint() << std::dec << '\n';
    // Välitulokset lasketaan 64-bittisinä: leveys valitaan sijoitettaessa.
    const sc_uint<8> a = 200, b = 100;
    const sc_uint<9> summa = a + b;
    const sc_uint<8> katkaistu = a + b;
    std::cout << "200+100: 9 bittiä " << summa << ", 8 bittiä "
              << katkaistu << '\n';
    // @loppu kokonaisluvut
}

void bittivektorit() {
    // @alku bittivektorit
    // sc_bv: kaksiarvoiset bitit; sc_lv: neliarvoiset (0, 1, X, Z).
    const sc_bv<8> maski("11110000");
    const sc_bv<8> data("10101010");
    std::cout << "and " << (maski & data) << ", xor " << (maski ^ data)
              << ", pienennys or " << data.or_reduce() << '\n';
    // Ajurit, jotka eivät aja jotakin bittiä, jättävät sen Z-tilaan.
    const sc_lv<4> ajuri1("01ZZ");
    const sc_lv<4> ajuri2("ZZ10");
    const sc_lv<4> ajuri3("1Z1Z");
    std::cout << "ajuri1 " << ajuri1 << ", pelkkiä 0/1-bittejä "
              << ajuri1.is_01() << '\n';
    // Väylän arvo ratkaistaan bitti kerrallaan (resolved logic):
    // Z väistyy, samat arvot säilyvät, eri arvot antavat X:n.
    auto ratkaise = [](const sc_lv<4>& p, const sc_lv<4>& q) {
        sc_lv<4> tulos;
        for (int i = 0; i < 4; ++i) {
            const sc_logic x = p[i], y = q[i];
            tulos[i] = (x == SC_LOGIC_Z)   ? y
                       : (y == SC_LOGIC_Z) ? x
                       : (x == y)          ? x
                                           : SC_LOGIC_X;
        }
        return tulos;
    };
    std::cout << "ratkaistu 1+2: " << ratkaise(ajuri1, ajuri2)
              << ", 1+3: " << ratkaise(ajuri1, ajuri3)
              << ", pelkkä or 1|2: " << (ajuri1 | ajuri2) << '\n';
    // @loppu bittivektorit
}

void kiintopiste() {
    // @alku kiintopiste
    // sc_fixed<W, I, kvantisointi, ylivuoto>: W bittiä, joista I
    // kokonaisosaa (etumerkki mukaan lukien). Q1.7: välillä [-1, 1).
    using Q7_katkaisu = sc_fixed<8, 1, SC_TRN, SC_WRAP>;
    using Q7_pyoristys = sc_fixed<8, 1, SC_RND, SC_SAT>;
    const double arvot[] = {0.3, -0.3, 0.99, 1.5, -2.0};
    for (const double x : arvot) {
        const Q7_katkaisu k = x;
        const Q7_pyoristys p = x;
        std::cout << x << " -> TRN/WRAP " << k << " (" << k.to_bin()
                  << "), RND/SAT " << p << " (" << p.to_bin() << ")\n";
    }
    // Kertolaskun tarkka tulos tarvitsee W1 + W2 bittiä.
    const sc_fixed<8, 1> c = 0.75, d = -0.5;
    const sc_fixed<16, 2> tulo = c * d;
    std::cout << "0,75 * -0,5 = " << tulo << " (" << tulo.to_bin()
              << ")\n";
    // @loppu kiintopiste
}

int sc_main(int, char*[]) {
    kokonaisluvut();
    bittivektorit();
    kiintopiste();
    return 0;
}

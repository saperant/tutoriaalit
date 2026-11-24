// Verilatorin C++-testipenkki suotimelle: lukee sisääntulon ja mallin
// ulostulon tekstitiedostoista (yksi luku riville), ajaa DUT:n kellon
// ja vertaa jokaisen ulostulon. Nopea pitkiin regressioihin: ei
// tapahtumasimulaattoria eikä Python-rajapintaa.
//
// Käyttö: Vfir_suora SYOTE ODOTETTU
// @alku paa
#include <cstdio>
#include <memory>
#include <vector>

#include "Vfir_suora.h"
#include "verilated.h"

static std::vector<int> lue(const char *polku) {
    std::vector<int> arvot;
    std::FILE *f = std::fopen(polku, "r");
    if (!f) return arvot;
    int v;
    while (std::fscanf(f, "%d", &v) == 1) arvot.push_back(v);
    std::fclose(f);
    return arvot;
}

int main(int argc, char **argv) {
    if (argc != 3) {
        std::fprintf(stderr, "käyttö: %s SYOTE ODOTETTU\n", argv[0]);
        return 2;
    }
    const std::vector<int> x = lue(argv[1]), odotettu = lue(argv[2]);
    if (x.empty() || x.size() != odotettu.size()) {
        std::fprintf(stderr, "tiedostot puuttuvat tai eri pituiset\n");
        return 2;
    }
    auto kon = std::make_unique<VerilatedContext>();
    auto dut = std::make_unique<Vfir_suora>(kon.get());

    // Yksi kellojakso: tulot asetetaan, nouseva reuna, laskeva reuna.
    auto jakso = [&] {
        dut->clk = 1;
        dut->eval();
        dut->clk = 0;
        dut->eval();
    };
    dut->nollaus = 1;
    dut->m_ready = 1;
    jakso();
    jakso();
    dut->nollaus = 0;

    size_t sisaan = 0, ulos = 0, erot = 0;
    while (ulos < odotettu.size()) {
        dut->s_valid = sisaan < x.size();
        // Etumerkillinen 12-bittinen arvo Verilatorin rajapinnan
        // etumerkittömään kenttään: ylimmät bitit pois.
        dut->s_data = sisaan < x.size() ? (x[sisaan] & 0xFFF) : 0;
        dut->eval();  // kombinatoriset ulostulot (s_ready) ajan tasalle
        const bool otettu = dut->s_valid && dut->s_ready;
        const bool valmis = dut->m_valid && dut->m_ready;
        // Ulostulo luetaan ennen reunaa, kuten monitori cocotbissa.
        const int y = (int(dut->m_data) ^ 0x800) - 0x800;
        jakso();
        if (otettu) ++sisaan;
        if (valmis) {
            if (y != odotettu[ulos] && ++erot <= 3)
                std::printf("n=%zu: RTL %d, malli %d\n", ulos, y,
                            odotettu[ulos]);
            ++ulos;
        }
    }
    dut->final();
    std::printf("%zu näytettä, %zu eroa\n", ulos, erot);
    return erot ? 1 : 0;
}
// @loppu paa

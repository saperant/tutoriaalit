// Reunojen porrastus: yksi näyte, ylinäytteistys (SSAA) ja
// moninäytteistys (MSAA). Mitataan peiton virhe ja varjostuskerrat.
#include <cmath>
#include <cstdio>
#include <string>
#include <vector>

#include "yhteinen/rasteri.hpp"

const int L = 40, K = 16;
const Vec2 A{1.3, 2.2}, B{8.1, 14.6}, C{38.7, 9.4};  // vastapäivään

// @alku naytteet
// Kuuluuko ruudun piste q kolmioon? Sama testi kuin rasteroinnissa.
bool sisalla(Vec2 q) {
    Kiinto p[3] = {kiintopisteeksi(A), kiintopisteeksi(B),
                   kiintopisteeksi(C)};
    Kiinto k = kiintopisteeksi(q);
    for (int i = 0; i < 3; ++i) {
        Kiinto a = p[(i + 1) % 3], b = p[(i + 2) % 3];
        long long w = reuna(a, b, k);
        if (w < 0 || (w == 0 && !vasen_tai_yla(a, b))) return false;
    }
    return true;
}

// Pikselin peitto: osuuksien keskiarvo annetuissa näytepisteissä.
double peitto(int x, int y, const std::vector<Vec2>& kuvio) {
    int osumia = 0;
    for (Vec2 s : kuvio) osumia += sisalla({x + s.x, y + s.y});
    return double(osumia) / kuvio.size();
}

std::vector<Vec2> ruudukko(int n) {  // n x n tasavälistä näytettä
    std::vector<Vec2> k;
    for (int j = 0; j < n; ++j)
        for (int i = 0; i < n; ++i)
            k.push_back({(i + 0.5) / n, (j + 0.5) / n});
    return k;
}
// Kierretty 4 näytteen kuvio: jokainen rivi ja sarake eri kohdassa.
const std::vector<Vec2> KIERRETTY = {
    {0.375, 0.125}, {0.875, 0.375}, {0.125, 0.625}, {0.625, 0.875}};
// @loppu naytteet

int main() {
    // @alku vertailu
    struct Tapa {
        const char* nimi;
        std::vector<Vec2> kuvio;
        bool kerran;  // MSAA: varjostus kerran pikseliä kohden
    };
    const Tapa tavat[] = {{"ei reunanpeh.", ruudukko(1), false},
                          {"SSAA 2x2", ruudukko(2), false},
                          {"SSAA 4x4", ruudukko(4), false},
                          {"MSAA 4 kierr.", KIERRETTY, true}};
    std::vector<Vec2> tarkka = ruudukko(16);
    std::printf("tapa           virhe ka  virhe max  varjostuksia\n");
    for (const Tapa& t : tavat) {
        double summa = 0, suurin = 0;
        long varjostuksia = 0;
        std::vector<std::string> rivit(K / 2);
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) {
                double p = peitto(x, y, t.kuvio);
                double e = std::abs(p - peitto(x, y, tarkka));
                summa += e;
                suurin = std::max(suurin, e);
                int osumia = int(std::lround(p * t.kuvio.size()));
                varjostuksia += t.kerran ? (osumia > 0) : osumia;
                if (y % 2 == 0)
                    rivit[y / 2] += " .:-=+*#%@"[std::min(9, int(p * 10))];
            }
        std::printf("%-13s  %8.3f  %9.3f  %12ld\n", t.nimi,
                    summa / (L * K), suurin, varjostuksia);
        if (t.kerran || t.kuvio.size() == 1)
            for (const std::string& r : rivit)
                std::printf("  |%s|\n", r.c_str());
    }
    // @loppu vertailu

#ifdef KUVITUS  // make kuvat: neljä tapaa 2 x 2 -asetelmana
    Kuva kuva(2 * L + 1, 2 * K + 1, {90, 90, 90});
    int i = 0;
    for (const Tapa& t : tavat) {
        for (int y = 0; y < K; ++y)
            for (int x = 0; x < L; ++x) {
                double p = peitto(x, y, t.kuvio);  // lineaarinen kirkkaus
                kuva(i % 2 * (L + 1) + x, i / 2 * (K + 1) + y) =
                    koodaa({p, p, p});
            }
        ++i;
    }
    tallenna_ppm(kuva, "11-antialiasointi.ppm");
#endif
}

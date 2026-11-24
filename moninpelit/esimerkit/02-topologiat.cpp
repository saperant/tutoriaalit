// Kolme arkkitehtuuria samoilla pelaajilla: vertaisverkko, asiakas–
// palvelin ja isäntä–asiakas. Lasketaan viestit, lähetyskaista ja
// pahin viive pelaajalta toiselle.
#include <algorithm>
#include <array>
#include <print>

constexpr int N = 4;
// Yhden suunnan viiveet millisekunteina: pelaajat 0–3 ja palvelin (4).
// Pelaaja 3 on muita kauempana.
constexpr std::array<std::array<int, N + 1>, N + 1> VIIVE{{
    {0, 12, 18, 70, 10},
    {12, 0, 15, 65, 9},
    {18, 15, 0, 60, 11},
    {70, 65, 60, 0, 45},
    {10, 9, 11, 45, 0},
}};
constexpr int PALVELIN = N;
constexpr int TIKIT = 60;          // päivitystä sekunnissa
constexpr int TILA_TAVUA = 120;    // yhden pelaajan tila
constexpr int SYOTE_TAVUA = 16;    // yhden tikin syöte

// @alku viive
// Pahin viive, jolla pelaajan i toiminta näkyy pelaajalle j.
int vertais(int i, int j) { return VIIVE[i][j]; }
int palvelimen_kautta(int i, int j) {
    return VIIVE[i][PALVELIN] + VIIVE[PALVELIN][j];
}
int isannan_kautta(int isanta, int i, int j) {
    if (i == isanta || j == isanta) {
        return VIIVE[i][j];  // isäntä on itse "palvelin"
    }
    return VIIVE[i][isanta] + VIIVE[isanta][j];
}
// @loppu viive

template <class F>
int pahin(F viive) {
    int p = 0;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            if (i != j) {
                p = std::max(p, viive(i, j));
            }
        }
    }
    return p;
}

int main() {
    // @alku vertailu
    std::println("{:<16} {:>9} {:>14} {:>10}", "malli", "viestit/s",
                 "lähetys B/s", "pahin ms");
    // Vertaisverkko: jokainen lähettää tilansa kaikille muille.
    std::println("{:<16} {:>9} {:>14} {:>10}", "vertaisverkko",
                 N * (N - 1) * TIKIT, (N - 1) * TILA_TAVUA * TIKIT,
                 pahin(vertais));
    // Palvelin: syöte ylös, koko maailman tila alas.
    std::println("{:<16} {:>9} {:>14} {:>10}", "asiakas–palvelin",
                 2 * N * TIKIT, SYOTE_TAVUA * TIKIT,
                 pahin(palvelimen_kautta));
    // Isäntä (pelaaja 0) lähettää koko tilan kaikille muille.
    std::println("{:<16} {:>9} {:>14} {:>10}", "isäntä 0",
                 2 * (N - 1) * TIKIT, (N - 1) * N * TILA_TAVUA * TIKIT,
                 pahin([](int i, int j) { return isannan_kautta(0, i, j); }));
    // @loppu vertailu
    std::println("isännän viive omaan peliin: {} ms, pelaajan 3: {} ms",
                 isannan_kautta(0, 0, 0), 2 * VIIVE[3][0]);
}

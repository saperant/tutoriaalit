// Tiedon rajaaminen: palvelin lähettää pelaajalle vain ne vastustajat,
// jotka tämä voi nähdä. Seinän läpi näkevä huijausohjelma ei voi näyttää
// tietoa, jota asiakas ei koskaan saanut.
#include <array>
#include <cstdlib>
#include <print>
#include <string>

constexpr std::array<const char*, 9> KARTTA{
    "####################",
    "#P.....#...........#",
    "#......#....b......#",
    "#..a...#...........#",
    "#......####..###...#",
    "#.............#..c.#",
    "#....d........#....#",
    "#.........e...#..f.#",
    "####################",
};

// @alku nakyvyys
// Näkölinja ruudukossa (Bresenhamin suora): estääkö jokin seinä?
bool nakyy(int x0, int y0, int x1, int y1) {
    const int dx = std::abs(x1 - x0), dy = -std::abs(y1 - y0);
    const int sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1;
    int virhe = dx + dy;
    for (;;) {
        if (KARTTA[y0][x0] == '#') {
            return false;
        }
        if (x0 == x1 && y0 == y1) {
            return true;
        }
        const int e2 = 2 * virhe;
        if (e2 >= dy) {
            virhe += dy;
            x0 += sx;
        }
        if (e2 <= dx) {
            virhe += dx;
            y0 += sy;
        }
    }
}
// @loppu nakyvyys

int main() {
    int px = 0, py = 0;
    for (int y = 0; y < 9; ++y) {
        for (int x = 0; KARTTA[y][x]; ++x) {
            if (KARTTA[y][x] == 'P') {
                px = x;
                py = y;
            }
        }
    }
    // @alku suodatus
    std::string lahetetaan;
    int kaikki = 0;
    for (int y = 0; y < 9; ++y) {
        std::string rivi = KARTTA[y];
        for (int x = 0; KARTTA[y][x]; ++x) {
            const char c = KARTTA[y][x];
            if (c >= 'a' && c <= 'z') {
                ++kaikki;
                if (nakyy(px, py, x, y)) {
                    lahetetaan += c;  // vain nämä kulkevat verkossa
                } else {
                    rivi[static_cast<std::size_t>(x)] = '?';
                }
            }
        }
        std::println("{}", rivi);
    }
    // @loppu suodatus
    std::println("vastustajia {}, lähetetään {}: {}", kaikki,
                 lahetetaan.size(), lahetetaan);
}

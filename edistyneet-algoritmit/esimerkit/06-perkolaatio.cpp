// Perkolaatio: ruudukon ruutuja avataan satunnaisessa järjestyksessä,
// kunnes avoimia ruutuja pitkin pääsee ylhäältä alas. Union-find pitää
// kirjaa yhtenäisistä alueista; kaksi virtuaalisolmua edustavat ylä-
// ja alareunaa.
#include <print>
#include <vector>

#include "testaus.hpp"
#include "unionfind.hpp"

// @alku perkolaatio
// Palauttaa avattujen ruutujen osuuden hetkellä, jolloin reunat
// yhdistyvät.
static double kynnys(int n, Satunnainen& s)
{
    const int yla = n * n, ala = n * n + 1;   // virtuaalisolmut
    Yhdisteet alueet{n * n + 2};
    std::vector<bool> auki(static_cast<std::size_t>(n * n), false);
    std::vector<int> jarjestys(static_cast<std::size_t>(n * n));
    for (int i = 0; i < n * n; ++i) {
        jarjestys[static_cast<std::size_t>(i)] = i;
    }
    s.sekoita(jarjestys);

    int avattu = 0;
    for (int ruutu : jarjestys) {
        auki[static_cast<std::size_t>(ruutu)] = true;
        ++avattu;
        int r = ruutu / n, c = ruutu % n;
        if (r == 0) {
            alueet.yhdista(ruutu, yla);
        }
        if (r == n - 1) {
            alueet.yhdista(ruutu, ala);
        }
        const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};
        for (int k = 0; k < 4; ++k) {
            int rr = r + dr[k], cc = c + dc[k];
            if (rr >= 0 && rr < n && cc >= 0 && cc < n
                && auki[static_cast<std::size_t>(rr * n + cc)]) {
                alueet.yhdista(ruutu, rr * n + cc);
            }
        }
        if (alueet.samassa(yla, ala)) {
            break;
        }
    }
    return static_cast<double>(avattu) / (n * n);
}
// @loppu perkolaatio

int main()
{
    // @alku ajo
    Satunnainen s{2026};
    for (int n : {10, 50, 200}) {
        constexpr int kokeita = 40;
        double summa = 0;
        for (int i = 0; i < kokeita; ++i) {
            summa += kynnys(n, s);
        }
        std::println("{:3} x {:<3}: keskimääräinen kynnys {:.3f} "
                     "({} koetta)", n, n, summa / kokeita, kokeita);
    }
    // @loppu ajo
}

// C-testipenkki, joka käyttää koko int-aluetta: tulot ja summat
// ylittävät 32 bittiä.
#include <array>
#include <cstdio>

#include YDIN
#include "vektorit.hpp"

int main() {
    vektorit::Satunnainen satunnainen(42);
    std::array<int, N> a{}, b{};
    for (int i = 0; i < N; ++i) {
        a[i] = satunnainen.vali(-50000, 50000);
        b[i] = satunnainen.vali(-50000, 50000);
    }
    std::printf("tulos %d\n", mac(a.data(), b.data()));
    return 0;
}

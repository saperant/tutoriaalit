// Bittitason apufunktiot muistinvaraajan ja rengaspuskurin käyttöön.
#include <stdbit.h>
#include <stdint.h>
#include <stdio.h>

// @alku kikat
// Pyöristää koon ylöspäin tasaukseen, joka on kahden potenssi.
static size_t tasaa(size_t koko, size_t tasaus)
{
    return (koko + tasaus - 1) & ~(tasaus - 1);
}

static bool kahden_potenssi(uint32_t x)
{
    return x != 0 && (x & (x - 1)) == 0;   // tai stdc_has_single_bit
}
// @loppu kikat

int main(void)
{
    printf("tasaa: %zu %zu %zu\n", tasaa(1, 16), tasaa(16, 16),
           tasaa(17, 16));
    printf("potenssi: %d %d %d\n", kahden_potenssi(64),
           kahden_potenssi(96), kahden_potenssi(0));
    // @alku stdbit
    uint32_t pyynto = 1000;
    printf("bittejä päällä %u, seuraava potenssi %u\n",
           stdc_count_ones(pyynto), stdc_bit_ceil(pyynto));
    printf("alin ykkösbitti %u, pituus %u bittiä\n",
           stdc_trailing_zeros(pyynto), stdc_bit_width(pyynto));
    // Rengaspuskurin indeksi: koko on kahden potenssi, joten
    // jakojäännöksen sijaan riittää maski.
    uint32_t koko = 1024, kirjoitettu = 5000;
    printf("indeksi %u = %u\n", kirjoitettu & (koko - 1),
           kirjoitettu % koko);
    // @loppu stdbit
    return 0;
}

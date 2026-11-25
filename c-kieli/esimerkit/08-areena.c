#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// @alku areena
// Areena (arena, bump allocator): yksi iso varaus, josta jaetaan
// pienempiä paloja peräkkäin. Paloja ei vapauteta yksitellen, vaan koko
// areena vapautetaan kerralla. Sopii, kun monella oliolla on sama elinaika,
// esim. yhden pyynnön käsittely tai jäsennyspuu.
typedef struct {
    unsigned char *muisti;
    size_t koko;
    size_t kaytetty;
} Areena;

bool areena_luo(Areena *a, size_t koko)
{
    a->muisti = malloc(koko);
    a->koko = a->muisti ? koko : 0;
    a->kaytetty = 0;
    return a->muisti != nullptr;
}

// Palauttaa tasatun palan tai nullptr, jos tila loppuu.
void *areena_varaa(Areena *a, size_t koko)
{
    const size_t tasaus = alignof(max_align_t);
    size_t alku = (a->kaytetty + tasaus - 1) & ~(tasaus - 1);
    if (alku > a->koko || koko > a->koko - alku) {
        return nullptr;
    }
    a->kaytetty = alku + koko;
    return a->muisti + alku;
}

void areena_tyhjenna(Areena *a) { a->kaytetty = 0; }

void areena_tuhoa(Areena *a)
{
    free(a->muisti);
    *a = (Areena){};
}
// @loppu areena

// @alku kaytto
typedef struct Sana {
    const char *teksti;
    struct Sana *seuraava;
} Sana;

// Pilkkoo rivin sanoiksi; kaikki muisti tulee areenasta.
Sana *pilko(Areena *a, const char *rivi)
{
    Sana *eka = nullptr;
    Sana **loppu = &eka;
    while (*rivi) {
        size_t n = strcspn(rivi, " ");
        if (n > 0) {
            char *kopio = areena_varaa(a, n + 1);
            Sana *s = areena_varaa(a, sizeof *s);
            if (kopio == nullptr || s == nullptr) {
                return nullptr;
            }
            memcpy(kopio, rivi, n);
            kopio[n] = '\0';
            *s = (Sana){.teksti = kopio};
            *loppu = s;
            loppu = &s->seuraava;
        }
        rivi += n + (rivi[n] == ' ');
    }
    return eka;
}

int main(void)
{
    Areena a;
    if (!areena_luo(&a, 4096)) {
        return EXIT_FAILURE;
    }
    const char *rivit[] = {"GET /index.html HTTP/1.1", "POST /api/tilaus"};
    for (size_t i = 0; i < 2; ++i) {
        int n = 0;
        for (Sana *s = pilko(&a, rivit[i]); s; s = s->seuraava) {
            printf("%s%s", n++ ? " | " : "", s->teksti);
        }
        printf("  (%zu tavua käytössä)\n", a.kaytetty);
        areena_tyhjenna(&a);   // seuraava pyyntö: kaikki kerralla pois
    }
    areena_tuhoa(&a);
}
// @loppu kaytto

// Kaksiulotteinen sivutaulukävely. Vieraan sivutaulut sijaitsevat
// vieraan fyysisessä muistissa, jonka osoitteet on vielä käännettävä
// isännän fyysisiksi laitteiston toisella tasolla (EPT/NPT). Ohjelma
// rakentaa molemmat taulut oikeasti ja laskee muistiviittaukset, kun
// TLB:stä ei löydy osumaa.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { SIVU = 4096, ALKIOT = 512, SIVUJA = 2048 };

// Isännän fyysinen muisti: taulukko 4 KiB:n sivuja.
static uint64_t (*muisti)[ALKIOT];
static unsigned varattu = 1;        // sivu 0 jätetään käyttämättä
static unsigned long viittauksia;

static uint64_t uusi_sivu(void)
{
    if (varattu == SIVUJA) {
        fputs("muisti loppui\n", stderr);
        exit(1);
    }
    return (uint64_t)varattu++ * SIVU;
}

static uint64_t *alkio(uint64_t fyys)
{
    return &muisti[fyys / SIVU][(fyys % SIVU) / 8];
}

// @alku lue
// Jokainen sivutaulun alkion luku on yksi muistiviittaus.
static uint64_t lue(uint64_t hpa)
{
    viittauksia++;
    return *alkio(hpa);
}
// @loppu lue

static unsigned indeksi(uint64_t osoite, int taso)
{
    return (unsigned)(osoite >> (12 + 9 * taso)) & (ALKIOT - 1);
}

// Yleinen radix-sivutaulu: lisää kuvauksen virt -> fyys tauluun, jonka
// juuri on osoitteessa juuri. kirj kertoo, miten taulun sivuun
// kirjoitetaan (isännän muistiin suoraan tai vieraan muistin kautta).
typedef uint64_t *kirjoitin(uint64_t osoite);

static void kuvaa(uint64_t juuri, int tasoja, uint64_t virt,
                  uint64_t fyys, kirjoitin *kirj,
                  uint64_t (*uusi)(void))
{
    uint64_t taulu = juuri;
    for (int t = tasoja - 1; t > 0; t--) {
        uint64_t *pte = kirj(taulu + 8 * indeksi(virt, t));
        if (*pte == 0)
            *pte = uusi() | 1;
        taulu = *pte & ~(uint64_t)(SIVU - 1);
    }
    *kirj(taulu + 8 * indeksi(virt, 0)) = fyys | 1;
}

// Isännän EPT: vieraan fyysinen osoite -> isännän fyysinen osoite.
static uint64_t ept_juuri;
static int ept_tasoja;

static uint64_t *isannan_muisti(uint64_t hpa) { return alkio(hpa); }

// @alku kavely
static uint64_t ept_kaanna(uint64_t gpa)
{
    uint64_t taulu = ept_juuri;
    for (int t = ept_tasoja - 1; t >= 0; t--)
        taulu = lue(taulu + 8 * indeksi(gpa, t)) & ~(uint64_t)(SIVU - 1);
    return taulu | (gpa & (SIVU - 1));
}

// Vieraan sivutaulun kävely: jokainen vieraan taulun osoite on
// vieraan fyysinen osoite, joten se käännetään ensin EPT:llä.
static uint64_t kaanna(uint64_t gva, uint64_t vieras_juuri, int tasoja)
{
    uint64_t taulu = vieras_juuri;                 // GPA
    for (int t = tasoja - 1; t >= 0; t--) {
        uint64_t hpa = ept_kaanna(taulu + 8 * indeksi(gva, t));
        taulu = lue(hpa) & ~(uint64_t)(SIVU - 1);  // seuraava GPA
    }
    return ept_kaanna(taulu | (gva & (SIVU - 1)));
}
// @loppu kavely

// Vieraan fyysinen muisti on isännän sivuja, joten vieraan sivutaulun
// kirjoitus kulkee EPT:n kautta (ei lasketa: rakentaminen ei ole
// mitattava kävely).
static uint64_t vieras_seuraava = 0x100000;
static uint64_t uusi_vieraan_sivu(void)
{
    uint64_t gpa = vieras_seuraava;
    vieras_seuraava += SIVU;
    kuvaa(ept_juuri, ept_tasoja, gpa, uusi_sivu(), isannan_muisti,
          uusi_sivu);
    return gpa;
}

static uint64_t *vieraan_muisti(uint64_t gpa)
{
    unsigned long ennen = viittauksia;
    uint64_t *p = alkio(ept_kaanna(gpa));
    viittauksia = ennen;
    return p;
}

static void mittaa(int vieras, int isanta)
{
    varattu = 1;
    vieras_seuraava = 0x100000;
    for (unsigned i = 0; i < SIVUJA; i++)
        for (unsigned j = 0; j < ALKIOT; j++)
            muisti[i][j] = 0;
    ept_tasoja = isanta;
    ept_juuri = uusi_sivu();

    uint64_t juuri = uusi_vieraan_sivu();
    uint64_t gva = 0x7f12345000;
    uint64_t data = uusi_vieraan_sivu();
    kuvaa(juuri, vieras, gva, data, vieraan_muisti, uusi_vieraan_sivu);

    viittauksia = 0;
    uint64_t hpa = kaanna(gva + 0x2a, juuri, vieras);
    unsigned long kaava = (unsigned long)((vieras + 1) * (isanta + 1) - 1);
    printf("%d + %d tasoa: %2lu viittausta (kaava %2lu), "
           "natiivisti %d, varjotaulu %d\n",
           vieras, isanta, viittauksia, kaava, vieras, vieras);
    if (hpa % SIVU != 0x2a)
        puts("  VIRHE: sivun sisäinen siirtymä hukkui");
}

int main(void)
{
    muisti = calloc(SIVUJA, sizeof *muisti);
    if (muisti == NULL)
        return 1;
    mittaa(2, 2);
    mittaa(4, 4);      // x86-64:n tavallinen sivutus
    mittaa(5, 5);      // 5-tasoinen sivutus (LA57)
    free(muisti);
    return 0;
}

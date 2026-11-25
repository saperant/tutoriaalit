// Rengaspuskuri: kiinteän kokoinen jono, esimerkiksi UART-ajurin
// vastaanottopuskuri. Kaksi vapaasti juoksevaa indeksiä: kirjoittaja
// kasvattaa toista ja lukija toista. Täysi ja tyhjä erottuvat, koska
// indeksien erotus on täyttöaste.
#include <stdint.h>
#include <stdio.h>

// @alku rengas
enum { KOKO = 8 };              // kahden potenssi: indeksi & (KOKO - 1)
static_assert((KOKO & (KOKO - 1)) == 0, "KOKO on kahden potenssi");

typedef struct {
    uint8_t data[KOKO];
    uint32_t kirjoitettu;       // kasvaa vain kirjoittajalla
    uint32_t luettu;            // kasvaa vain lukijalla
} Rengas;

static uint32_t rengas_taytto(const Rengas *r)
{
    return r->kirjoitettu - r->luettu;   // etumerkitön: oikein myös
}                                        // indeksien kiertäessä ympäri

static bool rengas_kirjoita(Rengas *r, uint8_t tavu)
{
    if (rengas_taytto(r) == KOKO) {
        return false;                    // täynnä
    }
    r->data[r->kirjoitettu & (KOKO - 1)] = tavu;
    r->kirjoitettu++;
    return true;
}

static bool rengas_lue(Rengas *r, uint8_t *tavu)
{
    if (rengas_taytto(r) == 0) {
        return false;                    // tyhjä
    }
    *tavu = r->data[r->luettu & (KOKO - 1)];
    r->luettu++;
    return true;
}
// @loppu rengas

// Puskurin sisältö ja indeksien paikat yhdellä rivillä: vapaa paikka
// on -, välilyönti _. Kirjan kuva kolmesta tilasta piirretään näistä
// riveistä (kaaviot/tee.py).
static void nayta(const Rengas *r, const char *tila)
{
    printf("%s [", tila);
    for (uint32_t i = 0; i < KOKO; i++) {
        // Paikka on käytössä, jos sen etäisyys lukuindeksistä on
        // pienempi kuin täyttö.
        bool kaytossa = ((i - r->luettu) & (KOKO - 1)) < rengas_taytto(r);
        char merkki = !kaytossa ? '-'
                      : r->data[i] == ' ' ? '_' : (char)r->data[i];
        printf("%c%s", merkki, i + 1 < KOKO ? " " : "");
    }
    printf("] luku %u, kirjoitus %u, täyttö %u\n", r->luettu & (KOKO - 1),
           r->kirjoitettu & (KOKO - 1), rengas_taytto(r));
}

int main(void)
{
    // Indeksit aloitetaan lähellä 2^32:ta, jotta niiden ympärikierto
    // tulee testatuksi heti eikä vasta tuntien käytön jälkeen.
    Rengas r = {.kirjoitettu = UINT32_MAX - 4, .luettu = UINT32_MAX - 4};
    const char *viesti = "PING 192.0.2.1\n";
    size_t lahetetty = 0;
    int odotuksia = 0;
    char vastaanotettu[64];
    size_t vastaanotetut = 0;
    bool kiertanyt_naytetty = false, taysi_naytetty = false;
    nayta(&r, "tyhjä:    ");

    // Kirjoittaja tuottaa 4 tavua kierroksessa, lukija ehtii lukea 2.
    for (int kierros = 0; viesti[lahetetty] != '\0' || rengas_taytto(&r);
         kierros++) {
        for (int i = 0; i < 4 && viesti[lahetetty] != '\0'; i++) {
            if (!rengas_kirjoita(&r, (uint8_t)viesti[lahetetty])) {
                odotuksia++;
                break;          // kirjoittaja odottaa seuraavaa kierrosta
            }
            lahetetty++;
        }
        if (!taysi_naytetty && rengas_taytto(&r) == KOKO) {
            nayta(&r, "täysi:    ");
            taysi_naytetty = true;
        } else if (!kiertanyt_naytetty && (r.kirjoitettu & (KOKO - 1))
                                          < (r.luettu & (KOKO - 1))) {
            nayta(&r, "kiertänyt:");
            kiertanyt_naytetty = true;
        }
        uint8_t tavu;
        for (int i = 0; i < 2 && rengas_lue(&r, &tavu); i++) {
            vastaanotettu[vastaanotetut++] = (char)tavu;
        }
        printf("kierros %2d: täyttö %u/%d\n", kierros, rengas_taytto(&r),
               KOKO);
    }
    vastaanotettu[vastaanotetut] = '\0';
    printf("vastaanotettu: %s", vastaanotettu);
    printf("puskuri täynnä %d kertaa, indeksit kiersivät: %s\n",
           odotuksia, r.luettu < UINT32_MAX - 4 ? "kyllä" : "ei");
    return 0;
}

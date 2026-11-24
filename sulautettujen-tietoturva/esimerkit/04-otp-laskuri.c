// Monotoninen laskuri kertakäyttöisessä OTP-muistissa (eFuse).
// OTP-bitin voi polttaa 0 -> 1 mutta ei palauttaa. Laskurin arvo on
// poltettujen bittien määrä (termometrikoodi), joten arvo voi vain
// kasvaa: vanhaa laiteohjelmistoa ei voi enää hyväksyä.
#include <stdint.h>
#include <stdio.h>

typedef struct {
    uint32_t sanat[2];          // 64 bittiä: versiot 0–64
} otp_t;

// @alku polta
// Laitteisto toteuttaa vain TAI-operaation: nollaus ei ole mahdollista.
static void otp_kirjoita(otp_t *otp, int sana, uint32_t arvo) {
    otp->sanat[sana] |= arvo;
}

static int laskuri(const otp_t *otp) {
    return __builtin_popcount(otp->sanat[0])
           + __builtin_popcount(otp->sanat[1]);
}

// Nostaa laskurin arvoon uusi polttamalla puuttuvat bitit.
static void nosta(otp_t *otp, int uusi) {
    for (int i = laskuri(otp); i < uusi && i < 64; i++) {
        otp_kirjoita(otp, i / 32, 1u << (i % 32));
    }
}
// @loppu polta

// @alku hyvaksy
static const char *arvioi(const otp_t *otp, int versio) {
    return versio >= laskuri(otp) ? "hyväksytään" : "hylätään";
}
// @loppu hyvaksy

int main(void) {
    otp_t otp = {{0, 0}};
    nosta(&otp, 3);
    printf("Laskuri %d, sana 0x%08x\n", laskuri(&otp), otp.sanat[0]);
    for (int v = 1; v <= 4; v++) {
        printf("  versio %d: %s\n", v, arvioi(&otp, v));
    }

    // Hyökkääjä yrittää palauttaa laskurin kirjoittamalla nollan.
    otp_kirjoita(&otp, 0, 0);
    printf("Nollausyrityksen jälkeen laskuri %d\n", laskuri(&otp));

    // Päivitys versioon 35 polttaa bittejä myös toisesta sanasta.
    nosta(&otp, 35);
    printf("Laskuri %d, sanat 0x%08x 0x%08x\n", laskuri(&otp),
           otp.sanat[0], otp.sanat[1]);
    printf("Jäljellä %d nostoa\n", 64 - laskuri(&otp));
    return 0;
}

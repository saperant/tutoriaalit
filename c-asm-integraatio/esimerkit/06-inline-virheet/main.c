// Kaksi tavallista inline-assemblyn virhettä. Kumpikin "toimii"
// -O0:lla ja hajoaa -O2:lla, koska optimoija luottaa siihen, mitä
// rajoitteet lupaavat.
#include <stdio.h>

// @alku muisti
// asm kirjoittaa muistiin osoittimen kautta. Ilman "memory"-
// clobberia kääntäjä ei tiedä, että *p muuttui, ja palauttaa
// arvon, jonka se muistaa ennen asm-lausetta.
#if defined(__x86_64__)
#define KIRJOITA_5 "movl $5, (%0)"
#define KIRJOITA_5_SOTKEE
#else
#define KIRJOITA_5 "li t0, 5\n\tsw t0, 0(%0)"
#define KIRJOITA_5_SOTKEE "t0",
#endif

__attribute__((noipa)) static int ilman_memorya(void) {
    int x = 1;
    __asm__(KIRJOITA_5 : : "r"(&x) : KIRJOITA_5_SOTKEE "cc");
    return x;
}

__attribute__((noipa)) static int memoryn_kanssa(void) {
    int x = 1;
    __asm__(KIRJOITA_5 : : "r"(&x) : KIRJOITA_5_SOTKEE "cc", "memory");
    return x;
}
// @loppu muisti

// @alku aikainen
// t = a + 2 * b. Tuloste %0 kirjoitetaan ensimmäisellä käskyllä,
// ennen kuin syöte %2 on luettu. Ilman &-merkkiä kääntäjä saa antaa
// tulosteelle saman rekisterin kuin b:lle, ja b ylikirjoittuu.
#if defined(__x86_64__)
#define A_PLUS_2B "mov %1, %0\n\tadd %2, %0\n\tadd %2, %0"
#else
#define A_PLUS_2B "mv %0, %1\n\tadd %0, %0, %2\n\tadd %0, %0, %2"
#endif

// Parametrien järjestys on valittu niin, että b on samassa
// rekisterissä, johon tulos lopuksi tarvitaan (tulosta-funktion
// ensimmäinen parametri).
__attribute__((noipa)) static long tulosta(long t, const char *nimi);

__attribute__((noipa)) static long ilman_et(long b, long a) {
    long t;
    __asm__(A_PLUS_2B : "=r"(t) : "r"(a), "r"(b));
    return tulosta(t, "ilman &");
}

__attribute__((noipa)) static long etin_kanssa(long b, long a) {
    long t;
    __asm__(A_PLUS_2B : "=&r"(t) : "r"(a), "r"(b));
    return tulosta(t, "&:n kanssa");
}
// @loppu aikainen

static long tulosta(long t, const char *nimi) {
    printf("  %-11s %ld\n", nimi, t);
    return t;
}

int main(void) {
    printf("x = 1, asm kirjoittaa 5:\n");
    printf("  ilman memorya   %d\n", ilman_memorya());
    printf("  memoryn kanssa  %d\n", memoryn_kanssa());
    printf("a = 1, b = 10, a + 2b:\n");
    ilman_et(10, 1);
    etin_kanssa(10, 1);
    return 0;
}

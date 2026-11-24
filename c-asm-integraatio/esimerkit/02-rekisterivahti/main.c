// Rekisterivahti: tarkistaa, noudattaako funktio kutsusopimusta, ja
// näyttää, mitä sopimuksen rikkominen tekee kutsujalle.
#include <stdio.h>
#include <string.h>

long vahdi(long (*f)(long), long x, unsigned *muuttuneet);
long kasvata_oikein(long x);
long kasvata_rikki(long x);

#if defined(__x86_64__)
static const char *const rekisterit[] = {"rbx", "rbp", "r12",
                                         "r13", "r14", "r15"};
#else
static const char *const rekisterit[] = {"s0", "s1", "s2",  "s3",
                                         "s4", "s5", "s6",  "s7",
                                         "s8", "s9", "s10", "s11"};
#endif
enum { REKISTEREITA = sizeof rekisterit / sizeof rekisterit[0] };

static void tutki(const char *nimi, long (*f)(long)) {
    unsigned muuttuneet = 0;
    long tulos = vahdi(f, 41, &muuttuneet);
    printf("%-15s tulos %ld, muuttuneet:", nimi, tulos);
    for (int i = 0; i < REKISTEREITA; i++) {
        if (muuttuneet & (1u << i)) {
            printf(" %s", rekisterit[i]);
        }
    }
    printf("%s\n", muuttuneet ? "" : " ei yhtään");
}

// @alku seuraus
// Kääntäjä pitää a:n kutsun yli säilyvässä rekisterissä (rbx, s0),
// koska se luottaa sopimukseen. noipa estää GCC:tä optimoimasta
// funktiota kutsukohdan vakioiden mukaan.
__attribute__((noipa)) static long laske(long (*f)(long), long a) {
    long b = 3 * a;
    long c = f(a);
    return b + c;
}
// @loppu seuraus

static long kasvata_c(long x) { return x + 1; }

#if defined(__x86_64__)
// @alku tasaus
#include <immintrin.h>

void kutsu_tasaamatta(void (*f)(void));

// Kääntäjä saa olettaa, että pino on funktion alussa sopimuksen
// mukaisesti tasattu, ja tallentaa 16 tavun vektorin pinoon käskyllä,
// joka vaatii 16 tavun tasauksen.
__attribute__((noipa)) static void kayttaa_vektoria(void) {
    volatile __m128i v = _mm_set1_epi32(7);
    (void)v;
}
// @loppu tasaus
#endif

int main(int argc, char **argv) {
#if defined(__x86_64__)
    if (argc > 1 && strcmp(argv[1], "tasaus") == 0) {
        kutsu_tasaamatta(kayttaa_vektoria);
        printf("ei kaatunut\n");
        return 0;
    }
#else
    (void)argc;
    (void)argv;
#endif
    tutki("kasvata_c", kasvata_c);
    tutki("kasvata_oikein", kasvata_oikein);
    tutki("kasvata_rikki", kasvata_rikki);
    // 3 * 5 + (5 + 1) = 21
    printf("laske(kasvata_oikein, 5) = %ld\n", laske(kasvata_oikein, 5));
    printf("laske(kasvata_rikki, 5)  = %ld\n", laske(kasvata_rikki, 5));
    return 0;
}

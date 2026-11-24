// Rajapinta: prototyyppi otsakkeessa, toteutus assemblyllä ja
// C-viitetoteutus, johon assembly-versiota verrataan.
#include <stdio.h>

#include "funktio.h"

static size_t laske_c(const char *s, char c) {
    size_t n = 0;
    for (; *s != '\0'; s++) {
        n += *s == c;
    }
    return n;
}

int main(void) {
    // @alku testit
    // Tavu 0xC3 on UTF-8:ssa ä:n ja ö:n ensimmäinen tavu. Se on
    // x86-64:llä negatiivinen (char on etumerkillinen) ja RISC-V:llä
    // positiivinen (char on etumerkitön).
    const struct { const char *s; char c; } testit[] = {
        {"", 'a'}, {"banaani", 'a'}, {"aaaa", 'a'}, {"abc", 'x'},
        {"hääyö", (char)0xC3},
    };
    int virheet = 0;
    for (size_t i = 0; i < sizeof testit / sizeof testit[0]; i++) {
        size_t a = laske(testit[i].s, testit[i].c);
        size_t c = laske_c(testit[i].s, testit[i].c);
        printf("tapaus %zu: assembly %zu, C %zu\n", i, a, c);
        virheet += a != c;
    }
    printf("%s\n", virheet == 0 ? "kaikki samat" : "EROJA");
    // @loppu testit
    return virheet != 0;
}

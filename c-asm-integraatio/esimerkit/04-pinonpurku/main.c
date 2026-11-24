// Pinonpurku assembly-funktion läpi. Purkaja (_Unwind_Backtrace) on
// sama, jota C++:n poikkeukset, debuggerit ja profiloijat käyttävät.
// Se tarvitsee jokaisesta kehyksestä purkutiedot (.eh_frame), jotka
// assembly-funktiolle syntyvät vain .cfi-direktiiveistä.
#include <stdint.h>
#include <stdio.h>
#include <unwind.h>

long kutsu_kautta(long (*f)(long), long x);
static long syvin(long x);
int main(void);

// @alku purku
struct tila {
    int main_loytyi;
    int kehyksia;
};

static _Unwind_Reason_Code kehys(struct _Unwind_Context *k, void *arg) {
    struct tila *t = arg;
    uintptr_t alku = _Unwind_GetRegionStart(k);
    const char *nimi = "?";
    if (alku == (uintptr_t)syvin) {
        nimi = "syvin";
    } else if (alku == (uintptr_t)kutsu_kautta) {
        nimi = "kutsu_kautta";
    } else if (alku == (uintptr_t)main) {
        nimi = "main";
        t->main_loytyi = 1;
    }
    printf("  %s\n", nimi);
    // Varmuuden vuoksi enintään kymmenen kehystä.
    if (++t->kehyksia == 10) {
        return _URC_END_OF_STACK;
    }
    return t->main_loytyi ? _URC_END_OF_STACK : _URC_NO_REASON;
}

__attribute__((noinline)) static long syvin(long x) {
    struct tila t = {0};
    _Unwind_Backtrace(kehys, &t);
    printf("main tavoitettu: %s\n", t.main_loytyi ? "kyllä" : "ei");
    return x + 1;
}
// @loppu purku

int main(void) {
    printf("kehykset sisimmästä ulospäin:\n");
    return kutsu_kautta(syvin, 41) == 42 ? 0 : 1;
}

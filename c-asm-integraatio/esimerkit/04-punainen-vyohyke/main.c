// x86-64:n punainen vyöhyke: lehtifunktio saa pitää paikallisia
// muuttujia 128 tavun alueella pino-osoittimen alapuolella siirtämättä
// osoitinta. Inline-assembly, joka työntää pinoon, kirjoittaa niiden
// päälle. Vain x86-64: RISC-V:n kutsusopimuksessa vyöhykettä ei ole.
#include <stdio.h>

// @alku rikki
// pushfq/pop on tavallinen tapa lukea lippurekisteri. Kääntäjä ei
// tiedä, että lause käyttää pinoa.
__attribute__((noipa)) static long liput_rikki(long x) {
    volatile long paikallinen = x;      // muistissa: -8(%rsp)
    unsigned long liput;
    __asm__ volatile("pushfq\n\tpop %0" : "=r"(liput));
    (void)liput;
    return paikallinen;                 // pushfq kirjoitti tämän päälle
}
// @loppu rikki

// @alku ohitus
// Korjaus: siirry vyöhykkeen ohi ennen työntöä ja palaa takaisin.
// lea ei muuta lippuja, toisin kuin sub ja add.
__attribute__((noipa)) static long liput_ohittaen(long x) {
    volatile long paikallinen = x;
    unsigned long liput;
    __asm__ volatile("lea -128(%%rsp), %%rsp\n\t"
                     "pushfq\n\tpop %0\n\t"
                     "lea 128(%%rsp), %%rsp" : "=r"(liput));
    (void)liput;
    return paikallinen;
}
// @loppu ohitus

int main(void) {
    long a = liput_rikki(5);
    long b = liput_ohittaen(5);
    printf("työntö vyöhykkeelle: 5 -> %s\n", a == 5 ? "5" : "muuttui");
    printf("vyöhykkeen ohi:      5 -> %ld\n", b);
#ifdef EI_VYOHYKETTA
    return (a == 5 && b == 5) ? 0 : 1;
#else
    return (a != 5 && b == 5) ? 0 : 1;
#endif
}

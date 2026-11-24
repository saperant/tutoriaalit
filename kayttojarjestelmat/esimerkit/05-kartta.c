// Prosessin muistikartta /proc/self/maps: kunkin alueen oikeudet ja
// alkuperä. Osoitteet vaihtelevat ajosta toiseen (ASLR), joten
// tulostetaan vain oikeudet ja alueen tyyppi.
#define _GNU_SOURCE
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>

#include "tarkista.h"

static const char vakio[] = "vain luettava";
static int muuttuja = 42;

// @alku etsi
// Etsii alueen, johon osoite kuuluu, ja tulostaa sen oikeudet.
static void alue(const char *nimi, uintptr_t a) {
    char ohjelma[4096];
    ssize_t n = TARKISTA(readlink("/proc/self/exe", ohjelma,
                                  sizeof ohjelma - 1));
    ohjelma[n] = '\0';
    FILE *f = fopen("/proc/self/maps", "r");
    if (f == nullptr) {
        perror("maps");
        exit(EXIT_FAILURE);
    }
    char rivi[4096];
    while (fgets(rivi, sizeof rivi, f)) {
        uintptr_t alku, loppu;
        char oikeudet[5];
        int kohta = 0;
        if (sscanf(rivi, "%lx-%lx %4s %*s %*s %*s %n", &alku, &loppu,
                   oikeudet, &kohta) < 3 || a < alku || a >= loppu) {
            continue;
        }
        rivi[strcspn(rivi, "\n")] = '\0';
        const char *polku = rivi + kohta;
        printf("%-18s %s  %s\n", nimi, oikeudet,
               strcmp(polku, ohjelma) == 0 ? "ohjelmatiedosto"
               : *polku ? polku : "anonyymi");
        break;
    }
    fclose(f);
}
// @loppu etsi

int main(void) {
    // @alku kartta
    alue("main (koodi)", (uintptr_t)main);
    alue("vakio (.rodata)", (uintptr_t)vakio);
    alue("muuttuja (.data)", (uintptr_t)&muuttuja);

    const size_t sivu = (size_t)sysconf(_SC_PAGESIZE);
    char *p = TARKISTA_MAP(mmap(nullptr, sivu, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    alue("mmap", (uintptr_t)p);
    TARKISTA(mprotect(p, sivu, PROT_READ));
    alue("mprotect", (uintptr_t)p);
    TARKISTA(munmap(p, sivu));
    // @loppu kartta
    return 0;
}

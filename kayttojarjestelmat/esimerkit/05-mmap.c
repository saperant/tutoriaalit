// mmap varaa osoiteavaruutta, ei muistia: sivut syntyvät vasta
// ensimmäisessä kosketuksessa sivuvirheen kautta.
#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>

#include "tarkista.h"

// @alku apu
static long sivuvirheet(void) {
    struct rusage r;
    TARKISTA(getrusage(RUSAGE_SELF, &r));
    return r.ru_minflt;                  // ilman levyhakua ratkaistut
}

// mincore kertoo sivu kerrallaan, onko sivu fyysisessä muistissa.
static size_t muistissa(void *p, size_t koko, size_t sivu) {
    unsigned char v[1024];
    TARKISTA(mincore(p, koko, v));
    size_t n = 0;
    for (size_t i = 0; i < koko / sivu; i++) {
        n += v[i] & 1;
    }
    return n;
}
// @loppu apu

int main(void) {
    // @alku anonyymi
    const size_t sivu = (size_t)sysconf(_SC_PAGESIZE);
    const size_t sivuja = 512, koko = sivuja * sivu;
    char *p = TARKISTA_MAP(mmap(nullptr, koko, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    TARKISTA(madvise(p, koko, MADV_NOHUGEPAGE));   // vain 4 KiB:n sivuja
    printf("varattu %zu sivua, muistissa %zu\n", sivuja,
           muistissa(p, koko, sivu));

    long ennen = sivuvirheet();
    for (size_t i = 0; i < sivuja; i += 2) {
        p[i * sivu] = 1;                 // joka toinen sivu
    }
    long virheita = sivuvirheet() - ennen;
    printf("kosketettu %zu sivua, muistissa %zu\n", sivuja / 2,
           muistissa(p, koko, sivu));
    printf("sivuvirheitä vähintään %zu: %s\n", sivuja / 2,
           virheita >= (long)(sivuja / 2) ? "kyllä" : "ei");

    TARKISTA(madvise(p, koko, MADV_DONTNEED));     // palautetaan ytimelle
    printf("MADV_DONTNEED: muistissa %zu", muistissa(p, koko, sivu));
    printf(", p[0] = %d\n", p[0]);     // uusi nollasivu
    TARKISTA(munmap(p, koko));
    // @loppu anonyymi

    // @alku tiedosto
    int fd = TARKISTA(open("data.bin", O_RDWR | O_CREAT | O_TRUNC, 0644));
    TARKISTA(ftruncate(fd, (off_t)sivu));
    char *jaettu = TARKISTA_MAP(mmap(nullptr, sivu, PROT_READ | PROT_WRITE,
                                     MAP_SHARED, fd, 0));
    char *oma = TARKISTA_MAP(mmap(nullptr, sivu, PROT_READ | PROT_WRITE,
                                  MAP_PRIVATE, fd, 0));
    strcpy(jaettu, "jaettu kirjoitus");
    printf("yksityinen näkee: \"%s\"\n", oma);   // ei vielä omaa kopiota
    strcpy(oma, "yksityinen");       // copy-on-write: oma kopio sivusta
    TARKISTA(msync(jaettu, sivu, MS_SYNC));

    char luettu[32] = {};
    TARKISTA(pread(fd, luettu, sizeof luettu - 1, 0));
    printf("tiedostossa: \"%s\"\n", luettu);
    printf("yksityinen: \"%s\"\n", oma);
    TARKISTA(munmap(jaettu, sivu));
    TARKISTA(munmap(oma, sivu));
    TARKISTA(close(fd));
    // @loppu tiedosto
    return 0;
}

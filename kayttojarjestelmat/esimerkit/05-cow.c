// fork ei kopioi muistia heti: lapsi ja vanhempi jakavat sivut, ja
// kopio syntyy vasta kirjoitettaessa (copy-on-write).
#define _GNU_SOURCE
#include <sys/mman.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

#include "tarkista.h"

static long sivuvirheet(void) {
    struct rusage r;
    TARKISTA(getrusage(RUSAGE_SELF, &r));
    return r.ru_minflt;
}

int main(void) {
    // @alku cow
    const size_t sivu = (size_t)sysconf(_SC_PAGESIZE);
    const size_t sivuja = 1000, koko = sivuja * sivu;
    unsigned char *p = TARKISTA_MAP(mmap(nullptr, koko,
        PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    TARKISTA(madvise(p, koko, MADV_NOHUGEPAGE));
    memset(p, 'v', koko);                // vanhempi koskettaa kaiken

    fflush(stdout);
    pid_t pid = TARKISTA(fork());
    if (pid == 0) {
        long a = sivuvirheet();
        unsigned summa = 0;
        for (size_t i = 0; i < koko; i += sivu) {
            summa += p[i];               // luku: sivut jaettuja
        }
        long b = sivuvirheet();
        for (size_t i = 0; i < koko; i += sivu) {
            p[i] = 'l';                  // kirjoitus: kopio joka sivusta
        }
        long c = sivuvirheet();
        printf("lapsi luki %zu sivua (summa %u)\n", sivuja, summa);
        printf("kirjoitus aiheutti vähintään %zu sivuvirhettä: %s\n",
               sivuja, c - b >= (long)sivuja ? "kyllä" : "ei");
        printf("luku aiheutti vähemmän sivuvirheitä: %s\n",
               b - a < c - b ? "kyllä" : "ei");
        fflush(stdout);
        _exit(0);
    }
    TARKISTA(waitpid(pid, nullptr, 0));
    bool ennallaan = true;
    for (size_t i = 0; i < koko; i++) {
        ennallaan = ennallaan && p[i] == 'v';
    }
    printf("vanhemman sivut ennallaan: %s\n", ennallaan ? "kyllä" : "ei");
    TARKISTA(munmap(p, koko));
    // @loppu cow
    return 0;
}

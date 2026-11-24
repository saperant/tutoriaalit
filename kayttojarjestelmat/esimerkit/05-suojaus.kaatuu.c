// Kirjoitus vain luettavaksi suojattuun sivuun: MMU nostaa
// sivuvirheen, ydin toteaa oikeuden puuttuvan ja lähettää SIGSEGV:n.
#define _GNU_SOURCE
#include <sys/mman.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku suojaus
    const size_t sivu = (size_t)sysconf(_SC_PAGESIZE);
    char *p = TARKISTA_MAP(mmap(nullptr, sivu, PROT_READ | PROT_WRITE,
                                MAP_PRIVATE | MAP_ANONYMOUS, -1, 0));
    p[0] = 'a';                          // sallittu
    TARKISTA(mprotect(p, sivu, PROT_READ));
    printf("luku onnistuu: %c\n", p[0]);
    fflush(stdout);
    p[0] = 'b';                          // SIGSEGV
    // @loppu suojaus
    TARKISTA(munmap(p, sivu));
    return 0;
}

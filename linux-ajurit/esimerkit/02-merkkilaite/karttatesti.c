// Testaa kartta-ajurin: kirjoittaa sivuun mmap-kuvauksen kautta ja lukee
// saman sisällön read-kutsulla ja toisen kuvauksen kautta.

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static const char *tulos(void *osoite)
{
    return osoite == MAP_FAILED ? strerror(errno) : "ok";
}

int main(void)
{
    long sivu = sysconf(_SC_PAGESIZE);
    int fd = open("/dev/kartta", O_RDWR);
    if (fd < 0) {
        perror("/dev/kartta");
        return 1;
    }

    // @alku kuvaus
    char *kuvaus = mmap(NULL, (size_t)sivu, PROT_READ | PROT_WRITE,
                        MAP_SHARED, fd, 0);
    printf("mmap: %s\n", tulos(kuvaus));
    strcpy(kuvaus, "kirjoitettu ilman jarjestelmakutsua");

    char puskuri[64] = "";
    ssize_t n = pread(fd, puskuri, sizeof puskuri - 1, 0);
    printf("read: %zd tavua, alussa \"%s\"\n", n, puskuri);

    char *toinen = mmap(NULL, (size_t)sivu, PROT_READ, MAP_SHARED, fd, 0);
    printf("toinen kuvaus: \"%s\", %s osoite\n", toinen,
           toinen == kuvaus ? "sama" : "eri");
    // @loppu kuvaus

    printf("kaksi sivua: %s\n",
           tulos(mmap(NULL, 2 * (size_t)sivu, PROT_READ, MAP_SHARED, fd,
                      0)));
    printf("toinen sivu: %s\n",
           tulos(mmap(NULL, (size_t)sivu, PROT_READ, MAP_SHARED, fd,
                      sivu)));
    munmap(toinen, (size_t)sivu);
    munmap(kuvaus, (size_t)sivu);
    close(fd);
    return 0;
}

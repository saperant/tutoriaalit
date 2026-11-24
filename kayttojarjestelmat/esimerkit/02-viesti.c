// Pieni ohjelma, jonka järjestelmäkutsut jäljitetään straceliä.
#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku viesti
    int fd = TARKISTA(open("viesti.txt",
                           O_WRONLY | O_CREAT | O_TRUNC, 0644));
    TARKISTA(write(fd, "hei ytimelle\n", 13));
    TARKISTA(close(fd));

    char puskuri[64];
    fd = TARKISTA(open("viesti.txt", O_RDONLY));
    ssize_t n = TARKISTA(read(fd, puskuri, sizeof puskuri));
    TARKISTA(close(fd));
    TARKISTA(write(STDOUT_FILENO, puskuri, (size_t)n));
    // @loppu viesti
    return 0;
}

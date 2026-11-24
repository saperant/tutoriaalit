// Kirjoittaa tekstin tiedostoon omassa prosessissaan. Jos ajuri kaatuu
// kirjoituksen aikana, ydin lopettaa tämän prosessin eikä init-prosessia.
// Käyttö: kirjoita tiedosto teksti
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    int fd = argc == 3 ? open(argv[1], O_WRONLY) : -1;
    if (fd < 0 || write(fd, argv[2], strlen(argv[2])) < 0) {
        printf("kirjoita: %s\n", strerror(errno));
        return 1;
    }
    close(fd);
    return 0;
}

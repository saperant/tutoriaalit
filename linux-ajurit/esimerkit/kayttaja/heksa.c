// Tulostaa tiedoston alun heksadesimaalina ja merkkeinä (kuten hexdump -C).
// Käyttö: heksa tiedosto [tavuja]
#include <ctype.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    unsigned char data[4096];
    size_t pyydetty = argc > 2 ? (size_t)atol(argv[2]) : sizeof data;
    int fd = argc > 1 ? open(argv[1], O_RDONLY) : -1;
    if (fd < 0 || pyydetty > sizeof data) {
        fprintf(stderr, "käyttö: heksa tiedosto [tavuja]\n");
        return 2;
    }
    ssize_t n = read(fd, data, pyydetty);
    close(fd);
    for (ssize_t rivi = 0; rivi < n; rivi += 16) {
        char merkit[17] = "";
        printf("%04zx ", (size_t)rivi);
        for (ssize_t i = rivi; i < rivi + 16 && i < n; i++) {
            printf(" %02x", data[i]);
            merkit[i - rivi] = isprint(data[i]) ? (char)data[i] : '.';
        }
        printf("  %s\n", merkit);
    }
    return n < 0;
}

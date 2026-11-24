// Järjestelmäkutsu kolmella tavalla: kirjaston kääre, syscall() ja
// virheen palautus errno-muuttujassa.
#define _GNU_SOURCE
#include <fcntl.h>
#include <string.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku kaare
    const char viesti[] = "write-kääre\n";
    TARKISTA(write(STDOUT_FILENO, viesti, strlen(viesti)));

    // Sama kutsu ilman käärettä: numero ja argumentit suoraan.
    const char suora[] = "syscall(SYS_write)\n";
    TARKISTA(syscall(SYS_write, STDOUT_FILENO, suora, strlen(suora)));
    printf("getpid() == syscall(SYS_getpid): %s\n",
           getpid() == syscall(SYS_getpid) ? "kyllä" : "ei");
    // @loppu kaare

    // @alku errno
    int fd = open("ei-ole.txt", O_RDONLY);
    if (fd == -1) {
        printf("open palautti -1, errno = %s: %s\n",
               strerrorname_np(errno), strerror(errno));
    }
    errno = 0;
    long tulos = syscall(SYS_close, 12345);   // kuvaajaa ei ole
    printf("close(12345) = %ld, errno = %s\n", tulos,
           strerrorname_np(errno));
    // @loppu errno
    return 0;
}

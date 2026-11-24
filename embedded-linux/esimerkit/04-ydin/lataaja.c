// Ajetaan initinä: lataa moduulin, näyttää sen ytimen lokiin kirjoittamat
// rivit ja moduuliluettelon, poistaa moduulin ja sammuttaa koneen.

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/syscall.h>
#include <unistd.h>

// @alku loki
// /dev/kmsg antaa ytimen lokin tietue kerrallaan muodossa
// "taso,järjestysnumero,aika,liput;viesti". Aika vaihtelee, joten
// tulostetaan vain viesti.
static void nayta_loki(int kmsg, const char *etuliite)
{
    char tietue[512];
    ssize_t n;
    while ((n = read(kmsg, tietue, sizeof tietue - 1)) > 0) {
        tietue[n] = '\0';
        char *viesti = strchr(tietue, ';');
        if (viesti != NULL && strncmp(viesti + 1, etuliite,
                                      strlen(etuliite)) == 0) {
            printf("loki: %s", viesti + 1);
        }
    }
}
// @loppu loki

static void nayta_moduulit(void)
{
    char rivi[256];
    FILE *f = fopen("/proc/modules", "r");
    while (f != NULL && fgets(rivi, sizeof rivi, f) != NULL) {
        rivi[strcspn(rivi, " ")] = '\0';
        printf("moduuli: %s\n", rivi);
    }
    if (f != NULL) {
        fclose(f);
    }
}

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    int kmsg = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);
    lseek(kmsg, 0, SEEK_END);  // vain tästä eteenpäin tulevat rivit

    // @alku lataus
    int fd = open("/lib/modules/hei.ko", O_RDONLY | O_CLOEXEC);
    if (fd < 0 || syscall(SYS_finit_module, fd, "viesti=initramfsista",
                          0) != 0) {
        printf("lataus: %s\n", strerror(errno));
        return 1;
    }
    close(fd);
    nayta_loki(kmsg, "hei:");
    nayta_moduulit();
    if (syscall(SYS_delete_module, "hei", O_NONBLOCK) != 0) {
        printf("poisto: %s\n", strerror(errno));
    }
    nayta_loki(kmsg, "hei:");
    // @loppu lataus

    sync();
    reboot(RB_POWER_OFF);
    return 1;
}

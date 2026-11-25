// Ajetaan initinä: näyttää, miten ydin näki laitepuun. Ydin julkaisee
// puun hakemistona /sys/firmware/devicetree/base: solmu on hakemisto ja
// ominaisuus tiedosto, jonka sisältö on ominaisuuden raakatavut.

#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <unistd.h>

#define PUU "/sys/firmware/devicetree/base"
#define ANTURI PUU "/anturi@9100000"

// Lukee ominaisuuden raakatavut; palauttaa pituuden tai -1.
static long lue(const char *polku, unsigned char *puskuri, size_t koko)
{
    FILE *f = fopen(polku, "rb");
    if (f == NULL) {
        return -1;
    }
    size_t n = fread(puskuri, 1, koko, f);
    fclose(f);
    return (long)n;
}

// @alku merkkijonot
// Merkkijonolista: arvot on erotettu NUL-merkeillä ("a\0b\0").
static void nayta_jonot(const char *otsikko, const char *polku)
{
    unsigned char arvo[256];
    long n = lue(polku, arvo, sizeof arvo - 1);
    printf("%-22s", otsikko);
    if (n <= 0) {
        printf("(puuttuu)\n");
        return;
    }
    for (long i = 0; i < n; i += (long)strlen((char *)arvo + i) + 1) {
        printf("%s\"%s\"", i == 0 ? "" : ", ", (char *)arvo + i);
    }
    printf("\n");
}

// Solut ovat 32-bittisiä isoendiantisia lukuja.
static void nayta_solut(const char *otsikko, const char *polku)
{
    uint32_t solut[16];
    long n = lue(polku, (unsigned char *)solut, sizeof solut);
    printf("%-22s<", otsikko);
    for (long i = 0; i < n / 4; i++) {
        printf("%s0x%x", i == 0 ? "" : " ", ntohl(solut[i]));
    }
    printf(">\n");
}
// @loppu merkkijonot

// @alku sidonta
// Näyttää, mihin ajuriin väylän laite on sidottu.
static void nayta_ajuri(const char *vayla, const char *laite)
{
    char polku[PATH_MAX], kohde[PATH_MAX];
    snprintf(polku, sizeof polku, "/sys/bus/%s/devices/%s/driver",
             vayla, laite);
    ssize_t n = readlink(polku, kohde, sizeof kohde - 1);
    if (n < 0) {
        printf("%s/%s: ei ajuria\n", vayla, laite);
        return;
    }
    kohde[n] = '\0';
    printf("%s/%s: ajuri %s\n", vayla, laite, strrchr(kohde, '/') + 1);
}
// @loppu sidonta

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    mkdir("/sys", 0555);
    if (mount("sysfs", "/sys", "sysfs", 0, NULL) != 0) {
        perror("mount /sys");
        return 1;
    }
    nayta_jonot("model:", PUU "/model");
    nayta_jonot("bootargs:", PUU "/chosen/bootargs");
    nayta_jonot("anturi compatible:", ANTURI "/compatible");
    nayta_solut("anturi reg:", ANTURI "/reg");
    nayta_solut("anturi interrupts:", ANTURI "/interrupts");
    nayta_solut("raja-arvo:", ANTURI "/tutoriaalit,raja-arvo");
    nayta_jonot("label:", ANTURI "/label");

    unsigned char alias[128] = {0};
    if (lue("/sys/bus/platform/devices/9100000.anturi/modalias", alias,
            sizeof alias - 1) > 0) {
        printf("modalias:             %s", (char *)alias);
    }
    nayta_ajuri("amba", "9000000.pl011");
    nayta_ajuri("platform", "9100000.anturi");

    sync();
    reboot(RB_POWER_OFF);
    return 1;
}

// Tulostaa anturin virtatilan yhdellä rivillä: ajonaikaisen
// virranhallinnan tila ja käyttölaskuri, säätimen tila, kellon
// käyttäjämäärä ja nollauslinjan taso. Tiedot luetaan samoista
// tiedostoista, joita kehittäjä lukisi käsin.
#include <glob.h>
#include <stdio.h>
#include <string.h>

// @alku polut
#define ANTURI "/sys/devices/platform/paineanturi/power/"
static const char *const polut[][2] = {
    {"tila", ANTURI "runtime_status"},
    {"kayttajia", ANTURI "runtime_usage"},
    {"vdd", "/sys/devices/platform/saadin-vdd-anturi/regulator/*/state"},
    {"kello", "/sys/kernel/debug/clk/naytekello/clk_enable_count"},
    {"nreset",
     "/sys/devices/platform/gpio-simulator/gpiochip*/sim_gpio1/value"},
};
// @loppu polut

static void lue(const char *malli, char *arvo, size_t koko)
{
    glob_t osumat;
    snprintf(arvo, koko, "?");
    if (glob(malli, 0, NULL, &osumat) != 0) {
        return;
    }
    FILE *f = fopen(osumat.gl_pathv[0], "r");
    if (f != NULL) {
        if (fgets(arvo, (int)koko, f) != NULL) {
            arvo[strcspn(arvo, "\n")] = '\0';
        }
        fclose(f);
    }
    globfree(&osumat);
}

int main(void)
{
    printf(" ");
    for (size_t i = 0; i < sizeof polut / sizeof polut[0]; i++) {
        char arvo[32];
        lue(polut[i][1], arvo, sizeof arvo);
        printf(" %s=%s", polut[i][0], arvo);
    }
    printf("\n");
    return 0;
}

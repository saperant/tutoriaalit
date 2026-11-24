// Kohdeohjelma purkutyökaluille: pieni varastokirjanpito.
#include <stdio.h>
#include <string.h>

struct nimike {
    char koodi[8];
    int saldo;
    int halytysraja;
};

static struct nimike varasto[] = {
    {"R-100", 12, 5},
    {"R-200", 3, 4},
    {"M-310", 0, 2},
};

enum { NIMIKKEITA = sizeof varasto / sizeof varasto[0] };

// @alku etsi
static struct nimike *etsi(const char *koodi)
{
    for (int i = 0; i < NIMIKKEITA; i++) {
        if (strcmp(varasto[i].koodi, koodi) == 0) {
            return &varasto[i];
        }
    }
    return NULL;
}
// @loppu etsi

static int ota(const char *koodi, int maara)
{
    struct nimike *n = etsi(koodi);
    if (n == NULL || maara <= 0 || maara > n->saldo) {
        return -1;
    }
    n->saldo -= maara;
    return n->saldo;
}

static void raportoi(void)
{
    for (int i = 0; i < NIMIKKEITA; i++) {
        if (varasto[i].saldo < varasto[i].halytysraja) {
            printf("TILAA: %s (saldo %d)\n", varasto[i].koodi,
                   varasto[i].saldo);
        }
    }
}

int main(void)
{
    printf("otto: %d\n", ota("R-100", 4));
    printf("otto: %d\n", ota("R-100", 9));
    raportoi();
    return 0;
}

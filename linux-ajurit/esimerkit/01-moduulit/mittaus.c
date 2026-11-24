// Mittausmoduuli: kirjaa parametrina annetut arvot tilastomoduuliin.
// Käyttää tilasto.ko:n vientiä, joten tilasto on ladattava ensin.
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>

#include "tilasto.h"

// @alku taulukko
static int arvot[8];
static int arvomaara;
module_param_array(arvot, int, &arvomaara, 0444);
MODULE_PARM_DESC(arvot, "kirjattavat arvot pilkuin eroteltuina");
// @loppu taulukko

static int __init mittaus_alku(void)
{
    for (int i = 0; i < arvomaara; i++) {
        tilasto_kirjaa(KBUILD_MODNAME, arvot[i]);
    }
    pr_info("kirjattiin %d arvoa\n", arvomaara);
    return 0;
}

static void __exit mittaus_loppu(void)
{
}

module_init(mittaus_alku);
module_exit(mittaus_loppu);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Esimerkki toisen moduulin viemän symbolin käytöstä");

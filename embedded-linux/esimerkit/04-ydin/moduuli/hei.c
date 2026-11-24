// Pienin ytimen moduuli: tulostaa parametrinsa ladattaessa ja
// poistettaessa. Käännetään ytimen käännöspuuta vasten (Kbuild).
#include <linux/init.h>
#include <linux/module.h>
#include <linux/moduleparam.h>

static char *viesti = "oletus";
module_param(viesti, charp, 0444);
MODULE_PARM_DESC(viesti, "ladattaessa tulostettava viesti");

static int __init hei_alku(void)
{
    pr_info("hei: ladattu, viesti=%s\n", viesti);
    return 0;
}

static void __exit hei_loppu(void)
{
    pr_info("hei: poistettu\n");
}

module_init(hei_alku);
module_exit(hei_loppu);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Tutoriaalin esimerkkimoduuli");

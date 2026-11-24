// Tilastomoduuli: muut moduulit kirjaavat mittausarvoja funktiolla
// tilasto_kirjaa(), ja moduuli pitää kirjaa määrästä, pienimmästä ja
// suurimmasta arvosta. Näyttää parametrit, niiden tarkistuksen ja
// symbolin viennin.
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/init.h>
#include <linux/limits.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/mutex.h>

#include "tilasto.h"

// @alku parametrit
static char *nimi = "tilasto";
module_param(nimi, charp, 0444);
MODULE_PARM_DESC(nimi, "tilaston nimi lokiriveillä");

static int raja = 100;
module_param(raja, int, 0644);
MODULE_PARM_DESC(raja, "varoitusraja, oltava > 0");
// @loppu parametrit

static DEFINE_MUTEX(lukko);
static int maara;
static int pienin = INT_MAX;
static int suurin = INT_MIN;

// @alku vienti
void tilasto_kirjaa(const char *lahde, int arvo)
{
    mutex_lock(&lukko);
    maara++;
    pienin = min(pienin, arvo);
    suurin = max(suurin, arvo);
    mutex_unlock(&lukko);
    if (arvo > READ_ONCE(raja)) {
        pr_warn("%s: %s ylitti rajan: %d > %d\n", nimi, lahde, arvo,
                READ_ONCE(raja));
    }
}
EXPORT_SYMBOL_GPL(tilasto_kirjaa);
// @loppu vienti

// @alku alku
static int __init tilasto_alku(void)
{
    if (raja <= 0) {
        pr_err("raja=%d ei kelpaa\n", raja);
        return -EINVAL;  // lataus epäonnistuu, moduulia ei jää ytimeen
    }
    pr_info("%s: valmis, raja %d\n", nimi, raja);
    return 0;
}

static void __exit tilasto_loppu(void)
{
    if (maara == 0) {
        pr_info("%s: ei arvoja\n", nimi);
    } else {
        pr_info("%s: %d arvoa, pienin %d, suurin %d\n", nimi, maara,
                pienin, suurin);
    }
}

module_init(tilasto_alku);
module_exit(tilasto_loppu);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Tutoriaalit");
MODULE_DESCRIPTION("Mittausarvojen tilasto muille moduuleille");
// @loppu alku

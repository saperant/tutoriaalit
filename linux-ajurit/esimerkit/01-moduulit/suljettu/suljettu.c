// Väärin: suljetun lisenssin moduuli yrittää käyttää GPL-symbolia.
// modpost hylkää moduulin jo käännöksessä.
#include <linux/init.h>
#include <linux/module.h>

#include "../tilasto.h"

static int __init suljettu_alku(void)
{
    tilasto_kirjaa(KBUILD_MODNAME, 1);
    return 0;
}

module_init(suljettu_alku);
MODULE_LICENSE("Proprietary");

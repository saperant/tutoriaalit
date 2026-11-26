// Paineanturin ajuri ilman virranhallintaa: anturi käynnistetään
// sidonnassa ja sammutetaan irrotuksessa. Resurssien haku ja virran
// kytkentäjärjestys ovat otsakkeessa paine.h.
#include <linux/module.h>
#include <linux/platform_device.h>

#include "paine.h"

static struct attribute *paine_attrs[] = {
    &dev_attr_halytyksia.attr,
    NULL,
};
ATTRIBUTE_GROUPS(paine);

// @alku probe
static void paine_sammuta(void *data)
{
    paine_virta_pois(data);
}

static int paine_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct paine *p;
    int virhe;

    p = devm_kzalloc(dev, sizeof(*p), GFP_KERNEL);
    if (!p)
        return -ENOMEM;
    p->dev = dev;
    platform_set_drvdata(pdev, p);
    virhe = paine_hae(p);
    if (virhe)
        return virhe;
    virhe = paine_virta_paalle(p);
    if (virhe)
        return dev_err_probe(dev, virhe, "virta ei kytkeydy\n");
    // Sammutus lisätään devm-ketjuun. Irrotuksessa ketju puretaan
    // lopusta alkaen: ensin keskeytys, sitten tämä sammutus ja vasta
    // sen jälkeen linjat, kello ja säädin palautetaan.
    virhe = devm_add_action_or_reset(dev, paine_sammuta, p);
    if (virhe)
        return virhe;
    return paine_pyyda_keskeytys(p);
}
// @loppu probe

static const struct of_device_id paine_of[] = {
    { .compatible = "tutoriaalit,paineanturi" },
    { }
};
MODULE_DEVICE_TABLE(of, paine_of);

static struct platform_driver paine_ajuri = {
    .probe = paine_probe,
    .driver = {
        .name = "paine",
        .of_match_table = paine_of,
        .dev_groups = paine_groups,
    },
};
module_platform_driver(paine_ajuri);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Paineanturi: kello, saadin ja GPIO-linjat laitepuusta");

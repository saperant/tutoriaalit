// Paineanturin ajuri virranhallinnalla: anturi on päällä vain, kun sitä
// käytetään. Resurssit ja kytkentäjärjestys ovat samat kuin paine.c:ssä
// (paine.h); tässä tiedostossa on vain se, mikä virranhallinnasta
// seuraa.
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/pm_runtime.h>

#include "paine.h"

#define LEPOVIIVE_MS 1000

// @alku runtime
// Ydin kutsuu näitä, kun käyttölaskuri putoaa nollaan ja lepoviive on
// kulunut, ja kun laskuri nousee nollasta. Takaisinkutsut ovat
// prosessikontekstissa ja saavat nukkua.
static int paine_runtime_suspend(struct device *dev)
{
    paine_virta_pois(dev_get_drvdata(dev));
    return 0;
}

static int paine_runtime_resume(struct device *dev)
{
    return paine_virta_paalle(dev_get_drvdata(dev));
}

// Makro tekee myös järjestelmän lepotilan takaisinkutsut: suspend ajaa
// yllä olevan sammutuksen, jos laite on päällä, ja resume palauttaa
// tilan, jossa laite oli.
static DEFINE_RUNTIME_DEV_PM_OPS(paine_pm, paine_runtime_suspend,
                                 paine_runtime_resume, NULL);
// @loppu runtime

// @alku mittaus
// Mittaus tarvitsee anturin päälle. pm_runtime_resume_and_get kasvattaa
// käyttölaskuria ja herättää laitteen, jos se nukkuu; put_autosuspend
// vähentää laskuria ja jättää laitteen päälle lepoviiveen ajaksi, jotta
// peräkkäiset mittaukset eivät kytke virtaa joka kerta.
static ssize_t paine_pa_show(struct device *dev,
                             struct device_attribute *a, char *puskuri)
{
    struct paine *p = dev_get_drvdata(dev);
    u32 nro;
    int virhe;

    virhe = pm_runtime_resume_and_get(dev);
    if (virhe)
        return virhe;
    mutex_lock(&p->lukko);
    msleep(10);  // muunnosaika; arvo on simuloitu vakio
    nro = ++p->mittauksia;
    mutex_unlock(&p->lukko);
    dev_info(dev, "mittaus %u\n", nro);
    pm_runtime_mark_last_busy(dev);
    pm_runtime_put_autosuspend(dev);
    return sysfs_emit(puskuri, "101325\n");
}
static DEVICE_ATTR_RO(paine_pa);
// @loppu mittaus

// Jatkuva mittaus pitää yhden viittauksen laitteeseen, joten anturi ei
// sammu ennen kuin tila kytketään pois.
static ssize_t jatkuva_show(struct device *dev, struct device_attribute *a,
                            char *puskuri)
{
    struct paine *p = dev_get_drvdata(dev);

    return sysfs_emit(puskuri, "%d\n", p->jatkuva);
}

static ssize_t jatkuva_store(struct device *dev, struct device_attribute *a,
                             const char *puskuri, size_t pituus)
{
    struct paine *p = dev_get_drvdata(dev);
    bool paalle;
    int virhe = kstrtobool(puskuri, &paalle);

    if (virhe)
        return virhe;
    mutex_lock(&p->lukko);
    if (paalle && !p->jatkuva) {
        virhe = pm_runtime_resume_and_get(dev);
    } else if (!paalle && p->jatkuva) {
        pm_runtime_mark_last_busy(dev);
        pm_runtime_put_autosuspend(dev);
    }
    if (!virhe)
        p->jatkuva = paalle;
    mutex_unlock(&p->lukko);
    return virhe ? virhe : pituus;
}
static DEVICE_ATTR_RW(jatkuva);

static struct attribute *paine_attrs[] = {
    &dev_attr_halytyksia.attr,
    &dev_attr_paine_pa.attr,
    &dev_attr_jatkuva.attr,
    NULL,
};
ATTRIBUTE_GROUPS(paine);

// @alku probe
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
    // Anturi käynnistetään kerran, jotta se voidaan tunnistaa ja
    // alustaa. Sen jälkeen ytimelle kerrotaan, missä tilassa laite on.
    virhe = paine_virta_paalle(p);
    if (virhe)
        return dev_err_probe(dev, virhe, "virta ei kytkeydy\n");
    pm_runtime_set_active(dev);
    pm_runtime_get_noresume(dev);  // hereillä proben loppuun asti
    pm_runtime_set_autosuspend_delay(dev, LEPOVIIVE_MS);
    pm_runtime_use_autosuspend(dev);
    pm_runtime_enable(dev);

    virhe = paine_pyyda_keskeytys(p);
    if (virhe) {
        pm_runtime_disable(dev);
        pm_runtime_put_noidle(dev);
        pm_runtime_set_suspended(dev);
        pm_runtime_dont_use_autosuspend(dev);
        paine_virta_pois(p);
        return virhe;
    }
    // Probe on valmis: viittaus vapautetaan, ja laite sammuu
    // lepoviiveen kuluttua, jos kukaan ei käytä sitä.
    pm_runtime_mark_last_busy(dev);
    pm_runtime_put_autosuspend(dev);
    return 0;
}
// @loppu probe

// @alku remove
// Attribuutit on poistettu ennen tätä kutsua, joten uusia käyttäjiä ei
// tule. pm_runtime_disable odottaa kesken olevan siirtymän loppuun; sen
// jälkeen tila ei muutu, ja anturi sammutetaan, jos se jäi päälle.
static void paine_remove(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct paine *p = platform_get_drvdata(pdev);

    pm_runtime_disable(dev);
    if (!pm_runtime_status_suspended(dev))
        paine_virta_pois(p);
    pm_runtime_set_suspended(dev);
    if (p->jatkuva)
        pm_runtime_put_noidle(dev);
    pm_runtime_dont_use_autosuspend(dev);
}
// @loppu remove

static const struct of_device_id paine_of[] = {
    { .compatible = "tutoriaalit,paineanturi" },
    { }
};
MODULE_DEVICE_TABLE(of, paine_of);

static struct platform_driver paine_ajuri = {
    .probe = paine_probe,
    .remove_new = paine_remove,
    .driver = {
        .name = "paine",
        .of_match_table = paine_of,
        .dev_groups = paine_groups,
        .pm = pm_ptr(&paine_pm),
    },
};
module_platform_driver(paine_ajuri);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Paineanturi: ajonaikainen virranhallinta ja lepotila");

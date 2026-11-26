// Paineanturin ajurin yhteinen osa: resurssien haku laitepuusta ja virran
// kytkentäjärjestys. Kaksi ajuria käyttää tätä: paine.c pitää anturin
// päällä koko sidonnan ajan, ja paine_pm.c sammuttaa sen, kun sitä ei
// käytetä.
//
// Anturi on simuloitu: virt-koneessa ei ole piiriä linjojen päässä.
// Ajurin kannalta se on kuitenkin tavallinen laite, joka tarvitsee
// käyttöjännitteen, näytekellon, nollauslinjan ja hälytyskeskeytyksen.
#ifndef PAINE_H
#define PAINE_H

#include <linux/atomic.h>
#include <linux/clk.h>
#include <linux/delay.h>
#include <linux/device.h>
#include <linux/gpio/consumer.h>
#include <linux/interrupt.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/regulator/consumer.h>

struct paine {
    struct device *dev;
    struct regulator *vdd;       // laitepuun vdd-supply
    struct clk *kello;           // laitepuun clocks
    struct gpio_desc *reset;     // reset-gpios; looginen 1 = nollaus
    struct gpio_desc *halytys;   // halytys-gpios, tulo
    int irq;                     // hälytyslinjan keskeytys
    atomic_t halytyksia;
    struct mutex lukko;          // suojaa alla olevat (paine_pm.c)
    bool jatkuva;
    u32 mittauksia;
};

// @alku hae
// Jokainen haku on devm-hallittu: ydin palauttaa resurssin, kun laite
// irrotetaan tai probe epäonnistuu. Jos tarjoajaa ei vielä ole, haku
// palauttaa -EPROBE_DEFER, ja dev_err_probe kirjaa syyn.
static int paine_hae(struct paine *p)
{
    struct device *dev = p->dev;
    u32 taajuus = 48000;
    int virhe;

    p->vdd = devm_regulator_get(dev, "vdd");
    if (IS_ERR(p->vdd))
        return dev_err_probe(dev, PTR_ERR(p->vdd), "vdd puuttuu\n");
    p->kello = devm_clk_get(dev, NULL);
    if (IS_ERR(p->kello))
        return dev_err_probe(dev, PTR_ERR(p->kello), "kello puuttuu\n");
    // GPIOD_OUT_HIGH on looginen arvo: linja otetaan lähdöksi ja anturi
    // pidetään nollauksessa. Laitepuun GPIO_ACTIVE_LOW kääntää sen
    // linjan tasoksi 0.
    p->reset = devm_gpiod_get(dev, "reset", GPIOD_OUT_HIGH);
    if (IS_ERR(p->reset))
        return dev_err_probe(dev, PTR_ERR(p->reset), "reset puuttuu\n");
    p->halytys = devm_gpiod_get(dev, "halytys", GPIOD_IN);
    if (IS_ERR(p->halytys))
        return dev_err_probe(dev, PTR_ERR(p->halytys),
                             "halytys puuttuu\n");
    p->irq = gpiod_to_irq(p->halytys);
    if (p->irq < 0)
        return dev_err_probe(dev, p->irq, "halytyksella ei keskeytysta\n");

    // Taajuutta pyydetään; kellon tarjoaja päättää, mitä saadaan.
    of_property_read_u32(dev->of_node, "tutoriaalit,naytetaajuus-hz",
                         &taajuus);
    virhe = clk_set_rate(p->kello, taajuus);
    if (virhe)
        return dev_err_probe(dev, virhe, "taajuus %u ei kelpaa\n", taajuus);
    dev_info(dev, "pyydetty %u Hz, saatu %lu Hz\n", taajuus,
             clk_get_rate(p->kello));
    mutex_init(&p->lukko);
    return 0;
}
// @loppu hae

// @alku virta
// Kytkentäjärjestys on anturin datalehdestä: ensin jännite, sitten kello,
// lopuksi nollaus vapautetaan. Sammutus tehdään käänteisesti.
static int paine_virta_paalle(struct paine *p)
{
    int virhe;

    virhe = regulator_enable(p->vdd);
    if (virhe)
        return virhe;
    virhe = clk_prepare_enable(p->kello);
    if (virhe) {
        regulator_disable(p->vdd);
        return virhe;
    }
    usleep_range(1000, 2000);  // jännite ja kello vakaiksi
    gpiod_set_value_cansleep(p->reset, 0);
    dev_info(p->dev, "virta paalla, %d mV\n",
             regulator_get_voltage(p->vdd) / 1000);
    return 0;
}

static void paine_virta_pois(struct paine *p)
{
    gpiod_set_value_cansleep(p->reset, 1);
    clk_disable_unprepare(p->kello);
    regulator_disable(p->vdd);
    dev_info(p->dev, "virta pois\n");
}
// @loppu virta

// @alku halytys
// Hälytyslinjan nouseva reuna. GPIO-ohjain voi olla hitaan väylän
// takana, joten käsittelijä on keskeytyssäie ilman yläpuoliskoa.
static irqreturn_t paine_halytys(int irq, void *data)
{
    struct paine *p = data;

    dev_info(p->dev, "halytys %d\n", atomic_inc_return(&p->halytyksia));
    return IRQ_HANDLED;
}

static int paine_pyyda_keskeytys(struct paine *p)
{
    return devm_request_threaded_irq(p->dev, p->irq, NULL, paine_halytys,
                                     IRQF_TRIGGER_RISING | IRQF_ONESHOT,
                                     dev_name(p->dev), p);
}
// @loppu halytys

static ssize_t halytyksia_show(struct device *dev,
                               struct device_attribute *a, char *puskuri)
{
    struct paine *p = dev_get_drvdata(dev);

    return sysfs_emit(puskuri, "%d\n", atomic_read(&p->halytyksia));
}
static DEVICE_ATTR_RO(halytyksia);

#endif

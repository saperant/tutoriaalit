// SPI-muistipiirin ajuri. Piiri on vspi.c:n simuloima, mutta ajuri on
// kirjoitettu kuten oikean SPI-flashin ajuri: se tunnistaa piirin,
// lukee muistia yhdellä viestillä ja kirjoittaa kirjoitusluvan jälkeen.
// Sisältö näkyy sysfsissä binääritiedostona sisalto.
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/spi/spi.h>
#include <linux/sysfs.h>

#define KOM_KIRJOITA  0x02
#define KOM_LUE       0x03
#define KOM_TILA      0x05
#define KOM_LUPA      0x06
#define KOM_TUNNISTE  0x9f
#define MUISTI_KOKO   256

struct muisti {
    struct spi_device *spi;
    struct mutex lukko;   // yksi komento kerrallaan, suojaa komennon
    // SPI-puskurien on oltava DMA-kelpoisia: ei pinossa, oma
    // välimuistirivi. Ohjain voi siirtää ne DMA:lla.
    u8 komento[2] ____cacheline_aligned;
};

// @alku lue
// Luku on yksi viesti, jossa on kaksi siirtoa: komento ja osoite, sitten
// data. CS pysyy alhaalla koko viestin ajan.
static int muisti_lue(struct muisti *m, u8 osoite, void *kohde, size_t n)
{
    struct spi_transfer siirrot[] = {
        { .tx_buf = m->komento, .len = 2 },
        { .rx_buf = kohde, .len = n },
    };

    m->komento[0] = KOM_LUE;
    m->komento[1] = osoite;
    return spi_sync_transfer(m->spi, siirrot, ARRAY_SIZE(siirrot));
}
// @loppu lue

// @alku kirjoita
static int muisti_kirjoita(struct muisti *m, u8 osoite, const void *data,
                           size_t n)
{
    struct spi_transfer siirrot[] = {
        { .tx_buf = m->komento, .len = 2 },
        { .tx_buf = data, .len = n },
    };
    int virhe;

    // Kirjoituslupa on oma komentonsa: CS:n on noustava välissä.
    m->komento[0] = KOM_LUPA;
    virhe = spi_write(m->spi, m->komento, 1);
    if (virhe)
        return virhe;
    m->komento[0] = KOM_KIRJOITA;
    m->komento[1] = osoite;
    return spi_sync_transfer(m->spi, siirrot, ARRAY_SIZE(siirrot));
}
// @loppu kirjoita

// @alku sysfs
static ssize_t sisalto_read(struct file *f, struct kobject *kobj,
                            struct bin_attribute *attr, char *puskuri,
                            loff_t kohta, size_t n)
{
    struct muisti *m = dev_get_drvdata(kobj_to_dev(kobj));
    int virhe;

    // sysfs rajaa kohdan ja pituuden attribuutin kokoon (attr->size).
    mutex_lock(&m->lukko);
    virhe = muisti_lue(m, kohta, puskuri, n);
    mutex_unlock(&m->lukko);
    return virhe ? virhe : n;
}

static ssize_t sisalto_write(struct file *f, struct kobject *kobj,
                             struct bin_attribute *attr, char *puskuri,
                             loff_t kohta, size_t n)
{
    struct muisti *m = dev_get_drvdata(kobj_to_dev(kobj));
    int virhe;

    mutex_lock(&m->lukko);
    virhe = muisti_kirjoita(m, kohta, puskuri, n);
    mutex_unlock(&m->lukko);
    return virhe ? virhe : n;
}
static BIN_ATTR_RW(sisalto, MUISTI_KOKO);

static struct bin_attribute *muisti_bin_attrs[] = {
    &bin_attr_sisalto,
    NULL,
};

// __ATTRIBUTE_GROUPS(muisti) odottaa ryhmän nimeksi muisti_group.
static const struct attribute_group muisti_group = {
    .bin_attrs = muisti_bin_attrs,
};
__ATTRIBUTE_GROUPS(muisti);
// @loppu sysfs

// @alku probe
static int muisti_probe(struct spi_device *spi)
{
    struct muisti *m;
    u8 komento = KOM_TUNNISTE;
    u8 tunniste[3];  // spi_write_then_read kopioi puskurit itse
    int virhe;

    m = devm_kzalloc(&spi->dev, sizeof(*m), GFP_KERNEL);
    if (!m)
        return -ENOMEM;
    m->spi = spi;
    mutex_init(&m->lukko);
    // spi_write_then_read: kirjoitus ja luku samassa CS-jaksossa.
    virhe = spi_write_then_read(spi, &komento, 1, tunniste, 3);
    if (virhe)
        return virhe;
    if (tunniste[0] != 0x5a)
        return dev_err_probe(&spi->dev, -ENODEV,
                             "tuntematon valmistaja 0x%02x\n", tunniste[0]);
    spi_set_drvdata(spi, m);
    dev_info(&spi->dev, "muistipiiri %02x %02x %02x, %u tavua\n",
             tunniste[0], tunniste[1], tunniste[2], 1u << tunniste[2]);
    return 0;
}
// @loppu probe

// @alku ajuri
static const struct spi_device_id muisti_id[] = {
    { "tutor-muisti" },
    { }
};
MODULE_DEVICE_TABLE(spi, muisti_id);

static struct spi_driver muisti_ajuri = {
    .driver = {
        .name = "tutor-muisti",
        .dev_groups = muisti_groups,
    },
    .probe = muisti_probe,
    .id_table = muisti_id,
};
module_spi_driver(muisti_ajuri);
// @loppu ajuri

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Esimerkki-SPI-muistipiirin ajuri");

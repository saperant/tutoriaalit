// Lämpöanturin I2C-ajuri. Anturi on kuvitteellinen, mutta sen
// rekisterikartta on tyypillinen: tunniste, asetus ja mittaus. QEMU:n
// virt-koneessa ei ole I2C-väylää, joten testeissä laitteen rekisterit
// tarjoaa ytimen i2c-stub-moduuli.
//
// Ajuri käyttää regmapia rekisterien lukuun ja rekisteröi lämpötilan
// hwmon-alijärjestelmään: /sys/class/hwmon/hwmonN/temp1_input.
#include <linux/err.h>
#include <linux/hwmon.h>
#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/regmap.h>

// @alku rekisterit
#define LAMPO_LAMPOTILA  0x00  // 1/100 °C, etumerkillinen
#define LAMPO_ASETUS     0x01  // bitti 0: valmiustila
#define LAMPO_RAJA       0x02  // hälytysraja, 1/100 °C
#define LAMPO_TUNNISTE   0x0f  // aina 0x005a
#define LAMPO_TUNNISTE_ARVO 0x005a
#define LAMPO_VALMIUS    BIT(0)
// @loppu rekisterit

// @alku regmap
// Kaikki rekisterit ovat 16-bittisiä. regmap valitsee SMBus-sanaluvun,
// koska väylä tukee sitä, ja tarkistaa rekisterien rajat. SMBus-sana on
// pienimmän tavun ensin; regmapin oletus on päinvastainen.
static bool lampo_kirjoitettava(struct device *dev, unsigned int rek)
{
    return rek == LAMPO_ASETUS || rek == LAMPO_RAJA;
}

static const struct regmap_config lampo_regmap = {
    .reg_bits = 8,
    .val_bits = 16,
    .val_format_endian = REGMAP_ENDIAN_LITTLE,
    .max_register = LAMPO_TUNNISTE,
    .writeable_reg = lampo_kirjoitettava,
    .cache_type = REGCACHE_NONE,  // mittaus muuttuu, ei välimuistia
};
// @loppu regmap

// @alku hwmon
static umode_t lampo_nakyvyys(const void *data,
                              enum hwmon_sensor_types tyyppi, u32 attr,
                              int kanava)
{
    switch (attr) {
    case hwmon_temp_input:
        return 0444;
    case hwmon_temp_max:
        return 0644;
    default:
        return 0;
    }
}

static int lampo_lue(struct device *dev, enum hwmon_sensor_types tyyppi,
                     u32 attr, int kanava, long *arvo)
{
    struct regmap *kartta = dev_get_drvdata(dev);
    unsigned int raaka;
    int virhe;

    virhe = regmap_read(kartta, attr == hwmon_temp_input ?
                        LAMPO_LAMPOTILA : LAMPO_RAJA, &raaka);
    if (virhe)
        return virhe;
    *arvo = (s16)raaka * 10L;  // hwmonin yksikkö on milliaste
    return 0;
}

static int lampo_kirjoita(struct device *dev,
                          enum hwmon_sensor_types tyyppi, u32 attr,
                          int kanava, long arvo)
{
    struct regmap *kartta = dev_get_drvdata(dev);

    arvo = clamp_val(arvo, -40000, 125000) / 10;
    return regmap_write(kartta, LAMPO_RAJA, (u16)(s16)arvo);
}

static const struct hwmon_ops lampo_ops = {
    .is_visible = lampo_nakyvyys,
    .read = lampo_lue,
    .write = lampo_kirjoita,
};

static const struct hwmon_channel_info *const lampo_kanavat[] = {
    HWMON_CHANNEL_INFO(temp, HWMON_T_INPUT | HWMON_T_MAX),
    NULL
};

static const struct hwmon_chip_info lampo_piiri = {
    .ops = &lampo_ops,
    .info = lampo_kanavat,
};
// @loppu hwmon

// @alku probe
static int lampo_probe(struct i2c_client *asiakas)
{
    struct device *dev = &asiakas->dev;
    struct regmap *kartta;
    struct device *hwmon;
    unsigned int tunniste;
    int virhe;

    kartta = devm_regmap_init_i2c(asiakas, &lampo_regmap);
    if (IS_ERR(kartta))
        return PTR_ERR(kartta);
    // Tunnisterekisteri varmistaa, että osoitteessa on oikea piiri.
    virhe = regmap_read(kartta, LAMPO_TUNNISTE, &tunniste);
    if (virhe)
        return dev_err_probe(dev, virhe, "tunnisteen luku\n");
    if (tunniste != LAMPO_TUNNISTE_ARVO)
        return dev_err_probe(dev, -ENODEV, "tunniste 0x%04x\n",
                             tunniste);
    // Herätetään piiri valmiustilasta.
    virhe = regmap_update_bits(kartta, LAMPO_ASETUS, LAMPO_VALMIUS, 0);
    if (virhe)
        return virhe;
    hwmon = devm_hwmon_device_register_with_info(dev, "tutorlampo",
                                                 kartta, &lampo_piiri,
                                                 NULL);
    if (IS_ERR(hwmon))
        return PTR_ERR(hwmon);
    dev_info(dev, "anturi osoitteessa 0x%02x (%s)\n",
             asiakas->addr, asiakas->adapter->name);
    return 0;
}
// @loppu probe

// @alku ajuri
static const struct i2c_device_id lampo_id[] = {
    { "tutor-lampo" },   // nimi, jolla laite luodaan ilman laitepuuta
    { }
};
MODULE_DEVICE_TABLE(i2c, lampo_id);

static const struct of_device_id lampo_of_match[] = {
    { .compatible = "tutoriaalit,lampo" },
    { }
};
MODULE_DEVICE_TABLE(of, lampo_of_match);

static struct i2c_driver lampo_ajuri = {
    .driver = {
        .name = "tutor-lampo",
        .of_match_table = lampo_of_match,
    },
    .probe = lampo_probe,
    .id_table = lampo_id,
};
module_i2c_driver(lampo_ajuri);
// @loppu ajuri

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Esimerkkilämpöanturin I2C-ajuri");

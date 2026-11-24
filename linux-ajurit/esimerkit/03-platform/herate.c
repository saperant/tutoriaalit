// Herätysajastin: platform-ajuri QEMU:n virt-koneen PL031-reaaliaikakellolle.
// Laitepuun oma solmu (herate.dtsi) korvaa koneen pl031-solmun, joten
// ajuri saa laitteen laitepuusta kuten mikä tahansa piirin oheislaite.
//
// Käyttäjälle ajuri tarjoaa laitteen /dev/herate: kirjoitus "N" asettaa
// herätyksen N sekunnin päähän, luku odottaa herätystä ja poll() kertoo,
// onko herätys tapahtunut. Lisäksi sysfs-attribuutit ja debugfs-hakemisto.
#include <linux/debugfs.h>
#include <linux/device.h>
#include <linux/interrupt.h>
#include <linux/io.h>
#include <linux/miscdevice.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/of.h>
#include <linux/platform_device.h>
#include <linux/poll.h>
#include <linux/seq_file.h>
#include <linux/spinlock.h>
#include <linux/uaccess.h>
#include <linux/wait.h>
#include <linux/workqueue.h>

// @alku rekisterit
// PL031:n rekisterit (ARM PrimeCell Real Time Clock, DDI 0224).
#define RTCDR     0x00   // laskuri, sekunteja (vain luku)
#define RTCMR     0x04   // vertailuarvo: keskeytys, kun RTCDR == RTCMR
#define RTCLR     0x08   // laskurin asetus
#define RTCIMSC   0x10   // keskeytysmaski, bitti 0
#define RTCRIS    0x14   // keskeytystila ennen maskia
#define RTCMIS    0x18   // maskattu keskeytystila
#define RTCICR    0x1c   // keskeytyksen kuittaus
#define RTCPERIPHID0 0xfe0  // tunnisterekisterit 0xfe0-0xfec
#define PL031_TUNNISTE 0x00041031  // osanumero 0x031, valmistaja ARM
#define TUNNISTE_MASKI 0x000fffff  // revisio ja asetukset eivät kiinnosta
// @loppu rekisterit

// @alku tila
struct herate {
    struct device *dev;
    void __iomem *rek;           // ioremapattu rekisterialue
    struct miscdevice misc;
    const char *nimi;            // laitepuun label
    u32 oletusviive;             // laitepuun tutoriaalit,oletusviive-s

    spinlock_t lukko;            // suojaa alla olevat; myös keskeytyksessä
    u32 heratyksia;              // keskeytysten määrä
    u32 luettu;                  // käyttäjälle jo kerrotut herätykset
    u32 jakso;                   // 0 = kertaherätys, muuten sekunteja

    struct mutex asetus;         // sarjallistaa herätysten asettamisen
    wait_queue_head_t odottajat;
    struct delayed_work vahti;   // varoittaa, jos keskeytys ei tule
    struct dentry *debug;
};
// @loppu tila

// @alku keskeytys
// Yläpuolisko: keskeytyskonteksti. Ei saa nukkua eikä ottaa mutexia.
// Kuitataan laite heti, jotta tasoliipaistu keskeytys ei toistu.
static irqreturn_t herate_irq(int irq, void *data)
{
    struct herate *h = data;

    if (!(readl(h->rek + RTCMIS) & 1))
        return IRQ_NONE;  // ei tämän laitteen keskeytys
    writel(1, h->rek + RTCICR);
    spin_lock(&h->lukko);
    h->heratyksia++;
    if (h->jakso)
        writel(readl(h->rek + RTCMR) + h->jakso, h->rek + RTCMR);
    else
        writel(0, h->rek + RTCIMSC);
    spin_unlock(&h->lukko);
    return IRQ_WAKE_THREAD;
}

// Alapuolisko omassa säikeessään: prosessikonteksti, saa nukkua.
static irqreturn_t herate_saie(int irq, void *data)
{
    struct herate *h = data;

    cancel_delayed_work(&h->vahti);
    wake_up_interruptible(&h->odottajat);
    dev_dbg(h->dev, "odottajat heratetty\n");
    return IRQ_HANDLED;
}
// @loppu keskeytys

// @alku vahti
// Viivästetty työ ajetaan työjonon säikeessä. Se varoittaa, jos
// keskeytystä ei tullut sekunnin kuluessa odotetusta.
static void herate_vahti(struct work_struct *tyo)
{
    struct herate *h = container_of(to_delayed_work(tyo), struct herate,
                                    vahti);

    // RTCRIS = 1: laite on nostanut keskeytyksen, mutta se ei tullut
    // perille. Vika on silloin keskeytyksen reitissä, ei laitteessa.
    dev_warn(h->dev, "keskeytys ei saapunut ajassa, RTCRIS=%u\n",
             readl(h->rek + RTCRIS));
}
// @loppu vahti

// @alku aseta
static void herate_aseta(struct herate *h, u32 sekunnit)
{
    unsigned long liput;

    mutex_lock(&h->asetus);
    spin_lock_irqsave(&h->lukko, liput);  // keskeytykset pois tällä CPU:lla
    writel(1, h->rek + RTCICR);
    writel(readl(h->rek + RTCDR) + sekunnit, h->rek + RTCMR);
    writel(1, h->rek + RTCIMSC);
    spin_unlock_irqrestore(&h->lukko, liput);
    mod_delayed_work(system_wq, &h->vahti, (sekunnit + 1) * HZ);
    mutex_unlock(&h->asetus);
}
// @loppu aseta

// @alku misc
static struct herate *herate_tiedostosta(struct file *tiedosto)
{
    // misc-ydin asettaa private_data:ksi miscdevice-rakenteen osoitteen.
    return container_of(tiedosto->private_data, struct herate, misc);
}

static bool herate_uusi(struct herate *h)
{
    unsigned long liput;
    bool uusi;

    spin_lock_irqsave(&h->lukko, liput);
    uusi = h->heratyksia != h->luettu;
    spin_unlock_irqrestore(&h->lukko, liput);
    return uusi;
}

static ssize_t herate_lue(struct file *tiedosto, char __user *puskuri,
                          size_t pituus, loff_t *sijainti)
{
    struct herate *h = herate_tiedostosta(tiedosto);
    unsigned long liput;
    char teksti[32];
    u32 nro;
    int n;

    if (!herate_uusi(h) && (tiedosto->f_flags & O_NONBLOCK))
        return -EAGAIN;
    if (wait_event_interruptible(h->odottajat, herate_uusi(h)))
        return -ERESTARTSYS;
    spin_lock_irqsave(&h->lukko, liput);
    nro = ++h->luettu;
    spin_unlock_irqrestore(&h->lukko, liput);
    n = scnprintf(teksti, sizeof(teksti), "herätys %u\n", nro);
    if (pituus < n)
        return -EINVAL;
    if (copy_to_user(puskuri, teksti, n))
        return -EFAULT;
    return n;
}

static ssize_t herate_kirjoita(struct file *tiedosto,
                               const char __user *puskuri, size_t pituus,
                               loff_t *sijainti)
{
    struct herate *h = herate_tiedostosta(tiedosto);
    u32 sekunnit;
    int virhe;

    // kstrtou32_from_user kopioi ja jäsentää; tyhjä syöte on oletus.
    if (pituus <= 1) {
        sekunnit = h->oletusviive;
    } else {
        virhe = kstrtou32_from_user(puskuri, pituus, 10, &sekunnit);
        if (virhe)
            return virhe;
    }
    if (sekunnit < 1 || sekunnit > 3600)
        return -ERANGE;
    herate_aseta(h, sekunnit);
    return pituus;
}

static __poll_t herate_poll(struct file *tiedosto, poll_table *taulu)
{
    struct herate *h = herate_tiedostosta(tiedosto);

    poll_wait(tiedosto, &h->odottajat, taulu);
    return herate_uusi(h) ? EPOLLIN | EPOLLRDNORM : 0;
}

static const struct file_operations herate_fops = {
    .owner = THIS_MODULE,
    .read = herate_lue,
    .write = herate_kirjoita,
    .poll = herate_poll,
    .llseek = no_llseek,
};
// @loppu misc

// @alku sysfs
// sysfs: yksi arvo tiedostoa kohden, tekstinä. Attribuutit ilmestyvät
// laitteen hakemistoon /sys/devices/platform/9010000.herateajastin/.
static ssize_t laskuri_show(struct device *dev, struct device_attribute *a,
                            char *puskuri)
{
    struct herate *h = dev_get_drvdata(dev);

    return sysfs_emit(puskuri, "%u\n", readl(h->rek + RTCDR));
}
static DEVICE_ATTR_RO(laskuri);

static ssize_t heratyksia_show(struct device *dev,
                               struct device_attribute *a, char *puskuri)
{
    struct herate *h = dev_get_drvdata(dev);

    return sysfs_emit(puskuri, "%u\n", READ_ONCE(h->heratyksia));
}
static DEVICE_ATTR_RO(heratyksia);

static ssize_t jakso_show(struct device *dev, struct device_attribute *a,
                          char *puskuri)
{
    struct herate *h = dev_get_drvdata(dev);

    return sysfs_emit(puskuri, "%u\n", READ_ONCE(h->jakso));
}

static ssize_t jakso_store(struct device *dev, struct device_attribute *a,
                           const char *puskuri, size_t pituus)
{
    struct herate *h = dev_get_drvdata(dev);
    unsigned long liput;
    u32 arvo;
    int virhe = kstrtou32(puskuri, 10, &arvo);

    if (virhe)
        return virhe;
    if (arvo > 3600)
        return -ERANGE;
    spin_lock_irqsave(&h->lukko, liput);
    h->jakso = arvo;
    if (arvo == 0)
        writel(0, h->rek + RTCIMSC);  // 0 lopettaa jaksollisen herätyksen
    spin_unlock_irqrestore(&h->lukko, liput);
    return pituus;
}
static DEVICE_ATTR_RW(jakso);

static struct attribute *herate_attrs[] = {
    &dev_attr_laskuri.attr,
    &dev_attr_heratyksia.attr,
    &dev_attr_jakso.attr,
    NULL,
};
ATTRIBUTE_GROUPS(herate);
// @loppu sysfs

// @alku debugfs
// debugfs: kehittäjän työkalu, ei vakaa rajapinta. Rekisterivedos
// seq_file-rajapinnalla.
static int rekisterit_show(struct seq_file *s, void *data)
{
    struct herate *h = s->private;
    static const struct { const char *nimi; u32 siirtyma; } r[] = {
        {"RTCDR", RTCDR}, {"RTCMR", RTCMR}, {"RTCIMSC", RTCIMSC},
        {"RTCMIS", RTCMIS},
    };

    for (int i = 0; i < ARRAY_SIZE(r); i++)
        seq_printf(s, "%-8s 0x%08x\n", r[i].nimi,
                   readl(h->rek + r[i].siirtyma));
    return 0;
}
DEFINE_SHOW_ATTRIBUTE(rekisterit);

static void herate_debugfs(struct herate *h)
{
    h->debug = debugfs_create_dir(dev_name(h->dev), NULL);
    debugfs_create_file("rekisterit", 0400, h->debug, h,
                        &rekisterit_fops);
    debugfs_create_u32("heratyksia", 0400, h->debug, &h->heratyksia);
}
// @loppu debugfs

// @alku tunnista
static u32 herate_tunniste(void __iomem *rek)
{
    u32 tunniste = 0;

    // Neljä 8-bittistä rekisteriä muodostavat 32-bittisen tunnisteen.
    for (int i = 0; i < 4; i++)
        tunniste |= (readl(rek + RTCPERIPHID0 + 4 * i) & 0xff) << (8 * i);
    return tunniste;
}
// @loppu tunnista

// @alku probe
static int herate_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct herate *h;
    u32 tunniste;
    int irq, virhe;

    // devm_-varaukset vapautuvat automaattisesti, kun laite irrotetaan
    // tai probe epäonnistuu.
    h = devm_kzalloc(dev, sizeof(*h), GFP_KERNEL);
    if (!h)
        return -ENOMEM;
    h->dev = dev;
    h->rek = devm_platform_ioremap_resource(pdev, 0);  // laitepuun reg
    if (IS_ERR(h->rek))
        return PTR_ERR(h->rek);
    tunniste = herate_tunniste(h->rek);
    if ((tunniste & TUNNISTE_MASKI) != PL031_TUNNISTE)
        return dev_err_probe(dev, -ENODEV, "tuntematon laite %08x\n",
                             tunniste);

    // Laitepuun valinnaiset ominaisuudet oletusarvoineen.
    h->nimi = "herate";
    of_property_read_string(dev->of_node, "label", &h->nimi);
    h->oletusviive = 1;
    of_property_read_u32(dev->of_node, "tutoriaalit,oletusviive-s",
                         &h->oletusviive);

    spin_lock_init(&h->lukko);
    mutex_init(&h->asetus);
    init_waitqueue_head(&h->odottajat);
    INIT_DELAYED_WORK(&h->vahti, herate_vahti);

    writel(0, h->rek + RTCIMSC);
    writel(1, h->rek + RTCICR);
    writel(0, h->rek + RTCLR);   // laskuri alkaa nollasta

    irq = platform_get_irq(pdev, 0);  // laitepuun interrupts
    if (irq < 0)
        return irq;
    virhe = devm_request_threaded_irq(dev, irq, herate_irq, herate_saie,
                                      0, dev_name(dev), h);
    if (virhe)
        return dev_err_probe(dev, virhe, "keskeytys %d\n", irq);

    h->misc.minor = MISC_DYNAMIC_MINOR;
    h->misc.name = "herate";
    h->misc.fops = &herate_fops;
    h->misc.parent = dev;
    virhe = misc_register(&h->misc);
    if (virhe)
        return virhe;
    platform_set_drvdata(pdev, h);
    herate_debugfs(h);
    dev_info(dev, "%s: PL031, oletusviive %u s\n", h->nimi,
             h->oletusviive);
    return 0;
}

static void herate_remove(struct platform_device *pdev)
{
    struct herate *h = platform_get_drvdata(pdev);

    debugfs_remove_recursive(h->debug);
    misc_deregister(&h->misc);
    writel(0, h->rek + RTCIMSC);
    cancel_delayed_work_sync(&h->vahti);
    dev_info(&pdev->dev, "irrotettu, keskeytyksia %u\n", h->heratyksia);
    // devm vapauttaa keskeytyksen, ioremapin ja muistin tämän jälkeen.
}
// @loppu probe

// @alku ajuri
static const struct of_device_id herate_of_match[] = {
    { .compatible = "tutoriaalit,herateajastin" },
    { }
};
MODULE_DEVICE_TABLE(of, herate_of_match);

static struct platform_driver herate_ajuri = {
    .probe = herate_probe,
    .remove_new = herate_remove,
    .driver = {
        .name = "herate",
        .of_match_table = herate_of_match,
        .dev_groups = herate_groups,
    },
};
module_platform_driver(herate_ajuri);
// @loppu ajuri

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Herätysajastin PL031-reaaliaikakellolle");

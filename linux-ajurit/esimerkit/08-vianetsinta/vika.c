// Vianetsinnän harjoitusmoduuli: debugfs-hakemiston /sys/kernel/debug/vika
// tiedostot käynnistävät kukin yhden tyypillisen ajurivirheen, jotta
// ytimen tarkistimien ilmoituksia voi harjoitella lukemaan. Moduuli on
// tarkoituksella virheellinen; älä lataa sitä tuotantojärjestelmään.
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/debugfs.h>
#include <linux/fs.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>

// @alku laske
struct mittaus {
    const char *nimi;
    int arvo;
};

// noinline: funktiot näkyvät omina niminään jäljityksessä ja
// kaatumisilmoituksessa.
static noinline int vika_summa(const struct mittaus *m, int n)
{
    int summa = 0;

    for (int i = 0; i < n; i++) {
        pr_debug("%s = %d\n", m[i].nimi, m[i].arvo);
        summa += m[i].arvo;
    }
    return summa;
}

static noinline void vika_laske(void)
{
    static const struct mittaus m[] = {{"tulo", 21}, {"meno", 19}};

    pr_info("summa %d\n", vika_summa(m, ARRAY_SIZE(m)));
}
// @loppu laske

// @alku kaada
static struct mittaus *viimeisin;  // ei koskaan asetettu: NULL

static noinline int vika_lue_viimeisin(void)
{
    return viimeisin->arvo;  // NULL-osoittimen käyttö
}
// @loppu kaada

// @alku nuku
static DEFINE_SPINLOCK(tilalukko);
static DEFINE_MUTEX(asetukset);
static DEFINE_MUTEX(laite);

static noinline void vika_nuku_lukossa(void)
{
    spin_lock(&tilalukko);
    mutex_lock(&asetukset);   // väärin: mutex voi nukkua
    mutex_unlock(&asetukset);
    spin_unlock(&tilalukko);
}
// @loppu nuku

// @alku jarjestys

static noinline void vika_tallenna(void)
{
    mutex_lock(&asetukset);
    mutex_lock(&laite);       // järjestys: asetukset, laite
    mutex_unlock(&laite);
    mutex_unlock(&asetukset);
}

static noinline void vika_palauta(void)
{
    mutex_lock(&laite);
    mutex_lock(&asetukset);   // järjestys: laite, asetukset
    mutex_unlock(&asetukset);
    mutex_unlock(&laite);
}
// @loppu jarjestys

// Jokainen debugfs-tiedosto tunnistetaan inoden yksityisestä datasta.
enum toiminto { LASKE, KAADA, NUKU, JARJESTYS };

static ssize_t vika_kirjoita(struct file *tiedosto, const char __user *p,
                             size_t pituus, loff_t *kohta)
{
    switch ((long)file_inode(tiedosto)->i_private) {
    case LASKE:
        vika_laske();
        break;
    case KAADA:
        pr_info("arvo %d\n", vika_lue_viimeisin());
        break;
    case NUKU:
        vika_nuku_lukossa();
        break;
    case JARJESTYS:
        vika_tallenna();
        vika_palauta();
        break;
    }
    return pituus;
}

static const struct file_operations vika_fops = {
    .owner = THIS_MODULE,
    .write = vika_kirjoita,
};

static struct dentry *hakemisto;

static int __init vika_alku(void)
{
    static const char *const nimet[] = {"laske", "kaada", "nuku",
                                        "jarjestys"};

    hakemisto = debugfs_create_dir("vika", NULL);
    for (long i = 0; i < ARRAY_SIZE(nimet); i++)
        debugfs_create_file(nimet[i], 0200, hakemisto, (void *)i,
                            &vika_fops);
    return 0;
}

static void __exit vika_loppu(void)
{
    debugfs_remove_recursive(hakemisto);
}

module_init(vika_alku);
module_exit(vika_loppu);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Tarkoituksella virheellinen moduuli vianetsintään");

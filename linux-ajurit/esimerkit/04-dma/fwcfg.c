// QEMU:n fw_cfg-laitteen DMA-ajuri. fw_cfg välittää vieraalle tiedostoja
// (-fw_cfg name=opt/...,file=...). Laite kopioi tiedoston sisällön
// vieraan muistiin DMA:lla, kun ajuri kirjoittaa ohjausrakenteen
// osoitteen laitteen DMA-rekisteriin.
//
// Ajuri näyttää DMA-rajapinnan molemmat muodot: ohjausrakenne on
// koherentissa muistissa (dma_alloc_coherent), ja tiedoston sisältö
// luetaan tavalliseen kmalloc-puskuriin virtauskuvauksella
// (dma_map_single).
#include <linux/debugfs.h>
#include <linux/dma-mapping.h>
#include <linux/io.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/of_address.h>
#include <linux/platform_device.h>
#include <linux/slab.h>
#include <linux/string.h>

static char *tiedosto = "opt/tutoriaalit/viesti";
module_param(tiedosto, charp, 0444);
MODULE_PARM_DESC(tiedosto, "luettavan fw_cfg-tiedoston nimi");

// @alku rajapinta
// Laitteen rekisterit (QEMU docs/specs/fw_cfg.rst, MMIO-versio).
#define FW_CFG_DATA       0x00
#define FW_CFG_VALITSIN   0x08   // 16 bittiä, iso tavujärjestys
#define FW_CFG_DMA        0x10   // 64 bittiä, iso tavujärjestys

#define FW_CFG_TUNNISTE   0x0000 // "QEMU"
#define FW_CFG_HAKEMISTO  0x0019 // tiedostoluettelo

// DMA-ohjausrakenne laitteen muodossa: kaikki kentät isoa tavujärjestystä.
struct fw_cfg_dma {
    __be32 ohjaus;
    __be32 pituus;
    __be64 osoite;
} __packed;

#define DMA_VIRHE   BIT(0)
#define DMA_LUKU    BIT(1)
#define DMA_VALITSE BIT(3)

struct fw_cfg_tiedosto {      // hakemiston alkio
    __be32 koko;
    __be16 valitsin;
    __be16 varattu;
    char nimi[56];
} __packed;
// @loppu rajapinta

struct fwcfg {
    struct device *dev;
    void __iomem *rek;
    struct fw_cfg_dma *ohjaus;   // CPU:n osoite koherenttiin muistiin
    dma_addr_t ohjaus_dma;       // laitteen näkemä osoite samaan muistiin
    struct debugfs_blob_wrapper blob;
    struct dentry *debug;
};

// @alku siirto
// Lukee pituus tavua valitsimen kohteesta laitteen osoitteeseen kohde.
static int fwcfg_dma(struct fwcfg *f, u16 valitsin, dma_addr_t kohde,
                     u32 pituus)
{
    u32 ohjaus = DMA_LUKU | DMA_VALITSE | ((u32)valitsin << 16);

    WRITE_ONCE(f->ohjaus->ohjaus, cpu_to_be32(ohjaus));
    f->ohjaus->pituus = cpu_to_be32(pituus);
    f->ohjaus->osoite = cpu_to_be64(kohde);
    // Kenttien on näyttävä laitteelle ennen käynnistystä. iowrite32be
    // käyttää writel:iä, joka tekee muistiesteen (wmb) ennen kirjoitusta.
    iowrite32be(upper_32_bits(f->ohjaus_dma), f->rek + FW_CFG_DMA);
    iowrite32be(lower_32_bits(f->ohjaus_dma), f->rek + FW_CFG_DMA + 4);
    // QEMU suorittaa siirron heti; oikea laite valmistuisi myöhemmin,
    // ja ajuri odottaisi keskeytystä tai tarkistaisi tilan ajastimella.
    for (int kierros = 0; kierros < 1000; kierros++) {
        u32 tila = be32_to_cpu(READ_ONCE(f->ohjaus->ohjaus));

        if (tila & DMA_VIRHE)
            return -EIO;
        if (tila == 0)
            return 0;
        cpu_relax();
    }
    return -ETIMEDOUT;
}
// @loppu siirto

// @alku etsi
// Hakemisto: 32-bittinen alkioiden määrä ja alkiot. Luetaan se
// koherenttiin puskuriin.
static int fwcfg_etsi(struct fwcfg *f, const char *nimi, u16 *valitsin,
                      u32 *koko)
{
    struct fw_cfg_tiedosto *alkiot;
    dma_addr_t dma;
    size_t tavut = 4 + 64 * sizeof(*alkiot);
    __be32 *maara;
    int virhe;

    maara = dma_alloc_coherent(f->dev, tavut, &dma, GFP_KERNEL);
    if (!maara)
        return -ENOMEM;
    virhe = fwcfg_dma(f, FW_CFG_HAKEMISTO, dma, tavut);
    if (!virhe) {
        u32 n = min_t(u32, be32_to_cpu(*maara), 64);

        alkiot = (struct fw_cfg_tiedosto *)(maara + 1);
        virhe = -ENOENT;
        for (u32 i = 0; i < n; i++) {
            if (strncmp(alkiot[i].nimi, nimi, sizeof(alkiot[i].nimi)))
                continue;
            *valitsin = be16_to_cpu(alkiot[i].valitsin);
            *koko = be32_to_cpu(alkiot[i].koko);
            virhe = 0;
            break;
        }
    }
    dma_free_coherent(f->dev, tavut, maara, dma);
    return virhe;
}
// @loppu etsi

// @alku lue
// Tiedoston sisältö luetaan kmalloc-puskuriin. dma_map_single antaa
// laitteelle osoitteen ja hoitaa välimuistin: ei-koherentilla laitteella
// se mitätöi puskurin välimuistirivit, jotta CPU ei lue vanhaa dataa.
static void *fwcfg_lue(struct fwcfg *f, u16 valitsin, u32 koko)
{
    void *puskuri = kmalloc(koko, GFP_KERNEL);
    dma_addr_t dma;
    int virhe;

    if (!puskuri)
        return ERR_PTR(-ENOMEM);
    dma = dma_map_single(f->dev, puskuri, koko, DMA_FROM_DEVICE);
    if (dma_mapping_error(f->dev, dma)) {
        kfree(puskuri);
        return ERR_PTR(-ENOMEM);
    }
    virhe = fwcfg_dma(f, valitsin, dma, koko);
    // Vasta kuvauksen purun jälkeen puskuri kuuluu taas CPU:lle.
    dma_unmap_single(f->dev, dma, koko, DMA_FROM_DEVICE);
    if (virhe) {
        kfree(puskuri);
        return ERR_PTR(virhe);
    }
    return puskuri;
}
// @loppu lue

// @alku probe
static int fwcfg_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    struct fwcfg *f;
    char tunniste[5] = "";
    u16 valitsin;
    u32 koko;
    void *sisalto;
    int virhe;

    f = devm_kzalloc(dev, sizeof(*f), GFP_KERNEL);
    if (!f)
        return -ENOMEM;
    f->dev = dev;
    f->rek = devm_platform_ioremap_resource(pdev, 0);
    if (IS_ERR(f->rek))
        return PTR_ERR(f->rek);

    // Tunniste luetaan ilman DMA:ta datarekisterin kautta tavu kerrallaan.
    iowrite16be(FW_CFG_TUNNISTE, f->rek + FW_CFG_VALITSIN);
    for (int i = 0; i < 4; i++)
        tunniste[i] = ioread8(f->rek + FW_CFG_DATA);
    if (strcmp(tunniste, "QEMU"))
        return dev_err_probe(dev, -ENODEV, "ei fw_cfg-laite\n");

    // Laite osaa 64-bittiset osoitteet. Ilman tätä ydin olettaa 32 bittiä.
    virhe = dma_set_mask_and_coherent(dev, DMA_BIT_MASK(64));
    if (virhe)
        return virhe;
    dev_info(dev, "laitepuussa dma-coherent: %s\n",
             of_dma_is_coherent(dev->of_node) ? "on" : "ei");

    f->ohjaus = dmam_alloc_coherent(dev, sizeof(*f->ohjaus),
                                    &f->ohjaus_dma, GFP_KERNEL);
    if (!f->ohjaus)
        return -ENOMEM;

    virhe = fwcfg_etsi(f, tiedosto, &valitsin, &koko);
    if (virhe)
        return dev_err_probe(dev, virhe, "%s puuttuu\n", tiedosto);
    sisalto = fwcfg_lue(f, valitsin, koko);
    if (IS_ERR(sisalto))
        return PTR_ERR(sisalto);
    dev_info(dev, "%s: valitsin 0x%04x, %u tavua\n", tiedosto, valitsin,
             koko);

    f->blob.data = sisalto;
    f->blob.size = koko;
    f->debug = debugfs_create_dir("fwcfg", NULL);
    debugfs_create_blob("sisalto", 0400, f->debug, &f->blob);
    platform_set_drvdata(pdev, f);
    return 0;
}

static void fwcfg_remove(struct platform_device *pdev)
{
    struct fwcfg *f = platform_get_drvdata(pdev);

    debugfs_remove_recursive(f->debug);
    kfree(f->blob.data);
}
// @loppu probe

static const struct of_device_id fwcfg_of_match[] = {
    { .compatible = "qemu,fw-cfg-mmio" },
    { }
};
MODULE_DEVICE_TABLE(of, fwcfg_of_match);

static struct platform_driver fwcfg_ajuri = {
    .probe = fwcfg_probe,
    .remove_new = fwcfg_remove,
    .driver = {
        .name = "tutor-fwcfg",
        .of_match_table = fwcfg_of_match,
    },
};
module_platform_driver(fwcfg_ajuri);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("QEMU:n fw_cfg-tiedostojen luku DMA:lla");

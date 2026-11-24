// Ohjelmallinen SPI-ohjain, jonka väylällä on simuloitu 256-tavuinen
// sarjamuistipiiri. QEMU:n virt-koneessa ei ole SPI-ohjainta, joten
// ohjain ja piiri ovat ohjelmaa; SPI-alijärjestelmä ja piirin ajuri
// (muisti.c) eivät näe eroa oikeaan laitteistoon.
//
// Moduuli luo itselleen platform-laitteen, ohjaimen ja väylälle yhden
// laitteen (spi_new_device), kuten piirin ajuri tai laitepuu tekisi.
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/spi/spi.h>

// @alku piiri
// Piirin komennot ovat tavallisen SPI-flash-muistin komentoja.
#define KOM_KIRJOITA  0x02  // osoite, data (vaatii kirjoitusluvan)
#define KOM_LUE       0x03  // osoite, sitten dataa
#define KOM_TILA      0x05  // tilarekisteri
#define KOM_LUPA      0x06  // kirjoituslupa (WEL)
#define KOM_TUNNISTE  0x9f  // valmistaja, tyyppi, koko
#define TILA_WEL      BIT(1)

struct vspi_piiri {
    u8 muisti[256];
    u8 tila;
    // Komennon tila: tavuja vastaanotettu tämän CS-jakson aikana.
    unsigned int tavu;
    u8 komento;
    u8 osoite;
};

// Yksi tavu kumpaankin suuntaan: SPI on aina kaksisuuntainen.
static u8 vspi_tavu(struct vspi_piiri *p, u8 sisaan)
{
    static const u8 tunniste[] = {0x5a, 0x01, 0x08};
    unsigned int n = p->tavu++;
    u8 ulos = 0xff;

    if (n == 0) {
        p->komento = sisaan;
        if (sisaan == KOM_LUPA)
            p->tila |= TILA_WEL;
        return ulos;
    }
    switch (p->komento) {
    case KOM_TUNNISTE:
        ulos = n <= 3 ? tunniste[n - 1] : 0xff;
        break;
    case KOM_TILA:
        ulos = p->tila;
        break;
    case KOM_LUE:
        if (n == 1)
            p->osoite = sisaan;
        else
            ulos = p->muisti[p->osoite++];
        break;
    case KOM_KIRJOITA:
        if (n == 1)
            p->osoite = sisaan;
        else if (p->tila & TILA_WEL)
            p->muisti[p->osoite++] = sisaan;
        break;
    }
    return ulos;
}
// @loppu piiri

// @alku ohjain
// SPI-ydin kutsuu set_cs-funktiota linjan tasolla: false = CS alhaalla eli
// valittu, koska CS on aktiivinen alhaalla.
static void vspi_cs(struct spi_device *spi, bool taso)
{
    struct vspi_piiri *p = spi_controller_get_devdata(spi->controller);

    if (!taso) {
        p->tavu = 0;
        dev_dbg(&spi->dev, "CS valittu\n");
    } else {
        // Kirjoitus päättyy CS:n nousuun; lupa kuluu.
        if (p->komento == KOM_KIRJOITA && p->tavu > 2)
            p->tila &= ~TILA_WEL;
        dev_dbg(&spi->dev, "CS vapautettu, %u tavua\n", p->tavu);
    }
}

// Yksi siirto (spi_transfer): tx_buf ja rx_buf voivat kumpikin puuttua.
static int vspi_siirto(struct spi_controller *ohjain,
                       struct spi_device *spi, struct spi_transfer *s)
{
    struct vspi_piiri *p = spi_controller_get_devdata(ohjain);
    const u8 *tx = s->tx_buf;
    u8 *rx = s->rx_buf;

    for (unsigned int i = 0; i < s->len; i++) {
        u8 ulos = vspi_tavu(p, tx ? tx[i] : 0xff);

        if (rx)
            rx[i] = ulos;
    }
    dev_dbg(&spi->dev, "siirto %u tavua%s%s\n", s->len, tx ? " tx" : "",
            rx ? " rx" : "");
    return 0;  // 0: siirto valmis, ei tarvitse odottaa keskeytystä
}
// @loppu ohjain

// @alku probe
static int vspi_probe(struct platform_device *pdev)
{
    struct spi_controller *ohjain;
    struct vspi_piiri *p;
    struct spi_board_info laite = {
        .modalias = "tutor-muisti",  // ajuri valitaan tällä nimellä
        .max_speed_hz = 10000000,
        .chip_select = 0,
        .mode = SPI_MODE_0,
    };
    int virhe;

    ohjain = devm_spi_alloc_host(&pdev->dev, sizeof(*p));
    if (!ohjain)
        return -ENOMEM;
    p = spi_controller_get_devdata(ohjain);
    memset(p->muisti, 0xff, sizeof(p->muisti));  // tyhjä flash
    ohjain->bus_num = -1;            // ydin valitsee väylän numeron
    ohjain->num_chipselect = 1;
    ohjain->mode_bits = SPI_CPOL | SPI_CPHA;
    ohjain->bits_per_word_mask = SPI_BPW_MASK(8);
    ohjain->set_cs = vspi_cs;
    ohjain->transfer_one = vspi_siirto;
    virhe = devm_spi_register_controller(&pdev->dev, ohjain);
    if (virhe)
        return virhe;
    if (!spi_new_device(ohjain, &laite))
        return -ENODEV;
    dev_info(&pdev->dev, "ohjain spi%d\n", ohjain->bus_num);
    return 0;
}
// @loppu probe

static struct platform_driver vspi_ajuri = {
    .probe = vspi_probe,
    .driver = { .name = "vspi" },
};

// @alku moduuli
static struct platform_device *vspi_laite;

static int __init vspi_alku(void)
{
    int virhe = platform_driver_register(&vspi_ajuri);

    if (virhe)
        return virhe;
    // Oikeassa järjestelmässä laite tulisi laitepuusta.
    vspi_laite = platform_device_register_simple("vspi", -1, NULL, 0);
    if (IS_ERR(vspi_laite)) {
        platform_driver_unregister(&vspi_ajuri);
        return PTR_ERR(vspi_laite);
    }
    return 0;
}

static void __exit vspi_loppu(void)
{
    platform_device_unregister(vspi_laite);
    platform_driver_unregister(&vspi_ajuri);
}

module_init(vspi_alku);
module_exit(vspi_loppu);
// @loppu moduuli
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Ohjelmallinen SPI-ohjain ja simuloitu muistipiiri");

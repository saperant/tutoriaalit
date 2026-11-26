// Näytekello: pieni kellon tarjoaja (clock provider). Se jakaa laitepuussa
// annetun vanhemman kellon kokonaisluvulla ja kytkee tuloksen päälle ja
// pois. Oikeassa piirissä nämä operaatiot kirjoittaisivat kellonhallinnan
// rekistereihin; tässä tila on muistissa ja muutokset kirjataan lokiin.
#include <linux/clk-provider.h>
#include <linux/minmax.h>
#include <linux/module.h>
#include <linux/of.h>
#include <linux/platform_device.h>

#define SUURIN_JAKAJA 4096

struct jakokello {
    struct clk_hw hw;       // kellokehyksen näkymä tähän kelloon
    struct device *dev;
    unsigned long jakaja;
    bool paalla;
};

static struct jakokello *kellosta(struct clk_hw *hw)
{
    return container_of(hw, struct jakokello, hw);
}

// @alku ops
// enable ja disable kutsutaan spinlock pidettynä: ne eivät saa nukkua.
// Hitaat toimet, kuten PLL:n lukittumisen odotus, kuuluvat
// prepare-operaatioon.
static int jakokello_enable(struct clk_hw *hw)
{
    struct jakokello *k = kellosta(hw);

    k->paalla = true;
    dev_info(k->dev, "paalle\n");
    return 0;
}

static void jakokello_disable(struct clk_hw *hw)
{
    struct jakokello *k = kellosta(hw);

    k->paalla = false;
    dev_info(k->dev, "pois\n");
}

static int jakokello_is_enabled(struct clk_hw *hw)
{
    return kellosta(hw)->paalla;
}

static unsigned long jakokello_recalc_rate(struct clk_hw *hw,
                                           unsigned long vanhempi)
{
    return vanhempi / kellosta(hw)->jakaja;
}

// Kuluttaja pyytää taajuutta; tarjoaja kertoo, minkä se pystyy
// tuottamaan. Kokonaislukujakaja ei osu jokaiseen taajuuteen.
static int jakokello_determine_rate(struct clk_hw *hw,
                                    struct clk_rate_request *pyynto)
{
    unsigned long vanhempi = pyynto->best_parent_rate;
    unsigned long jakaja = DIV_ROUND_CLOSEST(vanhempi,
                                             max(pyynto->rate, 1UL));

    pyynto->rate = vanhempi / clamp(jakaja, 1UL, SUURIN_JAKAJA);
    return 0;
}

static int jakokello_set_rate(struct clk_hw *hw, unsigned long taajuus,
                              unsigned long vanhempi)
{
    struct jakokello *k = kellosta(hw);

    k->jakaja = vanhempi / taajuus;
    dev_info(k->dev, "jakaja %lu: %lu Hz\n", k->jakaja,
             vanhempi / k->jakaja);
    return 0;
}

static const struct clk_ops jakokello_ops = {
    .enable = jakokello_enable,
    .disable = jakokello_disable,
    .is_enabled = jakokello_is_enabled,
    .recalc_rate = jakokello_recalc_rate,
    .determine_rate = jakokello_determine_rate,
    .set_rate = jakokello_set_rate,
};
// @loppu ops

static int jakokello_probe(struct platform_device *pdev)
{
    struct device *dev = &pdev->dev;
    // Vanhempi on laitepuun clocks-ominaisuuden ensimmäinen kello.
    static const struct clk_parent_data vanhempi = { .index = 0 };
    struct clk_init_data alku = {
        .name = dev->of_node->name,
        .ops = &jakokello_ops,
        .parent_data = &vanhempi,
        .num_parents = 1,
    };
    struct jakokello *k;
    int virhe;

    k = devm_kzalloc(dev, sizeof(*k), GFP_KERNEL);
    if (!k)
        return -ENOMEM;
    k->dev = dev;
    k->jakaja = 24;
    k->hw.init = &alku;
    of_property_read_string(dev->of_node, "clock-output-names",
                            &alku.name);
    virhe = devm_clk_hw_register(dev, &k->hw);
    if (virhe)
        return dev_err_probe(dev, virhe, "rekisterointi ei onnistu\n");
    // Tästä eteenpäin kuluttajan clocks = <&naytekello> löytää kellon.
    virhe = devm_of_clk_add_hw_provider(dev, of_clk_hw_simple_get,
                                        &k->hw);
    if (virhe)
        return virhe;
    dev_info(dev, "tarjolla, %lu Hz\n", clk_hw_get_rate(&k->hw));
    return 0;
}

static const struct of_device_id jakokello_of[] = {
    { .compatible = "tutoriaalit,jakokello" },
    { }
};
MODULE_DEVICE_TABLE(of, jakokello_of);

static struct platform_driver jakokello_ajuri = {
    .probe = jakokello_probe,
    .driver = {
        .name = "jakokello",
        .of_match_table = jakokello_of,
        // Kuluttajat pitävät kelloa: ajuria ei irroteta käsin.
        .suppress_bind_attrs = true,
    },
};
module_platform_driver(jakokello_ajuri);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Jakava ja portittava kello (kellon tarjoaja)");

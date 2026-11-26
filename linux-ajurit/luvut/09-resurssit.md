# Kellot, jännitteet ja GPIO-linjat

Tähänastisille laitteille riitti rekisterialue ja keskeytys. Oikean
piirilevyn oheislaite tarvitsee enemmän: käyttöjännitteen, joka on
kytkettävä päälle, kellon, jonka taajuus on asetettava, nollauslinjan,
joka on vapautettava oikealla hetkellä, ja usein muutaman GPIO-linjan.
Nämä tulevat toisilta laitteilta, joilla on omat ajurinsa. Ajuri ei
ohjaa niitä itse vaan pyytää niitä ytimen kehyksiltä nimellä, ja
laitepuu kertoo, mistä kukin tulee.

Tässä luvussa kirjoitetaan ajuri kuvitteelliselle paineanturille, joka
tarvitsee kaikki neljä. Virt-koneessa ei ole anturia eikä sen
ympäristöä, joten ympäristö kootaan ytimen omista ohjelmallisista
osista: GPIO-simulaattorista (`gpio-sim`) ja kiinteästä säätimestä
(`regulator-fixed`). Kellon tarjoaja kirjoitetaan itse, jotta kehyksen
toinen puoli tulee näkyviin. Ajurin koodi on silti sama kuin oikean
piirin ajurissa, koska se puhuu vain kehysten rajapinnoille. Sama pätee
I2C- ja SPI-laitteen ajuriin: resurssit haetaan samoilla funktioilla
väylästä riippumatta.

```{.dot otsikko="Paineanturin resurssit. Nuoli osoittaa tarjoajasta kuluttajaan; katkoviivalla piirretyt laitteet ovat ohjelmallisia."}
digraph {
  rankdir=LR; node [shape=box];
  pclk [label="clk24mhz\n(koneen kiinteä kello)"];
  kello [label="naytekello\n(ajuri jakokello)"];
  gpio [label="gpio-simulator\n(linjat 0–3)", style="rounded,dashed"];
  saadin [label="saadin-vdd-anturi\n(regulator-fixed)", style="rounded,dashed"];
  anturi [label="paineanturi\n(ajuri paine)", style="rounded,dashed"];
  pclk -> kello [label="24 MHz"];
  kello -> anturi [label="clocks"];
  gpio -> saadin [label="linja 0: kytkin"];
  saadin -> anturi [label="vdd-supply"];
  gpio -> anturi [label="linja 1: reset\nlinja 2: halytys"];
}
```

Ytimen asetuksiin tarvitaan säädin- ja GPIO-kehys sekä seuraavan luvun
virranhallinta. Kellokehys (`COMMON_CLK`) on ARM64-ytimessä aina
mukana:

```{.ini tiedosto="esimerkit/ymparisto/ajurit.config" osa="virta"}
```

## Resurssit laitepuussa

Kuluttajan solmu viittaa tarjoajiin *phandle*-viittauksilla, ja
jokaisella kehyksellä on oma ominaisuutensa:

```{.c tiedosto="esimerkit/07-resurssit/paine.dtsi"}
```

| Resurssi | Ominaisuus kuluttajassa | Tarjoajan merkintä |
|----------|-------------------------|--------------------|
| kello | `clocks`, nimet `clock-names` | `#clock-cells` |
| jännite | `<nimi>-supply` | `regulator-`-ominaisuudet |
| GPIO-linja | `<nimi>-gpios` | `gpio-controller`, `#gpio-cells` |
| nollaus | `resets` tai `reset-gpios` | `#reset-cells` |
| nastojen asetus | `pinctrl-0`, `pinctrl-names` | nasta-asetusten solmut |

Viittauksen perässä olevat luvut tulkitsee tarjoaja, ja niiden määrän
kertoo sen `#...-cells`-ominaisuus. GPIO-viittauksessa `<&linjat 1 1>`
ensimmäinen luku on linjan numero ja toinen liput: 1 tarkoittaa, että
linja on aktiivinen alhaalla (`GPIO_ACTIVE_LOW`). Ominaisuuden nimen
alkuosa (`vdd`, `reset`, `halytys`) on se nimi, jolla ajuri resurssia
pyytää.

Nastojen asetus (*pinctrl*) on listan ainoa, jota ajuri ei yleensä
pyydä itse: ydin asettaa solmun `default`-tilan nastat ennen
`probe`-kutsua. Virt-koneessa ei ole nastaohjainta, joten sitä ei
käsitellä tässä pidemmälle.

## Resurssien haku

Resurssien haku on otsakkeessa `paine.h`, koska seuraavan luvun ajuri
käyttää samaa koodia:

```{.c tiedosto="esimerkit/07-resurssit/paine.h" osa="hae"}
```

Haku ei vielä kytke mitään päälle. Se antaa kahvan (`struct clk *`,
`struct regulator *`, `struct gpio_desc *`), ja kehys kirjaa ajurin
resurssin käyttäjäksi. Kolme asiaa kannattaa huomata:

- **Kahva on kuluttajakohtainen.** Usea ajuri voi pitää samaa kelloa tai
  säädintä, ja kehys laskee käyttäjät. Kello sammuu vasta, kun viimeinen
  käyttäjä on sammuttanut sen.
- **GPIO-arvot ovat loogisia.** `GPIOD_OUT_HIGH` ja
  `gpiod_set_value(..., 1)` tarkoittavat "aktiivinen". Laitepuu kertoo,
  kumpi jännitetaso se on, joten sama ajuri toimii levyllä, jossa linja
  on käännetty. Ajuri, joka kirjoittaa itse nollan tarkoittaessaan
  aktiivista, tekee käännöksen kahdesti.
- **Taajuutta pyydetään, ei määrätä.** `clk_set_rate` pyöristää
  taajuuteen, jonka tarjoaja pystyy tuottamaan, ja `clk_get_rate`
  kertoo tuloksen. Ajurin on laskettava jakajansa ja ajoituksensa
  saadusta taajuudesta.

Jos kiinteä taajuus riittää, sen voi antaa laitepuussa ominaisuudella
`assigned-clock-rates`, jolloin ydin asettaa sen ennen `probe`-kutsua
eikä ajurissa tarvita `clk_set_rate`-kutsua lainkaan.

## Kytkentäjärjestys

Piirin datalehti määrää, missä järjestyksessä jännite, kello ja nollaus
kytketään. Järjestys on ajurissa yhdessä paikassa:

```{.c tiedosto="esimerkit/07-resurssit/paine.h" osa="virta"}
```

```{.ajoituskaavio otsikko="Kytkentäjärjestys funktioissa `paine_virta_paalle` ja `paine_virta_pois` (periaatekuva koodin järjestyksestä; aika-akseli ei ole mittakaavassa)."}
{"signal": [
  {"name": "vdd", "wave": "01.....0."},
  {"name": "näytekello", "wave": "0.1...0.."},
  {"name": "nreset", "wave": "0...1.0.."},
  {"name": "vaihe", "wave": "=.=.=.=..",
   "data": ["pois", "1–2 ms", "käytössä", "pois"]}
], "config": {"hscale": 2}}
```

Kellon käyttöönotossa on kaksi vaihetta. `clk_prepare` saa nukkua, ja
siinä tehdään hitaat toimet, kuten vaihelukon käynnistys. `clk_enable`
ei saa nukkua, joten sitä voi kutsua keskeytyksessä. Ajuri, joka ei
tarvitse kelloa keskeytyskäsittelijässä, käyttää yhdistelmää
`clk_prepare_enable` ja sen vastinetta `clk_disable_unprepare`.
`gpiod_set_value_cansleep` on vastaava valinta GPIO-linjalle: GPIO-ohjain
voi olla I2C-väylän takana, jolloin linjan asettaminen nukkuu.

Jokaisella päällekytkennällä on oltava vastaava sammutus, koska kehys
laskee kutsut. Kaksi `regulator_enable`-kutsua ja yksi
`regulator_disable` jättävät säätimen päälle. Kun kelloa ja jännitettä
ei tarvitse ohjata erikseen, yhdistetyt funktiot
`devm_clk_get_enabled` ja `devm_regulator_get_enable` hakevat resurssin,
kytkevät sen päälle ja sammuttavat sen irrotuksessa.

`probe` on näiden jälkeen lyhyt:

```{.c tiedosto="esimerkit/07-resurssit/paine.c" osa="probe"}
```

`devm_add_action_or_reset` lisää oman funktion hallittujen resurssien
ketjuun. Ketju puretaan käänteisessä järjestyksessä, joten anturi
sammutetaan ennen kuin sen linjat, kello ja säädin palautetaan, eikä
ajuri tarvitse `remove`-funktiota.

## Lykätty sidonta

Ajurien latausjärjestystä ei voi määrätä. Jos anturin ajuri ladataan
ennen kellon tarjoajaa, kelloa ei vielä ole:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="lykkays"}
```

Laite jää odottamaan, ja tiedosto `devices_deferred` kertoo syyn. Kun
kellon ajuri ladataan ja sidotaan, ydin yrittää odottavia laitteita
uudelleen, ja anturin `probe` ajetaan: taajuus asetetaan, kello
kytketään päälle ja anturi käynnistyy.

Mekanismeja on kaksi. Ydin lukee laitepuun viittaukset (`clocks`,
`-supply`, `-gpios`) jo laitteita luodessaan ja tekee niistä
*laitelinkit* tarjoajan ja kuluttajan välille (*fw_devlink*). Kuluttajan
`probe`-funktiota ei kutsuta ennen kuin sen tarjoajat on sidottu; yllä
oleva rivi `supplier naytekello not ready` tulee tästä tarkistuksesta.
Kaikkia riippuvuuksia ei kuitenkaan näe laitepuusta, joten ajurin on
silti välitettävä hakufunktion `-EPROBE_DEFER` eteenpäin
`dev_err_probe`-funktiolla, kuten luvussa 4 kuvattiin. Kumpikin päätyy
samaan lykättyjen laitteiden jonoon.

```{.dot otsikko="Lykätty sidonta: anturin ajuri ladataan ennen kellon tarjoajaa."}
digraph {
  rankdir=LR; node [shape=box];
  a [label="paine.ko ladataan"];
  b [label="tarjoaja naytekello\nei ole sidottu"];
  c [label="paineanturi lykättyjen\njonoon"];
  d [label="kello.ko ladataan,\nnaytekello sidotaan"];
  e [label="ydin yrittää jonon\nlaitteet uudelleen"];
  f [label="paine: probe onnistuu"];
  a -> b -> c;
  d -> e -> f;
  c -> e [style=dashed];
}
```

## Kellon tarjoaja

Kuluttajan `clk_set_rate` ja `clk_prepare_enable` päätyvät tarjoajan
operaatioihin. Tarjoaja täyttää `clk_ops`-taulun:

```{.c tiedosto="esimerkit/07-resurssit/kello.c" osa="ops"}
```

Kehys hoitaa kaiken muun: käyttäjien laskennan, kellopuun läpikäynnin
(vanhempi kytketään päälle ennen lasta) ja taajuuden muutoksen
välittämisen alaspäin. `determine_rate` vastaa kysymykseen "mitä
pystyt tuottamaan", ja `set_rate` saa aina taajuuden, jonka
`determine_rate` on jo hyväksynyt. Pyydetty 44 100 Hz ei jakaudu
tasan 24 MHz:stä, joten kuluttaja sai 44 117 Hz.

Tarjoajan `probe` rekisteröi kellon kehykselle funktiolla
`devm_clk_hw_register` ja julkaisee sen laitepuun solmun nimissä
funktiolla `devm_of_clk_add_hw_provider`. Vasta jälkimmäisen jälkeen
kuluttajan `clocks`-viittaus löytää kellon.

Kellojen tila näkyy debugfsissä kello kerrallaan:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="kello"}
```

Koko puun yhtenä taulukkona näyttää tiedosto
`/sys/kernel/debug/clk/clk_summary`. Se on ensimmäinen paikka, josta
katsotaan, kun laitteen rekisterit lukevat pelkkää nollaa: kello on
todennäköisesti pois päältä.

## Säädin

Säätimiä ajuri ei tässä kirjoita: `regulator-fixed` on ytimen oma ajuri
säätimelle, jonka jännite on kiinteä ja jota ohjataan yhdellä
GPIO-linjalla. Tila näkyy sysfsissä:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="saadin"}
```

Säädettävältä säätimeltä kuluttaja pyytää jännitealuetta funktiolla
`regulator_set_voltage`, ja kehys sovittaa yhteen kaikkien kuluttajien
pyynnöt ja laitepuussa annetut rajat. Jos laitteen solmussa ei ole
`-supply`-ominaisuutta lainkaan, `devm_regulator_get` palauttaa
*valesäätimen* ja kirjaa siitä lokiin. Luvun 7 testissä ytimen
LM75-ajuri sai sellaisen, koska käsin luodulla I2C-laitteella ei ole
laitepuun solmua.

## GPIO-linjat ja hälytyskeskeytys

GPIO-kehyksen debugfs-tiedosto näyttää varatut linjat ja niiden
käyttäjät:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="gpio"}
```

Säätimen kytkin (linja 0) on ylhäällä. Linja 1 on anturin nollaus: ajuri
asetti sen loogiseen arvoon 0 eli "ei nollausta", ja koska linja on
laitepuussa aktiivinen alhaalla, sen taso on ylhäällä. Linja 2 on tulo.

Tulolinjasta saa keskeytyksen funktiolla `gpiod_to_irq`, ja käsittelijä
pyydetään kuten luvussa 5:

```{.c tiedosto="esimerkit/07-resurssit/paine.h" osa="halytys"}
```

Simulaattorin linjaa voi vetää ylös ja alas sysfsin kautta, mikä vastaa
sitä, että anturi nostaisi hälytyslinjansa:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="halytys"}
```

Keskeytys tulee vain nousevalla reunalla, kuten pyydettiin. Tiedoston
`/proc/interrupts` rivillä keskeytysohjaimena on simulaattorin
`irq_sim`: GPIO-ohjain on myös keskeytysohjain, ja sen linjat ovat
keskeytyksiä siinä missä piirin omat keskeytyslinjat. Jos linjaa
käytetään pelkkänä keskeytyksenä, sen voi kuvata laitepuussa myös
suoraan ominaisuudella `interrupts-extended`, jolloin ajuri hakee sen
funktiolla `platform_get_irq` eikä tarvitse GPIO-rajapintaa.

Oma nollausohjain on GPIO-linjan vaihtoehto. Monessa järjestelmäpiirissä
lohkojen nollaukset ovat yhden rekisterin bittejä, ja niitä varten on
*reset*-kehys: laitepuussa `resets = <&ohjain 3>` ja ajurissa
`devm_reset_control_get_exclusive`, `reset_control_assert` ja
`reset_control_deassert`. Rakenne on sama kuin kelloilla ja säätimillä.

## Irrotus

Kun laite irrotetaan, hallittujen resurssien ketju puretaan:

```{.tuloste tiedosto="esimerkit/testit/07-resurssit.odotettu" osa="irrotus"}
```

Anturi sammutettiin, kellolla ei ole enää käyttäjiä, säädin on pois
päältä ja anturin linjat on vapautettu. Jäljellä on vain säätimen oma
kytkinlinja, nyt alhaalla. Jos jokin näistä jäisi päälle, ajuri olisi
jättänyt sammutuksen tekemättä tai kutsunut päällekytkentää useammin
kuin sammutusta.

## Käytännössä

- **Hae resurssit nimellä laitepuusta.** Ajuri ei tiedä, mikä säädin
  tai mikä GPIO-linja sille kuuluu; se tietää vain, että se tarvitsee
  `vdd`:n ja `reset`:n.
- **Käsittele GPIO-arvoja loogisina.** Aktiivinen taso kuuluu
  laitepuuhun. Käytä `gpiod`-rajapintaa; vanhat kokonaislukunumeroihin
  perustuvat `gpio_`-funktiot ovat poistumassa.
- **Tarkista saatu taajuus.** `clk_set_rate` voi onnistua ja antaa
  silti eri taajuuden kuin pyydettiin.
- **Pidä kytkentäjärjestys yhdessä funktiossa ja sammutus sen
  peilikuvana.** Sama pari kelpaa `probe`-funktioon, irrotukseen ja
  seuraavan luvun virranhallintaan.
- **Katso tila kehyksiltä, älä arvaa.** `clk_summary`,
  `/sys/class/regulator`, `/sys/kernel/debug/gpio` ja
  `devices_deferred` kertovat, mikä on päällä, kuka sitä käyttää ja
  mitä laite odottaa.

## Itsearviointi

- Osaat kuvata laitepuussa laitteen kellon, käyttöjännitteen ja
  GPIO-linjat ja selittää, miten viittauksen luvut tulkitaan.
- Osaat hakea ajurissa kellon, säätimen ja GPIO-linjan
  `devm_`-funktioilla ja kytkeä ne päälle ja pois oikeassa
  järjestyksessä.
- Osaat selittää, miksi GPIO-arvot ovat loogisia ja mitä
  `GPIO_ACTIVE_LOW` muuttaa.
- Osaat selittää lykätyn sidonnan: laitelinkit, `-EPROBE_DEFER` ja
  tiedoston `devices_deferred`.
- Osaat kirjoittaa yksinkertaisen kellon tarjoajan ja selittää
  `determine_rate`- ja `set_rate`-operaatioiden työnjaon.
- Osaat pyytää keskeytyksen GPIO-linjalta ja tarkistaa resurssien tilan
  debugfsistä ja sysfsistä.

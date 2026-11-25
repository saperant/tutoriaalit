# Laitepuu

PC:ssä ydin löytää laitteet itse: PCI-väylän laitteet kertovat
valmistajansa ja tyyppinsä, ja ACPI-taulukot kuvaavat loput. Useimmissa
sulautetuissa piireissä laitteet ovat kiinteissä muistiosoitteissa
ilman tunnistetta, eikä ydin voi kysyä, onko osoitteessa `0x09000000`
sarjaportti. Ennen 2010-luvun alkua ARM-ytimessä oli jokaiselle piirilevylle
oma C-tiedosto, joka luetteli laitteet. Nyt tieto on *laitepuussa*
(device tree): tietorakenteessa, joka kuvaa laitteiston ja jonka
käynnistin antaa ytimelle. Sama ydinkuva käynnistyy silloin monella
eri laitteella.

## Lähde ja käännetty muoto

Laitepuu kirjoitetaan tekstinä (`.dts`, *device tree source*), ja
yhteiset osat jaetaan sisällytettäviin tiedostoihin (`.dtsi`).
Laitepuukääntäjä `dtc` kääntää sen binäärimuotoon (`.dtb`, *device tree
blob*), jonka käynnistin lataa muistiin. Ytimen lähdepuussa laitepuut
ovat hakemistossa `arch/arm64/boot/dts/<valmistaja>/`. Tyypillinen
rakenne on kolmikerroksinen: piirin `.dtsi` kuvaa kaikki piirin
oheislaitteet, moduulin `.dtsi` muistin ja virranhallinnan, ja levyn
`.dts` kertoo, mitkä oheislaitteet on käytössä ja mitä niihin on
kytketty.

```{.dot otsikko="Laitepuun lähteen kerrokset. Nimet ovat esimerkkejä; ylempi tiedosto sisällyttää alemman ja muuttaa sen solmuja."}
digraph {
  rankdir=LR; node [shape=box];
  piiri [label="piiri.dtsi\nkaikki piirin oheislaitteet,\nstatus = \"disabled\""];
  moduuli [label="moduuli.dtsi\nmuisti, virranhallinta,\neMMC"];
  levy [label="levy.dts\nkäytössä olevat laitteet,\nniihin kytketyt piirit"];
  dtb [label="levy.dtb"];
  levy -> moduuli [label="#include"];
  moduuli -> piiri [label="#include"];
  levy -> dtb [label="dtc"];
}
```

QEMU:n virt-koneen laitepuuta ei ole ytimen lähteissä, koska QEMU
tuottaa sen käynnistyksessä sen mukaan, mitä laitteita koneeseen on
lisätty. Sen saa tiedostoon koneen valitsimella `dumpdtb`, ja `dtc`
purkaa sen takaisin tekstiksi:

```{.make tiedosto="esimerkit/Makefile" osa="dumpdtb"}
```

Purku on tehtävä samoilla koneen valitsimilla kuin käynnistys, koska
muistin koko ja prosessorien määrä ovat laitepuussa. Tästä syystä
käynnistysskripti on esimerkeissä yksi ja sama (luku 1).

## Solmut ja ominaisuudet

Laitepuu on puu, jonka *solmuilla* on *ominaisuuksia*. Solmun nimi on
muotoa `nimi@yksikköosoite`, jossa yksikköosoite on laitteen
ensimmäinen osoite. Virt-koneen laitepuun ylin taso näyttää tältä:

```{.dot tiedosto="esimerkit/06-laitepuu/puu.dot" otsikko="QEMU:n virt-koneen laitepuun ylin taso: solmun nimi ja ensimmäinen `compatible`-tunniste. Katkoviivat ovat sarjaportin viittaukset toisiin solmuihin."}
```

Kaavion piirtää skripti `06-laitepuu/puu.py` käännetystä laitepuusta,
ja testi varmistaa, että se vastaa QEMU:n tuottamaa puuta. Suurin osa
solmuista on laitteita kiinteissä osoitteissa. `cpus`, `memory` ja
`chosen` ovat erikoissolmuja, ja `apb-pclk` on kello, johon laitteet
viittaavat. Puretusta virt-koneen laitepuusta sarjaportin solmu
näyttää tältä (QEMU kirjoittaa ominaisuudet käänteisessä
järjestyksessä):

```{.c tiedosto="esimerkit/06-laitepuu/pl011.dts"}
```

Ominaisuuden arvo on tavujono, ja sen tyyppi riippuu ominaisuudesta:

- **merkkijonolista**: `compatible = "arm,pl011", "arm,primecell"`;
  purettuna merkkijonot näkyvät NUL-merkillä erotettuina (`\0`)
- **32-bittisiä soluja** kulmasulkeissa: `reg = <0x00 0x9000000 0x00
  0x1000>`; solut tallennetaan isoendiantisina
- **phandle**: viittaus toiseen solmuun sen numerolla, kuten
  `clocks = <0x8000 0x8000>`
- **tyhjä**: totuusarvo, kuten `interrupt-controller;`.

Tiedostosta ominaisuuksia luetaan komennolla `fdtget`. Seuraava
skripti kokoaa tärkeimmät:

```{.bash tiedosto="esimerkit/06-laitepuu/kysely.sh" osa="kyselyt"}
```

```{.tuloste tiedosto="esimerkit/testit/06-laitepuu.odotettu"}
```

## Osoitteet: reg ja #address-cells

`reg` on lista (osoite, koko) -pareja, mutta sen solujen määrä riippuu
*vanhemman* solmun ominaisuuksista `#address-cells` ja `#size-cells`.
Virt-koneen juuressa molemmat ovat 2, joten osoite ja koko ovat
kumpikin 64-bittisiä (kaksi 32-bittistä solua): sarjaportti alkaa
osoitteesta `0x0_09000000` ja on `0x1000` tavua pitkä. Muisti alkaa
osoitteesta `0x40000000`, ja sen koko `0x10000000` on 256 Mt, sama kuin
QEMU:n valitsin `-m 256`. Prosessorisolmun `cpus` alla `#address-cells`
on 1 ja `#size-cells` 0, joten prosessorin `reg` on pelkkä numero
ilman kokoa.

Väylien alla osoitteet ovat väylän omia. I2C-väylän solmussa
`#address-cells` on 1 ja `#size-cells` 0, ja laitteen `reg` on sen
I2C-osoite, kuten `reg = <0x48>`. Vanhemman `ranges`-ominaisuus kertoo,
miten väylän osoitteet näkyvät prosessorin osoiteavaruudessa.

## Keskeytykset ja phandlet

Juuren `interrupt-parent = <0x8002>` on *phandle*: se viittaa solmuun,
jonka `phandle`-ominaisuus on `0x8002`, eli GIC-keskeytysohjaimeen
`intc@8000000`. Kaikki juuren alla olevat solmut perivät tämän
keskeytysohjaimen, ellei niissä ole omaa `interrupt-parent`-ominaisuutta.
GIC:n `#interrupt-cells = <3>` kertoo, että keskeytys kuvataan kolmella
solulla:

1. tyyppi: 0 on jaettu oheislaitekeskeytys (SPI), 1 prosessorikohtainen
   (PPI)
2. numero tyypin sisällä: sarjaportilla SPI 1, joka on GIC:n
   keskeytys 33 (SPI:t alkavat numerosta 32)
3. liipaisu: 4 on tasoliipaisu korkealla tilalla, 1 nouseva reuna.

Lähdekoodissa phandleja ei kirjoiteta numeroina vaan *nimiöinä*:
solmun eteen kirjoitetaan `gic: intc@8000000 { ... };`, ja viittaus on
`interrupt-parent = <&gic>;`. Nimiöillä levyn `.dts` muuttaa piirin
`.dtsi`:n solmuja: `&uart0 { status = "okay"; };` ottaa käyttöön
sarjaportin, jonka piirin tiedosto on määritellyt pois käytöstä
(`status = "disabled"`). Puretussa puussa nimiöitä ei ole, koska
käännös korvaa ne numeroilla.

## compatible ja ajurin sidonta

`compatible` on laitepuun tärkein ominaisuus. Se luettelee laitteen
tunnisteet tarkimmasta yleisimpään muodossa `valmistaja,malli`. Ydin
etsii jokaiselle solmulle ajuria, jonka vastaavuustaulukossa
(`of_match_table`) on jokin luettelon merkkijonoista, ja käyttää
ensimmäistä osumaa. Levyvalmistaja voi siten kirjoittaa
`compatible = "levy,uart-v2", "arm,pl011"`: jos ytimessä on oma ajuri
levyn versiolle, se valitaan, muuten yleinen PL011-ajuri.

Mitä tunnisteita ajuri hyväksyy ja mitä ominaisuuksia solmussa on
oltava, kuvataan *sidontadokumentaatiossa* (bindings), ytimen
hakemistossa `Documentation/devicetree/bindings/` YAML-skeemoina.
Työkalu `dt-validate` (paketti `dtschema`) tarkistaa laitepuun niitä
vastaan. Sidonta on rajapintasopimus: laitepuu kuvaa laitteistoa, ei
ajurin asetuksia, ja vanhan laitepuun on toimittava uudenkin ytimen
kanssa.

## Oma laite laitepuuhun

Lisätään laitepuuhun kuvitteellinen lämpöanturi. Lisäys kirjoitetaan
omaan tiedostoonsa ja liitetään puretun laitepuun perään. `dtc`
yhdistää saman polun solmut, joten myöhempi `chosen`-solmu täydentää
alkuperäistä:

```{.c tiedosto="esimerkit/06-laitepuu/anturi.dtsi" osa="anturi"}
```

Valmistajan etuliite `tutoriaalit,` erottaa omat tunnisteet ja
ominaisuudet ytimen yleisistä. Omien ominaisuuksien nimissä etuliite
on pakollinen, jotta ne eivät törmää tuleviin yleisiin ominaisuuksiin.

```{.c tiedosto="esimerkit/06-laitepuu/anturi.dtsi" osa="chosen"}
```

`chosen`-solmu ei kuvaa laitteistoa vaan käynnistimen ja ytimen välisiä
tietoja: komentorivin (`bootargs`), konsolin (`stdout-path`) ja
initramfsin sijainnin, jonka käynnistin lisää. QEMU lisää laitepuuhun
satunnaiset siemenet (`rng-seed` ydintä varten ja `kaslr-seed` ytimen
osoiteavaruuden satunnaistamiseen). Ne poistetaan, jotta käännetty
laitepuu on joka kerta sama. Oikeassa laitteessa siemenet lisää
käynnistin, ja ne ovat tärkeitä, koska sulautetun laitteen
satunnaislukugeneraattori on käynnistyksessä usein vailla entropiaa.

Muokattu laitepuu annetaan QEMU:lle valitsimella `-dtb`, ja ytimen
komentoriviä ei anneta, jolloin ydin käyttää laitepuun `bootargs`-arvoa.
Init-ohjelmana on tutkija, joka lukee ytimen näkemän laitepuun
hakemistosta `/sys/firmware/devicetree/base`. Siellä solmu on hakemisto
ja ominaisuus tiedosto, jonka sisältö on ominaisuuden raakatavut:

```{.c tiedosto="esimerkit/06-laitepuu/tutkija.c" osa="merkkijonot"}
```

Lopuksi tutkija katsoo, onko laite sidottu ajuriin. Sidottu laite on
hakemisto väylän alla, ja sen `driver`-linkki osoittaa ajuriin:

```{.c tiedosto="esimerkit/06-laitepuu/tutkija.c" osa="sidonta"}
```

```{.tuloste tiedosto="esimerkit/testit/06-anturi.odotettu"}
```

Ydin loi solmusta *platform-laitteen* nimeltä `9100000.anturi`
(osoite ja solmun nimi), mutta yksikään ajuri ei tunne tunnistetta
`tutoriaalit,lampoanturi`, joten laite jäi ilman ajuria. Sarjaportti
taas on AMBA-väylän laite, ja sen ajuri on `uart-pl011`. *Modalias* on
merkkijono, jolla `udev` tai `mdev` etsii laitteelle moduulin: siinä on
solmun nimi (`N`), tyyppi (`T`) ja tunniste (`C`). Kun moduulin
vastaavuustaulukossa on sama tunniste, `depmod` kirjaa sen, ja moduuli
latautuu automaattisesti laitteen löytyessä. Tämän anturin ajuri
kirjoitetaan taidossa *Linux-laiteajurit*.

## Laitepuun päällysteet

Kun laitteeseen voi liittää lisäkortteja, kuten Raspberry Pin HAT-kortit
tai BeagleBonen capet, jokaista yhdistelmää varten ei kannata kääntää
omaa laitepuuta. *Päällyste* (overlay, `.dtbo`) on laitepuun osa, joka
viittaa perustan nimiöihin ja lisää tai muuttaa solmuja. Lähteen
alussa on `/plugin/;`, ja `dtc` kääntää sen valitsimella `-@`, joka
säilyttää nimiöt. U-Boot liittää päällysteen ennen käynnistystä
(`fdt apply`), ja Raspberry Pin laiteohjelmisto tekee saman
`config.txt`-tiedoston `dtoverlay`-riveistä.

## Käytännössä

- **Lähde piirin ja kehityskortin laitepuusta.** Kirjoita oma levysi
  `.dts` niin, että se sisällyttää piirin `.dtsi`:n ja vain ottaa
  käyttöön (`status = "okay"`) ja konfiguroi tarvitsemasi laitteet.
- **Tarkista laitepuu sidontoja vastaan.** `make dtbs_check` ajaa
  `dt-validate`n ytimen lähdepuussa, ja omat laitteesi kannattaa kuvata
  YAML-skeemalla samalla tavalla.
- **Kuvaa laitteisto, älä ajuria.** Laitepuuhun kuuluvat osoitteet,
  keskeytykset, kellot ja kytkennät, ei ajurin puskurikokoja tai
  ohjelmiston asetuksia.
- **Pidä ydin ja laitepuu yhdessä.** Laitepuu käännetään samasta
  lähdepuusta kuin ydin ja toimitetaan sen kanssa.
- **Katso ytimen näkemää puuta.** `/sys/firmware/devicetree/base` ja
  `dtc -I fs /sys/firmware/devicetree/base` näyttävät, mitä ydin
  oikeasti sai, ja paljastavat käynnistimen tekemät muutokset.

## Itsearviointi

- Osaat selittää, miksi sulautetut järjestelmät tarvitsevat laitepuun
  ja miten `.dts`, `.dtsi` ja `.dtb` liittyvät toisiinsa.
- Osaat lukea solmun ominaisuudet ja tulkita `reg`-arvon vanhemman
  `#address-cells`- ja `#size-cells`-arvojen avulla.
- Osaat tulkita GIC-keskeytyksen kolme solua ja phandle-viittauksen.
- Osaat lisätä laitepuuhun solmun, kääntää sen ja tarkistaa
  käynnistetystä järjestelmästä, miten ydin sen näki.
- Osaat kertoa, miten `compatible` sitoo solmun ajuriin, ja mihin
  `chosen`-solmua ja päällysteitä käytetään.

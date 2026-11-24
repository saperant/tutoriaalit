# Debuggaus: SWD, gdb ja QEMU

Mikrokontrollerissa ei ole näyttöä, käyttöjärjestelmää eikä
prosessinäkymää. Silti sen sisälle näkee paremmin kuin tavallisen
tietokoneen ohjelmaan: piirin debug-logiikka voi pysäyttää ytimen,
lukea ja kirjoittaa jokaisen rekisterin ja muistiosoitteen, asettaa
katkopisteitä flashiin ja vahtia muistiviittauksia laitteistolla.
Kaikki tämä toimii kahden johtimen kautta, vaikka ohjelma olisi
täysin jumissa.

## Debug-portti

ARM:n debug-arkkitehtuuri (CoreSight) liittää ytimeen *debug-porttiin*
(Debug Access Port), jonka kautta ulkoinen *debug-sovitin* käyttää
piirin väylää. Liitäntöjä on kaksi:

| Liitäntä | Johtimet | Huomio |
|----------|----------|--------|
| JTAG | TCK, TMS, TDI, TDO, (nTRST) | vanha standardi, ketjuttaa useita piirejä |
| SWD | SWCLK, SWDIO | Cortex-M:n tavallinen, kaksi johdinta |
| SWO | yksi lähtö | valinnainen jäljitys (ITM) SWD:n rinnalla |
| nRESET | yksi | sovitin voi resetoida piirin |

Kehityskorteilla sovitin on usein samalla kortilla, ja se näkyy
tietokoneelle USB-laitteena (ST-LINK, Nordicin J-Link OB, DAPLink).
Erillisiä sovittimia ovat esimerkiksi avoimeen CMSIS-DAP-standardiin
perustuvat (Raspberry Pi Debug Probe), SEGGER J-Link ja ST-LINK.
Tietokoneella sovitinta ohjaa *gdb-palvelin*, kuten OpenOCD, pyOCD,
probe-rs tai J-Link GDB Server, ja gdb ottaa palvelimeen yhteyden
TCP:n yli:

```text
openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg   # palvelin
arm-none-eabi-gdb ohjelma.elf -ex 'target extended-remote :3333'
(gdb) monitor reset halt
(gdb) load            # ohjelmoi flashin ELF-tiedoston segmenteistä
(gdb) continue
```

Sama gdb-protokolla toimii QEMU:n kanssa, jolloin sovitinta ei
tarvita. `make gdb E=nimi` käynnistää esimerkin valitsimilla `-S` (älä
käynnistä prosessoria) ja `-s` (gdb-palvelin porttiin 1234).

## Ytimen debug-resurssit

Ytimen debug-logiikka määrää, mitä gdb voi tehdä:

| Ominaisuus | Cortex-M3/M4 | Cortex-M0+ |
|------------|--------------|------------|
| laitteistokatkopisteet (FPB) | 6 | 4 |
| vahtipisteet (DWT) | 4 | 2 |
| kellojaksolaskuri CYCCNT | on | ei |
| jäljitys ITM ja SWO | on | ei |
| käskyjäljitys | ETM (valinnainen) | MTB (valinnainen) |

*Ohjelmallinen* katkopiste korvaa käskyn `bkpt`-käskyllä, mikä
onnistuu vain RAMissa. Flashissa ajettava koodi tarvitsee
*laitteistokatkopisteen*, ja niitä on vain muutama. Jos gdb ilmoittaa
"Cannot insert hardware breakpoint", jokin vanha katkopiste on
poistettava. Myös askellus (`next`, `finish`) käyttää katkopisteitä
taustalla.

*Vahtipiste* pysäyttää ohjelman, kun tiettyyn osoitteeseen kirjoitetaan
tai sieltä luetaan. Se on paras työkalu kysymykseen "kuka muuttaa tätä
muuttujaa", johon muuten ei ole vastausta: DWT vertaa jokaista
muistiviittausta laitteistolla hidastamatta ohjelmaa.

## Istunto gdb:llä

Esimerkki `11-gdb` laskee näytteiden keskiarvon, mutta tulos on
väärä. Virhe etsitään gdb-istunnolla, joka on kirjoitettu
komentotiedostoksi, jotta se voidaan ajaa ja tarkistaa testinä.

```{.c tiedosto="esimerkit/11-gdb/main.c" osa="keskiarvo"}
```

```{.tuloste tiedosto="esimerkit/testit/11-gdb.odotettu"}
```

Ohjelma käännetään lipulla `-Og`. Lipulla `-Os` kääntäjä sijoittaa
muuttujia rekistereihin, yhdistää ja poistaa niitä sekä järjestää koodia
uudelleen, ja gdb näyttää usein `<optimized out>` tai hyppii riveillä
odottamattomasti. `-Og` optimoi vain sen verran, ettei debuggaus kärsi.
gdb käynnistää QEMU:n itse ja puhuu sille putken kautta, joten portteja
ei tarvita:

```{.sh tiedosto="esimerkit/11-gdb/qemu.sh"}
```

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="yhteys"}
```

Ensin katsotaan tilaa resetin jälkeen. Prosessori on pysähtynyt
Reset_Handlerin ensimmäiseen käskyyn, pino-osoitin on vektoritaulun
ensimmäinen sana, ja toinen sana on Reset_Handlerin osoite plus yksi
eli Thumb-bitti. Viimeinen komento lukee CPUID-rekisterin suoraan
muistista: gdb näkee koko osoiteavaruuden, myös oheislaitteet.

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="alku"}
```

Sitten katkopiste funktioon, kutsupino ja taulukon sisältö. Lauseke
`taulukko[0]@n` näyttää osoittimen takaa `n` alkiota:

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="katko"}
```

Taulukko on kunnossa, joten vika on silmukassa. Ehdollinen katkopiste
pysähtyy vain silmukan viimeisillä kierroksilla, ja `info symbol`
kertoo, mitä muistissa on taulukon jälkeen:

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="ehto"}
```

Lopuksi `finish` ajaa funktion loppuun ja näyttää paluuarvon,
vahtipiste pysäyttää ohjelman, kun tulos tallennetaan, ja ohjelma
ajetaan semihosting-lopetukseen asti:

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="finish"}
```

```{.gdb tiedosto="esimerkit/11-gdb/istunto.gdb" osa="watch"}
```

```{.tuloste tiedosto="esimerkit/testit/11-gdb-istunto.odotettu"}
```

Silmukka käy läpi indeksin 8, joka on taulukon ulkopuolella, ja lukee
seuraavan muuttujan `raja` arvon 5000. Keskiarvo (800 + 5000) / 8 =
725. Korjaus on ehto `i < n`. Koodiosoitteet on tulosteesta korvattu
pisteillä, koska ne riippuvat kääntäjän versiosta.

Hyödyllisiä komentoja sulautetussa työssä:

| Komento | Tehtävä |
|---------|---------|
| `info registers`, `p/x $sp` | rekisterit |
| `x/8wx 0x20000000` | muistin sisältö sanoina |
| `p/x *(uint32_t *)0xE000ED28` | rekisterin luku (CFSR) |
| `info symbol 0x1234`, `list *0x1234` | osoitteen funktio ja rivi |
| `watch muuttuja`, `rwatch`, `awatch` | vahtipisteet |
| `monitor reset halt` | resetointi palvelimen kautta (OpenOCD) |
| `load` | flashin ohjelmointi |
| `bt` vikakäsittelijässä | kutsupino vian kohtaan asti |

gdb osaa purkaa kutsupinon myös poikkeuskehyksen yli: kun ohjelma on
pysähtynyt vikakäsittelijään, `bt` näyttää käsittelijän alla funktion,
jossa vika sattui.

## Muut menetelmät

Debuggeri pysäyttää ohjelman, ja pysäytys muuttaa sitä, mitä tutkitaan:
moottori ei pysähdy, vaikka ohjain pysähtyy, ja tiedonsiirto
aikakatkaistaan. Ajonaikaisia menetelmiä tarvitaan siksi rinnalla:

- **GPIO ja logiikka-analysaattori.** Nastan tilan vaihto
  keskeytyskäsittelijän alussa ja lopussa näyttää sen keston ja
  viiveen nanosekuntien tarkkuudella ilman, että ohjelma hidastuu.
- **Sarjaportin loki.** Helppo, mutta hidas: 115 200 bitin sekuntinopeudella
  rivi vie millisekunnin. Lokin on oltava puskuroitu ja keskeytyksestä
  riippumaton.
- **ITM ja SWO** lähettävät tulostetta debug-portin kautta
  kellojakson tarkkuudella aikaleimattuna.
- **RTT** (SEGGER Real-Time Transfer) kirjoittaa lokin RAMissa olevaan
  rengaspuskuriin, jota sovitin lukee taustalla. Se on nopea ja toimii
  ilman ylimääräisiä nastoja.
- **assert** ja vikaraportit (luku 9), jotka tallentavat tiedoston, rivin
  ja tilan ennen uudelleenkäynnistystä.

Tuotantolaitteessa debug-portti on lukittava tai sen käyttö
todennettava, koska sen kautta saa koko laitteen hallintaansa.
Lukitustasot ja todennettu debug ovat taidon *Sulautettujen
järjestelmien tietoturva* aihe.

## Käytännössä

- **Käytä debuggeria alusta asti**, älä pelkkiä tulosteita. Vahtipiste ja
  vikakäsittelijän kutsupino ratkaisevat ongelmat, joihin tulosteet eivät
  pääse.
- **Pidä erillinen debug-käännös** (`-Og -g`) ja tunne ero
  julkaisukäännökseen. Säilytä julkaisun ELF-tiedosto: ilman sitä
  kentältä tulleita osoitteita ei voi tulkita.
- **Kirjoita toistuvat gdb-istunnot komentotiedostoiksi**, kuten tämän
  luvun esimerkki. Niitä voi ajaa testeinä ja jakaa tiimissä.
- **Mittaa ajoitukset nastalla ja logiikka-analysaattorilla.**
  Ajoitusta ei voi debugata pysäyttämällä.
- **Lukitse debug-portti tuotannossa.**

## Itsearviointi

- Osaat kuvata ketjun gdb – gdb-palvelin – debug-sovitin – SWD –
  debug-portti ja nimetä kunkin osan tehtävän.
- Osaat selittää ohjelmallisten ja laitteistokatkopisteiden eron ja sen,
  miksi flashissa niitä on vain muutama.
- Osaat käyttää gdb:ssä katkopisteitä, ehtoja, vahtipisteitä, muistin
  tutkimista ja `finish`-komentoa.
- Osaat käynnistää esimerkin QEMU:ssa gdb-palvelimena ja ottaa siihen
  yhteyden.
- Osaat valita debuggerin, nastan vaihdon, ITM:n tai RTT:n tilanteen
  mukaan.

# Rekisterikuvaukset ja generointi

Oheislaitteen rekisterit näkyvät kolmessa paikassa: RTL:ssä (logiikka,
joka toteuttaa ne), ohjelmistossa (otsake, jolla ajuri käyttää niitä) ja
dokumentaatiossa (käsikirja, josta ihminen lukee ne). Jos kolme kuvausta
kirjoitetaan käsin, ne alkavat erota ensimmäisestä muutoksesta lähtien.
Ratkaisu on kirjoittaa rekisterit kerran koneluettavaan muotoon ja
generoida kaikki kolme siitä.

## Kuvaus

Pikku-SoC:n GPIO-lohkon rekisterit on kuvattu JSON-tiedostossa:

```{.json tiedosto="esimerkit/gen/gpio.json"}
```

Jokaisella rekisterillä on siirto lohkon alusta, leveys, tyyppi,
nollausarvo ja kuvaus. Tyyppi kertoo, miten ohjelmisto ja laitteisto
käyttävät rekisteriä:

| Tyyppi | Ohjelmisto | Laitteisto | Esimerkki |
|--------|------------|------------|-----------|
| `rw` | kirjoittaa ja lukee | lukee arvon | ohjausrekisteri, lähdöt |
| `ro` | lukee | antaa arvon | tila, tulot |
| `wo` | kirjoittaa | saa arvon ja pulssin | käynnistys, lopetus |
| `w1c` | lukee; ykkösen kirjoitus nollaa bitin | asettaa bittejä | keskeytysten tila |
| `vakio` | lukee | – | tunniste, versio |

Tyyppi `w1c` (write 1 to clear) on keskeytystilarekisterien
vakiotapa. Ohjelmisto kuittaa käsittelemänsä tapahtumat kirjoittamalla
lukemansa arvon takaisin, eikä se voi vahingossa nollata tapahtumaa,
joka tuli lukemisen ja kirjoittamisen välissä: kirjoitettava arvo
sisältää ykkösen vain niissä biteissä, jotka ohjelmisto näki.

## Generaattori

`gen/rekisterit.py` lukee kuvauksen ja tarkistaa sen ennen generointia:

```{.python tiedosto="esimerkit/gen/rekisterit.py" osa="lue"}
```

Tarkistukset ovat generaattorin tärkein osa. Päällekkäinen siirto,
tasaamaton osoite tai liian leveä nollausarvo on virhe kuvauksessa, ja
se pysäytetään ennen kuin virheellistä RTL:ää tai otsaketta syntyy.

Tyyppi määrää, mitä portteja generoitu lohko tarjoaa ympäröivälle
logiikalle:

```{.python tiedosto="esimerkit/gen/rekisterit.py" osa="portit"}
```

## Generoitu RTL

Generoitu rekisterilohko on APB-orja. Siinä on rekisterien kiikut,
kirjoituslogiikka tavukohtaisine lupineen ja lukumultiplekseri:

```{.systemverilog tiedosto="esimerkit/gen/gpio_regs.sv"}
```

Tiedoston ensimmäinen rivi kertoo, mistä se on generoitu ja ettei sitä
saa muokata. Generoitu tiedosto tallennetaan versionhallintaan, jotta
RTL:n lukija ja simulointityökalut näkevät sen ilman generaattoria.
Esimerkkien `Makefile` generoi tiedostot uudelleen väliaikaiseen
hakemistoon ja vertaa niitä tallennettuihin: jos joku muokkaa
kuvausta generoimatta tai generoitua tiedostoa käsin, testi kaatuu.

## Generoitu otsake ja dokumentaatio

Sama kuvaus tuottaa C-otsakkeen. Rakenne vastaa rekisterien siirtoja,
ja käännösaikaiset tarkistukset varmistavat sen:

```{.c tiedosto="esimerkit/gen/gpio_regs.h"}
```

Vain luettavat rekisterit ovat `const`: kääntäjä hylkää kirjoituksen
`GPIO->SISAAN = 1`, joten virhe löytyy jo käännöksessä. Dokumentaatio
generoidaan samasta lähteestä Markdowniksi:

```{.markdown tiedosto="esimerkit/gen/gpio_regs.md"}
```

## Kääre: generoitu ja käsin kirjoitettu logiikka

Rekisterilohko on vain lohkon ohjelmistorajapinta. Oheislaitteen
toiminta kirjoitetaan käsin sen ympärille. GPIO:ssa käsin kirjoitettu
osa tahdistaa tulot ja tunnistaa nousevat reunat:

```{.systemverilog tiedosto="esimerkit/rtl/gpio.sv" osa="kaytto"}
```

Generoitu lohko ei tiedä, mitä reunat tarkoittavat. Se tarjoaa
`reunat_set`-tulon, jolla logiikka asettaa bittejä, ja `reunat_q`-
lähdön, josta keskeytys johdetaan. Työnjako pitää generaattorin
yksinkertaisena ja lohkon logiikan tavallisena RTL:nä.

## Käytännössä

- **Yksi lähde.** RTL, otsake, dokumentaatio ja varmennusmalli
  generoidaan samasta kuvauksesta. Käsin ylläpidetty rekisteritaulukko
  käsikirjassa on väärä viimeistään toisessa versiossa.
- **Tarkista generoidun ajantasaisuus CI:ssä.** Generoidut tiedostot
  tallennetaan, ja CI generoi ne uudelleen ja vertaa. Näin kukaan ei
  muokkaa niitä käsin huomaamatta.
- **Valmiit työkalut tuotantoon.** SystemRDL ja PeakRDL, OpenTitanin
  `regtool` tai kaupalliset työkalut tuottavat myös UVM-rekisterimallin,
  laitepuun ja IP-XACT-kuvauksen. Oma pieni generaattori on
  perusteltu, kun tarpeet ovat yksinkertaiset ja kuvausmuoto halutaan
  pitää kevyenä.
- **Vältä lukemisen sivuvaikutuksia.** Read-to-clear-rekisteri on
  vaarallinen: debuggerin muistinäkymä tai kääntäjän ylimääräinen luku
  kuluttaa tapahtuman. W1C on turvallisempi.
- **Varaa bitit laajennuksille.** Käyttämättömät bitit luetaan
  nollina ja kirjoitukset niihin ohitetaan. Ajurin on kirjoitettava
  ne nolliksi, jotta myöhempi versio voi ottaa ne käyttöön.

## Itsearviointi

- Osaat kuvata rekisterilohkon koneluettavasti ja perustella, miksi
  RTL, otsake ja dokumentaatio generoidaan samasta lähteestä.
- Osaat valita rekisterille oikean tyypin (rw, ro, wo, w1c, vakio).
- Osaat selittää, miksi W1C-kuittaus on turvallinen ja
  read-to-clear vaarallinen.
- Osaat lukea generoidun APB-rekisterilohkon ja kytkeä sen ympäröivään
  logiikkaan.
- Osaat varmistaa CI:ssä, että generoidut tiedostot ovat ajan tasalla.

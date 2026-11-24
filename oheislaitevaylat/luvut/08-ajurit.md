# Ajurikerrokset

Ajuri on koodi, joka tekee oheislaitteesta käytettävän. Pienessä
ohjelmassa koko ajuri voi olla yksi funktio, joka kirjoittaa
rekistereihin. Kun laitteita, väyliä ja piirivaihtoehtoja on useita,
rakenne ratkaisee, voiko koodia testata, siirtää toiseen piiriin ja
korjata rikkomatta muuta. Tässä luvussa kootaan aiempien lukujen
ajurit kerroksiksi ja testataan ne isäntäkoneella.

## Kerrokset

| Kerros | Esimerkki | Tuntee | Ei tunne |
|--------------|----------------|----------------------|----------------|
| Rekisterit | `mps2.h`: `pl022_t`, `sbcon_t` | osoitteet ja bitit | mitään muuta |
| Väyläohjain | `i2c_sbcon.c`, `pl022.c` | oheislaitteen rekisterit ja ajoituksen | väylällä olevia laitteita |
| Väylärajapinta | `i2c.h` | siirron käsitteet (osoite, kirjoitus, luku) | ohjainta |
| Laiteajuri | `at24.c` | laitteen protokollan (sivut, kirjoitusjakso) | väyläohjainta |
| Sovellus | `06-eeprom/main.c` | mitä tallennetaan | väylää |

Rajapinta on kerrosten välinen sopimus. I2C:n rajapinta on yksi
funktio, joka tekee yhden siirron. Se on tarpeeksi yleinen kaikille
rekisterilaitteille ja tarpeeksi pieni toteutettavaksi millä tahansa
ohjaimella: bit-bang-isännällä, piirin I2C-ohjaimella, Linuxin
`/dev/i2c-N`-laitteella tai testimallilla.

```{.c tiedosto="esimerkit/ajurit/i2c.h" osa="rajapinta"}
```

Toteutus upottaa rajapinnan rakenteensa ensimmäiseksi jäseneksi.
Laiteajuri saa osoittimen rajapintaan, ja toteutus muuntaa sen
takaisin omaksi rakenteekseen. C:ssä tämä on tavallinen tapa
toteuttaa rajapinta ja sen toteutukset ilman dynaamista muistia:

```{.c tiedosto="esimerkit/ajurit/i2c_sbcon.h" osa="ohjain"}
```

Hinta on yksi epäsuora kutsu siirtoa kohti, mikä on muutama
kellojakso, kun itse siirto kestää satoja mikrosekunteja. Jos
epäsuoruus on liikaa, saman erottelun voi tehdä linkitysvaiheessa:
laiteajuri kutsuu nimettyä funktiota, ja käännös valitsee, mikä
tiedosto sen toteuttaa.

## Laiteajuri: EEPROM

AT24-sarjan EEPROM on tavallinen I2C-laite, jonka protokollassa on kaksi
ansaa. Kirjoitus kiertää *sivun* sisällä samoin kuin SPI-flashissa:
24C02:n sivu on 8 tavua, ja sivun rajan yli menevä kirjoitus jatkuu
saman sivun alusta. Kirjoituksen jälkeen piiri käynnistää sisäisen
kirjoitusjakson (enintään noin 5 ms), jonka aikana se ei kuittaa
osoitettaan. Ajuri jakaa kirjoitukset sivuiksi ja kysyy piiriltä
jokaisen sivun jälkeen, onko se valmis (ACK polling). Luku on
yksi siirto: osoitetavu, toistettu START ja peräkkäisluku.

```{.c tiedosto="esimerkit/ajurit/at24.h" osa="rajapinta"}
```

```{.c tiedosto="esimerkit/ajurit/at24.c" osa="kirjoita"}
```

```{.c tiedosto="esimerkit/ajurit/at24.c" osa="odota"}
```

Virheet käännetään kerroksen omalle kielelle. Väylän kaksi NACKia
ovat EEPROMille eri asioita: osoitteen NACK tarkoittaa, ettei laite
vastaa, ja datan NACK on väylävirhe. Kutsuja tietää, mitä tehdä
kummallekin, mutta sen ei tarvitse tuntea I2C:tä.

```{.c tiedosto="esimerkit/ajurit/at24.c" osa="virheet"}
```

Kohdelaitteessa sama ajuri käyttää SBCon-ohjainta:

```{.c tiedosto="esimerkit/06-eeprom/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/06-eeprom.odotettu"}
```

Kirjoitus osoitteisiin `05`–`0e` ylittää sivun rajan kohdassa `08`, ja
ajuri teki sen kahdessa osassa. QEMU:n EEPROM-malli alkaa kuitenkin
nollista eikä ykkösistä kuten tyhjä oikea piiri. Malli ei myöskään
kierrä sivun sisällä eikä mallinna kirjoitusjaksoa. Ajuri olisi
siis toiminut QEMU:ssa ilman sivujakoakin, ja virhe olisi löytynyt
vasta oikeasta laitteesta.

## Testaus isäntäkoneella

Koska laiteajuri tuntee vain väylärajapinnan, sen voi kääntää
isäntäkoneen kääntäjällä ja ajaa *mallia* vastaan. Malli toteuttaa saman
rajapinnan ja käyttäytyy kuten oikea piiri: sivun sisällä kiertävä
osoite, kirjoitusjakso ja valinnainen vika.

```{.c tiedosto="esimerkit/isanta/at24_testi.c" osa="malli"}
```

```{.c tiedosto="esimerkit/isanta/at24_testi.c" osa="testit"}
```

```{.make tiedosto="esimerkit/Makefile" osa="isanta"}
```

```{.tuloste tiedosto="esimerkit/testit/at24-testi.odotettu"}
```

Testi kattaa polut, joita kohdelaitteessa on vaikea tai mahdoton
tuottaa: piiri, joka ei valmistu kyselyrajan aikana, piiri, joka
hylkää tavun kesken kirjoituksen, ja alueen ylitys. Siirtojen määrä
paljastaa myös toteutuksen: kaksi sivua, kummallekin kirjoitus,
kolme kiireisen piirin kyselyä ja onnistunut kysely. Kun sama testi
käännetään ajurilla, joka ei jaa kirjoitusta sivuiksi
(`-DSIVUVIRHE`), malli paljastaa virheen, jonka QEMU ohitti:

```{.tuloste tiedosto="esimerkit/testit/at24-testi-sivuvirhe.odotettu"}
```

Isäntätestit käännetään AddressSanitizerin ja UBSanin kanssa, joten
ne löytävät myös puskurin ylitykset ja määrittelemättömän käytöksen,
joita mikrokontrollerissa ei huomaisi.

### Rekisterit muistina

Väyläohjainta ei voi testata rajapinnan tasolla, koska se puhuu
rekistereille. Rekisterit ovat kuitenkin vain osoitteita, ja ajuri saa
osoittimen niihin. Isäntätestissä osoitin osoittaa tavalliseen
muistisivuun:

```{.c tiedosto="esimerkit/isanta/pl022_testi.c" osa="sivu"}
```

Testi laskee jakajat kuudelle taajuudelle, alustaa lohkon ja
tarkistaa rekisteriarvot, siirtää tavuja yksi kerrallaan ja asettaa
lopuksi tilarekisteriin pysyvän BSY-tilan:

```{.tuloste tiedosto="esimerkit/testit/pl022-testi.odotettu"}
```

Muistisivulla testataan kellonjakajien laskenta, alustuksen
rekisteriarvot ja aikaraja: kun tilarekisteri väittää lohkon olevan
jumissa, ajuri palaa virheellä eikä jää silmukkaan. Muistisivun raja
näkyy myös. Muistipaikka ei ole FIFO, joten monen tavun siirtoa ei
voi testata näin. Se testataan kohdelaitteessa PL022:n
silmukkatilassa (luku 4). Kumpikin testi kattaa sen, mitä toinen ei.
Monimutkaisemmalle oheislaitteelle tehdään laitemalli, joka reagoi
rekisterikirjoituksiin, esimerkiksi QEMU:n kaltainen emulaattori tai
rekisterien käyttö funktioiden kautta, jotka testissä voi korvata.

## Pollaus, keskeytys vai DMA

| Ajurin tapa | Sopii | Hinta |
|-------------|-------|-------|
| Pollaus | lyhyet siirrot, alustus, käynnistyslatain, vikatilanteet | prosessori odottaa koko siirron |
| Keskeytys | tavuittaiset virrat (UART), tapahtumat | keskeytys jokaisesta tavusta, tilakone käsittelijässä |
| DMA | suuret ja jatkuvat siirrot (SPI-flash, ääni, A/D) | asetuksen monimutkaisuus, välimuisti, muistin varaus koko siirron ajaksi |

Sama laiteajuri voi käyttää mitä tahansa näistä, jos väylärajapinta
kätkee eron. Keskeytys- ja DMA-ajurin rajapinta on silloin yleensä
asynkroninen: siirto käynnistetään, ja valmistumisesta ilmoitetaan
takaisinkutsulla tai tapahtumalla. Synkroninen rajapinta, kuten tämän
paketin `siirto`, on helpoin käyttää ja testata, ja
reaaliaikakäyttöjärjestelmässä se on luonteva: tehtävä odottaa
semaforia, ja muut tehtävät ajetaan sillä aikaa. Väylä on silloin
jaettu resurssi, jonka siirrot suojataan mutexilla, jotta kahden
laiteajurin siirrot eivät sekoitu.

## Aikarajat ja virheet

Jokainen odotus laitteistoa on rajattava. Laitteistoa ei pidä
odottaa ikuisesti, koska irronnut johdin, jumiutunut laite tai väärä
kello pysäyttäisi koko ohjelman ilman jälkeä. Tämän paketin ajurit
laskevat odotuskierroksia, koska QEMU:n aika ei ole luotettava.
Oikeassa laitteessa raja kannattaa ilmaista aikana: ajuri lukee
millisekuntilaskurin odotuksen alussa ja vertaa erotusta rajaan.
Etumerkittömien lukujen erotus toimii myös laskurin pyörähtäessä
ympäri. Virhe palautetaan kutsujalle, kirjataan laskuriin ja
raportoidaan. Sen jälkeen ylempi kerros päättää, yritetäänkö
uudelleen, alustetaanko väylä vai siirrytäänkö vikatilaan. Tärkeintä
on, ettei virhettä niellä: ajuri, joka palauttaa nollia lukuvirheen
jälkeen, tuottaa uskottavan näköistä väärää dataa.

## Käytännössä

- **Erota laiteajuri väyläohjaimesta pienellä rajapinnalla.** Laite
  vaihtaa väylää ja ohjain piiriä harvemmin kuin luulisi, mutta testit
  hyötyvät erottelusta heti.
- **Testaa laiteajurit isäntäkoneella mallia vastaan**, joka
  käyttäytyy kuten datalehden piiri, ja lisää malliin viat, joita
  oikealla laitteella ei saa tuotettua.
- **Älä luota emulaattoriin laitteen yksityiskohdissa.** QEMU:n
  laitemallit ovat armollisempia kuin piirit.
- **Rajaa jokainen odotus**, käännä virheet kerroksen kielelle äläkä
  niele niitä.
- **Valitse pollaus, keskeytys tai DMA siirron koon ja tiheyden
  mukaan**, ja pidä rajapinta samana.

## Itsearviointi

- Osaat jakaa ajurin rekistereihin, väyläohjaimeen, väylärajapintaan
  ja laiteajuriin ja perustella, mitä kukin tuntee.
- Osaat toteuttaa C-rajapinnan funktio-osoittimella ja upotetulla
  rakenteella.
- Osaat toteuttaa EEPROMin sivutetun kirjoituksen ja ACK-kyselyn.
- Osaat kirjoittaa isäntäkoneella ajettavan testin laitemallia ja
  rekisterisivua vastaan ja kertoa, mitä kumpikin ei kata.
- Osaat valita pollauksen, keskeytyksen ja DMA:n välillä ja suunnitella
  aikarajat ja virheiden käsittelyn.

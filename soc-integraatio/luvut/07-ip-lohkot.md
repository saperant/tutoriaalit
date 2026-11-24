# Valmiit IP-lohkot

Järjestelmäpiirin lohkoista suurin osa on *IP-lohkoja* (intellectual
property): valmiita, uudelleenkäytettäviä suunnitelmia, jotka on
ostettu, lisensoitu, otettu avoimesta lähteestä tai tehty aiemmassa
projektissa. Integroijan työ on valita lohkot, ymmärtää niiden
oletukset ja koota ne niin, että oletukset pitävät.

## Hard, firm ja soft IP

| Tyyppi | Muoto | Joustavuus | Esimerkkejä |
|--------|-------|------------|-------------|
| Soft IP | RTL-lähdekoodi tai salattu RTL | parametroitava, mihin tahansa prosessiin | suoritinytimet, väyläkytkimet, UART, DMA |
| Firm IP | synteesin jälkeinen porttitason verkko | kiinteä logiikka, sijoittelu vapaa | salatut ytimet tietylle kirjastolle |
| Hard IP | valmis piirikuvio (layout) yhdelle prosessille | ei muutettavissa | PLL, SerDes, DDR PHY, ADC, flash |

Analogiset ja nopeat sekamuotoiset lohkot (PLL, SerDes, muistiliitäntöjen
fyysinen kerros) ovat lähes aina hard IP:tä, koska niiden toiminta
riippuu transistoritason suunnittelusta ja valmistusprosessista. Ne
tilataan valmistajalta tai IP-toimittajalta tietylle prosessille.
FPGA-piireissä hard IP:tä ovat esimerkiksi PCIe-ohjaimet, muistiohjaimet,
SerDes-lähetin-vastaanottimet ja joissain piireissä kokonaiset
Arm-suoritinjärjestelmät.

Pikku-SoC:n lohkot ovat soft IP:tä. Parametrit tekevät niistä
uudelleenkäytettäviä: kytkimen isäntien ja orjien määrä sekä
muistikartta (`KANTA`, `MASKI`) ja RAMin koko (`SANAT`) annetaan
instanssissa.

## IP-lohkon oletukset

Jokainen IP-lohko olettaa jotain ympäristöstään. Integrointivirheet
syntyvät lähes aina oletuksista, joita ei kirjoitettu ylös. Ennen
lohkon kytkemistä käydään läpi ainakin:

| Asia | Kysymys |
|------|---------|
| Kellot | Montako kelloa, mitkä taajuudet, ovatko ne toisiinsa nähden asynkronisia? |
| Nollaus | Synkroninen vai asynkroninen, aktiivinen ylä- vai alatasolla, vaaditaanko järjestys tai kesto? |
| Väylät | Mikä protokolla ja versio, mitkä valinnaiset signaalit, montako avointa siirtoa? |
| Keskeytykset | Taso- vai reunaliipaisu, aktiivinen ylä- vai alatasolla, kuitataanko rekisterillä? |
| Muisti | Tarvitseeko lohko muistimakroja, onko pariteetti tai ECC? |
| Testattavuus | Onko scan-ketju valmiina, tarvitaanko muistitestiä (MBIST)? |
| Teho | Saako kellon portittaa, saako alueen sammuttaa, onko säilytysrekistereitä? |
| Ohjelmisto | Onko ajuri, millä lisenssillä, mille käyttöjärjestelmille? |

Pikku-SoC:ssa nämä on ratkaistu yksinkertaisimmalla tavalla: yksi kello,
asynkroninen alatasolla aktiivinen nollaus, AXI4-Lite tai APB,
tasoliipaistut ylätasolla aktiiviset keskeytykset. Oikeissa IP-lohkoissa
mikä tahansa näistä voi olla toisin, ja niiden sovittaminen on
integroijan työtä: invertteri tässä, nollauksen tahdistin tuossa,
väyläsilta kolmannessa.

## IP-XACT

IP-XACT (IEEE 1685) on XML-muotoinen standardi IP-lohkojen kuvaamiseen.
Kuvaus sisältää lohkon portit ja niiden ryhmittelyn väyläliitännöiksi,
parametrit, muistikartan ja rekisterit kenttineen sekä tiedostoluettelot.
Työkalut lukevat kuvauksia ja:

- kytkevät lohkot väyläliitäntöjen tasolla yksittäisten signaalien
  sijaan (generoivat ylimmän tason RTL:n);
- generoivat muistikartan, C-otsakkeet ja dokumentaation;
- tarkistavat, että väyläliitännät ovat yhteensopivia.

IP-XACT on raskas kirjoittaa käsin, ja rekisterien kuvaamiseen
käytetään usein kevyempiä muotoja: SystemRDL (Accellera), OpenTitanin
`hjson`-rekisterikuvaukset tai yksinkertainen JSON/YAML, kuten luvun 8
generaattorissa. Idea on sama: kuvaus on ainoa lähde, ja kaikki muu
generoidaan siitä.

## Lisenssit

IP-lohkon lisenssi ratkaisee, saako sitä käyttää tuotteessa ja millä
ehdoilla:

| Lisenssi | Tyyppi | Huomioitavaa |
|----------|--------|--------------|
| Apache 2.0 | salliva | patenttilisenssi; mm. OpenTitan, monet RISC-V-ytimet |
| Solderpad Hardware License | salliva | Apache 2.0:n laitteistomuunnelma; PULP-projektin lohkot |
| ISC, MIT, BSD | salliva | lyhyt, ei patenttiehtoja; mm. PicoRV32 (ISC) |
| CERN-OHL-S/-W/-P | vahva/heikko/salliva copyleft | laitteistolle suunniteltu |
| Kaupallinen | sopimus | rojaltit, käyttöoikeus tiettyyn projektiin, vientirajoitukset |

Laitteistolisensseissä on ohjelmistolisensseistä poikkeavia kysymyksiä:
onko piirikuvio "johdannainen teos", mitä tarkoittaa "lähdekoodin
jakaminen", kun tuote on piisiru, ja koskevatko patentit toteutusta.
Lisenssien yhdistelmä tarkistetaan ennen kuin lohko otetaan mukaan,
ja jokaisen lohkon lisenssi ja alkuperä kirjataan (materiaaliluettelo,
SBOM, koskee myös laitteistoa).

## Integrointi lohko kerrallaan

Hyvä integrointitapa on edetä lohko kerrallaan ja testata jokainen
vaihe:

1. **Lohkon oma testi.** Lohko simuloidaan omalla testipenkillään sen
   omassa ympäristössä. Jos lohkon mukana tulee testipenkki tai
   varmennus-IP (VIP), se ajetaan ensin.
2. **Liitäntätesti.** Lohko kytketään järjestelmään, ja ohjelmisto
   lukee sen tunniste- tai versiorekisterin. Tämä varmistaa
   osoitteen, väylän ja kellot.
3. **Toimintatesti.** Ohjelmisto käyttää lohkoa: kirjoittaa, lukee,
   aiheuttaa keskeytyksen.
4. **Järjestelmätesti.** Lohko toimii yhdessä muiden kanssa kuormitettuna:
   DMA ja ydin samaan aikaan, keskeytykset sisäkkäin.

Pikku-SoC:n ohjelmat seuraavat samaa järjestystä: `kaynnistys.c` lukee
tunnisteet (vaihe 2), `keskeytykset.c` ja `dma.c` käyttävät lohkoja
(vaihe 3), ja `dma.c` kuormittaa kytkintä kahdella isännällä (vaihe 4).

## Käytännössä

- **Valitse IP sen dokumentaation ja testien perusteella.** Lohko,
  jolla on hyvä testipenkki, selkeä integrointiohje ja aktiivinen
  ylläpito, on halvempi kuin lohko, joka on hiukan pienempi.
- **Älä muokkaa IP:tä.** Muutokset tehdään kääreeseen (wrapper) tai
  parametreilla. Muokattu IP ei enää ole se, minkä toimittaja testasi,
  eikä päivitys onnistu.
- **Kirjaa oletukset.** Jokaisesta lohkosta pidetään integrointilistaa
  edellä olevan taulukon kysymyksistä. Lista on katselmoinnin pohja.
- **Tunnisterekisteri jokaiseen lohkoon.** Versio- ja tunnisterekisteri
  maksaa muutaman portin ja säästää tunteja: ohjelmisto tietää, minkä
  version kanssa se toimii.
- **Lisenssi ennen koodia.** Lohkoa ei lisätä edes kokeiluun ennen
  kuin lisenssi on tarkistettu. Pois ottaminen myöhemmin on kallista.

## Itsearviointi

- Osaat erottaa hard, firm ja soft IP:n ja kertoa, miksi analogiset
  lohkot ovat hard IP:tä.
- Osaat luetella IP-lohkon ympäristöoletukset ja kysyä ne ennen
  integrointia.
- Osaat kertoa, mitä IP-XACT kuvaa ja mitä sen avulla generoidaan.
- Osaat tunnistaa tavallisimmat laitteistolisenssit ja niiden erot.
- Osaat suunnitella lohkon integroinnin vaiheittain testeineen.

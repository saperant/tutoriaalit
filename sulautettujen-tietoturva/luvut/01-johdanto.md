# Johdanto {.runko-johdanto}

Sulautettu laite on tietokone, jonka omistaja ei ole sen ylläpitäjä.
Lämpömittari, ovilukko, teollisuusohjain tai sydämentahdistin toimii
vuosia kentällä, usein ilman ihmistä, ja jokainen kappale on
hyökkääjän ostettavissa ja purettavissa. Palvelimen tietoturvassa
oletetaan, että laitesali on lukittu. Sulautetuissa järjestelmissä
oletus on päinvastainen: **hyökkääjällä on laite käsissään**.

Tämä tutoriaali käsittelee niitä tietoturvan osia, jotka ovat
sulautetuille järjestelmille ominaisia:

- **luottamusketju**: miten laite varmistaa, että se ajaa vain
  valmistajan allekirjoittamaa ohjelmistoa, eikä palaa vanhaan
  haavoittuvaan versioon
- **avaimet**: missä salaisuudet säilytetään laitteessa, jota voi
  avata ja mitata, ja miten jokainen laite saa omansa
- **päivitykset**: miten laite päivitetään turvallisesti radiolinkin
  yli niin, ettei sähkökatko tai huono versio riko sitä
- **fyysiset hyökkäykset**: debug-portit, sivukanavat ja
  vikahyökkäykset sekä niiden vastatoimet
- **sääntely**: mitä EU:n kyberkestävyyssäädös ja alan standardit
  vaativat laitteelta ja valmistajalta

Kryptografian perusteet (tiivisteet, allekirjoitukset, AEAD, HKDF)
ovat tutoriaalissa *Kryptografia*, yleinen uhkamallinnus
tutoriaalissa *Tietoturvan perusteet* ja kehitysprosessin
turvallisuus tutoriaalissa *Tietoturva kehitystyössä*. Mikrokontrollerin
rakenne (muistikartta, vektoritaulu, käynnistyskoodi) on taidon
*Mikrokontrollerit ja bare-metal-ohjelmointi* aihe; tässä siitä kerrataan vain se, mitä
käynnistysketjun ymmärtäminen vaatii.

## Laboratorio

Esimerkeissä on kolme osaa:

1. **Käynnistysketju Cortex-M3:lle.** Kansiossa `esimerkit/laite/` on
   pieni käynnistin, joka tarkistaa laiteohjelmistokuvan
   Ed25519-allekirjoituksen, versionumeron ja tiivisteen ja
   käynnistää sovelluksen. Se käännetään `arm-none-eabi-gcc`:llä ja
   ajetaan QEMU:n `mps2-an385`-kortilla. Tuloste kulkee
   *semihosting*-rajapinnan kautta, joten sarjaporttia ei tarvita.
2. **Isäntäkoneen C-ohjelmat**, jotka mallintavat laitteiston
   ilmiöitä: OTP-laskurin, ajoitusvuodon ja vikahyökkäyksen.
3. **Python-ohjelmat**, jotka toteuttavat valmistajan ja
   taustajärjestelmän puolen: kuvien allekirjoituksen, manifestit,
   etätodennuksen, PUF-avaimen ja sivukanavahyökkäyksen.

Kaikki esimerkit testataan automaattisesti. Käynnistysketjun
skenaariot ajetaan QEMU:ssa, ja tuloste verrataan odotettuun:

```{.make tiedosto="esimerkit/laite/Makefile" osa="skenaariot"}
```

Kokeiluissa käytetään RFC 8032:n testiavaimia. Ne on julkaistu
standardissa, joten jokainen voi allekirjoittaa niillä mitä tahansa;
tuotantoavaimet luodaan ja säilytetään laitteistoturvamoduulissa
(HSM), eivätkä ne koskaan ole kehittäjän koneella.

## Esimerkkien ajaminen

Kehityskontissa (`.devcontainer/sulautettujen-tietoturva`) on ARM-
ristikääntäjä, QEMU ja Pythonin `cryptography`-kirjasto. Ilman
konttia tarvitaan Debian- tai Ubuntu-paketit `gcc-arm-none-eabi`,
`libnewlib-arm-none-eabi` ja `qemu-system-arm` sekä
`pip install cryptography`.

```text
make testaa                 # kaikki esimerkit ja skenaariot
make -C esimerkit/laite     # vain käynnistysketju
python3 esimerkit/06-puf.py # yksittäinen esimerkki
```

## Tutoriaalin rakenne

Luvut seuraavat laitteen elinkaarta. Ensin uhkamalli, sitten
käynnistys (luvut 3–5), avaimet (6) ja päivitykset (7). Luvut 8–10
käsittelevät fyysisiä hyökkäyksiä: debug-portteja, sivukanavia ja
vikahyökkäyksiä. Luku 11 käy läpi standardit ja sääntelyn, ja luku 12
kokoaa nyrkkisäännöt ja lähteet.

Jokainen luku päättyy osioihin *Käytännössä*, jossa kerrotaan miten
asiat tehdään oikeissa tuotteissa, ja *Itsearviointi*, jonka avulla
kokenut lukija voi ohittaa luvun, jonka asiat hän jo osaa.

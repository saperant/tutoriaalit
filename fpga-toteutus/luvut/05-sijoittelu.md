# Sijoittelu ja reititys

Synteesin jälkeen suunnitelma on lista primitiivejä ja niiden
kytkentöjä. Sijoittelu päättää, mihin piirin paikkaan kukin
primitiivi menee, ja reititys valitsee johtimet ja kytkimet, joilla
ne yhdistetään. FPGA:lla molemmat ovat rajoitettuja: paikat ja johtimet
ovat valmiina piirissä, ja työkalu valitsee niistä.

## Mitä nextpnr tekee

1. **Pakkaus.** LUT, kiikku ja kantosolu, jotka kuuluvat yhteen,
   yhdistetään logiikkasoluksi. Solut, joilla on samat ohjaussignaalit,
   voivat jakaa logiikkalohkon.
2. **Kiinteät paikat.** IO-solut sijoitetaan rajoitetiedoston
   nastoihin, kellot globaaleihin verkkoihin ja erikoislohkot (RAM, DSP,
   PLL) niille varattuihin paikkoihin.
3. **Globaali sijoittelu.** Analyyttinen sijoittelija (nextpnr:n
   oletus iCE40:lle on *HeAP*) ratkaisee solujen likimääräiset paikat
   minimoimalla johtimien kokonaispituuden, ja ajoitukseltaan kriittiset
   yhteydet painotetaan raskaammiksi.
4. **Tarkennus.** Simuloitu jäähdytys siirtää ja vaihtaa soluja
   pienissä askelissa. Satunnaisuus tekee lopputuloksesta riippuvan
   siemenestä.
5. **Reititys.** Reititin etsii jokaiselle verkolle polun johdinten ja
   kytkinten läpi. Jos sama johdin kelpaisi usealle verkolle, reititin
   neuvottelee: ruuhkaisten resurssien hinta nousee joka kierroksella,
   kunnes jokainen verkko löytää oman polkunsa (PathFinder-algoritmi).

## Siemen ja vaihtelu

Sama suunnitelma eri siemenillä tuottaa eri sijoittelun ja eri Fmax:n:

```{.makefile tiedosto="esimerkit/Makefile" osa="siemenet"}
```

```{.tuloste tiedosto="esimerkit/raportit/siemenet.odotettu"}
```

Tarkat taajuudet olivat 40,0, 41,0, 39,5, 41,5 ja 41,3 MHz: noin 5 %
vaihtelu pelkästä satunnaisuudesta. Siksi

- ajo tehdään kiinteällä siemenellä, jotta tulos on toistettava, ja
- suunnitelman marginaali ei saa olla muutaman prosentin varassa. Jos
  ajoitus täyttyy vain osalla siemenistä, suunnitelma on rajalla, ja
  pieni RTL-muutos voi rikkoa sen.

Siementen kokeilu ("seed sweep") on hätäratkaisu. Kestävä korjaus on
lyhentää kriittistä polkua (luku 6).

## Rajoitteet

Sijoittelua ohjataan rajoitteilla:

| Rajoite | iCE40 (nextpnr) | Tarkoitus |
|---------|-----------------|-----------|
| Nasta | `set_io nimi 35` (PCF) | portti oikeaan nastaan |
| Kello | `--freq` tai `set_frequency clk 48` (PCF) | ajoituksen tavoite |
| IO-asetukset | `set_io -pullup yes` | ylösveto, IO-standardi |
| Sijainti | `BEL`-attribuutti RTL:ssä | solu tiettyyn paikkaan |

Suuremmissa työkaluissa rajoitteet ovat SDC/XDC-muodossa (Tcl-pohjainen,
sama kuin ASIC-vuossa) ja kattavat myös IO-viiveet, monisyklipolut ja
kellojen väliset suhteet. nextpnr:n iCE40-tuki on suppeampi: se
raportoi IO-polkujen ja kellojen välisten polkujen viiveet mutta ei
vertaa niitä mihinkään vaatimukseen (luvut 6 ja 8).

## Ruuhka ja käyttöaste

Kun piiri täyttyy, reititysresurssit loppuvat ennen logiikkasoluja.
Reititin joutuu kiertämään, viiveet kasvavat, ja lopulta reititys ei
onnistu. Ruuhkaa aiheuttavat erityisesti

- **suuri tuulettuvuus**: yksi signaali moneen paikkaan, esimerkiksi
  sallinta tai nollaus, jota ei ole viety globaaliin verkkoon;
- **leveät multiplekserit**: kombinatorinen muisti luvun 4 tapaan;
- **kiinteät paikat**: IO-nastat ja RAM-lohkot vetävät logiikkaa
  luokseen, ja huonosti valitut nastat pakottavat signaalit kulkemaan
  piirin halki.

Nastajärjestys kannattaa sopia piirilevysuunnittelijan kanssa
aikaisin: samaan väylään kuuluvat nastat vierekkäin ja samalle puolelle
piiriä kuin niitä käsittelevä logiikka.

## Tulosten säilyttäminen

Suurissa suunnitelmissa sijoittelu kestää tunteja. Valmistajien
työkaluissa on tähän keinoja: osien lukitseminen (floorplanning,
pblock), osittainen uudelleenkäännös ja aiemman sijoittelun
hyödyntäminen. Pienillä piireillä vuo ajetaan alusta joka kerta, kuten
tässä tutoriaalissa.

## Käytännössä

- **Kiinteä siemen, marginaalia ajoitukseen.** Toistettava ajo ja
  vähintään 10–15 % marginaali Fmax:iin, jotta satunnaisuus ja pienet
  muutokset eivät riko ajoitusta.
- **Seuraa käyttöastetta.** Kun logiikkasolujen käyttö ylittää noin
  80 %, sijoittelu ja reititys vaikeutuvat nopeasti.
- **Suuren tuulettuvuuden signaalit globaaleihin verkkoihin tai
  rekisteröityinä kopioina.** Nollaus ja laajat sallinnat ovat
  tyypillisiä ruuhkan aiheuttajia.
- **Nastat ajoissa.** Pinnijärjestys vaikuttaa ajoitukseen ja
  reititykseen. Sovi se piirilevyn kanssa ennen kuin kumpikaan
  lukitaan.

## Itsearviointi

- Osaat kertoa sijoittelun ja reitityksen vaiheet ja mitä kussakin
  päätetään.
- Osaat selittää, miksi siemen vaikuttaa tulokseen ja miksi siementen
  kokeilu ei korvaa marginaalia.
- Osaat antaa nastat ja kellotaajuuden rajoitteina.
- Osaat tunnistaa ruuhkan syitä: tuulettuvuus, leveät multiplekserit,
  huono nastajärjestys.

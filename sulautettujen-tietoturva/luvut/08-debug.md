# Debug-portit

Kehitysvaiheessa debug-portti (JTAG tai Armin SWD) on välttämätön:
sen kautta ohjelmoidaan flash, pysäytetään suoritin ja luetaan
muistia ja rekistereitä. Samat ominaisuudet ovat hyökkääjälle täydelliset.
Avoin debug-portti ohittaa turvallisen käynnistyksen, lukee avaimet ja
muuttaa ohjelmaa ajon aikana. Lisäksi laitteissa on usein
sarjakonsoli (UART), jonka kautta saa käynnistimen tai
käyttöjärjestelmän komentotulkin.

## Lukitustasot

Mikrokontrollereissa debug-pääsyä rajataan lukitustasoilla. Monen
valmistajan (esim. STM32:n RDP, *readout protection*) malli on tämä:

| Taso | Debug | Flash debuggerilla | Tason laskeminen |
|------|-------|--------------------|------------------|
| 0 | täysi | luettavissa | – |
| 1 | rajattu | ei luettavissa | mahdollinen, pyyhkii flashin |
| 2 | pois | ei luettavissa | ei mahdollinen |

```{.python tiedosto="esimerkit/08-debug.py" osa="rdp"}
```

Taso 1 suojaa ohjelmistoa ja avaimia mutta antaa kehittäjän palauttaa
laitteen tehdastilaan. Taso 2 on lopullinen: piiriä ei voi enää
debugata eikä tutkia vikojen syitä palautetuista laitteista. Valinta on
liiketoimintapäätös yhtä lailla kuin tekninen.

Lukitus on yksi bittijono asetuksissa, ja sen tarkistaa
laitteisto käynnistyksessä. Siksi se on vikahyökkäysten (luku 10)
houkutteleva kohde. Julkaistuissa hyökkäyksissä esimerkiksi
nRF52-piirien debug-suojaus on ohitettu jännitehäiriöllä juuri tällä
hetkellä. Lukitukseen ei pidä luottaa ainoana suojana avainten
lukemista vastaan.

## Todennettu debug

Kentältä palautetun laitteen vika pitää voida selvittää. Ratkaisu on
**todennettu debug** (*authenticated debug*): portti avautuu vain
valmistajan allekirjoittamalla luvalla, joka on sidottu laitteeseen
ja yhteen istuntoon. Laite antaa haasteen, valmistajan palvelin
tarkistaa huoltajan oikeudet ja allekirjoittaa luvan, ja laite
tarkistaa sen:

```{.python tiedosto="esimerkit/08-debug.py" osa="todennettu"}
```

```{.tuloste tiedosto="esimerkit/08-debug.odotettu"}
```

Lupa sisältää laitteen sarjanumeron ja haasteen, joten sitä ei voi
käyttää toisessa laitteessa eikä toisessa istunnossa. Oikeudet (tässä
*vain luku*) rajaavat, mitä huoltaja saa tehdä. Armin piireissä sama
toteutetaan laitteistossa (*Authenticated Debug Access Control*), ja
monet mikrokontrollerivalmistajat tarjoavat sille oman ratkaisunsa.

## Sarjakonsoli ja testipisteet

UART-konsoli on usein suojaamaton: käynnistimen komentotulkki,
pääkäyttäjän kuori ilman salasanaa tai tulosteessa näkyvät avaimet.
Testipisteet piirilevyllä löytyvät helposti, vaikka liitintä ei olisi.
Tuotannossa konsoli pitää poistaa käytöstä tai vaatia sille
todennus, ja käynnistimen keskeytysnäppäin (esim. U-Bootin
`bootdelay`) asettaa nollaan.

## Käytännössä

- **Lukitse debug tuotannossa** ja valitse lukitustaso uhkamallin ja
  huoltotarpeen mukaan.
- **Todennettu debug** palautettujen laitteiden tutkimiseen
  pysyvän avoimen portin sijaan.
- **Poista tai todenna sarjakonsoli** ja tarkista, mitä käynnistin ja
  käyttöjärjestelmä tulostavat.
- **Testaa tuotantolaite.** Kokeile, saako debuggerilla yhteyden ja
  mitä konsolista saa; asetus voi unohtua tuotantolinjan ohjelmoinnista.
- **Älä luota lukitukseen yksin.** Avaimet kuuluvat turvaelementtiin tai
  suojattuun alueeseen, jotta lukituksen ohitus ei paljasta niitä.

## Itsearviointi

- Osaat kuvata lukitustasot ja niiden seuraukset huollolle ja
  vianselvitykselle.
- Osaat suunnitella todennetun debugin haaste–vastaus-protokollan,
  joka on sidottu laitteeseen ja istuntoon.
- Osaat luetella debug-porttien ja sarjakonsolin tavalliset
  virheet tuotantolaitteissa.

# DMA

Edellisten lukujen ajurit siirtävät jokaisen tavun prosessorin kautta:
luku oheislaitteen rekisteristä, kirjoitus muistiin, ja jokaisesta
tavusta keskeytys tai pollauskierros. Tämä riittää hitaille väylille,
mutta 1 Mbit/s:n UART tuottaa sata tuhatta tavua sekunnissa, ja
nopeampi SPI-flash, A/D-muunnin tai äänirajapinta vielä enemmän.
*DMA-ohjain* (Direct Memory Access) on väylän toinen isäntä, joka
siirtää dataa muistin ja oheislaitteiden välillä ilman prosessoria.
Prosessori asettaa siirron, jatkaa omaa työtään ja saa keskeytyksen,
kun siirto on valmis.

## Käsitteet

DMA-ohjaimessa on useita *kanavia*. Kukin kanava kuvaa yhden siirron:

- **lähde- ja kohdeosoite** sekä tieto siitä, kasvavatko ne siirron
  aikana. Muistipuskurin osoite kasvaa, oheislaitteen datarekisterin
  ei.
- **leveys** (8, 16 tai 32 bittiä) ja **purske** (montako siirtoa
  kerralla, kun väylä on saatu)
- **määrä**: montako siirtoa tehdään. Se lasketaan yleensä leveyden
  yksiköissä, ei tavuina.
- **vuonohjaus**: kuka päättää tahdin. Muistista muistiin -siirrossa
  DMA kopioi niin nopeasti kuin väylä antaa. Oheislaitteen kanssa
  oheislaite pyytää siirtoa *pyyntölinjalla* (request), esimerkiksi
  kun UARTin vastaanotossa on tavu tai SPI:n lähetys-FIFOssa on tilaa.
- **keskeytykset**: siirto valmis (transfer complete), puolet valmiina
  (half transfer) ja virhe.

Monessa ohjaimessa kanava osaa lukea seuraavan siirron *kuvaajan*
(descriptor) muistista. Kuvaajaketju kokoaa hajallaan olevat palat
yhteen tai jakaa yhden puskurin moneen paikkaan (scatter-gather), ja
rengasmainen ketju tai *kiertävä tila* (circular) toistaa siirtoa
loputtomasti. Jatkuvassa vastaanotossa käytetään kahta puoliskoa
(ping-pong): kun DMA täyttää toista, ohjelma käsittelee toista, ja
puolivälin ja lopun keskeytykset kertovat, kumpi on valmis.

## PL081 mps2-an505:llä

DMA-esimerkki ajetaan QEMU:n kortilla `mps2-an505`, jossa on Cortex-M33
ja ARM:n kaksikanavainen PL081. Ohjelma toimii turvallisessa tilassa
(TrustZone), joten se käyttää muistien ja oheislaitteiden turvallisia
aliaksia. Linkkeriskripti ja UARTin osoite valitaan makrolla `AN505`
(ks. `yhteinen/an505.ld` ja `mps2.h`). Rekisterikartta:

```{.c tiedosto="esimerkit/07-dma/pl081.h" osa="rekisterit"}
```

Kanava käynnistetään kirjoittamalla lähde, kohde, ensimmäisen
kuvaajan osoite ja ohjaussana kanavan rekistereihin ja lopuksi
käyttöönottobitti. Ennen käynnistystä tarvitaan muistiaita:

```{.c tiedosto="esimerkit/07-dma/main.c" osa="kaynnista"}
```

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="aidat"}
```

Prosessori voi pitää kirjoituksia kirjoituspuskurissaan, ja kääntäjä
voi järjestää muistioperaatioita uudelleen. DMA lukee muistia suoraan,
joten sen on nähtävä lähdedata ja kuvaajat ennen kuin se käynnistyy.
DSB odottaa, että aiemmat kirjoitukset ovat valmiit, ja sen `memory`-
merkintä estää kääntäjää siirtämästä muistioperaatioita aidan yli.
Siirron jälkeen tarvitaan sama toiseen suuntaan: prosessori ei saa
lukea kohdepuskuria ennen kuin DMA on valmis. Kääntäjän näkökulmasta
puskuria ei muuta kukaan, joten sen arvot voisivat olla jäljellä
rekistereissä aiemmasta luvusta. Aita tai `volatile`-lippu ja
funktiokutsu katkaisevat tämän päättelyn.

## Kopio, ketju ja yleinen virhe

Yksinkertaisin siirto on muistista muistiin. Kanava poistuu käytöstä,
kun kaikki sanat on siirretty:

```{.c tiedosto="esimerkit/07-dma/main.c" osa="kopio"}
```

Kuvaajaketju kokoaa viestin kolmesta erillisestä palasta ilman
yhtään prosessorin kopiota. Vain viimeisessä kuvaajassa on
keskeytysbitti, joten valmistumisesta ilmoitetaan kerran:

```{.c tiedosto="esimerkit/07-dma/main.c" osa="ketju"}
```

Kolmas siirto näyttää DMA:n yleisimmän virheen. Määrä annetaan
tavuina (`sizeof`), vaikka ohjain laskee sen lähteen leveyden
yksiköissä. 32 tavun eli 8 sanan kopiosta tulee 32 sanan kopio, joka
ylikirjoittaa puskurin perässä olevan muistin. Kukaan ei ilmoita
virheestä, ja vioittunut data löytyy jostain muualta paljon
myöhemmin.

```{.c tiedosto="esimerkit/07-dma/main.c" osa="koko"}
```

```{.tuloste tiedosto="esimerkit/testit/07-dma.odotettu"}
```

Emulaattorissa on kaksi rajoitusta, jotka on hyvä tietää. QEMU:n PL081
tekee koko siirron heti, kun kanava käynnistetään, joten siirto on
valmis jo seuraavalla käskyllä. Oikea DMA kilpailee väylästä
prosessorin kanssa ja valmistuu myöhemmin, joten ohjelma ei saa olettaa
mitään siirron kestosta. Lisäksi QEMU 8.2:n `mps2-an505`-mallissa DMA:n
keskeytys ei päädy NVIC:iin: kanavan valmistumisbitti nousee, mutta
mikään NVIC:n odottavien keskeytysten rekisterin bitti ei asetu.
Esimerkki kutsuu siksi samaa käsittelyfunktiota odotussilmukasta, jota
oikeassa ohjelmassa kutsuisi keskeytyskäsittelijä. Käsittelyn sisältö
on molemmissa sama: tilan luku, kuittaus ja tiedon välitys
pääohjelmalle.

## Välimuisti

Cortex-M3 ja M33 tässä kokoonpanossa eivät käytä datavälimuistia, mutta
Cortex-M7, monet M55-piirit ja kaikki sovellusprosessorit käyttävät.
Silloin DMA ja prosessori voivat nähdä saman osoitteen eri arvoisena:
prosessorin kirjoitus voi olla vasta välimuistissa, ja DMA:n kirjoitus
voi jäädä vanhan välimuistirivin taakse. Säännöt:

- **Ennen kuin DMA lukee muistia** (lähetys), puskurin välimuistirivit
  *kirjoitetaan muistiin* (clean). CMSIS: `SCB_CleanDCache_by_Addr`.
- **Ennen kuin prosessori lukee DMA:n kirjoittamaa muistia**
  (vastaanotto), rivit *mitätöidään* (invalidate), jotta seuraava
  luku hakee ne muistista. CMSIS: `SCB_InvalidateDCache_by_Addr`.
  Mitätöinti tehdään myös ennen siirron käynnistystä, jottei
  likainen rivi kirjoitu myöhemmin DMA:n datan päälle.
- **Puskuri tasataan välimuistirivin rajalle** (Cortex-M7:ssä
  32 tavua) ja sen koko pyöristetään rivin monikertaan. Muuten
  mitätöinti tuhoaa samalla rivillä olevan toisen muuttujan.
- Vaihtoehto on sijoittaa DMA-puskurit alueelle, jota ei välimuisteta:
  MPU:n määrittämälle alueelle tai tiiviisti kytkettyyn muistiin
  (TCM), jos DMA pääsee siihen.

Välimuistivirheet ovat ajoituksesta riippuvia ja katoavat usein
debuggerissa, koska pysäytys tyhjentää välimuistin tai muuttaa sen
sisältöä. Siksi säännöt kannattaa koota yhteen ajurikerrokseen eikä
ripotella sovellukseen.

## DMA ja prosessori samalla väylällä

DMA ei ole ilmainen. Se käyttää samaa väylämatriisia ja samoja
muistipankkeja kuin prosessori, ja kun molemmat haluavat samaan
pankkiin, toinen odottaa. Pitkät purskeet nopeuttavat siirtoa mutta
voivat viivästyttää keskeytyksen käsittelyä, joka hakee käskyjä tai
dataa samasta muistista. Reaaliaikaisessa järjestelmässä DMA-puskurit
sijoitetaan siksi usein eri SRAM-pankkiin kuin pino ja koodi, ja
kanavien prioriteetit asetetaan tarkoituksella. Tämä kytkee DMA:n
taitoon *Suorituskyvyn analyysi ja optimointi*.

## Käytännössä

- **Laske siirron määrä leveyden yksiköissä** ja tarkista se yhdestä
  paikasta, esimerkiksi makrolla, joka jakaa koon leveydellä.
- **Pidä puskuri olemassa koko siirron ajan.** Paikallinen puskuri
  pinossa, jonka funktio palaa ennen siirron loppua, on klassinen
  muistin korruptoija.
- **Muistiaita ennen käynnistystä ja valmistumisen jälkeen**, ja
  välimuistillisessa piirissä clean ennen lähetystä ja invalidate
  ennen vastaanotetun datan lukemista.
- **Kuittaa tilabitit ennen uutta siirtoa**, ja käsittele myös
  virhekeskeytys.
- **Käytä kaksoispuskuria jatkuvaan vastaanottoon** ja tarkista,
  että käsittely ehtii valmiiksi ennen kuin DMA palaa samaan puoliskoon.

## Itsearviointi

- Osaat kuvata DMA-kanavan asetukset: osoitteet ja niiden kasvatus,
  leveys, purske, määrä ja vuonohjaus.
- Osaat käyttää kuvaajaketjua palojen kokoamiseen ja kertoa, milloin
  keskeytys kannattaa pyytää.
- Osaat selittää, miksi DMA:n käynnistys ja valmistuminen vaativat
  muistiaidan, ja mitä `volatile` ja `memory`-merkintä tekevät.
- Osaat soveltaa välimuistin clean- ja invalidate-sääntöjä ja
  perustella puskurin tasauksen.
- Osaat tunnistaa yleisimmät DMA-virheet: väärä määrä, liian aikaisin
  vapautuva puskuri ja kuittaamaton tilabitti.

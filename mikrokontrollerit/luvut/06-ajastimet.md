# Ajastimet

Lähes jokainen sulautettu ohjelma tarvitsee aikaa: LEDin vilkutus,
anturin lukeminen kymmenen kertaa sekunnissa, aikakatkaisu
tiedonsiirrossa ja painikkeen värähtelyn suodatus. Mikrokontrollerissa
on tähän useita laskureita, jotka saavat kellonsa piirin
kellojärjestelmästä ja laskevat itsenäisesti prosessorin tehdessä
muuta.

| Ajastin | Missä | Tyypillinen käyttö |
|---------|-------|--------------------|
| SysTick | jokaisessa Cortex-M-ytimessä | järjestelmän tikki, RTOS:n ajoitus |
| yleisajastimet | piirin oheislaitteet | jaksolliset keskeytykset, PWM, pulssien mittaus |
| vahtikoira (watchdog) | piirin oheislaite | resetoi jumiutuneen ohjelman |
| RTC ja matalan tehon ajastin | erillinen virta-alue | kello ja herätys syvästä unesta |
| DWT:n CYCCNT | Cortex-M3 ja uudemmat | kellojaksojen mittaus |

## SysTick

SysTick on 24-bittinen alaspäin laskeva laskuri. Kun se saavuttaa
nollan, se lataa arvon LOAD-rekisteristä, asettaa COUNTFLAG-bitin ja
aiheuttaa halutessa poikkeuksen 15. Jakso on siis LOAD + 1 kelloa, ja
1 millisekunnin tikki 25 MHz:n kellolla tarvitsee arvon 24 999.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="systick"}
```

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="systick"}
```

CLKSOURCE valitsee prosessorin kellon tai piirin määrittelemän
viitekellon. CALIB-rekisteri kertoo valmistajan ilmoittaman arvon 10
millisekunnin jaksolle, mutta se ei ole kaikissa piireissä luotettava;
jakso kannattaa laskea piirin tunnetusta kellotaajuudesta.

## Aika ja ylivuoto

Millisekuntilaskuri on 32-bittinen ja pyörähtää nollaan noin 49,7
vuorokauden kuluttua. Se on pitkä aika testissä mutta lyhyt laitteelle,
joka on päällä vuosia. Vertailu `nyt >= alku + kesto` toimii, kunnes
`alku + kesto` ylittää rajan; sen jälkeen ehto on väärin juuri
pyörähdyksen ympärillä. Etumerkitön erotus `nyt - alku` lasketaan
modulo 2^32^ ja on aina oikea kulunut aika, kunhan se on alle
2^32^ tikkiä.

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="pyorahdys"}
```

Viive odottaa nukkuen: WFI pysäyttää prosessorin seuraavaan
keskeytykseen, eli tässä seuraavaan tikkiin. Viive alkaa laskurista
`0xFFFFFFF0`, jotta pyörähdys osuu sen keskelle.

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="viive"}
```

Tikkiin perustuva viive on aina tikin tarkkuudella: `viive_ms(1)` voi
kestää lähes nollasta yhteen millisekuntiin sen mukaan, missä kohtaa
tikkiä se alkaa. Jos tarvitaan vähintään annettu aika, odotetaan yksi
tikki enemmän. Mikrosekuntiviiveisiin käytetään laskurin arvoa
suoraan: SysTickin VAL tai DWT:n CYCCNT luetaan alussa ja odotetaan,
kunnes erotus on riittävä. Tyhjä `for`-silmukka viiveenä on huono
ratkaisu, koska sen kesto riippuu kääntäjästä, optimointitasosta,
kellosta ja flashin odotustiloista.

## Oheislaitteen ajastin

Piirin omat ajastimet ovat monipuolisempia: niissä on esijakaja,
ylös- tai alaspäin laskeva laskuri, uudelleenlatausarvo ja yleensä
useita *vertailu- ja kaappauskanavia*. CMSDK:n ajastin on
yksinkertaisimmasta päästä: 32-bittinen alaspäin laskeva laskuri ja
keskeytys nollassa.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="ajastin"}
```

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="ajastin0"}
```

Rekisterien kirjoitusjärjestyksellä on väliä: tämän ajastimen
RELOAD-kirjoitus asettaa myös laskurin arvon. Tällaiset sivuvaikutukset
löytyvät vain käyttöohjeesta, ja niiden huomiotta jättäminen tuottaa
ajastimen, joka laukeaa väärään aikaan vain ensimmäisellä kerralla.

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="kaytto"}
```

## Kuittaamaton keskeytys

Ajastimen keskeytyslinja on *tasoherkkä*: se pysyy ylhäällä, kunnes
INTSTATUS-bitti kuitataan. Jos käsittelijä ei kuittaa, NVIC merkitsee
keskeytyksen heti uudelleen odottavaksi, ja prosessori palaa
käsittelijään ketjutettuna. Pääohjelma ei pääse etenemään, mutta
mikään ei kaadu: laite vain näyttää jumiutuneelta. Esimerkin ajastin
laukeaa kerran, ja käsittelijä kuittaa joko heti tai vasta
tuhannennella kerralla.

```{.c tiedosto="esimerkit/06-ajastimet/main.c" osa="myrsky"}
```

```{.tuloste tiedosto="esimerkit/testit/06-ajastimet.odotettu"}
```

Viive toimii pyörähdyksen yli oikein, ajastin0 vaihtoi LEDiä
kymmenen kertaa (parillinen määrä, joten LED on taas pois), ja
kuittaamaton keskeytys ajettiin tuhat kertaa yhden laukeamisen
seurauksena.

## PWM ja kaappaus

Yleisajastimen vertailukanava vertaa laskuria rekisterin arvoon ja voi
muuttaa nastan tilaa ilman ohjelmaa. Kun nasta nousee laskurin alussa
ja laskee vertailuarvon kohdalla, syntyy *pulssinleveysmodulaatio*
(PWM): jakso pysyy samana ja pulssin leveys määrää keskimääräisen
tehon. LEDin kirkkaus, moottorin nopeus ja servon asento ohjataan
näin. Kaappauskanava toimii päinvastoin: se tallentaa laskurin arvon,
kun nastalla tapahtuu reuna, jolloin pulssin pituus tai taajuus
mitataan kellojakson tarkkuudella ilman, että keskeytyksen viive
vaikuttaa tulokseen.

```{.ajoituskaavio otsikko="PWM ja kaappaus (periaate). Laskuri kiertää 0–7; lähtö on ylhäällä, kun laskuri on pienempi kuin vertailuarvo 3. Kaappausrekisteri tallentaa laskurin arvon tulon nousevalla reunalla."}
{"signal": [
  {"name": "kello", "wave": "p................"},
  {"name": "laskuri", "wave": "=================",
   "data": ["0","1","2","3","4","5","6","7","0","1","2","3","4","5","6","7","0"]},
  {"name": "PWM-lähtö", "wave": "1..0....1..0....1"},
  {},
  {"name": "tulo", "wave": "0....1...0...1..."},
  {"name": "kaappaus", "wave": "x....=.......=...", "data": ["5", "5"]}
], "config": {"hscale": 0.8}}
```

Kuvan PWM:n pulssisuhde on 3/8. Tulon kaksi nousevaa reunaa kaapattiin
samalla laskurin arvolla peräkkäisillä kierroksilla, joten tulon jakso
on täsmälleen kahdeksan kelloa. Oikeassa ajastimessa laskurin
pyörähdykset lasketaan mukaan ylivuotokeskeytyksessä, kun mitattava
jakso on laskurin kierrosta pidempi. CMSDK:n ajastimessa ei ole
vertailu- eikä kaappauskanavia, joten tätä ei voi ajaa emuloidulla
kortilla; rekisterien nimet ja bitit ovat joka valmistajalla omansa.

## Ajastin laukaisee A/D-muunnoksen

Mikrokontrollerin oma A/D-muunnin (ADC) on tavallisesti
*peräkkäisapproksimaatiomuunnin* (SAR). Se toimii kahdessa vaiheessa:
näytteenottokondensaattori kytketään tuloon *näytteenottoajaksi*, ja
sen jälkeen muunnin hakee jännitettä vastaavan luvun bitti kerrallaan.
N-bittinen muunnin jakaa viitejännitteen $V_\mathrm{ref}$ 2^N^ portaaseen:

$$\mathrm{koodi} = \left\lfloor \frac{V_\mathrm{in}}{V_\mathrm{ref}}
\, 2^N \right\rfloor, \qquad
t_\mathrm{muunnos} = t_\mathrm{näyte} + N \cdot t_\mathrm{ADC-kello}.$$

12-bittisellä muuntimella ja 3,3 voltin viitteellä yksi porras on 0,8
millivolttia. Tulos on suhteessa viitejännitteeseen, joten viitteen
kohina ja ryömintä näkyvät suoraan mittauksessa. Jos mitattavan
lähteen impedanssi on suuri, kondensaattori ei ehdi latautua lyhyessä
näytteenottoajassa ja tulos jää liian pieneksi; näytteenottoaika
valitaan rekisteristä lähteen mukaan.

Signaalia mitattaessa tärkeintä on näytteiden *tasainen väli*. Jos
muunnos käynnistetään ohjelmasta, esimerkiksi tikkikeskeytyksen
käsittelijästä, näytteenottohetki heiluu keskeytyksen viiveen verran
(luku 5), ja heilunta näkyy signaalissa kohinana. Siksi ajastin
kytketään laukaisemaan muunnos suoraan laitteistossa: ajastimen
tapahtuma käynnistää näytteenoton, ja ohjelma saa keskeytyksen vasta,
kun tulos on valmis.

```{.ajoituskaavio otsikko="Ajastimen laukaisema A/D-muunnos (periaate). Näytteenottohetki ei riipu siitä, milloin ohjelma ehtii lukea tuloksen."}
{"signal": [
  {"name": "ajastimen tapahtuma", "wave": "010.......10......"},
  {"name": "muunnin", "wave": "2.3.4...2..3.4...2",
   "data": ["lepo", "näyte", "muunnos", "lepo", "näyte", "muunnos", "lepo"]},
  {"name": "valmis-keskeytys", "wave": "0.......10.......1"},
  {"name": "tulosrekisteri", "wave": "x.......=........=", "data": ["n", "n+1"]},
  {"name": "käsittelijä lukee", "wave": "0.........1.0....."}
], "config": {"hscale": 0.8}}
```

Näytteenottotaajuuden on oltava yli kaksi kertaa signaalin suurin
taajuus, ja sitä suuremmat taajuudet on suodatettava pois analogisesti
ennen muunninta (laskostuminen, taito *Signaalit ja järjestelmät*).
Hitaassa mittauksessa tarkkuutta saa lisää *ylinäytteistämällä*:
neljän peräkkäisen näytteen keskiarvo antaa yhden lisäbitin, kunhan
signaalissa on vähintään portaan verran kohinaa. Kun näytteitä tulee
tuhansia sekunnissa, tulokset siirretään puskuriin DMA:lla eikä
keskeytyksellä.

Emuloidussa kortissa ei ole A/D-muunninta. Taidossa *Oheislaiteväylät*
luetaan ulkoista muunninta SPI-väylän kautta emuloidusta piiristä, ja
taito *Digitaalinen signaalinkäsittely* käsittelee näytteet, jotka
tällainen keskeytys tuottaa.

## Vahtikoira

Vahtikoira on ajastin, joka resetoi piirin, jos ohjelma ei *ruoki*
sitä määräajassa. Se on viimeinen suoja virheelle, jota ei osattu
ennakoida: silmukka, joka odottaa ikuisesti, lukkiutunut tilakone tai
häiriön sekoittama muisti. CMSDK:n vahtikoirassa on kaksi porrasta.
Ensimmäinen aikaraja aiheuttaa keskeytyksen, joka on tällä kortilla
kytketty NMI:hin, ja jos sitä ei kuitata, toinen aikaraja resetoi
laitteen. Lukitusrekisteri estää karannutta ohjelmaa sammuttamasta
vahtia vahingossa.

```{.c tiedosto="esimerkit/yhteinen/mps2.h" osa="vahtikoira"}
```

```{.c tiedosto="esimerkit/06-vahtikoira/main.c" osa="vahti"}
```

Ratkaisevaa on, *missä* vahtia ruokitaan. Ruokinta kuuluu paikkaan,
jossa ohjelma todistaa toimivansa, yleensä pääsilmukan loppuun sen
jälkeen, kun jokainen tehtävä on edennyt. Esimerkin pääsilmukka mittaa
ja lähettää, ja kolmannella kierroksella lähetys jää odottamaan
kuittausta, jota ei tule:

```{.c tiedosto="esimerkit/06-vahtikoira/main.c" osa="tyo"}
```

Yleinen virhe on ruokkia vahtia ajastimen keskeytyksessä, koska se on
helppo paikka, joka ajetaan varmasti. Juuri siksi se on väärä:
keskeytys jatkuu, vaikka pääsilmukka olisi jumissa, eikä vahtikoira
koskaan laukea. Esimerkin tikkikäsittelijä tekee näin ensimmäisellä
käynnistyksellä ja toteaa itse, että pääsilmukka on seissyt kolme
aikarajaa:

```{.c tiedosto="esimerkit/06-vahtikoira/main.c" osa="tikki"}
```

Varoituskeskeytys on viimeinen tilaisuus kirjata, missä ohjelma oli.
Käsittelijä tallentaa vaiheen `.noinit`-alueelle (luku 3), joka säilyy
resetin yli, ja jättää keskeytyksen kuittaamatta:

```{.c tiedosto="esimerkit/06-vahtikoira/main.c" osa="nmi"}
```

```{.c tiedosto="esimerkit/06-vahtikoira/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/06-vahtikoira.odotettu"}
```

Ensimmäisellä käynnistyksellä laite olisi jäänyt jumiin pysyvästi,
vaikka vahtikoira oli päällä. Toisella vahti varoitti 100 millisekunnin
ja resetoi 200 millisekunnin kuluttua viimeisestä ruokinnasta, ja
kolmas käynnistys tietää syyn ja vaiheen. Oikeassa piirissä resetin
syy luetaan lisäksi valmistajan tilarekisteristä, joka erottaa
virrankytkennän, nastan, ohjelmallisen resetin ja vahtikoiran, ja
kirjaus lähetetään eteenpäin, kun yhteys taas toimii (luku 9).
Ikkunoitu vahtikoira hylkää myös liian aikaisen ruokinnan, mikä
paljastaa silmukan, joka ruokkii ja ohittaa muun työn.

Monissa piireissä vahtikoiraa ei voi pysäyttää käynnistyksen jälkeen,
ja sillä on oma kellolähteensä, jotta se toimii, vaikka pääkello
pysähtyisi. Emulaattorissa aikaraja kuluu virtuaaliajassa, joten
testi ajetaan QEMU:n valitsimella `-icount`, joka sitoo ajan
suoritettuihin käskyihin.

## Käytännössä

- **Laske aikaa etumerkittömällä erotuksella** `nyt - alku`, älä
  vertaa absoluuttisia aikoja.
- **Testaa ylivuoto aloittamalla laskuri läheltä rajaa.** Esimerkin
  tapa, `millit = 0xFFFFFFF0u`, löytää 49 päivän virheen sekunnissa.
- **Kuittaa ajastimen keskeytys** ja lue käyttöohjeesta, mitä
  rekisterikirjoitukset tekevät sivuvaikutuksina.
- **Käytä laitteiston PWM:ää ja kaappausta ohjelmallisen ajoituksen
  sijaan.** Ne ovat tarkkoja riippumatta keskeytysten viiveestä.
- **Ruoki vahtikoiraa vain todistetusta edistyksestä**, ei
  ajastimesta.
- **Laukaise A/D-muunnos ajastimella**, kun mittaat signaalia, ja
  valitse näytteenottoaika lähteen impedanssin mukaan.

## Itsearviointi

- Osaat alustaa SysTickin halutulle jaksolle ja selittää, miksi LOAD on
  jakso miinus yksi.
- Osaat kirjoittaa aikavertailun, joka toimii laskurin pyörähtäessä,
  ja testata sen.
- Osaat toteuttaa viiveen, joka nukkuu, ja kertoa sen tarkkuuden.
- Osaat selittää, mitä tasoherkälle keskeytykselle tapahtuu, jos sitä
  ei kuitata.
- Osaat kuvata PWM:n ja kaappauksen periaatteen.
- Osaat selittää, miksi A/D-muunnos laukaistaan ajastimella
  laitteistossa, ja laskea muuntimen portaan koon ja muunnosajan.
- Osaat ottaa vahtikoiran käyttöön, perustella ruokinnan paikan ja
  tallentaa jumiutumisen syyn seuraavaa käynnistystä varten.

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

## PWM, kaappaus ja vahtikoira

Yleisajastimen vertailukanava vertaa laskuria rekisterin arvoon ja voi
muuttaa nastan tilaa ilman ohjelmaa. Kun nasta nousee laskurin alussa
ja laskee vertailuarvon kohdalla, syntyy *pulssinleveysmodulaatio*
(PWM): jakso pysyy samana ja pulssin leveys määrää keskimääräisen
tehon. LEDin kirkkaus, moottorin nopeus ja servon asento ohjataan
näin. Kaappauskanava toimii päinvastoin: se tallentaa laskurin arvon,
kun nastalla tapahtuu reuna, jolloin pulssin pituus tai taajuus
mitataan kellojakson tarkkuudella ilman, että keskeytyksen viive
vaikuttaa tulokseen.

Vahtikoira on ajastin, joka resetoi piirin, jos ohjelma ei *ruoki*
sitä määräajassa. Ruokinta kuuluu paikkaan, jossa ohjelma todistaa
toimivansa, yleensä pääsilmukan loppuun sen jälkeen, kun jokainen
tehtävä on raportoinut edistyneensä. Ruokinta ajastimen
keskeytyksessä on yleinen virhe: keskeytys jatkuu, vaikka pääsilmukka
olisi jumissa, eikä vahtikoira koskaan laukea. Ikkunoitu vahtikoira
hylkää myös liian aikaisen ruokinnan, mikä paljastaa silmukan, joka
ruokkii ja ohittaa muun työn.

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

## Itsearviointi

- Osaat alustaa SysTickin halutulle jaksolle ja selittää, miksi LOAD on
  jakso miinus yksi.
- Osaat kirjoittaa aikavertailun, joka toimii laskurin pyörähtäessä,
  ja testata sen.
- Osaat toteuttaa viiveen, joka nukkuu, ja kertoa sen tarkkuuden.
- Osaat selittää, mitä tasoherkälle keskeytykselle tapahtuu, jos sitä
  ei kuitata.
- Osaat kuvata PWM:n, kaappauksen ja vahtikoiran periaatteen ja
  vahtikoiran oikean ruokintapaikan.

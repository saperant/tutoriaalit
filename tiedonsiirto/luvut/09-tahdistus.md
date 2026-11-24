# Symboli- ja kehystahdistus

Vastaanottimen A/D-muunnin näytteistää omalla kellollaan, joka ei ole
lähettimen symbolikellon tahdissa. Symbolin paras näytehetki on
tuntematon, ja se liukuu, koska kellojen taajuudet eroavat.
**Symbolitahdistus** etsii ja seuraa näytehetkeä. **Kehystahdistus**
selvittää, mistä kohdasta symbolivirtaa paketti tai kehys alkaa. Tämä
luku toteuttaa kummankin.

## Näytehetken valinta

Luvun 5 silmäkuvio näytti, että väärä näytehetki pienentää silmän
aukeamaa ja lisää ISI:ä. Vastaanotin ei voi vain valita lähintä
näytettä, koska näytteitä on tyypillisesti 2–8 symbolia kohti, ja
paras hetki osuu niiden väliin. Siksi arvo **interpoloidaan**
näytteiden välistä, ja interpolointikohtaa säädetään silmukalla.
Rakenne on sama kuin luvun 8 vaihelukitussa silmukassa: virheilmaisin,
silmukkasuodin ja NCO, joka nyt kertyttää aikaa vaiheen sijaan.

## Gardnerin ajoitusvirheilmaisin

**Gardnerin ilmaisin** tarvitsee kaksi näytettä symbolia kohti:
näytteen symbolin kohdalta ja näytteen kahden symbolin puolivälistä.
Kun symboli vaihtuu, signaali ylittää nollan puolivälissä. Jos
näytehetki on myöhässä, puolivälin näyte on jo nollan ohi seuraavan
symbolin suuntaan:

$$e_k = \operatorname{Re}\bigl\{(y_k - y_{k-1})\,y^*_{k-1/2}\bigr\}.$$

Ilmaisin ei tarvitse päätöksiä eikä kantoaallon vaihetta, joten
symbolitahdistus voi lukittua ennen kantoaallon palautusta.

Kokeessa lähetin käyttää RRC-pulssia ($\beta = 0{,}5$). Vastaanottimen
kello on 0,1 symbolia väärässä vaiheessa ja 200 ppm liian hidas, joten
näytehetki liukuu 0,0002 symbolia jokaisella symbolilla. Analoginen
signaali mallinnetaan 64 näytteellä symbolia kohti, ja vastaanotin
näytteistää sitä kahdeksalla näytteellä symbolia kohti.

```{.python tiedosto="esimerkit/09-gardner.py" osa="kanava"}
```

Silmukka lukee näytteen murtoindeksistä lineaarisella interpoloinnilla.
Tuotantovastaanottimissa käytetään kuutiollista Farrow-interpolaattoria
tai polyfaasisuodinpankkia, jotka ovat tarkempia pienemmällä
ylinäytteistyksellä.

```{.python tiedosto="esimerkit/09-gardner.py" osa="gardner"}
```

Mallista tiedetään oikeat symbolihetket, joten tulosta voi verrata
niihin. Vertailukohtana on vastaanotin, joka ottaa yksinkertaisesti
joka kahdeksannen näytteen.

```{.python tiedosto="esimerkit/09-gardner.py" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/09-gardner.odotettu"}
```

Ilman tahdistusta EVM kasvaa paketin aikana, koska näytehetki liukuu
symbolin keskeltä reunalle. 200 ppm:n kellovirhe siirtää näytettä
puoli symbolia 2 500 symbolissa. Gardner-silmukka seuraa
näytehetkeä niin, että ajoitusvirhe pysyy alle prosentissa
symbolin kestosta. Kuten kantoaallon silmukassa, ensimmäisen asteen
silmukkaan jää pysyvä virhe (1,3 % symbolista), koska kellojen
taajuusero vaatii jatkuvan korjauksen. Toisen asteen silmukka poistaa
sen.

## Kehystahdistus korrelaatiolla

Paketin alussa on tunnettu **alkuosa** (*preamble*), jota vastaanotin
etsii korreloimalla vastaanotettua signaalia sen kanssa. Hyvän alkuosan
autokorrelaatiossa on terävä huippu ja pienet sivukeilat, jotta
väärien osumien todennäköisyys on pieni ja paikka tarkka.
**Barker-koodit** ovat lyhyitä binäärijonoja, joiden autokorrelaation
sivukeilat ovat enintään 1.

```{.python tiedosto="esimerkit/09-kehys.py" osa="barker"}
```

Vastaanotin ei tiedä kantoaallon vaihetta, joten korrelaation
itseisarvoa verrataan kynnykseen. Kynnys asetetaan suhteessa
vastaanotetun signaalin energiaan samassa ikkunassa, jolloin se ei
riipu vastaanotetun signaalin tasosta. Kun kynnys ylittyy, valitaan
suurin huippu seuraavan alkuosan pituuden sisältä.

```{.python tiedosto="esimerkit/09-kehys.py" osa="etsi"}
```

```{.tuloste tiedosto="esimerkit/09-kehys.odotettu"}
```

Kaikki viisi kehystä löytyvät oikeista kohdista, vaikka
signaali-kohinasuhde on vain 3 dB ja kantoaallon vaihe tuntematon.
Normitettu mitta on kehyksen kohdalla vähintään 0,70 ja muualla
enintään 0,38, joten kynnykselle 0,5 jää marginaalia kumpaankin
suuntaan. Taajuusvirhe kiertää vaihetta alkuosan aikana 19 astetta ja
pienentää korrelaatiohuippua hieman. Paljon suuremmalla taajuusvirheellä
alkuosa jaetaan osiin, joiden korrelaatioiden itseisarvot summataan.

## Käytännössä

- **Tahdista järjestyksessä.** Tyypillinen järjestys on: kehyksen
  havaitseminen ja karkea ajoitus alkuosasta, karkea taajuusvirhe,
  sitten tarkka ajoitus- ja vaiheseuranta silmukoilla. Gardner-ilmaisin
  toimii kantoaallon vaiheesta riippumatta, joten se voi edeltää
  vaihesilmukkaa.
- **Interpoloi, älä vaihda näytetaajuutta.** Ohjelmistovastaanotin
  korjaa kellovirheen interpolaattorilla. Laitteistossa vaihtoehto on
  ohjata A/D-muuntimen kelloa, mutta se on hitaampi ja kalliimpi.
- **Valitse alkuosa autokorrelaation mukaan.** Barker-, m-jono- ja
  Zadoff–Chu-jonoilla on pienet sivukeilat. Pituus määrää
  havaitsemisvarmuuden: kymmenen kertaa pidempi alkuosa antaa 10 dB
  lisää korrelaatiovahvistusta.
- **Mittaa kynnyksen marginaali.** Simuloi kehyksen kohdan ja muun
  datan korrelaatiomitan jakaumat ja aseta kynnys niiden väliin.
  Raportoi sekä havaitsematta jääneiden että väärien hälytysten
  todennäköisyys.

## Itsearviointi

- Osaat selittää, miksi symbolin näytehetki on interpoloitava ja miksi
  kellojen taajuusero tekee siitä liukuvan.
- Osaat toteuttaa Gardnerin ajoitusvirheilmaisimen ja toisen asteen
  ajoitussilmukan sekä arvioida niiden tarkkuutta.
- Osaat etsiä kehyksen alun korrelaatiolla tuntemattomasta vaiheesta
  huolimatta ja asettaa normitetun kynnyksen.
- Osaat perustella alkuosan valinnan sen autokorrelaation avulla.

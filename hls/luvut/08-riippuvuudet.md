# Riippuvuudet muistin kautta

Luvun 6 takaisinkytkentä kulki muuttujan kautta, ja työkalu näki sen
suoraan koodista. Muistin kautta kulkeva riippuvuus on vaikeampi: kun
kierros kirjoittaa alkioon `h[x[i]]` ja seuraava lukee alkion
`h[x[i + 1]]`, ovatko ne sama alkio? Se riippuu datasta. Työkalun on
oletettava pahin, ja suunnittelijan on tiedettävä, milloin oletus on
turha ja milloin välttämätön.

## Histogrammi

Histogrammi laskee, montako kertaa kukin arvo esiintyy syötteessä.
Kierros lukee luokan laskurin, kasvattaa sitä ja kirjoittaa sen
takaisin:

```{.cpp tiedosto="esimerkit/08-histogrammi/hist.cpp" osa="ydin"}
```

```{.tuloste tiedosto="esimerkit/08-histogrammi/odotettu" osa="ajo1"}
```

Ajoituksesta näkyy ongelma. Syötteen alkio luetaan jaksolla 0, sen
osoittama laskuri jaksolla 1, ja kasvatettu arvo kirjoitetaan jaksolla
2. Jos II olisi 1, seuraava kierros lukisi laskurinsa samalla jaksolla 2,
jolla edellinen kierros kirjoittaa, eli ennen kirjoitusta. Jos
peräkkäiset alkiot kuuluvat samaan luokkaan, lukeminen saisi vanhan
arvon ja yksi lisäys katoaisi. Siksi työkalu valitsee II = 2: lukeminen
tapahtuu vasta jaksoa myöhemmin kuin edellinen kirjoitus.

## Riippuvuusanalyysi

Kun indeksit ovat silmukkamuuttujan lineaarisia lausekkeita, työkalu
voi laskea, millä kierrosten etäisyydellä kaksi osoitetta voivat olla
samat. Jos kierros *n* kirjoittaa alkioon *c · n + a* ja kierros *n + d*
lukee alkion *c · n + b*, osoitteet ovat samat, kun *c · d = a − b*:

```{.python tiedosto="esimerkit/minihls/dfg.py" osa="etaisyys"}
```

| Koodi | Etäisyys | Rajoittaako II:tä |
|-------------------------------|--------------------|----------------------------|
| `y[i] = x[i] + 1` | eri taulukot | ei |
| `a[i] = a[i] + 1` | sama kierros, ei kantamaa | ei |
| `a[i] = a[i - 1] + 1` | 1 | kyllä, kuten muuttuja |
| `a[i] = a[i - 4] + 1` | 4 | vain, jos ketju on yli 4 · II jaksoa |
| `h[x[i]] += 1` | tuntematon, oletetaan 1 | kyllä |

Etäisyys *d* lieventää ehtoa *d*-kertaisesti, koska arvo tarvitaan
vasta *d* kierrosta myöhemmin. Oikeat työkalut tekevät saman analyysin
monimutkaisemmille indekseille (esimerkiksi polyhedrimalli
sisäkkäisille silmukoille), mutta datasta riippuva indeksi on niillekin
tuntematon.

## Väärä lupaus

Pragma `dependence` kertoo työkalulle, ettei riippuvuutta ole, tai
antaa sen etäisyyden:

```{.cpp tiedosto="esimerkit/08-histogrammi/hist_vaara.cpp" osa="pragma"}
```

Työkalu uskoo pragmaa eikä voi tarkistaa sitä. Histogrammissa lupaus on
väärä, ja tulos näkyy vasta yhteissimulaatiossa:

```{.tuloste tiedosto="esimerkit/08-histogrammi/odotettu" osa="ajo2"}
```

II on 1 ja latenssi puolittui, mutta tulokset ovat väärin. C-simulaatio
meni läpi, koska kääntäjä ei tunne pragmaa: C++-ohjelmana ydin on
oikein. Virhe on tuotetussa laitteistossa, ja sen voi löytää vain
simuloimalla RTL:ää testivektoreilla, joissa peräkkäiset alkiot
toistuvat. Satunnaisessa syötteessä 16 luokasta toisto on niin yleinen,
että kaikki luokat menivät väärin. Syötteellä, jossa peräkkäiset arvot
ovat aina eri luokissa, virhe ei näkyisi lainkaan; siksi testipenkki
tuottaa toistoja tarkoituksella.

Pragma on oikea työkalu silloin, kun suunnittelija tietää jotain, mitä
työkalu ei voi päätellä: esimerkiksi että indeksit ovat permutaatio,
jossa sama alkio ei toistu, tai että kaksi kierrosta ei koskaan osu
samaan puoliskoon. Silloinkin lupaus on todennettava
yhteissimulaatiolla.

## Riippuvuuden kiertäminen

Histogrammin riippuvuus on todellinen, mutta sitä voi kiertää jakamalla
laskennan kahteen *osahistogrammiin*. Parilliset alkiot kasvattavat
toista ja parittomat toista, jolloin kummallakin riippuvuusketjulla on
kaksi jaksoa aikaa, ja kierros käsittelee kaksi alkiota:

```{.cpp tiedosto="esimerkit/08-histogrammi/hist_kaksi.cpp" osa="ydin"}
```

Paikalliset taulukot `p` ja `q` ovat ytimen sisäisiä muisteja. Syöte
jaetaan syklisesti kahteen pankkiin, jotta molemmat alkiot saadaan
samalla jaksolla:

```{.tuloste tiedosto="esimerkit/08-histogrammi/odotettu" osa="ajo3"}
```

Laskentasilmukan II on edelleen 2, mutta se käsittelee kaksi alkiota,
joten läpäisy on yksi alkio jaksossa. Osahistogrammien nollaus ja
yhdistäminen vievät 33 jaksoa, ja koko ydin vie 292 jaksoa 515:n sijaan.
Kun syöte on pitkä, nollaus ja yhdistys ovat pieni osa ajasta, ja
osahistogrammeja voi olla useampia. Tulokset ovat oikein, koska
riippuvuutta ei ohitettu vaan se jaettiin.

Muita tapoja käsitellä samaa ongelmaa:

| Tekniikka | Periaate |
|----------------------------------|----------------------------------------|
| osahistogrammit | riippuvuus jaetaan useaan muistiin |
| edellisen arvon välitys (*forwarding*) | jos luokka on sama kuin edellisellä kierroksella, käytetään rekisterissä olevaa arvoa |
| kertymä rekisterissä | peräkkäiset samat luokat lasketaan rekisteriin ja kirjoitetaan kerralla |
| muistin viiveen lyhentäminen | LUTRAM, jonka lukuviive on 0, lyhentää ketjua |
| lajittelu ensin | samat luokat peräkkäin, laskenta ilman muistia |

## Käytännössä

- **Lue II:n syy raportista.** Muistin kautta kulkeva riippuvuus
  näkyy taulukon nimenä; se ei katoa muistiportteja lisäämällä.
- **Älä käytä `dependence false` -pragmaa nopeuttaaksesi.** Käytä sitä
  vain, kun tiedät, ettei riippuvuutta ole, ja todenna se testeillä,
  jotka tuottavat pahimman tapauksen.
- **Testipenkki päättää, löytyykö virhe.** Satunnainen syöte ei
  välttämättä sisällä tapauksia, joissa riippuvuus toteutuu: tuota ne
  tarkoituksella.
- **Jaa riippuvuus, älä ohita sitä.** Osahistogrammit, välitys ja
  osittaiset summat säilyttävät oikeellisuuden ja parantavat
  läpäisyä.

## Itsearviointi

- Osaat tunnistaa koodista muistin kautta kulkevan kantaman
  riippuvuuden ja selittää, miksi se rajoittaa aloitusväliä.
- Osaat laskea riippuvuuden etäisyyden lineaarisille indekseille ja
  kertoa, miten etäisyys lieventää ehtoa.
- Osaat selittää, miksi väärä `dependence`-pragma läpäisee
  C-simulaation mutta ei yhteissimulaatiota.
- Osaat kiertää histogrammin riippuvuuden osahistogrammeilla tai
  välityksellä ja todentaa tuloksen.

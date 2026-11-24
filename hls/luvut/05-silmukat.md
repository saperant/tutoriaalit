# Silmukat ja avaaminen

Silmukat ovat HLS:n tärkein optimointikohde, koska lähes kaikki
laskenta on niissä. Liukuhihnattoman silmukan latenssi on

*latenssi = kierrokset · kierroksen pituus*,

joten nopeuttamiseen on kaksi keinoa: lyhentää kierrosta tai vähentää
kierroksia tekemällä enemmän työtä kierroksessa. Tämä luku käsittelee
jälkimmäistä, *silmukan avaamista* (*loop unrolling*). Liukuhihnoitus,
jossa kierrokset limittyvät, on seuraavan luvun aihe.

## Kierroksen pituus ja silmukan hallinta

Luvun 1 pistetulon kierros vei kaksi jaksoa: jaksolla 0 luetaan
alkiot muistista ja jaksolla 1 lasketaan tulo ja summa. Kierroksen
laskuri, vertailu ja siirtyminen seuraavaan kierrokseen ovat
tilakoneessa eivätkä vie omaa jaksoaan. Oikeissa työkaluissa silmukan
hallinta lisää usein yhden jakson kierrosta tai silmukkaa kohti
(silmukan poistumisehto tarkistetaan omassa tilassaan), ja raportti
näyttää erikseen *kierroksen latenssin* (*iteration latency*) ja
*silmukan latenssin*.

Sisäkkäisissä silmukoissa sisäsilmukan aloitus ja lopetus toistuvat
jokaisella ulomman silmukan kierroksella. Vitis HLS voi *litistää*
(*loop flatten*) täydellisesti sisäkkäiset silmukat yhdeksi silmukaksi,
jolloin hallinnan jaksot katoavat ja koko sisäkkäinen rakenne voidaan
liukuhihnoittaa kerralla. minihls ei litistä silmukoita.

## Osittainen avaaminen

Pragma `unroll factor=2` kopioi silmukan rungon kahdesti ja puolittaa
kierrokset:

```{.cpp tiedosto="esimerkit/05-avaus/mac_2.cpp" osa="pragma"}
```

Muunnos tehdään jäsennyspuulle ennen tietovuograafia. Kopiossa `k`
silmukkamuuttuja korvataan lausekkeella `i + k · askel`, ja askel
kerrotaan avauskertoimella. Täysi avaus korvaa muuttujan vakioilla, ja
silmukka katoaa:

```{.python tiedosto="esimerkit/minihls/muunnokset.py" osa="avaa"}
```

Kierrosmäärän on oltava jaollinen kertoimella. Oikeat työkalut
hyväksyvät myös jaottoman kierrosmäärän ja lisäävät jokaiseen kopioon
ehdon, joka ohittaa ylimääräiset kierrokset.

Avattu silmukka ajoitetaan kuten mikä tahansa suoraviivainen koodi:

```{.tuloste tiedosto="esimerkit/05-avaus/odotettu" osa="ajo2"}
```

Kierros laskee nyt kaksi tuloa kolmessa jaksossa, joten silmukka vie
12 jaksoa 16:n sijaan. Ajoituksesta näkyy, miksi parannus ei ole
kaksinkertainen: kummastakin muistista voi lukea vain yhden alkion
jaksossa, joten toinen alkiopari luetaan jaksolla 1. Toinen kertolasku
odottaa dataa jaksolle 2, ja koska ne ovat eri jaksoilla, molemmat
käyttävät samaa kertojaa `mul0`.

## Täysi avaaminen

Pragma `unroll` ilman kerrointa avaa silmukan kokonaan. Kahdeksan
kierroksen pistetulosta tulee yksi suoraviivainen lohko, jossa on
kahdeksan lukua kummastakin muistista, kahdeksan kertolaskua ja
seitsemän yhteenlaskua. Samaan taulukkoon on lisätty myös luvun 7
keino, *taulukon jako*: kumpikin taulukko jaetaan kahdeksaan pankkiin,
joilla on omat porttinsa:

```{.tuloste tiedosto="esimerkit/05-avaus/odotettu" osa="ajo3"}
```

```{.tuloste tiedosto="esimerkit/05-avaus/odotettu" osa="ajo4"}
```

Vertailu kaikista neljästä muunnelmasta:

| Muunnelma | Latenssi | Kertojat | Multiplekserit (bittiä) | Kiikut (bittiä) |
|--------------------|----------|----------|-------------------------|-----------------|
| ei avausta | 19 | 1 | 87 | 71 |
| avaus kahdella | 15 | 1 | 220 | 106 |
| täysi avaus | 10 | 1 | 554 | 262 |
| täysi avaus ja jako | 5 | 8 | 12 | 292 |

Täysi avaus ilman jakoa on huono kompromissi. Muistiportti rajoittaa
lukemisen yhteen alkioon jaksossa, joten kahdeksan tuloa lasketaan
silti peräkkäin, ja ne jakavat yhden kertojan, jonka eteen tulee
kahdeksan syötteen multiplekseri. Avaus ilman riittävää muistikaistaa
kasvattaa piiriä mutta nopeuttaa sitä vähän. Jaettuna kahdeksan
kertolaskua tehdään samalla jaksolla, ja latenssin määräävät enää
lukeminen, kertolasku ja seitsemän yhteenlaskun ketju: lohko vie neljä
jaksoa, koska 10 ns:n jaksoon mahtuu enintään viisi peräkkäistä
yhteenlaskua.

## Mitä avaaminen maksaa

- **Laitteisto kasvaa avauskertoimen mukana**, jos operaatiot tehdään
  rinnakkain. Täysi avaus 1 000 kierroksen silmukasta tuottaa tuhat
  kopiota rungosta.
- **Muistikaista ratkaisee.** Avaus hyödyttää vain, jos data saadaan
  yhtä nopeasti kuin laskenta sitä kuluttaa (luku 7).
- **Kantama riippuvuus jää.** Summa `s` on yhä yksi ketju: avaus ei
  muuta summien järjestystä, joten kahdeksan yhteenlaskua ovat
  peräkkäin. Kokonaisluvuilla työkalu tai suunnittelija voi järjestää
  summan puuksi; liukuluvuilla järjestyksen muuttaminen muuttaa
  tulosta, ja työkalut tekevät sen vain luvan kanssa.
- **Käännösaika kasvaa.** Suuri avattu runko hidastaa ajoitusta ja
  sidontaa, ja raportti muuttuu vaikealukuiseksi.

## Käytännössä

- **Avaa sisimpiä silmukoita, joiden kierrosmäärä on pieni**, kuten
  suodinkertoimet tai matriisin rivi. Suurilla silmukoilla käytä
  osittaista avausta tai liukuhihnoitusta.
- **Mitoita avaus muistiporttien mukaan.** Jos taulukosta luetaan
  avauksen jälkeen *k* alkiota kierroksessa, jaa se vähintään *k*
  pankkiin tai hyväksy, että luvut ovat peräkkäin.
- **Avaa ennen kuin optimoit käsin.** Pragma on helpompi muuttaa kuin
  käsin avattu koodi, ja C-simulaatio pysyy samana.
- **Liukuhihnoitus avaa sisäsilmukat itse.** Kun ulompi silmukka
  liukuhihnoitetaan, sen sisäsilmukat avataan kokonaan (luku 7).

## Itsearviointi

- Osaat laskea liukuhihnattoman silmukan latenssin kierrosten määrästä
  ja kierroksen pituudesta.
- Osaat avata silmukan osittain ja kokonaan pragmalla ja kertoa, miten
  työkalu muuntaa rungon.
- Osaat selittää, miksi avaus ilman riittävää muistikaistaa ei nopeuta
  silmukkaa mutta kasvattaa piiriä.
- Osaat arvioida avauksen vaikutuksen yksiköiden, multiplekserien ja
  rekisterien määrään.

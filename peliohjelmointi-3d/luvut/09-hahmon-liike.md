# Hahmon liike

Pelaajan hahmo on pelin eniten viilattu kappale. Sen pitää kulkea
rinteitä valumatta, nousta portaat pysähtymättä, liukua seinää pitkin
takertumatta ja pudota reunalta silloin, kun pelaaja sitä odottaa.
Fysiikkasimulaatio ei tuota tällaista liikettä itsestään, ja siksi
hahmo on lähes kaikissa peleissä *kinemaattinen*: koodi päättää, minne
hahmo liikkuu, ja törmäykset ainoastaan korjaavat tulosta. Tässä
luvussa tehdään tällainen ohjain kapselille, joka liikkuu
kolmioverkossa.

## Tila ja asetukset

Hahmo on kapseli, jonka paikka annetaan jalkojen kohdalta. Vaakaliike
tulee suoraan syötteestä; pystysuunnassa hahmolla on nopeus, jota
painovoima kasvattaa.

```{.cpp tiedosto="esimerkit/yhteinen/hahmo.hpp" osa="hahmo"}
```

Asetuksissa on kolme lukua, jotka määräävät, miltä maasto tuntuu:
jyrkin *käveltävä* rinne, korkein askelma, jonka yli hahmo nousee, ja
matka, jolta hahmo vedetään takaisin maahan.

## Irrotus maailmasta

Askeleen alussa hahmo siirretään sinne, minne syöte ja painovoima sen
vievät. Sen jälkeen se on mahdollisesti seinän tai lattian sisällä, ja
se työnnetään ulos kosketuksen normaalin suuntaan (luku
*Törmäysmuodot*). Lähellä olevat kolmiot haetaan maailman BVH:sta.

```{.cpp tiedosto="esimerkit/yhteinen/hahmo.hpp" osa="syvin"}
```

```{.cpp tiedosto="esimerkit/yhteinen/hahmo.hpp" osa="ratkaise"}
```

Funktiossa on kolme ratkaisua, joista jokainen korjaa näkyvän vian.

**Syvin kosketus ensin.** Tasainen seinä on kaksi kolmiota. Kun kapseli
painuu seinään, lähin piste toisessa kolmiossa on sen sisällä, mutta
toisessa yhteisellä reunalla, ja reunasta mitattu normaali osoittaa
vinoon. Jos molemmat kosketukset purettaisiin, hahmo nytkähtäisi
sivulle joka kerta, kun se ylittää kolmioiden rajan. Kun puretaan vain
syvin kosketus ja tilanne tarkistetaan uudelleen, vino näennäiskosketus
on jo kadonnut.

**Käveltävä pinta nostaa suoraan ylös.** Jos hahmo työnnettäisiin
rinteen normaalin suuntaan, se siirtyisi joka askeleella hieman alamäkeen
ja valuisi paikallaan seistessään. Pystysuora nosto pitää hahmon
paikallaan.

**Seinä työntää vaakasuunnassa.** Liian jyrkkä rinne ei saa nostaa
hahmoa, joten normaalista käytetään vain vaakakomponentti. Seinää
vasten vinosti kävelevä hahmo menettää seinää kohti olevan osan
liikkeestään ja säilyttää seinän suuntaisen: se *liukuu*.

## Maassa pysyminen

Pelkkä irrotus ei riitä alamäessä. Hahmo liikkuu askeleen vaakasuoraan,
maa laskee sen alta, ja hahmo on hetken ilmassa: se pomppii rinnettä
alas eikä voi hypätä, koska ei ole maassa. Siksi maassa kulkenut hahmo
lasketaan askeleen lopuksi alas, kunnes kapseli koskee johonkin:

```{.cpp tiedosto="esimerkit/yhteinen/hahmo.hpp" osa="alas"}
```

Lasku tehdään muodolla eikä säteellä, jotta hahmo lepää myös askelman
reunan päällä. Säteellä tarkistetaan ainoastaan, että jalkojen alla on
käveltävää pintaa kohtuullisen matkan päässä. Jos ei ole, hahmo on
kävellyt reunan yli ja alkaa pudota.

## Portaat

Kapselin pyöreä pohja nousee matalan kynnyksen yli itsestään, mutta
askelman reuna osuu kapselin kylkeen niin jyrkässä kulmassa, että
irrotus tulkitsee sen seinäksi. Portaille tarvitaan oma sääntönsä: jos
seinä pysäytti maassa kulkevan hahmon, sama liike yritetään uudelleen
askelman verran ylempää, ja hahmo lasketaan sen jälkeen alas.

```{.cpp tiedosto="esimerkit/yhteinen/hahmo.hpp" osa="askel"}
```

```{.dot otsikko="Yhden askeleen vaiheet. Useimmilla askelilla kuljetaan suoraan ylhäältä alas."}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.35;
  liike [label="liike: syöte + painovoima\nirrotus maailmasta"];
  porras [label="sama liike askelman\nverran ylempää, lasku alas"];
  tartunta [label="lasku alas enintään\ntartuntamatkan verran"];
  loppu [label="uusi paikka ja tila"];
  liike -> porras [label="seinä pysäytti\nmaassa kulkevan"];
  liike -> tartunta [label="oli maassa,\nei enää kosketa"];
  liike -> loppu;
  porras -> loppu;
  tartunta -> loppu;
}
```

Ylempää tehty yritys hyväksytään vain, jos hahmo pääsi sillä pidemmälle
ja sekä sen alla että edessä on käveltävää pintaa. Jälkimmäinen ehto
erottaa portaan jyrkästä rinteestä: ilman sitä hahmo kiipeäisi mitä
tahansa seinää askelma kerrallaan.

## Rata

Ohjain testataan radalla, jossa on jokainen tapaus: loiva rinne,
tasanne ja pudotus, liian jyrkkä rinne, portaat ja vino seinä. Rata
kootaan laatikoista ja kiiloista esimerkin funktiossa `rata`.

Syöte on käsikirjoitus, kuten syötteen tallenne taidossa
*Peliohjelmointi*: sama käsikirjoitus tuottaa aina saman reitin, joten
ohjaimen muutos, joka rikkoo jonkin tapauksen, näkyy testissä.

```{.cpp tiedosto="esimerkit/09-hahmo.cpp" osa="ohjelma"}
```

```{.cpp tiedosto="esimerkit/09-hahmo.cpp" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/09-hahmo.odotettu"}
```

![Rata ja hahmon reitti. Punainen viiva on kuljettu maassa, keltainen
ilmassa.](kuvat/rata.png){width=100%}

![Sama reitti sivusta: jalkojen korkeus matkan funktiona. Loivaa
rinnettä hahmo nousee tasaisesti, jyrkkä pysäyttää sen, ja portaissa
korkeus nousee askelmittain. Kierto jyrkän rinteen ohi tapahtuu
kuvatason sivussa.](kuvat/rata-profiili.png){width=100%}

Loiva rinne (noin 21 astetta) on käveltävä, ja hahmo nousee sen
tasaisella vaakanopeudella. Tasanteen reunalta se putoaa, koska
jalkojen alla ei ole pintaa tartuntamatkan päässä. Jyrkkä rinne (63
astetta) pysäyttää hahmon kuin seinä, eikä porrassääntö auta, koska
edessä ei ole käveltävää. Portaissa sääntö laukeaa viisi kertaa, kerran
jokaiselle 25 sentin askelmalle. Vinoa seinää vasten hahmo liukuu
sivulle.

## Mitä ohjaimesta puuttuu

Ohjain on tarkoituksella pieni. Tuotantokäytössä siihen lisätään
ainakin liikkuvat alustat (hahmo kiinnitetään alustan lapseksi, kuten
kontti koukkuun), hahmon ja muiden hahmojen väliset törmäykset,
kyykistyminen (kapselin korkeuden muutos ja tarkistus, mahtuuko hahmo
nousemaan), pyyhkäisy nopeaa putoamista varten ja hyppyyn liittyvät
helpotukset, kuten hypyn puskurointi ja armonaika reunan jälkeen
(taito *Peliohjelmointi*). Rakenne pysyy samana: liike, irrotus ja
erikoissäännöt maalle ja portaille.

## Käytännössä

- **Hahmo on kinemaattinen.** Pelaajan hahmoa ei simuloida jäykkänä
  kappaleena. Ohjaimen säännöt ovat pelisuunnittelua: ne päättävät,
  miltä liikkuminen tuntuu.
- **Kapseli, ei laatikko.** Laatikon kulmat takertuvat seiniin ja
  reunoihin. Kapselin pyöreä pohja ylittää pienet epätasaisuudet.
- **Pura syvin kosketus ensin ja toista.** Kaikkien kosketusten
  purkaminen kerralla tuottaa nytkähdyksiä kolmioiden rajoilla.
- **Maa on normaalin kysymys.** Käveltävyys päätetään normaalin
  y-komponentista. Sama raja estää myös portaiksi tulkitut jyrkät
  rinteet.
- **Testaa radalla ja käsikirjoituksella.** Jokainen ohjaimen muutos
  rikkoo jonkin tapauksen. Rata, jossa on kaikki tapaukset, ja
  tallennettu syöte tekevät siitä regressiotestin.
- **Piirrä reitti.** Reitin värittäminen tilan mukaan paljastaa
  pomppimisen ja väärät maakosketukset yhdellä silmäyksellä.

## Itsearviointi

- Osaat selittää, miksi pelaajan hahmo on kinemaattinen ja mitä se
  tarkoittaa.
- Osaat toteuttaa kapselin irrotuksen kolmioverkosta ja perustella,
  miksi käveltävä pinta nostaa ylös ja seinä työntää vaakasuunnassa.
- Osaat kertoa, mistä kolmioiden rajoilla syntyvät näennäiskosketukset
  johtuvat ja miten ne vältetään.
- Osaat toteuttaa maassa pysymisen ja portaiden nousun ja selittää,
  miten porras erotetaan jyrkästä rinteestä.

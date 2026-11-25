# Laaja vaihe: BVH

Edellisten lukujen testit verrattiin jokaista kohdetta vastaan.
Maailmassa, jossa on tuhansia kolmioita, se on liikaa: yksi säde
tarkoittaisi tuhansia kolmiotestejä, ja säteitä heitetään kymmeniä
joka askeleella. Taito *Peliohjelmointi* ratkaisi saman ongelman
tasossa tasavälisellä ruudukolla. Kolmioverkolle, jossa kohteet ovat
erikokoisia ja epätasaisesti jakautuneita, tavallisin rakenne on
*rajaavien tilavuuksien hierarkia* (*bounding volume hierarchy*, BVH).

## Rakenne

BVH on binääripuu. Jokaisella solmulla on laatikko, joka sisältää
kaiken solmun alla olevan. Lehdissä on muutama kohde, sisäsolmuissa
kaksi lasta. Jos säde ei osu solmun laatikkoon, se ei voi osua mihinkään
solmun alla, ja koko haara ohitetaan yhdellä testillä.

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="bvh"}
```

Rakenne ei tiedä, mitä kohteet ovat. Se saa luettelon laatikoita ja
palauttaa kohteiden indeksejä; tarkan testin tekee kutsuja. Sama puu
kelpaa siksi kolmioille, pelin kappaleille ja seuraavissa luvuissa
näkyvyyskarsintaan.

## Rakennus

Puu rakennetaan ylhäältä alas. Solmun laatikko on sen kohteiden
laatikoiden yhdiste. Kohteet jaetaan kahtia laatikon pisimmän akselin
suunnassa niin, että puolet jää kummallekin puolelle keskipisteiden
mediaania. Jako toistetaan, kunnes kohteita on enintään lehden koko.

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="rakenna"}
```

Mediaanijako tekee puusta tasapainoisen, joten syvyys kasvaa
logaritmisesti kohteiden määrän mukaan. `nth_element` jakaa osavälin
lineaarisessa ajassa lajittelematta sitä kokonaan.

Esimerkin maailma on maasto, jonka korkeus on muutaman kummun summa,
ja kaksi laatikkoa:

```{.cpp tiedosto="esimerkit/yhteinen/maasto.hpp" osa="korkeus"}
```

```{.cpp tiedosto="esimerkit/07-bvh.cpp" osa="maailma"}
```

```{.tuloste tiedosto="esimerkit/07-bvh.odotettu" rivit="1-1"}
```

![Maasto ja puun kolme ylintä tasoa: punaiset laatikot ovat juuren
lapset, keltaiset niiden lapset ja siniset seuraava taso. Sisarusten
laatikot voivat mennä päällekkäin; se on sallittua, mutta jokainen
päällekkäisyys maksaa ylimääräisiä
testejä.](kuvat/bvh.png){width=80%}

## Säteen läpikäynti

Säde testataan ensin juuren laatikkoa vastaan. Jos se osuu, käsitellään
solmun kohteet tai siirrytään lapsiin. Kun jokin osuma on jo löytynyt,
haara ohitetaan myös silloin, kun säde tulee sen laatikkoon vasta
löydetyn osuman takana.

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="sade-bvh"}
```

```{.cpp tiedosto="esimerkit/07-bvh.cpp" osa="sateet"}
```

```{.tuloste tiedosto="esimerkit/07-bvh.odotettu" rivit="3-6"}
```

Ylhäältä tuleva säde löytää osumansa 37 laatikkotestillä ja kahdeksalla
kolmiotestillä, kun kolmioita on 4 632. Säde, joka ei osu juuren
laatikkoon, hylätään yhdellä testillä. Vaakasuora säde kulkee monen
laatikon läpi ennen osumaa ja maksaa enemmän: läpikäynti käy lapset
kiinteässä järjestyksessä. Tuotantototeutus käy ensin sen lapsen, jonka
laatikkoon säde tulee aiemmin, jolloin lähin osuma löytyy varhain ja
karsii loput.

Rakenne on oikein vain, jos se antaa saman vastauksen kuin kaikkien
kohteiden testaaminen. Se varmistetaan vertaamalla:

```{.cpp tiedosto="esimerkit/07-bvh.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-bvh.odotettu" rivit="8-9"}
```

Kahdellesadalle säteelle tulos on sama, ja testejä tehdään keskimäärin
28 sädettä kohden 4 632:n sijaan.

## Alueen kysely

Hahmon törmäyksiä varten ei tarvita sädettä vaan kaikki kolmiot, jotka
ovat hahmon lähellä. Yleinen läpikäynti saa ehdon, jolla haara
hyväksytään, ja funktion, jota kutsutaan jokaiselle lehden kohteelle:

```{.cpp tiedosto="esimerkit/yhteinen/bvh.hpp" osa="lapikaynti"}
```

```{.cpp tiedosto="esimerkit/07-bvh.cpp" osa="alue"}
```

```{.tuloste tiedosto="esimerkit/07-bvh.odotettu" rivit="11-11"}
```

Hahmon kokoinen alue antaa 52 ehdokasta, joille tehdään tarkka testi.
Staattinen maailma kootaan luokaksi, joka omistaa kolmiot ja puun ja
tarjoaa nämä kaksi kyselyä:

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="maailma"}
```

## Liikkuvat kohteet ja muut rakenteet

Staattisen maailman puu rakennetaan kerran latauksen yhteydessä.
Liikkuville kappaleille on kolme tavallista tapaa: puu rakennetaan joka
askeleella uudelleen (mediaanijaolla se on nopeaa muutamalle tuhannelle
kappaleelle), solmujen laatikot *sovitetaan* uusiin paikkoihin
rakennetta muuttamatta, tai käytetään dynaamista puuta, jossa lehtiä
lisätään ja poistetaan. Fysiikkamoottorit pitävät staattiset ja
liikkuvat kappaleet yleensä eri puissa.

| Rakenne | Vahvuus | Heikkous |
|---------|---------|----------|
| tasavälinen ruudukko | yksinkertainen, vakioaikainen lisäys | erikokoiset kohteet, tyhjä tila |
| BVH | sopeutuu kohteiden kokoon ja tiheyteen | rakennus maksaa, päivitys vaatii työtä |
| kahdeksanpuu, k-d-puu | jakaa tilan eikä kohteita | kohde voi kuulua moneen soluun |

## Käytännössä

- **Laaja vaihe ei saa muuttaa tulosta.** Rakenne on optimointi, ja
  sen oikeellisuus testataan vertaamalla raakaan hakuun.
- **Kohteet indekseinä.** Puu ei omista kohteita, joten sama toteutus
  palvelee törmäyksiä, säteitä ja karsintaa.
- **Solmut yhtenä taulukkona.** Osoittimilla linkitetty puu hajottaa
  muistin; taulukko ja indeksit pitävät läpikäynnin välimuistissa.
- **Mittaa testien määrää, älä vain aikaa.** Laatikko- ja kohdetestien
  laskurit kertovat suoraan, toimiiko karsinta.
- **Staattinen ja liikkuva erikseen.** Maailman puu rakennetaan kerran
  ja huolella, liikkuvien puu nopeasti ja usein.

## Itsearviointi

- Osaat selittää, miksi BVH nopeuttaa kyselyjä ja mistä sen
  logaritminen syvyys tulee.
- Osaat rakentaa BVH:n mediaanijaolla ja käydä sen läpi säteellä niin,
  että jo löydetty osuma karsii haaroja.
- Osaat varmistaa testillä, ettei laaja vaihe muuta kyselyn tulosta.
- Osaat verrata BVH:ta ruudukkoon ja kertoa, miten liikkuvat kohteet
  käsitellään.

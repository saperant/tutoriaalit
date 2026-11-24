# Kolmiot

Kolmio on reaaliaikagrafiikan perusmuoto. Kolme pistettä määrää aina
tason, kolmio on aina kupera, ja minkä tahansa pinnan voi
approksimoida kolmioilla. Näytönohjaimet rasteroivat käytännössä vain
kolmioita: nelikulmiot, monikulmiot ja paksut viivat pilkotaan
kolmioiksi ennen rasterointia.

Tässä luvussa kolmio on jo ruudun koordinaateissa. Miten kolmion kärjet
sinne päätyvät, on seuraavan luvun aihe.

## Reunafunktio

Vanha tapa rasteroida kolmio on jakaa se vaakasuoriin juoviin
(scanline) ja täyttää jokainen juova vasemmalta reunalta oikealle.
Nykyiset näytönohjaimet käyttävät **reunafunktioita** (Pineda 1988),
koska ne sopivat rinnakkaislaskentaan: jokaisen pikselin voi testata
toisista riippumatta.

Reunafunktio kertoo, kummalla puolella suoraa $a \to b$ piste $p$ on.
Se on ristitulon $z$-komponentti eli kolmion $(a, b, p)$
kaksinkertainen etumerkillinen ala:

$$E_{ab}(p) = (p_x - a_x)(b_y - a_y) - (p_y - a_y)(b_x - a_x).$$

Kun kolmion kärjet ovat näytöllä katsottuna vastapäivään, kolmion
sisäpisteissä kaikki kolme reunafunktiota $E_{bc}$, $E_{ca}$ ja
$E_{ab}$ ovat positiivisia. Ruudun $y$-akseli osoittaa alas, joten
kaava on peilikuva matematiikan kirjojen tavallisesta muodosta.

```{.cpp tiedosto="esimerkit/yhteinen/rasteri.hpp" osa="kiintopiste"}
```

Kärkien koordinaatit pyöristetään ennen testiä **kiinteän pilkun**
ruudukkoon, jossa pikseli on jaettu 256 osaan. Näytönohjaimet tekevät
samoin (tyypillisesti 8 alipikselibittiä). Pyöristyksen jälkeen
reunafunktio lasketaan kokonaisluvuilla, joten tulos on tarkka:
nolla tarkoittaa, että piste on täsmälleen reunalla, eikä
liukulukujen pyöristys voi päättää asiaa kahdelle kolmiolle eri tavoin.

## Rasterointisilmukka

Rasteroija käy läpi kolmion rajaavan suorakulmion pikselit, laskee
jokaisen keskipisteen kolme reunafunktiota ja hyväksyy pikselin, jos
mikään ei ole negatiivinen:

```{.cpp tiedosto="esimerkit/yhteinen/rasteri.hpp" osa="rasteroi"}
```

Jos kolmion kärjet ovat myötäpäivään, ala on negatiivinen ja kärjet
`b` ja `c` vaihdetaan, jotta sama testi toimii. Painot vaihdetaan
takaisin ennen kutsua, joten kutsuja saa painot alkuperäisessä
järjestyksessä. Takapintojen hylkääminen kiertosuunnan perusteella
on putken päätös eikä rasteroijan (luku *Syvyys ja näkyvyys*).

Rajaava suorakulmio on yksinkertainen tapa löytää ehdokkaat. Ohut,
vino kolmio peittää vain pienen osan suorakulmiostaan, joten
laitteistot käyvät pikseleitä läpi lohkoina (esimerkiksi $8 \times 8$)
ja hylkäävät kokonaisia lohkoja kerralla. Reunafunktio on lineaarinen
$x$:n ja $y$:n suhteen, joten seuraavan pikselin arvo saadaan
lisäämällä vakio, eikä kertolaskuja tarvita silmukan sisällä. Tässä
toteutuksessa jokainen arvo lasketaan alusta selkeyden vuoksi.

## Yhteiset reunat ja vasen-ylä-sääntö

Kun kaksi kolmiota jakaa reunan, reunalla olevat pikselit eivät saa
jäädä piirtämättä (aukko) eivätkä tulla piirretyiksi kahdesti
(läpinäkyvällä pinnalla tuplapikselit näkyvät tummempina, ja
sekoitus- tai sapluunaoperaatiot tehdään kahteen kertaan). Jos
reunalla olevat pikselit hyväksytään molemmille ($E \ge 0$),
tuplapikseleitä syntyy. Jos ne hylätään molemmille ($E > 0$), syntyy
aukkoja.

Ratkaisu on **vasen-ylä-sääntö** (top-left rule): reunalla oleva
pikseli kuuluu kolmioon vain, jos reuna on kolmion *yläreuna*
(vaakasuora, kolmio sen alapuolella) tai *vasen reuna*. Jokainen
yhteinen reuna on toiselle kolmiolle vasen tai ylä ja toiselle oikea tai
ala, joten pikseli päätyy täsmälleen yhteen kolmioon.

```{.cpp tiedosto="esimerkit/yhteinen/rasteri.hpp" osa="vasen-yla"}
```

Rasteroijassa sääntö toteutetaan **vinoumana**: muiden reunojen
arvosta vähennetään yksi, jolloin nolla muuttuu negatiiviseksi.
Kiinteän pilkun ansiosta yksi on pienin mahdollinen ero, joten
vinouma ei siirrä mitään muuta pikseliä.

Seuraava ohjelma piirtää kuusikulmion kuutena kolmiona ja neliön
kahtena kolmiona. Kärjet ovat pikselien keskipisteissä, joten monen
pikselin keskipiste osuu täsmälleen reunalle. Luku kertoo, montako
kertaa pikseli piirrettiin:

```{.cpp tiedosto="esimerkit/04-peitto.cpp" osa="kolmiot"}
```

```{.cpp tiedosto="esimerkit/04-peitto.cpp" osa="laske"}
```

```{.tuloste tiedosto="esimerkit/04-peitto.odotettu"}
```

Ilman sääntöä vaakasuora keskijana on piirretty kahdesti ja
kuusikulmion keskipiste kuudesti. Säännön kanssa jokainen pikseli on
piirretty kerran, ja myös kuvion ulkoreunat noudattavat samaa sääntöä:
oikean ja alareunan pikselirivit jäävät pois. Kun viereen piirretään
toinen kuvio, se täyttää ne.

## Barysentriset koordinaatit

Rasteroija antaa jokaiselle pikselille kolme painoa
$\lambda_0, \lambda_1, \lambda_2$: reunafunktiot jaettuina kolmion
kaksinkertaisella alalla. Ne ovat pisteen **barysentriset
koordinaatit**:

$$p = \lambda_0 a + \lambda_1 b + \lambda_2 c, \qquad
\lambda_0 + \lambda_1 + \lambda_2 = 1.$$

Paino $\lambda_0$ on pisteen ja vastakkaisen reunan $bc$ muodostaman
osakolmion ala suhteessa koko kolmioon. Se on 1 kärjessä $a$ ja 0
reunalla $bc$. Kolmion sisällä kaikki painot ovat välillä 0–1, ja
ulkopuolella jokin on negatiivinen; reunafunktiotesti on siis sama
asia kuin painojen etumerkin tarkistus.

```{.cpp tiedosto="esimerkit/yhteinen/rasteri.hpp" osa="bary"}
```

```{.cpp tiedosto="esimerkit/04-barysentrinen.cpp" osa="painot"}
```

Kolmion painopisteessä kaikki painot ovat $1/3$, ja kolmion
ulkopuolisella pisteellä yksi paino on negatiivinen, vaikka summa on
edelleen 1.

## Interpolointi

Painoilla interpoloidaan mikä tahansa kärkiin liitetty arvo: väri,
normaali, tekstuurikoordinaatti tai syvyys. Arvo pikselissä on
$\lambda_0 v_a + \lambda_1 v_b + \lambda_2 v_c$. Klassinen esimerkki on
kolmio, jonka kärjet ovat punainen, vihreä ja sininen:

```{.cpp tiedosto="esimerkit/04-barysentrinen.cpp" osa="vari"}
```

```{.tuloste tiedosto="esimerkit/04-barysentrinen.odotettu"}
```

![Kärkien värit interpoloituna barysentrisillä painoilla. Värit
sekoitetaan lineaarisina ja koodataan sRGB:ksi.](kuvat/04-barysentrinen.png){width=35%}

Kolmion ala on 1040 pikseliä ja piirrettyjä pikseleitä on 1036.
Ero johtuu siitä, että vain keskipisteet testataan: reunojen
osittain peitetyt pikselit joko kuuluvat kolmioon kokonaan tai eivät
ollenkaan. Tämä on porrastuksen (aliasing) syy, ja siihen palataan
luvussa *Reunanpehmennys*.

Keskikohdan väri on harmahtava (157, 158, 153), koska kolmen päävärin
lineaarinen keskiarvo on harmaa. Jos värit interpoloitaisiin
sRGB-tavuina, keskikohta olisi selvästi tummempi.

Ruudulla lineaarinen interpolointi on oikein vain, kun kolmio on
ruudun suuntainen. Perspektiivissä kolmion kaukainen pää kutistuu, ja
painot on korjattava. Se on luvun *Perspektiivi* aihe.

## Käytännössä

- **Pyöristä kärjet kiinteään pilkkuun ennen peittotestiä.** Silloin
  samat reunat tuottavat samat päätökset molemmille kolmioille, ja
  tulos on toistettava.
- **Noudata vasen-ylä-sääntöä**, tai jokin yhteinen reuna tuottaa
  aukkoja tai tuplapikseleitä. Ero ei näy läpinäkymättömissä pinnoissa
  ennen kuin jokin sekoittaa tai laskee pikseleitä.
- **Barysentriset painot ovat rasteroinnin tärkein tulos.** Kaikki
  kärkiin liitetyt arvot interpoloidaan niillä.
- **Ohuet ja pienet kolmiot ovat kalliita.** Rajaava suorakulmio on
  suuri suhteessa peitettyyn alaan, ja hyvin pienet kolmiot
  (alle pikselin) tuhlaavat laitteistonkin tehoa.

## Itsearviointi

- Osaat laskea reunafunktion ja kertoa, mitä sen etumerkki ja nolla
  tarkoittavat.
- Osaat selittää vasen-ylä-säännön ja sen, miksi se tarvitaan
  yhteisille reunoille.
- Osaat laskea pisteen barysentriset koordinaatit ja interpoloida
  niillä kärkiin liitetyn arvon.
- Osaat perustella, miksi kärkien koordinaatit pyöristetään
  kiinteään pilkkuun ennen rasterointia.

# Approksimointi ja tarkka haku

NP-vaikean tehtävän edessä on kolme vaihtoehtoa.
*Approksimaatioalgoritmi* toimii polynomiajassa ja takaa, että
ratkaisu on enintään tietyn kertoimen päässä optimista. *Heuristiikka* on yleensä hyvä ja
nopea, mutta takuuta ei ole. *Tarkka haku* löytää optimin, mutta sen
aika on pahimmillaan eksponentiaalinen. Haarautuminen ja karsinta sekä
dynaaminen ohjelmointi osajoukkojen yli tekevät siitä silti
käyttökelpoisen pienille ja keskikokoisille syötteille. Tämän luvun
esimerkit vertaavat menetelmiä tarkkaan optimiin.

## Approksimaatiokerroin

Minimointitehtävän algoritmi on *$\rho$-approksimaatio*, jos sen
ratkaisun arvo on jokaisella syötteellä enintään $\rho \cdot
\text{OPT}$. Takuun todistaminen vaatii alarajan optimille, koska
optimia ei tunneta. Todistus vertaa algoritmin tulosta alarajaan ja
alarajaa optimiin.

## Solmupeite: kerroin 2

Etsitään pienin solmujoukko, joka koskettaa jokaista kaarta. Algoritmi
käy kaaret läpi ja ottaa molemmat päät aina, kun kaari on vielä
peittämättä. Otetut kaaret eivät jaa päätepisteitä, joten ne
muodostavat parituksen $M$. Mikä tahansa peite tarvitsee jokaisesta
$M$:n kaaresta vähintään yhden pään, joten $\text{OPT} \ge |M|$.
Algoritmin peitteen koko on $2|M| \le 2\,\text{OPT}$:

```{.cpp tiedosto="esimerkit/14-peitto.cpp" osa="solmupeite"}
```

Ilmeinen ahne vaihtoehto, joka ottaa aina eniten kaaria peittävän
solmun, on yllättäen huonompi. Sen kerroin voi kasvaa logaritmisesti.
Kerrointa $2 - \varepsilon$ ei osata saavuttaa, ja
*Unique Games* -konjektuurin mukaan se on mahdotonta.

## Joukkopeite: kerroin ln n

Annettuna on perusjoukko ja kokoelma sen osajoukkoja. Etsitään
pienin määrä osajoukkoja, joiden yhdiste on koko perusjoukko. Ahne
algoritmi valitsee aina joukon, joka peittää eniten vielä peittämättömiä
alkioita. Sen kerroin on $H(n) = 1 + 1/2 + \cdots + 1/n \le \ln n + 1$.
Kerroin on käytännössä paras mahdollinen: Dinurin ja Steurerin (2014)
mukaan kerrointa $(1 - \varepsilon) \ln n$ ei saavuteta
polynomiajassa, ellei $P = NP$.

```{.cpp tiedosto="esimerkit/14-peitto.cpp" osa="joukkopeite"}
```

Esimerkki vertaa molempia tarkkaan optimiin, joka lasketaan käymällä
läpi kaikki osajoukot. Verkoissa on enintään 14 solmua ja
joukkopeitteissä enintään 12 joukkoa. Lisäksi se tarkistaa, että
solmupeite on sallittu ja kerroin enintään 2:

```{.tuloste tiedosto="esimerkit/14-peitto.odotettu"}
```

Satunnaisilla syötteillä algoritmit ovat usein paljon parempia kuin
niiden takuu. Solmupeitteen kerroin 2 kuitenkin saavutetaan, jos
verkko on paritus: jokainen kaari erikseen, jolloin optimi ottaa yhden
pään ja algoritmi molemmat. Ahneen joukkopeitteen huonoimmat tapaukset
ovat rakennettuja, ja satunnaisdata osuu niihin harvoin.

## Kauppamatkustajan ongelma

Etsitään lyhin kierros, joka käy jokaisessa kaupungissa kerran.
Yleisessä muodossa ongelmaa ei voi edes approksimoida millään
kertoimella. Jos voisi, sillä voisi ratkaista Hamiltonin kierron.
*Metrisessä* tapauksessa, jossa etäisyydet toteuttavat
kolmioepäyhtälön, on kuitenkin hyviä menetelmiä.

**Held–Karp** (1962) on dynaaminen ohjelmointi osajoukkojen yli.
Taulukon alkio $\text{paras}[S][v]$ on lyhin polku solmusta 0 joukon
$S$ kautta solmuun $v$. Aika on $O(2^n n^2)$. Se on eksponentiaalinen,
mutta paljon parempi kuin $(n-1)!/2$ kierroksen läpikäynti: $n = 20$
on noin 400 miljoonaa askelta $6 \cdot 10^{16}$:n sijaan.

```{.cpp tiedosto="esimerkit/14-kauppamatkustaja.cpp" osa="tarkka"}
```

Kolme heuristiikkaa:

- **Lähin naapuri** menee aina lähimpään käymättömään kaupunkiin.
  Se on nopea, mutta viimeiset siirtymät joutuvat usein kulkemaan
  pitkiä matkoja. Takuuta ei ole vakiokertoimella.
- **Virittävän puun kierros** on 2-approksimaatio. Pienin virittävä
  puu on alaraja ($\text{MST} \le \text{OPT}$, koska kierros ilman
  yhtä kaarta on virittävä puu). Puun esijärjestys kulkee jokaisen
  kaaren enintään kahdesti, ja kolmioepäyhtälön ansiosta jo käytyjen
  solmujen ohittaminen ei pidennä. *Christofidesin* algoritmi (1976)
  korjaa puun parittomien solmujen parituksella ja saavuttaa kertoimen
  $3/2$.
- **2-opt** on paikallinen haku. Jos kahden kaaren vaihtaminen
  ristiin lyhentää kierrosta, kierroksen väli käännetään. Haku
  toistetaan, kunnes parannusta ei löydy. Takuuta ei ole, mutta
  tulos on käytännössä muutaman prosentin päässä optimista.

```{.cpp tiedosto="esimerkit/14-kauppamatkustaja.cpp" osa="kaksiopt"}
```

Lähin naapuri ja puukierros ovat esimerkkitiedostossa
`14-kauppamatkustaja.cpp`. Puukierros rakentaa virittävän puun
Primin algoritmilla taulukolla ($O(n^2)$) ja kulkee sen esijärjestyksessä
pinon avulla.

Etäisyydet pyöristetään kokonaisluvuiksi kuten TSPLIB-kirjaston
EUC_2D-muodossa. Pyöristys voi rikkoa kolmioepäyhtälön yhdellä
yksiköllä, joten ohjelma tarkistaa puurajan jokaisella syötteellä
erikseen. Vertailussa on 30 satunnaista 11 kaupungin karttaa:

```{.tuloste tiedosto="esimerkit/14-kauppamatkustaja.odotettu"}
```

Takuullinen algoritmi ei ole käytännössä paras. Virittävän puun
kierros on huonompi kuin lähin naapuri, vaikka vain sillä on takuu.
2-opt parantaa lähimmän naapurin alle prosentin päähän optimista.
Linin–Kernighanin heuristiikka ja sen toteutus LKH ovat tämän ajatuksen
jatkoa. Ne löytävät satojentuhansien kaupunkien kierroksia, jotka ovat
murto-osan prosentin päässä tunnetusta alarajasta.

## Haarautuminen ja karsinta

*Peruuttava haku* (engl. *backtracking*) rakentaa ratkaisua askel
kerrallaan ja peruu askeleen, kun se ei voi johtaa sallittuun
ratkaisuun. *Haarautuminen ja karsinta* (engl. *branch and bound*)
lisää siihen optimirajan. Jokaiselle haaralle lasketaan yläraja sille,
kuinka hyvän ratkaisun haara voi enintään tuottaa. Jos raja ei ylitä
parasta jo löydettyä ratkaisua, haara karsitaan.

0/1-reppuongelmassa esineet otetaan mukaan tai jätetään pois.
Peruuttava haku karsii vain ylipainoiset haarat:

```{.cpp tiedosto="esimerkit/14-reppu.cpp" osa="peruutus"}
```

Hyvä yläraja saadaan *relaksaatiosta*, eli helpommasta tehtävästä,
jonka optimi on vähintään alkuperäisen optimi. Murto-osainen reppu,
jossa esineestä saa ottaa osan, ratkeaa ahneesti arvotiheyden
mukaan. Sen arvo on siis yläraja 0/1-repulle. Kun esineet käydään läpi
samassa tiheysjärjestyksessä, ensimmäinen haara löytää heti hyvän
ratkaisun, ja raja karsii suurimman osan muista:

```{.cpp tiedosto="esimerkit/14-reppu.cpp" osa="karsinta"}
```

Malliksi käy dynaaminen ohjelmointi kapasiteetin yli (taito
*Algoritmit*):

```{.cpp tiedosto="esimerkit/14-reppu.cpp" osa="dp"}
```

Vertailu ratkaisee 20 satunnaista 20 esineen tehtävää kaikilla kolmella
menetelmällä. Kapasiteetti on puolet esineiden yhteispainosta, ja
arvo korreloi painon kanssa, mikä tekee karsinnasta vaikeampaa:

```{.tuloste tiedosto="esimerkit/14-reppu.odotettu"}
```

Karsinta pienentää hakupuuta lähes kuusituhatkertaisesti. Pahin
tapaus on yhä eksponentiaalinen, mutta käytännössä rajan laatu
ratkaisee. Lineaarisen ohjelmoinnin relaksaatio on sama ajatus
yleisessä muodossa, ja kokonaislukuoptimoinnin ratkaisijat (ILP)
yhdistävät sen haarautumiseen ja karsintaan.

## Menetelmän valinta

| Tilanne | Menetelmä |
|---------|-----------|
| pieni $n$ (osajoukot $\le 2^{25}$) | raaka haku tai DP osajoukkojen yli |
| hyvä yläraja tai alaraja on helppo laskea | haarautuminen ja karsinta |
| pienet kokonaislukupainot | pseudopolynominen DP |
| takuu tarvitaan | approksimaatioalgoritmi |
| laatu tärkeämpi kuin takuu | heuristiikka ja paikallinen haku |
| ongelma on standardi ja suuri | SAT-, ILP- tai rajoiteratkaisija |

## Käytännössä

- Laske aina alaraja tai yläraja. Sen avulla tiedät, kuinka kaukana
  heuristiikan tulos voi olla optimista, vaikka optimia ei tunneta.
- Aloita heuristiikka hyvästä alkuratkaisusta ja paranna sitä
  paikallisella haulla. 2-opt lähimmän naapurin päälle on paljon
  parempi kuin kumpikaan yksin.
- Haarautumisessa ja karsinnassa järjestys on tärkeä. Lupaavin haara
  ensin tuottaa hyvän ratkaisun aikaisin, ja se tekee karsinnasta
  tehokkaan.
- Testaa approksimaatio- ja heuristiikka-algoritmit tarkkaa
  ratkaisua vastaan pienillä syötteillä. Tarkista sallittuus
  (`vaadi`) ja raportoi kerroin, äläkä vaadi optimia.
- Takuu koskee pahinta tapausta. Satunnaisdata antaa usein liian
  myönteisen kuvan. Kokeile myös rakenteellisia syötteitä, kuten
  ryppäitä, ruudukkoja ja kaukaisia pisteitä.

## Itsearviointi

- Osaat määritellä approksimaatiokertoimen ja todistaa solmupeitteen
  2-approksimaation parituksen avulla.
- Osaat toteuttaa ahneen joukkopeitteen ja kertoa sen kertoimen ja
  miksi parempaa ei odoteta.
- Osaat ratkaista pienen kauppamatkustajan ongelman Heldin–Karpin
  menetelmällä ja perustella virittävän puun kierroksen kertoimen 2.
- Osaat toteuttaa 2-opt-paikallishaun ja arvioida heuristiikkojen
  laatua tarkkaa optimia vastaan.
- Osaat toteuttaa haarautumisen ja karsinnan relaksaatiosta saadulla
  rajalla ja selittää, miksi haarojen järjestys vaikuttaa tehoon.

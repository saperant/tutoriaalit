# Fenwick-puu ja segmenttipuu

Taulukon välisummat saa etuliitesummista vakioajassa:
$\text{summa}[a, b) = P[b] - P[a]$. Jos taulukkoa kuitenkin
päivitetään, jokainen päivitys muuttaa kaikkia myöhempiä
etuliitesummia, mikä vie ajan $O(n)$. Kun kyselyjä ja päivityksiä on
yhtä paljon, tarvitaan rakenne, jossa molemmat ovat logaritmisia.
*Fenwick-puu* ratkaisee tämän etuliitesummille hyvin tiiviisti.
*Segmenttipuu* ratkaisee saman mille tahansa liitännäiselle
operaatiolle ja laajenee välipäivityksiin.

## Fenwick-puu

Fenwick-puu (Fenwick 1994, engl. *binary indexed tree*) on taulukko,
jonka solmu $i$ (1-pohjainen) tallentaa välin
$(i - \text{alin}(i), i]$ summan. Tässä $\text{alin}(i) = i \mathbin{\&} -i$
on $i$:n alin ykkösbitti. Etuliitesumma kulkee indeksistä alaspäin
poistamalla alimman bitin, ja päivitys kulkee ylöspäin lisäämällä sen.
Kumpikin kulkee enintään $\log_2 n$ askelta:

```{.cpp tiedosto="esimerkit/07-fenwick.cpp" osa="fenwick"}
```

Esimerkkiohjelma tulostaa rakenteen muodon 16 alkiolle samoilla
bittikaavoilla:

```{.tuloste tiedosto="esimerkit/07-fenwick.odotettu" rivit="1-3"}
```

```{.dot tiedosto="kaaviot/fenwick-valit.dot" otsikko="Fenwick-puun solmujen kattamat välit 16 alkiolle. Etuliitesumma 13 lukee kolme solmua (vihreät ja violetti), päivitys paikkaan 5 muuttaa neljää (punertavat ja violetti); solmu 8 kuuluu molempiin (esimerkin tulosteesta)."}
```

Etuliite 13 = 1101₂ kootaan solmuista 13 (väli 13), 12 (välit 9–12)
ja 8 (välit 1–8): yksi solmu indeksin jokaista ykkösbittiä kohti.
Päivitys viidenteen alkioon (0-pohjainen indeksi 4, solmu 5 = 101₂)
koskee solmuja 5, 6, 8 ja 16, koska vain niiden välit sisältävät
paikan 5.

Funktio `etsi()` kääntää etuliitesumman: se löytää pienimmän indeksin,
jonka etuliitesumma ylittää $k$:n. Se laskeutuu bitti kerrallaan
suurimmasta alkaen, ja ehto on, että arvot ovat ei-negatiivisia.
Kun taulukko sisältää lukumääriä, `etsi(k)` on $k$:nneksi pienin
arvo. Tämä antaa liukuvan mediaanin ja persentiilit ajassa
$O(\log U)$, missä $U$ on arvoalueen koko. Esimerkki seuraa palvelun
vasteaikoja 1001 viimeisimmän pyynnön liukuvassa ikkunassa. Uusi
pyyntö kasvattaa vasteaikansa laskuria, ja ikkunasta poistuva pyyntö
vähentää omaansa. Mediaani on `etsi(n / 2)` ja 99. persentiili
`etsi(n * 99 / 100)`.

Vertailutesti käyttää mallina tavallista taulukkoa ja laskee
välisummat ja käänteishaun raa'asti. Sen rivi on tulosteessa ensin:

```{.tuloste tiedosto="esimerkit/07-fenwick.odotettu" alkaen="vertailutesti"}
```

Kaksi prosenttia pyynnöistä on hitaita (600 ms lisää). Mediaani ei
reagoi niihin, mutta 99. persentiili reagoi, kun ikkunaan sattuu yli
kymmenen hidasta pyyntöä. Juuri siksi palveluiden viiveitä seurataan
persentiileinä.

## Segmenttipuu

Segmenttipuu on täydellinen binääripuu taulukon päällä. Lehdet ovat
taulukon alkioita, ja sisäsolmu tallentaa lastensa yhdistetyn
tuloksen. Iteratiivisessa versiossa puu on taulukossa: lehdet
indekseissä $n \ldots 2n-1$ ja solmun $i$ lapset indekseissä $2i$ ja
$2i + 1$. Välikysely $[a, b)$ nousee molemmista päistä kohti juurta
ja ottaa mukaan solmut, jotka ovat kokonaan välin sisällä:

```{.cpp tiedosto="esimerkit/07-segmentti.cpp" osa="segmentti"}
```

Operaation ei tarvitse olla vaihdannainen, kunhan se on liitännäinen
ja sillä on neutraalialkio. Vasemmalta ja oikealta kertyvät tulokset
kootaan siksi erikseen. Minimi, maksimi, summa, suurin yhteinen
tekijä, matriisitulo ja merkkijonojen katenaatio kelpaavat.
Katenaatio on hyvä testioperaatio juuri siksi, että se ei ole
vaihdannainen. Jos toteutus yhdistää osat väärässä järjestyksessä,
minimi ei sitä paljasta, mutta katenaatio paljastaa.

## Laiska päivitys

Välipäivitys "lisää $d$ jokaiseen alkioon välillä $[a, b)$" koskisi
pahimmillaan kaikkia lehtiä. *Laiska* segmenttipuu (engl. *lazy
propagation*) pysähtyy solmuihin, jotka ovat kokonaan välin sisällä.
Se päivittää niiden tuloksen ja kirjaa *lykätyn* lisäyksen, joka
koskee koko alipuuta. Lykätty lisäys työnnetään lapsille vasta, kun
jokin operaatio laskeutuu niihin. Sekä päivitys että kysely ovat
$O(\log n)$:

```{.cpp tiedosto="esimerkit/07-segmentti.cpp" osa="laiska"}
```

Laiskuus vaatii, että lykätyn päivityksen vaikutus solmun tulokseen
voidaan laskea tuntematta lehtiä. Lisäys ja maksimi sopivat yhteen,
koska $\max(x_i + d) = \max(x_i) + d$. Lisäys ja summa vaativat solmun
pituuden ($\text{summa} + d \cdot \text{pituus}$), ja asetus ja lisäys
yhdessä vaativat järjestyssäännön lykätyille operaatioille.

Esimerkki on kokoustilan varausjärjestelmä. Varaus päiville
$[a, b)$ hyväksytään, jos jokaisena päivänä on tilaa:

```{.cpp tiedosto="esimerkit/07-segmentti.cpp" osa="varaukset"}
```

Vertailutesti tarkistaa iteratiivisen puun minimillä ja
katenaatiolla ja laiskan puun taulukolla, jossa lisäys käy koko välin
läpi.

```{.tuloste tiedosto="esimerkit/07-segmentti.odotettu"}
```

## Valinta

| Rakenne | Muisti | Kysely | Päivitys | Operaatio |
|---------|--------|--------|----------|-----------|
| etuliitesummat | $n$ | $O(1)$ | $O(n)$ | käännettävä (summa) |
| Fenwick-puu | $n$ | $O(\log n)$ | $O(\log n)$ | käännettävä (summa, xor) |
| segmenttipuu | $2n$ | $O(\log n)$ | $O(\log n)$ | liitännäinen |
| laiska segmenttipuu | $4n$ | $O(\log n)$ | $O(\log n)$ väli | liitännäinen + lykkäys |
| harva taulukko | $n \log n$ | $O(1)$ | ei | idempotentti (min, max) |

Fenwick-puun välisumma vaatii vähennyslaskun, joten se ei sovi
minimiin. Segmenttipuu sopii. Jos taulukko ei muutu, *harva taulukko*
(engl. *sparse table*) antaa välin minimin vakioajassa kahdesta
limittäisestä kahden potenssin pituisesta välistä.

## Käytännössä

- Fenwick-puu on ensimmäinen valinta, kun tarvitaan summia ja
  pistepäivityksiä. Koodia on kymmenen riviä, ja se on
  välimuistiystävällinen.
- Ole tarkka indeksien kanssa. Fenwick-puu on sisäisesti
  1-pohjainen, ja segmenttipuun välit kannattaa pitää puoliavoimina
  $[a, b)$ kaikkialla.
- Testaa segmenttipuu ei-vaihdannaisella operaatiolla. Järjestysvirhe
  pysyy muuten piilossa.
- Rekursiivinen laiska puu tarvitsee $4n$ solmua, koska $n$ ei ole
  yleensä kahden potenssi. Iteratiivinen versio pärjää $2n$:llä,
  mutta laiskuus on siinä hankalampi.
- Jos arvoalue on suuri ja harva (aikaleimat, tunnisteet), pakkaa
  koordinaatit: lajittele esiintyvät arvot ja käytä niiden
  järjestyslukuja indekseinä.

## Itsearviointi

- Osaat toteuttaa Fenwick-puun ja selittää, miksi alin ykkösbitti
  määrää solmun välin.
- Osaat käyttää Fenwick-puun käänteishakua $k$:nnen arvon ja
  persentiilien löytämiseen.
- Osaat toteuttaa iteratiivisen segmenttipuun mille tahansa
  liitännäiselle operaatiolle niin, että järjestys säilyy.
- Osaat toteuttaa laiskan välipäivityksen ja perustella, milloin
  lykätyn päivityksen vaikutus voidaan laskea solmussa.
- Osaat valita etuliitesummien, Fenwick-puun, segmenttipuun ja harvan
  taulukon välillä operaation ja päivitystarpeen mukaan.

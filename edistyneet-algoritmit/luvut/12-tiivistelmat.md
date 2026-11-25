# Todennäköisyyspohjaiset tiivistelmät

Tarkka vastaus vaatii usein muistia, joka kasvaa datan mukana.
Kysymykseen "onko tämä osoite nähty?" vastaaminen vaatii kaikkien
osoitteiden tallentamisen, ja kysymykseen "kuinka monta kertaa tätä
tuotetta on katsottu?" vastaaminen vaatii laskurin jokaiselle
tuotteelle. *Tiivistelmä* (engl. *sketch*, *synopsis*) vastaa
likimääräisesti, ja sen koko riippuu halutusta tarkkuudesta eikä
datan määrästä. Virhe on rajattu ja todennäköisyys tunnettu, joten
vastaus on hyödyllinen, kunhan sovellus sietää sen.

## Bloom-suodatin

*Bloom-suodatin* (Bloom 1970) on $m$ bitin taulukko ja $k$
hajautusfunktiota. Lisäys asettaa avaimen $k$ bittiä ykkösiksi.
Kysely vastaa "ehkä", jos kaikki $k$ bittiä ovat ykkösiä, ja muuten
"ei". Väärä "ei" on mahdoton, koska lisätyn avaimen bitit ovat aina
asetettuja. Väärä "ehkä" syntyy, kun muiden avainten bitit sattuvat
kattamaan kaikki kysytyn avaimen bitit.

```{.cpp tiedosto="esimerkit/12-bloom.cpp" osa="bloom"}
```

$k$ erillistä hajautusfunktiota ei tarvita. Kirschin ja Mitzenmacherin
*kaksoishajautus* $h_1 + i\,h_2$ antaa saman virhetodennäköisyyden
kahdella arvolla. $h_2$ ei saa olla nolla, koska silloin kaikki $k$
paikkaa olisivat samat. Bitin 1 asettaminen varmistaa sen.

## Virhetodennäköisyys

Kun $n$ avainta on lisätty, yksittäinen bitti on yhä nolla
todennäköisyydellä $(1 - 1/m)^{kn} \approx e^{-kn/m}$. Väärän
positiivisen todennäköisyys on likimäärin

$$p \approx \left(1 - e^{-kn/m}\right)^k,$$

ja se on pienin, kun $k = (m/n) \ln 2$. Silloin puolet biteistä on
ykkösiä, ja $p \approx 0{,}6185^{m/n}$. Kymmenen bittiä avainta kohden
antaa noin prosentin virheen riippumatta siitä, ovatko avaimet
kokonaislukuja vai kilotavun mittaisia merkkijonoja. Mittaus lisää
10 000 avainta 100 000 bitin suodattimeen eri $k$:n arvoilla ja
kysyy 100 000 avainta, joita ei lisätty:

```{.tuloste tiedosto="esimerkit/12-bloom.odotettu"}
```

Optimi on $k = 10 \ln 2 \approx 7$. Liian vähillä funktioilla
yksittäinen törmäys riittää vääräksi positiiviseksi. Liian monella
taulukko täyttyy ykkösistä. Vertailutesti tarkistaa vain sen, minkä
suodatin lupaa: jokainen lisätty avain löytyy. Väärien positiivisten
osuutta verrataan kaavaan.

Bloom-suodatin säästää kalliita hakuja. LevelDB, RocksDB ja Cassandra
pitävät jokaisen levytiedoston avaimista suodatinta muistissa ja
lukevat tiedoston vain, kun vastaus on "ehkä". Selaimet ja
välityspalvelimet tarkistavat sen avulla haitallisten osoitteiden
listaa. Perusversio ei tue poistoa, koska bitin nollaaminen voisi
poistaa toisenkin avaimen. *Laskuri-Bloom* korvaa bitit pienillä
laskureilla, ja *käkisuodatin* (engl. *cuckoo filter*) tallentaa
avainten sormenjäljet ja tukee poistoa.

## Count-Min-luonnos

*Count-Min* (Cormode ja Muthukrishnan 2005) arvioi esiintymiä
tietovirrassa. Se koostuu $d$ rivistä, joilla kullakin on $w$ laskuria
ja oma hajautusfunktio. Lisäys kasvattaa jokaisen rivin yhtä laskuria.
Arvio on rivien pienin laskuri. Törmäykset voivat vain kasvattaa
laskuria, joten arvio on aina vähintään todellinen määrä. Kun
$w = \lceil e / \varepsilon \rceil$ ja $d = \lceil \ln(1/\delta)
\rceil$, arvio ylittää todellisen määrän enintään $\varepsilon N$:llä
todennäköisyydellä vähintään $1 - \delta$. Tässä $N$ on virran pituus.

```{.cpp tiedosto="esimerkit/12-luonnos.cpp" osa="countmin"}
```

Testivirta noudattaa *Zipfin jakaumaa*. Tuotteen $r$ osuus on
verrannollinen lukuun $1/r$, kuten sanojen esiintymissä, verkkosivujen
katseluissa ja tiedostojen suosiossa. Virrassa on 200 000
katselua 100 000 tuotteesta. Luonnoksen parametrit ovat
$\varepsilon = 0{,}002$ ja $\delta = 0{,}01$, ja tarkat laskurit
lasketaan rinnalla mallina.

Luonnos käyttää 6800 laskuria satatuhannelle tuotteelle:

```{.tuloste tiedosto="esimerkit/12-luonnos.odotettu" asti="tuote 10000"}
```

Yksikään arvio ei ylitä rajaa $\varepsilon N = 400$, eikä yksikään ole
liian pieni. Suosituimpien tuotteiden arviot
ovat lähes tarkkoja. Harvinaisten tuotteiden arvioissa virhe on
suuri suhteessa todelliseen määrään, koska virhe riippuu virran
pituudesta eikä tuotteen omasta määrästä. Count-Min sopii siis
*suosituimpien* tunnistamiseen (engl. *heavy hitters*), kuten
verkkoliikenteen suurimpien lähettäjien tai trendaavien hakusanojen
etsimiseen.

## Säiliöotanta

Virrasta halutaan $k$ alkion tasainen satunnaisotos, mutta virran
pituutta ei tiedetä etukäteen, eikä sitä voi tallentaa.
*Säiliöotanta* (engl. *reservoir sampling*, Vitterin algoritmi R)
pitää $k$ alkion säiliötä. Alkio $i$ (0-pohjainen, $i \ge k$) korvaa
satunnaisen säiliön alkion todennäköisyydellä $k/(i+1)$. Induktiolla
jokainen $i + 1$:stä nähdystä alkiosta on säiliössä todennäköisyydellä
$k/(i+1)$:

```{.cpp tiedosto="esimerkit/12-luonnos.cpp" osa="sailio"}
```

Tasaisuus testataan tilastollisesti. Jokaisen 20 alkiosta pitäisi
esiintyä odotusarvoisesti 6000 otoksessa 30 000:sta. *Khii toiseen
-testi* (taito *Todennäköisyys*) vertaa havaittuja määriä odotettuihin:

```{.tuloste tiedosto="esimerkit/12-luonnos.odotettu" alkaen="otanta"}
```

Testisuure $9{,}8$ on selvästi alle 95 prosentin rajan $30{,}1$, joten
tasaisuudesta ei ole näyttöä. Tilastollinen testi on aina
todennäköisyyskysymys: kiinteällä siemenellä tulos on toistettava,
mutta uusi siemen voi joskus ylittää rajan, vaikka algoritmi on oikein.

## Muita tiivistelmiä

| Tiivistelmä | Kysymys | Muisti | Virhe |
|--------------|----------------|-------------------|-------------------|
| Bloom-suodatin | kuuluuko joukkoon | $1{,}44\,n \log_2(1/p)$ bittiä | vääriä positiivisia $p$ |
| Count-Min | montako kertaa | $O(\varepsilon^{-1} \log \delta^{-1})$ | yliarvio $\le \varepsilon N$ |
| HyperLogLog | montako eri alkiota | $O(\varepsilon^{-2})$ laskuria | suhteellinen $\approx 1{,}04/\sqrt{m}$ |
| t-digest, KLL | persentiilit | $O(\varepsilon^{-1})$ | järjestysvirhe $\le \varepsilon N$ |
| säiliöotanta | tasainen otos | $k$ alkiota | tarkka jakauma |

*HyperLogLog* (Flajolet ym. 2007) laskee erilaisten alkioiden määrän
muutamalla kilotavulla miljardeista alkioista. Se tarkkailee, kuinka
monta nollabittiä hajautusarvojen alussa on enimmillään. Redis ja
monet tietokannat tarjoavat sen valmiina (`PFCOUNT`,
`approx_count_distinct`).

## Käytännössä

- Päätä ensin, millaisen virheen sovellus sietää. Bloom-suodattimen
  väärä positiivinen maksaa ylimääräisen haun, mutta väärä negatiivinen
  voisi olla turvallisuusvirhe. Siksi suodatin on oikein päin vain, jos
  "ei" on varma vastaus.
- Mitoita suodatin odotetun avainmäärän mukaan. Ylitäyttö kasvattaa
  virheen nopeasti, eikä suodatinta voi kasvattaa jälkikäteen ilman
  avaimia.
- Käytä hyviä hajautusfunktioita. Tiivistelmien virherajat olettavat,
  että funktiot käyttäytyvät kuin satunnaiset. Huono funktio, kuten
  pelkkä jakojäännös, rikkoo ne säännöllisellä datalla.
- Tiivistelmät voi yhdistää. Kahden saman kokoisen Bloom-suodattimen
  bittitason TAI ja kahden Count-Min-luonnoksen laskurien summa ovat
  yhdistetyn datan tiivistelmiä, mikä sopii hajautettuun laskentaan.
- Testaa tiivistelmät niiden lupausten mukaan: varmat ominaisuudet
  `vaadi()`-tarkistuksilla ja todennäköisyysrajat mittauksella
  kiinteällä siemenellä.

## Itsearviointi

- Osaat toteuttaa Bloom-suodattimen kaksoishajautuksella ja johtaa sen
  väärien positiivisten todennäköisyyden.
- Osaat mitoittaa Bloom-suodattimen bittimäärän ja funktioiden määrän
  halutun virheen mukaan.
- Osaat toteuttaa Count-Min-luonnoksen ja selittää, miksi arvio ei ole
  koskaan liian pieni ja miten leveys ja syvyys määräytyvät.
- Osaat toteuttaa säiliöotannan ja todistaa induktiolla, että otos on
  tasainen.
- Osaat valita tiivistelmän kysymyksen ja sallitun virheen mukaan ja
  testata sen varmat ja todennäköisyyspohjaiset lupaukset erikseen.

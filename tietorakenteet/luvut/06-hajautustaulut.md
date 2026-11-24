# Hajautustaulut

Johdannon laskuritaulukko löysi tunnuksen yhdellä taulukon luvulla,
koska tunnus itse kelpasi indeksiksi. Hajautustaulu (engl. hash table)
yleistää idean mihin tahansa avaimeen: *hajautusfunktio* muuntaa
avaimen kokonaisluvuksi, ja luku pienennetään taulukon indeksiksi.
Hyvällä funktiolla avaimet jakautuvat tasaisesti, ja lisäys, haku ja
poisto ovat odotusarvoisesti vakioaikaisia. Hajautustaulu on
joukkojen ja sanakirjojen (avain–arvo-parien) oletustoteutus lähes
kaikissa kielissä.

Kaksi avainta voi tuottaa saman indeksin, joten jokaisen
hajautustaulun on käsiteltävä *törmäykset*. Tässä luvussa törmäykset
ratkaistaan *ketjuttamalla*: taulukon jokainen paikka (*ämpäri*) on
linkitetty lista avaimista, jotka osuvat siihen. Luku 7 esittelee
vaihtoehdon, avoimen osoitteistuksen.

## Hajautusfunktio

Hajautusfunktiolta vaaditaan kahta asiaa. Sen on oltava
*deterministinen* – sama avain antaa aina saman arvon – ja sen on
*sekoitettava* hyvin: pieni muutos avaimessa muuttaa arvoa paljon, ja
tavalliset avainjoukot (peräkkäiset numerot, yhteiset etuliitteet)
jakautuvat tasaisesti. Vertailussa on kaksi funktiota:

```{.c tiedosto="esimerkit/06-hajautus.c" osa="funktiot"}
```

FNV-1a käsittelee tavun kerrallaan: tavu yhdistetään tilaan
XOR-operaatiolla ja tila kerrotaan alkuluvulla. Kertolasku levittää
jokaisen tavun vaikutuksen tilan ylempiin bitteihin. Tavujen summa
taas jättää huomiotta järjestyksen (`ab` ja `ba` törmäävät), eikä
lyhyiden avainten summa koskaan kasva suureksi.

Mittaus vie 10 000 käyttäjätunnusta (`kayttaja0`, `kayttaja1`, …)
1024 ämpäriin ja laskee, montako vertailua onnistunut haku keskimäärin
vaatii. Ketjussa, jonka pituus on $m$, avaimien hakuun tarvitaan
yhteensä $1 + 2 + \dots + m = m(m + 1)/2$ vertailua:

```{.c tiedosto="esimerkit/06-hajautus.c" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/06-hajautus.odotettu"}
```

Summafunktiolla 933 ämpäriä 1024:stä jää tyhjiksi, koska summat
osuvat kapealle välille, ja pisin ketju on 615 avainta. Haku on
33 kertaa hitaampi kuin FNV-1a:lla, joka on lähes teoreettisen
tasaisen jakauman tasolla: kun kuormituskerroin on $\alpha$,
onnistunut haku vaatii keskimäärin noin $1 + \alpha/2$ vertailua.

### Hajautusarvosta indeksiksi

Hajautusarvo pienennetään taulukon kokoon jakojäännöksellä. Jos koko
on kahden potenssi, jakojäännös on bittimaski `h & (K - 1)`, joka
käyttää vain arvon *alimpia* bittejä. Se toimii FNV-1a:n kanssa, mutta
heikko funktio, jonka alimmat bitit vaihtelevat huonosti
(esimerkiksi osoitin, joka on aina jaollinen 16:lla), kasaa kaikki
avaimet harvoihin ämpäreihin. Silloin arvo kannattaa ensin sekoittaa
kertomalla se suurella parittomalla vakiolla ja ottamalla *ylimmät*
bitit. Tätä *Fibonacci-hajautusta* käytetään luvussa 7.

### Vihamieliset avaimet

Jos hyökkääjä voi valita avaimet – esimerkiksi HTTP-pyynnön
parametrien nimet – ja hajautusfunktio tunnetaan, hän voi laskea
tuhansia avaimia, jotka osuvat samaan ämpäriin, ja tehdä jokaisesta
hausta lineaarisen. Tähän perustuvat palvelunestohyökkäykset
pakottivat monet kielet vaihtamaan hajautusfunktionsa avaimelliseen,
satunnaisesti alustettuun funktioon (esimerkiksi SipHash). FNV-1a on
hyvä tavallisille avaimille, ei vihamielisille.

## Ketjutettu hajautustaulu

Esimerkki laskee sanojen esiintymiä. Rajapinnassa avain on
merkkijono ja arvo laskuri, ja kartta kopioi avaimen itselleen:

```{.dot otsikko="Ketjutettu hajautustaulu: lokero osoittaa saman lokeron alkioiden listaan"}
digraph {
  rankdir=LR; nodesep=0.15; ranksep=0.4;
  node [fontsize=9];
  taulu [shape=record, label="<0>0|<1>1|<2>2|<3>3|<4>4|<5>5|<6>6|<7>7"];
  a [label="\"ja\" 41"]; b [label="\"on\" 17"]; c [label="\"kissa\" 2"];
  d [label="\"se\" 23"];
  taulu:1 -> a -> b; taulu:4 -> c; taulu:6 -> d;
}
```

```{.c tiedosto="esimerkit/06-sanat/kartta.h"}
```

Jokainen alkio tallentaa hajautusarvonsa. Avain on alkion lopussa
*joustavana taulukkojäsenenä* (engl. flexible array member), joten
alkio ja avain varataan yhdellä `malloc`-kutsulla:

```{.c tiedosto="esimerkit/06-sanat/kartta.c" osa="rakenne"}
```

Tallennettu hajautusarvo maksaa neljä tavua alkiota kohti, mutta
säästää kahdesti. Haussa merkkijonot verrataan vain, jos
hajautusarvot ovat samat, ja useimmat erilaiset avaimet karsiutuvat
yhdellä kokonaislukuvertailulla. Uudelleenhajautuksessa arvoa ei
tarvitse laskea uudelleen.

### Kuormituskerroin ja uudelleenhajautus

Kuormituskerroin $\alpha$ on avainten määrä jaettuna ämpäreiden
määrällä. Ketjun keskipituus on $\alpha$, joten haun hinta kasvaa
lineaarisesti kertoimen mukana. Vakioajan säilyttämiseksi taulua on
kasvatettava, kun kerroin ylittää rajan – ketjutuksessa tavallisesti
1. Kasvatus on sama idea kuin vektorissa: ämpäreiden määrä tuplataan,
joten jokainen avain siirretään tasoitetusti vakiomäärän kertoja.

Siirrossa alkioita ei kopioida. Jokainen alkio irrotetaan vanhasta
ketjusta ja liitetään uuteen sen tallennetun hajautusarvon mukaan:

```{.c tiedosto="esimerkit/06-sanat/kartta.c" osa="uudelleen"}
```

Lisäys etsii ensin avainta. Jos sitä ei ole, taulu kasvatetaan
tarvittaessa ja uusi alkio lisätään ketjun alkuun:

```{.c tiedosto="esimerkit/06-sanat/kartta.c" osa="kasvata"}
```

Pääohjelma pilkkoo syötteen sanoiksi, laskee ne kartalla ja lajittelee
lopuksi parit esiintymien mukaan:

```{.c tiedosto="esimerkit/06-sanat/main.c" osa="paa"}
```

Syöte on lyhyt kappale tekstiä:

```{.tuloste tiedosto="esimerkit/06-sanat.syote"}
```

```{.tuloste tiedosto="esimerkit/06-sanat.odotettu"}
```

Työnjako on tyypillinen: hajautustaulu tekee laskemisesta
vakioaikaista, mutta sen järjestys on määrittelemätön, joten
järjestetty tuloste vaatii erillisen lajittelun. Kahdeksasta
ämpäristä alkanut taulu kasvoi kolmesti 64 ämpäriin.

### Poisto ketjusta

Ketjutetusta taulusta poistaminen on linkitetyn listan poisto
(luku 4): etsitään linkki, joka johtaa poistettavaan alkioon, ja
ohjataan se seuraavaan. Osoitin osoittimeen -tekniikka toimii
sellaisenaan, koska ämpäri on listan alkuosoitin.

## Mitä hajautustaulu ei tee

| Kysymys | Hajautustaulu | Hakupuu (luku 8) | Lajiteltu taulukko |
|---------|---------------|------------------|--------------------|
| Onko avain mukana? | odotusarvo $O(1)$ | $O(\log n)$* | $O(\log n)$ |
| Lisäys ja poisto | odotusarvo $O(1)$ | $O(\log n)$* | $O(n)$ |
| Avaimet järjestyksessä | lajittelu $O(n \log n)$ | $O(n)$ | $O(n)$ |
| Pienin, suurin, edeltäjä | $O(n)$ | $O(\log n)$* | $O(1)$ tai $O(\log n)$ |
| Välikysely $[a, b]$ | $O(n)$ | $O(\log n + k)$* | $O(\log n + k)$ |

\* tasapainotetussa puussa

Hajautustaulu vastaa vain kysymykseen "onko tämä avain mukana?".
Jos tarvitaan järjestystä, lähimpiä arvoja tai välejä, oikea rakenne on
puu tai lajiteltu taulukko. Lisäksi yksittäinen operaatio voi olla
hidas: uudelleenhajautus kopioi koko taulun linkit, ja huonolla tuurilla
tai vihamielisillä avaimilla ketju voi kasvaa pitkäksi.

## Käytännössä

- **Valmis, testattu hajautusfunktio.** FNV-1a lyhyille avaimille,
  avaimellinen funktio (SipHash) ulkoa tuleville avaimille. Älä keksi
  omaa.
- **Tallenna hajautusarvo** alkioon, jos avaimen vertailu on kallis tai
  taulu kasvaa usein.
- **Kasvata kuormituskertoimen mukaan.** Ketjutuksessa raja on noin 1,
  ja ämpäreiden määrä tuplataan.
- **Kahden potenssin koko ja bittimaski,** jos funktion alimmat bitit
  sekoittuvat hyvin; muuten sekoita ennen maskia.
- **Mittaa jakauma.** Tyhjät ämpärit ja pisin ketju paljastavat huonon
  funktion heti; keskimääräinen hakuaika ei aina paljasta.

## Itsearviointi

- Osaat selittää, mitä hajautusfunktiolta vaaditaan, ja näyttää
  mittauksella, miksi tavujen summa on huono funktio.
- Osaat toteuttaa ketjutetun hajautustaulun, joka kasvaa
  kuormituskertoimen mukaan.
- Osaat kertoa, miksi tallennettu hajautusarvo nopeuttaa hakua ja
  uudelleenhajautusta.
- Osaat valita hajautustaulun ja hakupuun välillä sen perusteella,
  mitä kyselyjä datalle tehdään.

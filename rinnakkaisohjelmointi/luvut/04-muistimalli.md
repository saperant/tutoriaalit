# Muistimalli

Yksisäikeinen ohjelma näyttää suorittuvan lause kerrallaan
kirjoitusjärjestyksessä. Todellisuudessa kääntäjä ja suoritin järjestävät
muistioperaatioita uudelleen koko ajan: kääntäjä pitää arvoja
rekistereissä ja siirtää latauksia silmukan ulkopuolelle, ja suoritin
puskuroi kirjoituksia ja suorittaa käskyjä epäjärjestyksessä. Yksi säie ei
huomaa tätä, koska sen omat havainnot pysyvät johdonmukaisina. Toinen säie
voi kuitenkin nähdä kirjoitukset eri järjestyksessä tai ei ollenkaan.

**Muistimalli** on kielen sopimus siitä, mitä säie saa nähdä toisen
säikeen kirjoituksista. C++11 määritteli sen ensimmäistä kertaa
(Boehm ja Adve 2008). Ennen sitä säikeistetyn C++-ohjelman merkitys
riippui kääntäjästä ja suorittimesta.

## Datakilpailu on määrittelemätöntä käyttäytymistä

Kaksi muistioperaatiota on **ristiriidassa** (*conflict*), jos ne
käsittelevät samaa muistipaikkaa ja ainakin toinen kirjoittaa.
**Datakilpailu** (*data race*) syntyy, kun kaksi ristiriitaista
operaatiota eri säikeistä ei ole tapahtumisjärjestyksessä (seuraava
kohta) ja ainakin toinen niistä ei ole atominen. Datakilpailu on
määrittelemätöntä käyttäytymistä samoin kuin taulukon yli kirjoittaminen.

Tämä on vahvempi väite kuin "tulos voi olla väärä". Kääntäjä saa olettaa,
ettei datakilpailuja ole, ja optimoida sen mukaan. Esimerkiksi silmukka
`while (!valmis) {}` tavallisella `bool`-muuttujalla saa kääntyä
ikuiseksi silmukaksi, koska muuttuja ei kääntäjän mielestä voi muuttua
silmukan aikana. Sama pätee 64-bittisen arvon kirjoitukseen 32-bittisellä
suorittimella: toinen säie voi nähdä puolet uudesta ja puolet vanhasta
arvosta (*torn write*).

Ohjelma, jossa ei ole datakilpailuja, käyttäytyy kuin säikeiden
operaatiot lomittuisivat jossain järjestyksessä, kun atomiset operaatiot
käyttävät oletusjärjestystä `seq_cst`. Tätä takuuta kutsutaan nimellä
*SC for DRF* (*sequential consistency for data-race-free programs*), ja se
on muistimallin tärkein yksittäinen tulos. Heikompia järjestyksiä
käyttävä ohjelma ei saa tätä takuuta, ja sen oikeellisuus on perusteltava
tarkemmin.

## Tapahtumisjärjestys

Muistimalli määrittelee operaatioiden välille suhteita:

- **Peräkkäisyys** (*sequenced-before*): saman säikeen operaatiot ovat
  lähdekoodin järjestyksessä, kuten yksisäikeisessä ohjelmassa.
- **Synkronointi** (*synchronizes-with*): kun säie lukee acquire-lukemisella
  arvon, jonka toinen säie kirjoitti release-kirjoituksella, kirjoitus
  synkronoituu lukemisen kanssa. Lukon vapautus synkronoituu saman lukon
  seuraavan oton kanssa, säikeen luonti säikeen alun kanssa ja säikeen
  loppu `join`in paluun kanssa.
- **Tapahtumisjärjestys** (*happens-before*) on näiden kahden yhdistelmä
  ketjuina. Jos A tapahtuu ennen B:tä, B näkee A:n kirjoitukset tai
  myöhemmät.

Kirjoitukset, jotka eivät ole tapahtumisjärjestyksessä lukemisen kanssa,
voivat näkyä tai olla näkymättä. Siksi lukolla suojattu data on turvallista:
jokainen lukon otto näkee kaikki aiemmat vapautukset ja siten kaikki
niitä edeltäneet kirjoitukset. Johdannon summaesimerkki toimi samasta
syystä: säikeen loppu synkronoituu `join`in kanssa.

## Julkaisu release/acquire-parilla

Yleisin lukoton malli on **julkaisu**: säie valmistelee datan tavallisilla
kirjoituksilla ja julkaisee sen yhdellä atomisella kirjoituksella:

```{.cpp tiedosto="esimerkit/04-julkaisu.cpp" osa="julkaisu"}
```

```{.tuloste tiedosto="esimerkit/04-julkaisu.odotettu"}
```

Kun lukija näkee lipun arvon `true` acquire-lukemisella, (2) synkronoituu
(3):n kanssa. Koska (1) on ennen (2):ta samassa säikeessä, (1) tapahtuu
ennen lukijan datan lukemista. Kaaviossa tapahtumisjärjestys on nuolten
muodostama polku: vasemmalla polku kulkee kirjoituksesta (1) lukuun
asti, oikealla se katkeaa säikeiden välillä.

```{.dot otsikko="Julkaisun tapahtumisjärjestys. Ohut nuoli on peräkkäisyys säikeen sisällä, paksu nuoli synkronointi säikeiden välillä. Relaxed-järjestyksellä synkronointia ei synny, joten kirjoitus ja luku ovat datakilpailussa."}
digraph {
  node [shape=box]; ranksep=0.4;
  subgraph cluster_a { label="release ja acquire"; color=gray60;
    subgraph cluster_a1 { label="julkaisija"; color=gray80;
      a1 [label="(1) asetukset = …"];
      a2 [label="(2) valmis.store(true,\nrelease)"]; a1 -> a2; }
    subgraph cluster_a2 { label="lukija"; color=gray80;
      a3 [label="(3) valmis.load(acquire)\n== true"];
      a4 [label="lue asetukset"]; a3 -> a4; }
    a2 -> a3 [label="  synkronoituu", penwidth=2];
  }
  subgraph cluster_b { label="relaxed"; color=gray60;
    subgraph cluster_b1 { label="julkaisija"; color=gray80;
      b1 [label="(1) asetukset = …"];
      b2 [label="(2) valmis.store(true,\nrelaxed)"]; b1 -> b2; }
    subgraph cluster_b2 { label="lukija"; color=gray80;
      b3 [label="(3) valmis.load(relaxed)\n== true"];
      b4 [label="lue asetukset"]; b3 -> b4; }
    b2 -> b3 [style=invis]; b1 -> b4 [label="ei järjestystä:\ndatakilpailu", style=dashed, dir=none, constraint=false];
  }
}
```
 Release estää aiempia operaatioita
siirtymästä release-kirjoituksen ohi myöhemmiksi, ja acquire estää
myöhempiä operaatioita siirtymästä acquire-lukemisen ohi aiemmiksi.
Ilman niitä datakilpailu syntyy, ja luku *ThreadSanitizer ja virheiden
etsintä* näyttää, miten työkalu sen raportoi.

## Muistijärjestykset

Jokaiselle atomiselle operaatiolle voi antaa järjestyksen:

| Järjestys | Takuu | Tyypillinen käyttö |
|-------|-----------------------|--------------------|
| `relaxed` | Vain atomisuus ja yhden muuttujan muutosjärjestys | Laskurit, tilastot |
| `release` | Kirjoitus: aiemmat operaatiot eivät siirry sen ohi | Julkaisu, lukon vapautus |
| `acquire` | Luku: myöhemmät operaatiot eivät siirry sen ohi | Julkaistun datan luku, lukon otto |
| `acq_rel` | Luku–kirjoitus-operaatio, molemmat | `compare_exchange`, `fetch_add` välitettynä |
| `seq_cst` | Lisäksi yksi kaikkien `seq_cst`-operaatioiden kokonaisjärjestys | Oletus |
| `consume` | Riippuvuusjärjestys (ei käytännössä toteutettu) | Ei käytetä; kääntäjät tekevät siitä `acquire`n |

Jokaisella atomisella muuttujalla on yksi **muutosjärjestys**
(*modification order*), jonka kaikki säikeet näkevät samana: kun säie
on nähnyt arvon, se ei myöhemmin näe saman muuttujan vanhempaa arvoa
(koherenssi). Tämä pätee myös `relaxed`-operaatioille. Eri muuttujien
välillä järjestystä ei sen sijaan ole ilman synkronointia.

## Litmus-testit

Muistimallien käytöstä tutkitaan **litmus-testeillä**: pienillä
kahden säikeen ohjelmilla, joista luetellaan sallitut lopputulokset.
Seuraava ajuri ajaa testin enintään 20 000 kertaa, kuitenkin enintään
kaksi sekuntia. Este pitää säikeet tahdissa, ja sen valmistumisfunktio
kirjaa kierroksen tuloksen ja päättää, jatketaanko:

```{.cpp tiedosto="esimerkit/04-litmus.cpp" osa="ajuri"}
```

Ajurin ensimmäisessä versiossa säikeet olivat samassa lohkossa kuin
`return maarat;`. GCC:llä käännettynä taulukko kopioitiin paluuarvoksi
ennen kuin säikeiden hajottimet odottivat ne loppuun, joten tulos oli
tyhjä ja ThreadSanitizer raportoi kilpailun. Clangilla virhe ei näkynyt,
koska se rakensi `maarat`in suoraan paluuarvon paikalle. Sama koodi siis
toimi toisella kääntäjällä sattumalta; muistimallin kannalta se oli
virheellinen molemmilla.

**Store buffering** (SB): kumpikin säie kirjoittaa omaan muuttujaansa ja
lukee toisen. Voivatko molemmat lukea nollan?

```{.cpp tiedosto="esimerkit/04-litmus.cpp" osa="sb"}
```

**Message passing** (MP): toinen säie kirjoittaa datan ja lipun, toinen
lukee lipun ja datan. Voiko lukija nähdä lipun mutta vanhan datan?

```{.cpp tiedosto="esimerkit/04-litmus.cpp" osa="mp"}
```

```{.tuloste tiedosto="esimerkit/04-litmus.odotettu"}
```

Ohjelma tarkistaa vain, että havaitut tulokset ovat sallittuja; kuinka
usein kukin tulos esiintyy, riippuu koneesta ja kuormasta, ja määrät
tulostetaan virhetulosteeseen. Tulokset tulkitaan näin:

- **SB (0,0)** on sallittu `relaxed`- ja release/acquire-järjestyksillä,
  koska kumpikaan ei estä kirjoitusta ja *myöhemmän* muuttujan lukemista
  vaihtamasta paikkaa. x86-suorittimet tekevät näin oikeasti:
  kirjoitus jää suorittimen kirjoituspuskuriin (*store buffer*), ja luku
  ohittaa sen. Vain `seq_cst` kieltää tuloksen. x86:lla se maksaa
  kirjoituksen yhteydessä täyden muistiaidan (`mfence` tai `xchg`).
- **MP (1,0)** on sallittu `relaxed`illa mutta kielletty
  release/acquire-parilla. x86 ei koskaan tuota sitä, koska sen
  muistimalli (x86-TSO) säilyttää kirjoitusten ja lukujen keskinäisen
  järjestyksen. ARM ja POWER tuottavat sen, joten `relaxed`-julkaisu, joka
  "toimii" x86:lla, rikkoutuu ARM-palvelimella tai puhelimessa.

Kirjoittajan koneella SB (0,0) ei näkynyt kertaakaan 20 000
kierroksessa, koska esteeltä heräävät säikeet eivät
käynnisty riittävän tarkasti yhtä aikaa. Erikoistyökalut kuten `litmus7` ajavat testejä
tiukemmin tahdistettuna ja löytävät tuloksen helposti. Havainto on
tärkeä: *se, ettei virhettä näy, ei todista sen puuttumista*. Muistimallin
sallima tulos voi ilmetä vasta toisella suorittimella tai kuormalla.

## Laitteisto ja hinta

| Operaatio | x86-64 | ARMv8 (AArch64) |
|-----------------|---------------|------------------|
| `relaxed`-luku ja -kirjoitus | tavallinen `mov` | tavallinen `ldr`/`str` |
| `acquire`-luku | tavallinen `mov` | `ldar` (tai `ldapr`) |
| `release`-kirjoitus | tavallinen `mov` | `stlr` |
| `seq_cst`-kirjoitus | `xchg` (sisältää aidan) | `stlr` |
| `fetch_add` ym. | `lock xadd` (aina täysi aita) | `ldadd`-perhe (LSE) tai LL/SC-silmukka |

x86:lla acquire ja release ovat siis suorittimelle ilmaisia; ne rajoittavat
vain kääntäjää. Siksi heikoista järjestyksistä saatava hyöty näkyy
lähinnä ARM- ja POWER-koneilla, ja virheet niissä vain siellä. Taulukko
on yksinkertaistettu: tarkka kuvaus on mm. Sewellin ja muiden
x86-TSO-artikkelissa ja ARMin arkkitehtuurikäsikirjassa.

`std::atomic_thread_fence` on erillinen muistiaita, joka yhdessä
`relaxed`-operaatioiden kanssa voi korvata release/acquire-parin. Aitoja
tarvitaan harvoin, ja ThreadSanitizer ei mallinna niitä (GCC varoittaa
`-Wtsan`). Operaatiokohtainen järjestys on selkeämpi.

## Käytännössä

- **Oletus on `seq_cst`.** Ohjelma, jossa ei ole datakilpailuja ja jonka
  atomiset operaatiot ovat `seq_cst`, käyttäytyy kuin lomitettu
  yksisäikeinen ohjelma. Heikommat järjestykset ovat optimointi, joka
  perustellaan ja mitataan.
- **`relaxed` vain riippumattomille arvoille.** Laskuri, jonka arvoa
  ei käytetä muun datan luvan antajana, on turvallinen. Lippu, joka
  julkaisee dataa, ei ole.
- **Release ja acquire tulevat parina.** Julkaisija kirjoittaa
  releasella, lukija lukee acquirella *saman muuttujan*. Eri muuttujat
  eivät synkronoidu.
- **Testaa ARMilla.** x86 piilottaa monet järjestysvirheet. CI:hin
  kannattaa lisätä AArch64-kone, jos ohjelma käyttää heikkoja järjestyksiä.
- **`volatile` ei ole atominen.** Se estää kääntäjää poistamasta
  operaatioita mutta ei takaa atomisuutta eikä järjestystä säikeiden
  välillä. Sitä käytetään muistiin kuvattuihin laitteisiin, ei
  säikeisiin.

## Itsearviointi

- Osaat määritellä datakilpailun ja kertoa, miksi se on määrittelemätöntä
  käyttäytymistä eikä vain väärä tulos.
- Osaat perustella tapahtumisjärjestyksen avulla, miksi
  release/acquire-julkaisu tai lukko tekee datan näkyväksi toiselle säikeelle.
- Osaat kertoa store buffering- ja message passing -testien sallitut
  tulokset eri muistijärjestyksillä ja sen, mitä x86 ja ARM niistä
  tuottavat.
- Osaat valita laskurille, julkaisulle ja lukolle sopivan
  muistijärjestyksen.

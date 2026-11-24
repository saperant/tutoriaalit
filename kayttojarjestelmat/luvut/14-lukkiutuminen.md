# Lukkiutuminen

Lukkiutumassa (engl. deadlock) joukko säikeitä odottaa toisiaan
niin, ettei kukaan voi edetä. Yksinkertaisin esimerkki on kaksi
säiettä ja kaksi lukkoa: ensimmäinen pitää lukkoa A ja odottaa B:tä,
toinen pitää B:tä ja odottaa A:ta. Ohjelma ei kaadu eikä tulosta
virhettä – se vain pysähtyy, usein harvoin ja vain kuormassa.

## Coffmanin ehdot

Coffman, Elphick ja Shoshani osoittivat 1971, että lukkiutuma voi
syntyä vain, jos neljä ehtoa ovat voimassa yhtä aikaa:

1. **Poissulkeminen:** resurssia voi käyttää vain yksi kerrallaan.
2. **Pito ja odotus:** säie pitää resurssia ja odottaa toista.
3. **Ei pakkoriistoa:** resurssia ei voi ottaa pois sen haltijalta.
4. **Kehäodotus:** on kehä säikeitä, joista kukin odottaa seuraavan
   pitämää resurssia.

Jokainen torjuntakeino rikkoo yhden ehdoista. Poissulkemisesta ei
yleensä voi luopua, mutta muut kolme ovat ohjelmoijan vallassa:

| Rikottava ehto | Keino |
|------------------|------------------------------------------------------|
| pito ja odotus | varaa kaikki kerralla tai ei mitään (`trylock` ja perääntyminen) |
| ei pakkoriistoa | aikaraja ja vapautus (`timedlock`), transaktion peruutus |
| kehäodotus | kiinteä lukkojärjestys |

## Lukkiutuma käytännössä

Esimerkki rakentaa lukkiutuman varmasti. Este pitää huolen, että
kumpikin säie ehtii ottaa ensimmäisen lukkonsa ennen kuin kumpikaan
yrittää toista. Aikarajallinen `pthread_mutex_timedlock` tekee
lukkiutumasta näkyvän virheen eikä jumia:

```{.c tiedosto="esimerkit/14-ristikkain.c" osa="ristikkain"}
```

Lukkiutuman erikoistapaus on säie, joka lukitsee saman tavallisen
mutexin kahdesti: se odottaa itseään. Virheitä tarkistava mutex
(`PTHREAD_MUTEX_ERRORCHECK`) palauttaa silloin `EDEADLK` ja
vapautettaessa ilman lukitusta `EPERM`, kuten esimerkin lopussa:

```{.tuloste tiedosto="esimerkit/14-ristikkain.odotettu"}
```

## Lukkojärjestys

Kehäodotus syntyy vain, jos säikeet lukitsevat samoja lukkoja eri
järjestyksessä. Jos kaikki lukot järjestetään ja jokainen säie lukitsee
ne aina nousevassa järjestyksessä, kehää ei voi syntyä: kehän
"suurimman" lukon haltijan pitäisi odottaa pienempää, mitä sääntö
kieltää. Tilisiirto lukitsee kaksi tiliä, ja järjestys tulee tilin
numerosta eikä siitä, kumpi on lähde:

```{.c tiedosto="esimerkit/14-jarjestys.c" osa="siirto"}
```

```{.tuloste tiedosto="esimerkit/14-jarjestys.odotettu"}
```

Neljä säiettä tekee 80 000 satunnaista siirtoa, eikä mikään
lukkiudu. ThreadSanitizer varoittaa *lock-order-inversion*-virheestä
heti, kun sama lukkopari on lukittu kerrankin eri järjestyksissä,
vaikka lukkiutuma ei olisi toteutunut (ytimessä `lockdep`).

Järjestys voi tulla myös tyypistä tai osoitteesta. Ongelmallisimpia
ovat takaisinkutsut lukon sisältä: kirjasto ei tiedä, mitä lukkoja
kutsuttu funktio ottaa.

## Havaitseminen: odotusgraafi

Järjestelmä voi myös antaa lukkiutumien syntyä ja purkaa ne
jälkikäteen. Tietokannat tekevät näin: transaktio, joka jää
lukkiutumaan, peruutetaan ja aloitetaan uudelleen. Havaitseminen
perustuu *resurssien varausgraafiin*. Kun kutakin resurssia on yksi,
graafi yksinkertaistuu odotusgraafiksi: kaari $P_i \to P_j$
tarkoittaa, että $P_i$ odottaa resurssia, jota $P_j$ pitää. Lukkiutuma
on graafin sykli, ja sen löytää syvyyshaulla, joka merkitsee
nykyisellä polulla olevat solmut:

```{.c tiedosto="esimerkit/14-pankkiiri.c" osa="sykli"}
```

Esimerkki tarkistaa kaksi graafia: ketjun P0 → P1 → P2 → P3 ja
kehän P0 → P1 → P2 → P0. Tuloste on luvun lopussa.

```{.dot otsikko="Odotusgraafit: ketju ei lukkiudu, kehä lukkiutuu"}
digraph {
  rankdir=LR;
  node [shape=circle];
  subgraph cluster_ketju { label="ketju"; color="#D9E0E3";
    a0 [label="P0"]; a1 [label="P1"]; a2 [label="P2"]; a3 [label="P3"];
    a0 -> a1 -> a2 -> a3; }
  subgraph cluster_keha { label="kehä = lukkiutuma"; color="#D9E0E3";
    b0 [label="P0"]; b1 [label="P1"]; b2 [label="P2"];
    b0 -> b1 -> b2; b2 -> b0 [color="#B04848", penwidth=1.4]; }
}
```

Kun resurssia on useita kappaleita, sykli on välttämätön mutta ei
riittävä ehto: jokin kehän resursseista voi vapautua kehän ulkopuolelta.
Silloin käytetään pankkiirin turvallisuustarkistusta nykyisillä
pyynnöillä.

## Välttäminen: pankkiirin algoritmi

Dijkstran *pankkiirin algoritmi* ei salli lukkiutumaa lainkaan.
Jokainen prosessi ilmoittaa etukäteen enimmäistarpeensa kustakin
resurssityypistä. Pyyntö myönnetään vain, jos tila pysyy
*turvallisena*: on olemassa järjestys, jossa jokainen prosessi voi
saada enimmäistarpeensa, päättyä ja vapauttaa resurssinsa seuraaville.
Muuten pyytäjä odottaa, vaikka resursseja olisi vapaana:

```{.c tiedosto="esimerkit/14-pankkiiri.c" osa="turvallinen"}
```

Pyyntö käsitellään kokeilemalla: resurssit siirretään pyytäjälle, tila
tarkistetaan, ja jos se ei ole turvallinen, siirto perutaan ja pyytäjä
jää odottamaan.

Esimerkissä on viisi prosessia ja kolme resurssityyppiä (A, B, C),
joita on yhteensä 10, 5 ja 7. Alussa vapaana on (3, 3, 2):

| Prosessi | Varattu | Enimmäistarve | Tarve |
|----------|---------|---------------|-------|
| P0 | 0 1 0 | 7 5 3 | 7 4 3 |
| P1 | 2 0 0 | 3 2 2 | 1 2 2 |
| P2 | 3 0 2 | 9 0 2 | 6 0 0 |
| P3 | 2 1 1 | 2 2 2 | 0 1 1 |
| P4 | 0 0 2 | 4 3 3 | 4 3 1 |

Sitten P1 pyytää (1, 0, 2), P4 (3, 3, 0) ja P0 (0, 2, 0):

```{.tuloste tiedosto="esimerkit/14-pankkiiri.odotettu"}
```

P1:n pyyntö jättää tilan turvalliseksi ja myönnetään. P4:n pyyntöön ei
riitä vapaita resursseja. P0:n pyyntöön riittäisi, mutta sen jälkeen
vapaana olisi (2, 1, 0), eikä kukaan voisi saada enimmäistarvettaan –
tila ei olisi turvallinen, joten P0 odottaa. Turvaton tila ei ole vielä
lukkiutuma, mutta se voi johtaa siihen, jos prosessit todella pyytävät
enimmäistarpeensa.

Yleiskäyttöisissä järjestelmissä enimmäistarpeita ei tiedetä, mutta
sulautetuissa järjestelmissä algoritmi on käyttökelpoinen malli.

## Elolukko ja nääntyminen

*Elolukossa* (engl. livelock) säikeet eivät ole estyneinä vaan
väistävät toisiaan loputtomasti, tyypillisesti `trylock`-perääntymisen
takia ilman satunnaista viivettä. *Nääntymisessä* järjestelmä etenee,
mutta tietty säie ei pääse koskaan vuoroon (luvut 4 ja 13).

## Käytännössä

- **Määrittele lukkojärjestys ja dokumentoi se:** yksi sääntö
  (osoite, tunniste, tyyppi) koko ohjelmalle.
- **Älä kutsu tuntematonta koodia lukon sisältä:** takaisinkutsut ja
  virtuaalifunktiot voivat ottaa lukkoja väärässä järjestyksessä.
- **ERRORCHECK-mutex ja ThreadSanitizer kehityksessä:** ne löytävät
  itsensä lukitsevat säikeet ja lukkojärjestyksen rikkomukset ennen
  kuin lukkiutuma toteutuu.

## Itsearviointi

- Osaat luetella Coffmanin neljä ehtoa ja kertoa, mitä ehtoa kukin
  torjuntakeino rikkoo.
- Osaat estää lukkiutuman kiinteällä lukkojärjestyksellä ja perustella,
  miksi se toimii.
- Osaat etsiä lukkiutuman odotusgraafin syklinä.
- Osaat suorittaa pankkiirin algoritmin turvallisuustarkistuksen ja
  päättää, voiko pyynnön myöntää.
- Osaat erottaa lukkiutuman, elolukon ja nääntymisen.

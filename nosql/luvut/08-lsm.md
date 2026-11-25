# LSM-puut

Relaatiotietokannat tallentavat datan tavallisesti B-puuhun, jota
päivitetään paikallaan (taito *Edistyneet
algoritmit ja tietorakenteet*). Jokainen kirjoitus on
satunnainen kirjoitus levyn sivulle. Cassandra, ScyllaDB, RocksDB,
LevelDB ja monen muun tietokannan tallennuskerros käyttävät sen sijaan
*LSM-puuta* (*log-structured merge tree*), jossa kirjoitukset ovat aina
peräkkäisiä eikä mitään muuteta paikallaan. Se selittää, miksi
Cassandra kirjoittaa nopeasti, miksi poisto on hautakivi ja miksi
taustalla pyörii kompaktointi.

Tässä luvussa rakennetaan pieni LSM-puu Pythonilla. Se jättää pois
rinnakkaisuuden, pakkauksen ja tasot, mutta periaatteet ovat samat.

```{.dot otsikko="LSM-puun rakenne: kirjoitus lokiin ja memtableen, lukeminen uusimmasta vanhimpaan."}
digraph {
  rankdir=LR;
  kirjoitus [shape=plaintext];
  loki [label="loki\n(levy, peräkkäin)"];
  mem [label="memtable\n(muisti, järjestetty)"];
  s3 [label="SSTable 3\n(uusin)"]; s2 [label="SSTable 2"];
  s1 [label="SSTable 1\n(vanhin)"];
  komp [label="kompaktointi", shape=ellipse];
  kirjoitus -> loki; kirjoitus -> mem;
  mem -> s3 [label="täynnä"];
  s1 -> komp; s2 -> komp; s3 -> komp;
}
```

## Kirjoitus

Kirjoitus menee ensin lokiin, jotta se säilyy kaatumisessa, ja sitten
muistissa olevaan *memtableen*. Kun memtable täyttyy, se kirjoitetaan
levylle järjestettynä *SSTable*-tiedostona (*sorted string table*),
jota ei enää muuteta. Poisto on kirjoitus, jonka arvo on hautakivi:

```{.python tiedosto="esimerkit/nosql/lsm.py" osa="kirjoitus"}
```

Levylle kirjoitetaan vain peräkkäin: lokin perään ja kokonaisia uusia
tiedostoja. Tämä on nopeaa sekä pyörivällä levyllä että SSD:llä, ja
kirjoitusnopeus ei riipu datan määrästä.

## Luku

Avaimesta voi olla monta versiota eri tiedostoissa, joten luku etsii
uusimmasta vanhimpaan ja palauttaa ensimmäisen löydön. Hautakivi on
löytö: se kertoo, että avain on poistettu, eikä vanhempia tiedostoja
tarvitse katsoa:

```{.python tiedosto="esimerkit/nosql/lsm.py" osa="luku"}
```

Puuttuvan avaimen haku joutuisi käymään läpi kaikki tiedostot. Siksi
jokaisella SSTablella on *Bloom-suodatin*, joka kertoo muutamalla
tiivisteellä, ettei avainta *varmasti* ole tiedostossa. Väärä
positiivinen on mahdollinen, väärä negatiivinen ei:

```{.python tiedosto="esimerkit/nosql/lsm.py" osa="bloom"}
```

Kymmenen bittiä avainta kohden ja seitsemän tiivistettä antavat noin
yhden prosentin väärien positiivisten osuuden. Paketin testi
tarkistaa sen 10 000 puuttuvalla avaimella.

## Kompaktointi

Tiedostoja kertyy, ja jokainen lisää lukujen työtä. *Kompaktointi*
yhdistää tiedostoja: se lukee ne järjestyksessä, säilyttää kustakin
avaimesta uusimman version ja pudottaa hautakivet ja niiden peittämät
versiot:

```{.python tiedosto="esimerkit/nosql/lsm.py" osa="kompaktointi"}
```

Oikeissa toteutuksissa kompaktointi tehdään taustalla ja vähitellen:
*koon mukaan porrastettu* (*size-tiered*) yhdistää samankokoisia
tiedostoja, *tasoittainen* (*leveled*) pitää jokaisen tason avaimet
erillisissä tiedostoissa. Hautakivi voidaan pudottaa vasta, kun
kaikki sitä vanhemmat versiot ovat mukana yhdistämisessä ja – hajautetussa
tietokannassa – kun se on ehtinyt kaikille kopioille (luku 7).

## Kokeilu

```{.python tiedosto="esimerkit/luku08/lsm.py" osa="kaytto"}
```

30 kirjoitusta ja poisto neljän avaimen memtablella tuottivat seitsemän
tiedostoa. Poistettu avain palauttaa `None`, koska hautakivi on
uusin versio.

```{.python tiedosto="esimerkit/luku08/lsm.py" osa="vahvistus"}
```

```{.tuloste tiedosto="esimerkit/luku08/lsm.odotettu"}
```

Lukiessa Bloom-suodatin ohitti yhden tiedoston, ja vain yksi luettiin.
*Kirjoitusvahvistus* (*write amplification*) on levylle kirjoitettujen
tavujen suhde sovelluksen kirjoittamiin: kompaktointi kirjoittaa saman
datan uudelleen. Oikeissa LSM-puissa kerroin on usein 10–30, ja se on
LSM-puun hinta. B-puussa vastaava hinta maksetaan
satunnaiskirjoituksina ja koko sivun kirjoituksena pienestäkin
muutoksesta.

| Ominaisuus | B-puu | LSM-puu |
|--------|---------------|-----------------|
| kirjoitus | paikallaan, satunnainen | peräkkäin, nopea |
| luku | yksi polku puussa | monta tiedostoa, Bloom-suodattimet apuna |
| poisto | heti | hautakivi, siivous kompaktoinnissa |
| taustatyö | vähän | kompaktointi kuluttaa levyä ja suoritinta |
| sopii | lukupainotteinen, päivittyvä data | kirjoituspainotteinen, aikasarjat, lokit |

## Käytännössä

- LSM-puu sopii kirjoituspainotteiseen kuormaan. Lukupainotteiselle
  datalle B-puu on usein parempi.
- Kompaktointi kuluttaa levyn kaistaa ja tilaa: varaa levyä niin, että
  suurimmankin yhdistämisen tulos mahtuu.
- Hautakivet maksavat, kunnes ne siivotaan. Rakenna malli, jossa
  poistetaan kokonaisia partitioita tai annetaan datan vanhentua
  aikavälin mukaan, ei yksittäisiä rivejä jatkuvasti.
- RocksDB on LSM-puu kirjastona; sitä käytetään monen tietokannan ja
  jonon tallennuskerroksena (esimerkiksi Kafka Streamsin tilasäilö).

## Itsearviointi

- Osaat selittää LSM-puun kirjoitus- ja lukupolun.
- Osaat kertoa, miksi poisto on LSM-puussa hautakivi ja milloin se
  voidaan siivota.
- Osaat selittää, mitä Bloom-suodatin säästää ja millaisen virheen se
  voi tehdä.
- Osaat vertailla B-puuta ja LSM-puuta kirjoitus- ja lukuvahvistuksen
  kannalta.

# Ehdot ja toisto

Edellisen luvun ohjelmat etenivät suoraan ylhäältä alas. Todelliset
ohjelmat tekevät valintoja (*jos* syöte on virheellinen, ...) ja
toistavat (*jokaiselle* riville, ..., *kunnes* tavoite täyttyy).
Näitä rakenteita kutsutaan *ohjausrakenteiksi*.

## Vertailut ja totuusarvot

Vertailun tulos on totuusarvo `True` tai `False`:

| Lauseke | Merkitys |
|---------|----------|
| `a == b`, `a != b` | yhtä suuret, eri suuret |
| `a < b`, `a <= b`, `a > b`, `a >= b` | suuruusvertailut |
| `1 <= x <= 5` | ketjutettu vertailu: `x` välillä 1–5 |
| `x in kokoelma` | sisältyykö `x` kokoelmaan tai merkkijonoon |
| `ehto1 and ehto2` | molemmat tosia |
| `ehto1 or ehto2` | ainakin toinen tosi |
| `not ehto` | ehdon vastakohta |

Yhtäsuuruuden vertailu on `==`; yksi `=` on sijoitus. Pythonissa myös
muut kuin totuusarvot kelpaavat ehdoksi: nolla ja tyhjä merkkijono ovat
*epätosia*, muut luvut ja merkkijonot tosia. Siksi `if teksti:`
tarkoittaa "jos teksti ei ole tyhjä". Sama koskee luvun *Kokoelmat*
tietorakenteita: tyhjä kokoelma on epätosi.

## Valinta: if, elif ja else

`if`-lauseen ehdon jälkeen tulee kaksoispiste, ja ehdollisesti
suoritettavat rivit sisennetään neljällä välilyönnillä. Sisennys ei ole
Pythonissa tyyliseikka vaan osa kielioppia: se määrää, mitkä rivit
kuuluvat lohkoon.

Esimerkki laskee lipun hinnan neljälle eri-ikäiselle ostajalle. Rivi
`for ika in [4, 15, 34, 67]:` toistaa sisennetyn lohkon kerran
jokaiselle hakasulkeissa luetellulle luvulle; toistoon palataan tässä
luvussa ja luetteloihin eli listoihin luvussa *Kokoelmat*.

```{.python tiedosto="esimerkit/03-lippu.py"}
```

```{.tuloste tiedosto="esimerkit/03-lippu.odotettu"}
```

Ehdot tarkistetaan järjestyksessä, ja vain ensimmäisen toteutuvan
haaran lohko suoritetaan. Järjestyksellä on siis väliä: jos ehto
`ika < 18` olisi ennen ehtoa `ika < 7`, lapsetkin saisivat nuoren
lipun. `else` kattaa kaikki muut tapaukset.

## Toisto ehdolla: while

`while`-silmukka toistaa lohkoa niin kauan kuin ehto on tosi. Se sopii
tilanteisiin, joissa toistokertojen määrää ei tiedetä etukäteen:

```{.python tiedosto="esimerkit/03-korko.py"}
```

```{.tuloste tiedosto="esimerkit/03-korko.odotettu"}
```

Silmukan rungon on muutettava jotakin, mikä vaikuttaa ehtoon. Jos
`saldo` ei kasvaisi, silmukka ei päättyisi koskaan. Jakojäännös
`vuodet % 5 == 0` valitsee joka viidennen kierroksen tulostettavaksi.

Silmukan toiminta selviää seuraamalla muuttujien arvoja kierros
kierrokselta. Sen voi tehdä paperilla taulukkona tai tulostamalla tilan
jokaisen kierroksen lopussa:

```{.python tiedosto="esimerkit/03-jaljitys.py"}
```

```{.tuloste tiedosto="esimerkit/03-jaljitys.odotettu"}
```

Jokaisella kierroksella `luku % 10` poimii viimeisen numeron ja
`luku // 10` pudottaa sen pois. Kolmannen kierroksen jälkeen `luku` on
0, ehto `luku > 0` on epätosi ja suoritus jatkuu silmukan jälkeisestä
rivistä. Sama jäljitys on ensimmäinen keino, kun silmukka ei toimi
odotetusti.

## Toisto joukon yli: for ja range

`for`-silmukka käy läpi kokoelman alkiot yksi kerrallaan. `range`
tuottaa lukujonon: `range(5)` on 0, 1, 2, 3, 4 ja `range(1, 6)` on
1, 2, 3, 4, 5. Loppuarvo ei kuulu jonoon. Silmukat voivat olla
sisäkkäin:

```{.python tiedosto="esimerkit/03-kertotaulu.py"}
```

```{.tuloste tiedosto="esimerkit/03-kertotaulu.odotettu"}
```

`print(..., end="")` jättää rivinvaihdon pois, joten saman rivin luvut
tulostuvat peräkkäin.

## Silmukan keskeyttäminen: break ja continue

`break` lopettaa silmukan heti, `continue` siirtyy seuraavaan
kierrokseen. Tavallinen käyttö on syötteen kysyminen, kunnes se kelpaa.
`while True` toistaa loputtomasti, ja silmukasta poistutaan `break`illa,
kun syöte on kelvollinen:

```{.python tiedosto="esimerkit/03-arvio.py"}
```

Syötteellä `neljä`, `7` ja `4` tuloste on:

```{.tuloste tiedosto="esimerkit/03-arvio.odotettu"}
```

Tulosteessa ei näy käyttäjän kirjoittamaa tekstiä, koska syöte luettiin
tiedostosta. Merkkijonon metodi `strip()` poistaa alun ja lopun
välilyönnit, ja `isdigit()` kertoo, koostuuko merkkijono pelkistä
numeroista. Tarkistus tehdään ennen muunnosta `int(vastaus)`, joten
muunnos ei voi epäonnistua.

```{.dot otsikko="Esimerkin `03-arvio` suoritus: `continue` palaa silmukan alkuun, `break` poistuu silmukasta."}
digraph {
  nodesep=0.45; ranksep=0.3;
  lue [label="vastaus = input(...)"];
  numero [label="pelkkiä numeroita?", shape=diamond, style=filled, margin="0,0.02"];
  virhe1 [label="tulosta virhe"];
  muunna [label="arvosana = int(vastaus)"];
  vali [label="1 <= arvosana <= 5?", shape=diamond, style=filled, margin="0,0.02"];
  virhe2 [label="tulosta virhe"];
  kiitos [label="tulosta kiitos"];
  lue -> numero [weight=10];
  numero -> muunna [label=" kyllä", weight=10];
  numero -> virhe1 [label="ei"];
  virhe1:n -> lue:e [label=" continue"];
  muunna -> vali [weight=10];
  vali -> kiitos [label=" kyllä: break", weight=10];
  vali -> virhe2 [label="ei"];
  virhe2:e -> lue:e [label="  uusi kierros"];
  { rank=same; numero; virhe1; }
  { rank=same; vali; virhe2; }
}
```

## Kokeile itse

Pohja ja tarkistus kuten edellisessä luvussa, esimerkiksi
`python3 tarkista.py --aloita 03-1`.

1. **Lämpötilan luokitus** (`03-1`). Ohjelma lukee lämpötilan ja
   tulostaa `pakkasta`, `nollassa`, `lämmintä` tai `hellettä` (25
   astetta tai enemmän).
2. **Summa lopetusmerkkiin asti** (`03-2`). Ohjelma lukee
   kokonaislukuja, kunnes luku on 0, ja tulostaa lukujen määrän ja
   summan.
3. **Collatzin jono** (`03-3`). Parillinen luku puolitetaan, pariton
   kerrotaan kolmella ja siihen lisätään yksi. Ohjelma tulostaa,
   monellako askeleella syötteenä annetusta luvusta päästään lukuun 1.
4. **Alkuluvut** (`03-4`). Ohjelma tulostaa alkuluvut väliltä 2–*n*.
   Tarvitset sisäkkäiset silmukat ja `break`-lauseen.

## Käytännössä

- **`for`, kun läpikäytävä joukko tunnetaan, `while`, kun toistetaan
  ehdon täyttymiseen asti.** `for`-silmukka ei voi unohtaa kasvattaa
  laskuria, joten se on turvallisempi aina kun se sopii.
- **Vartijaehto ja `continue` vähentävät sisäkkäisyyttä.** Esimerkin
  `03-arvio` virheelliset tapaukset käsitellään heti, ja normaali
  polku jatkuu sisentämättä. Yli kolmen tason sisennys on merkki siitä,
  että koodi kannattaa jakaa funktioiksi (seuraava luku).
- **Tarkista ennen kuin muunnat.** Ohjelma, joka kaatuu virheelliseen
  syötteeseen, on käyttäjälle virhe, vaikka ohjelmoija pitäisi syötettä
  käyttäjän virheenä.
- **Ehtojen järjestys on osa logiikkaa.** Kirjoita rajatapaukset
  (nolla, negatiivinen, raja-arvo kuten tasan 18 vuotta) auki ja
  tarkista, mihin haaraan kukin osuu.
- **Raja-arvot ovat yleisin virheiden lähde** (*off-by-one*):
  `range(1, 13)` on kuukaudet 1–12, ei 1–13. Testaa aina ensimmäinen
  ja viimeinen kierros.

## Itsearviointi

- Osaat kirjoittaa `if`–`elif`–`else`-rakenteen ja perustella ehtojen
  järjestyksen.
- Osaat valita `for`- ja `while`-silmukan välillä ja kirjoittaa
  silmukan, joka varmasti päättyy.
- Osaat kysyä syötettä uudelleen, kunnes se on kelvollinen.
- Osaat seurata silmukan suoritusta kierros kierrokselta ja kertoa
  muuttujien arvot jokaisen kierroksen jälkeen.
- Osaat käyttää `range`-funktiota ja kertoa, mitkä luvut
  `range(2, 10, 3)` tuottaa.

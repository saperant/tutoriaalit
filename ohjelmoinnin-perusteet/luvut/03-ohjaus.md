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
muut kuin totuusarvot kelpaavat ehdoksi: nolla, tyhjä merkkijono ja
tyhjä lista ovat *epätosia*, muut arvot tosia. Siksi `if teksti:`
tarkoittaa "jos teksti ei ole tyhjä".

## Valinta: if, elif ja else

`if`-lauseen ehdon jälkeen tulee kaksoispiste, ja ehdollisesti
suoritettavat rivit sisennetään neljällä välilyönnillä. Sisennys ei ole
Pythonissa tyyliseikka vaan osa kielioppia: se määrää, mitkä rivit
kuuluvat lohkoon.

```{.python tiedosto="esimerkit/03-lippu.py"}
```

```{.tuloste tiedosto="esimerkit/03-lippu.odotettu"}
```

Ehdot tarkistetaan järjestyksessä, ja vain ensimmäisen toteutuvan
haaran lohko suoritetaan. Järjestyksellä on siis väliä: jos ehto
`ika < 18` olisi ennen ehtoa `ika < 7`, lapsetkin saisivat nuoren
lipun. `else` kattaa kaikki muut tapaukset.

Esimerkin `for ika in [4, 15, 34, 67]:` toistaa lohkon jokaiselle
listan luvulle. Listoihin palataan luvussa *Kokoelmat*.

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
- Osaat käyttää `range`-funktiota ja kertoa, mitkä luvut
  `range(2, 10, 3)` tuottaa.

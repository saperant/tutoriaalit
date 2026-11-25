# Kokoelmat

Harva ohjelma käsittelee yksittäisiä arvoja. Arvosanoja on kymmeniä,
sanoja tuhansia ja asiakkaita miljoonia. *Kokoelma* säilyttää monta
arvoa yhden nimen alla. Pythonin neljä peruskokoelmaa ovat lista,
monikko, sanakirja ja joukko, ja oikean valinta tekee koodista
lyhyen ja nopean.

| Kokoelma | Kirjoitus | Ominaisuudet | Käyttö |
|------------|-----------|---------------|---------------|
| lista `list` | `[3, 1, 2]` | järjestetty, muutettava, sallii toistot | jono samanlaisia arvoja |
| monikko `tuple` | `(60.2, 24.9)` | järjestetty, muuttumaton | kiinteä arvoryhmä |
| sanakirja `dict` | `{"Aino": 5}` | avain → arvo, avaimet yksikäsitteisiä | haku avaimella |
| joukko `set` | `{"a", "b"}` | ei järjestystä eikä toistoja | jäsenyys, joukko-operaatiot |

## Lista

Lista on järjestetty jono arvoja. Alkioihin viitataan *indeksillä*,
joka alkaa nollasta: `arvosanat[0]` on ensimmäinen ja `arvosanat[-1]`
viimeinen. *Viipale* `arvosanat[:3]` on uusi lista kolmesta
ensimmäisestä alkiosta.

```{.dot otsikko="Lista `[3, 5, 0, 4, 2]`: jokaisella alkiolla on indeksi alusta (0, 1, 2, ...) ja lopusta (-1, -2, ...). Viipale `[1:4]` sisältää indeksit 1, 2 ja 3; loppuindeksi ei kuulu mukaan."}
digraph {
  node [shape=record, style=filled];
  lista [label="{indeksi|alkio|lopusta}|{0|3|-5}|{1|5|-4}|{2|0|-3}|{3|4|-2}|{4|2|-1}"];
}
```

```{.python tiedosto="esimerkit/05-arvosanat.py"}
```

```{.tuloste tiedosto="esimerkit/05-arvosanat.odotettu"}
```

Esimerkissä on listan tärkeimmät käyttötavat:

- `len`, `sum`, `min` ja `max` toimivat kaikille lukulistoille.
- *Listakooste* (*list comprehension*) `[a for a in arvosanat if a > 0]`
  luo uuden listan suodattamalla. Se on lyhenne silmukalle, joka lisää
  ehdon täyttävät alkiot tyhjään listaan metodilla `append`.
- `[0] * 6` luo kuuden nollan listan. Jakaumassa arvosana on suoraan
  indeksi, jolloin lukumäärän kasvattaminen ei vaadi vertailuja.
- `sorted` palauttaa uuden järjestetyn listan; metodi `sort()`
  järjestäisi alkuperäisen listan paikallaan.

Tärkeimmät listan metodit: `append(x)` lisää loppuun, `insert(i, x)`
kohtaan `i`, `pop()` poistaa ja palauttaa viimeisen, `remove(x)`
poistaa ensimmäisen arvon `x` ja `index(x)` kertoo sen paikan.

## Sanakirja

Sanakirja yhdistää *avaimet* arvoihin, kuten puhelinluettelo nimen
numeroon. Haku avaimella on nopea riippumatta sanakirjan koosta, kun
listasta etsiminen vaatii pahimmillaan kaikkien alkioiden läpikäynnin.

```{.python tiedosto="esimerkit/05-sanat.py"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/05-sanat.syote"}
```

```{.tuloste tiedosto="esimerkit/05-sanat.odotettu"}
```

```{.dot otsikko="Sanakirja `lukumaarat` syötteen lukemisen jälkeen (neljä yleisintä avainta). Arvo haetaan avaimella: `lukumaarat[\"koira\"]` on 3."}
digraph {
  ranksep=0.3;
  nimi [label="lukumaarat", shape=plain, style=""];
  sk [shape=record, style=filled,
      label="{avain|\"koira\"|\"pihalla\"|\"ja\"|\"lapsi\"}|{arvo|3|2|2|2}"];
  nimi -> sk;
}
```

Ohjelma lukee tekstin *vakiosyötteestä* `sys.stdin`, jota voi käydä
läpi rivi kerrallaan `for`-silmukalla kuten tiedostoa. Lause
`import sys` ottaa käyttöön standardikirjaston modulin `sys`;
moduleihin palataan luvussa *Modulit ja standardikirjasto*.

- `lukumaarat.get(sana, 0)` palauttaa arvon tai oletuksen 0, jos avainta
  ei ole. Pelkkä `lukumaarat[sana]` aiheuttaisi puuttuvalla avaimella
  virheen `KeyError`.
- `items()` palauttaa avain–arvo-parit. `sorted(..., key=...)`
  järjestää parit lukumäärän mukaan. `key` saa funktion, joka kertoo,
  mitä alkiosta verrataan; `lambda pari: pari[1]` on lyhyt nimetön
  funktio, joka palauttaa parin toisen osan.
- `for sana, maara in ...` *purkaa* parin kahteen nimeen.

Tuloste paljastaa yksinkertaisen ratkaisun rajat: *koira* ja *koiralle*
ovat eri sanoja. Kielen taivutus vaatii erillisen kirjaston; tärkeintä
on tunnistaa, mitä ohjelma ei tee, ja kertoa se.

## Joukko

Joukko sisältää kunkin arvon vain kerran. Se on tehokas jäsenyyden
tarkistamiseen ja joukko-operaatioihin:

```{.python tiedosto="esimerkit/05-kurssit.py"}
```

```{.tuloste tiedosto="esimerkit/05-kurssit.odotettu"}
```

Joukolla ei ole järjestystä, joten tulostettaessa se järjestetään
`sorted`-funktiolla. Muuten tulostusjärjestys voisi vaihdella.

## Monikko

Monikko on kiinteä ryhmä arvoja, jota ei voi muuttaa luomisen jälkeen.
Se sopii arvoille, jotka kuuluvat yhteen ja joiden merkitys riippuu
paikasta, kuten koordinaattipari. Sanakirjan `items()` palautti
avain–arvo-parit juuri monikoina.

```{.python tiedosto="esimerkit/05-monikko.py"}
```

```{.tuloste tiedosto="esimerkit/05-monikko.odotettu"}
```

- Monikko kirjoitetaan kaarisulkeisiin, ja sen alkiot *puretaan*
  nimiin sijoituksella `leveys, pituus = sijainti`.
- Funktio palauttaa useita arvoja monikkona: `return min(luvut),
  max(luvut)`. Paluuarvon tyyppi on `tuple[float, float]`.
- Koska monikko ei voi muuttua, se kelpaa sanakirjan avaimeksi ja
  joukon alkioksi. Lista ei kelpaa.

Kun kenttiä on enemmän kuin kaksi tai kolme, nimetyt kentät ovat
selvempiä kuin paikat: silloin käytetään luvun *Luokat ja oliot*
dataluokkaa.

## Sisäkkäiset rakenteet

Kokoelman alkiot voivat olla kokoelmia. Oikea data on usein tällaista:
jokaisella opiskelijalla on lista arvosanoja, ja taulukon jokainen rivi
on monikko.

```{.python tiedosto="esimerkit/05-sisakkaiset.py"}
```

```{.tuloste tiedosto="esimerkit/05-sisakkaiset.odotettu"}
```

Sisäkkäiseen rakenteeseen viitataan taso kerrallaan vasemmalta
oikealle: `arvosanat["Aino"]` on lista ja `arvosanat["Aino"][0]` sen
ensimmäinen alkio. Tyyppivihje `dict[str, list[int]]` kertoo rakenteen
samassa järjestyksessä: avaimet ovat merkkijonoja ja arvot
kokonaislukulistoja. `setdefault(avain, [])` palauttaa avaimen arvon ja
lisää ensin tyhjän listan, jos avainta ei ole.

Kahta tai kolmea tasoa syvempi rakenne on vaikea lukea. Silloin
sisemmille tasoille annetaan nimi funktiolla tai luokalla.

## Viittaukset ja muuttuvuus

Muuttuja viittaa arvoon; se ei sisällä kopiota. Kun lista sijoitetaan
toiseen nimeen, molemmat nimet viittaavat samaan listaan:

```{.python tiedosto="esimerkit/05-alias.py"}
```

```{.tuloste tiedosto="esimerkit/05-alias.odotettu"}
```

```{.dot otsikko="Esimerkin tilanne lopussa. Sijoitus `toinen_nimi = ostokset` antoi samalle listalle toisen nimen; `copy()` loi uuden listan."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.6;
  node [shape=plain, style=""];
  kopio; toinen_nimi; ostokset;
  l2 [shape=record, style=filled,
      label="{\"maito\"|\"leipä\"|\"juusto\"|\"omena\"}"];
  l1 [shape=record, style=filled,
      label="{\"maito\"|\"leipä\"|\"juusto\"}"];
  kopio -> l2;
  toinen_nimi -> l1;
  ostokset -> l1;
}
```

Tämä koskee kaikkia *muutettavia* arvoja: listoja, sanakirjoja,
joukkoja ja olioita. Myös funktiolle annettu lista on sama lista, joten
funktio voi muuttaa kutsujan dataa. Luvut, merkkijonot ja monikot ovat
*muuttumattomia*, joten niiden kohdalla ilmiötä ei voi havaita.

## Kokeile itse

1. **Parilliset luvut** (`05-1`). Funktio `parilliset` palauttaa
   listan parilliset luvut listakoosteella.
2. **Yleisin sana** (`05-2`). Funktio `yleisin` laskee esiintymät
   sanakirjaan ja palauttaa yleisimmän sanan; tasatilanteessa
   aakkosjärjestyksessä ensimmäisen.
3. **Yhteiset alkiot** (`05-3`). Funktio `yhteiset` palauttaa
   kummassakin listassa esiintyvät merkkijonot järjestettynä. Käytä
   joukkoja.
4. **Lisäys muuttamatta alkuperäistä** (`05-4`). Pohjan funktio
   muuttaa kutsujan listaa. Korjaa se palauttamaan uusi lista.

## Käytännössä

- **Valitse kokoelma käytön mukaan.** Haku avaimella: sanakirja.
  Onko alkio mukana: joukko. Järjestys ja toistot merkitsevät: lista.
  Kiinteä ryhmä eri merkityksisiä arvoja (koordinaatit, nimi ja ikä):
  monikko tai luvun *Luokat ja oliot* dataluokka.
- **Listassa samanlaisia asioita.** `[nimi, ika, kaupunki]` on huono
  lista, koska alkioiden merkitys riippuu paikasta. Lista on jono
  samaa lajia olevia arvoja.
- **Älä muuta kokoelmaa, jota käyt läpi silmukassa.** Alkioiden
  poistaminen läpikäytävästä listasta ohittaa alkioita. Luo sen sijaan
  uusi lista suodattamalla.
- **Funktio ei muuta parametrinaan saamaansa kokoelmaa**, ellei se ole
  funktion nimetty tarkoitus (kuten `lisaa_tuote`). Muuten se palauttaa
  uuden kokoelman.
- **Kooste silloin, kun se on luettava.** Yksinkertainen suodatus tai
  muunnos koosteena, monimutkaisempi logiikka tavallisena silmukkana.

## Itsearviointi

- Osaat valita listan, monikon, sanakirjan ja joukon välillä
  tehtävän mukaan ja perustella valinnan.
- Osaat käyttää indeksejä, viipaleita ja listan tärkeimpiä metodeja.
- Osaat laskea esiintymiä sanakirjalla ja järjestää tuloksen arvon
  mukaan.
- Osaat suodattaa ja muuntaa listan listakoosteella.
- Osaat selittää, miksi `kopio = lista` ei kopioi listaa.
- Osaat palauttaa funktiosta useita arvoja monikkona ja purkaa
  monikon nimiin.
- Osaat rakentaa sisäkkäisen rakenteen, kuten sanakirjan listoja, ja
  viitata sen alkioihin.

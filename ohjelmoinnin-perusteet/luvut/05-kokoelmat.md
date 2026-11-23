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

- `lukumaarat.get(sana, 0)` palauttaa arvon tai oletuksen 0, jos avainta
  ei ole. Pelkkä `lukumaarat[sana]` aiheuttaisi puuttuvalla avaimella
  virheen `KeyError`.
- `items()` palauttaa avain–arvo-parit. `sorted(..., key=...)`
  järjestää parit lukumäärän mukaan. `key` saa funktion, joka kertoo,
  mitä alkiosta verrataan; `lambda pari: pari[1]` on lyhyt nimetön
  funktio, joka palauttaa parin toisen osan.
- `for sana, maara in ...` *purkaa* parin kahteen nimeen.
- `sys.stdin` on ohjelman syöte, jota voi lukea rivi kerrallaan kuin
  tiedostoa. Moduli `sys` otetaan käyttöön lauseella `import sys`.

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

## Viittaukset ja muuttuvuus

Muuttuja viittaa arvoon; se ei sisällä kopiota. Kun lista sijoitetaan
toiseen nimeen, molemmat nimet viittaavat samaan listaan:

```{.python tiedosto="esimerkit/05-alias.py"}
```

```{.tuloste tiedosto="esimerkit/05-alias.odotettu"}
```

Tämä koskee kaikkia *muutettavia* arvoja: listoja, sanakirjoja,
joukkoja ja olioita. Myös funktiolle annettu lista on sama lista, joten
funktio voi muuttaa kutsujan dataa. Luvut, merkkijonot ja monikot ovat
*muuttumattomia*, joten niiden kohdalla ilmiötä ei voi havaita.

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

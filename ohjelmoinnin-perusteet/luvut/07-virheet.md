# Virheet ja poikkeukset

Ohjelmassa voi olla kolmenlaisia virheitä:

1. **Syntaksivirhe**: koodi ei ole kelvollista Pythonia, esimerkiksi
   kaksoispiste puuttuu. Python ei suostu ajamaan ohjelmaa lainkaan.
2. **Ajonaikainen virhe**: koodi on kelvollista, mutta jokin operaatio
   epäonnistuu, kuten tekstin muuntaminen luvuksi tai nollalla
   jakaminen. Python *nostaa poikkeuksen*.
3. **Looginen virhe**: ohjelma toimii, mutta tulos on väärä. Näitä
   löydetään testeillä (luku *Testaus*).

Tarkistustyökalut löytävät osan toisen ja kolmannen lajin virheistä
etukäteen. Tämä luku käsittelee poikkeuksia: miten virheilmoitus
luetaan, miten poikkeus käsitellään ja milloin oma koodi nostaa
poikkeuksen.

## Virheilmoituksen lukeminen

Ohjelma laskee syötteen lukujen keskiarvon, mutta ei varaudu
virheelliseen syötteeseen:

```{.python tiedosto="esimerkit/07-keskiarvo.kaatuu.py"}
```

Kun syötteen kolmas rivi on `kaksi`, ohjelma kaatuu:

```text
Traceback (most recent call last):
  File "07-keskiarvo.kaatuu.py", line 14, in <module>
    luvut = lue_luvut(sys.stdin.read().splitlines())
  File "07-keskiarvo.kaatuu.py", line 10, in lue_luvut
    luvut.append(float(rivi))
ValueError: could not convert string to float: 'kaksi'
```

Virheilmoitus (*traceback*) luetaan **alhaalta ylös**:

1. Viimeinen rivi kertoo poikkeuksen tyypin (`ValueError`) ja syyn.
2. Sen yläpuolella on rivi, jolla virhe tapahtui (tiedosto, rivinumero,
   funktio ja koodi).
3. Ylemmät rivit kertovat, mistä tuo funktio kutsuttiin, aina
   pääohjelmaan (`<module>`) asti.

```{.dot otsikko="Virheilmoitus on kutsupino (luku *Funktiot*) kaatumishetkellä: virheilmoituksen ylin rivi on pääohjelma ja alin kohta, jossa poikkeus nousi."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  m [label="<module>\nrivi 14"];
  f [label="lue_luvut\nrivi 10"];
  x [label="float(\"kaksi\")"];
  v [label="ValueError", shape=plain, style=""];
  m -> f [label="kutsuu"];
  f -> x [label="kutsuu"];
  x -> v [label="nostaa", style=dashed];
}
```

Poikkeus nousee kutsupinoa pitkin kutsujalta toiselle. Jos mikään
funktio ei käsittele sitä, se päätyy pääohjelmaan asti, ja Python
lopettaa ohjelman ja tulostaa pinon.

Yleisimmät poikkeukset:

| Poikkeus | Tyypillinen syy |
|----------|-----------------|
| `ValueError` | arvo on oikeaa tyyppiä mutta kelvoton: `int("abc")` |
| `TypeError` | väärä tyyppi: `"a" + 1` |
| `KeyError` | sanakirjassa ei ole avainta |
| `IndexError` | listan indeksi on liian suuri |
| `ZeroDivisionError` | jako nollalla |
| `FileNotFoundError` | tiedostoa ei ole |
| `NameError` | nimeä ei ole määritelty (kirjoitusvirhe) |
| `AttributeError` | arvolla ei ole metodia: `None.strip()` |

## Poikkeuksen käsittely: try ja except

`try`-lohkon koodi suoritetaan normaalisti. Jos siinä nousee
`except`-osassa mainittu poikkeus, suoritus siirtyy `except`-lohkoon,
ja ohjelma jatkaa siitä eteenpäin:

```{.python tiedosto="esimerkit/07-keskiarvo-korjattu.py"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/07-keskiarvo-korjattu.syote"}
```

```{.tuloste tiedosto="esimerkit/07-keskiarvo-korjattu.odotettu"}
```

Korjattu versio käsittelee kaikki tiedossa olevat poikkeamat:

- virheellinen rivi ohitetaan, ja käyttäjälle kerrotaan sen
  rivinumero; virhettä ei niellä hiljaa
- tyhjät rivit ohitetaan tarkoituksella
- jos lukuja ei ole lainkaan, ohjelma kertoo sen ja päättyy
  paluuarvolla 1 (`sys.exit(1)`), joka kertoo kutsujalle, että
  ohjelma epäonnistui. Nollalla jakamista ei koskaan tapahdu.

## Poikkeuksen nostaminen: raise

Oma funktio nostaa poikkeuksen lauseella `raise`, kun se ei voi tehdä
tehtäväänsä. Näin virheellinen arvo pysäytetään heti ensimmäisessä
kohdassa, jossa se huomataan, eikä se kulje ohjelmassa eteenpäin
aiheuttaen vääriä tuloksia:

```{.python tiedosto="esimerkit/07-tilisiirto.py"}
```

```{.tuloste tiedosto="esimerkit/07-tilisiirto.odotettu"}
```

`jasenna_summa` ei tulosta mitään eikä palauta erikoisarvoa kuten `-1`
virheen merkiksi. Se nostaa `ValueError`in, jonka viesti kertoo, mikä
syötteessä oli vialla. Kutsuja päättää, mitä virheelle tehdään:
tässä pyyntö hylätään ja seuraava käsitellään. `except ValueError as
virhe` antaa poikkeusolion nimelle `virhe`, ja `str(virhe)` on sen
viesti.

Kate tarkistetaan sen sijaan tavallisella `if`-lauseella, koska
riittämätön saldo on odotettu ja tavallinen tilanne eikä syötteen
virhe. Luvussa *Luokat ja oliot* tilisiirrosta tehdään luokka, jolla on
oma poikkeustyyppinsä.

`try`-lauseeseen voi lisätä myös `else`-lohkon, joka suoritetaan, jos
poikkeusta ei noussut, ja `finally`-lohkon, joka suoritetaan aina.

## Kun ohjelma ei toimi

Virheilmoitus kertoo, missä ohjelma kaatui, mutta syy voi olla
aiemmassa rivissä, ja looginen virhe ei kaada ohjelmaa lainkaan.
Virheen etsiminen (*debuggaus*) on järjestelmällistä työtä:

1. **Toista virhe.** Etsi pienin syöte, jolla virhe näkyy. Luvussa
   *Testaus* siitä tehdään testi, joka estää virheen paluun.
2. **Lue virheilmoitus** alhaalta ylös.
3. **Tarkista oletukset.** Tulosta välitulokset (`print(f"{muuttuja=}")`
   tulostaa nimen ja arvon) tai pysäytä ohjelma `breakpoint()`-kutsulla
   debuggeriin, jossa muuttujia voi tutkia ja koodia ajaa rivi
   kerrallaan. Editorien debuggerit tekevät saman graafisesti.
4. **Puolita.** Jos et tiedä, missä vaiheessa data menee vääräksi,
   tarkista se puolivälissä ja jatka siitä puoliskosta, jossa virhe on.
5. **Selitä ongelma ääneen** kollegalle tai vaikka kumiankalle
   (*rubber duck debugging*). Selittäessä huomaa usein oletuksen, joka
   ei pidä.

## Kokeile itse

1. **Iän jäsennys** (`07-1`). Funktio `jasenna_ika` palauttaa iän
   kokonaislukuna ja nostaa `ValueError`in, jos teksti ei ole luku tai
   ikä ei ole välillä 0–150.
2. **Kelvollisten rivien summa** (`07-2`). Funktio
   `summaa_kelvolliset` palauttaa lukurivien summan ja virheellisten
   rivien numerot. Tyhjät rivit eivät ole virheitä.
3. **Korjaa kaatuva ohjelma** (`07-3`). Pohjan ohjelma kaatuu
   kolmella eri syötteellä. Aja se, lue virheilmoitukset ja korjaa
   ohjelma käsittelemään tyhjät rivit, virheelliset pisteet ja tyhjä
   syöte.

## Käytännössä

- **Validoi syöte ohjelman reunalla.** Data tarkistetaan siinä, missä
  se tulee ohjelmaan (käyttäjältä, tiedostosta, verkosta). Sisempi koodi
  voi silloin luottaa siihen.
- **Nosta poikkeus, älä palauta virhekoodia.** Erikoisarvon, kuten `-1`
  tai `None`, voi unohtaa tarkistaa; poikkeusta ei voi.
- **Sieppaa vain poikkeukset, jotka osaat käsitellä, ja nimeä ne.**
  `except ValueError:` eikä pelkkä `except:`. Paljas `except` sieppaa
  myös ohjelmointivirheet, kuten kirjoitusvirheen nimessä, ja piilottaa
  ne.
- **Älä niele virheitä.** `except ValueError: pass` hävittää tiedon
  ongelmasta. Kerro käyttäjälle, kirjaa lokiin tai nosta eteenpäin.
- **Pidä `try`-lohko pienenä.** Lohkoon kuuluu vain rivi, jonka virhe
  käsitellään, jotta muiden rivien virheet eivät sekoitu siihen.
- **Kaatuminen on parempi kuin väärä tulos.** Ohjelma, joka jatkaa
  virheellisellä datalla, tuottaa vääriä raportteja, joita kukaan ei
  huomaa. Jos tilanteeseen ei osata reagoida järkevästi, poikkeuksen
  annetaan kaataa ohjelma selvällä viestillä.
- **Virheviesti kertoo, mikä arvo ja missä.** `virheellinen summa:
  'abc'` auttaa käyttäjää korjaamaan syötteen; `virhe` ei auta.

## Itsearviointi

- Osaat lukea virheilmoituksen alhaalta ylös ja löytää virheen
  aiheuttaneen rivin.
- Osaat käsitellä odotetun poikkeuksen `try`–`except`-lauseella ja
  kertoa käyttäjälle, mitä tapahtui.
- Osaat nostaa poikkeuksen omassa funktiossa kuvaavalla viestillä.
- Osaat perustella, milloin poikkeus käsitellään ja milloin ohjelman
  annetaan kaatua.
- Osaat etsiä virheen järjestelmällisesti: toistaa sen, rajata
  kohdan ja tarkistaa oletukset tulostamalla tai debuggerilla.

# Arvot, tyypit ja muuttujat

Ohjelma käsittelee *arvoja*: lukuja, tekstiä ja totuusarvoja. Jokaisella
arvolla on *tyyppi*, joka määrää, mitä arvolla voi tehdä. Lukuja voi
jakaa, tekstiä ei. Tyypin ymmärtäminen on ensimmäinen askel virheiden
välttämiseen.

## Perustyypit

| Tyyppi | Merkitys | Esimerkkejä |
|--------|----------|-------------|
| `int` | kokonaisluku, rajaton koko | `0`, `-12`, `10_000` |
| `float` | liukuluku eli desimaaliluku | `3.14`, `-0.5`, `1e6` |
| `str` | merkkijono eli teksti | `"Helsinki"`, `'ä'`, `""` |
| `bool` | totuusarvo | `True`, `False` |
| `None` | "ei arvoa" | `None` |

Desimaalierotin on koodissa aina piste. Alaviiva luvussa (`10_000`) vain
helpottaa lukemista. Funktio `type(arvo)` kertoo arvon tyypin.

## Lausekkeet ja operaattorit

*Lauseke* on koodin osa, jolla on arvo, kuten `2 + 3` tai
`hinta * maara`. Laskutoimitukset:

| Operaattori | Merkitys | `7 ? 2` |
|-------------|----------|---------|
| `+`, `-`, `*` | yhteen-, vähennys- ja kertolasku | `9`, `5`, `14` |
| `/` | jakolasku, tulos aina `float` | `3.5` |
| `//` | kokonaislukujako (pyöristää alaspäin) | `3` |
| `%` | jakojäännös | `1` |
| `**` | potenssi | `49` |

Laskujärjestys on matematiikan mukainen: potenssi ennen kerto- ja
jakolaskua ja ne ennen yhteen- ja vähennyslaskua. Sulkeilla
järjestyksen voi määrätä, ja niitä kannattaa käyttää aina, kun
järjestys ei ole lukijalle ilmeinen.

Kokonaislukujako ja jakojäännös ratkaisevat yllättävän monta käytännön
tehtävää: montako täyttä laatikkoa, montako jää yli, monesko viikko.
Seuraava ohjelma muuntaa sekunnit tunneiksi, minuuteiksi ja sekunneiksi:

```{.python tiedosto="esimerkit/02-aika.py"}
```

```{.tuloste tiedosto="esimerkit/02-aika.odotettu"}
```

Muotoilu `{minuutit:02d}` tulostaa kokonaisluvun kahden merkin
levyisenä etunollalla täytettynä.

## Muuttujat

Sijoituslause `nimi = lauseke` laskee lausekkeen arvon ja antaa sille
nimen. Muuttuja ei ole laatikko, johon arvo kopioidaan, vaan nimi, joka
viittaa arvoon. Sama nimi voidaan myöhemmin sijoittaa viittaamaan
toiseen arvoon: `saldo = saldo + 10` laskee ensin oikean puolen ja
siirtää sitten nimen uuteen arvoon. Lyhenne samalle on `saldo += 10`.

```{.dot otsikko="Sijoitus `saldo = saldo + 10` ei muuta arvoa 100, vaan siirtää nimen `saldo` uuteen arvoon 110."}
digraph {
  nodesep=0.3; ranksep=0.3;
  subgraph cluster_ennen {
    label="saldo = 100"; style=rounded; color="#B8C4C8"; margin=12;
    n1 [label="saldo", shape=plain, style=""];
    a1 [label="100"];
    n1 -> a1;
  }
  subgraph cluster_jalkeen {
    label="saldo = saldo + 10"; style=rounded; color="#B8C4C8"; margin=12;
    n2 [label="saldo", shape=plain, style=""];
    a2 [label="100", style="rounded,dashed"];
    b2 [label="110"];
    n2 -> a2 [style=invis];
    n2 -> b2;
  }
}
```

Kuvan ajattelutapa (nimi viittaa arvoon) selittää luvussa *Kokoelmat*
ilmiön, jossa kaksi nimeä viittaa samaan listaan.

Nimeämiskäytännöt (PEP 8, Pythonin tyyliopas):

- Muuttujat ja funktiot pienillä kirjaimilla, sanat alaviivalla
  erotettuina: `tippi_prosentti`, `laske_alv`.
- Vakiot eli arvot, joita ohjelma ei muuta, isoilla kirjaimilla:
  `SEKUNTIA_TUNNISSA`.
- Nimi kertoo merkityksen, ei tyyppiä: `henkiloita`, ei `luku1` tai
  `lista`. Yksikkö kuuluu nimeen, jos se ei ole ilmeinen: `kesto_s`,
  `hinta_snt`.

Ääkköset ovat Pythonissa sallittuja nimissä, mutta tässä tutoriaalissa
nimet kirjoitetaan ilman niitä, koska kaikki työkalut ja näppäimistöt
eivät käsittele niitä yhtä hyvin.

## Tulostus ja muotoilu

`print` tulostaa argumenttinsa välilyönnein erotettuina ja lopuksi
rivinvaihdon. *f-merkkijono* (`f"..."`) on suositeltu tapa koota
tulosteita:

| Muotoilu | Tulos | Merkitys |
|----------|-------|----------|
| `f"{x:.2f}"` | `3.14` | kaksi desimaalia |
| `f"{n:5}"` | `   42` | viiden merkin levyinen |
| `f"{s:<8}"` | `nimi    ` | vasemmalle tasattu |
| `f"{n:>8}"` | `      42` | oikealle tasattu |
| `f"{n:03d}"` | `007` | etunollat |
| `f"{x:.1%}"` | `12.5%` | prosentteina |

## Syötteen lukeminen

`input(kehote)` tulostaa kehotteen ja palauttaa käyttäjän kirjoittaman
rivin **aina merkkijonona**. Jos syöte on luku, se on muunnettava
funktiolla `int` tai `float`:

```{.python tiedosto="esimerkit/02-lampotila.py"}
```

Syötteellä `-3,5` tuloste on:

```{.tuloste tiedosto="esimerkit/02-lampotila.odotettu"}
```

Suomalainen käyttäjä kirjoittaa desimaalipilkun, joten ohjelma korvaa
sen pisteellä ennen muunnosta. Tämä on ensimmäinen esimerkki syötteen
*validoinnista*: ohjelma ei voi olettaa, että syöte on siinä muodossa,
jota ohjelmoija ajatteli. Jos syöte ei ole luku lainkaan, `float`
aiheuttaa virheen. Sen käsittely opetetaan luvussa *Virheet ja
poikkeukset*.

Merkkijono ja luku eivät summaudu. Tyyppitarkistin mypy huomaa virheen
ennen kuin ohjelmaa ajetaan:

```{.python tiedosto="esimerkit/02-tyyppi.ei-kaanny.py"}
```

```text
error: Unsupported operand types for + ("str" and "int")
```

## Liukulukujen tarkkuus

Tietokone esittää liukuluvut kaksijärjestelmässä, eikä esimerkiksi
lukua 0,1 voi esittää tarkasti. Pienet pyöristysvirheet näkyvät
vertailuissa:

```{.python tiedosto="esimerkit/02-liukuluku.py"}
```

```{.tuloste tiedosto="esimerkit/02-liukuluku.odotettu"}
```

Mittaustuloksille (lämpötila, matka) pyöristysvirhe ei haittaa. Rahassa
se haittaa, koska sentin virhe kirjanpidossa on virhe. Siksi rahasummat
käsitellään kokonaislukuina sentteinä, kuten tämän tutoriaalin
esimerkeissä, tai standardikirjaston `Decimal`-tyypillä.

## Kokeile itse

Tehtävien pohjat ja tarkistus on kuvattu johdannon osiossa *Tehtävät*:
`python3 tarkista.py --aloita 02-1` kopioi pohjan ja
`python3 tarkista.py 02-1` tarkistaa ratkaisun.

1. **Munakennot** (`02-1`). Ohjelma lukee munien määrän ja tulostaa,
   montako 12 munan kennoa tulee täyteen ja montako munaa jää yli.
2. **Matka-aika** (`02-2`). Ohjelma lukee matkan kilometreinä
   (desimaalipilkku sallittu) ja keskinopeuden ja tulostaa matka-ajan
   muodossa `2 h 09 min`.
3. **Lasku tasan** (`02-3`). Ohjelma lukee loppusumman sentteinä ja
   maksajien määrän ja tulostaa yhden osuuden euroina sekä sen, montako
   senttiä jää jakamatta. Liukulukuja ei tarvita.

## Käytännössä

- **Nimet kertovat merkityksen.** Koodia luetaan paljon useammin kuin
  kirjoitetaan. Hyvä nimi tekee kommentin tarpeettomaksi:
  `tunnit = kesto // SEKUNTIA_TUNNISSA` ei tarvitse selitystä.
- **Ei taikanumeroita.** Kaavassa esiintyvä `3600` tai `13.5` saa
  nimen (`SEKUNTIA_TUNNISSA`, `ALV_PROSENTTI`). Nimetty vakio kertoo,
  mitä luku tarkoittaa, ja sen voi muuttaa yhdestä paikasta, kun
  esimerkiksi verokanta muuttuu.
- **Syöte on aina tekstiä, ja se tarkistetaan.** Muunna syöte heti
  luettaessa oikeaan tyyppiin ja käsittele mahdolliset muodot (pilkku,
  välilyönnit).
- **Raha kokonaislukuina tai `Decimal`-tyyppinä**, ei liukulukuina.
  Liukulukuja ei verrata yhtäsuuruusoperaattorilla `==`, vaan
  pyöristetään tai verrataan erotuksen itseisarvoa pieneen lukuun.
- **Anna työkalujen löytää virheet.** mypy ja ruff huomaavat
  tyyppivirheet ja kirjoitusvirheet nimissä ennen ajoa.

## Itsearviointi

- Osaat nimetä Pythonin perustyypit ja kertoa, minkä tyyppinen tulos
  on lausekkeilla `7 / 2`, `7 // 2` ja `"7" * 2`.
- Osaat ratkaista jakamiseen liittyviä tehtäviä operaattoreilla `//`
  ja `%`.
- Osaat lukea syötteen, muuntaa sen luvuksi ja tulostaa tuloksen
  muotoiltuna f-merkkijonolla.
- Osaat selittää, miksi rahaa ei lasketa liukuluvuilla.
- Osaat nimetä muuttujat ja vakiot kuvaavasti PEP 8:n mukaan.

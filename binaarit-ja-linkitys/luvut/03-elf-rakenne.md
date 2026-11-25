# ELF-tiedoston rakenne

ELF-tiedostolla on kaksi näkymää. *Osiot* (*sections*) ovat linkkerin
näkymä: nimettyjä paloja, kuten koodi, alustetut muuttujat ja
symbolitaulu, jotka linkkeri yhdistää samannimisiin paloihin muista
tiedostoista. *Segmentit* (*segments*, ohjelmaotsakkeet) ovat
lataajan näkymä: muistialueita, jotka kartoitetaan prosessiin
tietyillä oikeuksilla. Objektitiedostossa on vain osiot, jaetussa
kirjastossa ja ohjelmassa molemmat, ja lataaja tarvitsee vain
segmentit.

```{.dot otsikko="ELF-tiedoston kaksi näkymää: osiotaulu jakaa tiedoston nimettyihin osioihin, ohjelmaotsakkeet kokoavat samat tavut segmenteiksi oikeuksien mukaan"}
digraph {
  rankdir=LR; nodesep=0.12; ranksep=0.9;
  node [shape=box, style="filled", fontsize=10, height=0.3];
  edge [arrowsize=0.6];
  subgraph cluster_osiot {
    label="linkkerin näkymä: osiot"; color="#B8C4C8"; fontsize=10;
    text [label=".text", fillcolor="#E4DCF0"];
    rodata [label=".rodata", fillcolor="#EEF1F2"];
    data [label=".data", fillcolor="#F1E3CC"];
    bss [label=".bss (ei tavuja tiedostossa)", fillcolor="#F1E3CC", style="filled,dashed"];
    symtab [label=".symtab, .strtab", fillcolor="white"];
  }
  subgraph cluster_segmentit {
    label="lataajan näkymä: segmentit"; color="#B8C4C8"; fontsize=10;
    r0 [label="LOAD R: ELF-otsake, lataajan taulut", fillcolor="#EEF1F2"];
    rx [label="LOAD R E", fillcolor="#E4DCF0"];
    r1 [label="LOAD R", fillcolor="#EEF1F2"];
    rw [label="LOAD RW (MemSiz > FileSiz)", fillcolor="#F1E3CC"];
    ei [label="ei ladata muistiin", fillcolor="white", style="filled,dashed"];
  }
  text -> rx; rodata -> r1; data -> rw; bss -> rw; symtab -> ei;
  r0 -> text [style=invis];
}
```

## Mihin osioon muuttuja päätyy

Kääntäjä valitsee osion määrittelyn perusteella: onko kyse koodista,
vakiosta, alustetusta vai nollalla alustetusta muuttujasta. Esimerkin
tiedostossa on yksi kustakin:

```{.c tiedosto="esimerkit/03-osiot/main.c" osa="muuttujat"}
```

Symbolitaulusta (`objdump -t`) näkee kunkin symbolin osion. Funktion
sisäinen `static`-muuttuja saa kääntäjältä nimen, kuten
`valimuisti.0`, koska samannimisiä voi olla useassa funktiossa;
skripti poistaa päätteen:

```{.bash tiedosto="esimerkit/03-osiot/aja.sh" osa="symbolit"}
```

```{.tuloste tiedosto="esimerkit/03-osiot/odotettu" alkaen="== symbolit ja osiot" asti="valimuisti"}
```

Tavalliset osiot:

| Osio | Sisältö | Tila tiedostossa |
|------|---------|------------------|
| `.text` | konekieli | koko |
| `.text.startup` | `main` ja muu kerran ajettava koodi | koko |
| `.rodata` | vakiot, merkkijonoliteraalit | koko |
| `.data` | alustetut muuttujat | koko |
| `.bss` | nollalla alustetut muuttujat | ei tilaa, vain koko |
| `.symtab`, `.strtab` | symbolitaulu ja nimet | koko, `strip` poistaa |
| `.rela.text` | relokaatiot (luku 5) | koko |

`.bss` on tyyppiä `NOBITS`: tiedostoon tallennetaan vain koko, ja
lataaja varaa nollatun muistin. 16 kilotavun `puskuri` ei kasvata
tiedostoa lainkaan, mutta jos sen ensimmäinen alkio alustettaisiin
ykköseksi, koko taulukko siirtyisi `.data`-osioon ja tiedostoon.
Osioiden nimet ja tyypit (`readelf -S`):

```{.bash tiedosto="esimerkit/03-osiot/aja.sh" osa="osiot"}
```

```{.tuloste tiedosto="esimerkit/03-osiot/odotettu" alkaen="== osiot (main.o)" asti=".rodata PROGBITS"}
```

GCC jakaa osioita tarkemmin, kun siitä on hyötyä. `.text.startup`
erottaa kerran ajettavan koodin kuumasta koodista, ja
`.rodata.str1.1` sisältää merkkijonoliteraalit, jotka linkkeri voi
yhdistää: tunnus `str1.1` tarkoittaa, että osio koostuu
nollapäätteisistä yksitavuisten merkkien jonoista, joten samat jonot
eri tiedostoista voidaan tallentaa vain kerran. Valitsimet
`-ffunction-sections` ja `-fdata-sections` vievät jaon loppuun asti:
jokainen funktio ja muuttuja saa oman osionsa, ja linkkeri voi
valitsimella `--gc-sections` poistaa osiot, joihin mikään ei viittaa.

## Segmentit ja muistin oikeudet

Linkkeri kokoaa osiot segmenteiksi niiden oikeuksien mukaan. Koodi on
luettavaa ja suoritettavaa, vakiot pelkästään luettavia, muuttujat
luettavia ja kirjoitettavia. Ohjelmaotsakkeiden (`readelf -l`) lopussa
on taulukko, joka kertoo, mitkä osiot kuuluvat kuhunkin segmenttiin.
Skripti poimii siitä `LOAD`-segmentit:

```{.bash tiedosto="esimerkit/03-osiot/aja.sh" osa="segmentit"}
```

```{.tuloste tiedosto="esimerkit/03-osiot/odotettu" alkaen="== segmentit"}
```

Ensimmäinen pelkästään luettava segmentti sisältää ELF-otsakkeen ja
lataajan tarvitsemat taulut (dynaamiset symbolit, relokaatiot).
Segmenttejä on neljä, koska jokaisella sivulla on yhdet oikeudet:
kirjoitettava ja suoritettava muisti ei saa olla samalla sivulla
(W^X). Segmentit tasataan sivun kokoon (4096 tavua), ja niiden välissä
on tyhjää osoiteavaruutta, joka ei vie tilaa tiedostossa.

Muut ohjelmaotsakkeet ohjaavat lataajaa:

| Otsake | Merkitys |
|--------|----------|
| `PHDR` | ohjelmaotsakkeet itse muistissa |
| `INTERP` | dynaamisen linkkerin polku (luku 12) |
| `LOAD` | kartoitettava alue ja sen oikeudet |
| `DYNAMIC` | dynaaminen osio: riippuvuudet, liput (luku 7) |
| `NOTE` | koontitunniste, ABI-merkinnät |
| `GNU_EH_FRAME` | poikkeusten ja pinon purun hakutaulu |
| `GNU_STACK` | pinon oikeudet; `RW` ilman `E`:tä |
| `GNU_RELRO` | alue, joka suojataan kirjoitukselta käynnistyksen jälkeen |

`GNU_STACK`-otsakkeen puuttuminen tai `E`-lippu tekee pinosta
suoritettavan, mikä on vanhojen assembly-tiedostojen yleinen virhe:
kokoaja lisää merkinnän vain, jos tiedostossa on rivi
`.section .note.GNU-stack,"",@progbits`. Linkkeri varoittaa
(`missing .note.GNU-stack section implies executable stack`).

`GNU_RELRO` kattaa osiot, joita lataaja kirjoittaa vain
käynnistyksessä (`.init_array`, `.dynamic`, `.got`). Kun relokaatiot
on tehty, lataaja asettaa alueen pelkästään luettavaksi. Tämä on
*RELRO*-suojaus: hyökkääjä ei voi ylikirjoittaa funktio-osoitteita,
joita ohjelma käyttää kirjastokutsuihin.

## Tiedoston koko ja muistin koko

Kunkin segmentin otsakkeessa on kaksi kokoa: `FileSiz` (tavuja
tiedostossa) ja `MemSiz` (tavuja muistissa). Ne eroavat
kirjoitettavassa segmentissä, jossa `.bss` on lopussa:
esimerkkiohjelmassa `FileSiz` on noin 600 tavua ja `MemSiz` yli 16
kilotavua. Lataaja nollaa erotuksen. Siksi `.bss` on aina
kirjoitettavan segmentin viimeinen osio.

Koko tiedoston tila jakautuu osioihin, ja `size` näyttää yhteenvedon
Berkeley-muodossa: `text` (koodi ja vakiot), `data` ja `bss`.
Sulautetuissa järjestelmissä tämä on ensimmäinen komento, jolla
tarkistetaan, mahtuuko ohjelma muistiin: `text + data` kuluttaa
flash-muistia, `data + bss` RAM-muistia.

## Käytännössä

- **Älä alusta suuria taulukoita turhaan.** Nollalla alustettu
  taulukko on `.bss`:ssä eikä vie tilaa tiedostossa. Yksikin nollasta
  poikkeava alkio siirtää koko taulukon `.data`-osioon.
- **Merkitse vakiot `const`:iksi.** `const`-taulukko päätyy
  `.rodata`-osioon, jonka sivut jaetaan prosessien kesken ja jota ei
  voi vahingossa ylikirjoittaa. Sulautetuissa järjestelmissä se jää
  flash-muistiin eikä kuluta RAM-muistia.
- **Tarkista pinon oikeudet.** `readelf -lW ohjelma | grep GNU_STACK`
  ei saa näyttää `E`-lippua. Lisää assembly-tiedostoihin
  `.note.GNU-stack`-osio.
- **Poista käyttämätön koodi.** `-ffunction-sections
  -fdata-sections` ja linkkerin `--gc-sections` pienentävät ohjelmaa,
  kun kirjastosta käytetään vain osaa.

## Itsearviointi

- Osaat kertoa, mihin osioon funktio, vakio, alustettu muuttuja ja
  nollalla alustettu muuttuja päätyvät, myös `static`-muuttujat.
- Osaat selittää osioiden ja segmenttien eron ja lukea
  `readelf -l`:n osioiden ja segmenttien vastaavuustaulukon.
- Osaat selittää, miksi `.bss` ei vie tilaa tiedostossa ja miksi
  `FileSiz` ja `MemSiz` eroavat.
- Osaat kertoa, mitä `GNU_STACK` ja `GNU_RELRO` suojaavat.

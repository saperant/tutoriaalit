# Tyypit, lausekkeet ja syöte {.runko-tyypit}

Go on staattisesti ja vahvasti tyypitetty: jokaisella lausekkeella on
käännösaikana tunnettu tyyppi, eikä tyyppien välillä tehdä
implisiittisiä muunnoksia. Tyypit päätellään esittelyssä, joten niitä
kirjoitetaan harvoin näkyviin. Luku käy läpi perustyypit, muunnokset
ja vakiot, sitten tulostuksen ja lopuksi syötteen lukemisen
vakiosyötteestä, tiedostosta ja komentoriviltä.

## Perustyypit ja nolla-arvot

| Tyyppi | Kuvaus | Nolla-arvo |
|--------|--------|-----------|
| `bool` | totuusarvo | `false` |
| `int`, `uint` | alustan sanakoko (64-bittisellä 64 bittiä) | `0` |
| `int8`…`int64`, `uint8`…`uint64` | kiinteä koko | `0` |
| `byte`, `rune` | `uint8`:n ja `int32`:n nimet: tavu ja Unicode-koodipiste | `0` |
| `float32`, `float64` | IEEE 754 | `0` |
| `complex64`, `complex128` | kompleksiluku | `0` |
| `string` | muuttumaton tavujono, yleensä UTF-8 | `""` |
| `*T`, `[]T`, `map[K]V`, `chan T`, `func`, `interface` | viitetyypit | `nil` |

Muuttuja esitellään kolmella tavalla: `var x int` (nolla-arvo),
`var x = 3` (päätelty tyyppi) ja funktion sisällä lyhyesti `x := 3`.
Jokainen muuttuja saa nolla-arvon, joten alustamatonta muistia ei ole:

```{.go tiedosto="esimerkit/03-tyypit.go" osa="nolla"}
```

Indekseihin, pituuksiin ja laskureihin käytetään `int`-tyyppiä, vaikka
arvo ei voisi olla negatiivinen. Etumerkittömiä tyyppejä käytetään
bittioperaatioihin, tavuihin ja tiedostomuotoihin.

## Muunnokset ja ylivuoto

Eri tyyppejä ei voi sekoittaa laskutoimituksessa, vaikka molemmat
olisivat kokonaislukuja. Muunnos kirjoitetaan `T(x)`:

```{.go tiedosto="esimerkit/03-tyypit.go" osa="muunnokset"}
```

- Liukuluvun muunnos kokonaisluvuksi katkaisee kohti nollaa.
  Tyypittömän vakion `int(2.99)` kääntäjä hylkää, koska arvo ei mahdu
  tyyppiin tarkasti.
- Kokonaislukujen ylivuoto kiertää hiljaa (kahden komplementti), eikä
  sitä tarkisteta ajonaikana. Kun ylivuoto on mahdollinen, käytä
  `math/bits`-paketin funktioita tai tarkista rajat itse.
- Kapeampaan tyyppiin muunnettaessa ylimmät bitit katoavat.

Sama sääntö pätee omiin tyyppeihin. `time.Duration` on oma tyyppinsä,
jonka pohjatyyppi on `int64`, eikä sitä voi kertoa `int`-muuttujalla:

```{.go tiedosto="esimerkit/03-muunnos.ei-kaanny.go"}
```

```
invalid operation: viive * yritykset (mismatched types
time.Duration and int)
```

Tämä on hyödyllistä: yksiköt eivät sekoitu vahingossa. Vakio
`250 * time.Millisecond` kelpaa, koska tyypitön vakio `250` saa
tarvittavan tyypin.

## Rakenteet ja metodit lyhyesti

Omat tyypit käsitellään luvussa 7, mutta jo tämän luvun esimerkit
tarvitsevat niistä kaksi asiaa. *Rakenne* (`struct`) kokoaa nimettyjä
kenttiä yhdeksi tyypiksi. *Metodi* on funktio, jonka nimen edellä on
*vastaanottaja* eli arvo, jolle metodia kutsutaan; Pythonissa sama
parametri on `self`. Luokkaa ei ole: metodin voi määritellä mille
tahansa samassa paketissa nimetylle tyypille, myös kokonaisluvulle.

```{.go tiedosto="esimerkit/03-rakenne.go" osa="rakenne"}
```

```{.go tiedosto="esimerkit/03-rakenne.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/03-rakenne.odotettu"}
```

Koosteliteraali `Mittaus{...}` luo arvon, ja kenttään viitataan
pisteellä. Luku 5 kertoo, milloin vastaanottaja on arvo ja milloin
osoitin.

## Vakiot ja iota

Vakiot lasketaan käännösaikana. *Tyypittömät* vakiot (`1 << 10`)
lasketaan mielivaltaisella tarkkuudella ja saavat tyypin vasta
käyttöpaikassa. Lueteltu tyyppi tehdään omasta kokonaislukutyypistä ja
`iota`-laskurista, joka kasvaa vakiolohkon jokaisella rivillä:

```{.go tiedosto="esimerkit/03-tyypit.go" osa="vakiot"}
```

```{.go tiedosto="esimerkit/03-tyypit.go" osa="taso"}
```

```{.tuloste tiedosto="esimerkit/03-tyypit.odotettu"}
```

Go:ssa ei ole varsinaista `enum`-tyyppiä, eikä kääntäjä tarkista, että
`switch` kattaa kaikki arvot. Arvon tekstiesitys saadaan
`String`-metodilla, jonka `stringer`-työkalu osaa tuottaa:
`//go:generate stringer -type=Taso`.

## Tulostus ja muotoilu

`fmt`-paketin funktiot muodostavat kolme perhettä: `Print*` kirjoittaa
vakiotulosteeseen, `Sprint*` palauttaa merkkijonon ja `Fprint*`
kirjoittaa mihin tahansa `io.Writer`-rajapintaan (tiedosto,
verkkoyhteys, puskuri). `*ln`-muodot lisäävät välilyönnit ja rivinvaihdon,
`*f`-muodot käyttävät muotoilujonoa.

```{.go tiedosto="esimerkit/03-muotoilu.go" osa="verbit"}
```

| Koodi | Merkitys |
|-------|----------|
| `%v`, `%+v`, `%#v` | arvo oletusmuodossa, kenttien nimet, Go-syntaksina |
| `%T` | tyypin nimi |
| `%d`, `%x`, `%o`, `%b` | kokonaisluku eri kannoissa |
| `%f`, `%.2f`, `%e`, `%g` | liukuluku |
| `%s`, `%q` | merkkijono, lainattuna ja koodinvaihdoin |
| `%6d`, `%-6d`, `%06d` | leveys, vasen tasaus, etunollat |
| `%w` | virheen kääriminen (vain `fmt.Errorf`, luku 8) |

Tyyppi, jolla on metodi `String() string`, toteuttaa
`fmt.Stringer`-rajapinnan, ja `%v` käyttää sitä. Muotoilujonon ja
argumenttien yhteensopivuuden tarkistaa `go vet` (luku 12).

```{.tuloste tiedosto="esimerkit/03-muotoilu.odotettu"}
```

`strconv`-paketti muuntaa merkkijonoja ja lukuja ja palauttaa
virheen, joka kertoo syötteen ja syyn:

```{.go tiedosto="esimerkit/03-muotoilu.go" osa="strconv"}
```

Kirjoitus `fmt.Fprintf(os.Stdout, ...)` on sama kuin `fmt.Printf`.
Virheilmoitukset kirjoitetaan `os.Stderr`-virtaan:

```{.go tiedosto="esimerkit/03-muotoilu.go" osa="stderr"}
```

## Syötteen lukeminen

Rivipohjainen syöte luetaan `bufio.Scanner`-tyypillä. Seuraava ohjelma
laskee anturikohtaiset keskiarvot ja ohittaa virheelliset rivit:

```{.go tiedosto="esimerkit/03-syote.go"}
```

```{.tuloste tiedosto="esimerkit/03-syote.syote"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

Virhetulosteeseen kirjoitetaan `rivi 5: strconv.ParseFloat: parsing
"21,5": invalid syntax` ja `rivi 6: odotettiin 2 kenttää`.

- `Scanner` jakaa syötteen oletuksena riveiksi ja poistaa
  rivinvaihdot. Rivin enimmäispituus on oletuksena 64 kt; pidemmille
  riveille kutsutaan `Buffer`-metodia tai käytetään
  `bufio.Reader`-tyypin `ReadString`-metodia.
- `strings.Fields` jakaa tyhjän kohdalta ja ohittaa peräkkäiset
  välilyönnit.
- Kartan arvona on osoitin, jotta tilastoa voi päivittää paikallaan.
- Tulostusjärjestys on lajiteltu, koska kartan läpikäyntijärjestys
  vaihtelee ajosta toiseen.

## Tiedostot ja komentoriviliput

Komentorivityökalu saa syötteensä useimmiten tiedostosta ja asetuksensa
lipuista. Tiedosto avataan funktiolla `os.Open` (lukemiseen) tai
`os.Create` (kirjoittamiseen), ja se suljetaan itse. `os.File` ei
puskuroi, joten rivipohjainen luku ja kirjoitus kääritään
`bufio`-paketin tyyppeihin:

```{.go tiedosto="esimerkit/03-tiedosto.go" osa="kirjoita"}
```

```{.go tiedosto="esimerkit/03-tiedosto.go" osa="lue"}
```

`defer` siirtää kutsun funktion loppuun (luku 4), joten tiedosto
sulkeutuu kaikilla paluupoluilla. Pienen tiedoston voi lukea kerralla
funktiolla `os.ReadFile` ja kirjoittaa funktiolla `os.WriteFile`.

`flag`-paketti jäsentää liput. Jokainen lippu esitellään nimellä,
oletusarvolla ja ohjetekstillä, ja `flag.Parse` täyttää arvot.
Lippujen jälkeen tulevat argumentit saadaan funktioilla `flag.Args` ja
`flag.Arg`; jäsentämätön komentorivi on viipaleessa `os.Args`.

```{.go tiedosto="esimerkit/03-tiedosto.go" osa="main"}
```

```{.go tiedosto="esimerkit/03-tiedosto.go" osa="aja"}
```

Ajo komennolla `tiedosto -raja 21 mittaukset.txt` tulostaa:

```{.tuloste tiedosto="esimerkit/03-tiedosto.odotettu"}
```

Tiedostovirhe on tyyppiä `*fs.PathError`, jonka viesti kertoo
toiminnon, polun ja syyn. Syytä verrataan `errors.Is`-funktiolla
(luku 8), ei viestin tekstiä tutkimalla. Lippu `-h` tulostaa
ohjetekstit, ja tuntematon lippu lopettaa ohjelman paluuarvolla 2.

## Käytännössä

- **Tee nolla-arvosta hyödyllinen.** Suunnittele tyypit niin, että
  `var x T` on käyttövalmis. Silloin konstruktoria ei tarvita, ja
  tyyppiä voi käyttää rakenteen kenttänä ilman alustusta.
- **Oma tyyppi yksiköille ja tunnisteille.** `type Sentit int64`,
  `type AsiakasID string` ja `time.Duration` estävät sekoittamasta
  arvoja, joilla on sama pohjatyyppi. Muunnos on näkyvä ja ilmainen.
- **Rahaa ei liukuluvuilla.** Käytä kokonaislukuja pienimmässä
  yksikössä (sentit) tai desimaalikirjastoa.
- **Lyhyet nimet lyhyessä näkyvyydessä.** Go-tyyli suosii lyhyitä
  nimiä (`i`, `r`, `err`), kun muuttujan elinikä on muutama rivi, ja
  kuvaavia nimiä pakettitasolla.
- **`iota`-luettelon nolla-arvo.** Jos tyypin nolla-arvo ei saa olla
  kelvollinen arvo, aloita luettelo vakiolla `Tuntematon` tai
  `iota + 1`. Silloin alustamaton kenttä erottuu.
- **Virheilmoitukset `os.Stderr`-virtaan**, tulokset vakiotulosteeseen.
  Silloin ohjelmaa voi käyttää putkessa.
- **Tarkista kirjoitetun tiedoston `Close`.** Käyttöjärjestelmä voi
  ilmoittaa kirjoitusvirheestä vasta suljettaessa. Luetun tiedoston
  sulkemisvirheellä ei ole merkitystä, joten `defer f.Close()` riittää.
- **Puskuroi ja tyhjennä.** `bufio.Writer` kerää pienet kirjoitukset
  yhdeksi järjestelmäkutsuksi, mutta data on perillä vasta
  `Flush`-kutsun jälkeen.
- **Hinta.** `fmt`-funktiot käyttävät heijastusta ja `any`-parametreja,
  jotka voivat allokoida. Kuumassa silmukassa `strconv.AppendInt` ja
  `strings.Builder` ovat moninkertaisesti nopeampia.

## Itsearviointi

- Osaat kertoa Go:n perustyyppien nolla-arvot ja hyödyntää niitä.
- Osaat muuntaa tyyppejä eksplisiittisesti ja kertoa, mitä
  ylivuodossa ja katkaisussa tapahtuu.
- Osaat määritellä luetellun tyypin `iota`-vakioilla ja omalla
  pohjatyypillä.
- Osaat muotoilla tulostetta `fmt`-paketin muotoilukoodeilla ja tehdä
  tyypille `String`-metodin.
- Osaat lukea rivipohjaista syötettä `bufio.Scanner`-tyypillä ja
  käsitellä jäsennys- ja lukuvirheet.
- Osaat määritellä rakenteen ja sille metodin.
- Osaat lukea ja kirjoittaa tiedoston puskuroidusti, sulkea sen
  oikein ja jäsentää komentorivin liput `flag`-paketilla.

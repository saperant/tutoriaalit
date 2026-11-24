# Laiteohjelmistokuvien rakenne ja purku

Analyysi alkaa tiedostosta, josta ei tiedetä vielä mitään: onko se
ohjelma vai data, koodia vai pakattua, yksi kuva vai säiliö monesta
osasta. Ensimmäiset kysymykset ovat muotoa koskevia, ja niihin vastaa
muutama yleinen havainto: tiedoston alku, tavujen entropia ja
luettavat merkkijonot.

## Raaka binääri, ELF ja tekstimuodot

Sulautetun laitteen ohjelma esiintyy kolmessa päämuodossa. **Raaka
binääri** (`.bin`) on pelkkä kopio flash-muistin sisällöstä: ei
otsaketta, ei symboleita, vain koodi ja data siinä järjestyksessä kuin
ne ovat muistissa. Se ladataan laitteeseen tiettyyn osoitteeseen, ja
ilman sitä osoitetta tiedosto ei kerro, mihin se kuuluu. **ELF**
(`.elf`) on linkkerin tuottama muoto, jossa on osiot, symbolit ja
mahdollisesti virheenjäljitystieto; valmistaja käyttää sitä sisäisesti,
mutta harvoin jakaa sellaisenaan. **Intel HEX** (`.hex`) ja
**S-record** (`.srec`) ovat tekstimuotoja, joissa binääri on koodattu
heksana rivi riviltä osoitteineen ja tarkisteineen; niitä käytetään
ohjelmointilaitteissa.

Sama LT-100:n sovellus kaikissa muodoissa, ja muotojen tunnistus
tiedoston alusta:

```{.bash tiedosto="esimerkit/01-muodot/aja.sh" osa="muunnos"}
```

```{.python tiedosto="esimerkit/tyokalut/tunnista.py" osa="tunnista"}
```

```{.bash tiedosto="esimerkit/01-muodot/aja.sh" osa="tunnistus"}
```

```{.tuloste tiedosto="esimerkit/01-muodot/odotettu" osa="s2"}
```

ELF tunnistuu taikaluvusta `\x7fELF`, ja sen otsake kertoo
arkkitehtuurin (ARM) ja tulokohdan. Raaka binääri ei kerro itsestään
mitään, mutta Cortex-M:n kuvan voi tunnistaa: ensimmäiset neljä tavua
ovat pinon alkuosoite (RAM-alueella, tyypillisesti `0x2000....`) ja
seuraavat neljä Reset-käsittelijän osoite (pariton, koska Thumb).
`flash.bin` alkaa käynnistyslataimella, `sovellus.bin` sovelluksella;
molemmissa alku näyttää vektoritaululta. Päivityspaketti `.lt1` ei
täsmää mihinkään tunnettuun muotoon, joten sen taikaluku `LT1P` jää
tutkittavaksi (luku jatkuu alempana).

Intel HEX -rivi on `:LLAAAATT<data>CC`, jossa `LL` on datan pituus,
`AAAA` osoitteen alaosa, `TT` tietueen tyyppi ja `CC` tarkiste. Oma
jäsennin tarkistaa tarkisteen ja kokoaa osoitealueen:

```{.python tiedosto="esimerkit/tyokalut/ihex.py" osa="tietue"}
```

```{.tuloste tiedosto="esimerkit/01-muodot/odotettu" osa="s3"}
```

Tyypin 02 tai 04 tietue asettaa osoitteen yläosan, tyyppi 00 on dataa
ja tyyppi 01 päättää tiedoston. S-record on sama idea eri
kirjainkoodein (S0 otsikko, S1–S3 data osoitteen leveyden mukaan, S7–S9
loppu).

## Entropia ja merkkijonot

Kun muoto on selvä, seuraava kysymys on, mitä tiedosto sisältää.
*Shannonin entropia* mittaa tavujen satunnaisuutta: 0 bittiä tavua
kohden on pelkkää täytettä, 4–5 tekstiä, 5–6,5 konekieltä ja lähes 8
pakattua tai salattua dataa. Lohkoittain laskettu entropia paljastaa
tiedoston rakenteen ilman, että sisältöä tulkitaan:

```{.python tiedosto="esimerkit/tyokalut/entropia.py" osa="luokka"}
```

Luettavat merkkijonot ovat nopein vihje tarkoitukseen: virheilmoitukset,
komentojen nimet, versiotekstit ja muotoilumerkkijonot. `strings -n 12`
näyttää vähintään 12 merkin jonot ja `-t x` niiden siirtymän.

## Säiliömuodon purkaminen

LT-100:n päivityspaketti `.lt1` on säiliö, joka sisältää sovelluksen,
asetukset ja käyttöohjeen. Sen rakenne selvitetään samalla
työkalupakilla: heksavedos alusta, entropia, merkkijonot ja otsakkeen
sanat usealla tulkinnalla.

```{.bash tiedosto="esimerkit/02-paketti/aja.sh" osa="vedos"}
```

```{.tuloste tiedosto="esimerkit/02-paketti/odotettu" osa="s1"}
```

Entropia erottaa osat: alku on otsaketta ja matalan entropian dataa,
loppu korkean entropian lohko (pakattu ohje). Otsakkeen sanat
kymmenjärjestelmässä, kahtena puolisanana ja ASCIIna kertovat, mitkä
kentät ovat lukuja, mitkä osoitteita ja mitkä taikalukuja:

```{.tuloste tiedosto="esimerkit/02-paketti/odotettu" osa="s4"}
```

Taikaluku `LT1P`, versionumero `0x00020401` (2.4.1), laitetunnus,
osioiden määrä ja kolme osiokuvausta (tyyppi, osoite, pituus, tarkiste)
hahmottuvat. Pari kenttää näyttää tarkisteelta; mikä alue minkäkin
tarkiste on, selvitetään kokeilemalla jokaista kenttää jokaisen alueen
tarkistesummaa vastaan usealla algoritmilla. Jos kenttä on alueen
sisällä, se nollataan laskennan ajaksi:

```{.python tiedosto="esimerkit/tyokalut/tarkistehaku.py" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/02-paketti/odotettu" osa="s5"}
```

Otsakkeen tarkiste kattaa koko paketin (kenttä itse nollattuna), ja
kukin osiotarkiste kattaa oman osionsa; kolmannen osion tarkiste täsmää
vasta *puretulle* datalle, mikä vahvistaa, että osio on zlib-pakattu.
Kun rakenne on ymmärretty, se kirjoitetaan jäsentimeksi, joka purkaa
paketin ja kokoaa sen takaisin. Edestakainen muunnos (`pura` ja
`kokoa`) on vahvin tapa todeta, että muoto on ymmärretty oikein: jos
koottu tiedosto on tavulleen alkuperäinen, mitään ei jäänyt arvailun
varaan.

```{.python tiedosto="esimerkit/tyokalut/lt1.py" osa="jasenna"}
```

```{.tuloste tiedosto="esimerkit/02-paketti/odotettu" osa="s5"}
```

## Käytännössä

- **Aloita muodosta, älä koodista.** Tiedoston alku, entropia ja
  merkkijonot kertovat minuutissa, onko kyseessä ELF, raaka kuva vai
  säiliö ja mitä se karkeasti sisältää. Vasta sitten kannattaa avata
  disassembler.
- **Tarkista tarkisteet laskemalla, älä arvaamalla.** Tuntematon 32- tai
  16-bittinen kenttä on usein CRC. Kokeile tunnettuja algoritmeja ja
  alueita ohjelmallisesti; osuma kertoo sekä algoritmin että alueen.
- **Edestakainen muunnos todistaa ymmärryksen.** Kun jäsennin kokoaa
  tiedoston tavulleen takaisin, muoto on varmasti oikein. Tämä on myös
  paras regressiotesti omalle työkalulle.
- **Puolustus:** pelkkä CRC ei suojaa väärentämiseltä, koska hyökkääjä
  laskee sen uudelleen. Aitouden takaa vain allekirjoitus (luku 10 ja
  *Sulautettujen järjestelmien tietoturva*). Pakkaaminen ei ole
  salausta: korkea entropia voi olla kumpaa tahansa, ja sen erottaa
  kokeilemalla purkua.

## Itsearviointi

- Osaat tunnistaa ELF-, raaka-, Intel HEX- ja S-record-muodon tiedoston
  alusta ja tunnistaa Cortex-M:n vektoritaulun raa'asta kuvasta.
- Osaat lukea entropiakäyrää ja päätellä siitä täytteen, koodin ja
  pakatun tai salatun datan rajat.
- Osaat selvittää tuntemattoman säiliömuodon otsakkeen kentät ja
  tunnistaa tarkisteen laskemalla sen eri alueista.
- Osaat kirjoittaa muodolle jäsentimen ja todeta sen oikeaksi
  edestakaisella muunnoksella.

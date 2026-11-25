# Johdanto {.runko-johdanto}

Tietokone ei tunne lukuja vaan bittejä. Kokonaisluku, liukuluku,
merkki ja osoite ovat kaikki bittijonoja, joille ohjelma antaa
tulkinnan. Useimmiten tulkinnan ei tarvitse näkyä: `a + b` toimii.
Kun se ei toimi, vika on lähes aina tulkinnan rajoissa. Myynnin summa
muuttuu negatiiviseksi, kahden mittauksen keskiarvo on `nan`, rahasumma
heittää sentillä tai matriisilaskenta on kymmenen kertaa hitaampi kuin
pitäisi.

Tämä tutoriaali käy läpi, miten tietokone esittää lukuja ja laskee
niillä, ja ennen kaikkea, mitä siitä seuraa ohjelmoijalle:

- **Kokonaisluvut:** kiinteä leveys, kahden komplementti, ylivuoto ja
  sen havaitseminen, bittioperaatiot sekä jakolasku negatiivisilla
  luvuilla.
- **Liukuluvut:** IEEE 754 -standardin rakenne, pyöristys,
  erikoisarvot, virheen kertyminen ja algoritmit, jotka pitävät virheen
  kurissa.
- **Koneoppimisen lukumuodot:** bfloat16, FP8 ja int8-kvantisointi, eli
  miksi neuroverkko voi laskea 8 bitin luvuilla.
- **Stokastinen pyöristys:** satunnainen pyöristyssuunta, jolla matalan
  tarkkuuden laskenta pysyy keskimäärin oikeana.
- **Luvut muistissa:** matriisien ja tensorien järjestys, askeleet ja
  välimuistin vaikutus laskennan nopeuteen.

## Esitiedot ja rajaus

Tutoriaali olettaa, että lukija osaa C:tä (taito *C-kieli*) ja
Pythonin perusteet. C näyttää, mitä laitteisto tekee; Python ja NumPy
näyttävät, miten samat ilmiöt näkyvät korkeammalla tasolla. Taito
*Lukujen esitys ja kiinteän pilkun aritmetiikka* jatkaa tästä laitteistosuunnittelun
suuntaan ja taito *Suorituskyvyn analyysi ja optimointi* mittaamisen suuntaan.

## Bitit, tavut ja sanat

Bitti on 0 tai 1. Tavu on kahdeksan bittiä ja pienin osoitettava
muistin yksikkö. Prosessori käsittelee kerralla *sanan*, nykyisissä
suorittimissa 64 bittiä. Kokonaislukutyypit ovat 8, 16, 32 tai 64
bitin levyisiä, liukuluvut yleensä 32 tai 64 bitin.

Bittijonot kirjoitetaan yleensä heksadesimaalina: yksi
heksadesimaalinumero on neljä bittiä, joten tavu on kaksi numeroa
(`0x00`–`0xff`). Binääriesitys `0b1010` on C23:ssa ja Pythonissa
sallittu, mutta pitkät binääriluvut ovat hankalia lukea.

Monitavuinen arvo tallennetaan muistiin tavu kerrallaan. *Tavujärjestys*
(endianness) kertoo, missä järjestyksessä. x86-64 ja yleensä myös ARM
ovat *little-endian*: vähiten merkitsevä tavu on pienimmässä
osoitteessa. Verkkoprotokollat ja monet tiedostomuodot käyttävät
*big-endian*-järjestystä, joten tavut on järjestettävä, kun data
ylittää ohjelman rajan.

Seuraava ohjelma tulostaa muutaman arvon tavut muistin järjestyksessä:

```{.c tiedosto="esimerkit/01-tavut.c" osa="arvot"}
```

```{.tuloste tiedosto="esimerkit/01-tavut.odotettu"}
```

Tulosteesta näkyy jo koko tutoriaalin aihepiiri. Luku 1000 on
`0x000003e8`, ja sen vähiten merkitsevä tavu `e8` on ensimmäisenä. Luku
−1 on pelkkiä ykkösbittejä. Desimaaliluku 0,1 ei ole tarkka: sen
binääriesitys on päättymätön `0x999…`, joka katkaistaan ja pyöristetään
(`cd` ja `9a` lopussa). Merkkijono on UTF-8-tavuja ja loppunolla.

Python piilottaa leveyden: `int` kasvaa tarpeen mukaan, ja `float` on
aina 64-bittinen liukuluku.

```{.python tiedosto="esimerkit/01-arvot.py" osa="tavut"}
```

```{.tuloste tiedosto="esimerkit/01-arvot.odotettu"}
```

## Työkalut

Esimerkit käännetään GCC 14:llä ja Clang 20:llä C23-standardin
mukaisesti, varoitukset virheinä sekä AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa. Sanitoija pysäyttää ohjelman
esimerkiksi etumerkillisen ylivuodon kohdalla, joten tutoriaalin
virheelliset esimerkit näkyvät virheilmoituksina eivätkä satunnaisina
tuloksina. Optimoinnista riippuvat kokeet ajetaan esimerkkihakemiston
Makefilellä (`make mittaa` ja `make nopea`).

Python-esimerkit tarkistetaan ruffilla ja mypyn tiukalla tilalla, ja
ne käyttävät NumPyä. Hyödyllisiä apuvälineitä ovat lisäksi:

- `printf("%a", x)` ja Pythonin `float.hex()` tulostavat liukuluvun
  tarkasti heksadesimaalimuodossa.
- `decimal.Decimal(x)` näyttää liukuluvun tarkan desimaaliarvon.
- Compiler Explorer (godbolt.org) näyttää, millaisiksi käskyiksi
  kääntäjä muuttaa aritmetiikan.
- `gdb`:n komento `p/x` ja `x/8xb` näyttävät muuttujan bitit ja tavut.

## Lukuohje

Luvut 2–5 käsittelevät kokonaislukuja, luvut 6–9 liukulukuja, muita
murtolukumuotoja ja pyöristystä ja luvut 10–11 lukujen järjestämistä
muistiin. Lukusuorat ja bittikaaviot on piirretty samoilla laskuilla
kuin esimerkit (`make kuvat`). Jokainen
luku päättyy osioihin *Käytännössä*, jossa on ammattilaisten käytännöt
perusteluineen, ja *Itsearviointi*. Jos hallitset itsearvioinnin
väitteet, voit ohittaa luvun. Pikaopas kokoaa tärkeimmät säännöt ja
koodimallit.

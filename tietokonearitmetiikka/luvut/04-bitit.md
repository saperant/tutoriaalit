# Bittioperaatiot

Bittioperaatiot käsittelevät kokonaislukua bittijonona. Niillä
pakataan useita pieniä arvoja yhteen sanaan, luetaan laitteiden
rekistereitä ja protokollien otsakkeita sekä toteutetaan nopeita
erikoistapauksia, kuten kahden potenssin pyöristyksiä.

| Operaatio | C ja Python | Käyttö |
|-----------|-------------|--------|
| JA | a & b | maskaus: valitse bitit |
| TAI | a \| b | aseta bitit |
| poissulkeva TAI | a ^ b | vaihda bitit, vertaa |
| komplementti | ~a | käännä kaikki bitit |
| siirto vasemmalle | a << n | kerro $2^n$:llä, siirrä kenttä paikalleen |
| siirto oikealle | a >> n | jaa $2^n$:llä, hae kenttä |

## Liput

Joukko kyllä/ei-tietoja mahtuu yhteen kokonaislukuun, kun kullekin
annetaan oma bittinsä. C23:ssa luettelotyypille voi antaa pohjatyypin,
jolloin liput ovat oikean levyisiä:

```{.c tiedosto="esimerkit/04-liput.c" osa="liput"}
```

Neljä perusoperaatiota ovat asettaminen (`|`), poistaminen (`& ~`),
vaihtaminen (`^`) ja testaaminen (`&`):

```{.c tiedosto="esimerkit/04-liput.c" osa="operaatiot"}
```

```{.tuloste tiedosto="esimerkit/04-liput.odotettu"}
```

Testauksessa on kaksi eri kysymystä: onko *jokin* bitti päällä
(`(x & maski) != 0`) ja ovatko *kaikki* päällä
(`(x & maski) == maski`). Sekoittaminen on tyypillinen virhe
oikeustarkistuksissa.

## Kentät

Kenttä on peräkkäisten bittien ryhmä. Se luetaan siirtämällä kenttä
alimpiin bitteihin ja maskaamalla loput pois:

```{.c tiedosto="esimerkit/04-otsake.c" osa="kentta"}
```

IPv4-otsakkeen ensimmäisessä 32-bittisessä sanassa on versio,
otsakkeen pituus, palveluluokka (DSCP), ruuhkailmoitus (ECN) ja
paketin kokonaispituus. Verkosta luetut tavut kootaan sanaksi
siirroilla, jolloin koneen tavujärjestyksellä ei ole merkitystä:

```{.c tiedosto="esimerkit/04-otsake.c" osa="tavut"}
```

```{.tuloste tiedosto="esimerkit/04-otsake.odotettu"}
```

![Esimerkin sanat kenttinä. Bitit numeroidaan oikealta alkaen nollasta,
joten kentän siirtomäärä on sen alimman bitin numero ja maskissa on
kentän leveyden verran ykkösiä.](kuvat/bittikentat.png){width=100%}

Näyttöjen RGB565-pikselissä punaiselle ja siniselle on viisi bittiä ja
vihreälle kuusi, koska silmä erottaa vihreän sävyjä tarkimmin.
Pakkauksessa alimmat bitit hylätään. Purussa ylimmät bitit toistetaan
alimpiin, jotta suurin arvo `0x1f` laajenee arvoksi 255 eikä 248:
valkoinen pysyy valkoisena. Kuvan alempi rivi on oranssi pikseli
(255, 128, 0), jonka vihreä kanava palaa arvona 130.

```{.c tiedosto="esimerkit/04-rgb565.c" osa="pakkaus"}
```

```{.tuloste tiedosto="esimerkit/04-rgb565.odotettu"}
```

C:n bittikentät (`unsigned r : 5;` rakenteessa) näyttävät
houkuttelevilta, mutta niiden järjestys sanan sisällä on toteutuksen
määrittelemä. Laitteiden ja protokollien kentät luetaan siksi siirroilla
ja maskeilla.

## Siirtojen säännöt

Siirroissa on kolme sudenkuoppaa. Ensimmäinen: **siirto, joka on
vähintään tyypin leveys, on määrittelemätön.** `1u << 32` ei ole nolla.
x86-64 käyttää siirtomäärästä vain viittä alinta bittiä, joten tulos on
käytännössä `1u << 0` eli 1. Maskin muodostus `(1u << leveys) - 1`
toimii siksi vain leveyksillä 0–31:

```{.c tiedosto="esimerkit/04-siirto.kaatuu.c" osa="maski"}
```

```text
runtime error: shift exponent 32 is too large for 32-bit type
'unsigned int'
```

Toinen: **negatiivisen luvun siirto oikealle** on toteutuksen
määrittelemä. GCC ja Clang tekevät aritmeettisen siirron
(etumerkkibitti kopioituu), mutta tulos pyöristyy kohti miinus
ääretöntä: `-7 >> 1` on −4, kun taas `-7 / 2` on −3.

Kolmas: **negatiivisen luvun siirto vasemmalle** ja siirto, jonka tulos
ei mahdu etumerkilliseen tyyppiin, ovat määrittelemättömiä. Bittejä
siirretään siksi etumerkittömissä tyypeissä.

Kokonaislukujen ylennys lisää yllätyksiä: `uint8_t`-arvo muuttuu
`int`:ksi ennen operaatiota, joten `~x` tuottaa negatiivisen `int`-luvun
eikä 8-bittistä tulosta. Siksi esimerkeissä tulos muunnetaan takaisin
(`(uint8_t)~HALLINTA`).

## Bittikikat ja `<stdbit.h>`

Monet usein tarvitut bittitason funktiot ovat lyhyitä, mutta helppo
kirjoittaa väärin:

```{.c tiedosto="esimerkit/04-kikat.c" osa="kikat"}
```

`x & (x - 1)` poistaa alimman ykkösbitin. Jos tulos on nolla, bittejä
oli yksi, eli luku on kahden potenssi. Tasaus ylöspäin lisää
`tasaus - 1` ja nollaa alimmat bitit. Muistinvaraajat ja
DMA-puskurit tarvitsevat tätä jatkuvasti.

C23 standardoi kääntäjien sisäiset funktiot otsakkeeseen
`<stdbit.h>`: bittien laskeminen, nollien laskeminen alusta ja lopusta
sekä kahden potenssiin pyöristäminen. Ne kääntyvät suoraan
prosessorin käskyiksi (`popcnt`, `lzcnt`, `tzcnt`).

```{.c tiedosto="esimerkit/04-kikat.c" osa="stdbit"}
```

```{.tuloste tiedosto="esimerkit/04-kikat.odotettu"}
```

Rengaspuskurin koko kannattaa valita kahden potenssiksi. Silloin
indeksi saadaan maskilla, joka on yksi käsky, ja kiertyvä
kirjoituslaskuri toimii suoraan (luku 3).

## Käytännössä

- **Nimeä maskit ja siirrot.** `kentta(sana, 18, 6)` tai nimetty vakio
  `DSCP_SIIRTO` on luettavampi kuin `(w >> 18) & 0x3f`, ja nimen voi
  tarkistaa datalehdestä tai standardista.
- **Bittioperaatiot etumerkittömillä tyypeillä.** Kaikki siirtojen
  määrittelemättömät tapaukset liittyvät etumerkillisiin tyyppeihin tai
  liian suuriin siirtomääriin.
- **Kokoa monitavuiset arvot siirroilla.** `memcpy` rakenteeseen tai
  `*(uint32_t *)p` riippuu tavujärjestyksestä ja tasauksesta. Siirroilla
  koottu koodi on siirrettävää, ja kääntäjä optimoi sen yhdeksi
  lataukseksi ja tavujen kääntökäskyksi.
- **Vältä C:n bittikenttiä ulkoisissa muodoissa.** Bittikenttä sopii
  ohjelman sisäiseen tiiviiseen rakenteeseen, ei rekisteriin tai
  tiedostomuotoon.
- **Käytä `<stdbit.h>`-funktioita.** Ne ovat testattuja ja kääntyvät
  aina yhdeksi käskyksi. Itse kirjoitettu silmukka nopeutuu vain, jos
  kääntäjä sattuu tunnistamaan sen.
- **Älä optimoi tavallista aritmetiikkaa biteillä.** `x * 8`, `x / 4`
  ja `x % 16` etumerkittömillä tyypeillä kääntyvät siirroiksi ja
  maskeiksi itsestään. Kirjoita se, mitä tarkoitat.

## Itsearviointi

- Osaat asettaa, poistaa, vaihtaa ja testata bittilippuja ja erottaa
  "jokin päällä" ja "kaikki päällä" -tarkistukset.
- Osaat lukea ja kirjoittaa bittikenttiä siirroilla ja maskeilla, kuten
  IPv4-otsakkeen tai RGB565-pikselin.
- Osaat luetella siirtojen määrittelemättömät ja toteutuksen
  määrittelemät tapaukset.
- Osaat tasata koon kahden potenssiin ja käyttää `<stdbit.h>`-funktioita.

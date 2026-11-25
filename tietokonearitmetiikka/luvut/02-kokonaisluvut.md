# Kokonaisluvut bitteinä

$n$ bitin kokonaislukutyypillä on $2^n$ eri bittikuviota. Kuvioiden
tulkinta on sopimus. Etumerkittömässä (unsigned) tulkinnassa kuvio on
tavallinen binääriluku väliltä $0 \ldots 2^n-1$. Etumerkillisessä
(signed) tulkinnassa puolet kuvioista on negatiivisia lukuja. Lähes
kaikki laitteistot ja C23-standardi käyttävät tähän *kahden
komplementtia*.

## Kahden komplementti

Kahden komplementissa ylimmän bitin paino on negatiivinen: $n$-bittinen
kuvio $b_{n-1} \ldots b_0$ tarkoittaa lukua

$$-b_{n-1} 2^{n-1} + \sum_{i=0}^{n-2} b_i 2^i .$$

Esimerkiksi 8 bitissä `10000000` on −128 ja `11111111` on
−128 + 127 = −1. Arvoalue on $-2^{n-1} \ldots 2^{n-1}-1$: negatiivisia
on yksi enemmän kuin positiivisia.

```{.c tiedosto="esimerkit/02-komplementti.c" osa="tulkinnat"}
```

```{.tuloste tiedosto="esimerkit/02-komplementti.odotettu"}
```

Tulkinnat hahmottaa helpoimmin ympyrällä. Kun bittikuvioon lisätään
yksi, siirrytään ympyrällä askel myötäpäivään, ja viimeisen kuvion
jälkeen tulee taas ensimmäinen. Etumerkitön ja etumerkillinen tulkinta
ovat sama ympyrä, jonka numerointi katkeaa eri kohdasta:

![Neljän bitin kuviot ympyrällä. Sisäkehällä on etumerkitön arvo ja
ulkokehällä kahden komplementin arvo; sävytetyn puoliskon ylin bitti on
1. Katkoviivat ovat kohdat, joissa tulkinta vuotaa
yli.](kuvat/lukuympyra.png){width=58%}

Negatiivinen luku $-k$ on siis sama kuvio kuin etumerkitön $2^n - k$:
−1 ja 15 ovat neljässä bitissä molemmat `1111`. Kahden komplementin etu
on, että yhteen-, vähennys- ja kertolasku ovat
bittitasolla samat kuin etumerkittömillä luvuilla: summain ei tiedä,
kumpaa tulkintaa ohjelma käyttää. Vastaluku saadaan kääntämällä bitit ja
lisäämällä yksi:

```{.c tiedosto="esimerkit/02-komplementti.c" osa="vastaluku"}
```

Muunnos etumerkillisestä etumerkittömäksi on C:ssä aina määritelty:
tulos on arvo modulo $2^n$, joten bitit säilyvät. Muunnos toiseen
suuntaan, kun arvo ei mahdu, on toteutuksen määrittelemä; GCC ja Clang
säilyttävät bitit. C23 teki kahden komplementin pakolliseksi mutta jätti
tämän säännön ennalleen. Muunnoksen kirjoittaminen näkyviin
(`(uint8_t)x`) kertoo lukijalle, että bittien uudelleentulkinta on
tarkoituksellista.

Kaventava muunnos, esimerkiksi `int32_t`-arvon sijoitus
`int16_t`-muuttujaan, pudottaa ylimmät bitit pois: lukuympyrä
vaihtuu pienempään, ja arvo 40 000 muuttuu arvoksi −25 536. Kääntäjä ei
varoita tästä oletuksena. Valitsin `-Wconversion` löytää hiljaiset
kavennukset, ja ulkoa tuleva arvo tarkistetaan rajoja vasten ennen
sijoitusta.

## Etumerkki ja vertailut

C muuntaa lausekkeen operandit yhteiseen tyyppiin. Kun `int` ja
`size_t` kohtaavat, `int` muutetaan etumerkittömäksi, ja −1 muuttuu
suurimmaksi mahdolliseksi luvuksi. Siksi seuraava tarkistus päästää
negatiivisen siirtymän läpi, vaikka sen pitäisi hylätä:

```{.c tiedosto="esimerkit/02-etumerkki.ei-kaanny.c" osa="vertailu"}
```

```text
error: comparison of integer expressions of different signedness:
'int' and 'size_t' {aka 'long unsigned int'} [-Werror=sign-compare]
```

Varoitus `-Wsign-compare` (osa `-Wextra`-joukkoa) löytää tämän. Oikea
korjaus tarkistaa negatiivisuuden ensin ja muuntaa vasta sitten.
Muunnoksen lisääminen pelkästään varoituksen hiljentämiseksi
(`(size_t)siirtyma < koko` ilman ensimmäistä ehtoa) säilyttää virheen.

## Etumerkin laajennus

Kun kapea etumerkillinen arvo levennetään, ylin bitti kopioidaan uusiin
bitteihin (*sign extension*). Kääntäjä tekee tämän automaattisesti,
kun `int8_t` muunnetaan `int32_t`:ksi. Laitteiden rekistereissä on
kuitenkin usein epätavallisen levyisiä kenttiä. Esimerkiksi
kiihtyvyysanturi antaa 12-bittisen kahden komplementin arvon 16-bittisen
rekisterin alaosassa. Laajennus on tehtävä itse:

```{.c tiedosto="esimerkit/02-laajennus.c" osa="laajennus"}
```

```{.tuloste tiedosto="esimerkit/02-laajennus.odotettu"}
```

Ehdoton XOR-ja-vähennys-temppu välttää haarautumisen ja toimii kaikilla
leveyksillä 1–32. Kentän ulkopuoliset bitit (rivin `0xf123` yläosa)
maskataan pois ensin, koska anturi ei lupaa niiden olevan nollia.

## Python ja NumPy

Pythonin `int` on rajaton: `2**100` on tarkka. Kun ohjelma käsittelee
kiinteän leveyden dataa, kuten tiedostomuotoja, verkkoprotokollia tai
laitteiden rekistereitä, leveys on emuloitava. Se tehdään maskeilla ja
`int.from_bytes`- ja `int.to_bytes`-metodeilla, joille annetaan
`signed=True`, kun tulkinta on etumerkillinen. NumPyn taulukoilla taas
on kiinteä leveys kuten C:ssä (`np.int32`, `np.uint8`), mikä tulee
vastaan luvussa 3.

## Käytännössä

- **Valitse tyyppi arvoalueen mukaan.** Kokoille ja indekseille
  `size_t`, laskureille ja määrille `int64_t`, protokollien ja
  rekisterien kentille tarkan leveyden tyypit (`uint16_t`). `int` on
  hyvä vain, kun arvoalue on varmasti pieni.
- **Etumerkittömät tyypit bittikuvioille, etumerkilliset luvuille.**
  Bittioperaatiot ja siirrot ovat yksiselitteisiä etumerkittömillä
  tyypeillä. Etumerkitön tyyppi ei kuitenkaan ole keino estää
  negatiivisia arvoja: `size_t n = -1` kääntyy ja on suuri luku.
- **Älä sekoita etumerkillisiä ja etumerkittömiä vertailuissa.** Pidä
  `-Wall -Wextra -Werror` päällä ja korjaa varoitus logiikalla, älä
  muunnoksella.
- **Laajenna etumerkki heti, kun luet laitteelta.** Muunna raakabitit
  tavalliseksi etumerkilliseksi luvuksi ajurin rajalla, jotta muu
  ohjelma ei käsittele 12-bittisiä kuvioita.
- **Tavujärjestys rajapinnoissa.** Kokoa monitavuiset kentät tavuista
  siirroilla (luku 4), älä kopioi rakennetta muistiin sellaisenaan:
  silloin koodi toimii kaikilla tavujärjestyksillä.

## Itsearviointi

- Osaat muuntaa luvun kahden komplementin bittikuvioksi ja takaisin
  ja kertoa $n$-bittisen tyypin arvoalueen.
- Osaat selittää, miksi `-1 < sizeof(x)` on C:ssä epätosi ja miten
  vertailu kirjoitetaan oikein.
- Osaat laajentaa $n$-bittisen kentän etumerkin ilman haarautumista.
- Osaat kertoa, miten Pythonin `int` eroaa C:n kokonaislukutyypeistä ja
  miten kiinteä leveys emuloidaan Pythonissa.

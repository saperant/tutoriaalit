# Jakolasku ja kääntäjän muunnokset

Yhteen-, vähennys- ja kertolasku ovat kokonaisluvuilla yksiselitteisiä.
Jakolaskussa on valittava, miten osamäärä pyöristetään, ja kielet
valitsevat eri tavoin. Jakolasku on myös laitteistossa hidas:
64-bittinen jakokäsky vie kymmeniä kellojaksoja, kun kertolasku vie
muutaman. Siksi kääntäjät korvaavat vakiolla jakamisen kertolaskulla.

## Katkaisu vai lattia

C, C++, Java, Rust ja Go katkaisevat osamäärän kohti nollaa. Jäännös
saa jaettavan etumerkin, jotta `(a / b) * b + a % b == a` pätee aina:

```{.c tiedosto="esimerkit/05-jako.c" osa="c"}
```

Python ja Ruby pyöristävät osamäärän kohti miinus ääretöntä
(*lattiajako*). Jäännös saa jakajan etumerkin, joten `x % n` on aina
välillä $0 \ldots n-1$, kun $n > 0$:

```{.python tiedosto="esimerkit/05-lattiajako.py" osa="python"}
```

```{.tuloste tiedosto="esimerkit/05-lattiajako.odotettu"}
```

![Osamäärä ja jäännös jakajalla 3. Katkaiseva jako on symmetrinen
nollan suhteen, joten osamäärä 0 kattaa viisi arvoa ja jäännöksen
etumerkki vaihtuu. Lattiajaossa portaat ja jäännöksen jakso jatkuvat
samanlaisina nollan yli.](kuvat/jako.png){width=92%}

Ero tulee vastaan, kun negatiivinen arvo kuvataan jaksolliseen
alueeseen: kellonajat, kulmat, viikonpäivät ja rengaspuskurin indeksit.
Kello 00.15 miinus 45 minuuttia on −30 minuuttia. C:n `%` antaa −30,
mutta vuorokauden aika on 23.30 edellisenä päivänä. C:ssä
lattiajako kirjoitetaan itse:

```{.c tiedosto="esimerkit/05-jako.c" osa="lattia"}
```

```{.tuloste tiedosto="esimerkit/05-jako.odotettu"}
```

Kattojako (pyöristys ylöspäin) tarvitaan, kun lasketaan sivujen,
pakettien tai lohkojen määrää. Positiivisille luvuille se on
`(a + b - 1) / b`:

```{.c tiedosto="esimerkit/05-jako.c" osa="katto"}
```

Kaava voi ylivuotaa, jos `a` on lähellä tyypin ylärajaa. Turvallinen
muoto on `a / b + (a % b != 0)`.

## Ylivuotava jakolasku

Jakolaskussa on kaksi määrittelemätöntä tapausta: jako nollalla ja
pienimmän negatiivisen luvun jakaminen luvulla −1, koska tulos
$2^{31}$ ei mahdu `int`-tyyppiin. Jälkimmäinen kaataa x86-64:llä
ohjelman samalla poikkeuksella kuin nollalla jako (`SIGFPE`).

```{.c tiedosto="esimerkit/05-jako-ylivuoto.kaatuu.c" osa="jako"}
```

```text
runtime error: division of -2147483648 by -1 cannot be represented
in type 'int'
```

## Kertolasku jakolaskun tilalla

Kun jakaja on vakio, kääntäjä laskee käänteisluvun kiinteän pilkun
lukuna ja korvaa jaon kertolaskulla ja siirrolla. Kymmenellä jako
32-bittisillä etumerkittömillä luvuilla on kertolasku luvulla
$\lceil 2^{35} / 10 \rceil$ = `0xCCCCCCCD` ja siirto 35 bittiä oikealle:

```{.c tiedosto="esimerkit/05-vakiojako.c" osa="kymmenella"}
```

Kertoimen ja siirron valinta takaa, että pyöristysvirhe ei koskaan
muuta tulosta. Esimerkki tarkistaa sen laajalla otoksella:

```{.tuloste tiedosto="esimerkit/05-vakiojako.odotettu"}
```

Kahden potenssilla jako on etumerkittömille luvuille pelkkä siirto.
Etumerkillisille kääntäjä lisää korjauksen, koska siirto pyöristää
kohti miinus ääretöntä ja jakolasku kohti nollaa:

```{.c tiedosto="esimerkit/05-vakiojako.c" osa="siirrot"}
```

Muunnoksia ei kannata tehdä käsin. Kääntäjä tekee ne joka tapauksessa,
ja käsin kirjoitettu siirto on väärin negatiivisilla luvuilla. Käsin
tehty muunnos on perusteltu vain, kun jakaja on ajonaikainen mutta
pysyy samana pitkään. Tällöin kirjasto kuten libdivide laskee kertoimen
kerran.

## Käytännössä

- **Tiedä kielen pyöristyssääntö.** Kun algoritmi siirretään Pythonista
  C:hen tai päinvastoin, `//` ja `%` negatiivisilla luvuilla muuttavat
  merkitystään. Kirjoita testi, jossa on negatiivinen syöte.
- **Jaksolliset arvot lattiajäännöksellä.** Kellonajat ja indeksit
  normalisoidaan välille $0 \ldots n-1$ funktiolla, joka korjaa C:n
  jäännöksen etumerkin.
- **Tarkista jakaja ulkoisesta syötteestä.** Nolla ja `INT_MIN / -1`
  kaatavat ohjelman. Keskiarvon nimittäjä tarkistetaan ennen jakoa.
- **Kirjoita jakolasku jakolaskuna.** Kääntäjä muuntaa vakiolla jaon
  kertolaskuksi ja kahden potenssin siirroksi. Etumerkittömät tyypit
  tuottavat yksinkertaisimman koodin, jos arvo ei voi olla
  negatiivinen.
- **Pyöristä tietoisesti.** Rahan jakaminen osiin (esimerkiksi
  kuukausierät) pyöristää jokaisessa osassa. Jäljelle jäävä sentti
  lisätään viimeiseen erään, jotta osien summa on alkuperäinen.

## Itsearviointi

- Osaat ennustaa `/`- ja `%`-operaattorien tuloksen negatiivisilla
  luvuilla C:ssä ja Pythonissa.
- Osaat kirjoittaa lattiajaon, lattiajäännöksen ja kattojaon C:llä
  ylivuototurvallisesti.
- Osaat nimetä jakolaskun kaksi määrittelemätöntä tapausta.
- Osaat selittää, miten kääntäjä korvaa vakiolla jaon kertolaskulla.

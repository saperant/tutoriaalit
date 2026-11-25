# Tapahtumat ja todennäköisyys

Todennäköisyys on luku nollan ja yhden väliltä, joka kertoo, kuinka
usein tapahtuma sattuu, kun koe toistetaan monta kertaa. Tämä luku
esittelee laskusäännöt ja kaksi tapaa laskea: tarkasti luettelemalla
ja likimäärin simuloimalla.

## Otosavaruus ja aksioomat

Kokeen kaikki mahdolliset tulokset muodostavat *otosavaruuden*
$\Omega$, ja *tapahtuma* on sen osajoukko. Kolmogorovin aksioomien
mukaan

1. $P(A) \ge 0$ jokaiselle tapahtumalle,
2. $P(\Omega) = 1$ ja
3. erillisille tapahtumille $P(A \cup B) = P(A) + P(B)$.

Kaikki muut säännöt seuraavat näistä. Tärkeimmät ovat komplementti
$P(\bar A) = 1 - P(A)$ ja yhdiste
$P(A \cup B) = P(A) + P(B) - P(A \cap B)$.

Jos tulokset ovat yhtä todennäköisiä, todennäköisyys on suotuisien
tulosten osuus: $P(A) = |A| / |\Omega|$. Silloin laskeminen on
kombinatoriikkaa. Kahden nopan summa lasketaan luettelemalla kaikki 36
paria, ja `Fraction` pitää tuloksen tarkkana:

```{.python tiedosto="esimerkit/02-noppa.py" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/02-noppa.odotettu" rivit="1-4"}
```

Komplementti on usein helpoin reitti: ”vähintään yksi” on vaikea
laskea suoraan, mutta ”ei yhtään” on yksinkertainen tulo. Johdannon
simulaatio antoi samalle todennäköisyydelle frekvenssit 0,4800,
0,5147 ja 0,5175: ne lähestyvät laskettua arvoa 0,5177, mutta sadalla
toistolla virhe on vielä useita prosenttiyksiköitä. Luvussa *Monte
Carlo -menetelmät* katsotaan, miksi virhe pienenee hitaasti, kuten
$1/\sqrt{n}$.

## Simulointi ja siemen

Jokainen tämän tutoriaalin luku tarkistaa kaavansa simuloimalla, joten
simuloinnin perusväline esitellään heti. NumPyn `default_rng(siemen)`
luo *generaattorin*. Se on olio, joka tuottaa satunnaisilta näyttäviä
lukuja laskemalla ne sisäisestä tilastaan. Tilan alkuarvo johdetaan
siemenestä, joten sama siemen tuottaa saman lukujonon:

```{.python tiedosto="esimerkit/02-siemen.py" osa="siemen"}
```

```{.tuloste tiedosto="esimerkit/02-siemen.odotettu"}
```

Ilman siementä (`default_rng()`) tila alustetaan käyttöjärjestelmän
satunnaisuudesta ja jokainen ajo on erilainen. Kiinteä siemen tekee
simulaatiosta toistettavan: virhe voidaan toistaa ja tulos testata.
Siemen ei tee tuloksesta ”oikeampaa”. Toisella siemenellä luvut
poikkeavat hieman, ja poikkeamien suuruus on juuri se epävarmuus, jota
myöhemmät luvut opettavat arvioimaan. Generaattorien sisäinen
toiminta ja rinnakkaiset satunnaislukuvirrat käsitellään luvussa
*Satunnaislukugeneraattorit ja otanta*.

## Syntymäpäiväongelma ja törmäykset

Kuinka monta henkilöä tarvitaan, jotta kahdella on 50 %:n
todennäköisyydellä sama syntymäpäivä? Vastaus on yllättävän pieni,
koska pareja on paljon. Lasketaan komplementti: kaikki eri päivinä.

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/02-syntymapaivat.odotettu" rivit="1-3"}
```

Simulointi antaa saman tuloksen:

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/02-syntymapaivat.odotettu" rivit="4-4"}
```

Sama ongelma on ohjelmoinnissa joka päivä: satunnaisesti valitut
tunnisteet, hajautusarvot ja tiivisteet törmäävät paljon aiemmin kuin
arvojen määrä antaisi olettaa. Törmäysriski kasvaa 50 %:iin, kun
tunnisteita on noin $\sqrt{2 d \ln 2}$ kappaletta $d$ mahdollisesta:

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="tunnisteet"}
```

```{.tuloste tiedosto="esimerkit/02-syntymapaivat.odotettu" rivit="5-"}
```

32-bittinen satunnainen tunniste ei siis riitä edes sadalle tuhannelle
riville. 128-bittinen UUID riittää käytännössä aina.

## Käytännössä

- **Laske komplementin kautta.** ”Vähintään yksi” on lähes aina helpompi
  laskea muodossa $1 - P(\text{ei yhtään})$.
- **Tarkista kaava luettelemalla tai simuloimalla.** Pienen tapauksen
  tarkka luettelo ja suuren tapauksen simulaatio paljastavat väärin
  valitun kaavan ennen kuin se päätyy päätöksiin.
- **Käytä tarkkaa aritmetiikkaa, kun voit.** `Fraction` ja kokonaisluvut
  eivät pyöristä; liukuluvut kuuluvat simulaatioihin ja suuriin
  lukuihin.
- **Mitoita satunnaiset tunnisteet syntymäpäiväongelmalla.** Bittejä
  tarvitaan kaksinkertaisesti tunnisteiden määrän logaritmiin nähden,
  ja reilusti lisää varmuusmarginaaliksi.

## Itsearviointi

- Osaat määritellä otosavaruuden ja tapahtuman sekä käyttää
  komplementti- ja yhdistesääntöä.
- Osaat laskea todennäköisyyden luettelemalla ja tarkistaa sen
  simuloimalla.
- Osaat tehdä simulaatiosta toistettavan generaattorioliolla ja
  siemenellä.
- Osaat arvioida satunnaisten tunnisteiden törmäysriskin
  syntymäpäiväongelman avulla.

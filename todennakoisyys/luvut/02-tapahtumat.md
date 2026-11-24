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

```{.tuloste tiedosto="esimerkit/02-noppa.odotettu"}
```

Komplementti on usein helpoin reitti: ”vähintään yksi” on vaikea
laskea suoraan, mutta ”ei yhtään” on yksinkertainen tulo. Simulaation
frekvenssi lähestyy laskettua arvoa, mutta sadalla toistolla virhe on
vielä useita prosenttiyksiköitä. Luvussa *Monte Carlo* katsotaan, miksi
virhe pienenee hitaasti, kuten $1/\sqrt{n}$.

## Syntymäpäiväongelma ja törmäykset

Kuinka monta henkilöä tarvitaan, jotta kahdella on 50 %:n
todennäköisyydellä sama syntymäpäivä? Vastaus on yllättävän pieni,
koska pareja on paljon. Lasketaan komplementti: kaikki eri päivinä.

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="tarkka"}
```

Simulointi antaa saman tuloksen:

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="simulointi"}
```

Sama ongelma on ohjelmoinnissa joka päivä: satunnaisesti valitut
tunnisteet, hajautusarvot ja tiivisteet törmäävät paljon aiemmin kuin
arvojen määrä antaisi olettaa. Törmäysriski kasvaa 50 %:iin, kun
tunnisteita on noin $\sqrt{2 d \ln 2}$ kappaletta $d$ mahdollisesta:

```{.python tiedosto="esimerkit/02-syntymapaivat.py" osa="tunnisteet"}
```

```{.tuloste tiedosto="esimerkit/02-syntymapaivat.odotettu"}
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
- Osaat arvioida satunnaisten tunnisteiden törmäysriskin
  syntymäpäiväongelman avulla.

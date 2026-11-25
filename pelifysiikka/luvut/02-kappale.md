# Jäykän kappaleen tila

*Jäykkä kappale* ei muuta muotoaan: sen kahden pisteen etäisyys pysyy
samana, liikkui kappale miten tahansa. Oletus ei ole koskaan täysin
tosi, mutta se pienentää kappaleen tilan kolmeentoista lukuun.
Kaksiulotteisessa pelissä kappaleen tila oli paikka ja nopeus. Tässä
luvussa siihen lisätään asento ja pyöriminen sekä suure, joka kertoo,
kuinka vaikea kappaletta on panna pyörimään.

## Tila

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="kappale"}
```

Tilaan kuuluu neljä suuretta:

- **Sijainti** on *massakeskipisteen* paikka maailmassa. Massakeskipiste
  on se piste, joka liikkuu kuin pistemassa: kappaleeseen vaikuttavien
  voimien summa kiihdyttää sitä, kohdistuivat voimat mihin tahansa.
- **Kierto** on asento kvaterniona.
- **Nopeus** on massakeskipisteen nopeus.
- **Kulmanopeus** $\boldsymbol\omega$ on vektori, jonka suunta on
  pyörimisakseli ja pituus pyörimisnopeus radiaaneina sekunnissa.
  Pyörimissuunta saadaan oikean käden säännöllä.

Kaikki neljä ovat maailman koordinaatistossa. Muoto ja hitausmomentit
ovat kappaleen omassa koordinaatistossa, jonka origo on
massakeskipisteessä.

Massan sijasta tallennetaan *käänteismassa*, kuten taidossa
*Peliohjelmointi*: liikkumattoman kappaleen käänteismassa on nolla,
jolloin jokainen impulssi kerrotaan nollalla eikä seinä tarvitse omaa
koodipolkuaan.

## Pisteen nopeus

Kappaleeseen kiinnitetty piste liikkuu massakeskipisteen mukana ja
kiertää sitä. Jos pisteen paikka massakeskipisteestä on
$\mathbf r$, sen nopeus on

$$\mathbf v_p = \mathbf v + \boldsymbol\omega \times \mathbf r.$$

Tämä on tutoriaalin eniten käytetty kaava: törmäyksessä, kitkassa ja
nivelissä tarvitaan aina kosketus- tai kiinnityspisteen nopeus, ei
massakeskipisteen.

```{.cpp tiedosto="esimerkit/02-kappale.cpp" osa="pisteen-nopeus"}
```

```{.tuloste tiedosto="esimerkit/02-kappale.odotettu" rivit="7-10"}
```

Lankku etenee metrin sekunnissa ja pyörii pystyakselin ympäri. Sen
päät liikkuvat vastakkaisiin suuntiin, ja akselilla oleva piste liikkuu
kuten massakeskipiste.

## Hitaustensori

Massa kertoo, kuinka suuri voima tarvitaan kiihdyttämään kappaletta.
Pyörimisessä vastaava suure on *hitausmomentti*: kuinka suuri
vääntömomentti tarvitaan kulmakiihtyvyyteen. Se riippuu massan lisäksi
siitä, kuinka kaukana akselista massa on, joten se on eri akselien
ympäri eri suuri. Lankku on helppo pyöräyttää pituusakselinsa ympäri
ja raskas kääntää päät edellä.

Kolmessa ulottuvuudessa hitausmomentit kootaan 3 × 3 -matriisiksi,
*hitaustensoriksi* $I$, joka muuntaa kulmanopeuden
liikemäärämomentiksi:

$$\mathbf L = I\,\boldsymbol\omega.$$

Kun kappaleen koordinaatisto valitaan symmetria-akselien mukaan,
tensori on lävistäjämatriisi ja riittää tallentaa kolme
*päähitausmomenttia*. Tasaisen pallon ja laatikon arvot saadaan
kaavoista:

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="tehtaat"}
```

```{.cpp tiedosto="esimerkit/02-kappale.cpp" osa="hitaus"}
```

```{.tuloste tiedosto="esimerkit/02-kappale.odotettu" rivit="1-2"}
```

Pallolla kaikki kolme ovat samat. Neljän kilon lankulla (2 m × 0,2 m ×
0,5 m) pituusakselin hitausmomentti on yli kymmenen kertaa pienempi
kuin kahden muun.

Lävistäjämuoto pätee vain kappaleen omassa koordinaatistossa. Kun
kappale kääntyy, sen hitaustensori maailmassa muuttuu:

$$I_\text{maailma} = R\,I_\text{paikallinen}\,R^{\mathsf T},$$

missä $R$ on asennon kiertomatriisi.

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="hitaus"}
```

```{.cpp tiedosto="esimerkit/02-kappale.cpp" osa="maailmassa"}
```

```{.tuloste tiedosto="esimerkit/02-kappale.odotettu" rivit="3-6"}
```

Kallellaan olevan lankun tensorissa on lävistäjän ulkopuolisia
alkioita: kulmanopeus ja liikemäärämomentti eivät enää ole
samansuuntaiset. Tästä seuraa seuraavan luvun vaikein kohta, vapaasti
pyörivän kappaleen huojunta.

Moottori tarvitsee lähes aina tensorin käänteismatriisin, koska
kysymys on "kuinka paljon kulmanopeus muuttuu tästä impulssista".
Käänteistensori lasketaan samalla tavalla päähitausmomenttien
käänteisluvuista, ja liikkumattoman kappaleen käänteistensori on
nollamatriisi.

## Impulssi pisteeseen

Impulssi $\mathbf J$ on voima kertaa aika, eli liikemäärän muutos. Kun
se annetaan pisteeseen, jonka paikka massakeskipisteestä on
$\mathbf r$, se muuttaa sekä nopeutta että kulmanopeutta:

$$\Delta\mathbf v = \frac{\mathbf J}{m}, \qquad
  \Delta\boldsymbol\omega = I^{-1}(\mathbf r \times \mathbf J).$$

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="piste"}
```

```{.cpp tiedosto="esimerkit/02-kappale.cpp" osa="impulssi"}
```

```{.tuloste tiedosto="esimerkit/02-kappale.odotettu" rivit="11-18"}
```

Sama impulssi antaa lankulle saman liikemäärän, osui se mihin tahansa:
massakeskipisteen nopeus on kummassakin tapauksessa 0,5 m/s. Päähän
osunut impulssi panee lankun lisäksi pyörimään, ja liike-energiaa
syntyy lähes nelinkertaisesti. Osumakohta itse lähtee liikkeelle
nopeammin kuin koko kappale: pyörimään pääsevä kappale on osumakohdasta
katsoen *kevyempi* kuin sen massa. Tämä havainto on törmäysvasteen
kaavan ydin luvussa 5.

## Säilyvät suureet

Kolme suuretta toimii koko tutoriaalin ajan simulaation mittareina:

```{.cpp tiedosto="esimerkit/yhteinen/kappale.hpp" osa="suureet"}
```

- **Liikemäärä** $m\mathbf v$ säilyy, kun ulkoisia voimia ei ole.
  Törmäys siirtää sitä kappaleelta toiselle.
- **Liikemäärämomentti** säilyy, kun ulkoisia vääntömomentteja ei ole.
  Sillä on kaksi osaa: massakeskipisteen liikkeestä tuleva
  $\mathbf x \times m\mathbf v$ ja pyörimisestä tuleva
  $I\boldsymbol\omega$.
- **Liike-energia** $\tfrac12 m v^2 + \tfrac12
  \boldsymbol\omega\cdot I\boldsymbol\omega$ säilyy vain täysin
  kimmoisissa törmäyksissä ilman kitkaa. Pelissä se saa pienentyä,
  mutta sen kasvu on aina virhe.

## Käytännössä

- **Tila maailmassa, massaominaisuudet kappaleessa.** Sijainti, asento
  ja nopeudet ovat maailman koordinaateissa, muoto ja päähitausmomentit
  kappaleen omissa. Maailman hitaustensori lasketaan asennosta
  tarvittaessa tai kerran askeleessa.
- **Massakeskipiste on kappaleen origo.** Jos mallin origo on muualla,
  ero korjataan, kun kappale luodaan. Väärä massakeskipiste näkyy
  kappaleena, joka pyörii oudon pisteen ympäri.
- **Hitausmomentit lasketaan muodosta.** Fysiikkamoottorit laskevat ne
  törmäysmuodosta ja tiheydestä. Käsin asetettu epäfysikaalinen arvo
  on tavallinen syy epävakauteen: hyvin pieni hitausmomentti jollakin
  akselilla tekee kappaleesta herkän pyörimään hallitsemattomasti.
- **Käänteissuureet** (käänteismassa ja käänteinen hitaustensori)
  tekevät liikkumattomasta kappaleesta tavallisen tapauksen ja
  säästävät jakolaskuja ratkaisijan sisäsilmukassa.
- **Massasuhteet kohtuullisina.** Sadan kilon laatikko yhden kilon
  laatikon päällä on iteratiiviselle ratkaisijalle vaikea. Peleissä
  massat valitaan niin, että vierekkäisten kappaleiden suhde pysyy
  noin kymmenen sisällä.

## Itsearviointi

- Osaat luetella jäykän kappaleen tilan suureet ja kertoa, missä
  koordinaatistossa kukin on.
- Osaat laskea kappaleeseen kiinnitetyn pisteen nopeuden.
- Osaat selittää, miksi hitaustensori maailmassa muuttuu kappaleen
  kääntyessä ja miten se lasketaan päähitausmomenteista.
- Osaat laskea, miten pisteeseen annettu impulssi muuttaa nopeutta ja
  kulmanopeutta.
- Osaat kertoa, mitkä suureet säilyvät törmäyksessä ja mikä saa
  pienentyä.

# Logiikkaportit

Portti laskee Boolen funktion tuloistaan. Perusportteja on kuusi, ja
jokainen niistä on totuustaulu:

```{.python tiedosto="esimerkit/03-portit.py" osa="portit"}
```

```{.python tiedosto="esimerkit/03-portit.py" osa="taulu"}
```

| Portti | Lauseke | Lähtö on 1, kun |
|--------|---------|-----------------|
| AND | $ab$ | kaikki tulot ovat 1 |
| OR | $a + b$ | jokin tulo on 1 |
| XOR | $a \oplus b$ | parittoman moni tulo on 1 |
| NAND | $\overline{ab}$ | jokin tulo on 0 |
| NOR | $\overline{a + b}$ | kaikki tulot ovat 0 |
| XNOR | $\overline{a \oplus b}$ | tulot ovat samat |

Tässä tutoriaalissa käytetään merkintöjä $ab$ (AND), $a + b$ (OR),
$a'$ tai $\bar{a}$ (NOT) ja $a \oplus b$ (XOR).

## NAND on universaali

Jokainen Boolen funktio voidaan rakentaa pelkistä NAND-porteista.
Riittää näyttää, että NOT, AND ja OR syntyvät NAND-porteista, sillä
niistä saa minkä tahansa funktion (luku 4):

```{.python tiedosto="esimerkit/03-portit.py" osa="nand"}
```

OR-portin rakentaminen käyttää De Morganin lakia
$a + b = \overline{\bar{a}\,\bar{b}}$. Esimerkki tarkistaa toteutukset
vertaamalla niitä totuustauluihin kaikilla syötteillä:

```{.python tiedosto="esimerkit/03-portit.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/03-portit.odotettu"}
```

Sama pätee NOR-portille. Tällä on käytännön merkitystä: CMOS-
tekniikassa NAND ja NOR ovat luonnostaan invertoivia ja halvimpia
portteja, ja synteesityökalu rakentaa logiikan niistä ja
monimutkaisemmista invertoivista soluista (esimerkiksi AND–OR–INVERT).
AND-portti on piirissä NAND ja invertteri peräkkäin.

## CMOS-portti kytkimistä

Nykyiset digitaalipiirit tehdään CMOS-tekniikalla (complementary
metal–oxide–semiconductor). Transistoria voi tällä tasolla ajatella
kytkimenä:

- **nMOS** johtaa, kun sen hilalla on 1. Se vetää lähtöä hyvin kohti
  nollaa.
- **pMOS** johtaa, kun sen hilalla on 0. Se vetää lähtöä hyvin kohti
  ykköstä.

CMOS-portissa on kaksi verkkoa: pMOS-transistoreista koottu
*ylösvetoverkko* käyttöjännitteeseen ja nMOS-transistoreista koottu
*alasvetoverkko* maahan. Verkot ovat toistensa duaaleja: missä toisessa
on sarjakytkentä, toisessa on rinnankytkentä.

```{.python tiedosto="esimerkit/03-cmos.py" osa="kytkimet"}
```

NAND-portissa alasveto on kaksi nMOS-transistoria sarjassa (molempien
tulojen on oltava 1) ja ylösveto kaksi pMOS-transistoria rinnan
(riittää, että jompikumpi tulo on 0):

```{.python tiedosto="esimerkit/03-cmos.py" osa="nand"}
```

Malli tarkistaa, että täsmälleen toinen verkko johtaa:

```{.python tiedosto="esimerkit/03-cmos.py" osa="lahto"}
```

```{.tuloste tiedosto="esimerkit/03-cmos.odotettu"}
```

Virheellinen portti, jonka alasveto on rinnankytketty, tuottaa
oikosulun käyttöjännitteestä maahan. Oikeassa piirissä se kuluttaa
virtaa ja antaa epämääräisen lähtöjännitteen. Kelluva lähtö taas
säilyttää edellisen varauksensa, mikä on muistia, jota kukaan ei
suunnitellut.

Kytkinmallista näkyy myös CMOS:n suurin etu: levossa kumpikaan verkko
ei johda käyttöjännitteestä maahan, joten portti ei kuluta virtaa.
Virtaa kuluu vain, kun lähtö vaihtaa tilaa ja johtimen kapasitanssi
varataan tai puretaan. Tästä seuraa dynaamisen tehon kaava
$P \approx \alpha C V^2 f$: teho kasvaa kellotaajuuden $f$ ja
kytkentäaktiivisuuden $\alpha$ mukana ja jännitteen neliönä.

## Viive, kuormitus ja johdotus

Portin lähdön muuttuminen vie aikaa, koska transistori varaa
kapasitanssin rajallisella virralla. Viive kasvaa, kun:

- portin lähtö ohjaa montaa tuloa (*fan-out*): kuormakapasitanssi
  kasvaa
- portissa on monta sarjassa olevaa transistoria: neljän tulon NAND on
  hitaampi kuin kahden tulon NAND
- johdin on pitkä: nykyisissä prosesseissa johdotuksen viive on usein
  suurempi kuin porttien.

Siksi synteesityökalu ei rakenna 32-tuloista AND-porttia vaan puun
pienistä porteista. Tähän palataan luvussa 6 (summaimen muistipolku) ja
luvussa 11 (kriittinen polku).

## Käytännössä

- **Ajattele funktioina, toteuta soluina.** Suunnittelija kirjoittaa
  Boolen funktion tai RTL-kuvauksen. Synteesityökalu valitsee
  solukirjaston portit, jotka toteuttavat sen pienimmällä pinta-alalla
  ja riittävällä nopeudella. Portteja ei piirretä käsin.
- **NAND- ja NOR-ajattelu auttaa lukemaan synteesituloksia.**
  Porttitason netlistassa on invertoivia soluja, ja De Morganin lait
  ovat avain niiden lukemiseen.
- **Teho on kytkentöjä.** Kun haluat vähentää tehoa, vähennä turhia
  kytkentöjä: pysäytä laskenta, jonka tulosta ei tarvita, ja estä
  kellon kulku lepäävään lohkoon (*clock gating*).
- **Fan-out ja johdinpituus maksavat.** Yksi signaali, joka ohjaa
  tuhatta kiikkua (esimerkiksi nollaus tai sallinta), puskuroidaan
  puuksi. Työkalut tekevät sen, mutta suunnittelijan pitää tietää,
  miksi tällainen signaali on hidas.

## Itsearviointi

- Osaat kirjoittaa kuuden perusportin totuustaulut ja rakentaa NOT-,
  AND- ja OR-portit NAND-porteista.
- Osaat selittää CMOS-portin ylös- ja alasvetoverkon ja sen, miksi ne
  ovat toistensa duaaleja.
- Osaat kertoa, miksi CMOS-portti ei kuluta virtaa levossa ja mistä
  dynaaminen teho syntyy.
- Osaat luetella tekijät, jotka kasvattavat portin viivettä.

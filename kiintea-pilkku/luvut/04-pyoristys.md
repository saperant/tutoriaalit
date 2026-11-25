# Pyöristys ja katkaisu

Joka kerta kun bittejä pudotetaan, tarvitaan pyöristyssääntö. Valinta
näyttää pieneltä yksityiskohdalta, mutta sillä on kaksi mitattavaa
seurausta: virheen *harha* (keskiarvo) ja virheen *hajonta*.
Harha kertyy suodattimissa ja takaisinkytkennöissä, hajonta näkyy
kohinana. Laitteistossa pyöristystavat eroavat myös hinnaltaan.
Pyöristystapojen määritelmät ja liukulukujen pyöristystilat ovat
tuttuja taidosta *Miten tietokone laskee*; tässä luvussa mitataan, mitä
kukin tapa tekee kiinteän pilkun datapolussa ja mitä se maksaa.

## Pyöristystavat

Kun $k$ bittiä pudotetaan, tulos on jakolasku luvulla $2^k$ jollakin
pyöristyksellä. Yleiset tavat:

| Tapa | Englanniksi | Laitteisto |
|------|-------------|------------|
| katkaisu kohti −∞ (lattia) | *truncation*, *floor* | ei mitään: bitit jätetään pois |
| kohti nollaa | *round toward zero* | korjaus negatiivisille |
| lähimpään, puolikas ylöspäin | *round half up* | summain: $+2^{k-1}$ ennen katkaisua |
| lähimpään parilliseen | *convergent*, *round half to even* | summain ja tasapelin tunnistus |

Kahden komplementin katkaisu on pyöristys kohti miinus ääretöntä:
−0,5 katkeaa luvuksi −1, ei nollaksi. C:n jakolasku sen sijaan
pyöristää kohti nollaa. Negatiivisen etumerkillisen luvun siirto
oikealle on C:ssä toteutuksen määrittelemä (GCC ja Clang siirtävät
aritmeettisesti), joten siirrettävä toteutus kirjoitetaan niin, että se
siirtää vain ei-negatiivisia lukuja:

```{.c tiedosto="esimerkit/04-pyoristys.c" osa="lattia"}
```

```{.c tiedosto="esimerkit/04-pyoristys.c" osa="tavat"}
```

```{.c tiedosto="esimerkit/04-pyoristys.c" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/04-pyoristys.odotettu"}
```

![Neljän pyöristystavan siirtofunktio: vaaka-akselilla arvo ennen
pyöristystä, pystyakselilla tulos. Lattia on kokonaan suoran alapuolella
(harha), kohti nollaa pyöristävässä on leveä porras nollan kohdalla
(vaimennus), ja kaksi oikeanpuoleista eroavat vain tasapeleissä.
Kuva on piirretty esimerkin `04-harha.py`
funktioilla.](kuvat/pyoristys.png){width=100%}

Erot näkyvät tasapeleissä ja negatiivisissa luvuissa. Puolikas
ylöspäin pyöristää −2,5:n luvuksi −2 mutta 2,5:n luvuksi 3, eli
tasapelit menevät aina samaan suuntaan. Parilliseen pyöristäminen
vuorottelee: 1,5 → 2, 2,5 → 2. Se on IEEE 754:n oletus ja syy siihen,
miksi liukulukujen pyöristys ei vinouta summia.

## Harha mitattuna

Harha mitataan tasajakautuneilla syötteillä, joissa pudotetut bitit
käyvät läpi kaikki arvot yhtä usein:

```{.python tiedosto="esimerkit/04-harha.py" osa="tavat"}
```

```{.python tiedosto="esimerkit/04-harha.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/04-harha.odotettu" rivit="1-5"}
```

Tulokset vastaavat teoriaa. Katkaisun harha on
$-\tfrac{1}{2}(1 - 2^{-k})$ LSB eli lähes puoli LSB:tä, ja virheen
tehollisarvo on noin $1/\sqrt{3} \approx 0{,}58$ LSB. Pyöristys lähimpään
puolittaa tehollisarvon noin $1/\sqrt{12} \approx 0{,}29$ LSB:hen.
Puolikas ylöspäin jättää pienen harhan $2^{-k-1}$ LSB, koska tasapelit
pyöristyvät aina ylös; parilliseen pyöristäminen poistaa senkin. Kohti
nollaa pyöristäminen näyttää harhattomalta, koska negatiivisten ja
positiivisten virheet kumoavat toisensa, mutta se pienentää
järjestelmällisesti itseisarvoja ja vaimentaa signaalia.

## Harha takaisinkytkennässä

Harha on vaarallisin silmukoissa, joissa sama tulos syötetään takaisin.
Liukuva keskiarvo $y \leftarrow y + (x - y)/16$ on yksinkertainen
yksinapainen IIR-suodatin:

```{.python tiedosto="esimerkit/04-harha.py" osa="kertyminen"}
```

```{.tuloste tiedosto="esimerkit/04-harha.odotettu" rivit="6-8"}
```

Katkaisulla keskiarvo jää alhaalta lähestyttäessä 15 yksikköä
tavoitteen alle mutta saavuttaa sen ylhäältä: virhe riippuu suunnasta,
eli suodatin on harhainen. Kun ero on pienempi kuin 16, askel
$(x - y)/16$ pyöristyy nollaksi, ja suodatin pysähtyy *kuolleelle
alueelle* (*deadband*). Pyöristys lähimpään puolittaa kuolleen alueen ja
tekee siitä symmetrisen, mutta ei poista sitä. Pysyvä ratkaisu on lisätä
tilamuuttujaan murtobittejä: kun $y$ pidetään neljä bittiä tarkempana
kuin $x$, kuollut alue kutistuu alle yhden LSB:n, vaikka pyöristys on
pelkkä katkaisu.

![Liukuvan keskiarvon asettuminen kohti arvoa 1000 ylhäältä ja
alhaalta. Vasemmalla käyrät näyttävät samoilta; suurennos paljastaa
kuolleen alueen. Katkaisu pysähtyy arvoon 985, pyöristys arvoihin 992
ja 1008, ja neljä lisämurtobittiä tilassa vie tuloksen yhden LSB:n
päähän tavoitteesta.](kuvat/keskiarvo.png){width=100%}

Kuollut alue on esimerkki *rajasyklistä* (*limit cycle*):
takaisinkytketty suodatin ei asetu siihen arvoon, johon tarkka laskenta
veisi, vaan jää pyöristyksen takia vakioon tai pieneen jaksolliseen
heiluntaan. Pyöristyksestä johtuva rajasykli on pieni, muutaman LSB:n
suuruinen (*granular limit cycle*). Luvun 5 ylivuotovärähtely on eri
ilmiö: se syntyy ylivuodosta ja on koko arvoalueen suuruinen.

## Käytännössä

- **Pyöristä lähimpään oletuksena.** Puolikkaan lisäys ennen katkaisua
  maksaa yhden summaimen, ja se puolittaa kohinan ja poistaa lähes koko
  harhan. Katkaisu on perusteltu vain, kun harha ei kerry eikä yksi
  summain ole liikaa.
- **Käytä parilliseen pyöristämistä takaisinkytkennöissä ja
  kertymissä.** Kun sama pyöristys toistuu tuhansia kertoja (IIR,
  kertymä, iteratiivinen algoritmi), pienikin harha kertyy.
- **Kirjoita siirrettävä lattiasiirto C-malleihin.** `x >> k`
  negatiivisella `x`:llä toimii GCC:ssä ja Clangissa, mutta bittitarkan
  mallin ei pidä riippua kääntäjän valinnasta.
- **Älä sekoita C:n jakolaskua siirtoon.** `x / 4` ja `x >> 2` antavat
  eri tuloksen negatiivisilla luvuilla. Laitteistomalliin kuuluu se,
  minkä laitteisto oikeasti tekee.
- **Lisää tilaan murtobittejä.** Takaisinkytkennän kuolleen alueen
  poistaa leveämpi tila, ei pyöristystapa.

## Itsearviointi

- Osaat toteuttaa katkaisun, pyöristyksen lähimpään ja pyöristyksen
  lähimpään parilliseen siirroilla ja summilla.
- Osaat kertoa kunkin pyöristystavan harhan ja virheen tehollisarvon
  sekä laitteistokustannuksen.
- Osaat selittää, miksi katkaisu aiheuttaa harhaa takaisinkytketyssä
  suodattimessa ja miten kuollut alue poistetaan.
- Osaat kirjoittaa negatiivisille luvuille siirrettävän
  aritmeettisen siirron C:llä.
- Osaat erottaa pyöristyksestä johtuvan rajasyklin
  ylivuotovärähtelystä.

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

Piirikaavioissa ja datalehdissä portit piirretään symboleina. AND-
portin runko on suora takaa ja pyöreä edestä, OR-portin runko on kaareva
ja kärjellinen, ja XOR-portissa on OR-portin takana toinen kaari. Pieni
ympyrä lähdössä tarkoittaa kääntöä: NAND on AND ja ympyrä.

![Perusporttien symbolit ja lausekkeet. Ympyrä lähdössä kääntää
arvon.](kuvat/portit.png){width=100%}

Tässä tutoriaalissa käytetään merkintöjä $ab$ (AND), $a + b$ (OR),
$a'$ tai $\bar{a}$ (NOT) ja $a \oplus b$ (XOR).

## NAND on universaali

Jokainen Boolen funktio voidaan rakentaa pelkistä NAND-porteista.
Riittää näyttää, että NOT, AND ja OR syntyvät NAND-porteista, sillä
niistä saa minkä tahansa funktion (luku 4):

```{.python tiedosto="esimerkit/03-portit.py" osa="nand"}
```

![NOT, AND ja OR NAND-porteista. Invertteri on NAND, jonka tulot on
kytketty yhteen.](kuvat/nand-rakenteet.png){width=100%}

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

Invertterissä kumpaakin verkkoa on yksi transistori. NAND-portissa
alasveto on kaksi nMOS-transistoria sarjassa (molempien tulojen on
oltava 1) ja ylösveto kaksi pMOS-transistoria rinnan (riittää, että
jompikumpi tulo on 0):

![Invertteri ja NAND-portti transistoreina. pMOS-transistorin hilalla
on ympyrä: se johtaa, kun hilalla on 0.](kuvat/cmos.png){width=78%}

Sama rakenne Python-mallina:

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
ei johda käyttöjännitteestä maahan, joten ihanteellinen portti ei
kuluta virtaa. Virtaa kuluu, kun lähtö vaihtaa tilaa ja johtimen
kapasitanssi varataan tai puretaan. Tästä seuraa dynaamisen tehon kaava
$P \approx \alpha C V^2 f$: teho kasvaa kellotaajuuden $f$ ja
kytkentäaktiivisuuden $\alpha$ mukana ja jännitteen neliönä.

Kytkinmalli on tässä kohdassa liian siisti. Oikea transistori ei
sulkeudu kokonaan, ja pienen viivanleveyden prosesseissa *vuotovirta*
kulkee myös levossa olevan portin läpi. Tämä *staattinen teho* on
nykypiireissä merkittävä osa kokonaistehosta, eikä kaava
$\alpha C V^2 f$ sisällä sitä. Siksi lepäävästä lohkosta katkaistaan
paristokäyttöisissä laitteissa koko käyttöjännite eikä vain kelloa.

## Kolmitila ja avoin nielu

Tavallisen CMOS-portin lähtö on aina joko ylös- tai alasvedetty, joten
kahta lähtöä ei saa kytkeä samaan johtimeen: kun ne ovat eri mieltä,
syntyy oikosulku. Joskus monen lähettäjän on silti jaettava yksi
johdin, esimerkiksi väylä tai piirin kaksisuuntainen nasta. Siihen on
kaksi rakennetta.

*Kolmitilalähdöllä* (*tri-state*) on sallintatulo. Kun sallinta on 0,
kumpikaan verkko ei johda, ja lähtö on irti johtimesta. Tätä kolmatta
tilaa merkitään Z:lla (suuri impedanssi). Väylällä saa kerrallaan olla
sallittuna yksi ajuri:

```{.python tiedosto="esimerkit/03-vayla.py" osa="ratkaisu"}
```

*Avoin nielu* (*open drain*) on lähtö, jossa on pelkkä alasveto.
Ykkösen tuottaa johtimen ja käyttöjännitteen välinen ylösvetovastus.
Useampi lähtö voi ajaa johdinta yhtä aikaa ilman oikosulkua, ja johdin
on 1 vain, kun kukaan ei vedä sitä alas (*langoitettu AND*):

```{.python tiedosto="esimerkit/03-vayla.py" osa="avoin"}
```

```{.python tiedosto="esimerkit/03-vayla.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/03-vayla.odotettu"}
```

| A | B | Johdin | Selitys |
|---|---|--------|---------|
| 0 tai 1 | Z | A:n arvo | yksi ajuri määrää |
| Z | Z | Z | johdin kelluu: arvo on mikä sattuu |
| 0 | 1 | X | väyläriita: oikosulku ja tuntematon arvo |

Simulaattorit käyttävät samoja neljää arvoa: 0, 1, Z ja X
(tuntematon). I2C-väylän molemmat johtimet ovat avoimia nieluja, ja
mikrokontrollerin nasta on kolmitilalähtö, jonka suunta valitaan
rekisteristä (taidot *Oheislaiteväylät* ja *Mikrokontrollerit ja
bare-metal-ohjelmointi*). Piirin sisällä kolmitilaväyliä ei nykyään
käytetä: jaettu johdin korvataan multiplekserillä (luku 5), jonka
ajoitus on helpompi analysoida.

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
- **Yksi ajuri johdinta kohden.** Piirin sisällä jokaisella signaalilla
  on yksi lähde. Kolmitila ja avoin nielu kuuluvat piirin nastoihin ja
  levyn väyliin, ja kelluvaksi jäävä tulo sidotaan vastuksella
  tunnettuun arvoon.
- **Fan-out ja johdinpituus maksavat.** Yksi signaali, joka ohjaa
  tuhatta kiikkua (esimerkiksi nollaus tai sallinta), puskuroidaan
  puuksi. Työkalut tekevät sen, mutta suunnittelijan pitää tietää,
  miksi tällainen signaali on hidas.

## Itsearviointi

- Osaat kirjoittaa kuuden perusportin totuustaulut ja rakentaa NOT-,
  AND- ja OR-portit NAND-porteista.
- Osaat selittää CMOS-portin ylös- ja alasvetoverkon ja sen, miksi ne
  ovat toistensa duaaleja.
- Osaat kertoa, mistä dynaaminen teho syntyy ja miksi levossa oleva
  portti kuluttaa silti vuotovirtaa.
- Osaat tunnistaa perusportit piirikaavion symboleista.
- Osaat selittää kolmitilalähdön ja avoimen nielun ja sen, mitä arvot
  Z ja X tarkoittavat.
- Osaat luetella tekijät, jotka kasvattavat portin viivettä.

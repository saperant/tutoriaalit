# Aktiiviset suodattimet

Passiivinen RC-suodatin vaimentaa 20 dB dekadilla, ja kaksi peräkkäistä
RC-astetta kuormittavat toisiaan. Kelojen avulla saisi jyrkempiä
suodattimia, mutta matalilla taajuuksilla kelat ovat suuria, kalliita ja
häiriöherkkiä. *Aktiivinen suodatin* korvaa kelat operaatiovahvistimella:
vastukset ja kondensaattorit muodostavat toisen kertaluvun lohkon, ja
vahvistin puskuroi sen niin, ettei seuraava lohko kuormita edellistä.
Korkeamman kertaluvun suodatin rakennetaan sarjaan kytketyistä toisen
kertaluvun lohkoista, aivan kuten digitaalinen IIR-suodatin
toisen kertaluvun osista (taito *Digitaalinen signaalinkäsittely*).

## Toisen kertaluvun alipäästö

Toisen kertaluvun alipäästön siirtofunktio on

$$
H(s) = \frac{K}{\frac{s^2}{\omega_0^2} + \frac{s}{Q\,\omega_0} + 1}.
$$

Kulmataajuus $\omega_0$ määrää, missä vaimennus alkaa, ja
hyvyysluku $Q$ muodon: pieni $Q$ antaa loivan, ylityksettömän vasteen ja
suuri $Q$ terävän polven, jota seuraa piikki. Taidossa
*Differentiaaliyhtälöt ja Laplace-muunnos* samat parametrit esiintyivät
vaimennussuhteena $\zeta = 1/(2Q)$. Suodatinperheet ovat eri $Q$-arvojen
valintoja:

| Perhe | Q (2. kertaluku) | Ominaisuus |
|-------|------------------|------------|
| Bessel | 0,577 | tasainen ryhmäviive, lähes ei ylitystä |
| Butterworth | 0,707 | tasaisin päästökaista, 4,3 % ylitys |
| Chebyshev 1 dB | 0,957 | jyrkempi siirtymä, aaltoilu päästökaistalla |

## Sallen-Key-rakenne

Sallen-Key-rakenteessa kaksi vastusta ja kaksi kondensaattoria
muodostavat RC-verkon, ja vahvistin on seuraaja. Takaisinkytkentä
kondensaattorin C1 kautta korottaa $Q$:ta yli sen, mihin passiivinen
RC-ketju pystyy.

![Sallen-Key-alipäästö, vahvistus 1. C1 kytkee lähdön takaisin
vastusten väliseen solmuun.](kuvat/sallen-key.png){width=62%}

Solmuyhtälöistä saadaan siirtofunktio
$H(s) = 1/(R_1 R_2 C_1 C_2 s^2 + C_2(R_1 + R_2)s + 1)$. Kun vastukset
ovat yhtä suuret, $Q = \sqrt{C_1/C_2}/2$, joten Butterworthin
$Q = 0{,}707$ vaatii $C_1 = 2C_2$:

```{.python tiedosto="esimerkit/04-sallen-key.py" osa="mitoitus"}
```

```{.spice tiedosto="esimerkit/04-sallen-key.cir"}
```

Python laskee siirtofunktion arvon taajuuksilla 100 Hz, 1 kHz ja 10 kHz
sijoittamalla $s = j2\pi f$ nimittäjäpolynomiin:

```{.python tiedosto="esimerkit/04-sallen-key.py" osa="siirtofunktio"}
```

```{.tuloste tiedosto="esimerkit/04-sallen-key.odotettu"}
```

![Sallen-Key-alipäästön vahvistus: SPICE ja siirtofunktio ovat
päällekkäin. Vaimennus on 40 dB dekadilla.](kuvat/sallen-key-bode.png){width=78%}

Mitoitettu vastus 11,254 kΩ ei ole standardiarvo. Käytännössä
valitaan lähin E96-arvo (11,3 kΩ) ja kondensaattoreiksi 10 nF ja 22 nF
tai kaksi rinnakkaista 10 nF:n kondensaattoria. Rajataajuus siirtyy
muutaman prosentin, mikä on yleensä vähemmän kuin kondensaattoreiden
toleranssi. Vahvistimen $GBW$:n on oltava selvästi suodattimen
taajuutta suurempi, nyrkkisääntönä $100\,f_0 Q$, muuten vahvistimen oma
napa vääristää vastetta.

## Multiple feedback ja symbolinen analyysi

*Multiple feedback* (MFB) -rakenteessa vahvistin on invertoiva, ja sekä
vastus että kondensaattori kytkevät lähdön takaisin. Rakenne kääntää
signaalin vaiheen, mutta siihen saa vahvistuksen ja se on vähemmän
herkkä vahvistimen ominaisuuksille. Sen siirtofunktion johtaminen käsin
on työläs mutta mekaaninen tehtävä, joka sopii SymPylle: kaksi
solmuyhtälöä, ihanteellisen vahvistimen säännöt ja ratkaisu.

![MFB-alipäästö. Lähtö kytkeytyy takaisin kahta reittiä: vastuksen R2
kautta solmuun `a` ja kondensaattorin C2 kautta invertoivaan tuloon
`m`.](kuvat/mfb.png){width=70%}

```{.python tiedosto="esimerkit/04-mfb.py" osa="symbolinen"}
```

Kertoimista luetaan $\omega_0$ ja $Q$, ja sama lauseke muutetaan
numeeriseksi funktioksi vertailua varten:

```{.python tiedosto="esimerkit/04-mfb.py" osa="arvot"}
```

```{.spice tiedosto="esimerkit/04-mfb.cir"}
```

```{.tuloste tiedosto="esimerkit/04-mfb.odotettu"}
```

Symbolinen ratkaisu kertoo myös suunnittelusäännöt: osoittaja on
$-R_2$ ja vakiotermi $R_1$, joten tasavahvistus on $-R_2/R_1$, ja
$\omega_0 = 1/\sqrt{R_2 R_3 C_1 C_2}$. Kun kaikki vastukset ovat samat,
$Q = \sqrt{C_1/C_2}/3$, joten Butterworth vaatii
$C_1 = 4{,}5\,C_2$. Tällainen johtaminen kannattaa tehdä koneella aina,
kun piiri on monimutkaisempi kuin oppikirjan esimerkki: virheet
etumerkeissä ja indekseissä ovat käsin laskiessa tavallisia, ja SPICE
vahvistaa tuloksen.

Samoista rakenteista saadaan muutkin suodatintyypit vaihtamalla
vastusten ja kondensaattorien paikkoja:

| Tyyppi | Sallen-Key | MFB |
|--------|------------|-----|
| alipäästö | R1, R2 sarjassa; C1 takaisinkytkennässä, C2 maahan | R1, R3 sarjassa; C1 maahan, R2 ja C2 takaisinkytkennässä |
| ylipäästö | vastukset ja kondensaattorit vaihtavat paikkaa | vastukset ja kondensaattorit vaihtavat paikkaa |
| kaistanpäästö | harvoin; $Q$ herkkä vahvistukselle | C sarjassa ja takaisinkytkennässä, R maahan ja takaisinkytkennässä |

Ylipäästön siirtofunktiossa osoittaja on $K s^2/\omega_0^2$ ja
kaistanpäästön $K s/(Q\omega_0)$; nimittäjä, $\omega_0$ ja $Q$ ovat
samaa muotoa kuin alipäästössä. Ylipäästön yläpäätä rajoittaa
vahvistimen oma kaistanleveys, joten aktiivinen ylipäästö on
todellisuudessa aina kaistanpäästö. Mitoitus kannattaa tehdä samalla
tavalla kuin edellä: johda siirtofunktio symbolisesti ja tarkista
simuloimalla.

## Toleranssit ja Monte Carlo

Suodattimen komponenttien arvot vaihtelevat: tarkkuusvastukset ±1 %,
keraamiset kondensaattorit tyypillisesti ±5 ... ±10 %. Monte Carlo
-analyysi simuloi suuren joukon piirejä satunnaisin arvoin ja kertoo,
miten paljon ominaisuudet hajoavat. Esimerkki kirjoittaa netlistiin
200 kopiota suodattimesta, ja yksi ngspice-ajo laskee ne kaikki:

```{.python tiedosto="esimerkit/04-montecarlo.py" osa="netlist"}
```

```{.python tiedosto="esimerkit/04-montecarlo.py" osa="tilastot"}
```

```{.tuloste tiedosto="esimerkit/04-montecarlo.odotettu"}
```

![200 Monte Carlo -piirin kulma- ja −3 dB:n taajuudet. Rajataajuuden
jakauma on leveämpi, koska se riippuu myös Q:sta.](kuvat/montecarlo.png){width=78%}

Kulmataajuus $f_0$ riippuu tulosta $R_1 R_2 C_1 C_2$, joten sen
suhteellinen hajonta on puolet komponenttien hajontojen neliösummasta,
ja simulointi vahvistaa arvion. Mutta −3 dB:n taajuus hajoaa enemmän,
1,9 %: se riippuu myös $Q$:sta, ja $Q$ riippuu kondensaattoreiden
*suhteesta*. Tämä on tyypillinen Monte Carlon löytö: yksinkertainen
herkkyyslasku antaa yhden suureen hajonnan, mutta mitattava ominaisuus
voi riippua muustakin. Kondensaattorien sovitus (sama valmistuserä,
C0G-eriste) parantaa tulosta enemmän kuin tarkemmat vastukset.

## Butterworth vai Bessel

Taajuustasossa Butterworth on paras: päästökaista on tasaisin. Aikatasossa
sen askelvasteessa on 4,3 %:n ylitys ja värähtely. Bessel-suodatin
uhraa jyrkkyyden ja saa tilalle lähes ylityksettömän askelvasteen,
koska sen ryhmäviive on tasainen: kaikki taajuudet viivästyvät yhtä
paljon, ja pulssin muoto säilyy.

```{.python tiedosto="esimerkit/04-bessel.py" osa="ylitys"}
```

```{.spice tiedosto="esimerkit/04-bessel.cir"}
```

```{.tuloste tiedosto="esimerkit/04-bessel.odotettu"}
```

![Butterworth- ja Bessel-suodattimen askelvaste samalla
kulmataajuudella.](kuvat/askel-suodattimet.png){width=78%}

Bessel-suodatin on hitaampi samalla kulmataajuudella; sen −3 dB:n
taajuus on noin 0,79 $f_0$. Valinta riippuu käytöstä: audiossa ja
spektrianalyysissä taajuusvaste ratkaisee, pulssien ja digitaalisten
signaalien käsittelyssä aikataso.

## Antialiasointisuodin

AD-muunnin näytteistää signaalin taajuudella $f_s$, ja kaikki yli
$f_s/2$:n taajuudet laskostuvat kaistalle (taito *Signaalit ja
järjestelmät*). Laskostuneita komponentteja ei voi poistaa
jälkikäteen, joten ne on vaimennettava *ennen* muunninta analogisella
suodattimella. Vaimennuksen on riitettävä muuntimen kohinatasolle
(luku 6):

```{.python tiedosto="esimerkit/04-antialiasointi.py" osa="vaatimus"}
```

```{.python tiedosto="esimerkit/04-antialiasointi.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/04-antialiasointi.odotettu"}
```

Neljännen kertaluvun suodatin (kaksi Sallen-Key-lohkoa) riittää.
Ylinäytteistys keventää vaatimusta: kun näytteet otetaan nelinkertaisella
taajuudella ja jyrkkä suodatus tehdään digitaalisesti desimoinnin
yhteydessä, analogiseksi suodattimeksi riittää kolmas kertaluku. Sigma-
delta-muuntimissa (luku 6) ylinäytteistys on niin suuri, että
yksinkertainen RC-suodin riittää.

## Käytännössä

- Rakenna korkeamman kertaluvun suodatin toisen kertaluvun lohkoista ja
  laita suurimman $Q$:n lohko viimeiseksi, jotta sen piikki ei
  ylikuormita seuraavia lohkoja.
- Mitoita taulukoista tai suodatinsuunnitteluohjelmalla ja tarkista
  simuloimalla. Johda epätavallisen rakenteen siirtofunktio
  symbolisesti (SymPy).
- Käytä suodattimissa C0G/NP0-kondensaattoreita. X7R-tyyppien
  kapasitanssi muuttuu jännitteen ja lämpötilan mukaan, mikä vääristää
  vastetta.
- Aja Monte Carlo ja tarkista se ominaisuus, joka oikeasti ratkaisee
  (esimerkiksi vaimennus estokaistan reunalla), ei vain nimellistä
  rajataajuutta.
- Valitse Bessel, kun aaltomuoto on tärkeä, ja Butterworth tai
  Chebyshev, kun taajuusvaste on tärkeä.

## Itsearviointi

- Osaat mitoittaa Sallen-Key-alipäästön annetulle kulmataajuudelle ja
  $Q$:lle ja verrata simuloitua taajuusvastetta siirtofunktioon.
- Osaat johtaa aktiivisen suodattimen siirtofunktion solmuyhtälöistä
  SymPyllä ja lukea siitä $\omega_0$:n ja $Q$:n.
- Osaat arvioida komponenttitoleranssien vaikutuksen herkkyysanalyysillä
  ja Monte Carlolla ja selittää, miksi eri suureet hajoavat eri tavoin.
- Osaat valita suodatinperheen taajuus- ja aikatason vaatimusten
  perusteella.
- Osaat laskea antialiasointisuodattimen kertaluvun muuntimen
  resoluutiosta ja näytetaajuudesta.

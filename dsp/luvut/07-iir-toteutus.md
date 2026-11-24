# IIR-toteutus

IIR-suotimen kertoimet voi kirjoittaa differenssiyhtälöksi suoraan, ja
pienillä asteluvuilla se toimii. Korkealla asteella ja kiinteällä
pilkulla suora toteutus hajoaa. Tässä luvussa suodin pilkotaan toisen
asteen lohkoiksi, lohko toteutetaan C:llä kahdessa suoramuodossa ja
tutkitaan, mitä kertoimien ja tilan kvantisointi tekee.

## Miksi toisen asteen lohkot

Kahdeksannen asteen suodin on nimittäjäpolynomi, jossa on yhdeksän
kerrointa. Navat ovat polynomin juuria, ja juuret ovat herkkiä
kertoimien muutoksille, kun navat ovat lähellä toisiaan. Kapeassa
alipäästössä kaikki navat ovat lähellä pistettä $z = 1$, jolloin
viimeisen bitin muutos kertoimessa voi siirtää napaa yli
yksikköympyrän.

Toisen asteen lohkoissa (*second-order sections*, SOS) suodin
kirjoitetaan tulona

$$H(z) = \prod_{j} \frac{b_{0j} + b_{1j} z^{-1} + b_{2j} z^{-2}}
{1 + a_{1j} z^{-1} + a_{2j} z^{-2}},$$

jossa jokaisella lohkolla on vain yksi napapari. Lohkon napoihin
vaikuttavat vain sen omat kaksi kerrointa, joten virheet eivät kasaannu.

```{.python tiedosto="esimerkit/07-sos.py" osa="navat"}
```

```{.python tiedosto="esimerkit/07-sos.py" osa="vaste"}
```

```{.tuloste tiedosto="esimerkit/07-sos.odotettu"}
```

Kun kertoimet pyöristetään float32-tarkkuuteen, lohkojen navat eivät
liiku neljännessä desimaalissa, mutta polynomin suurin napa siirtyy
yksikköympyrän ulkopuolelle ja suodin hajoaa. Edes float64-polynomi ei
ole turvallinen: sen impulssivaste poikkeaa 7 %. SciPyn `sosfilt`
ja `output="sos"` ovat siksi oletus kaikille IIR-suotimille, joiden
aste on yli kaksi.

Lohkojen järjestyksellä ja napojen ja nollien parituksella on myös
merkitystä. `zpk2sos` parittaa kunkin napaparin lähimpien nollien
kanssa ja järjestää lohkot niin, että jyrkimmin resonoiva lohko on
viimeisenä. Silloin välitulokset eivät ylivuoda kiinteässä pilkussa.

## Suoramuodot

Toisen asteen lohkon voi laskea monella algebrallisesti samanarvoisella
tavalla. Ne eroavat tilamuuttujien määrässä ja numeerisessa
käytöksessä. Kaksi yleisintä ovat **suoramuoto I** (DF1) ja
**transponoitu suoramuoto II** (DF2T):

```{.c tiedosto="esimerkit/07-biquad/biquad.c" osa="df1"}
```

```{.c tiedosto="esimerkit/07-biquad/biquad.c" osa="df2t"}
```

| Muoto | Tila | Vahvuus | Heikkous |
|------|-------|------------------------------|----------------------------|
| DF1 | 4 lukua | ei sisäistä ylivuotoa, sopii kiinteään pilkkuun | enemmän muistia |
| DF2T | 2 lukua | vähiten muistia, hyvä liukuluvuilla | tilamuuttujat voivat kasvaa suuriksi |
| DF2 | 2 lukua | vähän muistia | huono dynamiikka, vältä |

DF1 laskee kaikki tulot yhteen yhteen kertymään. Kun kertymässä on
vartijabittejä, kuten DSP-prosessorien 40-bittisissä akkumulaattoreissa,
välisummat saavat ylivuotaa, kunhan lopputulos mahtuu. Siksi DF1 on
kiinteän pilkun oletusmuoto. Liukuluvuilla DF2T on yleisin, ja SciPyn
`lfilter` käyttää sitä.

Ketju toteutetaan silmukkana lohkojen yli. Tila on kutsujan muistissa,
kuten FIR-suotimessa.

```{.c tiedosto="esimerkit/07-biquad/biquad.h" osa="tyypit"}
```

```{.c tiedosto="esimerkit/07-biquad/biquad.c" osa="kasittele"}
```

## Kertoimet laitteessa: Bristow-Johnsonin kaavat

Taajuuskorjaimissa ja muissa säädettävissä suotimissa kertoimet
lasketaan laitteessa, kun käyttäjä kääntää säädintä. Robert
Bristow-Johnsonin *Audio EQ Cookbook* antaa esivääristetyllä
bilineaarimuunnoksella johdetut kaavat yleisimmille toisen asteen
suotimille: alipäästö, ylipäästö, kaistanpäästö, lovi ja korostus.

```{.c tiedosto="esimerkit/07-biquad/biquad.c" osa="alipaasto"}
```

Kun $Q = 1/\sqrt2$, alipäästö on toisen asteen Butterworth, mikä
tarkistetaan vertailussa SciPyn `butter`-funktioon. Neljännen asteen
Butterworth saadaan kahdesta lohkosta, joiden $Q$ on
$1/(2\cos\theta)$, kun $\theta = \pi/8$ ja $3\pi/8$.

```{.c tiedosto="esimerkit/07-biquad/main.c" osa="suunnittelu"}
```

```{.c tiedosto="esimerkit/07-biquad/main.c" osa="muodot"}
```

```{.tuloste tiedosto="esimerkit/07-biquad.odotettu"}
```

Ketju vahvistaa 1 kHz:ä 6 dB ja on 8 kHz:llä Butterworthin −3 dB:ssä
(korostuslohkon pieni vaikutus mukaan lukien). DF1 ja DF2T antavat
liukuluvuilla saman tuloksen pyöristysvirheen tarkkuudella.
Vertailuohjelma tarkistaa ketjun SciPyn `sosfilt`-funktiota vastaan
toleranssilla $10^{-10}$ ja pytest kahdeksannen asteen elliptiseen
asti.

## Kertoimien kvantisointi

Kiinteän pilkun biquadissa kertoimet tallennetaan kokonaislukuina.
Kertoimen $a_1$ itseisarvo voi olla lähes 2, joten tavallinen muoto on
Q2.14 (16 bittiä) tai Q2.30 (32 bittiä). Kvantisointi siirtää
napoja, ja vaikutus on suurin, kun napa on lähellä pistettä $z = 1$
eli kun rajataajuus on pieni suhteessa näytetaajuuteen.

```{.python tiedosto="esimerkit/07-kvantisointi.py" osa="kvantisoi"}
```

```{.python tiedosto="esimerkit/07-kvantisointi.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/07-kvantisointi.odotettu"}
```

50 Hz:n alipäästössä 48 kHz:n näytetaajuudella osoittajan kertoimet
ovat noin $10^{-5}$, mikä on pienempi kuin Q2.14:n pienin askel
$6 \cdot 10^{-5}$. Suodin ei päästä läpi mitään. 500 Hz:llä vahvistus
on jo 0,13 dB väärin. Ratkaisuja on kolme: lisää bittejä (Q2.30),
pienempi näytetaajuus suotimelle (desimointi ensin, luku 9) tai
rakenne, joka on herkkä vain pienille muutoksille lähellä pistettä
$z = 1$. Viimeisestä esimerkkejä ovat hila- ja tilamuuttujarakenteet
sekä delta-operaattorimuoto, jotka mainitaan tässä vain nimeltä.

## Rajasyklit

Kiinteän pilkun IIR-suotimessa jokainen kertolasku pyöristetään.
Pyöristys on epälineaarinen operaatio, ja takaisinkytkentä voi jäädä
sen ansiosta värähtelemään, vaikka syöte on nolla. Lineaarinen suodin
vaimenisi nollaan, mutta kvantisoitu jää **rajasykliin**.

```{.c tiedosto="esimerkit/07-rajasykli.c" osa="suodin"}
```

```{.c tiedosto="esimerkit/07-rajasykli.c" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/07-rajasykli.odotettu"}
```

Pyöristys lähimpään jättää ensimmäisen asteen suotimen arvoon 4, koska
$0{,}9 \cdot 4 = 3{,}6$ pyöristyy takaisin neljään. Negatiivisella
kertoimella tila vaihtaa merkkiä joka näytteellä: syntyy Nyquistin
taajuinen värähtely, joka kuuluu äänessä vinkunana tai näkyy
mittauksessa vakiovirheenä. **Itseisarvon katkaisu** kohti nollaa
poistaa nollasyötteen rajasyklin, koska se pienentää tilan itseisarvoa
joka askeleella. Toinen tavallinen ratkaisu on pieni lisäkohina
(*dither*). Toisen asteen lohkoissa rajasykleillä on useampia muotoja,
ja ylivuodon aiheuttamat suuret rajasyklit estetään saturaatiolla eikä
kiertävällä aritmetiikalla.

## Käytännössä

- **Toteuta IIR-suotimet toisen asteen lohkoina** aina kun aste on yli
  kaksi, myös liukuluvuilla.
- **Valitse DF2T liukuluvuille ja DF1 kiinteälle pilkulle**, jossa on
  leveä kertymä.
- **Laske säädettävien suotimien kertoimet Bristow-Johnsonin
  kaavoilla** ja varmista ne vertaamalla SciPyn suunnitteluun.
- **Tarkista kvantisoidut kertoimet**: navat, tasavahvistus ja
  rajataajuus. Pieni rajataajuus suurella näytetaajuudella vaatii
  bittejä tai desimointia.
- **Testaa nollasyötteellä**, vaimeneeko kiinteän pilkun suodin
  nollaan, ja valitse pyöristystapa sen mukaan.

## Itsearviointi

- Osaat selittää, miksi korkea-asteinen IIR-suodin toteutetaan toisen
  asteen lohkoina, ja näyttää ilmiön kertoimien pyöristyksellä.
- Osaat toteuttaa biquad-ketjun C:llä suoramuodoissa DF1 ja DF2T ja
  perustella valinnan.
- Osaat laskea toisen asteen alipäästön ja korostuksen kertoimet
  Bristow-Johnsonin kaavoilla.
- Osaat arvioida kertoimien kvantisoinnin vaikutuksen ja tunnistaa
  rajasyklin sekä keinot sen poistamiseen.

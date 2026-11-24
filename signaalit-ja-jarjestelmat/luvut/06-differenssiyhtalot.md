# Differenssiyhtälöt ja rekursiiviset suotimet

Konvoluutio impulssivasteen kanssa vaatii yhtä monta kertolaskua
näytettä kohti kuin impulssivasteessa on näytteitä. Jos impulssivaste on
ääretön, kuten mustan laatikon $0.2 \cdot 0.8^n$ luvussa 1, suoraa
konvoluutiota ei voi laskea. Laatikko laski sen silti kahdella
kertolaskulla näytettä kohti, koska se käytti omaa edellistä
ulostuloaan. Tällainen **rekursiivinen** suodin kuvataan
differenssiyhtälöllä, ja se on tämän luvun aihe.

## Lineaarinen differenssiyhtälö

Yleinen kausaalinen LTI-suodin, jolla on äärellinen määrä kertoimia,
on

$$a_0\,y[n] = \sum_{k=0}^{M} b_k\,x[n-k] - \sum_{k=1}^{N} a_k\,y[n-k].$$

Kertoimet $b$ painottavat syötteitä, ja kertoimet $a$ palauttavat
aiempia ulostuloja takaisin. Merkit ja nimet ovat SciPyn ja MATLABin
käytännön mukaiset: `lfilter(b, a, x)`. Kertoimen $a_0$ on oltava
nollasta poikkeava, ja yleensä se on 1. Jos se ei ole, kaikki kertoimet
jaetaan sillä.

Jos kaikki $a_k$, $k \ge 1$, ovat nollia, suodin on **FIR**
(*finite impulse response*): impulssivaste on $b$ ja päättyy $M + 1$
näytteen jälkeen. Muuten suodin on yleensä **IIR** (*infinite impulse
response*): takaisinkytkentä pitää vasteen käynnissä loputtomasti,
vaikka se vaimenisi.

Suora toteutus laskee yhtälön sellaisenaan. Se on hidas Pythonilla,
mutta se on hyvä referenssi, ja juuri tämä silmukka ajetaan
mikro-ohjaimessa tai FPGA:ssa:

```{.python tiedosto="esimerkit/06-differenssi.py" osa="suora"}
```

```{.python tiedosto="esimerkit/06-differenssi.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-differenssi.odotettu"}
```

Esimerkissä $a_0 = 2$, ja normitus on välttämätön: ilman sitä tulos
olisi väärä kaikilla näytteillä. Impulssivaste vaimenee nopeasti ja
vaihtaa merkkiään, mikä kertoo kompleksisista navoista (luku 7).

## Eksponentiaalinen liukuva keskiarvo

Yleisin rekursiivinen suodin on **eksponentiaalinen liukuva keskiarvo**
(EMA):

$$y[n] = y[n-1] + \alpha\,(x[n] - y[n-1]) = \alpha\,x[n] + (1 - \alpha)\,y[n-1].$$

Jokainen uusi näyte siirtää arvoa osuuden $\alpha$ kohti mittausta.
Impulssivaste on $\alpha(1-\alpha)^n$, ja SciPyn kertoimet ovat
$b = [\alpha]$ ja $a = [1, -(1-\alpha)]$. EMA on liukuvan keskiarvon
halpa korvike: se vaatii yhden muistipaikan ja kaksi kertolaskua,
ikkunan pituudesta riippumatta.

Parametri valitaan yleensä **aikavakion** $\tau$ mukaan. Jatkuvan ajan
RC-alipäästösuotimen askelvaste on $1 - e^{-t/\tau}$, ja diskreetti
vastine saadaan valitsemalla $1 - \alpha = e^{-T_s/\tau}$. Silloin
askelvaste saavuttaa 63 prosenttia lopullisesta arvosta noin ajassa
$\tau$ ja 95 prosenttia ajassa $3\tau$.

```{.python tiedosto="esimerkit/06-ema.py" osa="ema"}
```

Kohinan vaimennus seuraa luvun 2 energialaskusta. Valkoisen kohinan
varianssi kerrotaan impulssivasteen energialla
$\sum h^2 = \alpha^2 / (1 - (1-\alpha)^2) = \alpha/(2 - \alpha)$.
Liukuvalla keskiarvolla sama luku on $1/M$, joten EMA vastaa kohinan
osalta liukuvaa keskiarvoa, jonka pituus on $M = (2-\alpha)/\alpha$.

```{.python tiedosto="esimerkit/06-ema.py" osa="kohina"}
```

```{.tuloste tiedosto="esimerkit/06-ema.odotettu"}
```

Diskreetti askel saavuttaa 63 prosenttia hetkellä 19 ms, koska
ensimmäinen näyte on jo hetkellä nolla. Pieni ero on tavallinen, kun
jatkuvan ajan nyrkkisääntöjä käytetään näytteistetyssä järjestelmässä.

## Alkutila

Rekursiivinen suodin muistaa menneisyyden tilassaan. `lfilter` aloittaa
oletuksena nollatilasta, mikä vastaa oletusta, että syöte on ollut
nolla ennen ensimmäistä näytettä. Jos signaalissa on suuri tasataso,
kuten 5 voltin anturijännite, nollatila tuottaa alkuun pitkän
transientin: suotimen ulostulo nousee nollasta kohti viittä volttia.
`lfilter_zi` laskee tilan, jossa suodin on tasapainossa vakiosyötteellä
1. Kun se kerrotaan ensimmäisellä näytteellä, suodin käyttäytyy kuin
syöte olisi aina ollut tällä tasolla.

```{.python tiedosto="esimerkit/06-alkutila.py" osa="alkutila"}
```

```{.tuloste tiedosto="esimerkit/06-alkutila.odotettu"}
```

Nollatilasta alkava ulostulo on alussa täysin väärä ja ylittää jopa
syötteen hetkellä 40, koska toisen asteen suotimen askelvasteessa on
ylitys. Sadan näytteen jälkeen erot ovat hävinneet. Molemmat ovat
oikeita vastauksia eri kysymyksiin. Jos signaali todella alkaa nollasta,
kuten kytkettäessä virta päälle, nollatila on oikea.

## Toisen asteen resonaattori

Kun takaisinkytkennässä on kaksi edellistä ulostuloa, suodin voi
värähdellä. Valitaan kertoimet
$a = [1, -2r\cos\theta, r^2]$. Seuraavan luvun kielellä suotimella on
kompleksinen napapari $re^{\pm i\theta}$, ja sen impulssivaste on
vaimeneva sini

$$h[n] = \frac{r^n \sin((n+1)\theta)}{\sin\theta},$$

jonka taajuus on $\theta$ radiaania näytettä kohti ja vaimennus $r$
näytettä kohti.

```{.python tiedosto="esimerkit/06-resonaattori.py" osa="resonaattori"}
```

```{.tuloste tiedosto="esimerkit/06-resonaattori.odotettu"}
```

Kun $r < 1$, värähtely vaimenee, ja mitä lähempänä ykköstä $r$ on, sitä
pidempään se soi ja sitä kapeampi on resonanssi. Kun $r = 1$,
värähtely jatkuu muuttumattomana: suodin on **oskillaattori**, ja
tällä rakenteella tuotetaan siniä laskemalla, esimerkiksi
DTMF-äänitaajuusvalinnan Goertzelin algoritmissa. Kun $r > 1$,
värähtely kasvaa eksponentiaalisesti, ja suodin on epästabiili.
Rekursiivinen suodin voi siis olla epästabiili, vaikka sen kertoimet
näyttävät viattomilta. FIR-suodin on aina stabiili.

## Käytännössä

- **Normita kertoimet ykköseksi** ($a_0 = 1$), ennen kuin kirjoitat
  differenssiyhtälön omaan toteutukseen, ja tarkista oma toteutus
  `lfilter`-funktiota vastaan.
- **Valitse EMA:n kerroin aikavakiosta**: $\alpha = 1 - e^{-T_s/\tau}$.
  Pienillä arvoilla $\alpha \approx T_s/\tau$. Älä kopioi kerrointa
  näytetaajuudesta toiseen.
- **Mieti alkutila.** Käytä `lfilter_zi`-funktiota, kun signaali on
  ollut vakaa ennen ensimmäistä näytettä, ja nollatilaa, kun
  järjestelmä todella käynnistyy levosta.
- **Pidä rekursiiviset suotimet matalina.** Korkea aste suorana
  differenssiyhtälönä on herkkä pyöristykselle (luku 7). Ketjuta
  toisen asteen lohkoja (`sosfilt`).

## Itsearviointi

- Osaat kirjoittaa differenssiyhtälön SciPyn kertoimina `b` ja `a`,
  toteuttaa sen silmukkana ja tarkistaa toteutuksen `lfilter`-funktiolla.
- Osaat erottaa FIR- ja IIR-suotimen ja selittää, miksi rekursiivinen
  suodin tuottaa äärettömän impulssivasteen.
- Osaat valita eksponentiaalisen keskiarvon kertoimen aikavakiosta ja
  laskea sen kohinanvaimennuksen.
- Osaat asettaa suotimen alkutilan `lfilter_zi`-funktiolla ja selittää,
  milloin nollatila on oikea valinta.

# Z-muunnos, navat ja nollat

Differenssiyhtälö kertoo, miten suodin lasketaan, mutta ei suoraan, mitä
se tekee. Onko suodin stabiili? Resonoiko se? Mitä taajuuksia se
vaimentaa? Vastaukset löytyvät, kun differenssiyhtälö muunnetaan
polynomien osamääräksi. **Z-muunnos** tekee tämän, ja sen tuloksen
nollakohdat ja navat ovat suotimen tiivein kuvaus.

## Määritelmä ja suppenemisalue

Jonon $x[n]$ Z-muunnos on kompleksimuuttujan $z$ funktio

$$X(z) = \sum_{n=-\infty}^{\infty} x[n]\,z^{-n}.$$

Se on potenssisarja muuttujassa $z^{-1}$, jonka kertoimet ovat jonon
arvot. Taidossa *Kompleksiluvut ja Fourier-analyysi* todettiin, että
konvoluutio on polynomien kertolasku. Z-muunnos tekee tästä havainnosta
työkalun: $x * h$ muuntuu tuloksi $X(z)H(z)$.

Sarja suppenee vain osalla tasoa. Tämä **suppenemisalue** (*region of
convergence*, ROC) on osa muunnosta. Kausaalisella eksponenttijonolla
$a^n u[n]$ sarja on geometrinen:

$$\sum_{n=0}^{\infty} a^n z^{-n} = \frac{1}{1 - a z^{-1}},
\qquad |z| > |a|.$$

Suljettu kaava on olemassa lähes kaikkialla, mutta sarja suppenee vain
ympyrän $|z| = |a|$ ulkopuolella:

```{.python tiedosto="esimerkit/07-suppeneminen.py" osa="suppeneminen"}
```

```{.tuloste tiedosto="esimerkit/07-suppeneminen.odotettu"}
```

Kun $|z| > a$, osasummat lähestyvät kaavan arvoa. Lähellä rajaa
($z = -0.85$) ne lähestyvät hitaasti, ja sisäpuolella ne kasvavat
rajatta, vaikka kaava antaa siistin luvun. Sama kaava $1/(1 - az^{-1})$
on myös ei-kausaalisen jonon $-a^n u[-n-1]$ muunnos alueessa $|z| < |a|$.
Siksi muunnos ilman suppenemisaluetta ei määrää jonoa yksikäsitteisesti.
Kausaalisten järjestelmien suppenemisalue on aina jonkin ympyrän
ulkopuoli, ja tässä tutoriaalissa käsitellään vain niitä.

| Jono | $X(z)$ | Suppenemisalue |
|------|--------|----------------|
| $\delta[n]$ | $1$ | koko taso |
| $\delta[n - k]$ | $z^{-k}$ | $z \ne 0$ |
| $u[n]$ | $1/(1 - z^{-1})$ | $\lvert z\rvert > 1$ |
| $a^n u[n]$ | $1/(1 - az^{-1})$ | $\lvert z\rvert > \lvert a\rvert$ |
| $r^n \cos(\theta n)\,u[n]$ | $\dfrac{1 - r\cos\theta\,z^{-1}}{1 - 2r\cos\theta\,z^{-1} + r^2 z^{-2}}$ | $\lvert z\rvert > r$ |

Tärkeimmät ominaisuudet: muunnos on lineaarinen, viive $k$ näytettä
kertoo muunnoksen tekijällä $z^{-k}$, ja konvoluutio muuntuu tuloksi.
Viiveominaisuus selittää, miksi $z^{-1}$ on signaalinkäsittelyn
lohkokaavioiden viivelohkon symboli.

## Siirtofunktio

Muunnetaan differenssiyhtälö puolittain. Viive $y[n-k]$ muuntuu
tuloksi $z^{-k}Y(z)$, joten

$$Y(z)\sum_{k=0}^{N} a_k z^{-k} = X(z)\sum_{k=0}^{M} b_k z^{-k},
\qquad H(z) = \frac{Y(z)}{X(z)} = \frac{B(z)}{A(z)}.$$

**Siirtofunktio** $H(z)$ on impulssivasteen Z-muunnos, ja se on kahden
polynomin osamäärä, joiden kertoimet ovat suoraan SciPyn `b` ja `a`.
Osoittajan nollakohdat ovat suotimen **nollat** ja nimittäjän
nollakohdat sen **navat**. Polynomi määräytyy nollakohdistaan
vakiokerrointa vaille, joten nollat, navat ja vahvistus kuvaavat
suotimen täysin. `scipy.signal.tf2zpk` laskee ne.

```{.python tiedosto="esimerkit/07-siirtofunktio.py" osa="siirtofunktio"}
```

Miksi $H(z)$ on järkevä luku mielivaltaisessa pisteessä $z$? Syötetään
suotimelle jono $x[n] = z_0^n$. Se on konvoluution **ominaisjono**:
$\sum_k h[k] z_0^{n-k} = z_0^n \sum_k h[k] z_0^{-k} = H(z_0)\,z_0^n$.
Ulostulo on sama jono kerrottuna vakiolla $H(z_0)$. Simulointi
vahvistaa tämän:

```{.python tiedosto="esimerkit/07-siirtofunktio.py" osa="ominaisjono"}
```

```{.tuloste tiedosto="esimerkit/07-siirtofunktio.odotettu"}
```

Kun $z_0 = 1$, syöte on vakio, ja $H(1) = \sum b / \sum a$ on suotimen
tasajännitevahvistus. Kun $|z_0| = 1$, syöte on kompleksinen sini, ja
$H$ yksikköympyrällä on taajuusvaste (luku 8). Kasvava jono
$z_0 = 1{,}2$ toimii myös, koska se on suppenemisalueessa.

## Navat ja stabiilisuus

Osamurtokehitelmän avulla siirtofunktio hajoaa ensimmäisen asteen
termeiksi $r_k/(1 - p_k z^{-1})$, ja jokainen termi on impulssivasteessa
jono $r_k p_k^n$. Impulssivaste on siis summa eksponenttijonoja, joiden
kantaluvut ovat navat. Tästä seuraa suodinanalyysin tärkein sääntö:

> Kausaalinen LTI-suodin on stabiili täsmälleen silloin, kun kaikki
> sen navat ovat yksikköympyrän sisällä, $|p_k| < 1$.

Navan etäisyys origosta kertoo vaimenemisnopeuden ja sen kulma
värähtelyn taajuuden, kuten edellisen luvun resonaattorissa.
Yksikköympyrällä oleva napa tuottaa jonon, joka ei vaimene eikä kasva
(summain, oskillaattori). Nollat eivät vaikuta stabiilisuuteen. Siksi
FIR-suodin, jonka kaikki navat ovat origossa, on aina stabiili.

```{.python tiedosto="esimerkit/07-navat.py" osa="stabiilius"}
```

Navat lasketaan kertoimista numeerisesti, ja juuri siinä piilee vaara.
Korkea-asteisen polynomin juuret ovat herkkiä kertoimien pienille
muutoksille, varsinkin kun juuret ovat lähellä toisiaan. Kapea
alipäästösuodin on juuri sellainen: kaikki navat ovat lähellä pistettä
$z = 1$. Kun kertoimet pyöristetään, kuten kiinteän pilkun toteutuksessa
tapahtuu, stabiili suodin voi muuttua epästabiiliksi.

```{.python tiedosto="esimerkit/07-navat.py" osa="herkkyys"}
```

```{.tuloste tiedosto="esimerkit/07-navat.odotettu"}
```

Kertoimien muutos on alle $10^{-4}$, mutta suurin napa siirtyy
yksikköympyrän ulkopuolelle. Kun sama suodin toteutetaan kolmena
toisen asteen lohkona (*second-order sections*, SOS), kunkin lohkon
navat pysyvät paikallaan saman pyöristyksen jälkeen. Siksi
korkea-asteiset IIR-suotimet suunnitellaan muodossa `output="sos"` ja
ajetaan funktiolla `sosfilt`. Kertoimien kvantisoinnin systemaattinen
käsittely kuuluu taitoon *Digitaalinen signaalinkäsittely*.

## Käänteinen muunnos ja ketjutus

Impulssivaste saadaan siirtofunktiosta osamurtokehitelmällä.
`scipy.signal.residuez` laskee residyt $r_k$ ja navat $p_k$ muodossa
$\sum_k r_k/(1 - p_k z^{-1})$, ja jokainen termi on jono
$r_k p_k^n u[n]$.

```{.python tiedosto="esimerkit/07-kaanteinen.py" osa="osamurrot"}
```

Kun suotimet kytketään sarjaan, siirtofunktiot kerrotaan, ja polynomien
kertolasku on kertoimien konvoluutio. Rinnankytkennässä siirtofunktiot
lasketaan yhteen.

```{.python tiedosto="esimerkit/07-kaanteinen.py" osa="kaskadi"}
```

```{.tuloste tiedosto="esimerkit/07-kaanteinen.odotettu"}
```

Käytännössä käänteinen muunnos tehdään harvoin käsin, koska
`lfilter` laskee impulssivasteen suoraan. Osamurrot ovat kuitenkin
selitys sille, miltä impulssivaste näyttää: hitain vaimeneva termi
kuuluu suurimpaan napaan ja ratkaisee, kuinka kauan suodin "soi".

## Käytännössä

- **Tarkista stabiilisuus navoista** (`tf2zpk` tai `np.roots(a)`),
  kun suunnittelet tai muutat IIR-suodinta, ja tee siitä testi.
- **Käytä toisen asteen lohkoja** (`output="sos"`, `sosfilt`)
  aina, kun aste on yli kaksi tai kertoimet pyöristetään.
- **Lue suodinta navoista ja nollista.** Napa lähellä yksikköympyrää
  tarkoittaa pitkää soimista ja terävää resonanssia; nolla
  yksikköympyrällä poistaa sen taajuuden kokonaan.
- **Laske tasajännitevahvistus** kaavalla $H(1) = \sum b/\sum a$ ja
  normita se, jos suotimen ei kuulu muuttaa signaalin tasoa.

## Itsearviointi

- Osaat laskea eksponenttijonon Z-muunnoksen ja sen suppenemisalueen
  ja selittää, miksi kaava ilman suppenemisaluetta ei määrää jonoa.
- Osaat muodostaa differenssiyhtälöstä siirtofunktion ja laskea sen
  navat ja nollat `tf2zpk`-funktiolla.
- Osaat päätellä kausaalisen suotimen stabiilisuuden navoista ja
  selittää, miksi toisen asteen lohkot kestävät pyöristystä paremmin.
- Osaat laskea impulssivasteen osamurroilla (`residuez`) ja ketjuttaa
  suotimia kertoimien konvoluutiolla.

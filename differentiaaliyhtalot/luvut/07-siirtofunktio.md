# Siirtofunktio ja vasteet

Kun lineaarisen järjestelmän alkuehdot ovat nollia, Laplace-muunnettu
lähtö on herätteen muunnos kerrottuna funktiolla, joka riippuu vain
järjestelmästä:

$$Y(s) = H(s)\,U(s).$$

$H(s)$ on **siirtofunktio**. Se tiivistää järjestelmän yhteen
rationaalifunktioon, jonka **navat** (nimittäjän nollakohdat) ja
**nollat** (osoittajan nollakohdat) kertovat vasteen luonteen. Tässä
luvussa siirtofunktio johdetaan piiristä, ja siitä lasketaan askelvaste,
taajuusvaste ja diskreetin ajan vastine.

```{.dot otsikko="Lohkokaavio: siirtofunktio kertoo herätteen muunnoksen."}
digraph {
  rankdir=LR;
  u [label="U(s)", shape=plaintext, style=""];
  h [label="H(s)"];
  y [label="Y(s) = H(s) U(s)", shape=plaintext, style=""];
  u -> h -> y;
}
```

## Siirtofunktio piiristä

Sarja-RLC-piirin kondensaattorijännitteelle pätee
$LC\,u_C'' + RC\,u_C' + u_C = u$. Nollilla alkuehdoilla muunnos
on $(LCs^2 + RCs + 1)\,U_C(s) = U(s)$, joten

$$H(s) = \frac{U_C(s)}{U(s)} = \frac{1}{LCs^2 + RCs + 1}.$$

Arvoilla $L = 10$ mH, $R = 20$ $\Omega$ ja $C = 1$ $\mu$F
ominaiskulmataajuus on $\omega_0 = 1/\sqrt{LC} = 10\,000$ rad/s ja
vaimennussuhde $\zeta = 0{,}1$ (luku 4).

```{.python tiedosto="esimerkit/07-siirtofunktio.py" osa="siirto"}
```

Navat $-1000 \pm 9950i$ kertovat kaiken olennaisen: reaaliosa $-1000$
1/s on vaimenemisnopeus (aikavakio 1 ms), ja imaginaariosa on
vaimennetun värähtelyn kulmataajuus $\omega_d = \omega_0\sqrt{1-\zeta^2}$.

## Askelvaste

**Askelvaste** on lähtö, kun tuloon kytketään hetkellä 0 vakiojännite.
Askeleen muunnos on $1/s$, joten askelvasteen muunnos on $H(s)/s$.
Loppuarvo on loppuarvolauseen mukaan $H(0)$, ja alivaimennetun
järjestelmän huippu osuu puolen värähdysjakson kohdalle
$t_p = \pi/\omega_d$. **Ylitys** on kaavan mukaan
$e^{-\zeta\pi/\sqrt{1-\zeta^2}}$.

```{.python tiedosto="esimerkit/07-siirtofunktio.py" osa="askel"}
```

SciPyn `scipy.signal` tekee saman numeerisesti. `lti` saa osoittajan ja
nimittäjän kertoimet korkeimmasta potenssista alkaen, ja `step` laskee
askelvasteen annetuilla ajanhetkillä.

```{.python tiedosto="esimerkit/07-siirtofunktio.py" osa="scipy"}
```

```{.tuloste tiedosto="esimerkit/07-siirtofunktio.odotettu"}
```

Symbolinen, numeerinen ja kaavalla laskettu huippu ovat samat; scipyn
huippuhetki poikkeaa vain aikataulukon välin verran.

![Sarja-RLC-alipäästön askelvaste kolmella vaimennussuhteella
($\omega_0 = 10\,000$ rad/s) ja vastaavat navat s-tasossa. Mitä lähempänä
imaginaariakselia navat ovat, sitä hitaammin värähtely
vaimenee.](kuvat/askelvaste.png){width=92%}

Kuvasta näkee siirtofunktion geometrian: napojen etäisyys origosta on
$\omega_0$, ja kulma negatiiviseen reaaliakseliin määrää vaimennussuhteen
($\cos\varphi = \zeta$). Kriittisesti vaimennetulla piirillä on
kaksoisnapa reaaliakselilla.

## Impulssivaste ja siirtofunktion merkitys

**Impulssivaste** $h(t)$ on siirtofunktion käänteismuunnos: lähtö, kun
tuloon syötetään hetkellinen sysäys. Luvun 6 konvoluutiokaavan mukaan
impulssivaste määrää järjestelmän vasteen mihin tahansa herätteeseen.
Siirtofunktio, impulssivaste ja differentiaaliyhtälö ovat siis kolme
esitystä samasta asiasta:

| Esitys | Muoto | Hyvä tehtävään |
|--------|-------|----------------|
| differentiaaliyhtälö | $LCu'' + RCu' + u = u_{in}$ | mallintaminen, epälineaariset laajennukset |
| siirtofunktio | $H(s) = 1/(LCs^2 + RCs + 1)$ | navat, stabiilisuus, kytkennät |
| impulssivaste | $h(t) = \mathcal{L}^{-1}\{H\}$ | konvoluutio, mittaukset |
| taajuusvaste | $H(i\omega)$ | suodattimet, Bode-kuvaaja |

## Taajuusvaste

Kun tuloon syötetään sini $\sin\omega t$, stabiilin järjestelmän lähtö on
jatkuvuustilassa sini samalla taajuudella. Sen amplitudi kerrotaan
luvulla $|H(i\omega)|$ ja vaihe siirtyy kulman $\arg H(i\omega)$ verran.
**Taajuusvaste** saadaan siis sijoittamalla siirtofunktioon $s = i\omega$.

```{.python tiedosto="esimerkit/07-taajuusvaste.py" osa="taajuus"}
```

Matalilla taajuuksilla piiri päästää signaalin läpi, ominaistaajuudella
se vahvistaa viisinkertaisesti ($1/(2\zeta)$) ja vaihe on $-90°$, ja
korkeilla taajuuksilla vaimennus kasvaa 40 dB dekadia kohti. Tämä on
toisen kertaluvun alipäästösuodin; taito *Elektroniikan perusteet ja
SPICE* näyttää saman Bode-kuvaajana ngspicellä, ja taito
*Analogiaelektroniikka* rakentaa suodattimia operaatiovahvistimilla.

## s-taso ja z-taso

Digitaalinen järjestelmä näytteistää signaalin välein $T$, ja jatkuvan
ajan $e^{st}$ muuttuu jonoksi $(e^{sT})^n = z^n$. Siksi jatkuvan ajan
napa $s$ vastaa diskreetin ajan napaa

$$z = e^{sT}.$$

Vasen puolitaso ($\operatorname{Re} s < 0$) kuvautuu yksikköympyrän
sisään ($|z| < 1$), ja imaginaariakseli yksikköympyrälle. Tämä yhdistää
Laplace-muunnoksen taidon *Signaalit ja järjestelmät* Z-muunnokseen:
stabiilisuusehto on molemmissa sama, vain eri tason kielellä.

```{.python tiedosto="esimerkit/07-taajuusvaste.py" osa="diskreetti"}
```

```{.tuloste tiedosto="esimerkit/07-taajuusvaste.odotettu"}
```

`cont2discrete` muuntaa jatkuvan järjestelmän diskreetiksi olettaen,
että tulo pysyy vakiona näytteiden välillä (*zero-order hold*). Diskreetin
järjestelmän navat ovat täsmälleen $e^{sT}$, mikä vahvistaa kuvauksen.

## Käytännössä

- **Lue navat ennen simulointia.** Napojen reaaliosat antavat
  aikavakiot, imaginaariosat värähtelytaajuudet ja kulma
  vaimennussuhteen.
- **Käytä siirtofunktiota kytkentöjen laskemiseen.** Sarjaan kytketyt
  lohkot kerrotaan, rinnakkaiset lasketaan yhteen ja takaisinkytkentä
  antaa $G/(1 + GH)$ (luku 8).
- **Muista nollat alkuehdoissa.** Siirtofunktio kuvaa vain herätteen
  vaikutuksen; alkuehtojen vaikutus lasketaan erikseen.
- **Tarkista taajuusvaste kahdella tavalla.** Sijoitus $s = i\omega$ ja
  `scipy.signal.freqs` tai simuloitu jatkuvuustilan amplitudi antavat
  saman tuloksen, jos malli on oikein.

## Itsearviointi

- Osaat johtaa siirtofunktion lineaarisesta differentiaaliyhtälöstä.
- Osaat laskea navat ja tulkita niistä aikavakiot, värähtelytaajuuden
  ja vaimennussuhteen.
- Osaat laskea askelvasteen symbolisesti ja `scipy.signal`-kirjastolla
  sekä arvioida ylityksen ja huippuhetken.
- Osaat laskea taajuusvasteen sijoituksella $s = i\omega$.
- Osaat selittää s-tason ja z-tason yhteyden $z = e^{sT}$ ja sen
  merkityksen stabiilisuudelle.

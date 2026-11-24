# Laplace-muunnos

**Laplace-muunnos** muuttaa lineaarisen differentiaaliyhtälön
algebralliseksi yhtälöksi. Derivointi muuttuu kertomiseksi $s$:llä,
alkuehdot tulevat mukaan automaattisesti, ja ratkaisu palautetaan
aikatasoon taulukon ja osamurtohajotelman avulla. Menetelmä on
sähkötekniikan ja säätötekniikan työkalu, koska se käsittelee
askel- ja impulssiherätteet luontevasti ja johtaa suoraan
siirtofunktioon (luku 7).

```{.dot otsikko="Laplace-menetelmä: kierros s-tason kautta."}
digraph {
  rankdir=LR;
  node [width=1.6];
  dy [label="differentiaali-\nyhtälö + alkuehdot"];
  alg [label="algebrallinen\nyhtälö Y(s)"];
  Ys [label="Y(s)\nosamurtoina"];
  y [label="ratkaisu y(t)"];
  dy -> alg [label="L{ }"];
  alg -> Ys [label="ratkaise,\napart"];
  Ys -> y [label="L^-1{ }\ntaulukko"];
  dy -> y [label="suoraan (vaikeaa)", style=dashed];
}
```

## Määritelmä ja taulukko

Funktion $f(t)$, $t \ge 0$, Laplace-muunnos on

$$F(s) = \mathcal{L}\{f\}(s) = \int_0^\infty f(t)\,e^{-st}\,dt.$$

Integraali suppenee, kun $s$:n reaaliosa on riittävän suuri;
insinöörikäytössä suppenemisalue on harvoin ongelma. SymPyn
`laplace_transform` laskee muunnoksen, ja `noconds=True` jättää
suppenemisehdot pois.

```{.python tiedosto="esimerkit/06-taulukko.py" osa="taulukko"}
```

Taulukon rivit on hyvä tunnistaa ulkoa: vakio on $1/s$, eksponentti
$e^{-at}$ on $1/(s + a)$, ja sini ja kosini tuottavat nimittäjän
$s^2 + \omega^2$. Nimittäjän nollakohdat eli **navat** kertovat, millaisia
aikafunktioita ratkaisussa on: napa $-a$ tarkoittaa termiä $e^{-at}$ ja
napapari $\pm i\omega$ värähtelyä taajuudella $\omega$.

## Ominaisuudet

Muunnoksen hyödyllisyys perustuu muutamaan sääntöön:

| Aikataso | s-taso | Nimi |
|----------|--------|------|
| $a f + b g$ | $aF + bG$ | lineaarisuus |
| $f'(t)$ | $sF(s) - f(0)$ | derivointi |
| $f''(t)$ | $s^2F(s) - s f(0) - f'(0)$ | toinen derivaatta |
| $\int_0^t f\,d\tau$ | $F(s)/s$ | integrointi |
| $e^{-at} f(t)$ | $F(s + a)$ | siirto s-tasossa |
| $f(t - T)\,u(t - T)$ | $e^{-sT}F(s)$ | viive |
| $(f * g)(t)$ | $F(s)\,G(s)$ | konvoluutio |

Derivointisääntö on menetelmän ydin: alkuarvot tulevat mukaan
termeinä, joten niitä ei tarvitse sovittaa erikseen lopuksi.

```{.python tiedosto="esimerkit/06-taulukko.py" osa="derivaatta"}
```

```{.python tiedosto="esimerkit/06-taulukko.py" osa="siirto"}
```

```{.tuloste tiedosto="esimerkit/06-taulukko.odotettu"}
```

## Alkuarvotehtävä vaihe vaiheelta

Ratkaistaan $y'' + 3y' + 2y = 4$, $y(0) = 1$, $y'(0) = 0$.

1. **Muunna** yhtälö termi kerrallaan derivointisäännöillä.
2. **Ratkaise** $Y(s)$ algebrallisesta yhtälöstä.
3. **Hajota** $Y(s)$ osamurroiksi (`sp.apart`).
4. **Palauta** jokainen osamurto taulukosta aikatasoon.

```{.python tiedosto="esimerkit/06-alkuarvo.py" osa="muunnos"}
```

```{.python tiedosto="esimerkit/06-alkuarvo.py" osa="osamurrot"}
```

Tulos tarkistetaan `dsolve`-funktiolla. **Alkuarvolause**
$y(0^+) = \lim_{s\to\infty} sY(s)$ ja **loppuarvolause**
$y(\infty) = \lim_{s\to 0} sY(s)$ antavat ratkaisun alku- ja loppuarvon
suoraan s-tasosta. Loppuarvolause pätee vain, jos ratkaisu todella
asettuu, eli kun $sY(s)$:n navat ovat vasemmassa puolitasossa.

```{.python tiedosto="esimerkit/06-alkuarvo.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-alkuarvo.odotettu"}
```

Osamurrot kertovat ratkaisun rakenteen: $2/s$ on loppuarvo 2,
$-2/(s+1)$ hitaampi vaimeneva termi ja $1/(s+2)$ nopeampi. Octaven
`residue` tekee saman hajotelman numeerisesti.

```{.octave tiedosto="esimerkit/octave/07-osamurrot.m" osa="osamurrot"}
```

```{.tuloste tiedosto="esimerkit/octave/07-osamurrot.odotettu"}
```

## Viive ja kytkentähetket

Laplace-muunnos käsittelee kytkennät luontevasti. **Heavisiden
askelfunktio** $H(t - T)$ on nolla ennen hetkeä $T$ ja yksi sen jälkeen,
ja viivesääntö antaa sen muunnokseksi $e^{-sT}/s$. Pulssi, joka
kytketään päälle hetkellä 1 ja pois hetkellä 3, on kahden askeleen
erotus $H(t-1) - H(t-3)$.

```{.python tiedosto="esimerkit/06-viive.py" osa="pulssi"}
```

Ratkaisussa jokainen askel käynnistää oman ensimmäisen kertaluvun
vasteensa omalla hetkellään. Aikatasossa sama vaatisi yhtälön
ratkaisemisen paloittain ja ratkaisujen liittämisen jatkuvasti
toisiinsa. Numeerinen simulointi vahvistaa tuloksen.

```{.python tiedosto="esimerkit/06-viive.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-viive.odotettu"}
```

## Konvoluutio

Lineaarisen järjestelmän lähtö on herätteen ja **impulssivasteen**
$h(t)$ konvoluutio

$$y(t) = (h * u)(t) = \int_0^t h(t - \tau)\,u(\tau)\,d\tau.$$

Integraali on työläs, mutta s-tasossa konvoluutio on pelkkä tulo
$Y = H\,U$. Esimerkki laskee saman molemmin tavoin. Diskreetti
vastine, summa näytteiden yli, on taidon *Signaalit ja järjestelmät*
konvoluutio.

```{.python tiedosto="esimerkit/06-konvoluutio.py" osa="konvoluutio"}
```

```{.tuloste tiedosto="esimerkit/06-konvoluutio.odotettu"}
```

## Samat laskut Maximalla

Maximassa `laplace` ja `ilt` ovat muunnos ja käänteismuunnos,
`partfrac` osamurtohajotelma. `desolve` ratkaisee lineaarisen
alkuarvotehtävän Laplace-muunnoksella; alkuarvot annetaan
`atvalue`-funktiolla.

```{.maxima tiedosto="esimerkit/maxima/06-laplace.mac" osa="laplace"}
```

```{.tuloste tiedosto="esimerkit/maxima/06-laplace.odotettu"}
```

## Käytännössä

- **Käytä Laplacea lineaarisille vakiokertoimisille yhtälöille.**
  Epälineaarisille ja aikariippuville yhtälöille se ei sovellu; niille
  jää numeerinen ratkaisu.
- **Tee osamurtohajotelma koneella, tulkitse käsin.** Jokainen termi on
  ratkaisun komponentti, ja sen napa kertoo komponentin aikavakion tai
  taajuuden.
- **Tarkista loppuarvolauseen ehto.** Jos navat eivät ole vasemmassa
  puolitasossa, lause antaa luvun, jota ratkaisu ei koskaan saavuta.
- **Tarkista tulos toisella menetelmällä.** `dsolve`, Maximan `desolve`
  ja numeerinen simulointi päätyvät samaan, jos muunnos on tehty oikein.

## Itsearviointi

- Osaat laskea Laplace-muunnoksen määritelmästä ja taulukosta sekä
  SymPyllä ja Maximalla.
- Osaat käyttää derivointi-, siirto- ja konvoluutiosääntöä.
- Osaat ratkaista lineaarisen alkuarvotehtävän Laplace-muunnoksella ja
  osamurtohajotelmalla.
- Osaat käyttää alku- ja loppuarvolausetta ja tiedät loppuarvolauseen
  ehdon.
- Osaat tulkita osamurtojen navat ratkaisun komponentteina.

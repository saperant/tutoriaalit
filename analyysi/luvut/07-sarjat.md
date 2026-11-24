# Sarjat ja Taylorin polynomit

Sarja on äärettömän monen termin summa. Ajatus kuulostaa teoreettiselta,
mutta jokainen laskimen ja ohjelmointikielen `sin`, `exp` ja `log`
lasketaan lopulta muutaman termin polynomina, joka on johdettu sarjasta.
Luvussa käydään läpi sarjan suppeneminen, Taylorin polynomit ja niiden
virhe sekä se, miten kirjasto laskee eksponenttifunktion.

## Suppeneminen

Sarja $\sum_{k=0}^\infty a_k$ **suppenee**, jos sen **osasummat**
$S_n = \sum_{k=0}^n a_k$ lähestyvät raja-arvoa. Muuten sarja
**hajaantuu**. **Geometrinen sarja** $\sum q^k$ suppenee, kun $|q| < 1$,
ja sen summa on $\frac{1}{1 - q}$. SymPyn `summation` laskee summan
symbolisesti.

```{.python tiedosto="esimerkit/07-sarjat.py" osa="osasummat"}
```

**Harmoninen sarja** $\sum 1/k$ on tärkeä varoittava esimerkki: termit
lähestyvät nollaa, mutta sarja hajaantuu. Osasummat kasvavat kuten
$\ln n$, eli hitaasti mutta rajatta. Termien lähestyminen nollaan on
suppenemisen välttämätön mutta ei riittävä ehto. Sarja $\sum 1/k^2$ sen
sijaan suppenee arvoon $\pi^2/6$.

Harmoninen sarja esiintyy algoritmien analyysissä: pikalajittelun
odotettu vertailumäärä ja hajautustaulun ketjujen pituudet johtavat
harmonisiin summiin (taito *Algoritmit*).

Suppenemisen testaamiseen on useita testejä. **Suhdetesti** on
käytännöllisin: jos $|a_{k+1}/a_k| \to L$, sarja suppenee, kun $L < 1$,
ja hajaantuu, kun $L > 1$. Jos $L = 1$, testi ei ratkaise.
**Potenssisarja** $\sum c_k x^k$ suppenee **suppenemissäteen** $R$
sisällä, eli kun $|x| < R$, missä suhdetestistä $R = \lim |c_k/c_{k+1}|$.

```{.python tiedosto="esimerkit/07-sarjat.py" osa="suhde"}
```

```{.tuloste tiedosto="esimerkit/07-sarjat.odotettu"}
```

Sarjan $\sum x^k/k$ suppenemissäde on 1. Sarja on $-\ln(1 - x)$, joka ei
ole määritelty, kun $x = 1$: säde ei ole sattumaa, vaan funktion
erikoiskohta rajoittaa sitä.

## Taylorin polynomit

**Taylorin polynomi** on polynomi, jolla on kehityskohdassa $a$ samat
derivaatat kuin funktiolla $n$:nteen kertalukuun asti:

$$P_n(x) = \sum_{k=0}^n \frac{f^{(k)}(a)}{k!}(x - a)^k.$$

Asteen 1 polynomi on luvun 4 linearisointi. Korkeampi aste ottaa mukaan
kaarevuuden ja sen muutokset. Kun $n \to \infty$ ja sarja suppenee
kohti funktiota, saadaan **Taylorin sarja**. SymPyn `series` antaa
kehitelmän valmiina, ja $O(x^n)$ merkitsee pois jätettyjä termejä.

```{.python tiedosto="esimerkit/07-taylor.py" osa="sarja"}
```

Polynomin muodostaminen määritelmästä on muutaman rivin funktio.

```{.python tiedosto="esimerkit/07-taylor.py" osa="taylor"}
```

Approksimaation virhettä rajoittaa **Lagrangen jäännöstermi**:

$$|f(x) - P_n(x)| \le \frac{M}{(n+1)!}|x - a|^{n+1},$$

missä $M$ on derivaatan $|f^{(n+1)}|$ yläraja välillä. Sinin kaikki
derivaatat ovat itseisarvoltaan enintään 1, joten $P_5$:n virhe on
enintään $|x|^7/7!$. (Sinin kehitelmässä $x^6$:n kerroin on nolla, joten
$P_5 = P_6$ ja raja tulee seitsemännestä derivaatasta.) Raja pitää, ja
lähellä kehityskohtaa se on lähes tarkka.

![Funktio $\sin x$ ja sen Taylorin polynomit $P_1$, $P_3$, $P_5$ ja
$P_7$ nollan ympärillä. Jokainen lisätermi laajentaa aluetta, jolla
approksimaatio on hyvä.](kuvat/taylor.png){width=70%}

## Insinöörin approksimaatiot

Pienen kulman approksimaatiot $\sin x \approx x$ ja
$\cos x \approx 1 - x^2/2$ ovat Taylorin polynomeja. Ne tekevät
heilurin, optiikan ja värähtelyjen yhtälöistä ratkeavia. Approksimaation
pätevyysalue on hyvä tietää numeroina: kymmenen asteen kulmalla
$\sin x \approx x$ on puolen prosentin päässä.

```{.python tiedosto="esimerkit/07-taylor.py" osa="pieni"}
```

```{.tuloste tiedosto="esimerkit/07-taylor.odotettu"}
```

Muita yleisiä approksimaatioita pienillä $x$:n arvoilla ovat
$e^x \approx 1 + x$, $\ln(1 + x) \approx x$ ja
$(1 + x)^n \approx 1 + nx$. Viimeinen on luvun 4 herkkyyden lähde:
suhteellinen muutos $x$ potenssiin $n$ korotettuna on noin $n$ kertaa
suhteellinen muutos.

Funktion kehittäminen sarjaksi muiden kuin potenssien avulla on
**Fourier-sarja**, jossa kantafunktioina ovat sinit ja kosinit. Se
käsitellään taidossa *Kompleksiluvut ja Fourier-analyysi*.

## Miten kirjasto laskee eksponenttifunktion

Taylorin sarja $e^x = \sum x^k/k!$ suppenee kaikilla $x$:n arvoilla,
mutta suurilla $|x|$:n arvoilla hitaasti, ja negatiivisilla arvoilla
termit vuorottelevat merkiltään ja kumoavat toisiaan. Matematiikkakirjasto
kiertää ongelman **välin supistuksella** (*range reduction*):

$$e^x = 2^k e^r, \qquad x = k \ln 2 + r, \qquad |r| \le \tfrac12 \ln 2.$$

Kerroin $2^k$ lasketaan muuttamalla liukuluvun eksponenttikenttää
(`math.ldexp`), ja $e^r$ pienellä $r$:llä vaatii vain kymmenkunta
termiä. Oikeat kirjastot käyttävät sarjan sijaan minimax-polynomia, joka
jakaa virheen tasaisesti välille, ja $\ln 2$:n lisätarkkaa esitystä.

```{.python tiedosto="esimerkit/07-kirjasto.py" osa="exp"}
```

Ilman välin supistusta sarja kohdassa $-20$ on katastrofi: termit ovat
suurimmillaan noin $4 \cdot 10^7$ ja vuorottelevat merkiltään, mutta
tulos on suuruusluokkaa $10^{-9}$. Liukulukujen 16 merkitsevää numeroa
eivät riitä, ja tulos on kolminkertainen oikeaan nähden.

```{.python tiedosto="esimerkit/07-kirjasto.py" osa="suora"}
```

```{.tuloste tiedosto="esimerkit/07-kirjasto.odotettu"}
```

Arvolla $x = 300$ oma toteutus poikkeaa kirjastosta suhteellisesti
$10^{-14}$. Syy on $k \ln 2$:n pyöristysvirhe, joka kasvaa $k$:n mukana.
Kirjastot jakavat $\ln 2$:n kahteen osaan (Codyn ja Waiten menetelmä),
jotta tulo $k \ln 2$ lasketaan tarkasti. Kahden täsmälleen samaa asiaa
laskevan toteutuksen ero viimeisissä numeroissa on numeriikan arkea.

## Samat laskut Maximalla

Maximassa `sum` laskee summan ja `taylor` Taylorin polynomin. Asetus
`simpsum: true` pyytää Maximaa sieventämään summat suljettuun muotoon.

```{.maxima tiedosto="esimerkit/maxima/07-sarjat.mac" osa="sarjat"}
```

```{.tuloste tiedosto="esimerkit/maxima/07-sarjat.odotettu"}
```

## Käytännössä

- **Termit nollaan ei riitä.** Tarkista suppeneminen testillä, ei
  osasummien silmäilyllä: harmonisen sarjan osasumma miljoonalla
  termillä on vasta noin 14.
- **Taylorin polynomi on paikallinen.** Se on tarkka kehityskohdan
  lähellä ja voi olla hyödytön kaukana. Laske virheraja tai kokeile
  numeerisesti koko käyttöalueella.
- **Tunne approksimaatioiden rajat.** $\sin x \approx x$ on prosentin
  tarkkuudella hyvä noin 14 asteeseen asti. Kirjoita raja koodin
  kommenttiin.
- **Älä laske kirjastofunktioita itse sarjoilla.** Kirjastojen
  toteutukset käsittelevät välin supistuksen, kumoutumisen ja
  erikoistapaukset. Omaa sarjaa tarvitaan vain, kun kirjastoa ei ole,
  esimerkiksi mikrokontrollerissa tai laitteistossa (taito *Lukujen esitys
  ja kiinteän pilkun aritmetiikka*).

## Itsearviointi

- Osaat laskea sarjan summan SymPyllä ja Maximalla ja tutkia
  suppenemista suhdetestillä.
- Osaat selittää, miksi harmoninen sarja hajaantuu, vaikka sen termit
  lähestyvät nollaa.
- Osaat muodostaa Taylorin polynomin ja arvioida sen virheen Lagrangen
  jäännöstermillä.
- Osaat käyttää tavallisimpia insinööriapproksimaatioita ja kertoa
  niiden pätevyysalueen.
- Osaat selittää välin supistuksen periaatteen eksponenttifunktion
  laskennassa.

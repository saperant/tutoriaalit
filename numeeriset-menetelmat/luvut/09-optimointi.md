# Optimointi

Optimointi etsii parametrit, jotka minimoivat tai maksimoivat
tavoitefunktion: mallin sovitus dataan, rakenteen massa
lujuusehdoilla, säätimen parametrit, tuotannon kate. Taidossa
*Differentiaali- ja integraalilaskenta* ääriarvot etsittiin
derivaatan nollakohdista, ja gradienttimenetelmä, Lagrangen
kertojat ja SciPyn `minimize` esiteltiin lyhyesti. Tässä luvussa
menetelmiä verrataan suppenemisen kannalta, ja mukaan tulee lineaarinen
optimointi, jota käytetään suunnittelussa ja logistiikassa.

Maksimointi on miinusmerkkisen funktion minimointia, joten käsitellään
vain minimointia. Paikallinen minimi on piste, jonka ympäristössä
funktio ei ole pienempi. Yleisessä tapauksessa mikään menetelmä ei
takaa *globaalia* minimiä, mutta **konveksilla** funktiolla jokainen
paikallinen minimi on globaali.

## Yhden muuttujan haku: kultainen leikkaus

Jos funktio on **unimodaalinen** välillä, eli sillä on yksi minimi ja
se laskee ennen minimiä ja nousee sen jälkeen, minimin voi rajata kuten
juuren puolitushaussa. Kaksi sisäpistettä vertailemalla tiedetään,
kumpi reunaosa voidaan hylätä. **Kultainen leikkaus** sijoittaa
pisteet suhteessa $\varphi = (\sqrt5 - 1)/2 \approx 0{,}618$, jolloin
toinen pisteistä kelpaa seuraavalle kierrokselle: jokainen kierros
maksaa vain yhden uuden funktion arvon.

```{.python tiedosto="esimerkit/09-kultainen.py" osa="kultainen"}
```

```{.python tiedosto="esimerkit/09-kultainen.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/09-kultainen.odotettu"}
```

Väli lyhenee kertoimella 0,618 funktion arvoa kohden, eli suppeneminen
on lineaarista. Se on hitaampaa kuin derivaatan juuren etsiminen
Newtonilla, mutta ei tarvitse derivaattaa. SciPyn
`minimize_scalar` (Brentin menetelmä) ja Octaven `fminbnd` yhdistävät
kultaisen leikkauksen paraabelisovitukseen samaan tapaan kuin `brentq`
yhdistää puolituksen ja interpoloinnin.

Tarkkuudesta kannattaa huomata yksi asia: minimin kohdalla funktio on
loiva, ja $f(x^* + \delta) \approx f(x^*) + \tfrac12 f''\delta^2$.
Funktion arvoista erottuu siksi vain noin $\sqrt\varepsilon$
suuruinen muutos minimin paikassa. Minimin *paikka* saadaan noin
kahdeksalla numerolla, vaikka funktion *arvo* on 16 numeron tarkkuudella.

## Gradienttimenetelmä ja Newtonin menetelmä

Usean muuttujan funktiolle gradientti $\nabla f$ osoittaa nopeimman
kasvun suuntaan. **Gradienttimenetelmä** ottaa askeleen
vastagradientin suuntaan ja valitsee askelpituuden **viivahaulla**:
askelta lyhennetään, kunnes funktio pienenee riittävästi (Armijon ehto).
**Newtonin menetelmä** sovittaa funktioon toisen asteen mallin
Hessen matriisin $H$ avulla ja hyppää mallin minimiin ratkaisemalla
yhtälöryhmän $H\,d = -\nabla f$.

Vertailun testifunktio on **Rosenbrockin funktio**
$f(x, y) = (1-x)^2 + 100(y - x^2)^2$, jonka minimi $(1, 1)$ on kapean,
kaarevan laakson pohjalla. Funktio on optimointimenetelmien
klassinen koetinkivi.

```{.python tiedosto="esimerkit/09-gradientti.py" osa="rosenbrock"}
```

```{.python tiedosto="esimerkit/09-gradientti.py" osa="menetelmat"}
```

```{.python tiedosto="esimerkit/09-gradientti.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-gradientti.odotettu"}
```

![Gradienttimenetelmän polku (3000 ensimmäistä askelta) ja
Newtonin menetelmän kuusi askelta Rosenbrockin funktion
tasa-arvokäyrillä.](kuvat/rosenbrock.png){width=66%}

Gradienttimenetelmä tarvitsee yli 10 000 kierrosta, koska laakson
pohjalla gradientti osoittaa lähes kohtisuoraan laakson seiniä kohti eikä
pitkin laaksoa. Menetelmä siksakkaa. Syy on Hessen matriisin ehtoluku:
gradienttimenetelmän suppeneminen hidastuu ehtoluvun kasvaessa
samaan tapaan kuin klassisten iteraatioiden luvussa 7. Newton ottaa
huomioon kaarevuuden, ja kuusi askelta riittää, vaikka sen
ensimmäiset askeleet poikkeavat kaukana laaksosta.

Puhdas Newton on kuitenkin hauras: Hessen matriisi on laskettava, se ei
välttämättä ole positiivisesti definiitti kaukana minimistä, ja
yhtälöryhmän ratkaisu maksaa $O(n^3)$. **Kvasi-Newton-menetelmät**
rakentavat Hessen matriisin arvion gradienttien muutoksista. **BFGS**
on niistä tunnetuin, ja se on `scipy.optimize.minimize`-funktion
oletusmenetelmä rajoittamattomille tehtäville. Se suppenee
superlineaarisesti ja tarvitsee vain gradientin. Suurille tehtäville
**L-BFGS** säilyttää vain muutaman viimeisimmän päivityksen, ja
koneoppimisessa käytetään stokastisia gradienttimenetelmiä
(SGD, Adam), koska tavoitefunktio on keskiarvo valtavasta datasta.

Jos gradienttia ei ole saatavilla, se voidaan arvioida
erotusosamäärillä (luku 5), mutta silloin tarkkuus heikkenee ja hinta
kasvaa $n$ funktion arvolla kierrosta kohden. **Nelder–Meadin
simpleksimenetelmä** (`method="Nelder-Mead"`, Octaven `fminsearch`)
ei käytä derivaattoja lainkaan. Se on hidas, mutta kestää kohinaa ja
epäjatkuvuuksia.

## Rajoitteet

Käytännön tehtävissä on lähes aina rajoitteita: muuttujien rajat,
lineaariset ehdot (budjetti) ja epälineaariset ehdot (jännitys alle
sallitun). Rajoitettujen tehtävien perusajatukset ovat:

- **Sakkomenetelmä** lisää tavoitefunktioon termin, joka kasvaa
  rajoitteen rikkoutuessa. Se on yksinkertainen, mutta suurilla
  sakkokertoimilla tehtävästä tulee huonokuntoinen.
- **Lagrangen kertojat ja KKT-ehdot** yleistävät gradientin
  nollakohdan rajoitetulle tehtävälle. Taidon *Differentiaali- ja
  integraalilaskenta* luvussa 8 ne ratkaistiin pienelle tehtävälle.
- **SQP** (sequential quadratic programming, SciPyn `SLSQP` ja
  `trust-constr`) ratkaisee joka kierroksella toisen asteen
  approksimaation lineaarisin rajoittein. Se on yleiskäyttöinen
  valinta sileille rajoitetuille tehtäville.

## Lineaarinen optimointi

Kun tavoitefunktio ja kaikki rajoitteet ovat lineaarisia, tehtävä on
**lineaarinen ohjelma** (LP). Sen käypä alue on monitahokas, ja
optimi on aina jossakin sen kärjessä. LP:itä ratkaistaan
**simpleksimenetelmällä** (siirrytään kärjestä parempaan naapuriin) ja
**sisäpistemenetelmillä**. SciPyn `linprog` käyttää HiGHS-kirjastoa,
joka ratkaisee miljoonien muuttujien tehtäviä.

```{.python tiedosto="esimerkit/09-linprog.py" osa="malli"}
```

```{.python tiedosto="esimerkit/09-linprog.py" osa="tulos"}
```

LP-ratkaisu voi olla murtoluku, mutta puolikkaita pöytiä ei myydä.
**Kokonaislukuoptimointi** (MILP) vaatii muuttujilta kokonaislukuarvoja.
Se on laskennallisesti paljon vaikeampi (NP-vaikea), ja ratkaisijat
käyttävät haarautumista ja rajoittamista (branch and bound) LP:n
päällä.

```{.python tiedosto="esimerkit/09-linprog.py" osa="kokonaisluvut"}
```

```{.tuloste tiedosto="esimerkit/09-linprog.odotettu"}
```

LP-optimissa molemmat resurssit loppuvat kesken, ja **varjohinnat**
kertovat, kuinka paljon kate kasvaisi, jos puuta olisi kilo tai
työtä tunti enemmän. Varjohinta on resurssin raja-arvo päätöksenteossa:
kannattaa ostaa lisää puuta, jos se maksaa alle 3 euroa kilolta. LP-tuloksen
pyöristäminen kokonaisluvuiksi ei yleensä anna kokonaislukuoptimia,
eikä pyöristetty ratkaisu edes välttämättä ole käypä; MILP-ratkaisija
löytää oikean vastauksen.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/09-optimointi.m"}
```

```{.tuloste tiedosto="esimerkit/octave/09-optimointi.odotettu"}
```

Octavessa `fminbnd` on yhden muuttujan haku välillä, `fminsearch`
Nelder–Mead ja `fminunc` kvasi-Newton-menetelmä. Lineaarisiin
ohjelmiin Octavessa on `glpk`.

## Käytännössä

- **Anna gradientti, jos voit.** Analyyttinen tai automaattisesti
  derivoitu gradientti tekee menetelmästä nopeamman ja tarkemman kuin
  erotusosamäärät.
- **Skaalaa muuttujat** samaan suuruusluokkaan. Huono skaalaus näkyy
  Hessen matriisin ehtolukuna ja hidastaa kaikkia menetelmiä.
- **Käynnistä usesta alkupisteestä**, jos funktio ei ole konveksi.
  Paikallinen menetelmä löytää vain lähimmän paikallisen minimin.
- **Lue `minimize`-tuloksen `success` ja `message`.** Pysähtyminen
  iteraatiorajaan ei ole minimi.
- **Tunnista lineaarinen tehtävä.** Jos tavoite ja rajoitteet ovat
  lineaarisia, `linprog` tai `milp` on nopeampi ja luotettavampi kuin
  yleinen optimoija, ja se antaa varjohinnat.
- **Älä pyöristä LP-ratkaisua kokonaisluvuiksi**, kun kokonaisluvut ovat
  olennaisia; käytä MILP-ratkaisijaa.

## Itsearviointi

- Osaat toteuttaa kultaisen leikkauksen haun ja selittää, miksi se
  tarvitsee vain yhden funktion arvon kierrokselta.
- Osaat selittää, miksi minimin paikka saadaan vain noin
  $\sqrt\varepsilon$ tarkkuudella.
- Osaat vertailla gradienttimenetelmää, Newtonin menetelmää ja BFGS:ää
  suppenemisen, hinnan ja luotettavuuden kannalta.
- Osaat selittää, miten Hessen matriisin ehtoluku hidastaa
  gradienttimenetelmää.
- Osaat muotoilla tuotannon suunnittelun lineaariseksi ohjelmaksi,
  ratkaista sen ja tulkita varjohinnat.
- Osaat perustella, milloin tarvitaan kokonaislukuoptimointia.

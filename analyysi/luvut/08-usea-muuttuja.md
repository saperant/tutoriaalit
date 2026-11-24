# Usean muuttujan derivaatat

Todellisissa ongelmissa suureet riippuvat monesta muuttujasta: maaston
korkeus kahdesta koordinaatista, kustannus useista suunnitteluparametreista
ja neuroverkon virhe miljoonista painoista. Luvussa yleistetään derivaatta
usean muuttujan funktioille: osittaisderivaatat, gradientti, suunnattu
derivaatta, gradienttimenetelmä optimoinnissa sekä Hessen ja Jacobin
matriisit. Vektoreita ja matriiseja käytetään taidon *Lineaarialgebra*
merkinnöin.

## Osittaisderivaatat

Kahden muuttujan funktion $h(x, y)$ **osittaisderivaatta** $x$:n
suhteen, $\partial h/\partial x$ tai $h_x$, lasketaan derivoimalla $x$:n
suhteen ja pitämällä $y$ vakiona. Se kertoo, kuinka nopeasti $h$
muuttuu, kun liikutaan $x$-akselin suuntaan. Esimerkissä $h(x, y)$ on
mäen korkeus metreinä paikassa $(x, y)$ kilometreinä.

```{.python tiedosto="esimerkit/08-gradientti.py" osa="osittais"}
```

Toisen kertaluvun **sekaderivaatat** $h_{xy}$ ja $h_{yx}$ ovat samat
jatkuvasti derivoituville funktioille (Schwarzin lause). Siksi
derivointijärjestyksellä ei yleensä ole väliä.

![Mäen $h(x, y) = 300 - 20x^2 - 40y^2 + 10xy$ tasa-arvokäyrät
(korkeus metreinä) ja gradienttikenttä. Nuolet osoittavat jyrkimmän
nousun suuntaan ja ovat kohtisuorassa tasa-arvokäyriä
vastaan.](kuvat/tasa-arvo.png){width=58%}

## Gradientti ja suunnattu derivaatta

**Gradientti** kokoaa osittaisderivaatat vektoriksi:

$$\nabla h = \begin{pmatrix} h_x \\ h_y \end{pmatrix}.$$

Gradientilla on kaksi tärkeää ominaisuutta. Se osoittaa **jyrkimmän
nousun suuntaan**, ja sen pituus on nousun jyrkkyys. Lisäksi se on
**kohtisuorassa tasa-arvokäyrää vastaan**: tasa-arvokäyrää pitkin korkeus
ei muutu, joten liike sitä pitkin ei nouse lainkaan.

**Suunnattu derivaatta** yksikkövektorin $\mathbf u$ suuntaan on
gradientin ja suunnan pistetulo:

$$D_{\mathbf u} h = \nabla h \cdot \mathbf u.$$

Pistetulo on suurimmillaan, kun $\mathbf u$ on gradientin suuntainen, ja
nolla, kun suunta on kohtisuorassa gradienttia vastaan. Pisteessä
$(1, 1)$ gradientti osoittaa etelälounaaseen, joten itään ja koilliseen
kuljettaessa laskeudutaan.

```{.python tiedosto="esimerkit/08-gradientti.py" osa="gradientti"}
```

```{.python tiedosto="esimerkit/08-gradientti.py" osa="tasa-arvo"}
```

```{.tuloste tiedosto="esimerkit/08-gradientti.odotettu"}
```

Usean muuttujan virheen eteneminen (luku 4) tehdään gradientilla: jos
syötteiden virheet ovat $\Delta x$ ja $\Delta y$, tuloksen virhe on
noin $h_x \Delta x + h_y \Delta y$. Riippumattomille satunnaisille
virheille käytetään neliöiden summaa:
$\sigma_h \approx \sqrt{(h_x\sigma_x)^2 + (h_y\sigma_y)^2}$.

## Gradienttimenetelmä

Jos gradientti osoittaa jyrkimmän nousun suuntaan, sen vastavektori
osoittaa jyrkimmän laskun suuntaan. **Gradienttimenetelmä** (*gradient
descent*) etsii minimiä ottamalla toistuvasti askeleen gradienttia
vastaan:

$$\mathbf p_{n+1} = \mathbf p_n - \alpha \nabla f(\mathbf p_n).$$

Askelpituus $\alpha$ (koneoppimisessa *learning rate*) on menetelmän
kriittinen parametri.

```{.python tiedosto="esimerkit/08-gradienttimenetelma.py" osa="menetelma"}
```

Kustannusfunktion $f(x, y) = (x - 1)^2 + 10(y + 2)^2$ tasa-arvokäyrät
ovat litteitä ellipsejä: $y$-suunnassa funktio on kymmenen kertaa
jyrkempi. Liian pieni askel etenee hitaasti, ja liian suuri askel
ylittää minimin jyrkässä suunnassa ja kasvattaa virhettä joka
kierroksella.

```{.python tiedosto="esimerkit/08-gradienttimenetelma.py" osa="askel"}
```

Vakaan askeleen raja on $2/L$, missä $L$ on Hessen matriisin (alla)
suurin ominaisarvo eli funktion jyrkin kaarevuus. Kun kaarevuudet eri
suuntiin eroavat paljon, menetelmä joutuu käyttämään jyrkimmän suunnan
sallimaa pientä askelta kaikkiin suuntiin ja etenee loivassa suunnassa
hitaasti. Kirjastojen menetelmät, kuten SciPyn `minimize` BFGS-menetelmällä,
arvioivat kaarevuutta kierrosten aikana ja säätävät askeleen sen
mukaan, joten ne pääsevät perille kymmenesosassa kierroksista.

```{.python tiedosto="esimerkit/08-gradienttimenetelma.py" osa="scipy"}
```

```{.tuloste tiedosto="esimerkit/08-gradienttimenetelma.odotettu"}
```

Neuroverkkojen koulutus on gradienttimenetelmää miljoonissa
ulottuvuuksissa. Gradientti lasketaan ketjusäännöllä (luku 3), ja
askelta säädetään menetelmillä kuten Adam, jotka arvioivat kaarevuutta
kevyesti.

## Hessen matriisi ja ääriarvojen luokittelu

Usean muuttujan funktion kriittisessä pisteessä gradientti on nollavektori.
Kriittinen piste luokitellaan **Hessen matriisilla**, joka kokoaa toisen
kertaluvun osittaisderivaatat:

$$H = \begin{pmatrix} f_{xx} & f_{xy} \\ f_{yx} & f_{yy} \end{pmatrix}.$$

Hessen matriisi on yhden muuttujan toisen derivaatan yleistys. Jos sen
kaikki ominaisarvot ovat positiivisia, kriittinen piste on **minimi**;
jos kaikki ovat negatiivisia, **maksimi**; ja jos merkkejä on molempia,
piste on **satulapiste**, joka on yhteen suuntaan minimi ja toiseen
maksimi. Jos jokin ominaisarvo on nolla, testi ei ratkaise.

```{.python tiedosto="esimerkit/08-hessen.py" osa="luokittelu"}
```

Funktiolla $x^3 - 3x + y^2$ on kaksi kriittistä pistettä. Pisteessä
$(1, 0)$ funktio kaartuu ylöspäin molempiin suuntiin, ja pisteessä
$(-1, 0)$ se kaartuu $x$-suunnassa alaspäin mutta $y$-suunnassa
ylöspäin.

## Rajoitettu optimointi: Lagrangen kertojat

Luvun 4 tölkkitehtävässä sidosehto ratkaistiin ja sijoitettiin
kohdefunktioon. Usein se ei onnistu, tai rajoitteita on monta.
**Lagrangen kertojien menetelmä** perustuu geometriseen havaintoon:
rajoitetussa optimissa kohdefunktion tasa-arvokäyrä sivuaa rajoituksen
käyrää, joten niiden gradientit ovat yhdensuuntaiset:

$$\nabla f = \lambda \nabla g, \qquad g(\mathbf x) = c.$$

Käytännössä muodostetaan **Lagrangen funktio**
$L = f - \lambda(g - c)$ ja ratkaistaan yhtälöryhmä, jossa kaikki sen
osittaisderivaatat ovat nollia. Tölkkitehtävä ratkeaa nyt kahdella
muuttujalla ilman sijoitusta.

```{.python tiedosto="esimerkit/08-lagrange.py" osa="lagrange"}
```

Kertojalla $\lambda$ on hyödyllinen tulkinta: se on optimin arvon
derivaatta rajoituksen suhteen. Tölkillä $\lambda \approx 0{,}465$
tarkoittaa, että kuutiosenttimetri lisää tilavuutta vaatii noin
$0{,}47$ cm² lisää peltiä. Taloustieteessä kertojaa kutsutaan
**varjohinnaksi**.

```{.python tiedosto="esimerkit/08-lagrange.py" osa="tulkinta"}
```

Numeerisesti rajoitettu optimointi tehdään SciPyn `minimize`-funktiolla
menetelmällä SLSQP, joka hyväksyy yhtälö- ja epäyhtälörajoitteet.

```{.python tiedosto="esimerkit/08-lagrange.py" osa="scipy"}
```

```{.tuloste tiedosto="esimerkit/08-lagrange.odotettu"}
```

Epäyhtälörajoitteet (esimerkiksi "korkeus enintään 12 cm") yleistävät
menetelmän Karushin, Kuhnin ja Tuckerin ehdoiksi. Ne ja muut
optimointimenetelmät käsitellään taidossa *Numeeriset menetelmät*.

## Jacobin matriisi

Kun funktio kuvaa vektorin vektoriksi, sen derivaatta on **Jacobin
matriisi**: rivillä $i$ ovat $i$:nnen komponentin osittaisderivaatat.
Jacobin matriisi on kuvauksen paras lineaarinen approksimaatio, kuten
tangentti yhden muuttujan funktiolle. Napakoordinaattimuunnoksen
$x = r\cos\theta$, $y = r\sin\theta$ Jacobin determinantti on $r$:
pieni suorakulmio $dr\,d\theta$ kuvautuu alueeksi, jonka ala on
$r\,dr\,d\theta$. Tätä tarvitaan moninkertaisissa integraaleissa
(luku 9).

```{.python tiedosto="esimerkit/08-hessen.py" osa="jacobi"}
```

```{.tuloste tiedosto="esimerkit/08-hessen.odotettu"}
```

Jacobin matriisi on myös Newtonin menetelmän yleistys yhtälöryhmille
($\mathbf x_{n+1} = \mathbf x_n - J^{-1}\mathbf f(\mathbf x_n)$) ja
robotiikan nivelnopeuksien ja työkalun nopeuden välinen kuvaus.

## Samat laskut Maximalla

Maximan `diff` laskee osittaisderivaatat, ja `hessian` muodostaa Hessen
matriisin. Kriittiset pisteet ratkaistaan yhtälöryhmänä.

```{.maxima tiedosto="esimerkit/maxima/08-usea.mac" osa="usea"}
```

```{.tuloste tiedosto="esimerkit/maxima/08-usea.odotettu"}
```

## Käytännössä

- **Piirrä tasa-arvokäyrät.** Kahden muuttujan funktion muoto selviää
  parhaiten tasa-arvokäyristä; ne paljastavat satulapisteet, litteät
  laaksot ja useat minimit.
- **Skaalaa muuttujat.** Kun muuttujien suuruusluokat eroavat paljon,
  gradienttimenetelmä hidastuu. Muuttujien skaalaus samaan
  suuruusluokkaan on halpa ja tehokas korjaus.
- **Käytä kirjaston optimoijaa.** Oma gradienttimenetelmä on hyvä
  opetusväline, mutta `scipy.optimize.minimize` on nopeampi ja
  luotettavampi. Anna sille gradientti (`jac`), jos se tunnetaan.
- **Luokittele kriittiset pisteet.** Gradientin nollakohta voi olla
  satulapiste. Tarkista Hessen matriisin ominaisarvot.

## Itsearviointi

- Osaat laskea osittaisderivaatat ja gradientin sekä tulkita gradientin
  suunnan ja pituuden.
- Osaat laskea suunnatun derivaatan ja perustella, miksi gradientti on
  kohtisuorassa tasa-arvokäyrää vastaan.
- Osaat toteuttaa gradienttimenetelmän ja selittää askelpituuden
  vaikutuksen suppenemiseen.
- Osaat luokitella kriittisen pisteen Hessen matriisin ominaisarvoilla.
- Osaat ratkaista rajoitetun optimointitehtävän Lagrangen kertojilla ja
  tulkita kertojan arvon.
- Osaat muodostaa Jacobin matriisin ja tulkita sen determinantin
  pinta-alan muutoksena.

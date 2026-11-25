# Interpolointi ja sovitus

Mittaukset, taulukot ja raskaat simulaatiot antavat funktion arvoja vain
yksittäisissä pisteissä. **Interpolointi** rakentaa funktion, joka
kulkee täsmälleen annettujen pisteiden kautta, ja sillä arvioidaan
arvoja pisteiden välissä. **Sovitus** etsii yksinkertaisen mallin, joka
kulkee pisteiden *läheltä*. Se sopii kohinaiselle datalle, jota ei kannata
noudattaa tarkasti. Luvun keskeinen opetus on, että korkea polynomin
aste ei ole tarkkuuden tae: pisteiden sijainti ja esitystapa
ratkaisevat.

## Interpolointipolynomi Newtonin muodossa

Pisteiden $(x_0, y_0), \ldots, (x_n, y_n)$ kautta kulkee täsmälleen yksi
enintään astetta $n$ oleva polynomi. Sen voi esittää monella tavalla,
ja tapa vaikuttaa sekä laskentaan että tarkkuuteen:

- **Monomikanta** $c_0 + c_1x + \cdots + c_nx^n$ johtaa
  Vandermonden yhtälöryhmään, joka on hyvin huonokuntoinen.
- **Lagrangen muoto** $\sum y_i \ell_i(x)$, jossa $\ell_i$ on 1
  pisteessä $x_i$ ja 0 muissa, ei vaadi yhtälöryhmää, mutta uuden
  pisteen lisääminen muuttaa kaikkia termejä.
- **Newtonin muoto**
  $c_0 + c_1(x-x_0) + c_2(x-x_0)(x-x_1) + \cdots$ laskee kertoimet
  **jaetuista erotuksista**. Uusi piste lisää vain yhden termin.

```{.python tiedosto="esimerkit/04-newton-muoto.py" osa="erotukset"}
```

Arvo lasketaan Hornerin tapaan sisältä ulospäin, jolloin kertolaskuja on
$n$. Esimerkki interpoloi lämpötilamittauksia ja lisää myöhemmin yhden
mittauksen:

```{.python tiedosto="esimerkit/04-newton-muoto.py" osa="esimerkki"}
```

```{.tuloste tiedosto="esimerkit/04-newton-muoto.odotettu"}
```

Neljä ensimmäistä kerrointa säilyvät, kun mittaus lisätään. Arvio
hetkellä 2,5 muuttuu, koska uusi piste kertoo käyrän muodosta jotain,
mitä vanhat eivät kertoneet. Interpoloinnin virhe on

$$f(x) - p(x) = \frac{f^{(n+1)}(\xi)}{(n+1)!}\prod_{i=0}^{n}(x - x_i),$$

jossa $\xi$ on jokin piste välillä. Kaava on samaa muotoa kuin Taylorin
polynomin jäännöstermi, ja siitä näkyy, mitkä tekijät ratkaisevat:
funktion korkeat derivaatat ja **solmupolynomi**
$\prod (x - x_i)$, joka riippuu vain pisteiden sijainnista.

Kun pisteitä on paljon, kirjastojen suositus on **barysentrinen
interpolointi** (`scipy.interpolate.BarycentricInterpolator`). Se on
Lagrangen muodon stabiili muunnelma, joka maksaa $O(n)$ arvoa kohden.

## Rungen ilmiö ja Tšebyšovin solmut

Tasavälinen pisteistö tuntuu luontevalta, mutta korkealla asteella se
on huono. Carl Runge osoitti vuonna 1901, että funktiolle
$1/(1 + 25x^2)$ tasavälinen interpolointi *hajaantuu* välin reunoilla,
kun pisteitä lisätään. Syy on solmupolynomi: tasavälisillä pisteillä
se on välin reunoilla valtava verrattuna keskiosaan.

**Tšebyšovin solmut** $x_k = \cos\bigl((2k+1)\pi/(2n+2)\bigr)$ ovat
tiheämmässä reunoilla. Ne minimoivat solmupolynomin suurimman arvon,
ja niillä interpolointi suppenee kaikille sileille funktioille.

```{.python tiedosto="esimerkit/04-runge.py" osa="solmut"}
```

```{.python tiedosto="esimerkit/04-runge.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/04-runge.odotettu"}
```

![Interpolointipolynomi astetta 12. Tasavälisillä solmuilla polynomi
heilahtelee voimakkaasti välin reunoilla, Tšebyšovin solmuilla se
noudattaa funktiota.](kuvat/runge.png){width=68%}

Asteella 32 tasavälisen interpoloinnin virhe on jo $5 \cdot 10^3$, kun
Tšebyšovin solmuilla se on $10^{-3}$ ja pienenee eksponentiaalisesti.
Vielä korkeammilla asteilla tasavälisen interpoloinnin tulosta
hallitsevat pyöristysvirheet, ja luku vaihtelee koneesta toiseen. Jos data on pakko mitata tasavälisesti, korkean
asteen polynomin sijaan käytetään splinejä tai pienimmän neliösumman
sovitusta matalalla asteella.

## Splinit

**Kuutiosplini** on paloittain kolmannen asteen polynomi, jonka arvo,
ensimmäinen ja toinen derivaatta ovat jatkuvia solmukohdissa. Kunkin
palan aste pysyy kolmena, joten Rungen heilahtelua ei synny, ja käyrä
näyttää silmälle sileältä. Kertoimet ratkeavat kolmilävistäjäisestä
yhtälöryhmästä, joten splinin rakentaminen maksaa vain $O(n)$.

```{.python tiedosto="esimerkit/04-splini.py" osa="splini"}
```

```{.tuloste tiedosto="esimerkit/04-splini.odotettu"}
```

Kun välien määrä kaksinkertaistuu, virhe pienenee noin
16-kertaiseksi, eli virhe on $O(h^4)$. Se on paras mahdollinen
kuutiopolynomeilla. Suppeneminen alkaa vasta, kun pisteet ovat niin
tiheässä, että ne erottavat funktion kapean huipun; harvalla
pisteistöllä mikään menetelmä ei näe sitä, mitä pisteiden välissä
tapahtuu.

Splinin päätepisteiden ehto (`bc_type`) täytyy valita: *not-a-knot*
(oletus) vaatii, että kaksi ensimmäistä ja kaksi viimeistä palaa ovat
samaa polynomia, *natural* asettaa toisen derivaatan nollaksi ja
*clamped* antaa ensimmäisen derivaatan. Jos derivaatat tunnetaan,
`PchipInterpolator` ja `Akima1DInterpolator` ovat muotoa säilyttäviä
vaihtoehtoja, jotka eivät ylitä datan arvoja (hyödyllisiä esimerkiksi
pitoisuuksille, jotka eivät saa mennä negatiivisiksi).

## Pienimmän neliösumman sovitus

Kun dataa on enemmän kuin mallin parametreja ja siinä on kohinaa,
etsitään parametrit $c$, jotka minimoivat jäännösten neliösumman
$\|Ac - y\|_2^2$. Taidossa *Lineaarialgebra* tehtävä
ratkaistiin **normaaliyhtälöillä** $A^TAc = A^Ty$ ja QR-hajotelmalla.
Numeeriselta kannalta valinta on tärkeä:

$$\kappa(A^TA) = \kappa(A)^2.$$

Normaaliyhtälöt neliöivät ehtoluvun, kun taas QR-hajotelma
($A = QR$, ratkaistaan $Rc = Q^Ty$) toimii suoraan matriisin $A$ ehtoluvulla.
Esimerkki sovittaa asteen 10 polynomin dataan, jonka tarkka ratkaisu
tunnetaan.

```{.python tiedosto="esimerkit/04-pns.py" osa="data"}
```

```{.python tiedosto="esimerkit/04-pns.py" osa="ratkaisut"}
```

```{.python tiedosto="esimerkit/04-pns.py" osa="rajat"}
```

```{.tuloste tiedosto="esimerkit/04-pns.odotettu"}
```

Matriisin $A$ ehtoluku on $2 \cdot 10^7$, ja normaaliyhtälöiden
matriisin $4 \cdot 10^{14}$. Normaaliyhtälöt menettävät siksi noin 14
numeroa ja QR noin 7. Kaikki menetelmät pysyvät teoreettisen rajansa
alla, mutta rajat ovat hyvin erilaiset. `numpy.linalg.lstsq` käyttää
singulaariarvohajotelmaa ja on yhtä tarkka kuin QR, ja se toimii myös,
jos $A$ ei ole täysiasteinen.

Ehtoluku johtuu tässä monomikannasta: sarakkeet $x^9$ ja $x^{10}$
ovat välillä $[0, 1]$ lähes samansuuntaiset. Ortogonaalinen kanta
(Legendren tai Tšebyšovin polynomit, NumPyn `polynomial.Chebyshev.fit`)
poistaa ongelman jo ennen ratkaisijaa.

### Regularisointi

Kun data on kohinaista ja malli joustava, pienimmän neliösumman
ratkaisu voi sovittaa kohinan: kertoimet kasvavat suuriksi ja
vuorottelevat merkiltään. **Tikhonovin regularisointi** (harjanne-
regressio) minimoi lausekkeen $\|Ac - y\|^2 + \lambda\|c\|^2$, joka
rankaisee suuria kertoimia. Se vastaa tavallista PNS-tehtävää
laajennetulle matriisille $\begin{bmatrix} A \\ \sqrt\lambda I
\end{bmatrix}$, joten sen voi ratkaista samoilla välineillä.
Parametrin $\lambda$ valinta on mallinnuskysymys; tavallinen tapa on
ristiinvalidointi. Sama ajatus on koneoppimisen L2-regularisoinnin
taustalla.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/04-sovitus.m"}
```

```{.tuloste tiedosto="esimerkit/octave/04-sovitus.odotettu"}
```

Octavessa kenoviiva `A \ y` ratkaisee ylimäärätyn yhtälöryhmän
pienimmän neliösumman mielessä QR-hajotelmalla. Normaaliyhtälöitä
`(A' * A) \ (A' * y)` ei kirjoiteta, vaikka ne näkyvät monissa
oppikirjoissa. `polyfit` skaalaa ja keskittää datan pyydettäessä
(kolmas paluuarvo), mikä parantaa ehtolukua.

## Käytännössä

- **Älä interpoloi korkean asteen polynomilla tasavälistä dataa.**
  Käytä splinejä, matalan asteen paloja tai Tšebyšovin solmuja, jos
  pisteet saa valita.
- **Kohinaiselle datalle sovitus, ei interpolointi.** Interpolointi
  kulkee jokaisen mittausvirheen kautta.
- **Ratkaise PNS-tehtävä QR:llä tai SVD:llä**, ei normaaliyhtälöillä.
  Kirjastojen `lstsq`, `polyfit` ja Octaven `\` tekevät oikein.
- **Skaalaa ja keskitä muuttujat.** Vuosiluvut $2000 \ldots 2030$
  potensseina ovat huonokuntoisia; $(t - 2015)/15$ on hyvä.
- **Ekstrapolointi on eri asia kuin interpolointi.** Polynomi kasvaa
  pisteistön ulkopuolella rajatta, eikä virhekaava anna mitään takuuta.
- **Valitse splinin reunaehdot tietoisesti**, ja käytä muotoa
  säilyttävää interpolointia, kun data on monotonista tai
  ei-negatiivista.

## Itsearviointi

- Osaat laskea interpolointipolynomin jaetuilla erotuksilla ja
  lisätä siihen pisteen.
- Osaat selittää interpoloinnin virhekaavan ja solmupolynomin merkityksen.
- Osaat selittää Rungen ilmiön ja miksi Tšebyšovin solmut toimivat.
- Osaat käyttää kuutiosplinejä ja mitata niiden virheen kertaluvun.
- Osaat perustella, miksi normaaliyhtälöt ovat numeerisesti huonompia
  kuin QR-hajotelma, ja laskea ehtolukujen suhteen.
- Osaat selittää regularisoinnin idean ja milloin sitä tarvitaan.

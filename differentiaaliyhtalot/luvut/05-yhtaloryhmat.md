# Yhtälöryhmät ja tilaesitys

Monimutkaisemmissa järjestelmissä on useita toisiinsa kytkeytyneitä
suureita: kaksi säiliötä, monisilmukkainen piiri, peto ja saalis,
heilurin kulma ja kulmanopeus. Ne kirjoitetaan **ensimmäisen kertaluvun
yhtälöryhmäksi**

$$\mathbf{x}' = A\,\mathbf{x} + \mathbf{b}(t)$$

eli **tilaesitykseksi**. Tilaesitys on numeeristen ratkaisijoiden ja
säätötekniikan yhteinen kieli: jokainen korkeamman kertaluvun yhtälö
voidaan kirjoittaa siihen muotoon, ja lineaarisen järjestelmän koko
käyttäytyminen on matriisin $A$ ominaisarvoissa.

## Korkea kertaluku ensimmäiseksi

Yhtälö $y'' + 5y' + 4y = 0$ muuttuu ryhmäksi, kun tilamuuttujiksi
valitaan $x_1 = y$ ja $x_2 = y'$:

$$\begin{pmatrix} x_1 \\ x_2 \end{pmatrix}' =
\begin{pmatrix} 0 & 1 \\ -4 & -5 \end{pmatrix}
\begin{pmatrix} x_1 \\ x_2 \end{pmatrix}.$$

Ensimmäinen rivi sanoo vain, että $x_1' = x_2$; toinen rivi on
alkuperäinen yhtälö. Sama temppu toimii mille tahansa kertaluvulle:
$n$:nnen kertaluvun yhtälöstä tulee $n$ ensimmäisen kertaluvun yhtälöä.

## Ominaisarvot ja -vektorit

Kun $A$:lla on ominaisarvo $\lambda$ ja ominaisvektori $\mathbf{v}$,
$\mathbf{x} = e^{\lambda t}\mathbf{v}$ on ratkaisu. Yleinen ratkaisu on
näiden lineaarikombinaatio (taito *Lineaarialgebra* käsittelee
ominaisarvot). Ominaisarvot ovat samat kuin luvun 4 karakteristisen
yhtälön juuret: tilaesitys ei muuta järjestelmää, vain sen kirjoitusta.

```{.python tiedosto="esimerkit/05-tilaesitys.py" osa="tila"}
```

## Matriisieksponentti

Skalaariyhtälön $x' = ax$ ratkaisu on $e^{at}x_0$. Ryhmälle sama pätee
**matriisieksponentilla**:

$$\mathbf{x}(t) = e^{At}\,\mathbf{x}_0, \qquad
e^{At} = I + At + \frac{(At)^2}{2!} + \cdots$$

Sarjaa ei lasketa sellaisenaan, vaan SymPy käyttää ominaisarvohajotelmaa
ja SciPyn `expm` skaalausta ja Padén approksimaatiota. Tulokset ovat
samat kymmenen desimaalin tarkkuudella.

```{.python tiedosto="esimerkit/05-tilaesitys.py" osa="eksponentti"}
```

```{.python tiedosto="esimerkit/05-tilaesitys.py" osa="dsolve"}
```

```{.tuloste tiedosto="esimerkit/05-tilaesitys.odotettu"}
```

Octavessa `eig` ja `expm` ovat perustyökaluja, ja syntaksi on lähellä
matemaattista merkintää.

```{.octave tiedosto="esimerkit/octave/05-tila.m" osa="tila"}
```

```{.tuloste tiedosto="esimerkit/octave/05-tila.odotettu"}
```

## Kytketyt säiliöt

Tilaesitys syntyy myös suoraan, kun mallissa on useita varastoja. Kaksi
säiliötä on sarjassa: puhdas vesi virtaa ensimmäiseen, sen ylivuoto
toiseen ja siitä ulos. Ensimmäisessä on alussa 5 kg suolaa. Kummankin
säiliön tase antaa yhden yhtälön, ja ensimmäisen säiliön ulosvirtaus on
toisen sisäänvirtaus:

```{.python tiedosto="esimerkit/05-sailiot.py" osa="ryhma"}
```

Ominaisarvot $-1/10$ ja $-1/5$ ovat säiliöiden aikavakioiden
käänteisluvut ($V/q$ = 10 ja 5 minuuttia), koska matriisi on
kolmiomatriisi. Toisen säiliön suolamäärä kasvaa ensin ja laskee sitten,
ja huippu on derivaatan nollakohdassa $10\ln 2 \approx 6{,}9$ minuuttia.

```{.python tiedosto="esimerkit/05-sailiot.py" osa="huippu"}
```

```{.python tiedosto="esimerkit/05-sailiot.py" osa="numeerinen"}
```

```{.tuloste tiedosto="esimerkit/05-sailiot.odotettu"}
```

Sama rakenne, ketju toisiaan ruokkivia ensimmäisen kertaluvun
varastoja, kuvaa lääkeaineen kulkua elimistössä, radioaktiivista
hajoamissarjaa ja monivaiheista RC-suodinta.

## Vaihetaso ja tasapainojen luokittelu

Kahden muuttujan järjestelmän ratkaisun voi piirtää **vaihetasoon**:
akseleina $x_1$ ja $x_2$, ja aika kulkee käyrää pitkin. Lineaarisen
järjestelmän ainoa tasapaino on origo, ja sen tyyppi riippuu $A$:n
ominaisarvoista. Kahdelle muuttujalle riittää kaksi lukua, **jälki**
$\operatorname{tr} A = \lambda_1 + \lambda_2$ ja **determinantti**
$\det A = \lambda_1 \lambda_2$:

| Ehto | Ominaisarvot | Tyyppi |
|------|--------------|--------|
| $\det A < 0$ | reaaliset, eri merkkiset | satulapiste (epästabiili) |
| $\det A > 0$, $\operatorname{tr}^2 > 4\det$ | reaaliset, samanmerkkiset | solmu |
| $\det A > 0$, $\operatorname{tr}^2 < 4\det$ | kompleksiset | spiraali |
| $\operatorname{tr} A = 0$, $\det A > 0$ | puhtaasti imaginaariset | keskus |

Solmu ja spiraali ovat stabiileja, kun $\operatorname{tr} A < 0$, ja
epästabiileja, kun $\operatorname{tr} A > 0$.

```{.python tiedosto="esimerkit/05-luokittelu.py" osa="luokittelu"}
```

```{.tuloste tiedosto="esimerkit/05-luokittelu.odotettu"}
```

Luvun 4 värähtelijät ovat tässä taulukossa tuttuja: ylivaimennettu on
stabiili solmu, alivaimennettu stabiili spiraali ja vaimentamaton keskus.

## Epälineaarinen heiluri

Heilurin yhtälö $\theta'' = -(g/L)\sin\theta$ on epälineaarinen.
Pienillä kulmilla $\sin\theta \approx \theta$, ja yhtälöstä tulee
harmoninen värähtelijä, jonka jaksonaika $2\pi\sqrt{L/g}$ ei riipu
amplitudista. Tämä **linearisointi** on fysiikan tunnetuin
approksimaatio, mutta kuinka hyvä se on?

Tarkka jaksonaika saadaan elliptisestä integraalista
$4\sqrt{L/g}\,K(\sin^2(\theta_0/2))$. Simulointi `solve_ivp`-funktiolla
ja tapahtuman (*event*) avulla mittaa puolijakson ajasta, jolloin
kulmanopeus seuraavan kerran vaihtaa merkkiä.

```{.python tiedosto="esimerkit/05-heiluri.py" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/05-heiluri.odotettu"}
```

Viiden asteen heilahduksella linearisointi on erinomainen, 30 asteella
virhe on kaksi prosenttia ja suurilla kulmilla malli on käyttökelvoton.
Linearisoinnin pätevyysalue kannattaa aina kirjoittaa näkyviin.

![Vaimennetun heilurin vaihetaso. Mustat pisteet (alin asento) ovat
stabiileja spiraaleja, valkoiset (ylin asento) satulapisteitä. Vihreät
ratkaisut kiertävät kerran ympäri tai asettuvat lähimpään
alimpaan asentoon.](kuvat/vaihetaso.png){width=80%}

Vaihetasosta näkee jotain, mitä mikään yksittäinen ratkaisu ei kerro:
riittävän suurella alkunopeudella heiluri kiertää ylimmän asennon yli ja
asettuu seuraavaan alimpaan asentoon $2\pi$:n päähän. Luku 8 palaa
epälineaaristen tasapainojen luokitteluun Jacobin matriisin avulla.

## Käytännössä

- **Kirjoita malli tilaesitykseen.** Kaikki numeeriset ratkaisijat
  tarvitsevat muodon $\mathbf{x}' = \mathbf{f}(t, \mathbf{x})$, ja
  ominaisarvot kertovat lineaarisen järjestelmän käytöksen.
- **Käytä kirjaston matriisieksponenttia.** `expm` on numeerisesti
  vakaa; Taylorin sarjan suora laskeminen ei ole.
- **Luokittele tasapaino jäljestä ja determinantista.** Kaksi lukua
  kertoo, värähteleekö järjestelmä ja vaimeneeko se.
- **Tarkista linearisoinnin pätevyys simuloimalla.** Linearisoitu malli
  on hyvä suunnittelun lähtökohta, mutta lopullinen tarkistus tehdään
  epälineaarisella mallilla.

## Itsearviointi

- Osaat muuntaa korkeamman kertaluvun yhtälön ensimmäisen kertaluvun
  ryhmäksi.
- Osaat ratkaista lineaarisen ryhmän ominaisarvojen ja
  matriisieksponentin avulla SymPyllä, SciPyllä ja Octavella.
- Osaat luokitella kahden muuttujan lineaarisen järjestelmän
  tasapainon jäljen ja determinantin perusteella.
- Osaat lukea vaihetasokuvaa ja tunnistaa siitä tasapainot ja niiden
  tyypit.
- Osaat arvioida linearisoinnin virheen vertaamalla epälineaariseen
  malliin.

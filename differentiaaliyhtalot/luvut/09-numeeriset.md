# Numeeriset ratkaisijat

Useimmilla käytännön yhtälöillä ei ole lausekeratkaisua: epälineaarinen
kitka, mitattu heräte, kymmenien muuttujien malli. Numeerinen ratkaisija
etenee aika-askel kerrallaan derivaatan ohjaamana. Tässä luvussa
toteutetaan kaksi klassista menetelmää, jotta niiden idea tulee tutuksi,
ja käytetään sitten kirjaston ratkaisijoita oikein: toleranssit,
tapahtumat ja jäykät yhtälöt. Menetelmien virheanalyysi ja
kertalukujen johtaminen kuuluvat taitoon *Numeeriset menetelmät*.

## Euler ja RK4

**Eulerin menetelmä** kulkee tangentin suuntaan:
$y_{n+1} = y_n + h\,f(t_n, y_n)$. Se on yksinkertainen mutta epätarkka,
koska tangentti kääntyy askeleen aikana. **Klassinen Runge–Kutta (RK4)**
arvioi kulmakertoimen neljästi askeleen aikana ja käyttää niiden
painotettua keskiarvoa.

```{.python tiedosto="esimerkit/09-euler-rk4.py" osa="menetelmat"}
```

Yhtälön $y' = -2ty$, $y(0) = 1$ tarkka ratkaisu $e^{-t^2}$ antaa
virheen jokaiselle askelpituudelle:

```{.python tiedosto="esimerkit/09-euler-rk4.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-euler-rk4.odotettu"}
```

Kun askel puolittuu, Eulerin virhe puolittuu ja RK4:n virhe pienenee
noin kuusitoistakertaisesti. Euler on **ensimmäisen kertaluvun** ja RK4
**neljännen kertaluvun** menetelmä: virhe on verrannollinen askeleen
ensimmäiseen ja neljänteen potenssiin. Samalla laskentamäärällä (RK4
laskee neljä derivaattaa askeleella) RK4 on useita kertaluokkia
tarkempi.

## Kirjaston ratkaisija: solve_ivp

Kirjaston ratkaisijat valitsevat askeleen itse: ne arvioivat virheen
jokaisella askeleella kahdella eri kertaluvun kaavalla ja pienentävät tai
suurentavat askelta, jotta arvioitu virhe pysyy toleranssin sisällä.
SciPyn `solve_ivp` käyttää oletuksena menetelmää RK45 (Dormand–Prince),
joka vastaa MATLABin ja Octaven `ode45`:tä.

Tärkeimmät valinnat ovat:

- `rtol` ja `atol`: suhteellinen ja absoluuttinen toleranssi. Oletus
  `rtol=1e-3` on karkea; insinöörilaskuissa käytetään usein
  `1e-6`–`1e-9`.
- `t_eval` tai `dense_output=True`: missä pisteissä ratkaisu halutaan.
- `events`: funktio, jonka nollakohta pysäyttää ratkaisun tai
  kirjataan, esimerkiksi osuma maahan tai rajan ylitys.

Esimerkissä pallo putoaa ilmanvastuksen kanssa, ja tapahtuma pysäyttää
simuloinnin, kun korkeus on nolla.

```{.python tiedosto="esimerkit/09-solve-ivp.py" osa="putoaminen"}
```

```{.tuloste tiedosto="esimerkit/09-solve-ivp.odotettu"}
```

Oletustoleranssilla osumahetki on oikein kolmen desimaalin tarkkuudella,
ja tiukempi toleranssi lisää funktiokutsuja. Toleranssi kannattaa
valita tarvittavan tarkkuuden mukaan ja tarkistaa tulos tiukemmalla
toleranssilla: jos tulos ei muutu, toleranssi riittää.

## Jäykät yhtälöt

Yhtälö on **jäykkä**, kun siinä on hyvin eri nopeuksilla tapahtuvia
ilmiöitä ja nopea ilmiö on jo vaimentunut. Esimerkiksi
$y' = -1000\,(y - \cos t)$ seuraa hitaasti muuttuvaa kosinia, mutta
sen nopea aikavakio on millisekunti. Eksplisiittinen menetelmä joutuu
pitämään askeleen nopean aikavakion luokkaa koko simuloinnin ajan,
vaikka ratkaisu muuttuu hitaasti: muuten numeerinen ratkaisu räjähtää.

```{.python tiedosto="esimerkit/09-jaykka.py" osa="jaykka"}
```

**Implisiittiset** menetelmät (Radau, BDF) ratkaisevat jokaisella
askeleella yhtälön, jossa uusi arvo esiintyy molemmin puolin. Askel on
kalliimpi, mutta menetelmä on vakaa suurillakin askelilla. Eksplisiittisen
ja implisiittisen Eulerin ero näkyy suoraan: eksplisiittinen menetelmä on
vakaa vain, kun $h \le 2/1000$.

```{.python tiedosto="esimerkit/09-jaykka.py" osa="euler"}
```

```{.tuloste tiedosto="esimerkit/09-jaykka.odotettu"}
```

![Askeleen pituus jäykässä yhtälössä. RK45 jumittuu vakausrajalle
(katkoviiva), vaikka ratkaisu muuttuu hitaasti; Radau kasvattaa
askelta heti, kun nopea alkuilmiö on ohi.](kuvat/jaykka.png){width=78%}

Octavessa jäykille yhtälöille on `ode23s` (Rosenbrock) ja `ode15s`
(BDF). Matalan kertaluvun `ode23s` on edullisin maltillisilla
toleransseilla:

```{.octave tiedosto="esimerkit/octave/09-jaykka.m" osa="jaykka"}
```

```{.tuloste tiedosto="esimerkit/octave/09-jaykka.odotettu"}
```

Jäykkyyden tunnistaa käytännössä siitä, että eksplisiittinen ratkaisija
on odottamattoman hidas tai ottaa valtavan määrän askeleita. Tyypillisiä
jäykkiä malleja ovat kemialliset reaktiot, piirisimulointi (SPICE
käyttää implisiittisiä menetelmiä) ja lämmönjohtuminen.

## Ratkaisijan valinta

| Tilanne | SciPy | Octave |
|---------|-------|--------|
| tavallinen, ei jäykkä | `RK45` (oletus) | `ode45` |
| korkea tarkkuus, sileä | `DOP853` | `ode45` tiukalla toleranssilla |
| karkea, nopea | `RK23` | `ode23` |
| jäykkä | `Radau`, `BDF` | `ode15s`, `ode23s` |
| ei tiedossa | `LSODA` (vaihtaa automaattisesti) | `ode15s` |

## Käytännössä

- **Vertaa tunnettuun ratkaisuun ennen kuin luotat ratkaisijaan.**
  Yksinkertaistettu tapaus, jolle tarkka ratkaisu on olemassa, paljastaa
  mallin ja koodin virheet.
- **Säädä toleranssia ja tarkista herkkyys.** Puolita `rtol` ja katso,
  muuttuuko tulos. Jos muuttuu, toleranssi on liian väljä.
- **Käytä tapahtumia ajanhetkien etsimiseen.** Osuman, rajan ylityksen
  tai ääriarvon hetki saadaan tarkasti ilman tiheää tulostusta.
- **Vaihda implisiittiseen, kun askelia on epäilyttävän paljon.**
  Jäykkä yhtälö on yleinen syy hitaaseen simulointiin.
- **Älä käytä omaa Euleria tuotannossa.** Omat toteutukset ovat
  oppimista varten; kirjaston ratkaisijat hallitsevat askeleen, virheen
  ja jäykkyyden.

## Itsearviointi

- Osaat toteuttaa Eulerin menetelmän ja RK4:n ja selittää niiden
  tarkkuuseron.
- Osaat käyttää `solve_ivp`-funktiota toleransseilla, tulostuspisteillä
  ja tapahtumilla.
- Osaat tunnistaa jäykän yhtälön ja valita sille implisiittisen
  ratkaisijan SciPyssä ja Octavessa.
- Osaat varmistaa numeerisen tuloksen luotettavuuden vertaamalla
  tunnettuun ratkaisuun ja tiukempaan toleranssiin.

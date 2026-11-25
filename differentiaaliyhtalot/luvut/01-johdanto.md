# Johdanto {.runko-johdanto}

**Differentiaaliyhtälö** kertoo, miten jokin suure muuttuu, sen sijaan
että kertoisi suureen arvon. Kahvi jäähtyy sitä nopeammin, mitä
kuumempaa se on. Kondensaattori varautuu sitä hitaammin, mitä lähempänä
syöttöjännitettä sen jännite on. Jousi vetää massaa sitä voimakkaammin,
mitä kauempana massa on lepoasemastaan. Kaikki nämä ovat lauseita
muutosnopeudesta eli derivaatasta, ja niistä seuraa koko järjestelmän
käyttäytyminen ajan funktiona.

Insinöörin työssä differentiaaliyhtälöt ovat kaikkialla: sähköpiireissä,
mekaniikassa, lämmönsiirrossa, säätötekniikassa, populaatiomalleissa ja
signaalinkäsittelyssä. Tämä tutoriaali opettaa kolme taitoa:

1. **Mallintaminen:** sanallisesta kuvauksesta yhtälöksi. Useimmat mallit
   ovat taseita: muutos on sisään tuleva miinus ulos lähtevä.
2. **Ratkaiseminen:** analyyttisesti, kun yhtälö on lineaarinen tai
   muuten siisti, ja numeerisesti aina muulloin. Analyyttinen ratkaisu
   kertoo rakenteen (aikavakiot, värähtelytaajuudet, stabiilisuuden),
   numeerinen ratkaisu toimii myös epälineaarisille malleille.
3. **Tulkitseminen:** mitä navat, ominaisarvot ja aikavakiot kertovat
   järjestelmästä ilman, että koko ratkaisua tarvitsee laskea.

## Ensimmäinen esimerkki: jäähtyvä kahvi

Newtonin jäähtymislaki sanoo, että kappaleen lämpötilan muutosnopeus on
verrannollinen lämpötilaeroon ympäristöön:

$$\frac{dT}{dt} = -k\,(T - T_y).$$

Miinusmerkki kertoo, että kuuma kappale jäähtyy ja kylmä lämpenee.
Mallin parametrit ovat ympäristön lämpötila $T_y$, alkulämpötila $T_0$
ja jäähtymisvakio $k$, joka riippuu kupista ja ilmavirroista.

```{.python tiedosto="esimerkit/01-kahvi.py" osa="malli"}
```

SymPyn `dsolve` ratkaisee yhtälön symbolisesti. Kun parametrit jätetään
symboleiksi, ratkaisusta näkee rakenteen: lämpötila lähestyy
eksponentiaalisesti huoneen lämpötilaa, ja vastaus kysymykseen ”milloin
kahvi on juotavaa” on logaritmi.

```{.python tiedosto="esimerkit/01-kahvi.py" osa="symbolinen"}
```

SciPyn `solve_ivp` ratkaisee saman yhtälön numeerisesti. Se ei tiedä
mitään ratkaisun muodosta, vaan etenee pienin askelin derivaatan
ohjaamana. Siksi se toimii myös yhtälöille, joilla ei ole lauseketta
ratkaisuksi.

```{.python tiedosto="esimerkit/01-kahvi.py" osa="numeerinen"}
```

```{.tuloste tiedosto="esimerkit/01-kahvi.odotettu"}
```

Numeerinen ja tarkka ratkaisu ovat samat neljän desimaalin tarkkuudella.
Tällainen vertailu tunnettuun ratkaisuun on tämän tutoriaalin
perusmenetelmä: kun ratkaisija toimii helpossa tapauksessa, sen
tuloksiin voi luottaa vaikeammassa.

Sama tehtävä GNU Octavella näyttää, että työkalut ovat vaihdettavissa:
`ode45` on MATLAB-yhteensopiva vastine SciPyn oletusmenetelmälle.

```{.octave tiedosto="esimerkit/octave/01-kahvi.m" osa="kahvi"}
```

```{.tuloste tiedosto="esimerkit/octave/01-kahvi.odotettu"}
```

## Esitiedot ja rajaus

Tutoriaali on tarkoitettu insinööriopiskelijalle ja ohjelmoijalle, joka
mallintaa fysikaalisia järjestelmiä, säätöä tai signaaleja. Derivaatta,
integraali, osamurtohajotelma ja Taylorin polynomi oletetaan tutuiksi
(taito *Differentiaali- ja integraalilaskenta*), samoin matriisit ja
ominaisarvot (taito *Lineaarialgebra*). Työkalujen perusteet esitellään
taidossa *Matematiikan perusteet ohjelmallisesti*.

Esimerkit tarvitsevat Python 3.12:n, SymPyn, NumPyn, SciPyn ja
Matplotlibin sekä Maximan ja GNU Octaven. Paketin kehityskontissa
kaikki on valmiina. Jokainen esimerkki on testattu ohjelma, ja kirjassa
näkyvät tulosteet ovat ohjelmien todellisia tulosteita.

## Tutoriaalin rakenne

| Luku | Aihe | Työkalut |
|------|------|----------|
| 2 | Mallintaminen | taseet, aikavakio, `dsolve` |
| 3 | Ensimmäisen kertaluvun yhtälöt | erottelu, integroiva tekijä, tasapainot |
| 4 | Toisen kertaluvun yhtälöt | karakteristinen yhtälö, resonanssi |
| 5 | Yhtälöryhmät ja tilaesitys | ominaisarvot, `expm`, vaihetaso |
| 6 | Laplace-muunnos | `laplace_transform`, `apart`, konvoluutio |
| 7 | Siirtofunktio | navat, askelvaste, `scipy.signal` |
| 8 | Stabiilisuus | Routh–Hurwitz, Jacobin matriisi |
| 9 | Numeeriset ratkaisijat | Euler, RK4, `solve_ivp`, jäykkyys |

Luvut 2–5 käsittelevät yhtälöitä aikatasossa, luvut 6–8 s-tasossa eli
Laplace-muunnoksen kautta, ja luku 9 kokoaa numeerisen ratkaisemisen.
Kiireinen lukija voi lukea luvut 2, 4, 6 ja 7, joista saa
insinöörin perustyökalut värähtelijöihin ja piireihin.

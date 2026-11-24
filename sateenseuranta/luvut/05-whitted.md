# Whitted-säteenseuranta

Turner Whitted julkaisi vuonna 1980 algoritmin, joka teki
säteenseurannasta tunnetun: kun säde osuu pintaan, lähetetään uudet
säteet valoihin varjojen selvittämiseksi, peilisuuntaan
heijastusta varten ja taitesuuntaan läpinäkyvää ainetta varten.
Jokainen uusi säde käsitellään samalla tavalla rekursiivisesti.
Algoritmi tuottaa terävät varjot, peiliheijastukset ja lasin
taittumisen oikein ilman erikoistapauksia, mutta ei pehmeitä varjoja,
himmeitä heijastuksia eikä epäsuoraa valoa. Sen rajat motivoivat
renderöintiyhtälön, joten se kannattaa rakentaa ensin.

## Algoritmi

```{.cpp tiedosto="esimerkit/05-whitted.cpp" osa="jalita"}
```

Funktio on rekursiivinen, ja syvyysraja pysäyttää kahden peilin
väliin jäävän säteen. Kolme pintatyyppiä käsitellään eri tavoin:

- **Diffuusi pinta** valaistaan pistevalosta Lambertin mallilla, jos
  varjosäde pääsee valoon asti. Varjosäteen yläraja on etäisyys
  valoon: valon takana oleva kappale ei varjosta.
- **Peili** lähettää yhden säteen heijastussuuntaan
  $\mathbf{d} - 2(\mathbf{d}\cdot\mathbf{n})\mathbf{n}$, ja
  heijastunut väri kerrotaan peilin heijastuskyvyllä.
- **Lasi** lähettää kaksi sädettä, heijastuneen ja taittuneen, ja
  painottaa ne Fresnelin kertoimella.

Normaali käännetään aina säteen tulopuolelle. Pallon normaali osoittaa
ulos, mutta lasin sisältä tuleva säde osuu pintaan sisäpuolelta, ja
heijastus, taittuminen ja lähtöpisteen siirto tarvitsevat tulopuolen
normaalin. Taittuneen säteen lähtöpiste siirretään vastakkaiselle
puolelle, koska säde jatkaa pinnan läpi.

Pistevalon radianssia ei voi määritellä, koska valolla ei ole
pinta-alaa. Sen sijaan pinnan saama irradianssi on
$E = I\cos\theta / r^2$, missä $I = \Phi / (4\pi)$ on tasaisesti
joka suuntaan säteilevän valon intensiteetti, $\Phi$ sen teho ja $r$
etäisyys. Lambertin pinnan radianssi on silloin $(\rho/\pi)\,E$.
Koodissa intensiteetti on vakio `VALO_I`, ja ympäristövalo on pieni
vakio, joka korvaa puuttuvan epäsuoran valon.

## Taittuminen ja Snellin laki

Valon nopeus aineessa on $c/n$, missä $n$ on taitekerroin: ilma 1,0,
vesi 1,33, lasi noin 1,5 ja timantti 2,4. Rajapinnassa säteen suunta
muuttuu Snellin lain mukaan:
$n_1 \sin\theta_1 = n_2 \sin\theta_2$. Vektorimuodossa, kun
$\eta = n_1 / n_2$, $\mathbf{n}$ osoittaa tulopuolelle ja
$\cos\theta_1 = -\mathbf{d}\cdot\mathbf{n}$, taittunut suunta on

$$\mathbf{t} = \eta\,\mathbf{d} + \big(\eta\cos\theta_1 -
\sqrt{1 - \eta^2(1 - \cos^2\theta_1)}\big)\,\mathbf{n}.$$

Jos neliöjuuren alla oleva lauseke on negatiivinen, taittunutta
sädettä ei ole: valo heijastuu kokonaan. Tämä *kokonaisheijastus*
tapahtuu, kun valo tulee tiheämmästä aineesta loivassa kulmassa.
Kriittinen kulma on $\sin\theta_c = n_2 / n_1$; lasista ilmaan se on
noin 42°.

```{.cpp tiedosto="esimerkit/yhteinen/materiaali.hpp" osa="fresnel"}
```

## Fresnelin yhtälöt

Rajapinta heijastaa osan valosta ja päästää loput läpi. Osuus riippuu
kulmasta ja polarisaatiosta. Polaroimattomalle valolle heijastuskerroin
on kahden polarisaation keskiarvo,

$$F = \tfrac{1}{2}\left(r_s^2 + r_p^2\right),\quad
r_s = \frac{\eta\cos\theta_1 - \cos\theta_2}{\eta\cos\theta_1 +
\cos\theta_2},\quad
r_p = \frac{\cos\theta_1 - \eta\cos\theta_2}{\cos\theta_1 +
\eta\cos\theta_2}.$$

Christophe Schlick esitti vuonna 1994 approksimaation, joka korvaa
kaavat polynomilla:
$F \approx F_0 + (1 - F_0)(1 - \cos\theta)^5$, missä
$F_0 = ((n_1 - n_2)/(n_1 + n_2))^2$ on heijastus kohtisuoraan. Kun valo
tulee tiheämmästä aineesta, kaavaan sijoitetaan taittuneen säteen
kulma, koska heijastus on samassa kulmaparissa molempiin suuntiin
sama.

```{.cpp tiedosto="esimerkit/05-fresnel.cpp" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/05-fresnel.odotettu"}
```

Lasi heijastaa kohtisuoraan 4 % valosta, mutta loivassa kulmassa
lähes kaiken. Tämän näkee järven pinnasta: suoraan alas katsottaessa
näkyy pohja, kaukana horisontissa taivas. Schlickin approksimaation
virhe on enimmillään pari prosenttiyksikköä ja suurin keskikulmissa,
mikä riittää lähes kaikkeen renderöintiin. Tiheämmästä aineesta
kokonaisheijastus alkaa, kun $\cos\theta_1 < 0{,}745$.

Metallit eivät päästä valoa läpi, ja niiden heijastus riippuu
aallonpituudesta: kulta heijastaa punaista enemmän kuin sinistä. Niiden
tarkka Fresnelin kerroin tarvitsee kompleksisen taitekertoimen, mutta
Schlickin kaava värillisellä $F_0$:lla on vakiintunut käytäntö.
Luku *Materiaalit ja fysikaalinen varjostus* käyttää sitä.

## Kohtaus

Kohtauksessa on peilipallo, lasipallo, punainen diffuusi pallo ja
shakkiruudullinen lattia. Jokaisessa pikselissä on neljä sädettä
kiinteässä 2 × 2 -kuviossa:

```{.cpp tiedosto="esimerkit/05-whitted.cpp" osa="kohtaus"}
```

```{.cpp tiedosto="esimerkit/05-whitted.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/05-whitted.odotettu"}
```

![Whitted-säteenseuranta: peilipallo, lasipallo ja diffuusi pallo
shakkilaudalla. Lasipallo kääntää taustan ylösalaisin, ja
lasipallon varjo on yhtä musta kuin punaisen pallon.](kuvat/05-whitted.png){width=70%}

Laskurit kertovat algoritmin luonteen. Säteitä on yhteensä runsaat
kaksi kertaa pikselisäteiden määrä, ja jokainen lasiin osuva säde
kaksinkertaistuu: heijastus ja taittuminen. Syvällä rekursiossa
säteiden määrä kasvaa eksponentiaalisesti, mutta niiden painot
pienenevät, joten käytännön renderöijät katkaisevat haaran, kun sen
paino jää alle kynnyksen.

Kokonaisheijastuksia on nolla, vaikka lasin sisällä kulkee
tuhansia säteitä. Tämä ei ole virhe: pallon sisällä säde osuu
pintaan aina samassa kulmassa kuin se tuli sisään, koska pallon
jänne on symmetrinen. Kriittistä kulmaa ei siksi ylitetä koskaan.
Lasikuutiossa tai prismassa kokonaisheijastus on tavallinen, ja
timantin kimallus perustuu siihen.

## Whittedin rajat

Kuvassa on neljä fysikaalisesti väärää asiaa, ja jokainen johtuu
samasta syystä: Whitted seuraa valoa vain peilisuuntiin ja pistemäiseen
valoon.

1. **Varjot ovat teräviä**, koska valo on piste. Oikeilla valoilla on
   pinta-ala, ja varjon reunalla osa valosta näkyy.
2. **Lasipallon varjo on musta.** Lasin läpi kulkeva valo keskittyy
   lattialle kirkkaaksi pisteeksi (kaustiikka), mutta varjosäde ei
   osaa taittua.
3. **Diffuusit pinnat eivät valaise toisiaan.** Punainen pallo ei
   heijasta punaista valoa lattialle; vakiosuuruinen ympäristövalo
   paikkaa puutetta.
4. **Kiiltävät pinnat ovat joko täydellisiä peilejä tai mattoja.**
   Harjattu metalli tai himmeä muovi vaatii heijastuksen moneen
   suuntaan.

Robert Cook, Thomas Porter ja Loren Carpenter ratkaisivat kohdat 1 ja
4 vuonna 1984 *jakautuneella säteenseurannalla* (distributed ray
tracing): yhden heijastussäteen sijaan lähetetään monta sädettä
satunnaisiin suuntiin ja valon pinnan satunnaisiin pisteisiin.
James Kajiya yleisti ajatuksen vuonna 1986 renderöintiyhtälöksi ja
polunseurannaksi, joka ratkaisee kaikki neljä. Seuraavat kolme lukua
rakentavat sen.

## Käytännössä

- **Käännä normaali tulopuolelle** ennen heijastusta, taittumista ja
  lähtöpisteen siirtoa. Lasin sisäpinnasta tuleva säde on muuten
  väärällä puolella.
- **Rajoita rekursion syvyys** ja katkaise haarat, joiden paino on
  pieni. Kaksi vastakkaista peiliä tuottaa muuten loputtoman
  rekursion.
- **Käytä Fresnelin kerrointa** lasissa ja vedessä vakioheijastuksen
  sijaan. Kulmariippuvuus on se, mikä saa ne näyttämään oikeilta.
- **Schlickin approksimaatio riittää** lähes aina; muista käyttää
  taittunutta kulmaa tiheämmästä aineesta tultaessa.
- **Tunnista Whittedin rajat**, kun kohtaus vaatii pehmeitä varjoja,
  kaustiikkaa tai epäsuoraa valoa: silloin tarvitaan polunseurantaa.

## Itsearviointi

- Osaat toteuttaa Whitted-säteenseurannan varjosäteillä,
  peiliheijastuksella ja taittumisella.
- Osaat laskea taittuneen suunnan Snellin laista ja tunnistaa
  kokonaisheijastuksen.
- Osaat laskea Fresnelin heijastuskertoimen tarkasti ja Schlickin
  approksimaatiolla ja selittää niiden eron.
- Osaat luetella Whitted-algoritmin rajat ja selittää, miksi ne
  johtuvat pistevalosta ja peilisuuntaisista säteistä.

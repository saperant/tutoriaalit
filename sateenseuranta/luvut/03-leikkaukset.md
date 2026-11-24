# Leikkaukset

Säteenseurantarenderöijä käyttää suurimman osan ajastaan
leikkaustesteihin: osuuko säde tähän kappaleeseen, ja jos osuu,
millä etäisyydellä. Tässä luvussa johdetaan testit palloille,
tasoille, kolmioille ja akselien suuntaisille laatikoille, testataan
ne ja käsitellään liukulukujen tarkkuus, joka on säteenseurannan
yleisin virhelähde.

Kaikilla testeillä on sama rajapinta: säde ja väli
$(t_\text{min}, t_\text{max})$, ja paluuarvona lähin osuma välillä tai
ääretön. Väli on tärkeä kahdesta syystä. Lähimmän osuman haussa
$t_\text{max}$ on tähänastinen lähin osuma, joten kauempana olevat
pinnat hylätään laskematta loppuun. Varjosäteessä $t_\text{max}$ on
etäisyys valoon, koska valon takana olevat esteet eivät varjosta.

## Pallo

Piste $\mathbf{p}$ on pallon pinnalla, kun
$|\mathbf{p} - \mathbf{c}|^2 = r^2$. Kun sijoitetaan
$\mathbf{p} = \mathbf{o} + t\mathbf{d}$ ja merkitään
$\mathbf{f} = \mathbf{o} - \mathbf{c}$, saadaan toisen asteen yhtälö

$$t^2 + 2(\mathbf{f}\cdot\mathbf{d})\,t + |\mathbf{f}|^2 - r^2 = 0,$$

kun $|\mathbf{d}| = 1$. Merkitään $b = -\mathbf{f}\cdot\mathbf{d}$ ja
$c = |\mathbf{f}|^2 - r^2$, jolloin juuret ovat
$t = b \pm \sqrt{b^2 - c}$. Koulun ratkaisukaava toimii, kun pallo on
lähellä ja suuri. Kaukana olevalle pienelle pallolle se menettää
tarkkuuden kahdessa kohdassa: diskriminantti $b^2 - c$ on kahden lähes
yhtä suuren luvun erotus, ja pienempi juuri $b - \sqrt{b^2 - c}$
samoin. Vakaa muoto laskee diskriminantin
kohtisuorasta etäisyydestä $\mathbf{l}$ keskipisteestä säteeseen,
$r^2 - |\mathbf{l}|^2$, ja pienemmän juuren muodossa $c / q$, jossa
ei vähennetä lähes yhtä suuria lukuja:

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="pallo"}
```

Jos säde alkaa pallon sisältä, ensimmäinen juuri on negatiivinen ja
osuma on toinen juuri, poistumiskohta. Tätä tarvitaan lasissa, jossa
säde kulkee pallon läpi.

Ero näkyy, kun sama 1 cm:n pallo siirretään yhä kauemmas:

```{.cpp tiedosto="esimerkit/03-tarkkuus.cpp" osa="naiivi"}
```

```{.cpp tiedosto="esimerkit/03-tarkkuus.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-tarkkuus.odotettu"}
```

Kun yksikkö on metri, sadan kilometrin päässä koulukaavan virhe on
0,07 mm, mikä riittää varjosäteen itseleikkaukseen. Kymmenessä
tuhannessa kilometrissä se on 8 mm eli lähes koko pallon säde: kaava
osuu pallon keskelle. Vakaa
muoto pysyy liukulukujen pyöristyksen tasolla. Suuret etäisyydet ovat
tavallisia: maisema, planeetta tai kaupunki kilometreinä, ja
lähellä kameraa pieni esine.

## Taso

Taso on pisteet $\mathbf{p}$, joille $\mathbf{n}\cdot\mathbf{p} = e$.
Sijoitus antaa suoraan
$t = (e - \mathbf{n}\cdot\mathbf{o}) / (\mathbf{n}\cdot\mathbf{d})$.
Jos säde on tason suuntainen, nimittäjä on nolla, ja säde joko ei osu
tai kulkee tasossa; kumpikaan ei ole näkyvä osuma.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="taso"}
```

## Kolmio: Möller–Trumbore

Kolmion pisteet ovat
$\mathbf{a} + u\,\mathbf{e}_1 + v\,\mathbf{e}_2$, missä
$\mathbf{e}_1 = \mathbf{b} - \mathbf{a}$,
$\mathbf{e}_2 = \mathbf{c} - \mathbf{a}$, $u, v \ge 0$ ja
$u + v \le 1$. Säde osuu, kun

$$\mathbf{o} + t\,\mathbf{d} = \mathbf{a} + u\,\mathbf{e}_1 + v\,\mathbf{e}_2,$$

eli kolmen tuntemattoman lineaarinen yhtälöryhmä
$[-\mathbf{d}\ \ \mathbf{e}_1\ \ \mathbf{e}_2]\,(t, u, v)^\mathsf{T} =
\mathbf{o} - \mathbf{a}$. Möllerin ja Trumboren algoritmi ratkaisee sen
Cramerin säännöllä. Determinantit ovat skalaarikolmituloja, ja
yhteiset ristitulot lasketaan kerran. Painot $u$ ja $v$ tarkistetaan
heti, kun ne on laskettu, joten useimmat ohi menevät säteet hylätään
ennen $t$:n laskemista:

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="kolmio"}
```

Painot $u$ ja $v$ ovat barysentriset koordinaatit, joilla
interpoloidaan kärkien normaalit ja tekstuurikoordinaatit kuten
rasteroinnissa. Säteenseurannassa interpolointi on aina
perspektiivikorjattu, koska painot lasketaan suoraan kolmion tasossa.

## Laatikko: laattamenetelmä

Akselien suuntainen laatikko (AABB) on kolmen *laatan* leikkaus:
$x_\text{min} \le x \le x_\text{max}$ ja samoin $y$:lle ja $z$:lle.
Kunkin laatan sisällä säde on välillä
$[(x_\text{min} - o_x)/d_x,\ (x_\text{max} - o_x)/d_x]$, ja laatikossa
se on kaikkien kolmen välin leikkauksessa. Jos leikkaus on tyhjä, säde
menee ohi:

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="laatikko"}
```

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="laatta"}
```

Laatikkotesti on kiihdytysrakenteen sisin silmukka, joten se on
kirjoitettu ilman jakolaskuja: suunnan käänteisluvut lasketaan
kerran säteelle. Akselin suuntaiselle säteelle käänteisluku on
ääretön, mikä toimii oikein: $(x_\text{min} - o_x)\cdot\infty$ on
$\pm\infty$, ja laatta joko rajaa kaiken tai ei mitään. Jos säde kulkee
täsmälleen laatan reunatasossa, tulo on $0 \cdot \infty$ eli NaN.
Vertailut on kirjoitettu niin, että NaN jättää välin ennalleen, sillä
jokainen vertailu NaN:n kanssa on epätosi. Tämä on liukulukujen
sääntö, jolle koodi rakennetaan tietoisesti, ei sattumalta toimiva
erikoistapaus.

## Testit

Jokainen leikkausfunktio testataan tapauksilla, joiden vastaus
tiedetään: edestä, sisältä, ylärajan takaa, ohi, kärjen vierestä ja
laatan reunatasoa pitkin.

```{.cpp tiedosto="esimerkit/03-leikkaukset.cpp" osa="tunnetut"}
```

Tunnetut tapaukset eivät kata kaikkea. Kolmiotesti verrataan siksi
satunnaistestissä toiseen, hitaampaan mutta suoraviivaiseen
toteutukseen: ensin tason leikkaus, sitten barysentriset painot
pinta-alojen suhteina. Jos versiot ovat eri mieltä, piste on joko
täsmälleen reunalla (painon itseisarvo alle $10^{-9}$), jolloin
kumpikin vastaus on hyväksyttävä, tai jommassakummassa on virhe:

```{.cpp tiedosto="esimerkit/03-leikkaukset.cpp" osa="satunnainen"}
```

```{.tuloste tiedosto="esimerkit/03-leikkaukset.odotettu"}
```

Laatan reunatasoa pitkin kulkeva säde lasketaan osumaksi, kuten
NaN-säännön mukaan pitääkin. Kiihdytysrakenteelle tämä on turvallinen
suunta: laatikkotesti saa ilmoittaa ylimääräisiä osumia, koska
sisällä olevat kolmiot testataan joka tapauksessa, mutta se ei saa
koskaan ohittaa oikeaa osumaa.

## Itseleikkaus ja "shadow acne"

Kun säde osuu pintaan, osumakohta lasketaan
$\mathbf{p} = \mathbf{o} + t\mathbf{d}$ liukuluvuilla. Piste ei ole
täsmälleen pinnalla vaan hieman sen jommallakummalla puolella. Jos
varjosäde lähtee pinnan alta, se osuu heti omaan pintaansa ja piste
näyttää varjossa olevalta. Tuloksena on satunnaisia tummia pisteitä,
englanniksi *shadow acne*. Esimerkki vertaa kolmea tapaa aloittaa
varjosäde:

```{.cpp tiedosto="esimerkit/03-akne.cpp" osa="varjo"}
```

```{.cpp tiedosto="esimerkit/03-akne.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/03-akne.odotettu"}
```

![Varjosäde ilman siirtoa (vasen), väli alkaen $t_\text{min} =
10^{-4}$ (keski) ja lähtöpiste siirrettynä normaalin suuntaan
(oikea).](kuvat/03-akne.png){width=95%}

Ilman siirtoa noin viidennes valaistuista pikseleistä on väärin
varjossa. Kumpikin korjaus toimii origon lähellä, mutta kun kohtaus
siirretään $10^{11}$ yksikön päähän, kiinteä $10^{-7}$:n siirto ei
enää riitä: liukulukujen väli on siellä noin $10^{-5}$. Myös
$t_\text{min}$ alkaa pettää. Kumpikin vakio on sidottu kohtauksen
mittakaavaan, ja tuotantorenderöijät laskevat siirron osumapisteen
koordinaattien suuruudesta (Wächter ja Binder, *Ray Tracing Gems*,
luku 6) tai laskevat leikkaukset paikallisissa koordinaateissa.

Väli $t_\text{min}$ ja siirto eroavat muuten. $t_\text{min}$ hylkää
kaikki lähellä olevat osumat, myös oikeat: kahden toisiaan koskettavan
kappaleen rajalla valo vuotaa. Normaalin suuntainen siirto ei estä
läheisiä osumia mutta toimii vain, kun siirron suunta on oikein: lasin
läpi kulkeva säde siirretään pinnan toiselle puolelle. Tämän
tutoriaalin kirjasto käyttää normaalin suuntaista siirtoa
`SIIRTO = 1e-7`, joka riittää kohtauksille, joiden koordinaatit ovat
alle tuhannen.

## Käytännössä

- **Testaa leikkaukset erikseen** tunnetuilla tapauksilla ja
  satunnaistesteillä toista toteutusta vastaan. Kuvasta virhettä on
  vaikea paikantaa.
- **Käytä numeerisesti vakaita kaavoja.** Toisen asteen yhtälön
  koulukaava ja kahden suuren luvun erotus ovat tyypillisiä
  tarkkuuden menetyksen paikkoja.
- **Siirrä toisen säteen lähtöpistettä normaalin suuntaan**, ja
  valitse puoli sen mukaan, jatkaako säde pinnan edestä vai takaa.
  Suhteuta siirto koordinaattien suuruuteen, jos kohtaus on suuri.
- **Anna laatikkotestin erehtyä varovaisesti.** Ylimääräinen osuma
  maksaa vain aikaa, puuttuva osuma tekee reiän kuvaan.
- **Kirjoita vertailut NaN:n huomioiden.** `t0 > tmin ? t0 : tmin`
  ja `std::max(tmin, t0)` käyttäytyvät NaN:n kanssa eri tavoin.

## Itsearviointi

- Osaat johtaa säteen ja pallon, tason, kolmion ja laatikon
  leikkauksen ja selittää, mitä välin $(t_\text{min}, t_\text{max})$
  ylärajalla säästetään.
- Osaat selittää, miksi toisen asteen yhtälön koulukaava menettää
  tarkkuutta kaukaisella pienellä pallolla, ja kirjoittaa vakaan
  muodon.
- Osaat testata leikkausfunktion tunnetuilla tapauksilla ja
  satunnaistestillä vertailutoteutusta vastaan.
- Osaat selittää itseleikkauksen syyn ja vertailla $t_\text{min}$:n
  ja normaalin suuntaisen siirron etuja ja rajoja.

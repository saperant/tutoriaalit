# Monte Carlo -integrointi

Taito *Todennäköisyys ja tilastot* arvioi piin ja integraaleja
satunnaisilla pisteillä ja totesi, että virhe pienenee kuten
$1/\sqrt{N}$ riippumatta ulottuvuudesta. Tässä luvussa sama menetelmä
sovitetaan suuntien integraaleihin: mistä jakaumasta suunnat poimitaan,
miten estimaatti painotetaan ja miten jakauman valinta vaikuttaa
kohinaan.

## Estimaattori

Integraalia $I = \int_D g(x)\,dx$ arvioidaan poimimalla
$x_1, \dots, x_N$ jakaumasta, jonka tiheys on $p(x) > 0$ kaikkialla,
missä $g(x) \neq 0$:

$$\hat I_N = \frac{1}{N}\sum_{k=1}^{N} \frac{g(x_k)}{p(x_k)}.$$

Estimaattori on *harhaton*: $E[\hat I_N] = \int (g/p)\,p\,dx = I$
kaikilla $N$. Sen varianssi on $\sigma^2/N$, missä $\sigma^2$ on
yksittäisen termin $g/p$ varianssi, joten keskivirhe on
$\sigma/\sqrt{N}$. Kaksi seurausta:

- **Neljä kertaa enemmän näytteitä puolittaa virheen.** Kohinaisesta
  kuvasta puolet siistimpään tarvitaan nelinkertainen laskenta-aika.
- **Varianssia voi pienentää valitsemalla $p$:n hyvin.** Jos $p$ on
  verrannollinen $g$:hen, $g/p$ on vakio ja varianssi nolla. Tätä
  kutsutaan *painotusnäytteistykseksi* (importance sampling).
  Täydellistä $p$:tä ei voi käyttää, koska sen normalisointi vaatisi
  $I$:n, mutta mitä lähempänä $g$:n muotoa $p$ on, sitä vähemmän
  kohinaa.

Pallonpuoliskon integraaleissa näytteet ovat suuntia, ja tiheys
mitataan avaruuskulmaa kohden. Kaksi tavallista jakaumaa ovat
tasainen, $p = 1/(2\pi)$, ja kosinipainotettu,
$p = \cos\theta/\pi$. Jälkimmäinen sopii renderöintiyhtälöön, jonka
integrandissa on aina $\cos\theta_i$.

## Suuntien poiminta

Tasainen pallonpuolisko poimitaan käänteisfunktiomenetelmällä:
$\cos\theta$ on tasajakautunut välillä $[0, 1]$ (Arkhimedeen
hattulause) ja kiertokulma $\phi$ välillä $[0, 2\pi)$. Kosinipainotettu
suunta saadaan Malleyn menetelmällä: poimitaan piste tasaisesti
yksikkökiekolta ja nostetaan se pallonpuoliskolle. Kiekon tasainen
tiheys projisoituu pallolle tiheydeksi $\cos\theta/\pi$.

```{.cpp tiedosto="esimerkit/yhteinen/naytteet.hpp" osa="naytteet"}
```

Suunnat lasketaan paikallisessa kannassa, jossa normaali on $z$-akseli.
Maailman koordinaatteihin päästään ortonormaalilla kannalla, joka
rakennetaan normaalista ilman haarautumia ja jakolaskuja nollalla
(Duff ym. 2017):

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="kanta"}
```

Paikallisessa kannassa $\cos\theta$ on suoraan $z$-komponentti, ja
BRDF:t kirjoitetaan siinä yksinkertaisemmin.

## Kokeilu: irradianssi taivaalta

Taivaan radianssi kasvaa horisontista lakipisteeseen,
$L(\omega) = 1 + 2\cos\theta$. Vaakasuoran pinnan irradianssi on

$$E = \int_\Omega (1 + 2\cos\theta)\cos\theta\,d\omega =
\pi + \tfrac{4\pi}{3} = \tfrac{7\pi}{3}.$$

Esimerkki arvioi sitä kolmella estimaattorilla: tasaisilla suunnilla,
kosinipainotetuilla suunnilla ja kosinipainotetuilla suunnilla, joiden
painossa on käytetty väärää tiheyttä:

```{.cpp tiedosto="esimerkit/07-montecarlo.cpp" osa="taivas"}
```

```{.cpp tiedosto="esimerkit/07-montecarlo.cpp" osa="estimaattorit"}
```

Jokaiselle näytemäärälle lasketaan 400 riippumatonta estimaattia eri
siemenillä. Niiden neliöpoikkeama tarkasta arvosta antaa RMSE:n, ja
keskiarvo paljastaa mahdollisen harhan:

```{.cpp tiedosto="esimerkit/07-montecarlo.cpp" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/07-montecarlo.odotettu"}
```

Tulos näyttää kolme asiaa.

1. **Virhe pienenee kuten $1/\sqrt{N}$.** RMSE kerrottuna
   $\sqrt{N}$:llä pysyy vakiona (noin 5,6 ja 1,5) satunnaisvaihtelun
   rajoissa. Tämä on tilastollinen testi, joka ei riipu kääntäjästä:
   kymmenen kertaa suurempi tai pienempi vakio paljastaisi virheen.
2. **Kosinipainotus vähentää virheen neljäsosaan** samalla
   näytemäärällä, mikä vastaa kuusitoista kertaa enemmän näytteitä.
   Ero syntyy siitä, että $g/p = \pi L(\omega)$ vaihtelee vain
   taivaan radianssin verran, kun tasaisessa poiminnassa myös
   $\cos\theta$ vaihtelee.
3. **Väärä tiheys tuottaa harhan, joka ei katoa.** Keskiarvo
   lähestyy arvoa $10\pi/3 \approx 10{,}47$ eikä oikeaa 7,33:a.
   Lisänäytteet tekevät väärästä vastauksesta vain tarkemman. Tällainen
   virhe ei näy kohinana vaan liian kirkkaana tai tummana kuvana, ja
   sen löytää vain vertaamalla tunnettuun arvoon.

## Harha, konsistenssi ja varianssi

Estimaattori on *harhaton*, jos sen odotusarvo on oikea kaikilla
$N$:n arvoilla, ja *konsistentti*, jos se suppenee oikeaan arvoon,
kun $N$ kasvaa. Polunseuranta on harhaton. Monet käytännön menetelmät
(kohinan poisto, kirkkaiden näytteiden leikkaus, välimuistit) ovat
harhaisia mutta konsistentteja tai eivät edes sitä, ja vaihtavat
pienen harhan suureen varianssin pienennykseen. Vaihtokauppa on
usein hyvä, mutta se on tehtävä tietoisesti, ja harhaton
vertailukuva tarvitaan joka tapauksessa testaukseen.

Kuvan virhettä mitataan tässä tutoriaalissa RMSE:llä vertailukuvaan,
joka on laskettu samalla menetelmällä paljon suuremmalla
näytemäärällä. RMSE yhdistää harhan ja varianssin:
$\text{RMSE}^2 = \text{harha}^2 + \text{varianssi}$. Vertailukuvan
oma kohina näkyy pienenä lattiana: jos vertailukuvassa on 128
näytettä, 16 näytteen kuvan virhe ei voi pienentyä mittauksessa
mielivaltaisesti.

## Käytännössä

- **Paino on $g/p$, ja $p$:n on vastattava poimintaa täsmälleen.**
  Yleisin polunseurannan virhe on pdf, joka ei vastaa
  poimintafunktiota: kerroin $\pi$ tai $\cos\theta$ puuttuu, tai
  tiheys on pinta-alaa kohden, kun integraali on avaruuskulman yli.
- **Testaa estimaattori tunnetulla integraalilla.** Keskiarvo
  monesta riippumattomasta ajosta paljastaa harhan; RMSE:n
  pieneneminen kuten $1/\sqrt{N}$ paljastaa, että varianssi on
  äärellinen.
- **Poimi integrandin muodon mukaan.** Kosinipainotus on oikea
  oletus diffuusille pinnalle; luku *Materiaalit* poimii kiiltävien
  pintojen suunnat niiden oman lohkon mukaan.
- **Kirjoita näytteet paikalliseen kantaan.** BRDF:t ja tiheydet ovat
  yksinkertaisia, kun normaali on $z$-akseli.

## Itsearviointi

- Osaat kirjoittaa Monte Carlo -estimaattorin mielivaltaisella
  tiheydellä ja osoittaa sen harhattomaksi.
- Osaat selittää, miksi virhe pienenee kuten $1/\sqrt{N}$, ja
  testata sen tilastollisesti.
- Osaat poimia suunnat tasaisesti ja kosinipainotetusti
  pallonpuoliskolta ja laskea niiden tiheydet.
- Osaat erottaa harhan ja varianssin ja tunnistaa väärästä
  tiheydestä johtuvan harhan.

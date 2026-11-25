# Valaistus

Tähän asti pikselin väri on tullut suoraan kärjistä tai tekstuurista.
Kolmiulotteinen muoto näkyy kuitenkin vasta valaistuksesta: pinnan
kirkkaus riippuu siitä, miten se on kääntynyt valoon ja katsojaan
nähden. Reaaliaikagrafiikan klassiset valaistusmallit ovat
empiirisiä: ne eivät simuloi valon fysiikkaa, mutta ne ovat halpoja ja
näyttävät uskottavilta. Fysikaalisesti perustellut mallit (PBR) ovat
taidon *Säteenseuranta ja fysikaalinen valaistus* aihe; ne
rakentuvat samoille käsitteille.

## Vektorit pinnalla

Valaistus lasketaan pinnan pisteessä neljällä yksikkövektorilla:

- $n$ on pinnan **normaali**,
- $l$ osoittaa pinnasta **valoa** kohti,
- $v$ osoittaa pinnasta **katsojaa** kohti,
- $r = 2 (n \cdot l) n - l$ on valon **heijastussuunta**.

![Valaistuksen vektorit pinnan pisteessä. Heijastussuunta $r$ on
valon suunnan $l$ peilikuva normaalin suhteen. Puolivälivektori $h$
on suuntien $l$ ja $v$ puolivälissä; se esitellään Blinn–Phongin
mallin yhteydessä.](kuvat/09-vektorit.png){width=58%}

Kaikkien on oltava samassa koordinaatistossa (yleensä maailmassa tai
kamerassa) ja normalisoituja. Kaksi yleisintä virhettä ovat juuri
nämä: normaali on mallin koordinaatistossa ja valo maailmassa, tai
interpoloitu normaali on unohdettu normalisoida.

## Lambert: mattapinta

Mattapinta siroaa valoa tasaisesti kaikkiin suuntiin, joten sen
kirkkaus ei riipu katsojasta. Pinta-alayksikölle osuvan valon määrä
on verrannollinen tulokulman kosiniin: vino valo levittyy suuremmalle
alalle. Tämä on **Lambertin** malli:

$$I_{\text{diffuusi}} = k_d \max(0, n \cdot l).$$

Negatiivinen pistetulo tarkoittaa, että valo tulee pinnan takaa, ja
se leikataan nollaan.

## Phong ja Blinn–Phong: kiilto

Kiiltävä pinta heijastaa valoa voimakkaimmin peilisuuntaan. **Phongin**
malli (1975) mittaa, kuinka lähellä katsesuunta on heijastussuuntaa,
ja terävöittää huipun potenssilla:

$$I_{\text{peili}} = k_s \max(0, r \cdot v)^{s}.$$

**Blinn–Phong** (1977) korvaa heijastussuunnan **puolivälivektorilla**
$h = (l + v)/|l + v|$ ja vertaa sitä normaaliin: $\max(0, n \cdot h)^s$.
Kun valo ja katsoja ovat kaukana, $h$ on vakio koko pinnalle, joten se
oli aikanaan halvempi. Se myös käyttäytyy paremmin loivissa kulmissa,
joissa Phongin kiilto katkeaa terävästi. Blinn–Phong oli OpenGL:n ja
Direct3D:n kiinteän putken malli.

```{.cpp tiedosto="esimerkit/yhteinen/valo.hpp" osa="valo"}
```

Kokonaisuuteen kuuluu vielä **ympäristövalo** (ambient), vakio, joka
korvaa kaiken epäsuoran valon: ilman sitä valolta piilossa olevat
pinnat olisivat täysin mustia. Usean valon tapauksessa diffuusi- ja
peiliosat summataan valoittain. Peiliosaa ei kerrota pinnan värillä,
koska heijastus on useimmissa materiaaleissa (muoveissa, maaleissa)
valon värinen; metalleilla se on pinnan värinen.

## Mallit lukuina

```{.cpp tiedosto="esimerkit/09-valaistus.cpp" osa="kulmat"}
```

```{.tuloste tiedosto="esimerkit/09-valaistus.odotettu"}
```

Katsoja on hieman vasemmalla, joten heijastus on suurimmillaan, kun
valo tulee yhtä paljon oikealta (37 astetta). Lambert pienenee
tasaisesti kosinina ja on nolla 90 asteessa. Blinn–Phongin huippu on
leveämpi kuin Phongin samalla eksponentilla: puolivälivektorin kulma
normaaliin on noin puolet heijastussuunnan ja katsesuunnan kulmasta.
Nelinkertainen eksponentti (128) tuottaa lähes saman huipun kuin
Phong eksponentilla 32. Mallista toiseen siirryttäessä eksponentit
on siis skaalattava.

## Missä valaistus lasketaan

Valaistuksen voi laskea kolmion, kärjen tai pikselin tarkkuudella, ja
ero on suuri sekä kuvassa että hinnassa. Esimerkki piirtää saman
128-kolmioisen pallon kolmella tavalla. Pallo on tehty oktaedrista
jakamalla jokainen kolmio neljään ja työntämällä uudet kärjet pallon
pinnalle:

```{.cpp tiedosto="esimerkit/yhteinen/malli.hpp" osa="pallo"}
```

**Tasainen varjostus** (flat) käyttää koko kolmiolle yhtä normaalia,
kolmion tason normaalia. Kolmiot erottuvat selvästi, mikä sopii
särmikkäille esineille ja tyylitellylle grafiikalle:

```{.cpp tiedosto="esimerkit/09-varjostus.cpp" osa="tasainen"}
```

**Gouraud-varjostus** (1971) laskee valaistuksen kärjissä ja
interpoloi värin. Se on halpa, koska valaistus lasketaan vain kerran
kärkeä kohden, mutta kiiltopiste katoaa tai vääristyy, jos se osuu
kolmion keskelle, sillä interpoloitu väri ei voi olla kirkkaampi kuin
kärkien värit:

```{.cpp tiedosto="esimerkit/09-varjostus.cpp" osa="gouraud"}
```

**Pikseleittäinen varjostus** (Phong-varjostus, ei pidä sekoittaa
Phongin heijastusmalliin) interpoloi normaalin ja paikan ja laskee
valaistuksen jokaisessa pikselissä. Interpoloitu normaali on lyhyempi
kuin yksi, joten se normalisoidaan:

```{.cpp tiedosto="esimerkit/09-varjostus.cpp" osa="pikseli"}
```

```{.cpp tiedosto="esimerkit/09-varjostus.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-varjostus.odotettu"}
```

![Sama pallo tasaisella, Gouraud- ja pikseleittäisellä varjostuksella.
Valo tulee vasemmalta ylhäältä.](kuvat/09-varjostus.png){width=85%}

Kirkkaimman pikselin arvo kertoo eron: tasaisessa ja pikseleittäisessä
varjostuksessa kiiltopiste on täysi (237), Gouraud-varjostuksessa se on
levinnyt ja himmentynyt (175). Keskikirkkaus on lähes sama kaikilla
kolmella, koska diffuusiosa on lähes lineaarinen normaalin suhteen ja
kestää interpoloinnin.

Nykyään valaistus lasketaan lähes aina pikseleittäin, koska
näytönohjaimilla on laskentatehoa siihen ja kärkien tiheydestä
riippumaton tulos on helpompi hallita. Gouraud elää edelleen hyvin
kevyissä tai tyylitellyissä renderöijissä.

## Valotyypit

Esimerkkien valo on **suunnattu** (directional): kaukainen valonlähde
kuten aurinko, jonka suunta $l$ on sama kaikkialla. **Pistevalon**
suunta lasketaan pisteestä valoon, ja sen voimakkuus vaimenee
etäisyyden neliönä. **Kohdevalo** on pistevalo, jonka valokeila on
rajattu kartioksi. Valon vaimeneminen on yksi syy laskea valaistus
lineaarisessa väriavaruudessa: neliöllinen vaimeneminen näyttää
oikealta vain lineaarisilla arvoilla.

Varjoja nämä mallit eivät tuota: pinta on valaistu, jos se on
kääntynyt valoon päin, vaikka sen ja valon välissä olisi jotain.
Varjot vaativat näkyvyystestin valosta katsottuna, joko varjokartalla
(taito *GPU-ohjelmointi: OpenGL ja Vulkan*) tai säteellä (*Säteenseuranta ja
fysikaalinen valaistus*).

## Käytännössä

- **Normalisoi ja pidä samassa koordinaatistossa** kaikki
  valaistuksen vektorit. Interpoloitu normaali on aina
  normalisoitava uudelleen.
- **Laske valaistus pikseleittäin**, ellei ole erityistä syytä
  säästää; Gouraud hukkaa kiiltopisteet.
- **Muista eksponenttien ero** Phongin ja Blinn–Phongin välillä
  (noin nelinkertainen), kun siirrät materiaaleja.
- **Valaistus lineaarisilla arvoilla.** Gamma-virhe näkyy liian
  terävänä siirtymänä valosta varjoon.
- **Ympäristövalo on paikkaus.** Kun kohtaus näyttää litteältä,
  oikea ratkaisu on epäsuoran valon mallintaminen (ympäristökartat,
  ambient occlusion), ei ympäristövalon kasvattaminen.

## Itsearviointi

- Osaat laskea Lambertin, Phongin ja Blinn–Phongin valaistuksen
  annetuilla vektoreilla.
- Osaat selittää tasaisen, Gouraud- ja pikseleittäisen varjostuksen
  erot ja kustannukset.
- Osaat perustella, miksi interpoloitu normaali on normalisoitava.
- Osaat kuvata suunnatun, piste- ja kohdevalon erot.

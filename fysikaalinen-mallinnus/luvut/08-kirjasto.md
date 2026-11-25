# Sama kirjastolla

Luvun 7 kirjasto osaa yhden asian: lineaariset kolmiot ja
lämmönjohtumisen. Jokainen uusi elementtityyppi, fysiikka tai
ulottuvuus vaatisi uutta kokoamiskoodia. Elementtikirjasto erottaa
nämä toisistaan: käyttäjä antaa verkon, valitsee elementin ja
kirjoittaa heikon muodon, ja kirjasto hoitaa kvadratuurin, kokoamisen
ja numeroinnin. Tässä luvussa luvun 7 tehtävät tehdään uudelleen
**scikit-fem**-kirjastolla. Tavoite on kaksiosainen: nähdä, että
kirjasto tekee saman kuin oma koodi, ja nähdä, mitä sillä saa lisää.

## Miksi scikit-fem

Avoimia elementtikirjastoja on useita. FEniCS ja deal.II ovat laajoja
ja tehokkaita, mutta ne ovat käännettäviä ohjelmistoja, joiden asennus
on oma työnsä. scikit-fem on puhdasta Pythonia: se asentuu yhdellä
komennolla, sen riippuvuudet ovat NumPy ja SciPy, ja sen tuottamat
matriisit ovat tavallisia SciPyn harvoja matriiseja. Kirjasto ei
piilota mitään, joten jokaisen välituloksen voi tulostaa ja verrata
omaan koodiin. Suurissa kolmiulotteisissa tehtävissä se on hitaampi
kuin käännetyt kirjastot, mutta periaatteet ja työnkulku ovat samat.

Käsitteet vastaavat luvun 7 osia:

| Käsite | `pienfem` | scikit-fem |
|---|---|---|
| verkko | `Verkko(pisteet, kolmiot)` | `MeshTri(p, t)` |
| elementti | kiinteä: lineaarinen kolmio | `ElementTriP1()`, `ElementTriP2()`, … |
| kanta | (sisäänrakennettu) | `Basis(verkko, elementti)` |
| heikko muoto | funktio `elementtimatriisi` | `BilinearForm`, `LinearForm` |
| kokoaminen | `jaykkyys(verkko)` | `muoto.assemble(kanta)` |
| reunaehto | `ratkaise(a, b, kiinni, arvot)` | `condense` ja `solve` |

Kirjaston verkko tallettaa pisteet ja kolmiot sarakkeittain eikä
riveittäin, joten oman verkon muunnos on transpoosi:

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="verkko"}
```

## Sama matriisi

Ensimmäinen koe on suora vertailu. Kirjaston valmis muoto `laplace` on
$\int \nabla u \cdot \nabla v\,dA$, sama kuin luvun 7
elementtimatriisi. Kun se kootaan samalla verkolla ja samalla
solmunumeroinnilla, tuloksen pitää olla sama matriisi.

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="sama"}
```

```{.tuloste tiedosto="esimerkit/08-kirjasto.odotettu" rivit="1-1"}
```

Matriisit ovat samat pyöristystarkkuudella. Vertailu on enemmän kuin
muodollisuus: kahdesta toisistaan riippumattomasta toteutuksesta
kumpikin toimii toisen tarkistuksena. Sama keino kannattaa aina, kun
otetaan käyttöön uusi työkalu: ratkaistaan sillä ensin jotain, minkä
vastaus tiedetään muuta kautta.

## Heikko muoto koodina

Kirjastossa tehtävä kirjoitetaan lähes samassa muodossa kuin paperilla.
Kuormavektori $\int f\,v\,dA$ on `LinearForm`, jolle annetaan funktio
testifunktiosta `v` ja kvadratuuripisteiden tiedoista `w`. `w.x`
sisältää pisteiden koordinaatit, joten paikasta riippuva lähde on
tavallinen lauseke. Funktio saa argumenttinaan kaikkien elementtien
kaikki kvadratuuripisteet kerralla taulukkona, joten Python-silmukkaa
elementtien yli ei ole.

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="ratkaisu"}
```

Neljä riviä tekee saman kuin luvun 7 kirjasto: kokoaminen, kuorma,
reunaehto ja ratkaisu. `kanta.get_dofs()` ilman argumentteja palauttaa
reunan vapausasteet, `condense` poistaa ne yhtälöistä ja `solve`
ratkaisee. Virhe lasketaan samalla mekanismilla: `Functional` integroi
lausekkeen alueen yli, ja `kanta.interpolate(u)` antaa ratkaisun arvot
kvadratuuripisteissä.

Kirjaston dokumentaatiossa muodot kirjoitetaan yleensä
dekoraattorilla `@BilinearForm`. Tässä käytetään tavallista
funktiokutsua, joka tekee saman ja sopii tyyppitarkistimelle.

## Korkeampi aste yhdellä rivillä

Funktion `l2_virhe` toinen argumentti on elementti. `ElementTriP2`
on **toisen asteen kolmio**: kantafunktiot ovat toisen asteen
polynomeja, ja kärkien lisäksi jokaisen sivun keskellä on solmu.
Kirjasto hoitaa uudet vapausasteet, tarkemman kvadratuurin ja
numeroinnin. Omaan koodiin sama muutos olisi vaatinut uuden
elementtimatriisin, uuden numeroinnin ja uuden kvadratuurin.

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/08-kirjasto.odotettu" rivit="2-6"}
```

Toisen asteen elementin $L^2$-virhe pienenee kuten $h^3$. Vertailu
samalla tuntemattomien määrällä on kiinnostavampi: 1089
tuntemattomalla lineaarinen elementti antaa virheen $1{,}3 \cdot
10^{-3}$ ja toisen asteen elementti $5{,}7 \cdot 10^{-5}$, eli
yli kaksikymmentäkertaisen tarkkuuden samalla yhtälöryhmän koolla.
Sileälle ratkaisulle asteen nosto on tehokkaampi kuin verkon
tihentäminen.

## Kun korkeampi aste ei auta

Sama koe L-alueessa, jonka ratkaisussa on luvun 7
kulmasingulariteetti:

```{.python tiedosto="esimerkit/08-kirjasto.py" osa="l-alue"}
```

```{.tuloste tiedosto="esimerkit/08-kirjasto.odotettu" alkaen="L-alue"}
```

Toisen asteen elementti on tässäkin tarkempi, mutta sen kertaluku on
sama kuin lineaarisen: noin 1,3. Virheraja $Ch^{p+1}$ olettaa
ratkaisulta $p + 1$ rajoitettua derivaattaa. Kun ratkaisu ei ole
sileä, kertaluvun määrää ratkaisun sileys eikä elementin aste. Asteen
nosto maksaa tuntemattomina, mutta ei tuota luvattua hyötyä.

Tässä kokeessa Dirichlet'n arvot eivät ole nollia. `kanta.doflocs`
antaa jokaisen vapausasteen paikan, myös sivujen keskisolmujen, ja
tarkan ratkaisun arvot sijoitetaan niihin. `condense` saa arvot
argumentissa `x`.

## Mitä kirjasto ei tee

Kirjasto poistaa kokoamiskoodin, mutta ei mallintajan työtä.

- **Heikko muoto on käyttäjän vastuulla.** Väärä etumerkki tai
  puuttuva reunatermi kootaan yhtä tehokkaasti kuin oikea.
- **Reunaehtojen joukot valitaan itse.** `get_dofs` ottaa ehdon
  koordinaateista tai nimetyn reunan. Väärin valittu joukko on
  yleisin virhe (luku 9 käyttää tätä symmetriatasoihin).
- **Verkko tulee muualta.** Kirjastossa on valmiit verkot
  yksinkertaisille alueille ja tihennysfunktio. Monimutkainen
  geometria verkotetaan erillisellä verkkogeneraattorilla, ja
  kirjasto lukee tuloksen tiedostosta (luku 11).
- **Tulos pitää edelleen tarkistaa.** Kirjaston oikeellisuus ei tee
  mallista oikeaa.

## Käytännössä

- **Aloita valmiilla muodoilla.** `skfem.models` sisältää Poissonin
  yhtälön ja lineaarisen elastisuuden muodot. Oma muoto kannattaa kirjoittaa
  vasta, kun valmis ei riitä, ja tarkistaa silloin valmista vasten
  tapauksessa, jossa ne yhtyvät.
- **Vertaa uutta työkalua tunnettuun.** Sama matriisi, sama ratkaisu
  tai sama kertaluku tehtävässä, jonka vastaus on tiedossa.
- **Nosta astetta, kun ratkaisu on sileä.** Toisen asteen elementit
  ovat rakenteiden laskennassa oletus (luku 9). Singulariteettien
  lähellä auttaa vain verkko.
- **Kiinnitä kirjaston versio.** Rajapinnat muuttuvat versioiden
  välillä. Tämän tutoriaalin esimerkit on ajettu versiolla 12.0.2, ja
  versio on kirjattu tiedostoon `pyproject.toml`.
- **Pidä oma pieni toteutus tallessa.** Se on nopein tapa selvittää,
  onko outo tulos mallin vai työkalun käytön vika.

## Itsearviointi

- Osaat nimetä elementtikirjaston peruskäsitteet (verkko, elementti,
  kanta, muoto) ja yhdistää ne oman kokoamiskoodin osiin.
- Osaat ratkaista Poissonin tehtävän scikit-femillä ja laskea virheen
  normin kirjaston välineillä.
- Osaat varmistaa, että kirjasto ja oma toteutus tuottavat saman
  matriisin, ja tiedät, miksi vertailu kannattaa.
- Osaat selittää, milloin elementin asteen nosto parantaa kertalukua
  ja milloin ei.

# Kosketukset

Kun kaksi kappaletta koskettaa, moottorin pitää tietää kolme asiaa:
missä kohdassa, mihin suuntaan ja kuinka syvällä. Taito
*3D-peliohjelmointi* vastasi kahteen jälkimmäiseen, koska hahmon
työntämiseen ulos seinästä riittävät normaali ja syvyys. Dynamiikka
tarvitsee myös kosketuskohdan, sillä siitä riippuu, kuinka kappale
alkaa pyöriä, ja usein yksi kohta ei riitä. Tämä luku tuottaa
kosketuspisteet pallolle, tasolle ja kierretylle laatikolle.

## Monisto

Kahden kappaleen kaikki kosketuspisteet ja niiden yhteinen normaali
muodostavat *moniston* (*contact manifold*):

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="monisto"}
```

Normaali osoittaa sovitusti kappaleesta `a` kappaleeseen `b`. Sopimus
on mielivaltainen, mutta sen on oltava sama kaikkialla: ratkaisija
työntää `b`:tä normaalin suuntaan ja `a`:ta vastaan.

Pisteiden määrä ratkaisee, pysyykö kappale levossa. Lattialla lepäävä
laatikko, jolla on yksi kosketuspiste, keikkuu sen varassa. Kahdella
pisteellä se keinuu niiden välisen janan ympäri. Vasta kolme tai
useampi piste, jotka eivät ole samalla suoralla, tukevat sitä kuten
oikea lattia.

Kosketus luodaan jo hieman ennen kuin pinnat osuvat toisiinsa
(vakio `MARGINAALI`). Syy selviää luvussa 7: lepäävän kappaleen pisteet
eivät saa ilmestyä ja kadota laskentatarkkuuden rajalla.

## Pallot ja taso

Pallon kosketus on aina yksi piste, ja normaali kulkee keskipisteen
kautta:

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="pallot"}
```

Pallon ja kierretyn laatikon testi viedään laatikon omaan
koordinaatistoon, jossa laatikko on akselien suuntainen ja lähin piste
saadaan rajaamalla, kuten taidossa *3D-peliohjelmointi*:

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="pallo-laatikko"}
```

Jos pallon keskipiste on jo laatikon sisällä, lähin piste on
keskipiste itse eikä suuntaa ole. Silloin pallo työnnetään ulos
lähimmän sivun kautta. Tämä haara on arvaus, ja luku 10 näyttää, mitä
tapahtuu, kun se arvaa väärin.

## Laatikko ja taso

Laatikon kahdeksan kärkeä saadaan keskipisteestä, akseleista ja
puolimitoista. Jokainen tason alle jäänyt kärki on kosketuspiste:

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="taso-laatikko"}
```

Lappeellaan lepäävä laatikko saa neljä pistettä, särmällään lepäävä
kaksi ja kulmallaan seisova yhden.

## Kaksi laatikkoa: erottava akseli

Kahden kierretyn laatikon testi on *erottavan akselin lause* (SAT),
joka on tuttu kahdesta ulottuvuudesta: kaksi kuperaa kappaletta eivät
kosketa, jos on akseli, jolle projisoituina ne eivät mene päällekkäin.
Kolmessa ulottuvuudessa kokeiltavia akseleita on viisitoista: kummankin
laatikon kolme sivunormaalia ja yhdeksän särmäparin ristituloa.
Särmäakselit tarvitaan, koska kaksi laatikkoa voi olla limittäin
jokaisen sivunormaalin suunnassa ja silti erillään, kun särmä osoittaa
särmää kohti.

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="sat"}
```

Jos erottavaa akselia ei löydy, pienimmän limityksen akseli on
kosketuksen normaali ja limitys sen syvyys. Särmäakseli hyväksytään
vain, jos se on selvästi sivuakseleita parempi, koska sivukosketuksesta
saadaan useita pisteitä ja särmäkosketuksesta vain yksi.

## Sivukosketus: leikkaus

Kun normaali on jommankumman laatikon sivunormaali, kosketusalue on
kahden sivun yhteinen osa. Laatikko, jonka sivu antoi normaalin, on
*viitelaatikko*. Toisesta laatikosta valitaan *tulosivu*: se sivu, joka
on eniten viitesivua vastakkain. Tulosivun nelikulmio leikataan
viitesivun neljään reunatasoon, ja ne leikatun monikulmion kärjet,
jotka ovat viitesivun alapuolella, ovat kosketuspisteitä.

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="leikkaus"}
```

Leikkaus on sama Sutherlandin ja Hodgmanin algoritmi, jolla taito
*Renderöinnin perusteet* leikkasi kolmion näkymäkartioon. Päällekkäin
ristissä olevat lankut osoittavat, miksi pelkät kärjet eivät riitä:
kumpikaan ei ole toisen sisällä yhdelläkään kärjellään, mutta
leikkaus tuottaa neljä pistettä lankkujen risteykseen.

Särmäkosketuksessa piste on kahden särmän lähimpien pisteiden
puolivälissä:

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="sarmat"}
```

## Kaikki parit

Funktio `kosketa` valitsee testin muotojen mukaan ja pitää huolen
normaalin suunnasta:

```{.cpp tiedosto="esimerkit/yhteinen/kosketus.hpp" osa="kosketa"}
```

```{.cpp tiedosto="esimerkit/04-kosketus.cpp" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/04-kosketus.odotettu"}
```

![Esimerkin kappaleet. Punaiset viivat ovat kosketusnormaaleja
kosketuspisteistä: lappeellaan olevalla laatikolla ja ristikkäisillä
lankuilla pisteitä on neljä, kulmallaan seisovalla laatikolla ja
särmäkosketuksella yksi.](kuvat/kosketus.png){width=100%}

Pallon ja laatikon normaali vaihtaa merkkiään, kun kappaleet annetaan
toisessa järjestyksessä. Tämä on tarkoitus: normaali osoittaa aina
ensimmäisestä toiseen.

## Yleinen kupera muoto: GJK ja EPA

Jokaiselle muotoparille kirjoitettu oma testi ei skaalaudu: kymmenen
muotoa tarkoittaisi 55 funktiota. Fysiikkamoottorit käsittelevät siksi
kaikki kuperat muodot yhdellä algoritmilla, joka tarvitsee muodosta
vain *tukifunktion*: mikä muodon piste on kauimpana annetussa
suunnassa. Pallolle se on keskipiste plus säde kertaa suunta,
laatikolle se kärki, jonka merkit vastaavat suunnan merkkejä.

Algoritmit perustuvat *Minkowskin erotukseen* $A - B$, joka on kaikkien
erotusten $\mathbf a - \mathbf b$ joukko. Muodot leikkaavat täsmälleen
silloin, kun erotus sisältää origon, ja origon etäisyys erotuksen
reunasta on muotojen etäisyys tai tunkeuma.

![Periaatekuva: kahden kuperan muodon Minkowskin erotus. Kun muodot
ovat erillään, origo (punainen risti) on erotuksen ulkopuolella; kun ne
leikkaavat, origo on sen sisällä.](kuvat/minkowski.png){width=75%}

- **GJK** (Gilbert, Johnson ja Keerthi) etsii origoa lähinnä olevan
  erotuksen pisteen rakentamatta erotusta. Se pitää yllä enintään
  neljän pisteen *simpleksiä* (piste, jana, kolmio tai tetraedri),
  jonka kärjet ovat tukifunktion arvoja, ja siirtää sitä kohti origoa.
  Jos simpleksi sulkee origon sisäänsä, muodot leikkaavat.
- **EPA** (*expanding polytope algorithm*) jatkaa siitä: se kasvattaa
  simpleksiä monitahokkaaksi kohti erotuksen reunaa ja löytää origoa
  lähimmän reunan kohdan, josta saadaan normaali ja syvyys.

Kosketuspisteet tuotetaan näidenkin jälkeen leikkaamalla, kuten edellä.
Tämän tutoriaalin moottori ei tarvitse GJK:ta, koska muotoja on kolme,
mutta tukifunktio on se rajapinta, jolla moottorit lisäävät uusia
muotoja.

## Käytännössä

- **Monisto on tärkeämpi kuin tarkka syvyys.** Pinojen vakaus riippuu
  siitä, että pisteitä on riittävästi ja että ne pysyvät samoina
  askeleesta toiseen. Sentin virhe syvyydessä ei näy; kadonnut
  kosketuspiste näkyy tärinänä.
- **Enintään neljä pistettä riittää.** Moottorit karsivat monistosta
  neljä pistettä, jotka kattavat suurimman alan ja joista yksi on
  syvin. Tämän tutoriaalin moottori pitää kaikki leikkauksen pisteet,
  koska se on yksinkertaisempaa.
- **Pysyvä monisto.** Vaihtoehto leikkaukselle on kerätä yksi piste
  askeleessa ja säilyttää edellisten askelten pisteet, kunnes ne
  siirtyvät liian kauas. Näin tehdään muodoille, joille leikkausta ei
  ole.
- **Sisäkkäin alkavat kappaleet** ovat sisällöntuotannon virhe, jota
  moottori ei voi korjata hyvin. Editorin kannattaa varoittaa niistä.
- **Sisäsärmät.** Tasaista kolmioverkkoa pitkin liukuva laatikko voi
  törmätä kahden kolmion väliseen särmään, vaikka pinta on sileä.
  Moottorit merkitsevät tällaiset särmät ja jättävät niiden normaalit
  huomiotta.

## Itsearviointi

- Osaat kertoa, mitä monisto sisältää ja miksi pisteiden määrä
  vaikuttaa siihen, pysyykö kappale levossa.
- Osaat selittää, miksi kahden laatikon testissä tarvitaan särmäparien
  ristitulot.
- Osaat kuvata, miten sivukosketuksen pisteet saadaan leikkaamalla.
- Osaat kertoa, mitä tukifunktio ja Minkowskin erotus ovat ja mihin
  GJK ja EPA niitä käyttävät.

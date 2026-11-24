# Materiaalit ja fysikaalinen varjostus

Lambert ja täydellinen peili ovat ääripäitä. Lähes kaikki todelliset
pinnat ovat niiden välissä: harjattu teräs, maalattu puu, muovi ja
kumi heijastavat valoa leveään tai kapeaan lohkoon peilisuunnan
ympärille. Fysikaalisesti perusteltu varjostus (PBR, *physically
based rendering*) kuvaa nämä yhdellä mallilla, jonka parametrit ovat
mitattavia: pinnan väri, karheus ja se, onko aine metalli vai
eriste. Samat parametrit toimivat polunseurannassa ja reaaliaikaisessa
grafiikassa, ja niiden ansiosta sama materiaali näyttää samalta
kaikissa valaistuksissa.

## Mikrofasettimalli

Mikrofasettiteoria (Torrance ja Sparrow 1967, Cook ja Torrance 1982)
olettaa, että pinta koostuu pienistä peileistä, *mikrofaseteista*,
joiden normaalit ovat jakautuneet makroskooppisen normaalin ympärille.
Valo heijastuu suunnasta $\mathbf{l}$ suuntaan $\mathbf{v}$ vain niistä
faseteista, joiden normaali on puolivälivektori
$\mathbf{h} = (\mathbf{l} + \mathbf{v}) / |\mathbf{l} + \mathbf{v}|$.
BRDF on

$$f(\mathbf{l}, \mathbf{v}) = \frac{D(\mathbf{h})\,G(\mathbf{l},
\mathbf{v})\,F(\mathbf{v}\cdot\mathbf{h})}
{4\,(\mathbf{n}\cdot\mathbf{l})(\mathbf{n}\cdot\mathbf{v})}.$$

- **$D$, normaalien jakauma**: kuinka suuri osa faseteista osoittaa
  suuntaan $\mathbf{h}$. Sileällä pinnalla jakauma on terävä, karhealla
  leveä.
- **$G$, varjostus ja peittyminen**: osa faseteista on toisten
  varjossa tai piilossa katsojalta. Termi on lähes 1 kohtisuoraan ja
  pienenee loivissa kulmissa.
- **$F$, Fresnel**: kuinka suuren osan valosta yksittäinen fasetti
  heijastaa, luvun *Whitted-säteenseuranta* kaavoilla.
- **Nimittäjä 4** tulee muunnoksesta puolivälivektorin avaruuskulmasta
  valon avaruuskulmaan.

## GGX-jakauma

Nykyään vallitseva jakauma on GGX (Walter ym. 2007, sama kuin
Trowbridgen ja Reitzin vuonna 1975 johtama):

$$D(\mathbf{h}) = \frac{\alpha^2}{\pi\,\big((\mathbf{n}\cdot\mathbf{h})^2
(\alpha^2 - 1) + 1\big)^2}.$$

Leveysparametri $\alpha$ lasketaan karheudesta neliönä,
$\alpha = r^2$ (Burley 2012). Silloin karheus 0,5 näyttää
puoliväliltä peilin ja maton välissä, mikä tekee parametrista
taiteilijalle intuitiivisen. GGX:n häntä on pitkä: kiiltopisteen
ympärillä on hehku, joka puuttuu vanhemmista jakaumista kuten
Beckmannista ja Phongista ja joka saa metallit näyttämään oikeilta.

Varjostustermi $G$ on Smithin malli, jossa kaksi suuntaa
oletetaan riippumattomiksi: $G = G_1(\mathbf{l})\,G_1(\mathbf{v})$.
GGX:lle $G_1$ on suljetussa muodossa:

```{.cpp tiedosto="esimerkit/yhteinen/materiaali.hpp" osa="ggx"}
```

## Metallit ja eristeet

Metallin ja eristeen ero on fysikaalisesti selvä. Metalli heijastaa
valon pinnasta, ja sen Fresnelin kerroin on värillinen: kulta
heijastaa kohtisuoraan noin 100 % punaisesta ja 35 % sinisestä. Valoa
ei pääse pinnan alle. Eristeen pinta heijastaa noin 4 % valosta
värittömänä, ja loput menee pinnan alle, siroaa ja tulee ulos
pinnan värisenä diffuusina valona. Siksi muovin kiiltopiste on
valkoinen ja kullan keltainen.

*Metallisuustyönkulussa* (metallic workflow) materiaalilla on väri ja
metallisuus 0 tai 1. Metallin väri on $F_0$, eristeen väri on
diffuusikerroksen albedo, ja $F_0 = 0{,}04$. Välit sekoittavat näitä
esimerkiksi ruosteen tai lian reunoilla. Diffuusikerros saa valon,
joka ei heijastunut pinnasta sisään tullessa eikä ulos lähtiessä,
joten se kerrotaan molempien suuntien läpäisyllä (Shirley ym. 1997):

```{.cpp tiedosto="esimerkit/yhteinen/materiaali.hpp" osa="materiaali"}
```

```{.cpp tiedosto="esimerkit/yhteinen/materiaali.hpp" osa="brdf"}
```

Polunseuranta poimii karhean pinnan suunnan kahdesta lohkosta.
Peililohko poimii mikrofasetin normaalin $\mathbf{h}$ jakaumasta
$D(\mathbf{h})\cos\theta_h$ ja heijastaa katsesuunnan siitä;
diffuusilohko on kosinipainotettu. Tiheys on lohkojen
todennäköisyyksillä painotettu summa, koska kumpi tahansa lohko olisi
voinut tuottaa saman suunnan. Funktiot `poimi` ja `pdf` olivat
edellisessä luvussa.

## Energian säilymisen testi

Uusi BRDF testataan laskemalla sen suunta-albedo: kuinka suuren osan
tulevasta valosta pinta heijastaa, kun valo tulee tasaisesti
kaikista suunnista. Monte Carlolla tämä on yksinkertaista, koska
`poimi` palauttaa painon $f\cos\theta/p$, jonka keskiarvo on juuri
albedo:

```{.cpp tiedosto="esimerkit/09-albedo.cpp" osa="albedo"}
```

Testi löytää tyypillisen virheen. Nimittäjän nelonen unohtuu helposti,
ja kuva näyttää silti uskottavalta, vain liian kirkkaalta:

```{.cpp tiedosto="esimerkit/09-albedo.cpp" osa="virheellinen"}
```

```{.cpp tiedosto="esimerkit/09-albedo.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/09-albedo.odotettu"}
```

Virheellinen BRDF heijastaa jopa neljä kertaa tulevan valon. Oikea
malli pysyy kaikissa tapauksissa alle yhden, mutta tuloksessa on
toinen opetus. Valkoinen metalli, jonka pitäisi heijastaa kaikki,
menettää karheudella 1 lähes 70 % energiasta. Tämä ei ole
toteutuksen virhe vaan mikrofasettimallin ominaisuus: malli laskee
vain yhden heijastuksen fasetista, ja karhealla pinnalla valo
heijastuu usein faseteista toisiin ennen kuin se pääsee pois.
Analyyttisesti tälle tapaukselle albedo on $1 - \ln 2 \approx 0{,}307$,
ja Monte Carlo -estimaatti osuu siihen. Kullan ja Contyn
(2017) monisirontakorjaus lisää puuttuvan energian taulukoidulla
termillä.

Ensimmäinen versio tämän luvun eristeestä antoi loivassa kulmassa
albedon 1,15: diffuusikerros kerrottiin vain heijastuksen $1 - F$:llä
puolivälivektorin kulmassa. Testi paljasti virheen, ja läpäisyn
kertominen molempiin suuntiin korjasi sen. Monessa
reaaliaikamoottorissa on yhä sama yksinkertaistus.

## Valkoinen uuni

Kokonaisen renderöijän energiatesti on *valkoinen uuni* (white
furnace): kappale ympäristössä, jonka radianssi on 1 joka suunnasta.
Jos kappaleen pinta heijastaa kaiken valon, se näyttää tarkalleen
yhtä kirkkaalta kuin tausta ja katoaa näkyvistä. Jos pinta menettää
energiaa, se erottuu tummempana; jos se luo energiaa, kirkkaampana.

```{.cpp tiedosto="esimerkit/09-uuni.cpp" osa="uuni"}
```

```{.cpp tiedosto="esimerkit/09-uuni.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/09-uuni.odotettu"}
```

![Valkoinen uuni: Lambert, eriste (karheus 0,5), metalli 0,3 ja
metalli 1,0 vasemmalta oikealle. Vasemmanpuoleinen Lambert-pallo
katoaa taustaan täsmälleen, joten palloja näkyy kolme.](kuvat/09-uuni.png){width=80%}

Lambert antaa täsmälleen 1,000, koska jokaisen näytteen paino on 1
ja jokainen säde palaa taustaan. Tarkka tulos on vahva testi: se
osoittaa, että poiminta, tiheys, kanta ja polunseurannan painot ovat
johdonmukaiset. Muut materiaalit menettävät energiaa kuten
albedotesti ennusti. Uunitestin voi ajaa jokaiselle materiaalille
ja jokaiselle renderöijän muutokselle regressiotestinä.

## Materiaalit kuvassa

```{.cpp tiedosto="esimerkit/09-pbr.cpp" osa="kohtaus"}
```

```{.cpp tiedosto="esimerkit/09-pbr.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/09-pbr.odotettu"}
```

![Kultaa (ylärivi) ja punaista muovia (alarivi), karheus 0,1–0,9
vasemmalta oikealle. Sileimmissä palloissa näkyy suoran valaistuksen
kohinaa, jota monitärkeysnäytteistys poistaisi.](kuvat/09-pbr.png){width=100%}

Kullan heijastus on keltainen ja muovin valkoinen, kuten pitääkin.
Karheuden kasvaessa valon heijastus levenee ja himmenee, mutta
heijastuvan valon kokonaismäärä pysyy lähes samana. Sileimpien
pallojen kiiltopisteissä ja lattiassa niiden ympärillä on kirkkaita
pisteitä: valon näyte osuu kapeaan lohkoon harvoin, ja BRDF:n mukaan
poimittu suunta, joka osuisi valoon helposti, jätetään laskematta,
koska suora valo on jo laskettu. Edellisen luvun MIS on tarkalleen
tämän ongelman ratkaisu.

## Käytännössä

- **Käytä metallisuustyönkulkua** ja mitattuja arvoja: eristeen
  $F_0 = 0{,}04$, metallin väri mittauksista. Rajoita metallisuus
  arvoihin 0 ja 1 paitsi siirtymissä.
- **Karheus neliöön** ennen GGX:ää, jotta parametri on tasainen
  silmälle.
- **Testaa jokainen BRDF albedolla ja valkoisella uunilla.**
  Energiaa luova BRDF näyttää usein uskottavalta, mutta tekee
  monipomppuisesta valosta liian kirkasta.
- **Hyväksy yhden sironnan energiahäviö tai korjaa se**
  monisirontatermillä. Karhea metalli on muuten liian tumma.
- **Poimi suunnat materiaalin lohkon mukaan** ja yhdistä strategiat
  MIS:llä. Kiiltävä pinta ja pieni valo ovat polunseurannan vaikein
  yhdistelmä.

## Itsearviointi

- Osaat kirjoittaa Cook–Torrance-mikrofasettimallin ja selittää
  termien $D$, $G$ ja $F$ merkityksen.
- Osaat laskea GGX-jakauman ja Smithin varjostustermin ja poimia
  mikrofasetin normaalin jakaumasta.
- Osaat selittää metallin ja eristeen eron ja toteuttaa
  metallisuustyönkulun.
- Osaat testata BRDF:n energian säilymisen albedolla ja valkoisella
  uunilla ja tulkita tuloksen.

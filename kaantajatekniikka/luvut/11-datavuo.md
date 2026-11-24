# Datavuoanalyysi

Optimoinnit tarvitsevat tietoa, joka riippuu koko funktion
ohjausvuosta: onko tämän rekisterin arvo vielä käytössä, onko tämä
lauseke jo laskettu, mikä kirjoitus tähän muuttujaan voi olla
voimassa? **Datavuoanalyysi** (*dataflow analysis*) laskee tällaisen
tiedon jokaisen peruslohkon alkuun ja loppuun. Menetelmä on yleinen:
analyysi määritellään muutamalla joukko-operaatiolla, ja sama
kiintopisteiteraatio ratkaisee ne kaikki.

## Elävyys

Rekisteri on **elävä** (*live*) ohjelman kohdassa, jos sen nykyistä
arvoa voidaan vielä lukea jollakin polulla ennen kuin se kirjoitetaan
uudelleen. Elävyyttä tarvitaan kolmeen asiaan: kuolleen koodin
poistoon (kirjoitus rekisteriin, joka ei ole elävä, on turha),
rekisterien varaukseen (kaksi samaan aikaan elävää arvoa tarvitsevat
eri rekisterit) ja karsittuun SSA-muotoon (luku 10).

Elävyys on **taaksepäin etenevä** analyysi: tieto kulkee käytöstä
kohti määrittelyä. Jokaiselle lohkolle B lasketaan ensin kaksi
paikallista joukkoa:

- *käyttö*(B): rekisterit, jotka luetaan B:ssä ennen kuin B kirjoittaa
  ne,
- *määr*(B): rekisterit, jotka B kirjoittaa.

Sitten ratkaistaan yhtälöt

$$\text{ulos}(B) = \bigcup_{S \in \text{seur}(B)} \text{sisään}(S),
\qquad
\text{sisään}(B) = \text{käyttö}(B) \cup (\text{ulos}(B) \setminus
\text{määr}(B)).$$

Ensimmäinen sanoo, että arvo on elävä lohkon lopussa, jos jokin
seuraaja voi lukea sen. Toinen sanoo, että arvo on elävä lohkon
alussa, jos lohko lukee sen tai jos se on elävä lopussa eikä lohko
kirjoita sitä.

## Kiintopiste

Silmukoiden takia yhtälöt viittaavat toisiinsa kehässä: silmukan
otsakkeen `ulos` riippuu rungon `sisään`-joukosta, joka riippuu
otsakkeen `ulos`-joukosta. Ratkaisu on **kiintopisteiteraatio**:
aloitetaan tyhjistä joukoista ja lasketaan yhtälöitä uudelleen, kunnes
mikään joukko ei muutu.

```{.cpp tiedosto="esimerkit/kide/elavyys.cpp" osa="laske"}
```

Iteraatio päättyy aina, koska joukot vain kasvavat ja niillä on
yläraja (kaikki rekisterit). Tämä on datavuoanalyysin teorian ydin:
kun analyysin arvot muodostavat äärellisen korkuisen **hilan** ja
siirtofunktiot ovat **monotonisia**, iteraatio saavuttaa pienimmän
kiintopisteen (Kildall 1973). Järjestyksellä on merkitystä vain
nopeudelle: taaksepäin etenevä analyysi suppenee nopeimmin, kun lohkot
käydään lopusta alkuun. Esimerkkifunktion elävyys (`--vaihe=elavyys`):

```{.tuloste tiedosto="esimerkit/naytteet/elavyys-summa.txt"}
```

Kolmas kierros vain toteaa, ettei mikään muuttunut. Parametri `n` on
elävä koko silmukan ajan, koska silmukan ehto lukee sen joka
kierroksella; silmukan jälkeen lohkossa L5 elää enää `s`. Väliaikaiset
`%3`–`%9` eivät näy, koska ne syntyvät ja kuolevat saman lohkon
sisällä: lohkojen rajoilla ne eivät ole eläviä.

Esitys `std::vector<bool>`-taulukkoina on yksinkertaisin mahdollinen.
Tuotantokääntäjät käyttävät bittivektoreita, joissa joukko-operaatiot
ovat sanan levyisiä bittioperaatioita, ja SSA-muodossa elävyys voidaan
laskea ilman iteraatiota suoraan määrittely–käyttö-ketjuista.

## Muut analyysit samalla kaavalla

Datavuoanalyysit eroavat suunnaltaan (eteen- vai taaksepäin) ja
yhdistämisoperaatioltaan (yhdiste vai leikkaus):

| Analyysi | Suunta | Yhdistäminen | Käyttö |
|----------|--------|--------------|--------|
| elävyys | taaksepäin | yhdiste | kuollut koodi, rekisterien varaus |
| saavuttavat määrittelyt | eteenpäin | yhdiste | vakioiden eteneminen |
| saatavilla olevat lausekkeet | eteenpäin | leikkaus | yhteiset alilausekkeet |
| erittäin kiireiset lausekkeet | taaksepäin | leikkaus | koodin siirto ylöspäin |

*Yhdiste* tarkoittaa, että tieto pätee, jos se pätee *jollakin*
polulla (arvo *voi* olla elävä); *leikkaus*, että sen on pädettävä
*kaikilla* poluilla (lauseke on *varmasti* laskettu). Valinta riippuu
siitä, mikä virhe on turvallinen: kuollut koodi saa jäädä poistamatta,
mutta elävää koodia ei saa poistaa. Analyysin on siis aina oltava
**konservatiivinen** siihen suuntaan, joka säilyttää ohjelman
merkityksen.

## Paikallinen ja globaali

Kiden optimoinnit (luku 12) yhdistävät kaksi tasoa. Arvonumerointi on
**paikallinen**: se käy yhden lohkon läpi alusta loppuun ja tietää
tarkasti, mitä kussakin kohdassa on laskettu, mutta unohtaa kaiken
lohkon rajalla. Kuolleen koodin poisto on **globaali**: se käyttää
elävyyttä lohkojen rajoilla ja kulkee kunkin lohkon sisällä taaksepäin
käsky käskyltä. Globaalit analyysit ovat vahvempia, mutta paikalliset
ovat nopeita ja yksinkertaisia, ja ne yhdessä kattavat suuren osan
hyödystä.

## Käytännössä

- **Kirjoita analyysi yhtälöinä ennen koodia.** Suunta, yhdistäminen
  ja siirtofunktio määräävät analyysin täysin; koodi on niiden suora
  käännös.
- **Tarkista monotonisuus.** Ei-monotoninen siirtofunktio voi jäädä
  heilumaan ikuisesti. Iteraatioiden yläraja testissä paljastaa sen.
- **Käy lohkot oikeassa järjestyksessä.** Eteenpäin etenevälle
  analyysille käänteinen jälkijärjestys, taaksepäin etenevälle sen
  käänteinen; kierrosten määrä pysyy pienenä.
- **Ole konservatiivinen oikeaan suuntaan.** Epätarkka analyysi on
  hyväksyttävä, väärä ei.

## Itsearviointi

- Osaat määritellä elävyyden ja kirjoittaa sen datavuoyhtälöt
  käyttö- ja määrittelyjoukoilla.
- Osaat ratkaista datavuoyhtälöt kiintopisteiteraatiolla ja perustella,
  miksi iteraatio päättyy.
- Osaat luokitella analyysit suunnan ja yhdistämisoperaation mukaan ja
  kertoa, mihin optimointiin kukin sopii.
- Osaat selittää paikallisen ja globaalin analyysin eron ja sen, miksi
  analyysin on oltava konservatiivinen.

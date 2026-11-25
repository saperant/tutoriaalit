---
title: Tiimit ja organisaatiomallit
subtitle: Pikaopas · Conway, tiimirakenteet, omistajuus, päätökset
---

# Conwayn laki ja mittaaminen

| Asia | Muistisääntö |
|----------------|--------------------------------------------------|
| Conwayn laki | järjestelmän rakenne jäljittelee tekijöidensä viestintärakennetta |
| tiimiraja | rajapinta: sen yli menevä muutos on kallis |
| käänteinen Conway | muotoile tiimit halutun arkkitehtuurin mukaan |
| jaon hyvyys | kuinka moni muutos pysyy yhden tiimin sisällä |
| sykli tiimien välillä | raja väärässä paikassa tai rajapinta puuttuu |
| yhteismuutokset | `git log --name-only`; suodata siivousmuutokset |
| rajoitus | historia kertoo nykyisen rakenteen kitkan, ei parasta rakennetta |

```{.python tiedosto="esimerkit/02-yhteismuutokset.py" osa="tiimit"}
```

# Organisaatiomallit

| Malli | Ryhmittely | Vahvuus | Heikkous |
|-------------|-------------|------------------|-------------------------|
| funktionaalinen | osaaminen | syvä erikoisosaaminen | työ kulkee osastolta toiselle |
| projekti | toimitus | selkeä tavoite | osaaminen hajoaa lopuksi |
| matriisi | molemmat | joustava resursointi | kaksi esihenkilöä |
| tuote | asiakasvirta | nopea palaute, omistajuus | päällekkäisyys |

Luovutuksen hinta on odotus rajalla, ei työ. Virtaustehokkuus = työaika
/ läpimenoaika. Komponenttitiimi sopii, kun osaaminen on harvinaista;
ominaisuustiimi, kun muutos leikkaa kerrosten läpi.

# Team Topologies

| Tiimityyppi | Tehtävä |
|-------------------|-----------------------------------------------|
| virtaan linjattu | toimittaa arvoa yhdelle työvirralle alusta tuotantoon |
| alustatiimi | sisäiset palvelut, jotka nopeuttavat virtatiimejä |
| mahdollistava | auttaa tiimejä hankkimaan puuttuvan osaamisen |
| monimutkainen osajärjestelmä | osa, joka vaatii syvää erikoisosaamista |

| Vuorovaikutus | Sopii | Varoitusmerkki |
|----------------|--------------------------|--------------------------|
| yhteistyö | uuden selvittämiseen, rajatuksi ajaksi | jatkuu kuukausia |
| palveluna | vakiintuneeseen tarpeeseen | käyttäjä tarvitsee tikettejä |
| fasilitointi | osaamisen siirtoon | auttaja tekee työn itse |

Murtumatasot: liiketoiminta-alue, sääntely, muutostahti, sijainti,
riski, suorituskyky, tekniikka (harvoin), käyttäjäryhmä. Malli on
sanasto ja ajattelun väline, ei testattu teoria.

# Kuorma ja tiimin koko

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| viestintäpolut | $n(n-1)/2$; tiimijako auttaa vain, jos riippuvuuksia on vähän |
| tiimin koko | noin 5–9 henkeä; yksi tiimi mahtuu yhteen keskusteluun |
| pysyvyys | tuo työ tiimille, älä ihmisiä työn luo |
| sisäinen kuorma | perusosaaminen: koulutus, harkitut tekniikkavalinnat |
| ulkoinen kuorma | ympäristö: automatisoi, tarjoa alustana |
| hyödyllinen kuorma | itse ongelma: tälle jätetään tilaa |
| vastuualueet | yksi kompleksinen tai muutama yksinkertaisempi alue tiimiä kohden |

# Omistajuus ja alustat

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| omistajuus | jokaisella osalla yksi tiimi; sisältää tuotannon |
| mallit | vahva: vain omistaja; heikko: omistaja hyväksyy; yhteinen: kuka tahansa |
| CODEOWNERS | viimeinen osuva sääntö voittaa; omistajaksi tiimi, ei henkilö |
| bussikerroin | montako ihmistä voi poistua ennen kuin osa jää ilman tuntijaa |
| alusta | tuote: käyttäjät, palaute, dokumentaatio, vapaaehtoinen käyttö |
| ohuin toimiva alusta | aloita ohjeesta ja mallista, älä järjestelmästä |
| InnerSource | muutos toisen tiimin koodiin katselmoinnin kautta |

# DevOps ja SRE

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| DevOps | yhteinen vastuu toimituksesta ja tuotannosta, ei tiimin nimi |
| virhebudjetti | 1 − SLO; kun budjetti loppuu, vakaus menee ominaisuuksien edelle |
| raadanta | käsin tehtävä toistuva ylläpitotyö; enintään puolet ajasta |
| päivystys | ringissä noin kahdeksan henkeä; mitoita ihmisten mukaan |
| jälkiselvitys | miten järjestelmä salli virheen, ei kuka sen teki |
| Westrum | patologinen, byrokraattinen, generatiivinen: miten tieto kulkee |

# Päätöksenteko

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| peruttava päätös | tehdään lähellä työtä, nopeasti |
| peruuttamaton päätös | harkitaan laajemmin; näitä on vähän |
| hyväksyntäryhmä | jonon pituus riippuu kokousvälistä ja kapasiteetista |
| neuvonantoprosessi | tekijä päättää kuultuaan asianosaisia ja asiantuntijoita |
| ADR | päätös, tilanne, vaihtoehdot ja seuraukset kirjataan |
| kilta | vapaaehtoinen käytäntöyhteisö; ei päätösvaltaa tiimien yli |

# Skaalausmallit

| Malli | Riippuvuudet | Varaus |
|----------------|------------------------|--------------------------|
| Scrum of Scrums | raportoidaan | ei poista riippuvuuksia |
| SAFe | hallitaan suunnittelulla | paljon rooleja ja prosessia |
| LeSS | poistetaan rakenteella | vaatii rakenteen purkamista |
| Spotify-kuvaus | vältetään autonomialla | tilannekuva, ei malli |

Jos toimitus vaatii $k$ tiimin onnistumista todennäköisyydellä $p$,
ajallaan valmistuu $p^k$. Riippuvuus poistetaan, jos voidaan, ja
hallitaan vain, jos ei voida.

# Hajautus ja muutos

| Asia | Sääntö |
|----------------|--------------------------------------------------|
| etäisyys | viestintä harvenee jyrkästi jo kymmenien metrien päässä |
| aikavyöhykkeet | tiimin sisällä vähintään puoli päivää yhteistä työaikaa |
| kiertoaika | kysymys–vastaus voi kestää vuorokauden; kirjoita koko asia kerralla |
| asynkroninen | kirjoitettu on oletus, kokous poikkeus; päätökset kirjataan |
| muutos | mittaa, valitse yksi raja, kokeile pienintä muutosta, mittaa uudelleen |

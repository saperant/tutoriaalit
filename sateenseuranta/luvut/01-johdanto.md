# Johdanto {.runko-johdanto}

Rasterointi kysyy, mihin pikseleihin kolmio osuu. Säteenseuranta kysyy
toisin päin: mitä pikselin läpi näkyy? Kamerasta lähetetään säde
jokaisen pikselin läpi, etsitään lähin pinta ja kysytään, kuinka paljon
valoa siitä tulee säteen suuntaan. Sama kysymys toistuu pinnalta
eteenpäin: tuleeko valo suoraan lampusta, heijastuuko se peilistä,
taittuuko lasista vai siroaako se seinien kautta? Kun kysymys esitetään
täsmällisesti, se on integraaliyhtälö, *renderöintiyhtälö*, ja sen
ratkaiseminen satunnaisilla näytteillä on *polunseurantaa*.

Tämä tutoriaali rakentaa polunseurantarenderöijän alusta asti
C++-ohjelmana. Matkan varrella käsitellään säteen ja kappaleiden
leikkaukset, kiihdytysrakenteet, klassinen Whitted-säteenseuranta,
radiometria, Monte Carlo -integrointi, fysikaaliset materiaalit ja
kohinan vähentäminen. Jokainen menetelmä testataan: leikkaukset
tunnetuilla tapauksilla ja satunnaistesteillä, kiihdytysrakenne
vertaamalla raakahakuun ja integraattori vertaamalla tunnettuihin
analyyttisiin arvoihin.

## Esitiedot ja rajaus

Esitietoina ovat taidot *Renderöinnin perusteet*, *Todennäköisyys ja
tilastot* ja *Algoritmit*. Renderöinnin perusteista käytetään
kuvapuskuria, lineaarista valoa ja sRGB-koodausta (luku *Kuvat ja
pikselit*), kameran koordinaatistoa (*Muunnokset*) sekä
Lambertin ja Phongin valaistusmalleja (*Valaistus*). Todennäköisyydestä
tarvitaan odotusarvo, varianssi, suurten lukujen laki ja Monte
Carlo -menetelmän perusidea (luvut *Odotusarvo ja varianssi*,
*Raja-arvolauseet* ja *Monte Carlo -menetelmät*). Algoritmeista
tarvitaan rekursio, hajota ja hallitse sekä vaativuusanalyysi.

Renderöijä lasketaan prosessorilla yhdessä säikeessä, ja kohtaukset
ovat pieniä. Näytönohjaimen säteenseurantarajapinnat kuuluvat taitoon
*GPU-ohjelmointi: OpenGL ja Vulkan* ja rinnakkaistus taitoon *Rinnakkaisohjelmointi*.
Spektrinen renderöinti, väliaineet (sumu, savu), ympäristövalaistus
kuvasta ja kaksisuuntaiset menetelmät rajataan pois; luku *Lopuksi*
kertoo, mistä niitä kannattaa lähteä opiskelemaan.

## Mihin säteenseurantaa tarvitaan

Elokuvien ja mainosten kuvat lasketaan polunseurannalla, koska se
tuottaa fysikaalisesti oikeat varjot, heijastukset ja epäsuoran valon
ilman erikoistapauksia. Arkkitehtuurin ja tuotesuunnittelun
visualisoinnissa samaa menetelmää käytetään valaistuksen
ennustamiseen: kuinka paljon päivänvaloa huoneeseen tulee, häikäiseekö
lamppu. Reaaliaikaisessa grafiikassa näytönohjaimet ovat vuodesta 2018
lähtien sisältäneet säteenseurannan laitteistoyksiköt, ja pelit
yhdistävät rasteroinnin ja muutaman säteen pikseliä kohden kohinan
poistoon. Taito *GPU-ohjelmointi: OpenGL ja Vulkan* mainitsee Vulkanin säteenseurannan
laajennukset; tämän tutoriaalin BVH ja leikkaustestit ovat juuri ne,
jotka laitteisto toteuttaa.

Samat menetelmät toimivat valon ulkopuolellakin. Äänen kulkua salissa,
radioaaltojen etenemistä kaupungissa ja neutronien kulkua reaktorissa
simuloidaan säteillä ja Monte Carlolla. Kiihdytysrakenteita käytetään
törmäystunnistuksessa ja lähimmän naapurin haussa.

## Tutoriaalin rakenne

| Luku | Aihe |
|------|------|
| Säteet ja kamera | primäärisäteet, neulanreikäkamera, värinä (jitter) |
| Leikkaukset | pallo, taso, kolmio, laatikko, tarkkuus ja itseleikkaus |
| Kiihdytysrakenteet | BVH, keskikohta- ja SAH-jako, läpikäynti |
| Whitted-säteenseuranta | varjot, heijastus, taittuminen, Fresnel |
| Radiometria ja renderöintiyhtälö | radianssi, irradianssi, BRDF |
| Monte Carlo -integrointi | estimaattori, harha, varianssi, painotus |
| Polunseuranta | suora valo, venäläinen ruletti, MIS |
| Materiaalit | mikrofasettimalli, GGX, metalli ja eriste, uunitesti |
| Näytteistys ja kohina | ositus, Halton, sävykuvaus, kohinan poisto |

Luvuissa rakentuu kirjasto hakemistoon `esimerkit/yhteinen/`:
vektorit (`vektori.hpp`), värit ja kuvat (`kuva.hpp`),
satunnaisluvut (`satunnainen.hpp`), säde ja leikkaukset (`sade.hpp`),
kamera (`kamera.hpp`), BVH (`bvh.hpp`), suuntien näytteistys
(`naytteet.hpp`), materiaalit (`materiaali.hpp`), kohtaus
(`kohtaus.hpp` ja `cornell.hpp`) sekä itse polunseuranta
(`polku.hpp`). Koodi on kirjoitettu selkeäksi; luvussa *Lopuksi*
kerrotaan, mitä tuotantorenderöijä tekisi toisin.

## Esimerkit ja testaus

Esimerkit ovat C++23:a ilman ulkoisia kirjastoja. Testeissä jokainen
käännetään GCC 14:llä ja Clang 20:llä AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa, ja kummankin tulosteen on oltava
täsmälleen sama kuin tiedostossa `<nimi>.odotettu`. Kuvista
tulostetaan tarkistussumma ja keskimääräinen luminanssi:

```text
vertailu 128     summa c1d1eb67  keskiarvo 0.1058
```

Satunnaisuus ja tarkka vertailu sopivat yhteen, kun satunnaisuus on
toistettavaa. Siksi esimerkit noudattavat muutamaa sääntöä:

- **Oma satunnaislukugeneraattori.** PCG32 tuottaa samalla siemenellä
  saman jonon kaikilla alustoilla. Standardikirjaston jakaumien
  algoritmeja ei ole määrätty, joten `std::uniform_real_distribution`
  voi antaa eri luvut GCC:n ja Clangin kirjastoilla.
- **Jokaisella pikselillä oma virta.** Pikselin satunnaisluvut eivät
  riipu siitä, missä järjestyksessä pikselit lasketaan. Sama sääntö
  tekee rinnakkaistamisesta myöhemmin helppoa.
- **Yksi satunnaisluku lauseessa.** Funktion argumenttien
  laskentajärjestystä ei ole määrätty: `f(g(), g())` voi kutsua
  ensin kumpaa tahansa, ja GCC ja Clang todella tekevät sen eri
  järjestyksessä. Tämä virhe löytyi tämän tutoriaalin testeistä kahdesti.
- **Matematiikkafunktiot ajonaikana.** Kumpikin kääntäjä kutsuu
  samaa C-kirjastoa (`sin`, `cos`, `pow`), joten tulokset ovat samat.
  Kääntäjä voi kuitenkin laskea vakioargumentit itse käännösaikana
  eri tarkkuudella, joten tulostettavat vakiot lasketaan
  peruslaskutoimituksilla.

Kun tarkkaa tarkistussummaa ei voi verrata, kuten silloin, kun
tuloksen pitää vain lähestyä tunnettua arvoa, ohjelma laskee virheen
itse ja tulostaa sen pyöristettynä. Tilastolliset testit ovat silloin
muotoa "keskiarvo on 1,000" tai "virhe pienenee neljäsosaan, kun
näytteitä on 16 kertaa enemmän".

Esimerkit kirjoittavat kuvan myös PPM-tiedostoon. Tämän dokumentin
kuvat on tuotettu niistä komennolla `make kuvat`, joka kääntää
esimerkit optimoituina ja makrolla `KUVITUS`, jolloin kuvat ovat
suurempia ja näytteitä on enemmän. Selittävät piirrokset ja
mittaustulosten kuvaajat tekee `kuvat/piirra.py` Matplotlibilla;
kuvaajien luvut se lukee esimerkkien `.odotettu`-tiedostoista. Testeissä kuvat ovat pieniä
(32 × 24 – 80 × 40 pikseliä), koska sanitoijien kanssa käännetty
koodi on kymmeniä kertoja hitaampaa.

## Työkalut

```text
make testaa   # rakenne, esimerkit kahdella kääntäjällä
make pdf      # tämä dokumentti ja pikaopas
make kuvat    # kuvitus hakemistoon kuvat/
```

Kehityskontissa (`.devcontainer/sateenseuranta`) ovat GCC, Clang,
Pandoc ja TeX. Yksittäisen esimerkin voi kääntää ja ajaa suoraan:

```text
g++ -std=c++23 -O2 -DKUVITUS esimerkit/08-polku.cpp -o polku
./polku && display 08-polku.ppm
```

Optimoitu käännös on noin kymmenen kertaa nopeampi kuin
sanitoijilla käännetty ja kymmeniä kertoja nopeampi kuin
optimoimaton. Polunseuranta on lähes täysin laskentaa, joten
optimointitaso ratkaisee, kuinka suuren kuvan kärsii odottaa.

# Johdanto {.runko-johdanto}

Pelin fysiikka on simulaatio, jonka pitää valmistua 16 millisekunnissa
ja näyttää uskottavalta. Laatikkopino pysyy pystyssä, ovi kääntyy
saranallaan, köysi heiluu ja kangas laskeutuu pöydälle. Lisäksi kaiken
pitää toimia silloinkin, kun pelaaja tekee jotain, mitä kukaan ei
ennakoinut.

Tämä tutoriaali rakentaa pienen kolmiulotteisen fysiikkamoottorin osa
kerrallaan: jäykän kappaleen tila ja liike, kosketusten muodostaminen,
törmäysvaste ja kitka, rajoitteiden ratkaisija, nivelet, lepotila ja
nopeat kappaleet. Sen jälkeen käsitellään kangas, vesi ja hiukkaset,
jotka ratkaistaan eri tavoin mutta samoilla periaatteilla, ja lopuksi
determinismi: miten sama syöte saadaan tuottamaan sama tulos.

## Uskottava, stabiili ja ajoissa

Fysiikka on sama kuin insinöörin simulaatiossa: Newtonin lait,
liikemäärän ja liikemäärämomentin säilyminen, kitka. Vaatimukset ovat
toiset. Tieteellisessä laskennassa virhe mitataan ja pienennetään
tihentämällä askelta ja verkkoa, ja laskenta saa kestää tunteja
(taito *Fysikaalinen mallinnus ja simulointi*). Pelissä aikabudjetti on
kiinteä, eikä tulosta verrata mittaukseen. Siksi tärkeysjärjestys on
toinen:

1. **Stabiilisuus.** Simulaatio ei saa räjähtää, vaikka kappaleet
   pinotaan, puristetaan nurkkaan tai ammutaan toisiaan päin. Energiaa
   saa hävitä, mutta sitä ei saa syntyä.
2. **Aikabudjetti.** Laskenta on rajattu: kiinteä määrä ratkaisijan
   kierroksia askeleessa, ei kierroksia "kunnes virhe on pieni".
3. **Uskottavuus.** Pelaaja huomaa tärisevän pinon ja läpi putoavan
   kappaleen, mutta ei viiden prosentin virhettä heilurin jaksossa.

Tarkkuudesta ei silti luovuta kokonaan. Tutoriaalin testit vertaavat
simulaatiota lukion fysiikan kaavoihin aina, kun kaava on olemassa:
heilurin jakso, kaltevan tason kiihtyvyys, vierivän pallon loppunopeus
ja kelluvan kappaleen upotussyvyys. Kun kaavaa ei ole, tarkistetaan
säilymislait.

## Esitiedot ja rajaus

Tutoriaali jatkaa taidosta *3D-peliohjelmointi*, eikä sen sisältöä
opeteta uudelleen:

- kvaterniot asennon esityksenä ja niiden normalisointi
- törmäysmuodot (pallo, laatikko, kapseli, kolmio), lähin piste ja
  kosketus normaalina ja syvyytenä
- säteenheitto ja laatat (*slabs*) laatikkoa vastaan
- laaja vaihe tilarakenteella
- kinemaattinen hahmo-ohjain, jonka liikkeen koodi päättää.

Sen kautta oletetaan taidot *Peliohjelmointi* (kiinteä aika-askel,
puoli-implisiittinen Euler, impulssivaste ilman pyörimistä ja
lepäävien kosketusten iterointi kahdessa ulottuvuudessa),
*Renderöinnin perusteet*, *Moderni C++* ja *Lineaarialgebra*.
Fysiikasta riittää lukion mekaniikka: voima, liikemäärä, energia ja
vääntömomentti.

Tutoriaalin ulkopuolelle jäävät:

- **Ajoneuvot, räsynuket kokonaisuutena ja murtuminen.** Ne ovat tässä
  opittujen rajoitteiden sovelluksia, ja ne mainitaan vain lyhyesti.
- **Yleiset kuperat muodot ja kolmioverkot dynaamisina kappaleina.**
  Moottorin kappaleet ovat palloja ja laatikoita; yleisen kuperan
  muodon menetelmät (GJK ja EPA) esitellään periaatteena.
- **Laskenta näytönohjaimella** on taidossa *GPU-laskenta*.
- **Tarkkuuteen tähtäävä simulointi** on taidossa *Fysikaalinen
  mallinnus ja simulointi*.
- **Valmiin fysiikkamoottorin käyttö.** Viimeinen luku kertoo, millä
  nimillä tämän tutoriaalin käsitteet löytyvät yleisistä moottoreista.

## Ensimmäinen simulaatio

Valmiin moottorin käyttö on lyhyt. Maailmaan lisätään kappaleita, ja
sitä askelletaan kiinteällä aika-askeleella:

```{.cpp tiedosto="esimerkit/01-ensimmainen.cpp" osa="maailma"}
```

```{.cpp tiedosto="esimerkit/01-ensimmainen.cpp" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

![Ensimmäinen simulaatio 0,6 sekunnin välein: pallo vierii ramppia
alas, osuu torniin ja torni kaatuu. Kuvat ovat samasta ohjelmasta kuin
tuloste.](kuvat/ensimmainen.png){width=100%}

Kukaan ei kirjoittanut koodia, joka kaataa tornin. Pallo vierii, koska
rampin kitka panee sen pyörimään, torni kaatuu, koska osuma antaa
alimmalle laatikolle impulssin, ja laatikot jäävät lattialle, koska
kosketukset estävät niitä vajoamasta. Loput luvut rakentavat funktion
`askel` sisällön.

## Tutoriaalin rakenne

| Luku | Aihe |
|------|------|
| Jäykän kappaleen tila | massakeskipiste, asento, kulmanopeus, hitaustensori |
| Voimat ja integrointi | vääntömomentti, pyörimisen integrointi, säilyvät suureet |
| Kosketukset | kosketuspisteet pallolle, tasolle ja laatikolle; monisto |
| Törmäysvaste | impulssi, kun kappaleet saavat pyöriä |
| Kitka | Coulombin laki, kitkakartio ja sen likiarvo |
| Rajoitteet ja ratkaisija | peräkkäiset impulssit, lämmin käynnistys, sijainnin korjaus |
| Nivelet | etäisyys, pallonivel ja sarana |
| Simulaatioaskel, pinot ja lepo | askeleen vaiheet, laaja vaihe, saaret ja nukahtaminen |
| Nopeat kappaleet | tunneloituminen ja jatkuva törmäystunnistus |
| Kangas | jouset, jäykkyysraja ja sijaintipohjainen dynamiikka |
| Vesi ja hiukkaset | korkeuskenttä, noste ja hiukkasallas |
| Determinismi | toistettavuus, tilannevedokset ja liukuluvut |
| Lopuksi | fysiikkamoottorit, nyrkkisäännöt, jatkotaidot ja lähteet |

Luvut 2–9 rakentuvat toistensa päälle ja muodostavat jäykkien
kappaleiden moottorin. Kangas, vesi ja determinismi ovat luettavissa
erikseen, kun rajoitteiden ajatus luvusta 7 on tuttu.

## Esimerkit ja työkalut

Esimerkit ovat C++23:a. Ne käännetään testeissä GCC 14:llä ja Clang
20:llä AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, ja
molempien kääntäjien tulosteen on oltava sama. Moottori on
otsaketiedostoina hakemistossa `esimerkit/yhteinen/`:

| Otsake | Sisältö |
|--------|---------|
| `vektori.hpp`, `matriisi3.hpp`, `kvaternio.hpp` | `Vec3`, `Mat3`, `Kvat`; samat sopimukset kuin taidossa *3D-peliohjelmointi* |
| `kappale.hpp` | jäykkä kappale, hitaustensori, integrointi |
| `kosketus.hpp` | kapea vaihe: kosketuspisteet |
| `ratkaisija.hpp` | kosketusrajoitteet ja peräkkäiset impulssit |
| `nivel.hpp` | etäisyys, pallonivel, sarana |
| `maailma.hpp` | laaja vaihe, simulaatioaskel, lepotila, pyyhkäisy |
| `kangas.hpp`, `vesi.hpp` | kangas, korkeuskenttävesi ja hiukkasallas |
| `liukuluvut.hpp` | liukulukulaskennan toistettavuus |
| `piirto.hpp`, `kuvitus.hpp` | kuvitus: pieni ohjelmistorenderöijä |

Ulkoisia kirjastoja ei ole. Koordinaatisto on oikeakätinen, y osoittaa
ylös, yksiköt ovat metri, kilogramma ja sekunti, ja kulmat ovat
radiaaneja. Yksittäisen esimerkin voi kääntää ja ajaa
esimerkkihakemistossa:

```text
g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined 09-pino.cpp
./a.out             # testattu tuloste
./a.out pyramidi    # lisäksi kuvasarja pyramidi-1.ppm ...
```

Esimerkit eivät avaa ikkunaa. Kuvat syntyvät pienellä
ohjelmistorenderöijällä, joka on sama kuin taidossa
*3D-peliohjelmointi*, ja kuvaajat piirretään esimerkkien kirjoittamista
aikasarjoista (`make kuvat`).

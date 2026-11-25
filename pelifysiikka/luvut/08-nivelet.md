# Nivelet

Kosketus on rajoite, joka syntyy ja katoaa itsestään. *Nivel* on
rajoite, jonka suunnittelija asettaa: ovi on saranalla karmissa,
lamppu roikkuu ketjussa, heiluri kääntyy kiinnityspisteensä ympäri.
Nivel ratkaistaan samalla ratkaisijalla kuin kosketus. Eroja on kaksi:
impulssi saa olla kumman merkkinen tahansa, koska nivel sekä työntää
että vetää, ja rivejä on yhdestä kuuteen sen mukaan, kuinka monta
liikkeen vapausastetta nivel poistaa.

## Vapausasteet

Vapaalla jäykällä kappaleella on kuusi vapausastetta: kolme
siirtymälle ja kolme kierrolle. Nivel poistaa niistä osan.

| Nivel | Poistaa | Jää | Esimerkki |
|-------|---------|-----|-----------|
| etäisyys | 1 (pisteiden etäisyys) | 5 | köysi, tanko |
| pallonivel | 3 (pisteen siirtymä) | 3 kiertoa | olkapää, ketjun lenkki |
| sarana | 5 | 1 kierto | ovi, kyynärpää, pyörä |
| liukunivel | 5 | 1 siirtymä | mäntä, hissi |
| kiinteä | 6 | 0 | kaksi kappaletta yhtenä |

Tässä luvussa toteutetaan kolme ensimmäistä.

```{.cpp tiedosto="esimerkit/yhteinen/nivel.hpp" osa="nivel"}
```

Kiinnityspisteet tallennetaan kummankin kappaleen omaan
koordinaatistoon. Kun kappaleet liikkuvat, pisteet muunnetaan
maailmaan, ja niiden ero on nivelen *virhe*.

## Etäisyys ja pallonivel

Etäisyysrajoitteessa on yksi rivi, jonka suunta on pisteestä toiseen:
pisteiden suhteellinen nopeus tässä suunnassa pidetään nollassa.

Pallonivelessä kiinnityspisteiden on pysyttävä samassa paikassa, eli
niiden suhteellisen nopeuden on oltava nolla kaikissa kolmessa
suunnassa. Kolme riviä voisi ratkaista yksi kerrallaan, mutta ne
kytkeytyvät toisiinsa samassa pisteessä niin vahvasti, että kannattaa
ratkaista ne kerralla. Tehollisen massan tilalle tulee 3 × 3
-matriisi

$$K = \Bigl(\frac1{m_a} + \frac1{m_b}\Bigr)\mathbf 1
  - [\mathbf r_a]_\times I_a^{-1} [\mathbf r_a]_\times
  - [\mathbf r_b]_\times I_b^{-1} [\mathbf r_b]_\times,$$

missä $[\mathbf r]_\times$ on ristitulon matriisi, ja impulssi on
$K^{-1}$ kertaa nopeusvirhe. Tämä on *lohkoratkaisu*: pieni
yhtälöryhmä ratkaistaan tarkasti iteroinnin sisällä.

```{.cpp tiedosto="esimerkit/yhteinen/nivel.hpp" osa="valmistelu"}
```

## Sarana

Sarana on pallonivel, jolle lisätään kaksi kulmariviä. Kummallakin
kappaleella on oma akselinsa, ja niiden on pysyttävä samansuuntaisina.
Ehto kirjoitetaan kahden vektorin avulla: kappaleen $b$ akselilla ei
saa olla komponenttia kahteen kappaleen $a$ akselia vastaan
kohtisuoraan suuntaan. Vapaaksi jää kierto yhteisen akselin ympäri.

```{.cpp tiedosto="esimerkit/yhteinen/nivel.hpp" osa="ratkaise"}
```

Lämpimässä käynnistyksessä on nivelille ominainen ansa. Yhden rivin
rajoitteesta talletetaan kertynyt impulssi *lukuna*, ja suunta
lasketaan joka askeleella uudelleen. Jos talteen pannaan vektori,
vanhan suunnan komponentti, jota uusi rivi ei näe, jää kappaleeseen
pysyväksi voimaksi. Tämän tutoriaalin heiluri kiihtyi ensimmäisessä
versiossaan itsestään juuri siitä syystä, ja virhe löytyi energian
seurannalla.

## Heiluri testinä

Heilurin jaksolle on kaava, joten nivelet voi tarkistaa samaan tapaan
kuin kitkan. Pistemäinen paino metrin langassa heilahtaa ajassa
$2\pi\sqrt{L/g}$ ja päästään roikkuva metrin tanko ajassa
$2\pi\sqrt{2L/(3g)}$.

```{.cpp tiedosto="esimerkit/08-nivelet.cpp" osa="heilurit"}
```

```{.cpp tiedosto="esimerkit/08-nivelet.cpp" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/08-nivelet.odotettu" rivit="1-6"}
```

Jaksot osuvat millisekunnin tarkkuudella. Lankaheilurin ero kaavaan
ei ole simulaation virhe: kaava pätee äärettömän pienelle
heilahdukselle, ja tässä käytetyllä 0,1 radiaanin kulmalla tarkka
jakso on 0,06 prosenttia pidempi. Tulos ei riipu askeleen pituudesta,
mikä kertoo, että virhe ei tule integroinnista.

Nivelellä yhdistetyt kappaleet eivät saa törmätä toisiinsa. Tangon
pää on kiinni katossa, ja jos moottori loisi niiden välille myös
kosketuksen, nivel ja kosketus taistelisivat samasta liikkeestä.
Simulaatioaskel ohittaa siksi parit, joilla on yhteinen nivel.

## Ketju ja ajautuminen

Viiden lenkin ketju on vaikeampi tapaus: jokainen nivel vetää
naapureitaan, ja alussa ketju putoaa vaakasuorasta asennosta nopeasti.

```{.cpp tiedosto="esimerkit/08-nivelet.cpp" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/08-nivelet.odotettu" alkaen="viiden lenkin ketju" asti="0.2         10          4"}
```

![Ketju putoaa ja heilahtaa. Kuvien väli on 0,23
sekuntia.](kuvat/ketju.png){width=100%}

Taulukosta näkyy kolme asiaa:

- **Ilman sijainnin korjausta nivelet ajautuvat erilleen.**
  Nopeusrajoite pitää pisteiden nopeuden samana, mutta kaarevalla
  radalla suora askel vie pisteet silti erilleen. Virhe kertyy:
  kymmenessä sekunnissa rako on 39 senttimetriä.
- **Korjaus pitää raon kurissa mutta ei poista sitä.** Suurin rako,
  seitsemän senttimetriä, syntyy nopean putoamisen aikana.
- **Kierrosten lisääminen ei auta, askeleen lyhentäminen auttaa.**
  Neljäkymmentä kierrosta antaa saman raon kuin kymmenen, koska
  rivit toteutuvat jo: virhe syntyy vasta, kun paikat integroidaan.
  Neljä aliaskelta kymmenellä kierroksella pienentää raon
  kuudesosaan.

Energia pienenee kaikissa tapauksissa. Osa häviöstä on todellista,
sillä lenkit törmäävät toisiinsa kimmottomasti, ja osa on ratkaisijan
ja korjauksen tuottamaa vaimennusta. Iteroiva ratkaisija vaimentaa
ketjuja ja köysiä aina hieman, ja pitkät ketjut tuntuvat siksi
todellisia kumimaisemmilta.

## Sarana käytännössä

```{.cpp tiedosto="esimerkit/08-nivelet.cpp" osa="sarana"}
```

```{.tuloste tiedosto="esimerkit/08-nivelet.odotettu" alkaen="ovi 2 s"}
```

Ovelle annetaan kulmanopeus, jossa on komponentteja kaikkien kolmen
akselin ympäri. Sarana poistaa kaksi niistä ensimmäisessä askeleessa.
Jäljelle jäävä pyöriminen pystyakselin ympäri on hitaampaa kuin
alkuarvo 2 rad/s, koska ovi kääntyy nyt reunansa eikä
massakeskipisteensä ympäri ja liikemäärämomentti saranan akselin
suhteen säilyy: $I_\text{keskellä}\cdot 2 = I_\text{reunalla}\cdot
0{,}50$.

## Käytännössä

- **Nivelet ennen kosketuksia.** Ratkaisija käy nivelet ensin, jolloin
  kosketukset toteutuvat tarkemmin. Venyvä ketju on pienempi virhe
  kuin lattian läpi roikkuva.
- **Rajat ja moottorit.** Saranan kiertokulmalle annetaan tavallisesti
  rajat (ovi aukeaa 110 astetta), ja niveleen voi liittää moottorin,
  joka ajaa kulmanopeutta kohti tavoitetta enintään annetulla
  väännöllä. Molemmat ovat yksi lisärivi: raja on epäyhtälö kuten
  kosketus, moottori on rivi, jonka impulssi on rajattu.
- **Räsynukke** on kymmenkunta kappaletta ja niveliä kulmarajoineen.
  Vaikeus ei ole nivelissä vaan massasuhteissa ja rajojen
  virittämisessä.
- **Pitkät ketjut ja köydet** ovat iteroivalle ratkaisijalle huonoin
  tapaus: virhe etenee ketjua pitkin lenkki kerrallaan. Köysi
  kannattaa usein tehdä luvun 11 hiukkasmenetelmällä.
- **Älä anna niveltyneiden kappaleiden törmätä toisiinsa**, ellei
  siihen ole syytä. Moottoreissa tämä on nivelen asetus.
- **Irtoava nivel.** Nivelen kertynyt impulssi kertoo siihen
  kohdistuvan voiman. Kun se ylittää rajan, nivel poistetaan: näin
  tehdään katkeavat köydet ja hajoavat rakenteet.

## Itsearviointi

- Osaat kertoa, montako vapausastetta etäisyysrajoite, pallonivel ja
  sarana poistavat.
- Osaat selittää, miksi pallonivelen kolme riviä ratkaistaan yhtenä
  lohkona.
- Osaat tarkistaa nivelen toteutuksen heilurin jaksolla.
- Osaat selittää, miksi nivelet ajautuvat erilleen ilman sijainnin
  korjausta ja miksi kierrosten lisääminen ei korjaa sitä.
- Osaat kertoa, miksi yhden rivin rajoitteen kertynyt impulssi
  talletetaan lukuna.

# Rajoitteet ja ratkaisija

Yhden kosketuspisteen impulssi on suljettu kaava. Laatikkopinossa
kosketuksia on kymmeniä, ja jokainen vaikuttaa naapureihinsa: kun
alimman laatikon ja lattian välinen impulssi pysäyttää alimman
laatikon, toiseksi alin törmää siihen. Tässä luvussa kosketukset
ratkaistaan yhdessä menetelmällä, jota lähes kaikki pelien
fysiikkamoottorit käyttävät: *peräkkäisillä impulsseilla*
(*sequential impulses*). Sama ratkaisija hoitaa seuraavassa luvussa
nivelet.

## Rajoite nopeuksille

*Rajoite* on ehto, jonka kappaleiden liikkeen on toteutettava.
Kosketuksen rajoite on "pinnat eivät saa lähestyä toisiaan", kitkan
"pinnat eivät saa liukua" ja nivelen "nämä kaksi pistettä pysyvät
yhdessä". Moottori ratkaisee rajoitteet *nopeuksille*: se etsii
impulssit, joiden jälkeen nopeudet toteuttavat ehdot, ja integroi
sitten paikat näillä nopeuksilla.

Jokainen rajoite on yksi tai useampi *rivi*. Rivillä on suunta
(kosketuksessa normaali), ja siihen liittyy kolme lukua, jotka
lasketaan kerran askeleen alussa:

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="massat"}
```

*Tehollinen massa* on luvun 5 kaavan nimittäjän käänteisluku: se
kertoo, kuinka suuri impulssi tarvitaan muuttamaan pisteiden
suhteellista nopeutta rivin suunnassa yhden yksikön. Kun rivin
nopeusvirhe on $v - v_\text{tavoite}$, korjaava impulssi on virhe
kertaa tehollinen massa.

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="valmistelu"}
```

## Peräkkäiset impulssit

Ratkaisija käy rivit läpi yksi kerrallaan ja korjaa kunkin virheen
ikään kuin muita rivejä ei olisi. Korjaus rikkoo aiemmin korjattuja
rivejä, joten kierros toistetaan. Jokaisella kierroksella virheet
pienenevät. Menetelmä on lineaarisen yhtälöryhmän Gaussin–Seidelin
iteraatio (taito *Numeeriset menetelmät*) sillä erolla, että
tuntemattomia rajataan matkalla.

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="normaali"}
```

Ratkaiseva yksityiskohta on rajaus. Kosketus saa työntää mutta ei
vetää, joten normaali-impulssi ei saa olla negatiivinen. Jos rajataan
jokaisen kierroksen *lisäys* ei-negatiiviseksi, impulssi voi vain
kasvaa, eikä liian suureksi arvattua impulssia voi perua. Siksi
jokainen rivi muistaa askeleen aikana *kertyneen* impulssinsa `jn`,
ja rajaus tehdään kertymälle: yksittäinen lisäys saa olla
negatiivinen, kunhan summa ei ole. Tämä yksi muutos erottaa toimivan
ratkaisijan pomppivasta.

Kitkan raja riippuu samasta kertymästä, kuten edellisessä luvussa
nähtiin, ja kierroksessa kitka ratkaistaan ennen normaaleja:

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="ratkaise"}
```

## Lämmin käynnistys

Levossa olevan pinon impulssit ovat lähes samat askeleesta toiseen:
jokainen kosketus kantaa yläpuolellaan olevien laatikoiden painon.
Jos ratkaisija aloittaa joka askeleella nollasta, sen on löydettävä
sama ratkaisu uudelleen kymmenellä kierroksella. *Lämmin käynnistys*
(*warm starting*) antaa edellisen askeleen impulssit heti askeleen
alussa, jolloin kierrokset vain hienosäätävät niitä:

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="lammita"}
```

Tätä varten uuden askeleen kosketuspiste on tunnistettava samaksi
kuin edellisen askeleen piste. Tässä moottorissa piste perii
impulssit, jos se on alle kahden senttimetrin päässä vanhasta:

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="periyta"}
```

Tästä syystä luvun 4 kosketusmarginaali on tarpeen. Jos lepäävän
laatikon kärki olisi vuorotellen millimetrin tason ylä- ja
alapuolella, piste katoaisi ja syntyisi uudelleen, ja sen kertynyt
impulssi nollautuisi joka kerta.

Esimerkki mittaa kierrosten määrän ja lämpimän käynnistyksen
vaikutuksen kuuden kuution pinolla:

```{.cpp tiedosto="esimerkit/07-ratkaisija.cpp" osa="pino"}
```

```{.cpp tiedosto="esimerkit/07-ratkaisija.cpp" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/07-ratkaisija.odotettu" rivit="1-10"}
```

![Pinon ylimmän laatikon korkeus ajan funktiona neljällä asetuksella.
Ilman lämmintä käynnistystä neljä kierrosta ei riitä kantamaan pinoa,
ja se kaatuu viidessä sekunnissa.](kuvat/ratkaisija.png){width=75%}

Ilman lämmintä käynnistystä pino vajoaa ja huojuu vielä 30
kierroksellakin. Lämpimällä käynnistyksellä kymmenen kierrosta pitää
sen pystyssä puolen senttimetrin tarkkuudella. Lämmin käynnistys ei
maksa juuri mitään, ja se on ratkaisijan tärkein yksittäinen
parannus. Liian vähillä kierroksilla sekään ei auta: ensimmäisten
askelten aikana syntynyt virhe kaataa pinon ennen kuin kertymät
ehtivät asettua.

## Sijainnin korjaus

Nopeusrajoite estää kappaleita lähestymästä, mutta se ei poista
limitystä, joka on jo syntynyt. Limitystä syntyy aina: ratkaisija ei
suppene täysin, ja paikat integroidaan äärellisellä askeleella.

*Baumgarten korjaus* lisää rivin tavoitenopeuteen termin, joka on
verrannollinen virheeseen:

$$v_\text{tavoite} = \frac{\beta}{\Delta t}\,
  \max(0,\ \text{syvyys} - \text{vara}).$$

Kerroin $\beta$ kertoo, kuinka suuri osa virheestä korjataan yhdessä
askeleessa. *Vara* (*slop*) on pieni sallittu limitys, jota ei
korjata; ilman sitä kosketus värähtelisi nollan ympärillä.

Korjauksella on hinta. Se muuttaa virheen nopeudeksi, ja nopeus on
liike-energiaa, jota fysiikassa ei ole:

```{.cpp tiedosto="esimerkit/07-ratkaisija.cpp" osa="baumgarte"}
```

```{.tuloste tiedosto="esimerkit/07-ratkaisija.odotettu" alkaen="laatikko 10 cm"}
```

Pienellä kertoimella laatikko nousee pinnalle rauhallisesti puolessa
sekunnissa. Kertoimella 0,8 se on pinnalla kahdessa askeleessa mutta
lentää metrin ilmaan. Kun peliin ilmestyy kappale toisen sisään, tämä
näkyy kappaleiden sinkoutumisena.

Tavallisia tapoja lieventää ongelmaa ovat pieni $\beta$ (0,1–0,3),
korjausnopeuden katto ja korjaus erillisillä *näennäisnopeuksilla*,
jotka siirtävät kappaletta mutta eivät jää sen nopeudeksi (*split
impulse*). Luvun 11 sijaintipohjainen dynamiikka kääntää asetelman
toisin päin: se korjaa sijainnit suoraan ja johtaa nopeudet niistä.

## Ennakoiva kosketus

Kun kosketuspiste luodaan marginaalin sisällä ennen kuin pinnat
osuvat, sen syvyys on negatiivinen. Silloin rivin tavoitteeksi
asetetaan

$$v_\text{tavoite} = \frac{\text{syvyys}}{\Delta t} < 0,$$

eli pinnat saavat lähestyä toisiaan juuri sen verran, että rako
sulkeutuu askeleen aikana. Kappale pysähtyy pintaan eikä sen sisään.
Tällaista riviä kutsutaan *ennakoivaksi kosketukseksi* (*speculative
contact*), ja se on halvin tapa vähentää läpimenoja. Luku 10 palaa
asiaan.

## Käytännössä

- **Kiinteä määrä kierroksia.** Kierrosten määrä on aikabudjetti:
  tavallisia arvoja ovat 4–10. Ratkaisija lopetetaan kesken, ja
  jäljelle jäänyt virhe hyväksytään.
- **Kertyneet impulssit ja lämmin käynnistys** kuuluvat jokaiseen
  toteutukseen. Ilman niitä pinot eivät pysy pystyssä millään
  kohtuullisella kierrosmäärällä.
- **Järjestys vaikuttaa.** Viimeisenä ratkaistu rivi toteutuu
  tarkimmin. Siksi normaalit ratkaistaan kitkan jälkeen ja kosketukset
  nivelten jälkeen: läpimeno on pahempi virhe kuin pieni liukuma.
- **Massasuhteet.** Raskas kappale kevyen päällä suppenee hitaasti,
  koska kevyen kappaleen rivit siirtävät raskasta vain vähän
  kierroksessa. Lääkkeitä ovat kohtuulliset massat, lisäkierrokset ja
  aliaskeleet.
- **Aliaskeleet kierrosten sijaan.** Uudemmat moottorit jakavat
  askeleen useaan lyhyeen aliaskeleeseen ja tekevät kussakin vain
  yhden tai kaksi kierrosta. Lyhyempi askel pienentää sekä
  integroinnin että rajoitteiden virhettä, ja tulos on samalla
  laskentamäärällä usein jäykempi. Seuraava luku mittaa tämän.
- **Pehmeät rajoitteet.** Baumgarten kertoimen sijasta rajoitteelle
  voi antaa jousen taajuuden ja vaimennussuhteen. Parametrit ovat
  silloin askeleen pituudesta riippumattomia ja suunnittelijalle
  ymmärrettäviä.

## Itsearviointi

- Osaat selittää, mitä rajoitteen rivi ja tehollinen massa ovat.
- Osaat kuvata peräkkäisten impulssien kierroksen ja perustella, miksi
  rajaus tehdään kertyneelle impulssille.
- Osaat kertoa, mitä lämmin käynnistys tekee ja mitä se vaatii
  kosketuspisteiltä.
- Osaat selittää Baumgarten korjauksen ja sen, miksi suuri kerroin
  lisää simulaatioon energiaa.
- Osaat kertoa, mikä ennakoiva kosketus on.

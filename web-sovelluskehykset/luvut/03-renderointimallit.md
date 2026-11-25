# Renderöintimallit

Jokaisen kehyksen ytimessä on vastaus yhteen kysymykseen: **kun tila
muuttuu, mistä kehys tietää, mitä DOM:n kohtia on päivitettävä?**
Vastauksia on neljä. Ne selittävät suurimman osan kehysten eroista:
miksi Reactissa tilaa ei saa muuttaa paikallaan, miksi Vuessa arvo
luetaan `.value`-kentästä ja miksi Svelte tarvitsee kääntäjän.

Tässä luvussa jokainen malli toteutetaan muutamalla kymmenellä rivillä.
Toteutukset eivät ole käyttökelpoisia kehyksiä, mutta ne ovat ajettavia,
ja niiden tulosteista näkyy, kuinka paljon työtä kukin malli tekee.

```{.dot otsikko="Neljä tapaa päästä tilan muutoksesta DOM:n päivitykseen"}
digraph {
  rankdir=LR;
  node [width=1.9];
  m [label="tila muuttuu", shape=ellipse, width=1.2];
  d [label="DOM päivittyy", shape=ellipse, width=1.2];
  a [label="näkymä lasketaan uudelleen,\nkuvauksia verrataan"];
  b [label="kaikki sidokset\nluetaan ja verrataan"];
  c [label="arvo ilmoittaa\nlukijoilleen"];
  e [label="käännetty koodi\npäivittää tietyt solmut"];
  m -> a [label="virtuaalinen DOM"]; a -> d;
  m -> b [label="muutostentunnistus"]; b -> d;
  m -> c [label="signaalit"]; c -> d;
  m -> e [label="kääntäjä"]; e -> d;
}
```

## Virtuaalinen DOM

Reactin perusajatus on, että näkymä on **funktio tilasta**. Komponentti
ei päivitä mitään: se palauttaa kuvauksen siitä, miltä näkymän pitää
näyttää tällä tilalla. Kuvaus on kevyt oliopuu, virtuaalinen DOM.

```{.typescript tiedosto="esimerkit/periaatteet/vdom.ts" osa="solmu"}
```

Kun tila muuttuu, funktio ajetaan uudelleen ja kehys vertaa uutta
kuvausta edelliseen. Vain erot viedään oikeaan DOM:iin. Tätä vertailua
kutsutaan **täsmäytykseksi** (*reconciliation*).

```{.typescript tiedosto="esimerkit/periaatteet/vdom.ts" osa="tasmaytys"}
```

Kokeillaan kolmea muutosta tehtävälistaan:

```{.typescript tiedosto="esimerkit/periaatteet/vdom.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/vdom.odotettu"}
```

Ensimmäinen tulos näyttää mallin vahvuuden: koko näkymä laskettiin
uudelleen, mutta DOM:iin tehtiin yksi muutos. Kaksi jälkimmäistä
näyttävät, miksi listoissa tarvitaan avaimet. Ilman avaimia vertailu
etenee järjestysnumeron mukaan: ensimmäistä riviä verrataan ensimmäiseen
ja niin edelleen, joten yhden rivin poisto näyttää siltä, että jokaisen
rivin sisältö vaihtui. Lopputulos on ruudulla oikea, mutta väärät
elementit säilyivät, ja niiden mukana kohdistus ja kenttien arvot
siirtyvät väärille riveille. Avaimilla sama muutos on yksi poisto.

Mallin seuraukset:

- **Tila on muuttumaton arvo.** Kehys huomaa muutoksen siitä, että
  komponentille annetaan uusi tila. Jos taulukkoa muutetaan paikallaan,
  viittaus on sama eikä mitään tapahdu. Tästä tulee Reactin sääntö
  kopioida muutettaessa.
- **Komponenttifunktio ajetaan usein.** Jokainen tilan muutos ajaa
  komponentin ja oletuksena sen lapset uudelleen. Siksi funktion on
  oltava puhdas ja nopea, ja siksi Reactissa on välineet laskennan
  ohittamiseen (`memo`, `useMemo`) sekä kääntäjä, joka lisää niitä
  automaattisesti.
- **Kustannus riippuu näkymän koosta**, ei muutoksen koosta: vertailu
  käy läpi koko alipuun.

Vue käyttää samaa mallia, mutta kahdella erolla: reaktiivinen tila
kertoo, mitkä komponentit on laskettava uudelleen (seuraava kohta), ja
mallipohjan kääntäjä merkitsee, mitkä kohdat voivat ylipäätään muuttua
(luku 4).

## Muutostentunnistus

AngularJS ja sen seuraaja Angular valitsivat alun perin toisen tien.
Tila on tavallisia olioita, joita saa muuttaa suoraan. Kehys ei tiedä,
mikä muuttui, joten jokaisen tapahtuman jälkeen se laskee mallipohjan
kaikki sidokset uudelleen ja vertaa tuloksia edellisiin.

```{.typescript tiedosto="esimerkit/periaatteet/muutostentunnistus.ts" osa="ydin"}
```

```{.typescript tiedosto="esimerkit/periaatteet/muutostentunnistus.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/muutostentunnistus.odotettu"}
```

Sovelluksen koodi on tässä mallissa yksinkertaisinta: ei kopioita, ei
erityisiä tilaolioita. Hinta näkyy viimeisestä rivistä. Hiiren
liikahdus ei muuttanut mitään, mutta kaikki sidokset tarkistettiin
silti, koska kehys ei voi tietää sitä etukäteen. Lisäksi kehyksen on
saatava tietää, milloin jokin tapahtuma on käsitelty. Angular ratkaisi
tämän pitkään kirjastolla `zone.js`, joka kietoi selaimen asynkroniset
rajapinnat (tapahtumat, ajastimet, verkkopyynnöt) omiin versioihinsa.

Angular on siirtymässä tästä mallista signaaleihin. Tämän tutoriaalin
Angular-toteutus toimii ilman `zone.js`-kirjastoa, ja sen tila on
kokonaan signaaleissa.

## Signaalit

Kolmas malli kääntää asetelman. Kehyksen ei tarvitse etsiä muutosta,
jos tila itse kertoo siitä. **Signaali** on arvo, joka kirjaa, kuka sitä
luki, ja ilmoittaa muutoksesta vain lukijoilleen.

```{.typescript tiedosto="esimerkit/periaatteet/signaalit.ts" osa="ydin"}
```

Riippuvuuksia ei luetella missään. Kun efekti ajetaan, jokainen sen
lukema signaali kirjaa sen lukijakseen. Tätä kutsutaan automaattiseksi
riippuvuuksien seurannaksi.

```{.typescript tiedosto="esimerkit/periaatteet/signaalit.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/signaalit.odotettu"}
```

Tulosteessa on kolme havaintoa:

- Suodattimen vaihto ajoi vain listan efektin. Yhteenveto ei lue
  suodatinta, joten siihen ei koskettu, eikä mitään verrattu.
- Kun lisättiin valmis tehtävä, avoimien määrä laskettiin uudelleen,
  mutta tulos oli sama luku, joten yhteenvedon efektiä ei ajettu.
  Muutos pysähtyi siihen, missä arvo ei muuttunut.
- Samassa tilanteessa listan efekti ajettiin, vaikka näkyvät tehtävät
  olivat samat. Suodatus tuotti uuden taulukon, ja uusi taulukko on eri
  arvo kuin vanha, vaikka sisältö olisi sama. Signaalit vertaavat
  viittauksia samoin kuin React.

Sama rakenne on Vuen `ref`- ja `computed`-funktioissa, Angularin
`signal`- ja `computed`-funktioissa, Solidin signaaleissa ja Svelten
riimuissa. Nimet vaihtelevat, kolmikko on sama: lähdearvo, johdettu arvo
ja efekti.

Mallin seuraukset:

- **Arvo on kääreen sisällä.** Seuranta vaatii, että lukeminen ja
  kirjoittaminen kulkevat kehyksen kautta. Siksi Vuessa kirjoitetaan
  `laskuri.value`, Angularissa `laskuri()` ja `laskuri.set(…)`. Svelte
  piilottaa kääreen kääntäjällä.
- **Kustannus riippuu muutoksen koosta**, ei näkymän koosta.
- **Riippuvuudet syntyvät ajon aikana.** Arvo, joka luetaan vain
  ehtolauseen toisessa haarassa, ei ole riippuvuus ennen kuin haara
  ajetaan. Tämä on yleensä oikein mutta yllättää joskus.

## Käännösaikainen reaktiivisuus

Neljäs malli tekee työn ennen selainta. Svelten alkuperäinen oivallus
oli, että mallipohjasta näkee jo käännösvaiheessa, mikä tekstisolmu
riippuu mistäkin muuttujasta. Kääntäjä voi tuottaa suoraan koodin,
joka päivittää oikeat solmut, eikä selaimeen tarvitse lähettää
vertailijaa.

```{.typescript tiedosto="esimerkit/periaatteet/kaantaja.ts" osa="kaantaja"}
```

```{.typescript tiedosto="esimerkit/periaatteet/kaantaja.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/kaantaja.odotettu"}
```

Tuotetussa koodissa ei ole silmukkaa eikä vertailua. Kun `maara`
muuttuu, kaksi tekstisolmua saa uuden arvon ja muu jää rauhaan.

Kääntäjä näkee kuitenkin vain yhden tiedoston kerrallaan. Tila, joka
kulkee funktioiden ja moduulien läpi, jää siltä näkemättä. Svelte 5
yhdisti siksi mallit: riimut (`$state`, `$derived`) ovat signaaleja,
joiden kääreen kääntäjä kirjoittaa näkymättömiin, ja mallipohjat
käännetään edelleen suoriksi DOM-päivityksiksi.

## Mallit kehyksissä

| Kehys | Miten muutos havaitaan | Miten DOM päivitetään |
|-------|------------------------|-----------------------|
| React | komponentille asetetaan uusi tila | komponentti ajetaan, virtuaalinen DOM täsmäytetään |
| Vue | reaktiivinen viittaus ilmoittaa lukijoilleen | komponentti ajetaan, käännetty mallipohja rajaa vertailun |
| Angular | signaali ilmoittaa (aiemmin: kaikki tarkistetaan) | komponentin mallipohjan sidokset päivitetään |
| Svelte | riimu ilmoittaa lukijoilleen | käännetty koodi päivittää tietyt solmut |

Sarakkeista näkyy, että "virtuaalinen DOM vastaan signaalit" on väärä
vastakkainasettelu. Kysymyksiä on kaksi: miten muutos havaitaan ja
kuinka tarkasti se viedään DOM:iin. Kehykset yhdistelevät vastauksia,
ja suunta on viime vuodet ollut sama kaikilla: muutoksen havaitseminen
siirtyy signaaleihin ja yhä suurempi osa työstä kääntäjälle.

## Käytännössä

- **Mallista seuraavat kehyksen säännöt.** Reactin "älä muuta tilaa
  paikallaan", Vuen `.value` ja Angularin sulut signaalin perässä eivät
  ole makuasioita vaan suoria seurauksia siitä, miten kehys havaitsee
  muutoksen. Kun mallin tuntee, sääntöjä ei tarvitse opetella ulkoa.
- **Avain on aina tiedon oma tunniste**, ei järjestysnumero. Sääntö on
  sama kaikissa neljässä kehyksessä, koska ongelma on sama: mikä vanha
  rivi vastaa mitäkin uutta.
- **Uusi taulukko on muutos, vaikka sisältö olisi sama.** Sekä
  virtuaalinen DOM että signaalit vertaavat viittauksia. Johdettu arvo,
  joka palauttaa joka kerta uuden olion, käynnistää lukijansa turhaan.
  Yleensä se ei haittaa; raskaissa näkymissä siihen kannattaa
  kiinnittää huomiota.
- **Suorituskykyerot ovat useimmissa sovelluksissa merkityksettömiä.**
  Kaikki neljä mallia päivittävät tavallisen lomakenäkymän nopeammin
  kuin käyttäjä ehtii huomata. Erot näkyvät tuhansien rivien
  taulukoissa ja tiheästi päivittyvissä kaavioissa, ja niissäkin ensin
  kannattaa mitata (taito *Web-sovellukset*, suorituskykyluku).
- **Älä valitse kehystä vertailutestin perusteella.** Mittarit mittaavat
  kehyksen ydintä, ja oikean sovelluksen hitaus on lähes aina omassa
  koodissa tai verkossa.

## Itsearviointi

- Osaat selittää neljä tapaa, joilla kehys saa tietää, mitä DOM:n kohtia
  on päivitettävä, ja nimetä kehyksen kullekin.
- Osaat perustella virtuaalisen DOM:n mallilla, miksi Reactissa tila
  kopioidaan eikä muuteta paikallaan.
- Osaat kertoa, mitä signaali, johdettu arvo ja efekti ovat ja miten
  riippuvuudet syntyvät ilman, että niitä luetellaan.
- Osaat selittää täsmäytyksen tulosteesta, mitä avaimen puuttuminen
  listasta aiheuttaa.
- Osaat sanoa, mitä rajoitteita käännösaikaisella reaktiivisuudella on
  ja miksi Svelte yhdisti sen signaaleihin.

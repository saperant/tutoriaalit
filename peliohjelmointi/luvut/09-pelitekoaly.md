# Pelitekoäly

Pelin tekoälyn tehtävä on tuottaa uskottavia ja ennustettavia
vastustajia, ei optimaalista peliä. Useimmat pelihahmot rakentuvat
kolmesta osasta: *päätös* (mitä hahmo yrittää), *havainto* (mitä se
tietää maailmasta) ja *liike* (miten se pääsee perille). Päätös on
luvun *Pelin tila ja tapahtumat* tilakone. Tämä luku lisää siihen kaksi
muuta: näkölinjan ja reitinhaun.

## Reitinhaku ruudukossa

Reitinhaku etsii halvimman reitin verkossa. Ruutukartassa solmuja ovat
ruudut ja kaaria siirtymät viereisiin ruutuihin; askeleen hinta voi
riippua maastosta.

```{.cpp tiedosto="esimerkit/yhteinen/reitinhaku.hpp" osa="kartta"}
```

*Dijkstran algoritmi* käsittelee ruudut hinnan mukaisessa
järjestyksessä alusta lähtien, joten se leviää joka suuntaan, kunnes
maali tulee vastaan. *A\** lisää jokaiselle ruudulle arvion
jäljellä olevasta matkasta, *heuristiikan* h, ja käsittelee ensin
ruudun, jonka f = g + h on pienin: g on tunnettu hinta alusta, f arvio
koko reitin hinnasta. Haku suuntautuu maalia kohti.

```{.cpp tiedosto="esimerkit/yhteinen/reitinhaku.hpp" osa="heuristiikka"}
```

Heuristiikan ehto on tärkein yksittäinen asia: jos arvio ei koskaan
ylitä todellista hintaa, A\* löytää halvimman reitin. Liian suuri arvio
tekee hausta nopeamman mutta reitistä mahdollisesti huonomman.
Nollaheuristiikalla A\* on Dijkstran algoritmi.

```{.cpp tiedosto="esimerkit/yhteinen/reitinhaku.hpp" osa="haku"}
```

Avoimet ruudut ovat prioriteettijonossa. Sama ruutu voi olla jonossa
useasti eri hinnoilla; vanhentuneet merkinnät ohitetaan, kun ne
nousevat kärkeen. Reitti kootaan lopuksi seuraamalla `mista`-taulukkoa
maalista alkuun. Tasatilanteiden järjestys on määrätty loppuun asti,
jotta haku on deterministinen (luku *Pelisilmukka*).

```{.cpp tiedosto="esimerkit/09-reitinhaku.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/09-reitinhaku.odotettu"}
```

Molemmat löytävät hinnan 26, mutta A\* tutkii 78 ruutua ja Dijkstra
182. Reitti kulkee suon läpi: 24 askelta, joista yksi maksaa kolme.
Kierto seinän alapäästä olisi 30 askelta. Jos suo olisi neljä ruutua
leveä, kierto voittaisi; halvin reitti ei ole sama asia kuin lyhin.
Kun maaliin ei pääse, haku käy läpi kaiken saavutettavan ennen kuin se
luovuttaa, mikä on reitinhaun kallein tapaus.

![Ruutujen käsittelyjärjestys vaaleasta tummaan samalla kartalla.
Dijkstran algoritmi leviää tasaisesti alusta, A\* etenee maalia kohti
ja laajenee sivuille vasta seinän edessä. Pisteytetty ruutu on
suota.](kuvat/reitinhaku.png){width=80%}

Algoritmien oikeellisuuden ja vaativuuden käsittelee taito
*Algoritmit*; tässä riittää, että prioriteettijonolla haku on
O(n log n) tutkittujen ruutujen määrän suhteen.

## Näkölinja

Vartija näkee pelaajan, jos tämä on kantaman sisällä eikä välissä ole
estettä. Ruudukossa näkölinja tarkistetaan käymällä läpi ruudut, joiden
kautta suora viiva kulkee (Bresenhamin viiva).

```{.cpp tiedosto="esimerkit/09-vartija.cpp" osa="nakolinja"}
```

Sama tarkistus kelpaa ammuksille ja valonlähteille. Jatkuvassa
maailmassa vastaava työkalu on säde (raycast) luvun *Törmäykset*
muotoja vastaan.

## Vartija: päätös, havainto ja liike yhdessä

Vartijalla on samat kolme tilaa kuin luvun *Pelin tila ja tapahtumat*
esimerkissä, mutta nyt havainto on näkölinja ja liike reitinhaun
tulos. Tila päättää vain *kohteen*: partiopisteen tai pelaajan
viimeisen havaitun ruudun.

```{.dot otsikko="Vartijan tilakone" leveys="75%"}
digraph {
  rankdir=LR; nodesep=0.5;
  node [shape=box, style=rounded];
  partio [label="partio\nkohde: partiopiste"];
  takaa [label="takaa-ajo\nkohde: pelaaja"];
  etsinta [label="etsintä\nkohde: viimeinen havainto"];
  partio -> takaa [label="näkee"];
  takaa -> etsinta [label="ei näe"];
  etsinta -> takaa [label="näkee"];
  etsinta -> partio [label="odotus päättyi"];
}
```

```{.cpp tiedosto="esimerkit/09-vartija.cpp" osa="vartija"}
```

Päivityksessä on kaksi vaihetta. Ensin havainto ratkaisee siirtymät,
sitten nykyinen tila valitsee kohteen ja reitinhaku antaa seuraavan
askeleen. Esimerkin pelaaja kävelee tallennettua reittiä vartijan
huoneeseen, pakenee ja piiloutuu seinän taakse.

```{.tuloste tiedosto="esimerkit/09-vartija.odotettu"}
```

![Sama ajo karttana. Vartija huomaa huoneeseensa tulleen pelaajan,
seuraa tätä
niin kauan kuin näkölinja säilyy, kävelee viimeiseen havaintopaikkaan,
odottaa ja palaa partioon. Pelaajan reitti on katkoviiva; täytetty neliö
on alku ja tyhjä loppu.](kuvat/vartija.png){width=95%}

Vartija ei huijaa: se ei tiedä pelaajan paikkaa, kun näkölinja
katkeaa, joten pelaaja voi paeta. Juuri tämä tekee vastustajasta
reilun. Kun vartija menee viimeiseen havaintopaikkaan eikä suoraan
pelaajan luo, pelaaja ymmärtää, miksi se toimii niin kuin toimii.

## Käytännössä

- **Reittiä ei lasketa joka ruudussa.** Esimerkki hakee reitin joka
  askeleella, koska kartta on pieni. Pelissä reitti lasketaan
  uudelleen, kun kohde vaihtaa ruutua tai reitti katkeaa, ja hakuja
  jaetaan usealle ruudulle (aikabudjetti).
- **Verkko on valinta.** Ruudukko sopii ruutukarttoihin. Vapaassa
  maastossa käytetään reittipisteitä tai navigointiverkkoa (navmesh),
  jossa solmuja on vähemmän; pelimoottorit laskevat sen tason
  geometriasta.
- **Liikkeen pehmennys:** ruudukon reitti on kulmikas. Hahmo ohjataan
  kohti reitin seuraavaa pistettä rajatulla kiihtyvyydellä (*steering*),
  ja turhat välipisteet poistetaan näkölinjatestillä.
- **Kun tilakone ei riitä:** tilojen ja siirtymien määrä kasvaa
  nopeasti. Käyttäytymispuu (behavior tree) kokoaa käyttäytymisen
  uudelleenkäytettävistä osista, ja hyötyfunktio (utility AI) pisteyttää
  vaihtoehdot ja valitsee parhaan. Molemmat päättävät edelleen vain
  kohteen; havainto ja liike pysyvät samoina.
- **Reaktioviive ja epätarkkuus** tehdään tarkoituksella. Vastustaja,
  joka reagoi samalla ruudulla ja osuu aina, tuntuu epäreilulta.
- **Hinta:** reitinhaku on tekoälyn kallein osa. Mittaa hakujen määrä
  ja tutkittujen ruutujen määrä ruutua kohden, ja rajaa ne.

## Itsearviointi

- Osaat toteuttaa A\*-haun ruudukossa ja selittää arvojen g, h ja f
  merkityksen.
- Osaat kertoa, milloin heuristiikka takaa halvimman reitin, ja miten
  A\* liittyy Dijkstran algoritmiin.
- Osaat tarkistaa näkölinjan ruudukossa.
- Osaat yhdistää tilakoneen, havainnon ja reitinhaun pelihahmoksi ja
  pitää ne erillään toisistaan.
- Osaat nimetä tilakonetta järeämmät päätösrakenteet ja reitinhaun
  kustannusten rajaamisen keinot.

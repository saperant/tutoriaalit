# Johdanto {.runko-johdanto}

Virtauslaskenta (*computational fluid dynamics*, CFD) ratkaisee
tietokoneella, miten neste tai kaasu liikkuu: ilma auton tai rakennuksen
ympärillä, vesi putkistossa, veri suonessa, jäähdytysilma
laitekotelossa. Sillä korvataan tuulitunnelikokeita, mitoitetaan pumppuja
ja lämmönvaihtimia ja ennustetaan säätä. Yhtälöt on tunnettu 1800-luvulta
asti, mutta käsin ne ratkeavat vain muutamassa yksinkertaisessa
tapauksessa.

Virtauslaskenta on fysikaalisen mallinnuksen vaativin arkinen
sovellus, ja syitä on kolme. Ne ovat samalla tämän tutoriaalin runko.

1. **Advektio.** Neste kuljettaa mukanaan kaiken, mitä siinä on: lämmön,
   savun ja myös oman liikemääränsä. Kuljetustermi käyttäytyy
   numeerisesti toisin kuin diffuusio, ja luontevin diskretointi on
   sille epästabiili. Luvut 3–5.
2. **Paine.** Kokoonpuristumattomassa virtauksessa paineelle ei ole omaa
   yhtälöä. Paine on se kenttä, joka pitää massan tallessa, ja se on
   ratkaistava jokaisella aika-askeleella koko alueessa. Luvut 6–8.
3. **Turbulenssi.** Useimmat kiinnostavat virtaukset ovat pyörteisiä
   kaikissa mittakaavoissa millimetrin osista metreihin. Kaikkea ei
   voi laskea auki, joten osa on mallinnettava. Luku 11.

Tutoriaalin tavoite on, että lukija ymmärtää, mitä virtauslaskentaohjelma
tekee ja miksi, ja osaa arvioida, voiko sen tulokseen luottaa. Siksi
kaikki toteutetaan itse NumPyllä ja SciPyllä pienissä kaksiulotteisissa
tehtävissä, ja jokainen tulos tarkistetaan tarkkaa ratkaisua, tasetta
tai tiheämpää hilaa vasten. Valmiita virtauslaskentaohjelmia ei ajeta,
mutta viimeinen luku kertoo, millä nimillä samat käsitteet löytyvät
niistä.

```{.dot otsikko="Tutoriaalin eteneminen. Jokainen vaihe lisää yhden vaikeuden edellisen päälle."}
digraph {
  rankdir=LR;
  node [shape=box];
  a [label="diffuusio\n(tuttu)"];
  b [label="+ advektio\nluvut 3–5"];
  c [label="+ paine\nluvut 6–8"];
  d [label="tarkistus-\ntehtävät\nluvut 9–10"];
  e [label="turbulenssi,\nratkaisijat\nluvut 11–12"];
  a -> b -> c -> d -> e;
}
```

## Esitiedot ja rajaus

Tutoriaali olettaa taidon *Fysikaalinen mallinnus ja simulointi*. Siitä
tarvitaan säilymislaki ja tase kontrollitilavuudessa, säilyvä
diskretointi, differenssimenetelmä lämpö- ja aaltoyhtälölle
stabiilisuusrajoineen, CFL-ehto, Poissonin yhtälön ratkaiseminen
harvalla matriisilla sekä tarkistamisen menetelmät: kertaluvun
mittaaminen, valmistettu ratkaisu ja Richardsonin ekstrapolointi. Näitä
ei johdeta uudelleen. Elementtimenetelmää ei tässä tarvita.

Tutoriaali käsittelee kokoonpuristumatonta, laminaaria virtausta kahdessa
ulottuvuudessa suorakulmaisella hilalla. Rajauksen ulkopuolelle jäävät

- kokoonpuristuva virtaus ja shokkiaallot, vapaat nestepinnat,
  monifaasivirtaukset ja lämmönsiirron kytkentä virtaukseen; näistä on
  lyhyt katsaus viimeisessä luvussa,
- turbulenssimallien toteutus; luku 11 selittää, mitä mallit tekevät ja
  mitä ne vaativat hilalta,
- rakenteettomat verkot ja mutkikkaat geometriat; luku 12 kertoo, mikä
  niissä muuttuu,
- reaaliaikainen nesteanimaatio peleissä, joka on taidossa
  *Pelifysiikka*. Siinä tavoite on uskottava ja ehdottoman stabiili
  liike kiinteässä aikabudjetissa. Tässä tavoite on tarkkuus, jonka
  suuruus tunnetaan, ja sen saavuttamiseen käytetään niin paljon
  laskenta-aikaa kuin tarvitaan.

## Työkalut

Esimerkit ovat Pythonia ja tarvitsevat vain NumPyn ja SciPyn. Luvussa 3
rakennetaan pieni kirjasto `kuljetus` aineen kulkeutumiselle tunnetussa
virtauksessa ja luvussa 7 kirjasto `virta`, joka ratkaisee Navier–Stokesin
yhtälöt. Myöhemmät luvut käyttävät niitä.

Esimerkit ajetaan hakemistossa `esimerkit/`, esimerkiksi
`python3 01-levy.py`. Jokaisen esimerkin tuloste on tallennettu
tiedostoon `.odotettu`, ja testit vertaavat ajon tulosta siihen. Kuvat
piirtää `kuvat/piirra.py` samoilla funktioilla, joita esimerkit
käyttävät (`make kuvat`). Raskaimmat esimerkit, onkalo ja pyörrerata,
kestävät kymmenestä kahteenkymmeneen sekuntia.

Tiheys on kaikissa virtausesimerkeissä vakio, ja se on jaettu yhtälöistä
pois: "paine" tarkoittaa painetta jaettuna tiheydellä ja viskositeetti
kinemaattista viskositeettia $\nu = \mu/\rho$ (m²/s).

## Ensimmäinen esimerkki: liikemäärä leviää kuten lämpö

Vedessä on suuri levy. Hetkellä nolla se nykäistään liikkeelle omassa
tasossaan nopeudella $U$. Kuinka paksu kerros vettä on sekunnin kuluttua
lähtenyt mukaan?

**Säilymislaki.** Tarkastellaan levyn suuntaista ohutta vesikerrosta
korkeudella $y$. Sen liikemäärä muuttuu vain sen verran kuin ylä- ja
alapinnan leikkausjännitykset sitä vetävät. **Aineen laki** on Newtonin
viskositeettilaki: leikkausjännitys on verrannollinen nopeuden
muutokseen kerrosten välillä, $\tau = \mu\,\partial u/\partial y$.
Yhdessä ne antavat

$$\frac{\partial u}{\partial t} = \nu\,\frac{\partial^2 u}{\partial y^2},
  \qquad u(0, t) = U, \qquad u(y, 0) = 0.$$

Tämä on lämpöyhtälö. Lämpötilan paikalla on nopeus ja
lämpötilanjohtavuuden paikalla kinemaattinen viskositeetti: **viskositeetti
on liikemäärän diffuusiota**. Levy on kuuma seinä, josta liikemäärä
johtuu nesteeseen.

```{.python tiedosto="esimerkit/01-levy.py" osa="malli"}
```

**Diskretointi.** Vesi jaetaan kerroksiin, ja jokaisen kerroksen tase
kirjoitetaan pintojen leikkausjännityksillä. Aika-askel on
implisiittinen Euler, koska yhtälö on jäykkä. Kaikki tämä on tuttua
taidosta *Fysikaalinen mallinnus ja simulointi*; uutta on vain suureiden
tulkinta.

```{.python tiedosto="esimerkit/01-levy.py" osa="ratkaisu"}
```

**Tarkistus.** Tehtävällä on tarkka ratkaisu virhefunktion avulla, joten
virhe voidaan mitata. Kun kerrosten paksuus puolitetaan ja aika-askel
jaetaan neljällä, virheen pitää pienentyä neljäsosaan.

```{.python tiedosto="esimerkit/01-levy.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/01-levy.odotettu" rivit="1-5"}
```

![Veden nopeus levyn yläpuolella kolmella hetkellä. Mukaan lähtenyt
kerros paksunee ajan neliöjuuressa.](kuvat/levy.png){width=70%}

Kerrosta, jossa nopeus poikkeaa ympäristöstä, sanotaan
**rajakerrokseksi**. Tarkasta ratkaisusta nähdään, että nopeus on
pudonnut prosenttiin levyn nopeudesta korkeudella
$\delta = 3{,}64\sqrt{\nu t}$:

```{.python tiedosto="esimerkit/01-levy.py" osa="paksuus"}
```

```{.tuloste tiedosto="esimerkit/01-levy.odotettu" rivit="6-9"}
```

Vastaus on 3,6 millimetriä. Luku kertoo virtauslaskennan
perusongelman: viskositeetti vaikuttaa vedessä ja ilmassa vain ohuessa
kerroksessa pintojen lähellä, ja juuri sinne tarvitaan tiheä hila.
Kaikkialla muualla nestettä liikuttavat paine ja sen oma hitaus, ja
niitä ei tässä esimerkissä ollut lainkaan. Loppu tutoriaalista käsittelee
niitä.

## Tutoriaalin rakenne

1. Johdanto
2. Virtauksen yhtälöt – massan ja liikemäärän tase, kokoonpuristumattomuus,
   Reynoldsin luku
3. Kontrollitilavuusmenetelmä – ruutujen tase, säilyvyys, savuvana
   tuulessa
4. Advektio – neljä kaaviota, numeerinen diffuusio, rajoittimet
5. Advektio ja diffuusio yhdessä – hilan Péclet'n luku, väärä diffuusio
6. Paine ja porrastettu hila – shakkilautaongelma, projektio
7. Projektiomenetelmä – kirjasto `virta`, Taylorin ja Greenin pyörre,
   aika-askeleen rajat
8. Reunaehdot – seinä, sisään- ja ulosvirtaus, reunan paikan vaikutus
9. Kansivetoinen onkalo – vakiotehtävä, kolme hilaa, virhearvio
10. Virtaus esteen ohi – pyörrerata, Strouhalin luku, kaavion vaikutus
11. Turbulenssi – mittakaavat, suoran simuloinnin hinta, mallien
    periaate, seinän läheisyys
12. Ratkaisijat ja suppeneminen – jäännös, monihila, mitä oikeat
    ohjelmat tekevät toisin
13. Lopuksi – tarkistuslista, käsitteet valmiissa ohjelmissa,
    jatkotaidot, lähteet

Luvut 2–5 käsittelevät kulkeutumista tunnetussa virtauksessa, ja niissä
riittävät yksinkertaiset ohjelmat. Luvuista 6–8 syntyy virtausratkaisija,
ja luvut 9–10 koettelevat sitä tehtävillä, joilla oikeatkin ohjelmat
tarkistetaan. Lukijalle, jota kiinnostaa vain valmiin ohjelman tulosten
arviointi, tärkeimmät ovat luvut 5, 8, 9 ja 11 sekä viimeisen luvun
tarkistuslista.

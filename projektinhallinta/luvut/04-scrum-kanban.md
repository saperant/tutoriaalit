# Scrum ja Kanban

Scrum ja Kanban ovat kaksi yleisintä tapaa järjestää ketterän tiimin
työ. Scrum jakaa ajan kiinteän mittaisiin jaksoihin ja määrittelee
roolit ja tapaamiset. Kanban ei määrää kumpaakaan vaan rajoittaa
keskeneräisen työn määrää ja ohjaa työn virtausta. Tässä luvussa
kuvataan kummankin säännöt, perustelut ja tavallisimmat tavat käyttää
niitä väärin.

## Scrum

Scrumin määrittelee Ken Schwaberin ja Jeff Sutherlandin ylläpitämä
*Scrum Guide*, kymmenkunta sivua pitkä dokumentti, jonka tuorein versio
on vuodelta 2020. Scrum kutsuu itseään kehykseksi: se kertoo, mitä
rooleja, tapahtumia ja tuotoksia on, mutta ei sitä, miten ohjelmisto
tehdään.

Scrum perustuu **empiiriseen prosessinohjaukseen**: koska työtä ei
voi suunnitella etukäteen tarkasti, tehdään vähän, katsotaan tulosta ja
säädetään. Tämä vaatii kolme asiaa: läpinäkyvyyttä (tilanne on kaikkien
nähtävissä), tarkastelua ja mukauttamista.

```{.dot otsikko="Scrumin sykli: jokainen sprintti tuottaa käyttökelpoisen lisäyksen"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  tj [label="tuotejono"]; ss [label="sprintin\nsuunnittelu"];
  sp [label="sprintti\n(enintään 1 kk)\npäivittäinen\nScrum"];
  ka [label="katselmus"]; re [label="retrospektiivi"];
  li [label="lisäys\n(valmis)", shape=box];
  tj -> ss -> sp -> ka -> re;
  sp -> li;
  ka -> tj [constraint=false, style=dashed, label="palaute"];
  re -> ss [constraint=false, style=dashed, label="parannukset"];
}
```

### Vastuut

Scrum-tiimissä on kolme vastuuta, ja tiimi on tyypillisesti enintään
kymmenen hengen kokoinen.

- **Tuoteomistaja** (*product owner*) vastaa siitä, että tiimi tekee
  arvokkainta mahdollista työtä. Hän järjestää tuotejonon. Tuoteomistaja
  on yksi henkilö, ei komitea, ja organisaation on kunnioitettava hänen
  päätöksiään.
- **Kehittäjät** tekevät työn ja päättävät, miten se tehdään ja
  paljonko sprinttiin otetaan.
- **Scrum master** vastaa siitä, että Scrum toimii: hän auttaa tiimiä
  parantamaan työtapojaan ja poistaa esteitä. Hän ei ole
  projektipäällikkö eikä jaa tehtäviä.

### Tapahtumat

**Sprintti** on enintään kuukauden mittainen jakso, jonka aikana
tehdään käyttökelpoinen lisäys tuotteeseen. Sprintit seuraavat toisiaan
ilman taukoja ja ovat saman mittaisia. Sprintin sisällä on neljä
tapahtumaa:

| Tapahtuma | Tarkoitus | Tulos |
|----------------------|--------------------------------------|---------------------------|
| sprintin suunnittelu | miksi, mitä ja miten tässä sprintissä | sprintin tavoite ja tehtävälista |
| päivittäinen Scrum | kehittäjät tarkistavat etenemisen kohti tavoitetta, 15 min | päivän suunnitelma |
| sprintin katselmus | lisäys näytetään sidosryhmille | palaute ja päivitetty tuotejono |
| retrospektiivi | tiimi tarkastelee omaa työtapaansa | parannustoimet |

### Tuotokset

Jokaiseen tuotokseen liittyy sitoumus, joka tekee siitä mitattavan:

| Tuotos | Sisältö | Sitoumus |
|----------------------|--------------------------------------|---------------------------|
| tuotejono | järjestetty lista kaikesta, mitä tuotteeseen tarvitaan | tuotetavoite |
| sprintin tehtävälista | sprinttiin valitut työt ja suunnitelma | sprintin tavoite |
| lisäys | käyttökelpoinen askel kohti tuotetavoitetta | valmiin määritelmä |

Olennaista on, että tiimi sitoutuu sprintin **tavoitteeseen**, ei
tehtävälistaan. Lista voi muuttua sprintin aikana, kun työstä opitaan
lisää, kunhan tavoite ei vaarannu. Vanhemmissa Scrum Guiden versioissa
puhuttiin sprintin sisältöön sitoutumisesta, ja moni organisaatio
toimii edelleen niin. Seuraava laskelma näyttää, miksi se on huono
ajatus.

### Mihin sprintissä voi sitoutua

Tiimin **nopeus** (*velocity*) on sprintissä valmistuneiden töiden
kokoarvioiden summa. Nopeus vaihtelee sprintistä toiseen. Kun
seuraavaan sprinttiin otetaan töitä historian keskiarvon verran,
kuinka usein kaikki valmistuu?

```{.python tiedosto="esimerkit/04-sprintti.py" osa="sitoumus"}
```

```{.tuloste tiedosto="esimerkit/04-sprintti.odotettu"}
```

Keskiarvoon mitoitettu sprintti valmistuu kokonaan joka toisella
kerralla. Tämä seuraa suoraan keskiarvon määritelmästä, mutta
käytännössä se tulkitaan usein tiimin epäonnistumiseksi. Jos sprintin
koko sisällön valmistuminen on lupaus, on mitoitettava alimman
neljänneksen mukaan, jolloin kolme sprinttiä neljästä onnistuu ja
osa kapasiteetista jää tarkoituksella varaukseksi.

Tulosteen kaksi viimeistä riviä testaavat kahta suosittua nyrkkisääntöä
historiaa vastaan. ”Eilisen sää” eli edellisen sprintin nopeus piti
viidessä sprintissä yhdestätoista, kolmen sprintin liukuva keskiarvo
viidessä yhdeksästä. Kumpikaan ei ole lupaus vaan keskimääräinen
odotus. Scrumin oma vastaus on sitoutua tavoitteeseen ja pitää osa
tehtävistä joustavina.

### Tavallisia väärinkäytöksiä

Scrum on helppo ottaa käyttöön muodollisesti ja vaikea oikeasti.
Tunnistettavia oireita:

- **Päivittäinen Scrum on tilanneraportti esihenkilölle.** Tapaamisen
  tarkoitus on kehittäjien keskinäinen suunnittelu.
- **Katselmuksessa näytetään kalvoja.** Tarkoitus on näyttää toimivaa
  ohjelmistoa ja saada siitä palautetta.
- **Retrospektiivi ei johda muutoksiin.** Jos samat asiat toistuvat
  kerrasta toiseen, tapaaminen on menettänyt merkityksensä.
- **Tuoteomistaja ei saa päättää.** Jos jokainen priorisointi
  hyväksytetään ohjausryhmässä, palautesilmukka on yhtä pitkä kuin
  ohjausryhmän kokousväli.
- **Nopeutta käytetään tavoitteena tai tiimien vertailuun.** Pisteet
  ovat tiimin sisäinen suhteellinen mitta. Kun niitä aletaan vaatia
  lisää, arviot kasvavat ja mittari menettää merkityksensä.
- **Sprintin lopussa ei ole mitään julkaistavaa.** ”Valmis” tarkoittaa
  silloin ”koodattu”, ja testaus ja integrointi kertyvät loppuun.
  Sprintit ovat vain vaiheittaisen mallin aikalaatikoita.

Scrumia on myös arvosteltu aiheesta. Tapahtumat vievät aikaa, ja
pienelle tai jatkuvaa ylläpitoa tekevälle tiimille sprinttirytmi voi
olla keinotekoinen. Scrum ei sisällä teknisiä käytäntöjä, joten ilman
automaattisia testejä ja jatkuvaa integraatiota lisäys ei pysy
julkaisukelpoisena. Ja koska Scrum paljastaa organisaation ongelmat
mutta ei ratkaise niitä, sen käyttöönotto ilman halua muuttaa mitään
muuta tuottaa lähinnä lisää palavereita.

## Kanban

Kanban on alun perin Toyotan tuotannonohjauksen väline: kortti
(japaniksi *kanban*) on lupa valmistaa lisää osia, ja korttien määrä
rajoittaa keskeneräisen tuotannon määrää. David J. Anderson sovitti
ajatuksen tietotyöhön 2000-luvun puolivälissä.

Kanban ei ole prosessimalli vaan tapa parantaa olemassa olevaa
prosessia. Lähtökohta on, että aloitetaan nykytilasta: rooleja ja
vastuita ei muuteta, vaan työ tehdään näkyväksi ja sitä aletaan ohjata.
Andersonin kuusi käytäntöä ovat:

1. **Tee työ näkyväksi.** Taulun sarakkeet vastaavat työn vaiheita ja
   kortit töitä.
2. **Rajoita keskeneräistä työtä** (*work in progress*, WIP).
   Sarakkeella on enimmäismäärä, ja uusi työ aloitetaan vasta, kun
   tilaa vapautuu.
3. **Hallitse virtausta.** Seurataan, kuinka kauan työt viipyvät ja
   mihin ne pysähtyvät.
4. **Tee pelisäännöt näkyviksi.** Esimerkiksi mitä sarakkeesta
   siirtyminen edellyttää ja miten kiireelliset työt käsitellään.
5. **Rakenna palautesilmukat.** Säännölliset tarkastelut työlle ja
   prosessille.
6. **Paranna yhdessä ja kokeillen.**

```{.dot otsikko="Kanban-taulu: sarakkeiden WIP-rajat suluissa, työ vedetään oikealta"}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.3;
  node [shape=record];
  j [label="jono|T-8\nT-9\nT-10"];
  a [label="analyysi (2)|T-7"];
  t [label="toteutus (3)|T-4\nT-5\nT-6"];
  k [label="katselmointi (2)|T-3"];
  v [label="valmis|T-1\nT-2"];
  j -> a -> t -> k -> v;
}
```

**Veto** (*pull*) on Kanbanin keskeinen mekanismi. Työtä ei työnnetä
seuraavaan vaiheeseen silloin, kun edellinen vaihe saa sen valmiiksi,
vaan seuraava vaihe vetää uuden työn, kun sillä on tilaa. Kuvan
taulussa toteutus on täynnä. Analyysistä vapautuva tekijä ei aloita
uutta analyysiä vaan katsoo, voiko auttaa oikealla: katselmoinnissa on
tilaa. WIP-raja tekee ruuhkan näkyväksi ja ohjaa ihmiset purkamaan
sitä. Luku 7 näyttää simuloimalla, miksi tämä lyhentää läpimenoaikaa.

Kanban ei tunne sprinttejä. Suunnittelu, julkaisu ja retrospektiivi
voivat kukin kulkea omassa rytmissään: jonoa täydennetään viikoittain,
julkaistaan aina kun jotain valmistuu ja työtapoja tarkastellaan
kuukausittain. Ennustaminen perustuu mitattuihin läpimenoaikoihin ja
läpäisyyn (luku 6) eikä sprintin sisältöön.

Töille voidaan määritellä **palveluluokkia**: esimerkiksi
tuotantohäiriö ohittaa jonon, päivämäärään sidottu työ aloitetaan
ajoissa ja tavalliset työt tehdään saapumisjärjestyksessä. Luokat
tekevät näkyväksi sen, mikä muuten tapahtuisi huutamalla.

Kanbanin heikkoudet ovat sen vahvuuksien kääntöpuolia. Koska mikään ei
pakota pysähtymään, katselmukset ja retrospektiivit jäävät helposti
pois. Koska nykytilaa ei muuteta, huono prosessi voi jäädä
visualisoiduksi huonoksi prosessiksi. Ja ilman sprintin tavoitetta työ
voi muuttua päättymättömäksi tikettivirraksi, josta suunta puuttuu.

## Vertailu

| Asia | Scrum | Kanban |
|----------------------|------------------------------------|------------------------------------|
| rytmi | kiinteän mittaiset sprintit | jatkuva virta |
| roolit | tuoteomistaja, Scrum master, kehittäjät | ei määrättyjä rooleja |
| työn rajoitus | sprintin sisältö | WIP-rajat sarakkeittain |
| muutos kesken jakson | vain jos sprintin tavoite ei vaarannu | milloin tahansa, kun tilaa on |
| mittarit | nopeus, tavoitteen toteutuminen | läpimenoaika, läpäisy, WIP |
| sopii erityisesti | tuotekehitykseen tavoite kerrallaan | ylläpitoon ja epätasaiseen työvirtaan |

Käytännössä tiimit yhdistelevät. Scrum-tiimi ottaa sprintin sisälle
WIP-rajat, ja Kanban-tiimi lainaa säännöllisen katselmuksen ja
retrospektiivin. Yhdistelmää kutsutaan toisinaan nimellä Scrumban.
Nimeä tärkeämpää on, että tiimi tietää, miksi kukin käytäntö on
olemassa.

Kun tiimejä on monta saman tuotteen ympärillä, tarvitaan lisäksi tapa
sovittaa niiden työ yhteen. Tähän on tarjolla skaalausmalleja (Scrum of
Scrums, LeSS, Nexus, SAFe), jotka eroavat toisistaan lähinnä siinä,
kuinka paljon rakennetta ne lisäävät. Niitä ja tiimirakenteiden
suunnittelua käsittelee taito *Tiimit ja organisaatiomallit*.

## Käytännössä

- **Aloita ongelmasta, älä menetelmästä.** Jos vaiva on, ettei
  tiedetä, mitä pitäisi tehdä seuraavaksi, tarvitaan tuoteomistajuutta.
  Jos vaiva on, että kaikki on kesken, tarvitaan WIP-rajoja. Menetelmän
  vaihtaminen ei korjaa kumpaakaan itsestään.
- **Sitoudu tavoitteeseen, älä listaan.** Sprintin tavoite kertoo,
  miksi sprintti tehdään. Listan viimeiset työt ovat joustovaraa.
- **Pidä valmiin määritelmä tiukkana.** Sekä Scrumissa että Kanbanissa
  mittarit ovat arvottomia, jos ”valmis” ei tarkoita julkaistavissa
  olevaa.
- **Älä vertaile tiimien nopeuksia.** Pisteiden skaala on tiimikohtainen.
  Vertailukelpoisia ovat läpimenoaika ja asiakkaan kokema hyöty.
- **Lyhennä sprinttiä, jos suunnitelmat eivät pidä.** Lyhyempi jakso
  pienentää erää ja tihentää palautetta. Kahden viikon sprintti on
  yleisin, mutta viikon sprintti on perusteltu, kun epävarmuus on
  suurta.
- **Suojaa retrospektiivi.** Se on ainoa tapahtuma, jonka aiheena on
  itse työtapa, ja ensimmäinen, joka kiireessä perutaan.
- **Laske WIP-raja tekijöistä.** Hyvä lähtöarvo on yksi työ henkeä
  kohden tai vähän alle, jolloin joku on aina vapaa auttamaan. Rajaa
  säädetään sen mukaan, mitä mittarit näyttävät (luku 7).

## Itsearviointi

- Osaat luetella Scrumin vastuut, tapahtumat ja tuotokset sekä kunkin
  tuotoksen sitoumuksen.
- Osaat selittää, miksi keskinopeuteen mitoitettu sprintti valmistuu
  kokonaan vain noin joka toisella kerralla.
- Osaat tunnistaa tavallisia tapoja käyttää Scrumia väärin.
- Osaat kuvata Kanbanin käytännöt ja selittää vedon ja WIP-rajan
  merkityksen.
- Osaat vertailla Scrumia ja Kanbania ja perustella, kumpi sopii
  annettuun tilanteeseen lähtökohdaksi.

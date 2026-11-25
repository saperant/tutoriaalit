# Superskalaarisuus ja epäjärjestys

Liukuhihna nostaa suorituskyvyn parhaimmillaan yhteen käskyyn jaksossa.
Sen jälkeen ainoa tie eteenpäin on suorittaa useampi käsky samassa
jaksossa: **superskalaarinen** ydin noutaa, purkaa ja suorittaa
2–8 käskyä jaksossa. Tämä toimii vain, jos ohjelmassa on riippumattomia
käskyjä, eli **käskytason rinnakkaisuutta** (ILP, *instruction-level
parallelism*). Tämä luku mittaa, paljonko sitä testiohjelmissa on ja
mitä laitteistoa sen hyödyntäminen vaatii.

## Järjestyksessä suorittava superskalaari

Yksinkertaisin leveä ydin on kahden tai neljän käskyn levyinen
liukuhihna, joka lähettää käskyt suoritukseen ohjelmajärjestyksessä
(*in-order*). Jos käsky odottaa operandiaan, kaikki sen takana odottavat
myös, vaikka ne olisivat riippumattomia. Leveys auttaa vain, kun
peräkkäiset käskyt ovat riippumattomia. ARM Cortex-A55 ja monet
sulautetut RISC-V-ytimet ovat tällaisia: ne ovat pieniä ja
energiatehokkaita.

## Epäjärjestyssuoritus

Epäjärjestyksessä suorittava (*out-of-order*, OoO) ydin noutaa ja purkaa
käskyt järjestyksessä, mutta lähettää ne suoritukseen heti, kun niiden
operandit ovat valmiit, ohjelmajärjestyksestä riippumatta. Tulokset
kuitenkin vahvistetaan (*commit*, *retire*) taas järjestyksessä, joten
ulospäin kaikki näyttää yhä järjestyksessä tapahtuvalta.

```{.dot otsikko="Epäjärjestyksessä suorittavan ytimen rakenne. Alku- ja loppupää etenevät ohjelmajärjestyksessä, keskiosa datan valmistumisen järjestyksessä. Katkoviiva: nimeäminen varaa käskylle paikan ROB:sta. Pisteviiva: väärä ennuste tyhjentää nuoremmat käskyt ja ohjaa noudon uudelleen"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.14;
  edge [fontsize=8];
  node [fontsize=9, margin="0.04,0.03", width=0.3, height=0.3];
  subgraph cluster_etu {
    label="järjestyksessä"; fontsize=8; style="rounded,dashed"; margin=6;
    N [label="nouto,\nennustin"]; P [label="purku"];
    R [label="nimeä-\nminen"];
  }
  subgraph cluster_ooo {
    label="epäjärjestyksessä"; fontsize=8; style="rounded,filled"; fillcolor="#f3e6c8"; margin=6;
    Q [label="liikkeelle-\nlähtöjono"];
    X [label="suoritus-\nyksiköt"];
    L [label="lataus- ja\ntalletusjonot"];
    {rank=same; X; L}
  }
  subgraph cluster_pois {
    label="järjestyksessä"; fontsize=8; style="rounded,dashed"; margin=6;
    ROB [label="ROB:\npoisto"];
  }
  N -> P -> R -> Q -> X -> ROB;
  R -> ROB [constraint=false, style=dashed];
  X -> Q [label="herätys", constraint=false];
  X -> L [dir=both];
  ROB -> N [constraint=false, style=dotted];
}
```

Rakenteet:

1. **Uudelleennimeäminen** (*register renaming*). Arkkitehtuurisia
   rekistereitä on 32, mutta fyysisiä satoja. Jokainen kirjoitus saa uuden
   fyysisen rekisterin, ja nimeämistaulu (RAT) kertoo, mikä fyysinen
   rekisteri vastaa kutakin arkkitehtuurista. Näin WAR- ja
   WAW-riippuvuudet katoavat: ne johtuivat vain siitä, että sama nimi
   käytettiin uudelleen.
2. **Liikkeellelähtöjono** (*issue queue*, Tomasulon algoritmissa
   *reservation station*). Käsky odottaa jonossa, kunnes sen
   lähdeoperandit on laskettu. Jono kuuntelee valmistuvien käskyjen
   tuloksia ja herättää odottajat.
3. **Uudelleenjärjestyspuskuri** (ROB, *reorder buffer*). Jokainen
   käsky saa paikan ohjelmajärjestyksessä. Käsky poistuu ROB:sta vasta,
   kun se ja kaikki sitä vanhemmat ovat valmiita. ROB:n koko on
   **ikkuna**: kuinka kaukaa tulevaisuudesta ydin voi etsiä
   riippumattomia käskyjä. Nykyisissä ytimissä se on 200–600 käskyä.
4. **Lataus- ja talletusjonot**. Lataus voi ohittaa aiemman talletuksen
   vain, jos osoitteet eivät ole samat. Osoite ei aina ole vielä
   tiedossa, joten ydin arvaa (*memory disambiguation*) ja tarkistaa
   arvauksen myöhemmin.

Väärin ennustettu haara ja poikkeus käsitellään ROB:n kautta: kun
virheellinen käsky on vanhin, kaikki sitä nuoremmat hylätään ja
nimeämistaulu palautetaan. Tarkat poikkeukset (luku 9) seuraavat
järjestyksessä tapahtuvasta poistosta.

Uudelleennimeämisen näkee parhaiten esimerkistä. Nimeäjä käy käskyt
läpi järjestyksessä, lukee lähteiden fyysiset rekisterit
nimeämistaulusta ja antaa jokaiselle kohteelle uuden:

```{.cpp tiedosto="esimerkit/11-nimeaminen.cpp" osa="nimeaminen"}
```

Esimerkki nimeää `summa`-ohjelman summaussilmukan kaksi kierrosta ja
laskee riippuvuudet ennen ja jälkeen:

```{.tuloste tiedosto="esimerkit/11-nimeaminen.odotettu"}
```

Arkkitehtuurisilla nimillä toinen kierros ei voi alkaa ennen kuin
ensimmäinen on lukenut `t2`:n ja `t1`:n, koska se kirjoittaa samoihin
rekistereihin: ikkunassa on 8 WAR- ja 6 WAW-riippuvuutta. Fyysisillä
nimillä jokainen rekisteri kirjoitetaan täsmälleen kerran, joten
jäljelle jäävät vain 11 aitoa RAW-riippuvuutta. Niistäkin kierrosten
välinen ketju on lyhyt: toisen kierroksen `slli` tarvitsee vain
`addi`:n tuloksen `p36`, joten kierrosten lataukset voivat olla
liikkeellä yhtä aikaa. Ainoa kierroksesta toiseen kulkeva pitkä ketju
on summa `a0` (`p10` → `p35` → `p40`).

Vanha fyysinen rekisteri vapautuu vasta, kun sen korvannut käsky on
poistunut ROB:sta: siihen asti poikkeus tai väärä ennuste voi vaatia
vanhan arvon takaisin.

Robert Tomasulo kehitti dynaamisen ajoituksen IBM System/360 Model 91:n
liukulukuyksikköön 1967. Laajaan käyttöön se tuli vasta 1990-luvulla
(Pentium Pro, MIPS R10000, Alpha 21264), kun transistoreita riitti ROB:n
ja suurten jonojen toteuttamiseen.

## Rajatutkimus

Kuinka paljon ILP:tä testiohjelmissa on? Esimerkki ajaa samat
käskyjäljet idealisoitujen ydinmallien läpi. Malli olettaa, että
muisti osuu aina (lataus 2 jaksoa, kertolasku 3, muut 1) ja ennustus on
täydellinen, ellei toisin mainita. Ainoat rajoitukset ovat leveys,
ikkuna ja datariippuvuudet:

```{.cpp tiedosto="esimerkit/11-ilp.cpp" osa="malli"}
```

Malli ajetaan viidelle ohjelmalle kahdeksalla ydinkokoonpanolla.
Leveys on käskyjä jaksossa, ikkuna uudelleenjärjestyspuskurin koko:

```{.tuloste tiedosto="esimerkit/11-ilp.odotettu"}
```

![IPC ydinkokoonpanon mukaan (sama data kuin taulukossa). Punaiset
merkit näyttävät, mihin neljän levyinen ydin 128 käskyn ikkunalla
putoaa ilman uudelleennimeämistä ja kaksibittisellä
ennustimella.](kuvat/ipc.png){width=80%}

Tulosten tulkinta:

- **Järjestyksessä leveys auttaa vähän.** Kaksi käskyä jaksossa nostaa
  IPC:n 0,9:stä noin 1,4:ään, mutta neljä ei juuri enempää. Peräkkäiset
  käskyt riippuvat toisistaan (`slli` → `add` → `lw` → `add`), joten
  leveä järjestyksessä toimiva ydin odottaa. `matriisi` hyötyy vähiten,
  koska kertolaskun kolmen jakson viive pysäyttää kaiken sen takana.
- **Ikkuna ratkaisee.** Neljän levyinen OoO-ydin 16 käskyn ikkunalla on
  jo 1,7–2,5-kertainen järjestyksessä toimivaan verrattuna, ja
  128 käskyn ikkunalla `matriisi` ja `fib` saavuttavat leveyden ylärajan
  4. Ikkuna löytää seuraavan silmukkakierroksen käskyt, jotka ovat
  riippumattomia nykyisestä.
- **Uudelleennimeäminen on välttämätön.** Ilman sitä 128 käskyn ikkuna
  menettää neljänneksestä kahteen viidennekseen IPC:stä ja `matriisi`
  kaksi kolmannesta: silmukka käyttää samoja
  rekistereitä joka kierroksella, ja WAR/WAW-riippuvuudet sitovat
  kierrokset toisiinsa.
- **Ennustus rajoittaa käytännössä.** Kun täydellinen ennustus vaihdetaan
  kaksibittiseen laskuriin, `kupla` putoaa 3,7:stä 1,9:ään ja `fib`
  4,0:sta 2,3:een. Jokainen virhe tyhjentää ikkunan. Leveä ydin on
  arvokas vain hyvän ennustimen kanssa.
- **Riippuvuusketju on yläraja.** `lista` jää muita alemmas, koska
  osoitinjahdin jokainen lataus odottaa edellistä. Edes kahdeksan
  levyinen ydin 512 käskyn ikkunalla ei pääse sen ketjun ohi.

David Wallin klassinen tutkimus (1991) päätyi samaan: realistisilla
ennustimilla ja ikkunoilla tyypillisten ohjelmien ILP on 5–7, ja
täydellisellä laitteistolla kymmeniä. Todellisten ytimien IPC on
kokonaislukuohjelmissa 1,5–3, koska välimuistihudit lisäävät latausten
viiveen satoihin jaksoihin.

## Hinta

Epäjärjestyssuoritus on kallista. Liikkeellelähtöjonon jokaisen
alkion on verrattava jokaisen jakson jokaista valmistuvaa tulosta
omiin lähteisiinsä, nimeämistaulua luetaan ja kirjoitetaan useaan
kertaan jaksossa, ja ROB, fyysinen rekisteritiedosto ja jonot vievät
pinta-alaa. Suuri OoO-ydin käyttää moninkertaisesti energiaa käskyä
kohden pieneen järjestyksessä toimivaan verrattuna. Siksi puhelimien
järjestelmäpiireissä on rinnakkain suuria ja pieniä ytimiä (ARM
big.LITTLE, Intelin P- ja E-ytimet).

Vaihtoehtoja on kokeiltu:

- **VLIW** (*very long instruction word*): kääntäjä ajoittaa käskyt
  valmiiksi rinnakkaisiin nippuihin, ja laitteisto suorittaa ne
  sellaisenaan. Intel Itanium (2001) epäonnistui, koska kääntäjä ei
  tiedä välimuistihutien viiveitä etukäteen. VLIW elää
  signaaliprosessoreissa, joissa viiveet ovat ennustettavia.
- **SMT** (*simultaneous multithreading*, Intelin Hyper-Threading):
  yksi ydin suorittaa kahden säikeen käskyjä yhtä aikaa ja täyttää
  toisen säikeen odottaessa tyhjiksi jääneet suorituspaikat. Hyvä
  muistia odottaville kuormille, huono, kun yksi säie jo täyttää ytimen.
- **Vektorikäskyt** (RISC-V V, x86 AVX, ARM SVE): yksi käsky käsittelee
  monta alkiota. Datarinnakkaisuus on halvempaa kuin käskyrinnakkaisuus,
  koska riippumattomuus on taattu käskyn tasolla.

## Spekulaation varjopuoli

Epäjärjestyksessä suorittava ydin suorittaa jatkuvasti käskyjä, joiden
tuloksia ei ehkä koskaan vahvisteta. Arkkitehtuurinen tila palautetaan,
mutta mikroarkkitehtuurinen jää: väärän polun lataus on tuonut lohkon
välimuistiin. **Spectre** (2018) käyttää tätä: hyökkääjä kouluttaa
ennustimen ohjaamaan uhrin taulukkoviitteen rajojen yli, ja
spekulatiivinen lataus lukee salaisuuden ja käyttää sitä toisen
taulukon indeksinä. Kun spekulaatio peruuntuu, salaisuus näkyy siitä,
mikä toisen taulukon lohko on välimuistissa (mitataan ajoituksella).
**Meltdown** käytti samaa tekniikkaa lukeakseen ytimen muistia, koska
Intelin ytimet tarkistivat oikeudet vasta poistovaiheessa.

Torjunnat ovat sekä laitteistossa (korjatut tarkistukset,
ennustimien eristys) että ohjelmistossa (ytimen ja käyttäjän sivutaulujen
erottaminen, `lfence`, taulukkoindeksien maskaus, *retpoline*). Ne
maksavat suorituskykyä, ja niiden yksityiskohdat käsitellään taidossa
*Sulautettujen järjestelmien tietoturva*.

## Käytännössä

- **Riippumattomat ketjut nopeutuvat.** Jaa summa usealle akulle,
  avaa silmukat ja vältä osoitinjahtia kuumassa silmukassa. Leveä ydin
  palkitsee koodin, jossa on monta itsenäistä laskentaketjua.
- **IPC kertoo pullonkaulasta.** `perf stat` näyttää IPC:n; Intelin
  *top-down*-menetelmä (`perf stat --topdown`, VTune) jakaa hukatut
  paikat neljään luokkaan: nouto- ja purkurajoitteiset, väärä
  spekulaatio, suoritusrajoitteiset ja muistirajoitteiset.
- **Ennustettavuus on leveyttä tärkeämpi.** Mittaukset näyttivät, että
  ennustusvirheet puolittavat leveän ytimen hyödyn. Haaraton koodi
  datasta riippuvissa kohdissa auttaa usein enemmän kuin mikään muu.
- **Älä luota ajoitukseen turvallisuudessa.** Salaisuuksia käsittelevän
  koodin (kryptografia) on oltava vakioaikaista: ei salaisuudesta
  riippuvia haaroja eikä muistiosoitteita.

## Itsearviointi

- Osaat selittää, miksi järjestyksessä toimivan ytimen leveys ei
  yksinään nosta IPC:tä.
- Osaat kuvata uudelleennimeämisen, liikkeellelähtöjonon ja ROB:n
  tehtävät ja sen, miten ne yhdessä säilyttävät tarkat poikkeukset.
- Osaat nimetä lyhyen käskyjonon uudelleen ja osoittaa, mitkä WAR- ja
  WAW-riippuvuudet katoavat ja mitkä RAW-riippuvuudet jäävät.
- Osaat tulkita ILP-rajatutkimuksen tuloksia: ikkunan, nimeämisen ja
  ennustuksen vaikutus.
- Osaat selittää, miten spekulatiivinen suoritus vuotaa tietoa
  välimuistin kautta.

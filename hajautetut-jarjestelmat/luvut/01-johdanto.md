# Johdanto {.runko-johdanto}

Hajautettu järjestelmä on joukko tietokoneita, jotka tekevät yhteistä
työtä viestejä vaihtamalla ja näyttävät käyttäjälle yhdeltä
järjestelmältä. Leslie Lamportin usein lainattu määritelmä on
osuvampi: hajautettu järjestelmä on sellainen, jossa kone, jonka
olemassaolosta et tiennyt, voi estää omaa konettasi toimimasta.

Hajauttamiseen on kolme syytä. *Vikasietoisuus*: yksi kone kaatuu
ennemmin tai myöhemmin, joten tieto ja palvelu kopioidaan usealle
koneelle. *Skaalautuvuus*: yksi kone ei jaksa kaikkea kuormaa tai
säilytä kaikkea dataa. *Läheisyys*: käyttäjät ovat eri puolilla
maailmaa, ja valon nopeus asettaa viiveelle alarajan. Kaikki kolme
johtavat samaan ongelmaan: koneiden pitää sopia asioista, vaikka
viestit viivästyvät, katoavat ja kulkevat ristiin, ja vaikka osa
koneista on kaatunut.

Tämä tutoriaali käsittelee hajautettujen järjestelmien periaatteita:
mitä vikoja voi tapahtua, mitä aika tarkoittaa ilman yhteistä kelloa,
miten tieto replikoidaan, mitä konsistenssi tarkoittaa, miten koneet
pääsevät yksimielisyyteen (konsensus) ja miten usean koneen
transaktiot tehdään. Jokainen asia toteutetaan C++-ohjelmana, joka
ajetaan deterministisessä verkkosimulaattorissa.

## Miksi simulaattori

Hajautetun ohjelman virheet syntyvät harvinaisista tapahtumajärjestyksistä:
viesti saapuu juuri ennen aikakatkaisua, verkko jakautuu kahtia
kesken vaalin, solmu kaatuu levylle kirjoittamisen ja vastauksen
välissä. Oikeassa verkossa tällaista tilannetta ei saa toistettua, ja
virheestä jää käteen vain loki, jossa kellot ovat eri ajassa.

Deterministinen simulaattori kääntää asetelman. Kaikki solmut ajetaan
yhdessä prosessissa ja yhdessä säikeessä. Viestit, ajastimet ja viat
ovat tapahtumia simuloidussa ajassa, ja jokainen satunnainen päätös
(viive, katoaminen, monistuminen, kellon ajautuminen) tehdään
siemenestä. Sama siemen tuottaa aina saman suorituksen, joten
virheen löytänyt siemen on täydellinen toistettava testitapaus.
Koska aika on simuloitua, tuhannen sekunnin vikaskenaario ajetaan
millisekunneissa, ja testi voi kokeilla tuhansia siemeniä.

Menetelmä ei ole pelkkä opetustyökalu. FoundationDB-tietokanta
rakennettiin alusta asti deterministisen simuloinnin varaan, ja sen
kehittäjien mukaan suurin osa virheistä löytyi simulaattorista eikä
tuotannosta. TigerBeetle ja monet muut tietokannat ovat seuranneet
perässä. Toinen tunnettu lähestymistapa, Jepsen, testaa oikeita
järjestelmiä oikeassa verkossa vikoja aiheuttamalla ja tarkistaa
historiat linearisoituvuuden kaltaisia malleja vastaan. Luvussa
*Konsistenssimallit* tehdään pieni versio Jepsenin tarkistimesta.

## Esitiedot ja rajaukset

Tutoriaali olettaa taidot *Verkko-ohjelmointi*, *Rinnakkaisohjelmointi*
ja *Algoritmit*. Verkko-ohjelmoinnista tarvitaan käsitys soketeista,
etäkutsuista, aikakatkaisuista, uudelleenyrityksistä ja
idempotenssista; tässä samoja asioita tarkastellaan koko järjestelmän
tasolla. Rinnakkaisohjelmoinnin muistimallit ja lukot ovat hyvä
vertailukohta, mutta hajautetussa järjestelmässä ei ole jaettua
muistia eikä yhteistä kelloa: kaikki tieto toisista solmuista on
viestien tuomaa ja siksi vanhaa.

Arkkitehtuuritason asiat, kuten mikropalvelut, viestinvälittäjät ja
SAGA-malli, käsitellään taidossa *Palveluarkkitehtuurit*, ja
tietokantatransaktiot eristystasoineen taidossa *SQL*. Kapasiteetin
mitoitus, välimuistit ja kuormantasaus kuuluvat jatkotaitoon
*Skaalautuvien järjestelmien suunnittelu*.

## Tutoriaalin rakenne

Luvut 2–11 etenevät perusteista konsensukseen ja testaukseen:

2. *Vikamallit ja simulaattori*: mitä voi mennä vikaan, synkroninen ja
   asynkroninen järjestelmä, vikailmaisin ja simulaattorin rakenne.
3. *Aika ja järjestys*: fyysiset kellot, Lamportin kellot,
   vektorikellot ja hybridikellot.
4. *Replikointi*: johtaja ja seuraajat, synkroninen ja asynkroninen
   replikointi sekä johtajaton replikointi kvoorumeilla.
5. *CRDT:t*: tietorakenteet, jotka yhdistyvät ilman koordinointia.
6. *Konsistenssimallit*: linearisoituvuus ja sen tarkistin, istunto-
   takuut ja niiden rikkeet.
7. *Raft: johtajavaali*: termit, äänestys ja satunnaistetut
   aikarajat.
8. *Raft: loki ja turvallisuus*: replikointi, sitoutuminen ja
   turvallisuusominaisuuksien testaus vikojen alla.
9. *CAP ja PACELC*: mitä jakautunut verkko pakottaa valitsemaan.
10. *Hajautetut transaktiot*: kaksivaiheinen sitoutuminen, sen estotila
    ja idempotenssi.
11. *Simulointitestaus*: siemenhaku, vian pienentäminen ja testauksen
    rajat.

## Esimerkit ja testaus

Esimerkit ovat C++23:a ilman ulkoisia kirjastoja. Simulaattori ja
yhteiset osat ovat hakemistossa `esimerkit/yhteinen/`:

| Tiedosto | Sisältö |
|----------|---------|
| `satunnainen.hpp` | toistettava PCG32-generaattori |
| `simulaattori.hpp` | solmujen rajapinta ja tapahtumasimulaattori |
| `kellot.hpp` | Lamportin kello, vektorikello, hybridikello |
| `crdt.hpp` | kasvava ja kaksisuuntainen laskuri, OR-joukko |
| `historia.hpp` | linearisoituvuuden tarkistin |
| `raft.hpp` | Raft-solmu, asiakas ja turvallisuustarkistukset |
| `viat.hpp` | satunnaiset vikaohjelmat |
| `raftkoe.hpp` | Raft-klusterin simulointitesti |

Testeissä jokainen esimerkki käännetään GCC 14:llä ja Clang 20:llä
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, ja kummankin
tulosteen on oltava täsmälleen sama kuin tiedostossa
`<nimi>.odotettu`. Tämä on vaativampi ehto kuin pelkkä
toistettavuus samalla kääntäjällä: simulaattori ei saa riippua mistään,
minkä kääntäjä tai standardikirjasto saa valita.

- **Oma satunnaislukugeneraattori.** Standardikirjaston jakaumien
  algoritmeja ei ole määrätty, joten esimerkit käyttävät PCG32:ta ja
  omaa välin muunnosta.
- **Yksi satunnaisluku lauseessa.** Funktion argumenttien
  laskentajärjestystä ei ole määrätty: `f(g(), g())` voi kutsua
  ensin kumpaa tahansa, ja GCC ja Clang todella tekevät sen eri
  järjestyksessä.
- **Järjestetyt säiliöt.** `std::unordered_map`in läpikäyntijärjestys
  riippuu toteutuksesta, joten simulaattori ja algoritmit käyttävät
  `std::map`ia, `std::set`iä ja vektoreita.
- **Kokonaislukuaika.** Simuloitu aika on millisekunteina
  kokonaislukuna, ja todennäköisyydet ovat promilleja.

## Työkalut

```text
make testaa   # rakenne ja esimerkit kahdella kääntäjällä
make pdf      # tämä dokumentti ja pikaopas
```

Kehityskontissa (`.devcontainer/hajautetut-jarjestelmat`) ovat GCC,
Clang, Pandoc ja TeX. Yksittäisen esimerkin voi kääntää ja ajaa
suoraan esimerkkihakemistossa:

```text
g++ -std=c++23 -O2 08-replikointi.cpp -o replikointi && ./replikointi
```

Optimoituna simulointitestit ovat kymmeniä kertoja nopeampia kuin
sanitoijien kanssa, joten omia kokeiluja kannattaa ajaa näin ja
siemeniä voi kokeilla tuhansia.

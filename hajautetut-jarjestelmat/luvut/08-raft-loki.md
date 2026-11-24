# Raft: loki ja turvallisuus

Johtaja on Raftissa lokin ainoa kirjoittaja. Asiakkaan komento lisätään
johtajan lokiin, johtaja replikoi sen seuraajille, ja kun enemmistö on
tallentanut merkinnän, se on *sitoutettu* (*committed*): se ei enää
katoa, ja sen saa soveltaa tilakoneeseen. Tämä luku käy läpi
replikoinnin, sitoutumisen säännön ja turvallisuusominaisuudet ja
testaa toteutuksen sadalla satunnaisella vikaohjelmalla.

## Lokin replikointi

Johtaja pitää jokaiselle seuraajalle kirjaa kahdesta indeksistä:
`seuraava` on seuraavaksi lähetettävä merkintä ja `vastaava` suurin
indeksi, jonka seuraaja on vahvistanut. Lisäysviesti (*AppendEntries*)
kertoo uusien merkintöjen lisäksi edeltävän merkinnän indeksin ja
termin. Seuraaja hyväksyy viestin vain, jos sen lokissa on samassa
kohdassa saman termin merkintä. Muuten se vastaa kieltävästi, ja johtaja
siirtyy taaksepäin, kunnes lokit kohtaavat. Hyväksytyn kohdan jälkeiset
ristiriitaiset merkinnät seuraaja katkaisee ja korvaa johtajan
merkinnöillä:

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="replikointi"}
```

Tarkistuksesta seuraa induktiolla *lokien yhtäpitävyys* (*Log
Matching*): jos kahdessa lokissa on samassa indeksissä saman termin
merkintä, lokit ovat samat siihen asti. Johtaja luo termillään vain yhden
merkinnän kuhunkin indeksiin, ja jokainen hyväksytty lisäys varmistaa,
että edeltävä kohta täsmää.

Tyhjä syke on sama viesti ilman merkintöjä. Se pitää seuraajat
seuraajina ja kuljettaa tiedon sitoutetusta kohdasta, joten seuraajat
voivat soveltaa merkinnät tilakoneeseensa.

## Sitoutuminen

Johtaja sitouttaa suurimman indeksin, joka on enemmistön lokissa ja
jonka merkintä on johtajan *nykyiseltä termiltä*. Jälkimmäinen ehto on
Raftin hienovaraisin kohta. Edellisen termin merkintä voi olla
enemmistöllä ja silti kadota: jos se ei ole uusimman termin merkintä,
toinen ehdokas, jolla on uudempi termi lokin lopussa, voi voittaa vaalin
ja korvata sen (Raft-artikkelin kuva 8). Kun johtaja sitouttaa oman
termin merkinnän, kaikki sitä edeltävät tulevat sitoutetuiksi
samalla.

Tästä syystä uusi johtaja lisää termin alussa tyhjän merkinnän. Ilman
sitä edellisten termien merkinnät jäisivät odottamaan, kunnes joku
asiakas lähettää komennon, ja siihen asti johtaja ei voisi vastata
luotettavasti edes lukuihin.

Sovellettu merkintä välitetään tilakoneeseen ja, jos johtaja odotti
sitä, asiakkaalle vastauksena:

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="tilakone"}
```

Asiakas (`RaftAsiakas`) ei tiedä, kuka on johtaja. Se lähettää komennon
jollekin palvelimelle, joka kertoo tuntemansa johtajan, ja
aikakatkaisun jälkeen kokeilee satunnaista palvelinta.

Asiakas voi lähettää saman komennon uudelleen, jolloin se päätyy
lokiin kahdesti. Oikea järjestelmä estää tämän tilakoneessa
asiakaskohtaisella sarjanumerolla, saman idempotenssin avulla kuin
luvussa *Hajautetut transaktiot*.

## Turvallisuusominaisuudet

Raft-artikkeli todistaa viisi ominaisuutta:

| Ominaisuus | Väite |
|------------|-------|
| vaaliturvallisuus | termillä on enintään yksi johtaja |
| vain lisäys | johtaja ei poista eikä korvaa omia merkintöjään |
| lokien yhtäpitävyys | sama indeksi ja termi tarkoittaa samaa lokia siihen asti |
| johtajan täydellisyys | sitoutettu merkintä on jokaisen myöhemmän termin johtajan lokissa |
| tilakoneen turvallisuus | kaikki solmut soveltavat samaan indeksiin saman merkinnän |

Johtajan täydellisyys on se, jota vaalin lokiehto suojaa. Sitoutettu
merkintä on enemmistöllä, ja ehdokas tarvitsee äänet enemmistöltä, joten
ainakin yksi äänestäjä on tallentanut merkinnän. Äänestäjä ei anna
ääntä ehdokkaalle, jonka loki on vanhempi kuin oma, joten voittajan
lokissa on merkintä.

Testissä ominaisuudet tarkistetaan suoraan. Tarkkailija näkee jokaisen
johtajan ja jokaisen sovelletun merkinnän:

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="tarkkailija"}
```

Lokien yhtäpitävyys ja johtajan täydellisyys tarkistetaan 10 ms välein
kaikista elossa olevista solmuista. Johtajan täydellisyys koskee vain
johtajia, joiden termi on suurempi kuin sitoutuksen termi, koska
verkosta erillään oleva vanha johtaja voi oikeutetusti olla jäljessä:

```{.cpp tiedosto="esimerkit/yhteinen/raft.hpp" osa="lokien-tarkistus"}
```

## Satunnaiset vikaohjelmat

Vikaohjelma on lista kaatumisia ja verkon jakoja, jotka arvotaan
siemenestä. Kullakin vialla on alku ja kesto:

```{.cpp tiedosto="esimerkit/yhteinen/viat.hpp" osa="asenna"}
```

Koe ajaa viiden palvelimen ja kahden asiakkaan klusteria verkossa, joka
kadottaa ja monistaa 2 % viesteistä:

```{.cpp tiedosto="esimerkit/yhteinen/raftkoe.hpp" osa="koe"}
```

```{.cpp tiedosto="esimerkit/08-replikointi.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/08-replikointi.odotettu"}
```

Sadassa ajossa, joissa jokaisessa oli kahdeksan vikaa, yhtäkään
turvallisuusominaisuutta ei rikottu. Viat näkyvät etenemisessä: vikojen
kanssa asiakkaat saivat vahvistettua keskimäärin kaksi kolmasosaa
siitä, mitä ilman vikoja, koska vaalien ja jakojen aikana komennot
odottavat.

## Virhe, jonka testi löytää

Hyvä testi löytää virheen, kun sellainen on. Seuraava esimerkki ajaa
saman testin toteutukselle, josta vaalin lokiehto on poistettu
makrolla `RAFT_BUGI_AANESTYS`:

```{.cpp tiedosto="esimerkit/08-bugi.cpp" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/08-bugi.odotettu"}
```

Virhe paljastui jo ensimmäisellä siemenellä ja 81 ajossa sadasta. Solmu,
jolta puuttui sitoutettu merkintä, voitti vaalin, ja johtajan
täydellisyys rikkoutui. Siemen ja sen vikaohjelma ovat valmis
toistettava testitapaus. Luku *Simulointitestaus* pienentää
vikaohjelman niin, että virheen syy näkyy suoraan jäljestä.

## Mitä Raftista jäi pois

Toteutus kattaa Raftin ytimen. Tuotannossa tarvitaan lisäksi:

- **Tilannevedokset ja lokin tiivistys.** Loki kasvaa rajatta, joten
  tilakoneen tila tallennetaan ajoittain ja vanhat merkinnät poistetaan.
  Kauas jäänyt seuraaja saa tilannevedoksen lokin sijaan.
- **Kokoonpanon muutokset.** Solmujen lisääminen ja poistaminen ilman,
  että vanha ja uusi enemmistö voivat valita eri johtajat (yhteinen
  konsensus tai muutos solmu kerrallaan).
- **Linearisoituvat luvut.** Johtaja ei voi vastata lukuun omasta
  tilastaan, koska se voi olla vanhentunut johtaja erillään verkosta.
  Se joko varmistaa johtajuutensa sykkeellä enemmistöltä ennen
  vastausta (*ReadIndex*) tai käyttää aikaan perustuvaa vuokraa
  (*lease*), joka olettaa kellojen ajautuman rajatuksi.
- **Suorituskyky.** Merkintöjen niputtaminen, liukuhihnoitetut
  lisäykset ja levyn ryhmäkirjoitus.

Paxos ratkaisee saman ongelman. Perus-Paxos sopii yhdestä arvosta
kaksivaiheisella protokollalla (valmistelu ja hyväksyntä), ja Multi-Paxos
toistaa sen lokin jokaiselle kohdalle vakaan johtajan kanssa, jolloin
se muistuttaa Raftia. Erot ovat lähinnä johtajan valinnassa ja siinä,
saako lokiin jäädä aukkoja. Zab (ZooKeeper) ja Viewstamped Replication
ovat samaa sukua.

## Käytännössä

- **Sitouta vain oman termin merkintöjä.** Tämä on Raftin yleisin
  toteutusvirhe. Tyhjä merkintä termin alussa tekee säännöstä
  käytännössä huomaamattoman.
- **Testaa turvallisuus jatkuvasti.** Tarkista ominaisuudet jokaisen
  tapahtuman tai lyhyen välin jälkeen, ei vain ajon lopussa: väliaikainen
  rike voi korjautua näkymättömiin ennen loppua.
- **Erota turvallisuus ja eteneminen myös testeissä.** Turvallisuusrike
  on aina virhe. Hidas eteneminen vikojen aikana on odotettua, mutta
  ajon lopussa, kun viat ovat ohi, klusterin pitää taas edetä.
- **Tallenna kaatuneen testin siemen.** Siemen ja vikaohjelma ovat koko
  testitapaus. Lisää ne regressiotesteihin.
- **Älä lue johtajalta ilman varmistusta.** Linearisoituva luku vaatii
  ReadIndexin tai vuokran.

## Itsearviointi

- Osaat kuvata lisäysviestin johdonmukaisuustarkistuksen ja sen, miten
  johtaja korjaa jäljessä olevan tai ristiriitaisen seuraajan lokin.
- Osaat selittää sitoutumisen säännön ja sen, miksi edellisen termin
  merkintää ei saa sitouttaa pelkän enemmistön perusteella.
- Osaat luetella Raftin viisi turvallisuusominaisuutta ja perustella
  johtajan täydellisyyden vaalin lokiehdolla.
- Osaat kirjoittaa tarkistimen turvallisuusominaisuuksille ja ajaa
  Raftia satunnaisten vikaohjelmien alla.
- Osaat kertoa, mitä tuotantokelpoinen Raft tarvitsee ytimen lisäksi.

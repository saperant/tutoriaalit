# CAP ja PACELC

Edellisissä luvuissa järjestelmät joutuivat valitsemaan kahdesta
huonosta: synkroninen replikointi pysähtyi seuraajan kaaduttua, Raftin
vähemmistö ei voinut tehdä mitään, ja asynkroninen replikointi hukkasi
kirjoituksia. Valinta ei johdu huonoista algoritmeista. CAP-lause
osoittaa, että se on väistämätön, ja PACELC laajentaa saman ajatuksen
tilanteeseen, jossa verkko toimii.

## CAP-lause

Eric Brewerin konjektuurin (2000) todistivat Gilbert ja Lynch (2002).
Täsmällisessä muodossaan se koskee kolmea ominaisuutta:

- **Konsistenssi** (*C*): linearisoituvuus, ks. luku 6.
- **Saatavuus** (*A*): jokainen pyyntö toimivalle solmulle saa
  lopulta vastauksen, joka ei ole virhe.
- **Jakautumisen sieto** (*P*): järjestelmä toimii, vaikka verkko
  kadottaa mielivaltaisesti viestejä solmujen välillä.

Lause sanoo, ettei järjestelmä voi taata kaikkia kolmea. Todistus on
lyhyt: jaa verkko kahtia, kirjoita toiselle puolelle ja lue toiselta.
Jos luku vastaa, se ei voi tietää kirjoituksesta, joten linearisoituvuus
rikkoutuu. Jos luku ei vastaa, saatavuus rikkoutuu.

Lause luetaan usein väärin "valitse kaksi kolmesta". Verkon jakautuminen
ei ole valinta, se tapahtuu. Valinta tehdään vain jakautumisen aikana:
joko osa pyynnöistä hylätään (*CP*), tai kaikki saavat vastauksen ja
konsistenssista tingitään (*AP*). Kun verkko toimii, järjestelmä voi
tarjota molemmat. Määritelmät ovat lisäksi tiukkoja: CAP:n saatavuus
vaatii vastauksen *jokaiselta* toimivalta solmulta, joten Raft-klusteri,
jonka enemmistö toimii, on CAP:n mielessä saavuttamaton, vaikka
käyttäjä ei huomaisi katkosta lainkaan.

## Koe

Kokeessa on kolme replikaa ja kaksi asiakasta kahdessa konesalissa:
{r0, r1, A} ja {r2, B}. Konesalien välillä viesti viipyy 40 ms
pidempään. Hetkellä 1000 verkko jakautuu konesalien välillä
sekunniksi. Asiakkaat lisäävät joukkoon alkioita. CP-tilassa lisäys
vaatii kahden replikan kuittauksen, AP-tilassa paikallinen replika
kuittaa heti ja levittää tilansa 50 ms välein, joko korvaamalla koko
arvon (LWW) tai yhdistämällä (CRDT, ks. luku 5):

```{.dot otsikko="Kokeen kokoonpano. Katkoviivalla piirretyt konesalien väliset yhteydet katkeavat sekunniksi."}
graph {
  rankdir=LR; nodesep=0.35; ranksep=1.1;
  subgraph cluster_1 {
    label="konesali 1 (enemmistö)"; fontsize=9; color="#B8C4C8";
    A [label="asiakas A", shape=ellipse]; r0; r1;
    A -- r0; r0 -- r1;
  }
  subgraph cluster_2 {
    label="konesali 2 (vähemmistö)"; fontsize=9; color="#B8C4C8";
    r2; B [label="asiakas B", shape=ellipse];
    r2 -- B;
  }
  r0 -- r2 [style=dashed, label="+40 ms"];
  r1 -- r2 [style=dashed];
}
```

```{.cpp tiedosto="esimerkit/09-cap.cpp" osa="replika"}
```

Asiakas lisää uuden alkion, odottaa vastausta ja jatkaa 20 ms:n
päästä. Pyyntö epäonnistuu, jos kuittauksia ei ole tullut 300 ms:ssa.

```{.cpp tiedosto="esimerkit/09-cap.cpp" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/09-cap.odotettu"}
```

CP-tilassa enemmistön puolen asiakas A jatkoi normaalisti, ja
vähemmistön asiakas B ei saanut yhtään lisäystä läpi: sen kolme yritystä
odottivat aikarajaan asti. Kuitattuja lisäyksiä ei kadonnut. AP-tilassa
kumpikin puoli jatkoi, mutta LWW-replikointi hukkasi 73 kuitattua
lisäystä: kun verkko palasi, toisen puolen joukko korvasi toisen. CRDT-
joukko yhdisti puolet, eikä mitään kadonnut. AP ei siis välttämättä
tarkoita hukkaa, mutta se tarkoittaa, että tietotyypin on kestettävä
samanaikaiset muutokset.

## PACELC

Daniel Abadi (2012) huomautti, että CAP käsittelee vain poikkeustilaa.
PACELC laajentaa sen: jos verkko jakautuu (*P*), valitaan saatavuuden
(*A*) ja konsistenssin (*C*) välillä; muuten (*E*, *else*) valitaan
viiveen (*L*, *latency*) ja konsistenssin (*C*) välillä. Konsistenssi
maksaa aina, koska se vaatii koordinointia, ja koordinointi vaatii
viestejä etäisille replikoille.

Kokeen viivesarakkeet näyttävät tämän ilman jakoa. CP-tilassa asiakas B
odotti keskimäärin 96 ms, koska enemmistö on toisessa konesalissa. A
odotti 22 ms, koska sen konesalissa on kaksi replikaa. AP-tilassa kumpikin
sai vastauksen paikalliselta replikalta noin 20 ms:ssa. Kolmen
konesalin Raft-klusterissa jokainen kirjoitus maksaa vähintään
lähimmän toisen konesalin kiertoajan.

| Järjestelmä | Jakautuessa | Muuten | Huomio |
|-----------------------|-------------|---------|-------------------------------|
| etcd, ZooKeeper, Consul | C | C | konsensus jokaiselle kirjoitukselle |
| Spanner, CockroachDB | C | C | tiukka sarjallistuvuus, viive konesalien välillä |
| Cassandra, Riak, Dynamo | A | L | säädettävä R ja W, oletuksena heikko |
| PNUTS (Yahoo) | C | L | johtaja tietuekohtaisesti, luvut paikallisilta replikoilta |
| DynamoDB | A | L | vahvasti konsistentti luku valinnaisena |

Luokittelu on karkea, koska useimmissa järjestelmissä valinnan voi
tehdä operaatiokohtaisesti: Cassandran `QUORUM`-luku, MongoDB:n
`readConcern` ja DynamoDB:n `ConsistentRead` siirtävät operaation
taulukossa toiseen sarakkeeseen.

## Käytännössä

- **Valitse jokaiselle tiedolle oma malli.** Tilaukset ja maksut
  tarvitsevat konsistenssin, tuotekatalogi ja suositukset kestävät
  vanhaa tietoa. Sama järjestelmä voi tarjota molempia.
- **Suunnittele vähemmistön käytös.** CP-järjestelmän vähemmistö
  hylkää pyynnöt. Kerro käyttäjälle selvä virhe ja ohjaa liikenne
  enemmistön puolelle, älä jätä pyyntöjä roikkumaan.
- **AP vaatii yhdistettävät tietotyypit.** Jos valitset saatavuuden,
  valitse myös ristiriitojen ratkaisu: CRDT, sisarukset tai
  sovelluslogiikka. LWW on harvoin oikea valinta.
- **Viive on jokapäiväinen hinta.** Jakautuminen on harvinaista, mutta
  konsistenssin viive maksetaan jokaisessa operaatiossa. Sijoita
  enemmistö lähelle kirjoittajia.
- **Älä luota luokitteluun, testaa.** Konfiguraatio, oletusasetukset ja
  versiot muuttavat järjestelmän käytöstä. Jepsen-tyyppinen testi
  kertoo, mitä järjestelmä oikeasti tekee.

## Itsearviointi

- Osaat määritellä CAP-lauseen kolme ominaisuutta täsmällisesti ja
  esittää lauseen todistuksen idean.
- Osaat selittää, miksi "valitse kaksi kolmesta" on harhaanjohtava
  muotoilu.
- Osaat kuvata PACELC-mallin ja sen, miksi konsistenssi maksaa viivettä
  myös ilman vikoja.
- Osaat näyttää simulaattorissa CP- ja AP-järjestelmän käytöksen
  jakautuneessa verkossa ja mitata saatavuuden ja hukatut kirjoitukset.
- Osaat sijoittaa tavallisia tietokantoja CAP- ja PACELC-luokkiin ja
  kertoa, milloin luokittelu ei päde.

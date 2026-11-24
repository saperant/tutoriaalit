# Johdanto {.runko-johdanto}

*NoSQL* on yhteisnimi tietokannoille, joiden tietomalli ei ole
relaatiotaulu: avain-arvo-, dokumentti-, leveäsarake-, graafi- ja
aikasarjatietokannoille. Nimi on huono, sillä useimmissa niistä on
nykyään SQL:ää muistuttava kyselykieli, ja relaatiotietokannat ovat
oppineet tallentamaan dokumentteja. Yhteistä on lähinnä se, että
kukin on tehty yhdenlaista käyttöä varten ja tekee sen paremmin kuin
yleiskäyttöinen relaatiotietokanta – ja muun huonommin.

Tämä tutoriaali ei myy NoSQL:ää. Relaatiotietokanta on oikea
oletusvalinta lähes jokaiseen sovellukseen, ja suurin osa
NoSQL-projektien ongelmista syntyy siitä, että valinta tehtiin muodin
eikä kuorman perusteella. Tavoite on, että tunnet kunkin perheen
tietomallin, vahvuudet ja hinnan niin hyvin, että osaat perustella,
milloin se kannattaa – ja milloin PostgreSQL riittää.

Jokaista tietokantaa käytetään oikeana palvelimena: esimerkit
käynnistävät Redisin, MongoDB:n, Cassandran, Neo4j:n ja PostgreSQLin
Docker-konteissa ja puhuvat niille samoilla Python-asiakkailla, joita
tuotannossakin käytetään. Lisäksi luvussa 8 rakennetaan oma pieni
LSM-puu, joka on Cassandran ja monen muun tietokannan tallennuskerros.

## Esimerkkien ympäristö

Esimerkit ovat hakemistossa `esimerkit/`. Tietokannat käynnistää
[Testcontainers](https://testcontainers.com)-kirjasto, joka luo
kertakäyttöisen kontin, odottaa palvelun valmistumista, kertoo
satunnaisen portin ja pysäyttää kontin lopuksi. Testcontainersin
käyttö integraatiotesteissä on oman taitonsa *Integraatiotestaus ja
Testcontainers* aihe; tässä se on vain keino saada oikea tietokanta
käyttöön yhdellä rivillä.

Kuvien versiot on lukittu, jotta esimerkit tuottavat joka kerta saman
tuloksen:

```{.python tiedosto="esimerkit/nosql/kontit.py" osa="kuvat"}
```

Kuvat haetaan Docker Hubin virallisten kuvien peilistä
`mirror.gcr.io`, koska Docker Hub rajoittaa nimettömiä latauksia.
Tietokanta käynnistyy vasta, kun esimerkki pyytää sitä, ja asiakas
odottaa, että palvelin vastaa:

```{.python tiedosto="esimerkit/nosql/kontit.py" osa="redis"}
```

Yksittäisen esimerkin voi ajaa suoraan, jolloin se käynnistää omat
konttinsa:

```
cd esimerkit
python3 luku03/rakenteet.py
```

Docker-palvelun on oltava käynnissä. Kehityskontissa
(`.devcontainer/nosql`) kontit käynnistetään isäntäkoneen Dockerilla.

## Mitä on testattu

`make testaa` ajaa jokaisen esimerkin ja vertaa sen tulosteen
tiedostoon `.odotettu`. Ajo on pytest-testi, jossa kaikki esimerkit
jakavat saman ympäristön, joten esimerkiksi Cassandra käynnistyy vain
kerran:

```{.python tiedosto="esimerkit/testit/test_esimerkit.py"}
```

Tulosteisiin ei pääse mitään, mikä vaihtelee ajosta toiseen:
tunnisteet, ajat, portit ja palvelinten versiot jätetään pois, ja
jokaisessa kyselyssä on järjestys. Tämä on hyvä tapa myös omissa
testeissä: jos testi riippuu järjestyksestä, jota tietokanta ei lupaa,
se hajoaa aikanaan.

Lisäksi `make testaa` ajaa ruffin ja `mypy --strict`-tarkistuksen sekä
oman LSM-puun satunnaistestin.

## Verkkokauppa

Esimerkit kuvaavat samaa pientä retkeilytarvikekauppaa, jotta
tietomallien erot näkyvät:

```{.python tiedosto="esimerkit/nosql/data.py" osa="tilaukset"}
```

Tilauksessa on asiakas ja rivit. Relaatiomallissa rivit ovat omassa
taulussaan, dokumenttimallissa tilauksen sisällä, Cassandrassa ne
monistetaan jokaisen kyselyn tarpeisiin, ja graafissa kiinnostavaa ovat
yhteydet: kuka osti mitä ja kuka seuraa ketä.

## Lisenssit

Tietokantojen lisenssit ovat muuttuneet viime vuosina, ja ne vaikuttavat
siihen, miten tietokantaa saa käyttää ja tarjota palveluna.

| Tietokanta | Lisenssi | Merkitys käyttäjälle |
|-------------|-----------------|------------------------------|
| PostgreSQL | PostgreSQL License (MIT-tyyppinen) | vapaa käyttää ja muuttaa |
| Redis 7.2 | BSD-3 | avoin; viimeinen BSD-versio, jota esimerkit käyttävät |
| Redis 7.4 | RSALv2 tai SSPLv1 | lähdekoodi saatavilla, mutta ei avoin lisenssi; palveluna tarjoaminen rajoitettu |
| Redis 8 | lisäksi AGPLv3 | avoin lisenssi palasi vaihtoehdoksi |
| Valkey | BSD-3 | Linux Foundationin avoin haara Redis 7.2:sta |
| MongoDB | SSPLv1 | sisäinen käyttö vapaata; palveluna tarjoaminen vaatii koko palvelun lähdekoodin julkaisemisen |
| Cassandra | Apache 2.0 | avoin |
| Neo4j Community | GPLv3 | avoin; klusterointi vain kaupallisessa versiossa |

Opetuskäyttöön ja oman sovelluksen tietokannaksi kaikki sopivat. Jos
aiot tarjota tietokantaa palveluna muille, lue lisenssi tarkasti.
SSPL:ää ja RSAL:ia ei pidetä avoimina lisensseinä, ja juuri siksi
syntyivät Valkey ja OpenSearch, joita ylläpitävät säätiöt.

## Esitiedot ja rajaus

Esitietoina oletetaan taidot *SQL ja relaatiotietokannat* (normalisointi,
transaktiot, indeksit) ja *Kontit ja pilvi* (Docker). Replikoinnin ja
konsistenssin teoria – kvoorumit, CAP ja PACELC, CRDT:t – on taidossa
*Hajautetut järjestelmät*; tässä ne näytetään oikeilla tietokannoilla.
Redis välimuistina ja osioinnin suunnittelu ovat taidossa
*Skaalautuvien järjestelmien suunnittelu*.

Pois jäävät tietokantojen ylläpito tuotannossa (varmuuskopiot,
klusterin laajentaminen, valvonta) ja pilvipalvelujen omat tietokannat
kuten DynamoDB ja Firestore. Niiden tietomallit ovat kuitenkin samoja
kuin tässä käsiteltävien: DynamoDB on Cassandran sukulainen ja
Firestore dokumenttitietokanta.

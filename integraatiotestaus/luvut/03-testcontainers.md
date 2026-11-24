# Testcontainers

Testcontainers on kirjastoperhe, joka käynnistää Docker-kontteja
testikoodista. Alkuperäinen toteutus on Javalle, ja samaa mallia
seuraavat toteutukset Go:lle, .NETille, Node.js:lle, Rustille ja
Pythonille. Tutoriaali käyttää Python-versiota `testcontainers` 4.15.0;
käsitteet ovat kaikissa samat.

## Mitä kirjasto tekee

Testcontainers puhuu Docker-daemonille sen rajapinnan kautta, samoin
kuin `docker`-komentorivi. Kontin käynnistys tekee nämä vaiheet:

1. Hakee kuvan, jos sitä ei ole paikallisesti.
2. Käynnistää siivoojakontin (*Ryuk*), jos se ei jo ole käynnissä.
3. Luo kontin: ympäristömuuttujat, verkot, liitokset ja paljastetut
   portit. Isännän portit valitsee Docker satunnaisesti.
4. Käynnistää kontin ja odottaa, että se on *valmis*: lokirivi, avoin
   portti, HTTP-vastaus tai komennon onnistuminen.
5. Antaa testille osoitteen ja portin, joilla kontin palvelu tavoitetaan.

Lopuksi kontti pysäytetään ja poistetaan. Jos testiprosessi kaatuu
ennen sitä, Ryuk huomaa yhteyden katkeavan ja poistaa prosessin kontit,
verkot ja taltiot.

Satunnaiset isäntäportit ovat tärkeä yksityiskohta: rinnakkaiset
testiajot samalla koneella eivät törmää toisiinsa, eikä testi oleta,
että portti 5432 on vapaa.

## Elinkaari käsin

Tavallisesti kontti käytetään `with`-lauseella, mutta elinkaari näkyy
selvimmin, kun vaiheet kirjoitetaan auki. Yleinen `DockerContainer`
toimii mille tahansa kuvalle; tässä Redis, jonka valmius tunnistetaan
lokirivistä:

```{.python tiedosto="esimerkit/luku03/elinkaari.py" osa="elinkaari"}
```

```{.tuloste tiedosto="esimerkit/luku03/elinkaari.odotettu"}
```

`try`–`finally` varmistaa, että kontti poistetaan, vaikka testi
epäonnistuisi. `with`-lause tekee saman lyhyemmin, ja pytestin fixture
(luku 4) vielä siistimmin.

## Odotusstrategiat

Kontin käynnistyminen ei tarkoita, että palvelu olisi valmis.
PostgreSQL-kuva esimerkiksi käynnistää tietokannan, ajaa
alustusskriptit, sammuttaa sen ja käynnistää uudelleen: portti voi olla
hetken auki ennen kuin tietokanta hyväksyy yhteyksiä. Testi, joka
yhdistää liian aikaisin, epäonnistuu satunnaisesti.

| Strategia | Valmis, kun | Sopii |
|-----------|-------------|-------|
| lokiviesti | kontti kirjoittaa annetun rivin | useimmat palvelimet |
| portti | TCP-portti hyväksyy yhteyden | yksinkertaiset palvelut |
| HTTP | polku vastaa halutulla tilakoodilla | web-palvelut |
| terveystarkistus | kuvan HEALTHCHECK raportoi terveen | kuvat, joissa se on |
| komento | komento kontissa onnistuu | tietokannat (`psql -c`) |

Valmiit moduulit tuntevat palvelunsa: `PostgresContainer` ajaa kontissa
`psql`-kyselyn, kunnes se onnistuu. Omalle kontille strategia valitaan
itse. Kiinteä `time.sleep(5)` on aina väärä valinta: se on hidas
nopealla koneella ja liian lyhyt kuormitetulla CI-koneella.

## Valmiit moduulit

Moduuli on `DockerContainer`-aliluokka, joka tuntee palvelun oletukset:
kuvan, portin, tunnukset, valmiusehdon ja yhteysosoitteen muodon.
Pythonin Testcontainersissa moduuleja on kymmeniä (PostgreSQL, MySQL,
MongoDB, Redis, Kafka, RabbitMQ, LocalStack, Elasticsearch …).
Varastopalvelun testit käyttävät kahta:

```{.python tiedosto="esimerkit/testiapu/kontit.py" osa="postgres"}
```

Kuvan nimi tulee keskitetysti tiedostosta `testiapu/kuvat.py`, jossa
versiot on lukittu ja kuvat haetaan peilistä (luku 10):

```{.python tiedosto="esimerkit/testiapu/kuvat.py" osa="kuvat"}
```

`get_connection_url()` antaa SQLAlchemyn yhteysosoitteen, jossa ovat
satunnainen isäntäportti ja kontin tunnukset. Tunnukset ovat
kertakäyttöisiä, joten ne saavat olla koodissa.

## Oma kuva testissä

Kaikkea ei löydy valmiina kuvana. Varastopalvelun hintapalvelu on toisen
tiimin palvelu; testeissä sen tilalla on pieni väärennös, joka on
kirjoitettu Pythonin vakiokirjastolla ja paketoitu omaksi kuvakseen:

```{.dockerfile tiedosto="esimerkit/apukuva/Dockerfile"}
```

```{.python tiedosto="esimerkit/apukuva/hintapalvelu.py" osa="kasittelija"}
```

Testcontainers rakentaa kuvan testin alussa (`DockerImage`), ja kontin
valmius odotetaan HTTP-kyselyllä:

```{.python tiedosto="esimerkit/testiapu/kontit.py" osa="apukuva"}
```

```{.python tiedosto="esimerkit/luku03/oma_kuva.py" osa="oma_kuva"}
```

```{.tuloste tiedosto="esimerkit/luku03/oma_kuva.odotettu"}
```

Docker käyttää rakennusvälimuistia, joten kuvan rakentaminen kestää
ensimmäisellä kerralla hetken ja sen jälkeen alle sekunnin. Kuva on
saman versionhallinnan alla kuin testit: kun väärennöstä muutetaan,
muutos näkyy samassa katselmoinnissa.

## Compose ja monen kontin kokonaisuudet

Testcontainers osaa käynnistää myös Docker Compose -tiedoston
(`DockerCompose`), mikä on kätevää, kun kehittäjien paikallinen ympäristö
on jo kuvattu Compose-tiedostona. Integraatiotesteissä yksittäiset
kontit ja yhteinen Docker-verkko (luku 8) ovat yleensä parempia: testi
näyttää koodissa, mitä se tarvitsee, ja jokainen testi voi käynnistää
vain tarvitsemansa.

## Muut kielet

Rakenne on sama kaikissa toteutuksissa; vain kielen testikehys vaihtuu.

| Kieli | Kirjasto | Elinkaari testikehyksessä |
|--------|-----------------------|----------------------------------|
| Java | `org.testcontainers` | JUnit 5: `@Testcontainers`, `@Container` |
| Kotlin | sama kuin Java | JUnit 5 tai Kotest-laajennus |
| Go | `testcontainers-go` | `t.Cleanup(...)` |
| .NET | `Testcontainers` (NuGet) | xUnit `IAsyncLifetime` |
| Node.js | `testcontainers` (npm) | `beforeAll`/`afterAll` |
| Python | `testcontainers` (PyPI) | pytest-fixture |

Javan JUnit 5 -laajennuksessa staattinen `@Container`-kenttä vastaa
pytestin istuntolaajuista fixturea ja instanssikenttä testikohtaista.
Spring Bootin `@ServiceConnection` kytkee kontin osoitteen sovelluksen
asetuksiin, mitä *Taustapalvelut* käsittelee. Pythonissa sama tehdään
käsin fixturessa: osoite annetaan testattavalle koodille parametrina.

## Käytännössä

- Käytä valmista moduulia, kun sellainen on: se tuntee palvelun
  valmiusehdon paremmin kuin itse kirjoitettu.
- Älä koskaan nuku arvattua aikaa. Odota lokiriviä, porttia tai
  HTTP-vastausta.
- Älä oleta porttinumeroita. Kysy kontilta isäntä ja kartoitettu portti.
- Lukitse kuvien versiot. `latest` vaihtuu kenenkään huomaamatta, ja
  testi epäonnistuu syystä, jolla ei ole mitään tekemistä muutoksen
  kanssa.
- Pidä testien omat apukuvat versionhallinnassa testien vieressä.

## Itsearviointi

- Osaat selittää kontin elinkaaren vaiheet ja Ryukin tehtävän.
- Osaat valita odotusstrategian palvelun mukaan ja perustella, miksi
  kiinteä viive on väärä ratkaisu.
- Osaat käynnistää valmiin moduulin ja yleisen kontin ja hakea niiden
  osoitteen ja portin.
- Osaat rakentaa testissä oman kuvan ja käynnistää siitä kontin.

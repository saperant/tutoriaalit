# Tietokanta sovelluksen rajapintana

Edellinen luku käytti tietokantaa suoraan ajurin kautta, ja SQL-lauseet
olivat siellä, missä niitä tarvittiin. Kun sovellus kasvaa, kyselyt
leviävät ympäri koodia: sama taulu luetaan kymmenessä paikassa, eikä
skeeman muutoksen vaikutuksia enää näe yhdestä tiedostosta. Siksi
tietokantakoodi kootaan omaan kerrokseensa, ja sen ja SQL:n väliin voi
tulla kyselynrakentaja tai oliorelaatiomuunnin (ORM). Tämä luku
esittelee tasot alhaalta ylös Pythonin ja Javan esimerkein, kertoo,
milloin mitäkin kannattaa käyttää, ja päättyy siihen, miten
tietokantakoodi testataan.

```{.dot otsikko="Tietokantarajapinnan tasot. Ylempi taso piilottaa SQL:ää enemmän, mutta jokainen tuottaa lopulta ajurille SQL-lauseen."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.25;
  palvelu [label="palvelukerros"];
  dao [label="tietovarasto\n(DAO, repository)"];
  orm [label="ORM\n(SQLAlchemy ORM, JPA)"];
  rakentaja [label="kyselynrakentaja\n(SQLAlchemy Core, jOOQ)"];
  ajuri [label="ajuri\n(DB-API, JDBC)"];
  kanta [label="tietokanta", shape=cylinder];
  palvelu -> dao;
  dao -> orm; dao -> rakentaja; dao -> ajuri;
  orm -> rakentaja -> ajuri -> kanta;
}
```

## Ajuri

Alin taso on luvun 14 ajuri: se lähettää SQL-tekstin ja parametrit
tietokannalle ja palauttaa rivit. Malli on sama kielestä riippumatta.
Pythonin DB-API ja Javan JDBC määrittelevät molemmat yhteyden, lauseen,
parametrit, tulosjoukon ja transaktion. Ajureita on yksi kullekin
tietokannalle (`sqlite3`, `psycopg`, PyMySQL; JDBC:ssä
`org.postgresql.Driver` ja MariaDB Connector/J), ja SQL kirjoitetaan
sen tietokannan murteella (luku 12). Luvun 14 haku JDBC:llä:

```{.java tiedosto="esimerkit/java/TuoteDao.java" osa="hae"}
```

Parametrit sidotaan `?`-paikkoihin samoin kuin Pythonissa.
Javan `try`-lohko resursseineen vastaa Pythonin `with`-lausetta ja
sulkee lauseen ja tulosjoukon. Testi kääntää tämän tiedoston, mutta
ajoon tarvittaisiin JDBC-ajuri ja tietokanta; ajettavat Java-esimerkit
ovat taidossa *Taustapalvelut*.

## Tietovarasto: DAO ja repository

Tietovarasto (*data access object*, DAO, tai *repository*) kokoaa
yhden käsitteen tietokantakoodin yhteen luokkaan. Palvelukerros
käyttää vain varaston rajapintaa:

```{.python tiedosto="esimerkit/15-dao.py" osa="rajapinta"}
```

Toteutus sisältää SQL:n, ja vain se tietää, mitä tietokantaa
käytetään:

```{.python tiedosto="esimerkit/15-dao.py" osa="sqlite"}
```

Palvelukerroksen sääntö ei näe SQL:ää:

```{.python tiedosto="esimerkit/15-dao.py" osa="palvelu"}
```

Rajapinnan ansiosta palvelun voi testata muistiin tehdyllä
testikaksoisella:

```{.python tiedosto="esimerkit/15-dao.py" osa="muisti"}
```

Testikaksoinen on nopea, mutta se ei tarkista SQL:ää, rajoitteita
eikä murre-eroja. Ero näkyy, kun palvelua kutsutaan virheellisellä
arvolla:

```{.python tiedosto="esimerkit/15-dao.py" osa="ero"}
```

```{.tuloste tiedosto="esimerkit/15-dao.odotettu"}
```

Molemmat toteutukset antavat saman tuloksen tavallisessa käytössä,
mutta vain oikea tietokanta hylkää negatiivisen hinnan. Osio
*Tietokantakoodin testaus* luvun lopussa palaa tähän.

## Kyselynrakentaja

Kyselynrakentaja rakentaa SQL:n ohjelmointikielen olioista. Kysely on
silloin tavallista koodia: sen osia voi koota funktioilla, tyypit
tarkistetaan, ja rakentaja kirjoittaa kunkin tietokannan murteen.
SQLAlchemy Core:

```{.python tiedosto="esimerkit/15-core.py" osa="taulut"}
```

```{.python tiedosto="esimerkit/15-core.py" osa="kysely"}
```

Sama kysely käännetään kolmelle murteelle ja ajetaan SQLitessä:

```{.python tiedosto="esimerkit/15-core.py" osa="murteet"}
```

```{.tuloste tiedosto="esimerkit/15-core.odotettu"}
```

Parametrien merkintä vaihtuu murteen mukaan, ja MariaDB-murre kirjoittaa
`INNER JOIN`. SQLite tarvitsee `LIMIT`-lauseeseen `OFFSET`-osan.
Javassa vastaava kirjasto on **jOOQ**. Se generoi tietokannan skeemasta
luokat, joten sarakkeen nimen tai tyypin virhe on käännösvirhe:

```{.java tiedosto="esimerkit/java/Jooq.java.txt" osa="jooq"}
```

Ote ei käänny ilman jOOQ-kirjastoa ja generoitua koodia, eikä sitä
testata tässä paketissa. jOOQ on avoin avoimille tietokannoille ja
kaupallinen Oraclelle ja SQL Serverille.

## ORM

Oliorelaatiomuunnin (*object-relational mapper*) kuvaa taulut
luokiksi ja rivit olioiksi. Sovellus käsittelee olioita, ja ORM päättää,
milloin ja millä SQL:llä ne luetaan ja tallennetaan. SQLAlchemyn
ORM-mallit:

```{.python tiedosto="esimerkit/15-orm.py" osa="mallit"}
```

ORM:n keskeiset mekanismit ovat

- **työyksikkö** (*unit of work*): istunto kerää muutokset ja kirjoittaa
  ne yhdessä transaktiossa, kun lohko päättyy tai kutsutaan `flush`,
- **identiteettikartta** (*identity map*): istunnossa kutakin riviä
  vastaa yksi olio, joten sama asiakas on sama olio, haettiin se miten
  tahansa,
- **laiska lataus** (*lazy loading*): yhteydet luetaan vasta, kun niitä
  käytetään.

```{.python tiedosto="esimerkit/15-orm.py" osa="tyoyksikko"}
```

```{.python tiedosto="esimerkit/15-orm.py" osa="identiteetti"}
```

Laiska lataus on mukava, mutta silmukassa se tuottaa luvun 14
N+1-kyselyt huomaamatta: koodissa näkyy vain olion ominaisuuden luku,
ei kyselyä. Ennakkolataus (`selectinload`) hakee kaikkien asiakkaiden
tilaukset yhdellä lisäkyselyllä:

```{.python tiedosto="esimerkit/15-orm.py" osa="n-plus-1"}
```

```{.tuloste tiedosto="esimerkit/15-orm.odotettu"}
```

Testi ajaa saman ohjelman SQLiten lisäksi PostgreSQL:ää ja MariaDB:tä
vasten, ja tulosteen on oltava kaikissa sama. Siirrettävyys on ORM:n
etu, mutta se pätee vain siihen, mitä ORM itse kirjoittaa: luvun 12
erot jakolaskussa ja vertailussa koskevat ORM:n kautta tehtyjä
kyselyitä yhtä lailla.

Javassa ORM-standardi on JPA, jonka yleisin toteutus on Hibernate.
Spring Data rakentaa sen päälle repository-rajapinnat, joiden
kyselyt johdetaan metodien nimistä. Skeeman versiointiin ORM:n kanssa
käytetään migraatiotyökalua: SQLAlchemyn kanssa Alembicia, Javassa
Flywayta tai Liquibasea (luku 14).

## Milloin mitäkin

| Taso | Hyvä | Varo |
|------|------|------|
| ajuri ja SQL | täysi hallinta, raportit, joukkopäivitykset | toistuva rivien muunto, murre koodissa |
| kyselynrakentaja | koottavat kyselyt, murteet, tyyppitarkistus | kirjaston opettelu, monimutkainen SQL voi olla kömpelöä |
| ORM | CRUD, olioverkot, työyksikkö | N+1, piilotettu SQL, suuret joukot olioina |

Kaikki abstraktiot vuotavat: suorituskyky, lukitus ja murre-erot
riippuvat lopulta siitä SQL:stä, jonka tietokanta saa. Siksi
kehityksessä kirjataan lokiin jokainen lause (`echo=True`
SQLAlchemyssä, `show-sql` Hibernatessa), ja ORM:n rinnalla käytetään
suoraa SQL:ää siellä, missä se on selkeämpää.

## Tietokantakoodin testaus

Kerrosjako määrää myös, mitä vasten kukin osa testataan:

| Testattava | Mitä vasten | Mitä testi löytää |
|------------|-------------|-------------------|
| palvelukerroksen säännöt | testikaksoinen | logiikkavirheet, nopeasti |
| tietovarasto, kyselyt | oikea tietokanta | SQL-virheet, rajoitteet, murre-erot |
| migraatiot | tyhjä tietokanta, sama järjestelmä kuin tuotannossa | rikkinäinen tai puuttuva migraatio |
| kyselyjen määrä | lauselaskuri | N+1 |

Tietovaraston testi tarvitsee tietokannan, jonka tila tunnetaan testin
alussa. SQLitellä jokainen testi voi avata oman muistitietokannan.
Palvelintietokannalla skeema luodaan migraatioilla kerran, ja kukin
testi ajetaan transaktiossa, joka perutaan lopuksi, tai taulut
tyhjennetään testien välillä. Tämän tutoriaalin palvelinesimerkit
käynnistävät testiajossa väliaikaiset PostgreSQL- ja MariaDB-palvelimet
(`esimerkit/palvelimet/aja.sh`); sovellusprojektissa sama tehdään
kertakäyttöisellä kontilla Testcontainers-kirjastolla (taito
*Integraatiotestaus ja Testcontainers*; Java-esimerkki taidon
*Taustapalvelut* testausluvussa).

Testitietokannan on oltava sama järjestelmä kuin tuotannossa. SQLite
testeissä ja PostgreSQL tuotannossa eroavat tyypeissä, lukituksessa ja
virheilmoituksissa (luku 12), ja juuri ne virheet, jotka testin piti
löytää, löytyvät vasta tuotannosta.

## Käytännössä

- **Tietovarasto rajaa SQL:n yhteen paikkaan**, käytettiin sen sisällä
  mitä tasoa tahansa. Palvelukerros ei tunne tauluja eikä istuntoja.
- **Valitse taso tehtävän mukaan, ei koko sovellukselle kerralla.** ORM
  lomakkeiden takana olevaan CRUDiin, SQL raportteihin ja
  joukkopäivityksiin samassa sovelluksessa.
- **Mittaa kyselyjen määrä testeissä.** Esimerkin laskuri on halpa tapa
  havaita N+1 ennen tuotantoa.
- **Testaa tietovarastot oikeaa tietokantaa vasten.** Testikaksoinen
  sopii palvelukerroksen yksikkötesteihin, mutta SQL, rajoitteet ja
  murre-erot testataan samalla tietokantajärjestelmällä kuin
  tuotannossa.
- **Transaktion raja on palvelukerroksessa** (luku 14): ORM:n istunto
  avataan pyyntöä tai liiketoimintatapahtumaa kohden, ei koko
  sovelluksen ajaksi.

## Itsearviointi

- Osaat kuvata tietokantarajapinnan tasot ajurista ORM:ään ja kertoa,
  mitä kukin piilottaa.
- Osaat eristää tietokantakoodin tietovarastoon ja testata palvelun
  testikaksoisella.
- Osaat rakentaa kyselyn kyselynrakentajalla ja tarkistaa, millaista
  SQL:ää se tuottaa eri tietokannoille.
- Osaat selittää ORM:n työyksikön, identiteettikartan ja laiskan
  latauksen sekä korjata N+1-ongelman ennakkolatauksella.
- Osaat valita, mikä osa tietokantakoodista testataan testikaksoisella
  ja mikä oikeaa tietokantaa vasten.

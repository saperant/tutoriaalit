# SQL sovelluksesta

Tähän asti SQL on kirjoitettu komentorivityökaluun. Sovelluksessa samat
lauseet lähtevät ohjelmakoodista, ja väliin tulee *ajuri*: kirjasto,
joka avaa yhteyden, lähettää lauseen tietokannalle ja muuntaa tuloksen
ohjelmointikielen arvoiksi. SQL itse ei muutu, mutta ympärille tulee
uusia kysymyksiä: miten ohjelman arvot viedään kyselyyn, missä
transaktio alkaa ja päättyy ja mitä tehdään, kun tietokanta hylkää
lauseen.

```{.dot otsikko="Sovellus puhuu tietokannalle ajurin kautta. SQL-teksti ja arvot kulkevat erikseen, ja tulos palaa riveinä."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.9;
  sovellus [label="sovelluskoodi"];
  ajuri [label="ajuri\n(sqlite3, psycopg, JDBC)"];
  kanta [label="tietokanta", shape=cylinder];
  sovellus -> ajuri [label="SQL-teksti, jossa\npaikkamerkit"];
  sovellus -> ajuri [label="arvot erikseen"];
  ajuri -> kanta [label="lause + parametrit"];
  kanta -> ajuri [label="rivit tai virhe"];
  ajuri -> sovellus [label="kielen arvot\ntai poikkeus"];
}
```

Luku etenee samassa järjestyksessä kuin sovelluksen ensimmäinen
tietokantakutsu: yhteys ja kysely, arvojen vienti parametreina,
transaktiot, virheet ja lopuksi kaksi asiaa, jotka tulevat vastaan
heti, kun sovellus kasvaa: kyselyjen määrä ja skeeman muuttaminen.
Esimerkit käyttävät Python 3.12:n standardikirjaston
`sqlite3`-moduulia. Pythonin ajurit noudattavat samaa DB-API-määrittelyä
(PEP 249), joten sama rakenne toimii PostgreSQL:n `psycopg`-ajurilla ja
MariaDB:n PyMySQL:llä; erot kerrotaan matkan varrella. Seuraava luku
kokoaa tietokantakoodin kerroksiksi ja esittelee kyselynrakentajan ja
ORM:n.

## Yhteys, kysely ja tulokset

*Yhteys* on istunto tietokantaan. SQLitessä se on avoin tiedosto,
palvelintietokannassa verkkoyhteys ja kirjautunut käyttäjä. Yhteydet
avataan yhdessä funktiossa, jotta asetukset ovat aina samat. Luvun 9
`PRAGMA foreign_keys` on yhteyskohtainen ja kuuluu siksi tähän:

```{.python tiedosto="esimerkit/14-yhteys.py" osa="avaa"}
```

`execute` lähettää lauseen ja palauttaa *kursorin*, josta rivit luetaan.
Kursorin voi käydä läpi silmukassa, jolloin rivit haetaan sitä mukaa
kuin niitä käytetään, tai lukea kerralla (`fetchall`). Yhden rivin
kyselyyn sopii `fetchone`, joka palauttaa `None`, jos riviä ei ole:

```{.python tiedosto="esimerkit/14-yhteys.py" osa="kysely"}
```

```{.python tiedosto="esimerkit/14-yhteys.py" osa="yksi"}
```

Ajuri muuntaa tietokannan arvot kielen tyypeiksi. NULL on Pythonissa
`None`. SQLitessä on vain neljä tallennustyyppiä, joten päivämäärä
palaa tekstinä ja muunnetaan sovelluksen reunalla:

```{.python tiedosto="esimerkit/14-yhteys.py" osa="tyypit"}
```

Muuttavan lauseen jälkeen kursori kertoo, mitä tapahtui: `lastrowid` on
lisätyn rivin tunniste ja `rowcount` muuttuneiden rivien määrä.
Muutokset jäävät voimaan vasta sitoutuksessa:

```{.python tiedosto="esimerkit/14-yhteys.py" osa="muutos"}
```

```{.tuloste tiedosto="esimerkit/14-yhteys.odotettu"}
```

Palvelintietokannan ajuri tuntee enemmän tyyppejä. Sama tehtävä
`sqlite3`:lla ja PostgreSQL:n `psycopg`-ajurilla:

```{.python tiedosto="esimerkit/14-tyypit.py" osa="sqlite"}
```

```{.python tiedosto="esimerkit/14-tyypit.py" osa="postgres"}
```

```{.tuloste tiedosto="esimerkit/palvelimet/14-tyypit.pg.odotettu"}
```

PostgreSQL:n `numeric` on Pythonissa `Decimal`, `date` on `date` ja
`timestamptz` aikavyöhykkeellinen `datetime`, joten rahasummat ja ajat
säilyvät tarkkoina ilman omaa muunnoskoodia (luku 12). Rakenne on
muuten sama; vain paikkamerkki vaihtui (`?` → `%s`), mihin palataan
seuraavassa osiossa.

Yhteyden avaaminen palvelimeen maksaa: TCP-yhteys, TLS-kättely ja
kirjautuminen vievät millisekunteja, ja jokainen yhteys varaa
palvelimelta muistia. Palvelinsovellus ei siksi avaa yhteyttä pyyntöä
kohden vaan lainaa sen *yhteysaltaasta* (*connection pool*) ja palauttaa
sen käytön jälkeen.

## Arvot kyselyyn: parametrit

Lähes jokainen sovelluksen kysely riippuu arvosta, joka tunnetaan vasta
ajon aikana: haettavan asiakkaan nimi, tilauksen tunniste, lomakkeen
kenttä. Arvoa ei kirjoiteta SQL-tekstiin. Tekstiin tulee *paikkamerkki*,
ja arvot annetaan `execute`-kutsulle erikseen:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="oikein"}
```

Kun arvoja on monta tai sama arvo toistuu, nimetyt paikkamerkit ovat
selkeämpiä:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="nimetty"}
```

```{.python tiedosto="esimerkit/14-parametrit.py" osa="kaytto"}
```

Tietokanta jäsentää SQL-tekstin ensin ja sijoittaa arvot valmiiseen
lauseeseen vasta sen jälkeen. Arvo on siis aina arvo: sen sisältö ei
voi muuttaa lauseen rakennetta, eikä heittomerkki nimessä `O'Connor`
vaadi mitään erikoiskäsittelyä. Samalla tietokanta voi käyttää
jäsennettyä lausetta ja sen suunnitelmaa uudelleen eri arvoilla.

Paikkamerkin kirjoitusasu riippuu ajurista, ei tietokannasta:

| Ajuri | Paikkamerkki | Nimetty |
|-------|--------------|---------|
| `sqlite3` | `?` | `:nimi` |
| `psycopg`, PyMySQL | `%s` | `%(nimi)s` |
| JDBC (Java) | `?` | ei ole |

`%s` ei ole Pythonin merkkijonomuotoilua, vaikka näyttää siltä: arvot
annetaan edelleen `execute`-kutsun toisena argumenttina, ei
`%`-operaattorilla.

### Miksi arvoja ei liimata tekstiin: SQL-injektio

Paikkamerkin vaihtoehto olisi rakentaa SQL-teksti itse yhdistämällä
merkkijonoja:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="liimaus"}
```

Nyt arvo on osa SQL-tekstiä, ja tietokanta jäsentää sen lauseen mukana.
Seuraus näkyy kahdella syötteellä:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="hajoaa"}
```

```{.tuloste tiedosto="esimerkit/14-parametrit.odotettu"}
```

Ensimmäisessä tapauksessa nimen heittomerkki päättää merkkijonon kesken,
ja loppuosa on kelvotonta SQL:ää. Liimattu kysely on siis rikki jo
tavallisella syötteellä. Toisessa tapauksessa syöte on valittu niin,
että tulos on kelvollista SQL:ää, jonka merkitys on eri: ehto
`nimi = '' OR '1'='1'` on tosi jokaiselle riville. Tämä on
*SQL-injektio*. Samalla tavalla hyökkääjä voi lukea muita tauluja
(`UNION SELECT`), ohittaa kirjautumisen tai muuttaa tietoja, koska
tietokanta ei voi erottaa sovelluksen kirjoittamaa SQL:ää syötteen
mukana tulleesta.

Heittomerkkien korvaaminen tai syötteen "puhdistaminen" ei ole korjaus:
säännöt riippuvat tietokannasta ja merkistöstä, ja yksikin unohtunut
kohta riittää. Parametri poistaa koko virheluokan, koska arvoa ei
jäsennetä SQL:nä lainkaan. Parametrisoitu haku palauttaa hyökkäyssyötteellä
nolla riviä: sen nimistä asiakasta ei ole.

### Listat ja tunnisteet

Paikkamerkki vastaa yhtä arvoa. `IN`-listalle tehdään yksi paikkamerkki
kutakin arvoa kohden; SQL-tekstiin päätyy edelleen vain paikkamerkkejä:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="lista"}
```

Taulujen ja sarakkeiden nimiä ei voi parametrisoida, koska ne ovat osa
lauseen rakennetta. Kun käyttäjä valitsee esimerkiksi järjestyksen,
nimi valitaan *sallittujen luettelosta*, eikä syötettä käytetä
sellaisenaan:

```{.python tiedosto="esimerkit/14-parametrit.py" osa="tunniste"}
```

## Transaktiot

Luvun 10 `BEGIN`, `COMMIT` ja `ROLLBACK` ovat sovelluksessa yhteyden
metodeja. Python 3.12:n `sqlite3.connect(..., autocommit=False)` toimii
DB-API:n mukaisesti: transaktio on aina auki, ja `commit()` tai
`rollback()` päättää sen. Yhteys `with`-lauseessa sitoo transaktion,
kun lohko päättyy normaalisti, ja peruu sen, kun lohkosta lähtee
poikkeus:

```{.python tiedosto="esimerkit/14-transaktiot.py" osa="siirto"}
```

```{.python tiedosto="esimerkit/14-transaktiot.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/14-transaktiot.odotettu"}
```

Toisessa siirrossa Matin tili ei riitä. Ensimmäinen `UPDATE` ehti jo
lisätä rahat Ainolle, mutta `CHECK`-rajoitteen virhe peruu koko
transaktion. Rajoite tekee tarkistuksen ja `with`-lohko perumisen:
sovelluksessa ei tarvita kumpaakaan erikseen.

`with yhteys` *ei sulje* yhteyttä, vaan hallitsee vain transaktiota.
Yhteys suljetaan `close()`-kutsulla tai
`contextlib.closing`-kääreellä, kuten luvun ensimmäisessä esimerkissä.
Oletusasetus ilman `autocommit`-parametria on vanha käytös, jossa
moduuli avaa transaktiot vain osalle lauseista; uusi koodi käyttää
parametria aina. `psycopg`-ajurissa vastaava lohko on
`with yhteys.transaction():`; siellä `with yhteys` sitoo transaktion ja
myös sulkee yhteyden.

## Virheet

Tietokanta ilmoittaa hylätystä lauseesta virheellä, jonka ajuri
muuntaa poikkeukseksi. DB-API määrittelee poikkeuksille yhteisen
jaottelun, joka on sama kaikissa ajureissa:

| Poikkeus | Syy | Sovelluksen toimi |
|---------------------|----------------------------------------|---------------------------------|
| `IntegrityError` | rajoite rikkoutui | muunna sovelluksen virheeksi |
| `OperationalError` | lukitus, yhteys katkesi, levy täynnä | yritä uudelleen, jos tilapäinen |
| `ProgrammingError` | virheellinen SQL, väärä parametrimäärä | korjaa koodi |
| `DataError` | arvo ei sovi tyyppiin | hylkää syöte |

Rajoitevirhe on odotettu tilanne, ei ohjelmointivirhe: kaksi käyttäjää
voi yrittää rekisteröidä saman sähköpostiosoitteen samalla hetkellä,
ja vain `UNIQUE`-rajoite ratkaisee kilpailun oikein (luku 9).
Tietovarastokoodi muuntaa sen sovelluksen omaksi virheeksi, jonka
käyttöliittymä osaa näyttää:

```{.python tiedosto="esimerkit/14-virheet.py" osa="rajoite"}
```

```{.python tiedosto="esimerkit/14-virheet.py" osa="kaytto"}
```

Tarkistus ennen lisäystä (`SELECT`, sitten `INSERT`) ei korvaa tätä:
kahden lauseen välissä toinen yhteys ehtii lisätä saman osoitteen.
Etukäteistarkistus kelpaa lomakkeen pikapalautteeksi, mutta oikeellisuus
tulee rajoitteesta ja sen virheen käsittelystä.

Tilapäiset virheet ovat toinen ryhmä. SQLitessä toinen kirjoittaja voi
pitää tietokantaa varattuna (luku 10), ja PostgreSQL keskeyttää
*serializable*-tasolla ristiriitaisen transaktion tai lukkiutuman
toisen osapuolen. Silloin koko transaktio ajetaan uudelleen alusta:

```{.python tiedosto="esimerkit/14-virheet.py" osa="uudelleen"}
```

```{.python tiedosto="esimerkit/14-virheet.py" osa="lukitus"}
```

```{.tuloste tiedosto="esimerkit/14-virheet.odotettu"}
```

Uudelleenyritys on turvallinen vain, jos epäonnistunut yritys peruttiin
kokonaan eikä transaktion sisällä tehty muuta kuin tietokantamuutoksia.
Sähköpostin lähetys tai maksukutsu transaktion keskellä toistuisi
jokaisella yrityksellä. `psycopg`:ssä vastaavat poikkeukset ovat
`errors.SerializationFailure` ja `errors.DeadlockDetected`.

## N+1-kyselyt

Kun sovellus toimii oikein, seuraava yleinen ongelma on kyselyjen
määrä. N+1-ongelmassa sovellus hakee listan yhdellä kyselyllä ja
sitten jokaisen rivin lisätiedot omalla kyselyllään:

```{.python tiedosto="esimerkit/14-n-plus-1.py" osa="n-plus-1"}
```

Sama tieto saadaan yhdellä liitoksella:

```{.python tiedosto="esimerkit/14-n-plus-1.py" osa="liitos"}
```

Kyselyt lasketaan jäljityskutsulla, joka saa jokaisen suoritetun lauseen:

```{.python tiedosto="esimerkit/14-n-plus-1.py" osa="laskuri"}
```

```{.tuloste tiedosto="esimerkit/14-n-plus-1.odotettu"}
```

Viidellä asiakkaalla ero on pieni, mutta kyselyjen määrä kasvaa datan
mukana. Palvelintietokannassa jokainen kysely on verkkokierros (0,1–1
ms samassa konesalissa), joten 1 000 asiakkaan sivu maksaa sekunnin
pelkkää odotusta. ORM-kirjastoissa sama ongelma syntyy huomaamatta
(luku 15).

## Skeeman versiointi

Sovelluksen koodi ja tietokannan skeema muuttuvat yhdessä, mutta
skeemaa ei voi korvata uudella versiolla kuten koodia: taulussa on jo
dataa. Tuotantotietokannan skeemaa muutetaan siksi *migraatioilla*:
numeroiduilla muutoksilla, jotka ajetaan järjestyksessä ja kukin
kerran. SQLitessä versio tallennetaan tietokannan otsakkeeseen
`PRAGMA user_version`:

```{.python tiedosto="esimerkit/14-migraatiot.py" osa="migraatiot"}
```

```{.tuloste tiedosto="esimerkit/14-migraatiot.odotettu"}
```

Kukin migraatio ja versionumeron päivitys ovat samassa transaktiossa,
joten keskeytynyt migraatio ei jätä kantaa puolivalmiiksi. SQLitessä ja
PostgreSQL:ssä skeemamuutokset ovat transaktionaalisia, MariaDB:ssä ja
MySQL:ssä eivät. Valmiita työkaluja ovat Alembic
(SQLAlchemy), Djangon migraatiot, Flyway ja Liquibase.

## Käytännössä

- **Yhteyden asetukset yhdessä paikassa.** SQLitessä jokainen yhteys
  tarvitsee `PRAGMA foreign_keys = ON` -asetuksen ja odotusajan; tehdas-
  funktio avaa yhteydet aina samoin. Palvelintietokannassa yhteydet
  otetaan yhteysaltaasta.
- **Parametrit aina.** Yksikään arvo ei päädy SQL-tekstiin
  merkkijonoja yhdistämällä, ei edes "luotettava" tai numeerinen.
  Tunnisteet valitaan sallittujen luettelosta.
- **Pienimmät oikeudet.** Sovelluksen tietokantakäyttäjällä ei ole
  oikeutta muuttaa skeemaa tai lukea tauluja, joita se ei tarvitse.
  Jos jokin kysely silti jää haavoittuvaksi, vahinko rajautuu näihin
  oikeuksiin.
- **Transaktion rajat palvelukerroksessa.** Yksi liiketoimintatapahtuma
  (tilauksen luonti) on yksi transaktio, joka sitoutetaan tai perutaan
  kokonaisuutena. Tietokantakutsut eivät sido kukin erikseen.
- **Rajoitevirhe on osa rajapintaa.** Odotetut rajoitteet muunnetaan
  sovelluksen virheiksi yhdessä paikassa; tuntematon tietokantavirhe
  saa kaataa pyynnön ja päätyä lokiin.
- **Uudelleenyritys vain tilapäisille virheille**, rajatulla määrällä
  ja kasvavalla, satunnaistetulla viiveellä. Ohjelmointivirhettä ei
  yritetä uudelleen.
- **Migraatiot versionhallintaan.** Skeema syntyy aina samoista
  migraatioista kehityksessä, testeissä ja tuotannossa. Ajettua
  migraatiota ei muuteta.
- **Hinnat**: jokainen `execute` palvelintietokantaan on verkkokierros.
  Monta riviä lisätään yhdellä `executemany`-kutsulla tai monen rivin
  `INSERT`-lauseella yhdessä transaktiossa, ja suuri tulos luetaan
  kursorista silmukassa eikä `fetchall`-kutsulla muistiin.

## Itsearviointi

- Osaat avata yhteyden, suorittaa kyselyn ja lukea tuloksen kursorista
  sekä kertoa, miten ajuri muuntaa tietokannan tyypit kielen arvoiksi.
- Osaat viedä arvot kyselyyn parametreina, myös `IN`-listoissa, ja
  valita tunnisteet sallittujen luettelosta.
- Osaat selittää, miksi SQL-tekstiin liimattu arvo johtaa
  SQL-injektioon ja miksi parametri poistaa ongelman.
- Osaat hallita transaktiota Pythonissa niin, että virhe peruu kaikki
  muutokset.
- Osaat muuntaa rajoitevirheen sovelluksen virheeksi ja yrittää
  tilapäisesti epäonnistunutta transaktiota uudelleen.
- Osaat tunnistaa N+1-kyselyt, mitata kyselyjen määrän ja korvata ne
  liitoksella.
- Osaat versioida skeeman migraatioilla ja perustella, miksi ajettua
  migraatiota ei muuteta.

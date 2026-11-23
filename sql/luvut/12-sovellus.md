# SQL sovelluksesta

Sovellus käyttää tietokantaa ajurin kautta. Pythonissa ajurit noudattavat
DB-API-määrittelyä (PEP 249): yhteys, `execute`, parametrit ja
transaktiot toimivat samalla tavalla moduuleissa `sqlite3` ja `psycopg`
(PostgreSQL). Luvun esimerkit käyttävät standardikirjaston
`sqlite3`-moduulia ja Python 3.12:ta.

## Parametrit ja SQL-injektio

SQL-injektio syntyy, kun syöte liitetään SQL-tekstiin. Syöte muuttuu
silloin osaksi kyselyä:

```{.python tiedosto="esimerkit/12-parametrit.py" osa="vaara"}
```

Syötteellä `' OR '1'='1` ehto muuttuu muotoon `nimi = '' OR '1'='1'`,
joka on tosi kaikille riveille. Samalla tekniikalla hyökkääjä voi lukea
muita tauluja tai muuttaa tietoja. Korjaus on *parametrisoitu kysely*:
SQL-teksti ja arvot lähetetään erikseen, eikä arvoa koskaan tulkita
SQL:nä.

```{.python tiedosto="esimerkit/12-parametrit.py" osa="oikein"}
```

`sqlite3` käyttää paikkamerkkiä `?` tai nimettyä `:nimi`, `psycopg`
merkkiä `%s`. IN-listalle tehdään yksi paikkamerkki kutakin arvoa
kohden; SQL-tekstiin päätyy vain paikkamerkkejä:

```{.python tiedosto="esimerkit/12-parametrit.py" osa="lista"}
```

Taulujen ja sarakkeiden nimiä ei voi parametrisoida. Kun käyttäjä
valitsee esimerkiksi järjestyksen, nimi valitaan *sallittujen
luettelosta*, eikä syötettä käytetä sellaisenaan:

```{.python tiedosto="esimerkit/12-parametrit.py" osa="tunniste"}
```

```{.tuloste tiedosto="esimerkit/12-parametrit.odotettu"}
```

## Transaktiot

Python 3.12:n `sqlite3.connect(..., autocommit=False)` toimii
DB-API:n mukaisesti: transaktio on aina auki, ja `commit()` tai
`rollback()` päättää sen. Yhteys `with`-lauseessa sitoo transaktion,
kun lohko päättyy normaalisti, ja peruu sen, kun lohkosta lähtee
poikkeus:

```{.python tiedosto="esimerkit/12-transaktiot.py" osa="siirto"}
```

```{.python tiedosto="esimerkit/12-transaktiot.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/12-transaktiot.odotettu"}
```

Toisessa siirrossa Matin tili ei riitä. Ensimmäinen `UPDATE` ehti jo
lisätä rahat Ainolle, mutta `CHECK`-rajoitteen virhe peruu koko
transaktion. Rajoite tekee tarkistuksen ja `with`-lohko perumisen:
sovelluksessa ei tarvita kumpaakaan erikseen.

`with yhteys` *ei sulje* yhteyttä, vaan hallitsee vain transaktiota.
Yhteys suljetaan `close()`-kutsulla tai
`contextlib.closing`-kääreellä. Oletusasetus ilman `autocommit`-
parametria on vanha käytös, jossa moduuli avaa transaktiot vain osalle
lauseista; uusi koodi käyttää parametria aina.

## N+1-kyselyt

N+1-ongelmassa sovellus hakee listan yhdellä kyselyllä ja sitten
jokaisen rivin lisätiedot omalla kyselyllään:

```{.python tiedosto="esimerkit/12-n-plus-1.py" osa="n-plus-1"}
```

Sama tieto saadaan yhdellä liitoksella:

```{.python tiedosto="esimerkit/12-n-plus-1.py" osa="liitos"}
```

Kyselyt lasketaan jäljityskutsulla, joka saa jokaisen suoritetun lauseen:

```{.python tiedosto="esimerkit/12-n-plus-1.py" osa="laskuri"}
```

```{.tuloste tiedosto="esimerkit/12-n-plus-1.odotettu"}
```

Viidellä asiakkaalla ero on pieni, mutta kyselyjen määrä kasvaa datan
mukana. Palvelintietokannassa jokainen kysely on verkkokierros (0,1–1
ms samassa konesalissa), joten 1 000 asiakkaan sivu maksaa sekunnin
pelkkää odotusta. ORM-kirjastoissa ongelma syntyy huomaamatta
viivästetystä latauksesta (*lazy loading*), kun silmukassa luetaan
olion yhteyttä; korjaus on ennakkolataus (SQLAlchemyssä
`selectinload`, Djangossa `select_related` ja `prefetch_related`).

## Skeeman versiointi

Tuotantotietokannan skeemaa muutetaan *migraatioilla*: numeroiduilla
muutoksilla, jotka ajetaan järjestyksessä ja kukin kerran. SQLitessä
versio tallennetaan tietokannan otsakkeeseen `PRAGMA user_version`:

```{.python tiedosto="esimerkit/12-migraatiot.py" osa="migraatiot"}
```

```{.tuloste tiedosto="esimerkit/12-migraatiot.odotettu"}
```

Kukin migraatio ja versionumeron päivitys ovat samassa transaktiossa,
joten keskeytynyt migraatio ei jätä kantaa puolivalmiiksi. SQLitessä ja
PostgreSQL:ssä skeemamuutokset ovat transaktionaalisia, MySQL:ssä eivät.
Valmiita työkaluja ovat Alembic (SQLAlchemy), Djangon migraatiot,
Flyway ja Liquibase.

## Käytännössä

- **Parametrit aina.** Yksikään arvo ei päädy SQL-tekstiin
  merkkijonoja yhdistämällä, ei edes "luotettava" tai numeerinen.
  Tunnisteet valitaan sallittujen luettelosta.
- **Pienimmät oikeudet.** Sovelluksen tietokantakäyttäjällä ei ole
  oikeutta muuttaa skeemaa tai lukea tauluja, joita se ei tarvitse.
  Injektion vahinko rajautuu silloin näihin oikeuksiin.
- **Transaktion rajat palvelukerroksessa.** Yksi liiketoimintatapahtuma
  (tilauksen luonti) on yksi transaktio, joka sitoutetaan tai perutaan
  kokonaisuutena. Tietokantakutsut eivät sido kukin erikseen.
- **Yhteyden asetukset yhdessä paikassa.** SQLitessä jokainen yhteys
  tarvitsee `PRAGMA foreign_keys = ON` -asetuksen ja odotusajan; tehdas-
  funktio avaa yhteydet aina samoin. Palvelintietokannassa yhteydet
  otetaan *yhteysaltaasta* (*connection pool*), koska yhteyden avaus
  maksaa millisekunteja.
- **Migraatiot versionhallintaan.** Skeema syntyy aina samoista
  migraatioista kehityksessä, testeissä ja tuotannossa. Ajettua
  migraatiota ei muuteta.
- **Testaa samalla tietokannalla kuin tuotanto.** SQLite testeissä ja
  PostgreSQL tuotannossa eroavat tyypeissä, lukituksessa ja
  virheilmoituksissa; virheet löytyvät vasta tuotannosta.
- **ORM vai SQL.** ORM nopeuttaa tavallisia CRUD-toimintoja, mutta
  raportit, joukkopäivitykset ja ikkunafunktiot kirjoitetaan SQL:nä.
  Kaikissa tapauksissa kehittäjän on tiedettävä, mitä SQL:ää ORM tuottaa:
  kyselyiden lokitus on päällä kehityksessä.

## Itsearviointi

- Osaat selittää SQL-injektion ja torjua sen parametreilla, myös
  IN-listoissa ja käyttäjän valitsemissa sarakkeissa.
- Osaat hallita transaktiota Pythonissa niin, että virhe peruu kaikki
  muutokset.
- Osaat tunnistaa N+1-kyselyt, mitata kyselyjen määrän ja korvata ne
  liitoksella tai ennakkolatauksella.
- Osaat versioida skeeman migraatioilla ja perustella, miksi ajettua
  migraatiota ei muuteta.

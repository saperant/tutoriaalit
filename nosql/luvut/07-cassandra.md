# Cassandra: leveäsaraketietokanta

Apache Cassandra on tehty kirjoittamaan valtavia määriä dataa monelle
palvelimelle niin, ettei yksikään palvelin ole erityinen. Klusterissa
ei ole johtajaa: jokainen solmu ottaa vastaan kirjoituksia, data
jaetaan solmuille avaimen tiivisteen mukaan ja kopioidaan usealle
solmulle. Solmuja lisätään, kun kuorma kasvaa, ja läpäisy kasvaa
lähes suoraan solmujen määrän mukana. Sama malli on ScyllaDB:ssä
ja Amazonin DynamoDB:ssä, joiden juuret ovat samassa Dynamo-artikkelissa.

Hinta on kova: liitoksia ei ole, kyselyn on kohdistuttava tunnettuun
osioon, ja transaktiot rajoittuvat yhteen osioon. Cassandra palvelee
erinomaisesti kyselyjä, joita varten taulut on suunniteltu, eikä
juuri muita.

## Tietomalli: partitio ja klusterointi

Cassandran kyselykieli CQL näyttää SQL:ltä, mutta taulu on
rakenteeltaan toinen. Pääavaimella on kaksi osaa:

- **Partitioavain** päättää, mille solmuille rivi tallennetaan.
  Saman partitioavaimen rivit ovat samassa paikassa ja luetaan yhdellä
  haulla.
- **Klusterointiavain** järjestää rivit partition sisällä. Partitio on
  levyllä valmiiksi järjestetty, joten väli- ja järjestyshaut sen
  sisällä ovat halpoja.

Avainavaruus (*keyspace*) vastaa tietokantaa, ja sille annetaan
replikointikerroin:

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="avaruus"}
```

Tilaukset asiakkaittain, uusin ensin:

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="taulu"}
```

```{.dot otsikko="Partitio asiakkaittain: rivit järjestyksessä päivän mukaan."}
digraph {
  rankdir=LR; node [shape=record];
  aino [label="{partitio: aino|{2026-11-21|T5|49}|{2026-11-20|T3|168}|{2026-11-02|T1|107}}"];
  eero [label="{partitio: eero|{2026-11-03|T2|299}}"];
  ilona [label="{partitio: ilona|{2026-11-21|T4|90}}"];
  s1 [label="solmu A", shape=box]; s2 [label="solmu B", shape=box];
  aino -> s1; eero -> s2; ilona -> s1;
}
```

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="lisays"}
```

Haku osuu yhteen partitioon ja käyttää klusterointijärjestystä:

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="haku"}
```

## Kyselyt ensin, taulut niiden mukaan

Haku muulla kuin partitioavaimella vaatisi kaikkien solmujen kaikkien
partitioiden läpikäynnin. Cassandra kieltäytyy, ellei kyselyyn lisää
`ALLOW FILTERING`, mikä on tuotannossa lähes aina virhe:

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="kielletty"}
```

Oikea tapa on uusi taulu, jonka partitioavain on uuden kyselyn
hakuehto. Data kirjoitetaan molempiin:

```{.python tiedosto="esimerkit/luku07/taulut.py" osa="toinen"}
```

```{.tuloste tiedosto="esimerkit/luku07/taulut.odotettu"}
```

Tämä on Cassandran mallinnuksen ydin: yksi taulu kyselyä kohden, ja
denormalisointi on normaalia. Kirjoitukset ovat halpoja, joten
kirjoittaminen moneen tauluun on hyväksyttävä hinta nopeista luvuista.
Sovelluksen on pidettävä kopiot samassa tahdissa; `BATCH`-lause
kirjoittaa useaan tauluun niin, että kaikki kirjoitukset tehdään
lopulta, mutta ei eristetysti.

Partition koko on toinen suunnittelukysymys. Partitio, joka kasvaa
rajatta (esimerkiksi kaikki yhden anturin mittaukset), hidastuu ja
kuormittaa samoja solmuja. Tavallinen korjaus on lisätä
partitioavaimeen aikaväli.

## Aikasarja ämpäreihin

Varaston lämpötila-anturit lähettävät mittauksen kymmenen minuutin
välein. Partitioavain on anturi ja päivä, joten yksi partitio sisältää
yhden anturin yhden päivän mittaukset, uusin ensin. Taulun oletuselinaika
poistaa yli 30 päivän ikäiset mittaukset:

```{.python tiedosto="esimerkit/luku07/aikasarja.py" osa="taulu"}
```

```{.python tiedosto="esimerkit/luku07/aikasarja.py" osa="lisays"}
```

Uusin mittaus on partition ensimmäinen rivi, ja aikaväli on
klusterointiavaimen väli samassa partitiossa. Kumpikin haku lukee
vain yhden partition:

```{.python tiedosto="esimerkit/luku07/aikasarja.py" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/luku07/aikasarja.odotettu"}
```

Neljän tunnin mittaukset jakautuivat kahteen partitioon päivän
vaihtuessa. Kyselyn, joka ylittää päivän rajan, on haettava molemmat
partitiot; sovellus laskee tarvittavat päivät ja tekee haut
rinnakkain. Ämpärin koko valitaan niin, että partitio pysyy
kohtuullisena: kymmenen minuutin välein tuleville mittauksille
päivä on pieni, sekunnin välein tuleville tunti voi olla oikea.

Elinaika taulun oletuksena ja partitiot aikaväleittäin sopivat hyvin
yhteen: kokonaiset partitiot vanhenevat yhtä aikaa, ja Cassandran
aikaikkunoihin perustuva kompaktointi (`TimeWindowCompactionStrategy`)
voi pudottaa vanhentuneen tiedoston kokonaan ilman hautakivien
läpikäyntiä.

## Säädettävä konsistenssi

Jokainen kysely kertoo *konsistenssitason*: kuinka monen kopion on
vastattava. Kun replikointikerroin on 3, taso `ONE` tarvitsee yhden,
`QUORUM` kaksi ja `ALL` kaikki kolme. Taidossa *Hajautetut
järjestelmät* perustellaan, miksi kirjoitus ja luku tasolla `QUORUM`
näkevät aina toisensa: kaksi kahden joukkoa kolmesta leikkaavat.

Esimerkissä avainavaruuden replikointikerroin on 3, mutta klusterissa
on vain yksi solmu. Se vastaa tilannetta, jossa kaksi kolmesta
kopiosta on poissa:

```{.python tiedosto="esimerkit/luku07/konsistenssi.py" osa="tasot"}
```

```{.tuloste tiedosto="esimerkit/luku07/konsistenssi.odotettu"}
```

`ONE` onnistui, koska yksi kopio oli saatavilla. `QUORUM` ja `ALL`
hylättiin ennen kirjoitusta (*Unavailable*), koska koordinaattori tiesi,
ettei vaadittua määrää kopioita ole elossa. Tämä on CAP-valinta
konkreettisesti: sama data, ja kysely voi valita saatavuuden tai
konsistenssin.

## Poistot ja hautakivet

Cassandran tallennuskerros on LSM-puu (luku 8): tiedostoja ei muuteta
paikallaan. Poisto ei siksi poista mitään vaan kirjoittaa
*hautakiven* (*tombstone*), joka peittää vanhemmat versiot, kunnes
kompaktointi siivoaa ne. Hautakivi säilytetään vähintään
`gc_grace_seconds` (oletus 10 päivää), jotta se ehtii kopioitua kaikille
solmuille; muuten pois ollut solmu voisi herättää poistetun rivin
henkiin.

Elinaika (TTL) toimii samoin: vanhentunut arvo muuttuu hautakiveksi.

```{.python tiedosto="esimerkit/luku07/poistot.py" osa="ttl"}
```

Paljon poistoja tai lyhyitä elinaikoja samassa partitiossa on tunnettu
ongelma: luku joutuu käymään läpi tuhansia hautakiviä, ja Cassandra
varoittaa tai keskeyttää kyselyn. Jonomainen käyttö, jossa rivejä
lisätään ja poistetaan jatkuvasti, sopii Cassandralle huonosti.

## Kevyet transaktiot

Ehdollinen kirjoitus (`IF NOT EXISTS`, `IF sarake = arvo`) on
*kevyt transaktio* (*lightweight transaction*, LWT). Se toteutetaan
Paxos-konsensuksella kopioiden kesken, joten se on lineaarisoituva,
mutta vaatii useita edestakaisia matkoja:

```{.python tiedosto="esimerkit/luku07/poistot.py" osa="lwt"}
```

```{.tuloste tiedosto="esimerkit/luku07/poistot.odotettu"}
```

Kuponki voi olla vain yhdellä. Kevyitä transaktioita käytetään
harvoin tarvittavaan yksilöllisyyteen, kuten käyttäjätunnuksen
varaamiseen, ei jokaiseen kirjoitukseen.

## Käytännössä

- Luettele kyselyt ennen tauluja. Jokaiselle kyselylle oma taulu, jonka
  partitioavain on kyselyn yhtäsuuruusehto.
- Pidä partitiot rajattuina: lisää avaimeen aikaväli tai muu jako, jos
  partitio kasvaisi rajatta.
- Älä käytä `ALLOW FILTERING`-ehtoa tuotannossa; tarve on merkki
  puuttuvasta taulusta.
- Kirjoita ja lue tasolla `QUORUM` (tai `LOCAL_QUORUM` monessa
  konesalissa), kun tarvitset uusimman arvon. `ONE` on nopeampi mutta
  voi palauttaa vanhan.
- Vältä jonomaista käyttöä ja suuria poistomääriä samassa partitiossa
  hautakivien vuoksi.
- Valmistele lauseet (`prepare`): ajuri lähettää vain parametrit ja
  osaa ohjata kyselyn suoraan oikealle solmulle.

## Itsearviointi

- Osaat selittää partitio- ja klusterointiavaimen eron ja suunnitella
  taulun kyselyn mukaan.
- Osaat kertoa, miksi Cassandra hylkää haun ilman partitioavainta ja
  mitä sen sijaan tehdään.
- Osaat valita konsistenssitason ja ennustaa, milloin kysely
  epäonnistuu kopioiden puuttuessa.
- Osaat selittää, mitä hautakivet ovat ja miksi niistä tulee
  ongelma.

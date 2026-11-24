# Tietokannan valinta

Tähän mennessä on käsitelty neljä tietomallia. Tämä luku esittelee
lyhyesti kaksi muuta perhettä, joihin törmää usein – aikasarja- ja
hakutietokannat – ja kokoaa valinnan perusteet.

## Aikasarjatietokannat

Aikasarja on jono aikaleimattuja mittauksia: lämpötilat,
palvelimen kuorma, pörssikurssit, sähkönkulutus. Kuormalla on
tunnistettavat piirteet: kirjoituksia tulee tasaisesti valtavasti,
lähes aina uusimpaan aikaan; vanhaa dataa ei muuteta; kyselyt koskevat
aikaväliä ja koosteita (keskiarvo viiden minuutin ikkunoissa); ja vanha
data harvennetaan tai poistetaan säilytysajan jälkeen.

Aikasarjatietokannat hyödyntävät näitä piirteitä: ne pakkaavat
peräkkäiset arvot tehokkaasti (aikaleimojen erotukset, arvojen
XOR-pakkaus), jakavat datan aikaväleihin, joista vanhimman voi
poistaa kokonaisena, ja laskevat koosteet valmiiksi.

| Tietokanta | Malli | Huomioita |
|-------------|-------------------|-------------------|
| InfluxDB | oma tallennusmuoto, SQL ja InfluxQL | yleiskäyttöinen mittausdatalle |
| Prometheus | veto (*pull*) ja PromQL | palveluiden valvonta, ei pitkäaikaissäilytykseen |
| TimescaleDB | PostgreSQL-laajennus | täysi SQL, aikaväliin jaetut taulut |
| QuestDB, ClickHouse | sarakepohjaiset | analytiikka suurella datalla |

Cassandra sopii myös aikasarjoille, kun partitioavaimeen kuuluu
aikaväli (luku 7). Ja relaatiotietokanta riittää pitkälle: taidossa
*SQL ja relaatiotietokannat* näytetään, miten aikasarjoja käsitellään
PostgreSQLissa.

## Hakutietokannat

Tekstihaku – "retkikeitin kaasu kevyt" – vaatii *käänteisen
indeksin*: jokaisesta sanasta luettelo dokumenteista, joissa se
esiintyy. Hakutietokanta jäsentää tekstin sanoiksi kielen mukaan
(taivutusmuotojen perusmuodot, yhdyssanat), laskee osumille
relevanssin (BM25) ja palauttaa parhaat ensin. Lisäksi se laskee
koosteet hakutulokselle ("retkeily 12, valaisimet 3").

Elasticsearch ja sen avoin haara OpenSearch ovat yleisimmät; kevyempiä
ovat Meilisearch ja Typesense. PostgreSQLin tekstihaku (`tsvector`)
ja `pg_trgm` riittävät moneen sovellukseen. Suomen kielen taivutus
on haastavaa: perusmuotoistus vaatii kielikohtaisen analysaattorin,
esimerkiksi Voikko-sanaston.

Hakutietokanta ei ole yleensä pääasiallinen tallennuspaikka, vaan
siihen kopioidaan data relaatiotietokannasta. Kopio on lopulta
konsistentti: juuri tallennettu tuote ei välttämättä löydy haulla
heti.

Elasticsearchin lisenssi vaihtui vuonna 2021 avoimesta SSPL:ään ja
Elastic-lisenssiin, ja OpenSearch syntyi avoimena haarana. Vuonna 2024
Elasticsearch lisäsi vaihtoehdoksi AGPL-lisenssin.

## Vertailu

| Ominaisuus | Relaatio | Avain-arvo | Dokumentti | Leveäsarake | Graafi |
|----------|------------|------------|------------|------------|----------|
| esimerkki | PostgreSQL | Redis | MongoDB | Cassandra | Neo4j |
| tietomalli | taulut, liitokset | avain ja tietorakenne | sisäkkäiset dokumentit | partitio, järjestetyt rivit | solmut ja suhteet |
| kyselyt | vapaat | avaimella | kentillä, aggregaatio | partitioavaimella | polut |
| transaktiot | täydet | skriptit, `MULTI` | dokumentti, myös useampi | partitio, LWT | täydet |
| skaalaus | pysty, replikat | muisti, klusteri | osiointi | lineaarinen | pysty |
| vahvuus | yleiskäyttöisyys | nopeus | joustava rakenne | kirjoitusmäärä | yhteydet |

## Valintaprosessi

1. **Kirjoita kyselyt ja määrät.** Mitä luetaan, millä avaimella,
   kuinka usein ja kuinka suuria vastauksia? Mitä kirjoitetaan ja
   kuinka paljon?
2. **Kokeile relaatiotietokantaa.** Jos kuorma mahtuu yhdelle
   palvelimelle replikoineen ja kyselyt ovat moninaisia, valinta on
   tehty.
3. **Nimeä, mikä ei riitä.** Kirjoitusmäärä, latenssi, tietomallin
   hankaluus, polkukyselyt? Jos et osaa nimetä, relaatiotietokanta
   riittää.
4. **Valitse kapein työkalu, joka ratkaisee nimetyn ongelman,** ja
   pidä muu data relaatiotietokannassa.
5. **Mittaa todellisella datalla.** Tietokantojen esittelyluvut on
   saatu niiden omilla vertailuilla.
6. **Huomioi ylläpito ja lisenssi.** Jokainen tietokanta on varmuuskopioitava,
   päivitettävä ja valvottava. Pilvipalvelun hallinnoitu versio
   poistaa osan työstä, mutta sitoo palveluntarjoajaan.

## Käytännössä

- Uusi tietokanta on uusi operatiivinen vastuu. Lisää se vasta, kun
  nimetty ongelma on mitattu.
- Kopioitu data (haku, välimuisti, analytiikka) on lopulta
  konsistenttia. Suunnittele, miten kopio päivitetään ja mitä käyttäjä
  näkee viiveen aikana.
- Aikasarjoille ja tekstihaulle kokeile ensin PostgreSQLin omia keinoja
  (aikaväliin jaetut taulut, `tsvector`).
- Lue lisenssi ennen valintaa, jos aiot tarjota palvelua muille.

## Itsearviointi

- Osaat kertoa, mitkä kuorman piirteet tekevät aikasarjatietokannasta
  hyödyllisen.
- Osaat selittää käänteisen indeksin periaatteen ja miksi hakutietokanta
  on yleensä kopio.
- Osaat verrata relaatio-, avain-arvo-, dokumentti-, leveäsarake- ja
  graafitietokantoja tietomallin, kyselyjen ja skaalautumisen kannalta.
- Osaat perustella tietokannan valinnan kuorman perusteella.

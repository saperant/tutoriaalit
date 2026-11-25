# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Arvioi ennen kuin suunnittelet.** Pyynnöt sekunnissa, tallennus,
  kaista ja muisti kertovat, mahtuuko palvelu yhdelle koneelle ja mikä
  loppuu ensin.
- **Tavoitteet persentiileinä ja SLO:ina.** "p99 alle 200 ms" ja
  "99,9 % kuukaudessa" ovat mitattavia; "nopea" ja "aina ylhäällä" eivät.
- **Häntä ratkaisee hajautetussa pyynnössä.** Pidä pyynnöt kapeina ja
  leikkaa häntä varmistetuilla pyynnöillä, kun hitaus on satunnaista.
- **Mitoita N + 1 ja 60–70 % käyttöasteelle.** Jono kasvaa jyrkästi
  käyttöasteen lähestyessä sataa.
- **Tilaton sovelluskerros, tila erikseen.** Tilaton skaalautuu
  vaakaan; tila skaalautuu replikoinnilla ja osioinnilla.
- **Tasaa mukautuvasti.** Vähiten kesken tai kahden satunnaisen valinta
  kestää eri nopeuksiset palvelimet.
- **Konsistentti hajautus tai kiinteät lohkot.** Modulo siirtää lähes
  kaiken, kun solmuja lisätään.
- **Välimuisti TTL:llä, invalidoinnilla ja ryntäyssuojalla.** Ja palvelu,
  joka toimii ilman välimuistia.
- **Lue omat kirjoituksesi.** Asynkroninen replika on jäljessä;
  ratkaise, mitkä luvut saavat olla vanhoja.
- **Jono tasaa, mutta purkuaika riippuu ylijäämästä.** Seuraa jonon
  pituutta ja vanhimman viestin ikää.
- **Vähintään kerran ja idempotentti kuluttaja.** Täsmälleen kerran
  syntyy vain kuluttajan avulla.
- **Uudelleenyritys budjetilla ja määräajalla.** Muuten lyhyt häiriö voi
  muuttua pysyväksi ylikuormaksi.
- **Sarjassa saatavuudet kertautuvat.** Kahdenna tai tee ohitettavaksi
  jokainen yhden kappaleen osa, ja hajauta vikaantumisalueittain.
- **Histogrammit, jäljet ja oireisiin perustuvat hälytykset.** Persentiilejä
  ei voi keskiarvoistaa, ja jäljen tunnus yhdistää signaalit.

## Jatkotaidot

Tutoriaali käsitteli rakennuspalikat yksi kerrallaan ja kokosi ne yhdeksi
pieneksi palveluksi. Seuraavat askeleet ovat:

- **Palvelujen väliset mallit**: saga, outbox, yhdyskäytävä ja
  perintöjärjestelmän uudistaminen (taito *Palveluarkkitehtuurit*).
- **Käyttö ja ylläpito**: kontit ja Kubernetes (taito *Kontit ja
  pilvi-infrastruktuuri*), käyttöönottoputket ja julkaisustrategiat
  (taito *Jatkuva integraatio ja toimitus*) sekä palvelutasot ja
  valvonta (taito *Palvelinympäristöt*).
- **Tietokannan valinta**: avain-arvo-, dokumentti- ja
  leveäsaraketietokannat ja niiden replikointimallit (taito
  *NoSQL-tietokannat*).
- **Organisaatio**: järjestelmän rakenne seuraa tiimien rakennetta, ja
  palvelurajat ovat myös omistajuusrajoja (taito *Tiimit ja
  organisaatiomallit*).
- **Tietoturva**: todennus palvelujen välillä, salaisuudet ja
  hyökkäyspinta (taito *Palveluarkkitehtuurin tietoturva*).
- **Harjoittelu**: suunnittele syötepalvelu, chat, tiedostojen
  synkronointi tai maksupalvelu samoilla vaiheilla, ja kokeile arviota
  pienellä toteutuksella kuten luvussa 12.

## Lähteet

Kirjat:

- Martin Kleppmann: *Designing Data-Intensive Applications*. O'Reilly
  2017. Replikointi, osiointi, transaktiot ja virrat; alan
  perusteos.
- Betsy Beyer, Chris Jones, Jennifer Petoff, Niall Richard Murphy
  (toim.): *Site Reliability Engineering*. O'Reilly 2016. Sekä Betsy
  Beyer ym. (toim.): *The Site Reliability Workbook*. O'Reilly 2018.
  SLO:t, virhebudjetit ja monen ikkunan kulumishälytykset. Molemmat
  luettavissa verkossa: sre.google/books.
- Michael T. Nygard: *Release It! Design and Deploy Production-Ready
  Software*, 2. painos. Pragmatic Bookshelf 2018. Vakausmallit:
  aikarajat, katkaisijat, laipiot.
- Neil J. Gunther: *Guerrilla Capacity Planning*. Springer 2007.
  Universaali skaalautuvuuslaki.
- Leonard Kleinrock: *Queueing Systems, Volume 1: Theory*. Wiley 1975.
- Brendan Gregg: *Systems Performance*, 2. painos. Addison-Wesley 2020.
  USE-menetelmä.

Artikkelit:

- Jeffrey Dean, Luiz André Barroso: The Tail at Scale. *Communications of
  the ACM* 56(2), 2013.
- John D. C. Little: A Proof for the Queuing Formula: L = λW.
  *Operations Research* 9(3), 1961.
- David Karger ym.: Consistent Hashing and Random Trees. *STOC* 1997.
- David G. Thaler, Chinya V. Ravishankar: Using Name-Based Mappings to
  Increase Hit Rates. *IEEE/ACM Transactions on Networking* 6(1), 1998.
- Michael Mitzenmacher: The Power of Two Choices in Randomized Load
  Balancing. *IEEE TPDS* 12(10), 2001.
- Daniel E. Eisenbud ym.: Maglev: A Fast and Reliable Software Network
  Load Balancer. *NSDI* 2016.
- Giuseppe DeCandia ym.: Dynamo: Amazon's Highly Available Key-value
  Store. *SOSP* 2007.
- Rajesh Nishtala ym.: Scaling Memcache at Facebook. *NSDI* 2013.
  Vuokrat, ryntäyksen esto ja alueiden välinen invalidointi.
- Nathan Bronson ym.: Metastable Failures in Distributed Systems.
  *HotOS* 2021. Sekä Lexiang Huang ym.: Metastable Failures in the Wild.
  *OSDI* 2022.
- Benjamin H. Sigelman ym.: Dapper, a Large-Scale Distributed Systems
  Tracing Infrastructure. Google, tekninen raportti 2010.

Verkossa:

- Marc Brooker: Timeouts, retries, and backoff with jitter, sekä David
  Yanacek: Using load shedding to avoid overload. *Amazon Builders'
  Library*, aws.amazon.com/builders-library.
- Tom Wilkie: The RED Method. Grafana Labs -blogi 2018. Brendan Gregg:
  The USE Method, brendangregg.com.
- W3C: *Trace Context*, suositus, w3.org/TR/trace-context.
- OpenTelemetry-dokumentaatio, opentelemetry.io.
- Prometheus: *Histograms and summaries* ja *Exposition formats*,
  prometheus.io/docs.
- PostgreSQL-dokumentaatio: *High Availability, Load Balancing, and
  Replication* ja *Write-Ahead Log* -asetukset,
  postgresql.org/docs/current. Esimerkit on ajettu versiolla 16.
- Redis-dokumentaatio: *Streams*, *Key eviction* ja *Lua scripting*,
  redis.io/docs.
- HAProxy: *Configuration Manual* ja *Management Guide* (Runtime
  API), docs.haproxy.org. Esimerkit on ajettu versiolla 2.8.
- psycopg 3 -dokumentaatio, psycopg.org/psycopg3/docs.
- Compose Specification, compose-spec.io.

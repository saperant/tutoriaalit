# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Aloita modulaarisena monoliittina.** Erota palvelu, kun sille on
   konkreettinen syy: oma tiimi ja julkaisutahti, poikkeava skaalaus tai
   vikojen eristys. Kirjaa syy päätöstietueeseen.
2. **Rajat kyvykkyyksien ja kielen mukaan**, ei kerrosten tai taulujen.
   Yksi transaktio muuttaa yhtä aggregaattia.
3. **Tieto on yhden palvelun omaa.** Muut kysyvät, kopioivat
   tapahtumista tai viittaavat tunnisteella; jaettua skeemaa ei ole.
4. **Jokaisella etäkutsulla on aikaraja**, ja jokainen muuttava kutsu
   on idempotentti, koska aikakatkaisun jälkeen lopputulos on
   tuntematon.
5. **Uudelleenyritys vain ohimeneviin virheisiin**, eksponentiaalisella
   odotuksella ja satunnaisuudella; katkaisija jokaiseen riippuvuuteen.
6. **Lyhyet synkroniset ketjut.** Viive on summa ja saatavuus tulo.
7. **Komennot jonoihin, tapahtumat aiheisiin**, ja jokainen kuluttaja
   on idempotentti.
8. **Outbox jokaiseen tilaa muuttavaan ja viestejä lähettävään
   palveluun.**
9. **Saga tilakoneena**: kompensoitavat vaiheet ensin, myöhästyneet ja
   toistetut viestit ohitetaan.
10. **Rajapinta kehittyy yhteensopivasti**, ja sopimustestit
    varmistavat sen jokaisessa käännöksessä.
11. **Vanha korvataan pala kerrallaan** julkisivun ja korruption
    estokerroksen avulla.

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| Modulaarinen monoliitti | rajat ilman verkon hintaa | 3 |
| Prosessinsisäinen tapahtuma | moduulien välinen kytkentä | 3 |
| Rajattu konteksti, kontekstikartta | missä rajat ovat | 4 |
| Julkaistu kieli | vakaa sopimus kontekstien välillä | 4 |
| Etäproseduurikutsu | etäkutsu paikallisen näköisenä | 5 |
| Suvaitsevainen lukija; laajenna ja supista | rajapinnan muutos rikkoo asiakkaat | 5 |
| Aikaraja, uudelleenyritys, katkaisija, laipio | hidas tai kaatunut riippuvuus | 6 |
| Kuorman pudotus | ylikuorma hidastaa kaikkia | 6 |
| Kilpailevat kuluttajat | työn jakaminen kopioille | 8 |
| Julkaise–tilaa | tapahtuma monelle tuntemattomalle | 8 |
| Idempotentti vastaanottaja (inbox) | vähintään kerran -toimitus | 8 |
| Kuolleiden kirjeiden jono | myrkkyviesti tukkii jonon | 8 |
| Kääntäjä, pilkkoja, kokooja, reititin, suodatin | viestien muokkaus ja reititys | 9 |
| Korrelaatiotunnus | osien kokoaminen, jäljitys | 9, 11 |
| Saga (orkestroitu, koreografioitu) | ei yhteistä transaktiota | 10 |
| Outbox, välittäjä, CDC | tila ja viesti eri järjestelmissä | 10 |
| API-yhdyskäytävä, BFF | sisäänkäynti ja käyttöliittymäkohtaiset tarpeet | 11 |
| Palveluverkko | itä–länsi-liikenteen yhteiset asiat | 11 |
| Kuluttajavetoinen sopimus | rajapinnan muutos rikkoo kuluttajan | 11 |
| Kuristajaviikuna, rinnakkaisajo | perintöjärjestelmän korvaaminen | 12 |
| Korruption estokerros | vieras malli leviää omaan koodiin | 4, 12 |
| Abstraktiolla haarauttaminen | sisäosan korvaaminen | 12 |

## Jatkotaidot

- *Palveluarkkitehtuurin tietoturva*: palvelujen välinen todennus
  (mTLS, työkuormien identiteetit), nollaluottamus, salaisuudet
  tuotannossa ja pääsynhallinta pilvessä.
- *Skaalautuvien järjestelmien suunnittelu*: kapasiteetti, välimuistit,
  replikointi, osiointi, havaittavuus ja saatavuuslaskelmat koko
  järjestelmälle.
- *Hajautetut järjestelmät*: konsistenssimallit, konsensus ja
  vikamallit, joiden varaan välittäjät ja tietokannat rakentuvat.
- *Tiimit ja organisaatiomallit*: Conwayn laki, tiimityypit ja
  omistajuus, joiden mukaan palvelujen rajat käytännössä asettuvat.
- *Jatkuva integraatio ja toimitus*: palvelukohtaiset julkaisuputket,
  julkaisustrategiat ja tietokantamuutokset ilman katkoa.
- *Integraatiotestaus ja Testcontainers*: palvelun testaaminen oikeaa
  välittäjää ja tietokantaa vasten.

## Lähteet ja dokumentaatio

- **Martin Fowler** (<https://martinfowler.com>): artikkelit
  *Microservices* (Lewis ja Fowler), *MonolithFirst*,
  *StranglerFigApplication*, *BoundedContext*, *CircuitBreaker*,
  *BranchByAbstraction* ja *What do you mean by "Event-Driven"?*.
- **Chris Richardson: Microservice Architecture**
  (<https://microservices.io>): mallikieli (saga, outbox, API gateway,
  database per service) perusteluineen.
- **Enterprise Integration Patterns** (<https://www.enterpriseintegrationpatterns.com>):
  Hohpen ja Woolfin mallien luettelo kaavioineen.
- **Pact-dokumentaatio** (<https://docs.pact.io>): kuluttajavetoiset
  sopimukset ja sopimusvälittäjä.
- **Resilience4j** (<https://resilience4j.readme.io>), **ArchUnit**
  (<https://www.archunit.org>), **Spring Modulith**
  (<https://spring.io/projects/spring-modulith>) ja **ActiveMQ
  Artemis** (<https://activemq.apache.org/components/artemis/>)
  -dokumentaatiot.
- **ADR**: Michael Nygardin alkuperäinen kirjoitus *Documenting
  Architecture Decisions* ja <https://adr.github.io>.
- **Kirjat:** Sam Newman, *Building Microservices* (2. painos) ja
  *Monolith to Microservices*. Eric Evans, *Domain-Driven Design*, ja
  Vlad Khononov, *Learning Domain-Driven Design*. Gregor Hohpe ja
  Bobby Woolf, *Enterprise Integration Patterns*. Chris Richardson,
  *Microservices Patterns*. Michael Nygard, *Release It!* Matthew
  Skelton ja Manuel Pais, *Team Topologies*. Neal Ford ym., *Software
  Architecture: The Hard Parts*.

### Työkalut

- **Kafka**, **RabbitMQ**, **ActiveMQ Artemis**, **NATS** ja pilvien
  jonopalvelut (SQS, Pub/Sub, Service Bus) viestinvälitykseen.
- **Debezium** muutostietojen kaappaukseen.
- **OpenTelemetry** hajautettuun jäljitykseen; **Jaeger** ja **Grafana
  Tempo** jälkien tarkasteluun.
- **Apache Camel** ja **Spring Integration** integraatiomalleihin.
- **Kong**, **Envoy**, **Spring Cloud Gateway** yhdyskäytäviksi;
  **Istio** ja **Linkerd** palveluverkoiksi.
- **Pact** ja **Spring Cloud Contract** sopimustestaukseen.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.

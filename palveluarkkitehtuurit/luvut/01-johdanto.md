# Johdanto {.runko-johdanto}

Palveluarkkitehtuuri vastaa kysymykseen, miten järjestelmä jaetaan
osiin ja miten osat keskustelevat. Ohjelmistoarkkitehtuuria on kuvattu
niiksi päätöksiksi, joita on kallis muuttaa jälkikäteen. Palvelujen
rajat, tiedon omistus ja viestintätapa ovat juuri sellaisia: väärin
vedetty raja maksaa vuosia, ja oikein vedetty raja antaa tiimeille
mahdollisuuden kehittää ja julkaista itsenäisesti.

Tutoriaali ei kannata mitään arkkitehtuurityyliä. Monoliitti,
modulaarinen monoliitti ja mikropalvelut ovat kaikki oikeita
vastauksia eri tilanteissa, ja jokaisella on hintansa. Tavoite on, että
osaat nimetä hinnan, mitata sen ja valita tietoisesti.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Taustapalvelut* (yhden Spring Boot -palvelun
rakenne, transaktiot, idempotenssiavain, outbox-taulu) ja *Kontit ja
pilvi-infrastruktuuri* (kontit, Kubernetesin peruskäsitteet). Niitä ei
toisteta.
Esimerkiksi idempotenssiavaimen toteutus on taustapalveluissa; tässä
katsotaan, mitä idempotenssi tarkoittaa, kun viestejä kulkee palvelujen
välillä.

Hajautettujen järjestelmien teoria (konsensus, replikointi,
konsistenssimallit) on taidossa *Hajautetut järjestelmät* ja
skaalautuvuus, välimuistit ja kapasiteetti taidossa *Skaalautuvien
järjestelmien suunnittelu*. Palvelujen välisen liikenteen suojaaminen
(mTLS, työkuormien identiteetit, nollaluottamus) on taidossa
*Palveluarkkitehtuurin tietoturva*, ja tiimien rakenne ja vastuut, joita
palvelujako heijastaa, taidossa *Tiimit ja organisaatiomallit*.

## Esimerkkijärjestelmä

Kaikki esimerkit käsittelevät samaa verkkokauppaa: asiakas tilaa
tuotteita, varasto varaa ne, maksupalvelu veloittaa, ja vahvistettu
tilaus päätyy toimitukseen ja laskutukseen. Kuva näyttää kaupan
palvelut ja niiden välisen liikenteen siinä muodossa, johon luvut 8–11
päätyvät; aiemmat luvut rakentavat sen pala kerrallaan.

```{.dot otsikko="Esimerkkijärjestelmä. Yhtenäinen nuoli on synkroninen kutsu, jonka vastausta kutsuja odottaa, ja katkoviiva viesti välittäjän kautta. Myynti ohjaa varausta ja veloitusta komennoilla; toimitus ja laskutus tilaavat myynnin tapahtumat."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.55;
  asiakas [label="asiakas", shape=plain, style=""];
  gw [label="yhdyskäytävä"];
  myynti [label="myynti", penwidth=1.6];
  varasto [label="varasto"]; maksut [label="maksut"];
  aihe [label="aihe\ntilaukset.tapahtumat", shape=cylinder, height=0.5];
  toimitus [label="toimitus"]; laskutus [label="laskutus"];
  asiakas -> gw [label="HTTP"];
  gw -> myynti;
  gw -> varasto;
  myynti -> varasto [label="saldo?"];
  myynti -> varasto [label="VARAA, VAPAUTA", style=dashed];
  myynti -> maksut [label="VELOITA", style=dashed];
  myynti -> aihe [label="TilausVahvistettu", style=dashed];
  aihe -> toimitus [style=dashed]; aihe -> laskutus [style=dashed];
}
```

Sama liiketoiminta toteutetaan eri tavoin, jotta erot näkyvät:

| Moduli | Luvut | Mitä näyttää |
|--------|-------|--------------|
| `modulaarinen` | 3 | yksi sovellus, moduulirajat testeinä, tapahtumat prosessin sisällä |
| `etakutsut` | 5–7, 11 | RPC, aikarajat, uudelleenyritys, katkaisija, kutsuketjut, sopimustestit, yhdyskäytävä |
| `viestit` | 8–10 | upotettu välittäjä, jonot ja aiheet, integraatiomallit, saga, outbox |
| `uudistus` | 12 | perintöjärjestelmä, korruption estokerros, kuristajaviikuna |

`etakutsut` ja `uudistus` eivät käytä kehystä: HTTP-palvelimet ovat
JDK:n `HttpServer`-olioita, jotta mekanismi näkyy. `modulaarinen` ja
`viestit` ovat Spring Boot -sovelluksia samalla pinolla kuin
taustapalveluissa (Java 21, Spring Boot 4.2, JdbcClient, H2).

## Pino ja valinnat

| Osa | Valinta | Miksi |
|-----|---------|-------|
| Moduulirajat | ArchUnit | Rajat testeinä; toimii kaikissa Java-projekteissa |
| Viestinvälittäjä | ActiveMQ Artemis upotettuna | Oikea JMS-välittäjä ilman Dockeria |
| Katkaisija | Resilience4j | Javan vakiintunut vikasietoisuuskirjasto |
| JSON | Jackson 3 | Spring Bootin oletus |
| Sopimustestit | oma pieni toteutus | Periaate näkyy; Pact ja Spring Cloud Contract mainitaan |

**Miksi Artemis eikä Kafka.** Kafka on yleisin tapahtumavirtojen
alusta, ja sen malli (pysyvä loki, osiot, kuluttajaryhmät) on luvussa 8
vertailuna. Esimerkeissä tarvitaan kuitenkin välittäjä, joka käynnistyy
testin sisällä sekunnissa ja toteuttaa klassiset jonot, aiheet ja
kuolleiden kirjeiden jonon. Artemis on Apache-säätiön JMS-välittäjä,
jonka Spring Boot osaa upottaa sovellukseen. Tuotannossa sama koodi
toimii erillisen Artemis- tai ActiveMQ-palvelimen kanssa, ja
RabbitMQ:lle tai Kafkalle muutokset rajoittuvat lähettäjään ja
kuuntelijoihin.

Esimerkeissä "palvelut" ajetaan testin ajaksi samassa prosessissa.
Tämä on opetuksellinen oikopolku: palvelut eivät silti kutsu toistensa
koodia eivätkä lue toistensa tauluja, vaan kaikki kulkee HTTP:n tai
viestien kautta. Siirto omiin prosesseihin ja kontteihin ei muuta
koodia, ainoastaan osoitteet.

## Esimerkkiprojekti

```text
esimerkit/
├── pom.xml          yhteinen: Spring Boot -versio, Java 21, modulit
├── mvnw, .mvn/      Maven Wrapper
├── Makefile         make = ./mvnw verify
├── modulaarinen/    luku 3
├── etakutsut/       luvut 5–7 ja 11
├── viestit/         luvut 8–10
└── uudistus/        luku 12
```

```text
make                                   # kaikki testit
./mvnw -pl viestit test -Dtest=SagaTest   # yksi testiluokka
```

Ensimmäinen ajo lataa Mavenin ja riippuvuudet; sen jälkeen koko
testisarja kestää alle minuutin. Kaikki tekstissä näytetty koodi on
projektin tiedostoista, ja testit varmistavat sen toiminnan.

## Arkkitehtuuripäätökset kirjataan

Arkkitehtuuripäätös kirjataan lyhyenä *arkkitehtuuripäätöstietueena*
(*architecture decision record*, ADR): konteksti, päätös, vaihtoehdot ja
seuraukset. Tietueet ovat versionhallinnassa koodin vieressä, ja
myöhemmin tuleva näkee, miksi raja on juuri siinä. Päätöstä ei poisteta
eikä muokata, kun se vanhenee, vaan uusi tietue korvaa sen.

```text
# 7. Laskutus kuuntelee myynnin tapahtumia

Tila: hyväksytty (korvaa päätöksen 3)

Konteksti: Laskutus kutsui myyntiä synkronisesti jokaisesta
tilauksesta, ja myynnin huolto pysäytti laskutuksen.

Päätös: Myynti julkaisee TilausVahvistettu-tapahtuman, ja laskutus
tallentaa tarvitsemansa tiedot itse.

Seuraukset: Laskutus on enintään sekunteja jäljessä. Tapahtuman
muoto on julkinen sopimus, jota muutetaan vain taaksepäin
yhteensopivasti.
```

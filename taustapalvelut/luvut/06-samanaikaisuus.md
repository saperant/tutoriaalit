# Samanaikaiset pyynnöt ja idempotenssi

Palvelin käsittelee pyyntöjä rinnakkain, ja verkko häviää vastauksia.
Kaksi kysymystä toistuu jokaisessa muuttavassa rajapinnassa: mitä
tapahtuu, kun kaksi pyyntöä muuttaa samaa tietoa yhtä aikaa, ja mitä
tapahtuu, kun sama pyyntö tulee kahdesti. Luvun lopussa roolit
vaihtuvat: kun palvelu itse kutsuu toista palvelua tai lähettää
viestin, se on se asiakas, jonka pyyntö voi kadota.

## Kilpatilanne: lue, tarkista, kirjoita

Naiivi saldon vähennys lukee saldon, tarkistaa sen sovelluksessa ja
kirjoittaa uuden arvon. Kun kaksi pyyntöä tekee tämän yhtä aikaa,
molemmat voivat lukea saldon 1, molemmat hyväksyä tilauksen ja
molemmat kirjoittaa 0: viimeinen kappale myytiin kahdesti. Korjaus
on tehdä tarkistus ja muutos samassa SQL-lauseessa. Tietokanta lukitsee
rivin päivityksen ajaksi, ja jälkimmäinen pyyntö näkee ensimmäisen
tuloksen.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/Varasto.java" osa="varasto"}
```

Testi lähettää kymmenen samanaikaista tilausta tuotteesta, jota on
kolme kappaletta. Täsmälleen kolme onnistuu:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="kilpailu"}
```

Sama tulos saataisiin lukitsemalla rivi ennen lukua
(`SELECT ... FOR UPDATE`, *pessimistinen lukitus*) tai
*Serializable*-eristystasolla ja uudelleenyrityksellä. Ehdollinen
päivitys on näistä yksinkertaisin ja nopein, kun koko sääntö mahtuu
yhteen lauseeseen.

## Optimistinen lukitus

Kaikki muutokset eivät ole yhden lauseen mittaisia. Ylläpitäjä avaa
tuotteen, miettii hintaa minuutin ja tallentaa. Rivin lukitseminen
minuutiksi ei tule kysymykseen. *Optimistinen lukitus* olettaa, että
ristiriidat ovat harvinaisia: rivillä on versionumero, ja päivitys
tehdään ehdolla `WHERE id = ? AND versio = ?`. Jos joku muu on ehtinyt
väliin, ehto ei osu riviin, ja Spring Data heittää
`OptimisticLockingFailureException`-poikkeuksen.

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteRepositoryTest.java" osa="optimistinen"}
```

Rajapinnassa versio kulkee HTTP:n omalla mekanismilla, kuten luvussa
2: `ETag` vastauksessa ja `If-Match` muutospyynnössä. Ohjain vaatii
ehdon (428 ilman sitä), ja vanhentunut ehto on 412:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="hinta"}
```

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="ehdollinen"}
```

Versio tarkistetaan kahdesti: palvelu vertaa asiakkaan versiota
luettuun (asiakkaan vanha näkymä), ja tallennus vertaa luettua
tietokannan nykyiseen (samanaikainen tallennus palvelun sisällä).

Huomaa, että varaston ehdollinen päivitys kasvattaa myös versiota.
Muuten hinnanmuutos, joka luki tuotteen ennen tilausta, kirjoittaisi
vanhan saldon takaisin, koska Spring Data JDBC tallentaa koko rivin.

## Idempotenssiavain

Asiakas lähettää tilauksen, ja yhteys katkeaa ennen vastausta. Menikö
tilaus perille? Asiakas ei tiedä. Jos se yrittää uudelleen, syntyy
ehkä kaksi tilausta; jos ei yritä, tilaus ehkä puuttuu. Ratkaisu on
*idempotenssiavain*: asiakas luo jokaiselle toiminnolle satunnaisen
avaimen (esim. UUID) ja lähettää sen otsakkeessa `Idempotency-Key`
jokaisessa yrityksessä. Palvelin muistaa avaimet ja palauttaa toistolle
saman tuloksen. Maksupalvelut kuten Stripe toimivat näin, ja IETF:ssä
on standardiehdotus otsakkeesta.

```{.dot otsikko="Idempotenssiavain: kadonneen vastauksen jälkeen toisto palauttaa saman tilauksen"}
digraph {
  nodesep=0.6; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=0.9, label="asiakas"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5;
  t1 [shape=box, width=0.9, label="palvelu"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5;
  t2 [shape=box, width=0.9, label="tietokanta"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3 -> t2_4 -> t2_5;
  {rank=same; t0; t1; t2;}
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0_4; t1_4; t2_4;}
  {rank=same; t0_5; t1_5; t2_5;}
  t0 -> t1 -> t2 [style=invis];
  t0_0 -> t1_0 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="POST /tilaukset, avain K"];
  t1_1 -> t2_1 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="tilaus 7 ja avain K"];
  t1_2 -> t0_2 [style=dashed, arrowhead=tee, color="#B4532A", constraint=false, label="201 katoaa matkalla", fontcolor="#B4532A"];
  t0_3 -> t1_3 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="POST uudelleen, avain K"];
  t1_4 -> t2_4 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="avain K on jo"];
  t1_5 -> t0_5 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="201, tilaus 7"];
}
```

Avain tallennetaan samassa transaktiossa kuin tilaus. Pääavain
`(asiakas, avain)` estää käsittelemästä samaa avainta kahdesti, myös
kahdessa samanaikaisessa pyynnössä:

```{.sql tiedosto="esimerkit/kauppa/src/main/resources/db/migration/V4__idempotenssi.sql" osa="v4"}
```

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/TilausPalvelu.java" osa="toisto"}
```

Ohjain katsoo ensin, onko avaimella jo tilaus. Jos kaksi pyyntöä
samalla avaimella kilpailee, jälkimmäisen lisäys törmää pääavaimeen,
sen transaktio peruuntuu (saldotkin), ja ohjain palauttaa ensimmäisen
tuloksen:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tilaus/TilausOhjain.java" osa="luonti"}
```

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tilaus/TilausIntegraatioTest.java" osa="idempotenssi"}
```

Tuotantototeutuksessa avaimille annetaan vanhenemisaika (esim. 24 h)
ja vanhat poistetaan eräajona. Lisäksi tallennetaan pyynnön tiiviste:
sama avain eri rungolla on asiakkaan virhe (422), ei toisto.

Eräajo on tavallisimmin ajastettu metodi (`@Scheduled`) samassa
palvelussa. Kun palvelusta on käynnissä useita instansseja, ajastin
laukeaa jokaisessa. Poisto vanhenemisajan perusteella on idempotentti,
joten rinnakkaiset ajot eivät haittaa. Työ, jota ei saa tehdä kahdesti
(lasku, muistutusviesti), tarvitsee lukon: tietokannan rivin, jonka
vain yksi instanssi saa varattua (`SELECT ... FOR UPDATE SKIP LOCKED`
tai kirjasto kuten ShedLock), tai alustan ajastimen, joka käynnistää
työn kerran (Kubernetesin CronJob).

## Toisen palvelun kutsuminen

Kun palvelu kutsuu toista palvelua (maksu, toimitus, sähköposti), se on
itse asiakas, ja kaikki edellä sanottu pätee toisin päin. Lisäksi
riippuvuuden hitaus muuttuu omaksi hitaudeksi: jos toimituspalvelu
jumittuu ja kutsu odottaa ikuisesti, jokainen odottava pyyntö varaa
säikeen ja pahimmillaan tietokantayhteyden, ja oma palvelu jumittuu
perässä. Suojia on kolme:

- **Aikaraja jokaiseen kutsuun**, yhteyden avaamiselle ja vastaukselle
  erikseen. Monen asiakaskirjaston oletus on odottaa rajatta.
- **Uudelleenyritys vain idempotentille kutsulle** ja vain tilapäiselle
  virheelle (5xx, aikaraja, yhteysvirhe), kasvavalla viiveellä,
  satunnaisuudella ja ylärajalla. Asiakkaan virhettä (4xx) ei toisteta,
  koska sama pyyntö epäonnistuisi samoin. Muuttava kutsu tehdään
  toistettavaksi idempotenssiavaimella.
- **Varavastaus**, jos tieto ei ole välttämätön: tuotesivu näytetään
  ilman toimitusaika-arviota mieluummin kuin ei lainkaan.

Springin `RestClient` on synkroninen HTTP-asiakas, joka sopii
virtuaalisäikeiden kanssa. Toimituspalvelun asiakas asettaa aikarajat
ja toistaa tilapäisen virheen:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/toimitus/ToimitusAsiakas.java" osa="asiakas"}
```

Testi käyttää valepalvelimena luvun 2 `HttpServer`-luokkaa. Kolme
tapausta: kaksi 503-vastausta ja sitten onnistuminen, palvelu, joka ei
vastaa lainkaan, ja 404, jota ei toisteta:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/toimitus/ToimitusAsiakasTest.java" osa="testit"}
```

Esimerkin kauppa ei tarvitse toimituspalvelua, joten asiakas on oma
luokkansa testeineen eikä osa tilauksen käsittelyä. Oikeassa
palvelussa kutsu tehdään transaktion ulkopuolella (luku 5), ja
aikarajat tulevat asetuksista.

Kun virheitä on paljon, pelkkä uudelleenyritys pahentaa tilannetta:
jokainen pyyntö odottaa aikarajan verran ja kuormittaa kaatunutta
palvelua. **Katkaisija** (*circuit breaker*) lopettaa kutsut hetkeksi
kokonaan ja vastaa heti virheellä tai varavastauksella. Javassa siihen
käytetään Resilience4j-kirjastoa. Katkaisija, laipiot ja kutsuketjun
aikabudjetti toteutetaan testattuina taidossa *Palveluarkkitehtuurit*.

## Kun tietokanta ei riitä: outbox

Tilauksen jälkeen halutaan usein lähettää viesti: vahvistussähköposti
tai tapahtuma viestijonoon. Jos viesti lähetetään transaktion sisällä
ja transaktio peruuntuu, viesti on lähtenyt turhaan; jos se lähetetään
sitoutuksen jälkeen ja palvelu kaatuu välissä, viesti katoaa.
*Outbox*-mallissa viesti kirjoitetaan samaan tietokantaan samassa
transaktiossa (taulu `outbox`), ja erillinen prosessi lähettää taulun
rivit ja merkitsee ne lähetetyiksi. Vastaanottajan on oltava
idempotentti, koska sama viesti voi tulla kahdesti.

Tässä tutoriaalissa outbox jää periaatteen tasolle, koska kaupalla ei
ole viestijonoa. Malli toteutetaan testattuna taidossa
*Palveluarkkitehtuurit*, ja jonojen mitoitus on taidossa
*Skaalautuvien järjestelmien suunnittelu*.

## Käytännössä

- **Tarkistus ja muutos samaan lauseeseen**, kun se on mahdollista:
  `UPDATE ... WHERE saldo >= ?` ja muutettujen rivien määrä.
- **Optimistinen lukitus ihmisten muokkauksiin**: versio sarakkeessa,
  `ETag` ja `If-Match` rajapinnassa, 412 ristiriidassa. Asiakas hakee
  uuden version ja näyttää käyttäjälle eron.
- **Idempotenssiavain jokaiseen POST-pyyntöön, jolla on rahallisia tai
  muita peruuttamattomia seurauksia.** Avaimen ja tuloksen tallennus
  samassa transaktiossa kuin itse toiminto.
- **Yksilöivä rajoite on paras lukko.** Tietokanta valvoo sen myös
  kilpatilanteessa ja usealla palvelininstanssilla; JVM:n `synchronized`
  ei suojaa, kun instansseja on kaksi.
- **Uudelleenyritys vain idempotentille toiminnolle**, eksponentiaalisella
  viiveellä ja satunnaisuudella (*jitter*), jotta kaatunutta palvelua
  ei kaadeta uudelleen yhtäaikaisilla yrityksillä.
- **Aikaraja jokaiseen lähtevään kutsuun**, eikä kutsuja transaktion
  sisällä. Päätä etukäteen, mitä käyttäjälle näytetään, kun riippuvuus
  ei vastaa.
- **Hinta:** ehdollinen päivitys pitää rivilukon vain lauseen ajan.
  Kuuma rivi (suosittu tuote kampanjassa) silti sarjallistaa kaikki
  tilaukset; ratkaisuja ovat varauserät, jonotus tai saldon jakaminen
  usealle riville.

## Itsearviointi

- Osaat tunnistaa lue–tarkista–kirjoita-kilpatilanteen ja korjata sen
  ehdollisella päivityksellä.
- Osaat toteuttaa optimistisen lukituksen tietokannassa ja rajapinnassa
  (`ETag`, `If-Match`, 412, 428).
- Osaat toteuttaa idempotenssiavaimen niin, että se toimii myös
  samanaikaisille toistoille.
- Osaat kutsua toista palvelua aikarajoin ja valita, mitkä virheet
  yritetään uudelleen ja mitkä ei.
- Osaat selittää, miksi viestin lähetys transaktion yhteydessä vaatii
  outbox-mallin.

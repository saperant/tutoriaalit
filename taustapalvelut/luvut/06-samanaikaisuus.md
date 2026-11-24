# Samanaikaiset pyynnöt ja idempotenssi

Palvelin käsittelee pyyntöjä rinnakkain, ja verkko häviää vastauksia.
Kaksi kysymystä toistuu jokaisessa muuttavassa rajapinnassa: mitä
tapahtuu, kun kaksi pyyntöä muuttaa samaa tietoa yhtä aikaa, ja mitä
tapahtuu, kun sama pyyntö tulee kahdesti.

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

## Kun tietokanta ei riitä: outbox

Tilauksen jälkeen halutaan usein lähettää viesti: vahvistussähköposti
tai tapahtuma viestijonoon. Jos viesti lähetetään transaktion sisällä
ja transaktio peruuntuu, viesti on lähtenyt turhaan; jos se lähetetään
sitoutuksen jälkeen ja palvelu kaatuu välissä, viesti katoaa.
*Outbox*-mallissa viesti kirjoitetaan samaan tietokantaan samassa
transaktiossa (taulu `outbox`), ja erillinen prosessi lähettää taulun
rivit ja merkitsee ne lähetetyiksi. Vastaanottajan on oltava
idempotentti, koska sama viesti voi tulla kahdesti. Malli ja
viestijonot käsitellään taidossa *Järjestelmäsuunnittelu*.

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
- Osaat selittää, miksi viestin lähetys transaktion yhteydessä vaatii
  outbox-mallin.

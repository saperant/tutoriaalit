# Tietokantojen skaalaus ja replikointi

Sovelluskerros skaalautuu lisäämällä palvelimia, mutta tila on
tietokannassa, ja tietokanta skaalautuu huonommin. Tavallinen kehitys
on: ensin isompi kone, sitten yhteysallas ja välimuisti, sitten
lukureplikat ja lopulta osiointi (luku 5). Tämä luku käsittelee
välivaiheita, joilla useimmat palvelut pärjäävät pitkään, ja niiden
seurauksia sovellukselle. Replikoinnin teoria, kuten kvoorumit ja
konsistenssimallit, on taidossa *Hajautetut järjestelmät*; tässä
katsotaan, miltä se näyttää PostgreSQLissa.

## Lukureplikat

PostgreSQLin suoratoistoreplikointi lähettää ensisijaisen palvelimen
WAL-lokin (*write-ahead log*) replikoille, jotka toistavat sen. Replikat
ottavat vastaan lukuja mutta eivät kirjoituksia. Luku:kirjoitus-suhteen
ollessa suuri replikat moninkertaistavat lukukapasiteetin. Esimerkki
luo replikan `pg_basebackupilla`:

```{.python tiedosto="esimerkit/jarjestelma/ymparisto.py" osa="replika"}
```

Oletuksena replikointi on asynkroninen: ensisijainen kuittaa
kirjoituksen ennen kuin replika on saanut sen. Replikalta luettu tieto
voi siksi olla vanhaa. Viive on tavallisesti millisekunteja, mutta
kuormassa, verkon häiriössä tai replikalla ajettavan pitkän kyselyn
aikana se voi kasvaa sekunteihin tai minuutteihin. Esimerkissä replika
asetetaan soveltamaan muutokset kahden sekunnin viiveellä
(`recovery_min_apply_delay`), jotta ilmiö näkyy joka ajolla:

```{.python tiedosto="esimerkit/luku07/replikointi.py" osa="vanhentunut"}
```

```{.tuloste tiedosto="esimerkit/luku07/replikointi.odotettu"}
```

Ensisijainen näyttää uuden saldon 50, replika vielä vanhan 100.
Käyttäjälle tämä näkyy niin, että hän tallentaa muutoksen, sivu
latautuu uudelleen replikalta, ja muutos on kadonnut.

## Lue omat kirjoituksesi

Useimmat sovellukset sietävät vanhentuneen luvun muiden käyttäjien
datasta mutta eivät omastaan. *Lue omat kirjoituksesi* (*read your
writes*) on istuntotakuu, joka korjaa juuri tämän. Tapoja on kolme:

- **Lue ensisijaiselta jonkin aikaa kirjoituksen jälkeen.** Istuntoon
  merkitään kirjoitusaika, ja seuraavat luvut esimerkiksi 10 sekunnin
  ajan ohjataan ensisijaiselle. Yksinkertaista, mutta raja on arvaus.
- **Lue ensisijaiselta käyttäjän omat tiedot.** Profiilisivu, asetukset
  ja ostoskori luetaan aina ensisijaiselta, muu replikoilta.
- **Odota, että replika on saavuttanut kirjoituksen.** Kirjoituksen
  jälkeen otetaan talteen WAL-sijainti, ja replikalta luetaan vasta,
  kun se on soveltanut muutokset siihen asti:

```{.python tiedosto="esimerkit/luku07/replikointi.py" osa="omat"}
```

Viimeinen tapa on tarkin, ja se toimii myös usean palvelun välillä, kun
sijainti kulkee pyynnön mukana. Hinta on odotus, jos replika on jäljessä;
sovellus voi silloin lukea ensisijaiselta.

Replika kieltäytyy kirjoituksista (`25006 ReadOnlySqlTransaction`), joten
sovelluksen on tiedettävä, kumpaa yhteyttä se käyttää. Tavallinen ratkaisu
on kaksi yhteysallasta, kirjoitus- ja lukuallas, ja tietokerros, joka
valitsee altaan kyselyn mukaan.

## Synkroninen replikointi

Synkroninen replikointi poistaa vanhentuneet luvut ja kuitattujen
kirjoitusten katoamisen, mutta jokainen kirjoitus odottaa replikaa.
PostgreSQLissa tasoja on useita: `remote_write` ja `on` odottavat, että
replika on vastaanottanut tai kirjoittanut WAL:n, ja `remote_apply`, että
replika on myös soveltanut sen, jolloin replikalta luettu tieto on
tuore:

```{.python tiedosto="esimerkit/luku07/replikointi.py" osa="synkroninen"}
```

Kirjoitus odotti replikan viiveen ajan, ja sen jälkeen replika näytti
heti uuden arvon. Tämä on PACELC:n *else*-haara käytännössä: ilman
verkon jakautumistakin valitaan latenssin ja konsistenssin välillä.
Saman konesalin sisällä synkroninen replikointi maksaa millisekunnin
tai pari kirjoitusta kohden, mantereiden välillä satoja millisekunteja.
Tavallinen kompromissi on yksi synkroninen replika lähellä (pysyvyys
vikaantumisessa) ja asynkronisia replikoita kauempana (luvut ja
katastrofista palautuminen).

## Yhteysaltaat

PostgreSQL käynnistää jokaiselle yhteydelle oman prosessin, ja yhteyden
avaus maksaa millisekunteja. Satojen sovelluspalvelinten tuhannet
yhteydet kuluttavat kannan muistin ja lukkokilpailun, vaikka suurin osa
niistä on käyttämättä. Siksi yhteydet kierrätetään altaassa. Luvun 12
palvelun allas:

```{.python tiedosto="esimerkit/jarjestelma/lyhyt.py" osa="allas"}
```

Altaan koko on samalla kannan rinnakkaisuuden raja. Littlen lain
mukaan tarvitaan kyselyt sekunnissa kertaa kyselyn kesto (luku 3):
1 000 kyselyä sekunnissa, 5 ms kukin, pitää kesken keskimäärin viittä
yhteyttä. Kun palvelimia on paljon, väliin lisätään erillinen
yhteyksien kokoaja (*connection pooler*), kuten PgBouncer, joka jakaa
pienen joukon kantayhteyksiä suurelle joukolle asiakkaita.

## Indeksit, denormalisointi ja esilaskenta

Ennen replikoita ja osiointia kannattaa varmistaa, että kyselyt ovat
halpoja. Indeksit ja kyselysuunnitelmat käsitellään taidossa *SQL ja
relaatiotietokannat*. Järjestelmätasolla lisäkeinoja ovat:

- **Denormalisointi.** Usein yhdessä luettava data tallennetaan
  yhteen, esimerkiksi tilauksen summa tilausriville eikä laskettuna
  joka kerta riveistä. Hinta on päivitysten ylläpito.
- **Esilaskenta.** Raskaat koosteet (etusivun suosituimmat, käyttäjän
  aikajana) lasketaan kirjoitettaessa tai taustalla, ei luettaessa.
  Syötepalvelun *fan-out on write* kirjoittaa uuden viestin jokaisen
  seuraajan aikajanalle; julkkiksille, joilla on miljoonia seuraajia,
  aikajana kootaan lukiessa (*fan-out on read*).
- **CQRS.** Kirjoitus- ja lukumalli erotetaan: kirjoitukset normaaliin
  kantaan, ja tapahtumista rakennetaan lukuun optimoitu näkymä esim.
  hakuindeksiin (taito *Palveluarkkitehtuurit*).

## SQL vai NoSQL

Valinta tehdään datan ja kyselyjen mukaan, ei muodin:

| Tarve                                      | Tyypillinen valinta                         |
|--------------------------------------------|---------------------------------------------|
| suhteita, liitoksia, transaktioita, ad hoc -kyselyjä | relaatiotietokanta (PostgreSQL, MySQL) |
| suuri avain–arvo-kuorma, tunnetut hakupolut | avain–arvo tai laajasarakkeinen (DynamoDB, Cassandra) |
| dokumentit, joiden rakenne vaihtelee | dokumenttikanta tai PostgreSQLin JSONB |
| aikasarjat | aikasarjakanta tai osioitu taulu |
| tekstihaku | hakuindeksi (OpenSearch), tietokanta lähteenä |
| analytiikka suurista määristä | sarakepohjainen (ClickHouse, BigQuery) |
| maailmanlaajuinen vahva konsistenssi | NewSQL (Spanner, CockroachDB) |

Relaatiotietokanta on hyvä oletus. NoSQL-kantojen skaalautuvuus perustuu
siihen, että ne luopuvat liitoksista ja osioiden välisistä
transaktioista ja vaativat suunnittelemaan avaimet kyselyjen mukaan
etukäteen. Jos kyselyt eivät ole tiedossa, joustavuus on arvokkaampaa
kuin skaalautuvuus, jota ei vielä tarvita.

## Käytännössä

- **Mittaa replikointiviive ja hälytä siitä.** `pg_stat_replication`
  ensisijaisella ja `pg_last_xact_replay_timestamp()` replikalla kertovat
  viiveen.
- **Päätä, mitkä luvut saavat olla vanhoja.** Oma data ensisijaiselta tai
  WAL-sijainnin kanssa, muu replikoilta.
- **Käytä yhteysallasta aina.** Mitoita se Littlen lailla, ja lisää
  PgBouncer, kun palvelimia on paljon.
- **Yksi synkroninen replika lähelle.** Se estää kuitattujen
  kirjoitusten katoamisen ensisijaisen kaatuessa kohtuullisella hinnalla.
- **Automatisoi vaihto ja testaa se.** Replika on hyödytön
  vikaantumisessa, jos sen ylentäminen on käsityötä, jota ei ole
  kokeiltu (Patroni, pilven hallinnoidut kannat).
- **Aloita relaatiotietokannasta.** Vaihda tai lisää erikoistunut kanta,
  kun tunnet kuorman ja kyselyt.

## Itsearviointi

- Osaat luoda PostgreSQL-lukureplikan ja selittää, miksi asynkronisen
  replikan luku voi olla vanhentunut.
- Osaat toteuttaa lue omat kirjoituksesi -takuun ohjaamalla luvut
  ensisijaiselle tai odottamalla WAL-sijaintia replikalla.
- Osaat kertoa synkronisen replikoinnin tasot ja niiden latenssihinnan.
- Osaat mitoittaa yhteysaltaan ja perustella SQL- tai NoSQL-kannan
  valinnan kyselyjen perusteella.

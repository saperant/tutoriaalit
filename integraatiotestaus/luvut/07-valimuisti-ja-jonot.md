# Välimuisti ja viestijonot

Tietokanta on integraatiotestien tavallisin kohde, mutta sama tapa
toimii kaikille palveluille, joille on konttikuva: Redis, RabbitMQ,
Kafka, Elasticsearch, S3-yhteensopiva MinIO tai pilvipalvelujen
emulaattori LocalStack. Tässä luvussa varastopalvelun hintavälimuisti ja
varaustapahtumat testataan oikeaa Redisiä vasten.

## Välimuistin testaaminen

Hintavälimuisti noudattaa *cache-aside*-mallia: ensin katsotaan
välimuistista, ja jos arvoa ei ole, se haetaan lähteestä ja tallennetaan
vanhenemisajan (TTL) kanssa.

```{.python tiedosto="esimerkit/varasto/valimuisti.py" osa="valimuisti"}
```

Yksikkötestissä Redisin voisi korvata sanakirjalla, mutta silloin
testaamatta jäisi juuri se, mikä välimuistissa menee rikki: avainten
muoto, vanhenemisaika, serialisointi ja tavut vastaan merkkijonot.
Integraatiotesti käyttää oikeaa Redisiä ja lähteenä vakoilijaa, joka
laskee haut:

```{.python tiedosto="esimerkit/testit/test_valimuisti.py" osa="valimuistitestit"}
```

Ensimmäinen testi tarkistaa kolme asiaa, jotka väärennös olisi helposti
hyväksynyt väärin: kirjainkoko ei tee eri avainta, toinen haku ei mene
lähteeseen, ja avaimella on oikeasti vanhenemisaika (Redisin `TTL`).
Puuttuva vanhenemisaika on tyypillinen tuotantovika: välimuisti kasvaa
rajatta ja palvelee vanhaa hintaa ikuisesti.

Vanhenemisen odottaminen testissä (`sleep(61)`) olisi hidas ja epävakaa.
Testi tarkistaa, että vanhenemisaika on asetettu; Redis huolehtii siitä,
että avain vanhenee.

## Viestijono: vähintään kerran

Varaustapahtumat julkaistaan Redis Streamsiin, josta laskutus lukee ne
kuluttajaryhmänä. Kuluttaja kuittaa viestin vasta käsittelyn jälkeen.
Jos se kaatuu ennen kuittausta, viesti jää odottamaan, ja toinen
kuluttaja voi ottaa sen haltuunsa. Tämä on *vähintään kerran*
-toimitusta: viesti voi tulla kahdesti, joten käsittelyn on oltava
idempotentti (tapahtuman tunnus kirjataan, ja kaksoiskappale ohitetaan).

```{.python tiedosto="esimerkit/varasto/tapahtumat.py" osa="julkaise"}
```

```{.python tiedosto="esimerkit/varasto/tapahtumat.py" osa="kasittele"}
```

Vikatilanteen kulku näkyy, kun sen ajaa vaihe vaiheelta oikeassa
Redisissä:

```{.python tiedosto="esimerkit/luku07/odottavat.py" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/luku07/odottavat.odotettu"}
```

Testi tekee saman tarkistuksin:

```{.python tiedosto="esimerkit/testit/test_tapahtumat.py" osa="tapahtumatestit"}
```

Tällaista testiä ei voi kirjoittaa ilman oikeaa välityspalvelinta.
Kuittaukset, odottavat viestit ja haltuunotto ovat Redisin
käyttäytymistä, eivät oman koodin. Testi varmistaa, että oma koodi
käyttää niitä oikein: kuittaa vasta onnistuneen käsittelyn jälkeen ja
ottaa kaatuneen kuluttajan viestit haltuun. Vanhenemisraja on testissä
nolla millisekuntia, jotta testin ei tarvitse odottaa; tuotannossa se on
sekunteja tai minuutteja.

## Muut välityspalvelimet

Samat tarkistukset sopivat muihin jonoihin, mutta niiden käsitteet
eroavat:

| Välittäjä | Kuittaus | Uudelleentoimitus | Testikontti |
|--------------|------------|------------------------|-----------------|
| Redis Streams | `XACK` | `XAUTOCLAIM`, `XCLAIM` | `redis` |
| RabbitMQ | ack/nack | nack tai yhteyden katkeaminen | `rabbitmq` |
| Kafka | siirtymän commit | kuluttaja lukee siirtymästä | `kafka`, Redpanda |
| SQS | viestin poisto | näkyvyysaikakatkaisu | LocalStack |

Kafka-kontti on raskas (satoja megatavuja, käynnistys sekunteja), joten
testeissä käytetään usein Kafka-yhteensopivaa Redpandaa. Kumpaa tahansa
käytetäänkin, testin rakenne on sama: julkaise, kuluta, simuloi kaatuminen
ennen kuittausta ja tarkista, että viesti käsitellään kerran.

## Asynkronisuus testissä

Viestijonotesteissä on yksi lisävaikeus: kuluttaja käsittelee viestit
eri säikeessä tai prosessissa kuin testi. Testin on odotettava, että
käsittely on tapahtunut, eikä nukuttava arvattua aikaa. Hyvä malli on
odottaa ehtoa aikarajan kanssa (`odota_kunnes(lambda: ...,
aikaraja=5)`), jolloin testi on nopea onnistuessaan ja antaa selkeän
virheen epäonnistuessaan. Varastopalvelun testeissä kuluttaja ajetaan
testin omassa säikeessä, joten odottamista ei tarvita.

## Käytännössä

- Testaa välimuistista avainten muoto, vanhenemisaika ja serialisointi
  oikeaa palvelinta vasten. Logiikan (milloin välimuistiin mennään)
  voi testata väärennöksellä.
- Tyhjennä välimuisti tai jono jokaisen testin alussa, jotta testit eivät
  näe toistensa avaimia.
- Testaa jonoista vikatilanne: kaatuminen ennen kuittausta ja
  kaksoistoimitus. Onnistuneen tapauksen testaaminen ei kerro paljon.
- Odota asynkronista käsittelyä ehdolla ja aikarajalla, älä kiinteällä
  viiveellä.

## Itsearviointi

- Osaat testata välimuistin oikeaa Redisiä vasten ja tarkistaa
  vanhenemisajan odottamatta sitä.
- Osaat selittää vähintään kerran -toimituksen ja idempotentin
  käsittelyn.
- Osaat kirjoittaa testin, joka simuloi kuluttajan kaatumisen ennen
  kuittausta ja varmistaa viestin käsittelyn.
- Osaat valita jonon testikontin ja tunnistaa, miten kuittaus ja
  uudelleentoimitus eroavat välittäjien välillä.

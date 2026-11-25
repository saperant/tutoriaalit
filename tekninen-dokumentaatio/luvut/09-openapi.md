# HTTP-rajapinnan kuvaus

HTTP-rajapinnan käyttäjä ei näe palvelun koodia eikä usein käytä edes
samaa ohjelmointikieltä. Hänen viitteensä on rajapinnan kuvaus: mitä
polkuja on, mitä niille lähetetään ja mitä ne vastaavat. OpenAPI on
tälle kuvaukselle vakiintunut koneluettava muoto.

## Kuvaus on sopimus

OpenAPI-kuvaus on YAML- tai JSON-tiedosto, jossa on kolme osaa:
yleistiedot, polut toimintoineen ja uudelleenkäytettävät skeemat.
Lukeman lisääminen esimerkkipalveluun:

```{.yaml tiedosto="esimerkit/openapi/saa.yaml" osa="post"}
```

Toiminnolla on tunniste (`operationId`), josta asiakaskirjastojen
generaattorit tekevät funktion nimen, yhden virkkeen tiivistelmä ja
jokaiselle tilakoodille oma vastauksensa. Virhevastaus on kuvattu
yhtä tarkasti kuin onnistunut: rajapinnan käyttäjä kirjoittaa koodia
nimenomaan virheiden varalle.

Skeema kuvaa tietorakenteen. OpenAPI 3.1:ssä skeemat ovat JSON Schemaa:

```{.yaml tiedosto="esimerkit/openapi/saa.yaml" osa="lukema"}
```

Skeema kertoo saman kuin luvun 7 docstring, mutta koneelle: kentät,
tyypit, rajat ja se, että kosteus saa olla `null`. Kuvaus
(`description`) kertoo ihmiselle sen, mitä tyyppi ei kerro: yksikön ja
merkityksen. `additionalProperties: false` tekee skeemasta tiukan,
jolloin ylimääräinen kenttä on virhe eikä hiljaa ohitettu kirjoitusvirhe.

Samasta kuvauksesta syntyy selattava viite (Swagger UI, Redoc),
asiakaskirjastoja ja palvelinrunkoja (openapi-generator),
testipyyntöjä ja jäljitelmäpalvelimia. Siksi kuvauksen laatu
kertautuu: epämääräinen skeema tuottaa epämääräisen asiakaskirjaston.

## Kuvaus ensin vai koodi ensin

Kuvaus voidaan kirjoittaa käsin ja toteuttaa sen mukaan, tai se
voidaan tuottaa toteutuksesta. Taito *Taustapalvelut* käsittelee
valinnan palvelun toteuttajan näkökulmasta. Dokumentaation kannalta
ero on tämä:

| Tapa | Totuuden lähde | Vahvuus | Riski |
|---------------|----------------|-----------------------------|--------------------------|
| kuvaus ensin | YAML-tiedosto | rajapinta suunnitellaan ja katselmoidaan ennen koodia | toteutus ajautuu kuvauksesta |
| koodi ensin | palvelun koodi | kuvaus on aina toteutuksen mukainen | rajapinta muuttuu vahingossa koodin mukana |

Kummassakin tapauksessa tarvitaan tarkistus, joka sitoo kuvauksen ja
toteutuksen yhteen. Koodi ensin -tavassa generoitu kuvaus tallennetaan
versionhallintaan ja sen muutos katselmoidaan. Kuvaus ensin -tavassa
toteutus testataan kuvausta vasten, kuten seuraavaksi.

## Kuvaus toteutusta vasten

Esimerkkipalvelun käsittelijä on tavallinen funktio, joka saa
pyynnön osat ja palauttaa vastauksen:

```{.python tiedosto="esimerkit/saa/palvelu.py" osa="kasittele"}
```

Koska käsittelijä ei tarvitse verkkoa, kuvauksen voi tarkistaa sitä
vasten suoraan. Tarkistin tekee kolme asiaa: varmistaa, että tiedosto
on kelvollista OpenAPI:a, vertaa kuvauksen reittejä toteutuksen
reitteihin ja ajaa jokaisen kuvauksen esimerkkipyynnön.
Esimerkkipyynnöt poimitaan kuvauksesta:

```{.python tiedosto="esimerkit/openapi/tarkista.py" osa="kutsut"}
```

Jokaisen vastauksen tilakoodin pitää olla kuvattu, ja rungon pitää
kelvata tilakoodin skeemaan:

```{.python tiedosto="esimerkit/openapi/tarkista.py" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/openapi/tarkista.odotettu"}
```

Kuvauksen esimerkit ovat siis testitapauksia: sama pyyntö, jonka
lukija kopioi viitteestä, on ajettu toteutusta vasten. Esimerkki, joka
ei toimi, ei pääse dokumentaatioon.

Kun skeeman kentän nimi muutetaan mutta toteutus jää ennalleen,
tarkistus epäonnistuu:

```{.makefile tiedosto="esimerkit/Makefile" osa="openapi"}
```

```{.tuloste tiedosto="esimerkit/openapi/vanhentunut.odotettu"}
```

Oikeassa palvelussa sama tarkistus tehdään HTTP:n yli käynnissä
olevaa palvelua vasten. Valmiita työkaluja ovat esimerkiksi
Schemathesis, joka generoi skeemoista myös satunnaisia pyyntöjä, ja
Dredd. Palvelujen välistä sopimustestausta käsittelee taito
*Integraatiotestaus ja Testcontainers*.

## Muutokset ja versiot

Julkaistu rajapinta on lupaus. Kuvauksen muutokset jakautuvat kahteen
ryhmään:

| Muutos | Yhteensopiva? |
|----------------------------------------------|---------------|
| uusi polku tai toiminto | kyllä |
| uusi valinnainen kenttä pyyntöön | kyllä |
| uusi kenttä vastaukseen | kyllä, jos asiakkaat ohittavat tuntemattomat kentät |
| kentän poisto tai uudelleennimeäminen | ei |
| valinnaisen kentän muuttaminen pakolliseksi | ei |
| arvoalueen kaventaminen | ei |

Yhteensopimattomasta muutoksesta kerrotaan etukäteen: kenttä tai
toiminto merkitään kuvauksessa vanhentuneeksi (`deprecated: true`),
muutoslokiin kirjataan poistumisen ajankohta (luku 2), ja vasta
seuraava pääversio poistaa sen. Kuvaustiedostojen erotuksen voi
tarkistaa koneellisesti (esimerkiksi oasdiff), jolloin vahingossa
tehty rikkova muutos pysähtyy putkeen.

Viestipohjaisille rajapinnoille vastaava muoto on AsyncAPI ja
gRPC-palveluille Protocol Buffers -määrittely. Periaate ei muutu:
yksi koneluettava kuvaus, josta syntyvät viite ja koodi ja jota vasten
toteutus tarkistetaan.

## Käytännössä

- **Kuvaus versionhallintaan palvelun viereen.** Rajapinnan muutos
  näkyy katselmoinnissa YAML-rivien muutoksena, ei vasta asiakkaan
  virheilmoituksena.
- **Esimerkki jokaiselle toiminnolle.** Lukija aloittaa esimerkistä,
  ja esimerkki on halvin testi.
- **Kuvaa virheet.** Jokainen tilakoodi, jonka palvelu voi palauttaa,
  ja virherungon muoto.
- **Tiukat skeemat.** Pakolliset kentät, arvoalueet ja
  `additionalProperties: false` tekevät kuvauksesta tarkistettavan.
- **Tekstiä tiivistelmää pidemmälle.** `description`-kentät tukevat
  Markdownia; käytä niitä yksiköihin, sivutukseen ja
  käyttöoikeuksiin.
- **Opas erikseen.** Viite kertoo, mitä toiminnot tekevät. Se ei
  kerro, missä järjestyksessä niitä kutsutaan tavallisessa
  käyttötapauksessa; se on oppaan tehtävä.

## Itsearviointi

- Osaat lukea ja kirjoittaa OpenAPI-kuvauksen toiminnon
  pyyntöineen, vastauksineen ja skeemoineen.
- Osaat verrata kuvaus ensin- ja koodi ensin -tapoja dokumentaation
  luotettavuuden kannalta.
- Osaat kuvata, miten rajapintakuvaus tarkistetaan toteutusta vasten.
- Osaat luokitella rajapinnan muutoksen yhteensopivaksi tai
  rikkovaksi ja kertoa, miten rikkova muutos viestitään.

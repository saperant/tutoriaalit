# Rajapinnan suunnittelu

Rajapinta on sopimus, jota palvelu ei voi muuttaa yksin: kun mobiili-
sovelluksen vanha versio on käyttäjien puhelimissa, sen käyttämät
kentät ja polut on pidettävä toiminnassa vuosia. Siksi rajapinta
suunnitellaan ensin ja sen muutokset tehdään taaksepäin
yhteensopivasti. Tämä luku käy läpi kaupan rajapinnan rakenteen;
toteutus seuraa luvuissa 4–9. Luvun koodiotteet ovat jo valmiista
Spring-ohjaimesta, koska sopimus näkyy niissä tarkimmin. Merkinnät
(`@GetMapping`, `@RequestParam`, `@RestControllerAdvice`) selitetään
luvussa 4; tässä riittää lukea niistä polku, parametrit ja palautettava
tyyppi.

## Resurssit ja polut

REST-tyylissä polku nimeää *resurssin* (substantiivi), ja metodi kertoo,
mitä sille tehdään. Kaupan rajapinta:

| Pyyntö | Merkitys | Oikeus |
|--------|----------|--------|
| `GET /api/v1/tuotteet?sivu=0&koko=20` | tuotelista sivuittain | kaikki |
| `GET /api/v1/tuotteet/{id}` | yksi tuote, `ETag` | kaikki |
| `POST /api/v1/tuotteet` | uusi tuote | ylläpitäjä |
| `PUT /api/v1/tuotteet/{id}/hinta` | hinnan muutos, `If-Match` | ylläpitäjä |
| `POST /api/v1/tilaukset` | uusi tilaus, `Idempotency-Key` | asiakas |
| `GET /api/v1/tilaukset` | omat tilaukset | asiakas |
| `GET /api/v1/tilaukset/{id}` | yksi tilaus | omistaja, ylläpitäjä |
| `GET /api/v1/raportit/myynti` | myydyimmät tuotteet | ylläpitäjä |

Nyrkkisääntöjä:

- Monikko kokoelmalle (`/tuotteet`), tunniste yksittäiselle
  (`/tuotteet/42`). Verbit pois polusta: ei `/haeTuote?id=42`.
- Hierarkia vain, kun lapsi ei ole olemassa ilman vanhempaa
  (`/tilaukset/7/rivit`). Muuten suodatus kyselyparametrilla
  (`/tilaukset?asiakas=aino`).
- Toiminto, joka ei ole luonteva tilan muutos, mallinnetaan
  alaresurssina: `PUT /tuotteet/42/hinta` tai `POST /tilaukset/7/peruutus`.
  Erillinen hinta-resurssi on myös valtuutuksen ja lokituksen kannalta
  selkeämpi kuin yleinen PATCH.

## Esitysmuoto on eri asia kuin tietomalli

Ohjain ei palauta tietokantaentiteettiä vaan erillisen *DTO:n* (*data
transfer object*). Muuten jokainen tietokannan sarake vuotaisi
rajapintaan, ja skeeman muutos rikkoisi asiakkaat. Recordit ovat
tähän sopivia: muuttumattomia, ja Jackson muuntaa ne JSONiksi ja
takaisin ilman lisäkoodia.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="dto"}
```

Muotoilusopimukset kirjataan kerran ja noudatetaan kaikkialla:

- **Raha** kokonaislukuna pienimmässä yksikössä (`hintaSentteina`)
  tai merkkijonona (`"12.90"`) ja valuutta erikseen. JSONin luku on
  JavaScriptissä liukuluku, eikä `0.1 + 0.2` ole `0.3`.
- **Ajat** ISO 8601 -muodossa UTC:nä (`2026-11-24T08:15:00Z`).
  Aikavyöhyke muunnetaan näyttäessä, ei tallentaessa.
- **Tunnisteet**: sisäinen juokseva numero paljastaa liiketoiminnan
  määriä ja kutsuu arvaamaan (`/tilaukset/1001`). Julkisessa
  rajapinnassa käytetään usein satunnaista UUID:tä; tässä
  tutoriaalissa omistajuuden tarkistus (luku 8) estää vierailta
  tilauksilta.
- **Nimet** yhdellä tyylillä (`camelCase` JSONissa). Puuttuva kenttä ja
  `null` tarkoittavat samaa, ellei toisin sovita.

## Sivutus

Lista palautetaan aina sivuina; rajaton lista kaatuu ennen pitkää
muistiin tai aikakatkaisuun. Ohjain rajaa pyydetyn sivukoon
asetuksen mukaan, joten asiakas ei voi pyytää miljoonaa riviä:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="listaus"}
```

*Sivunumerosivutus* (`sivu`, `koko`, kokonaismäärä) on helppo ja
sopii hallintanäkymiin. Se on kuitenkin hidas syvällä
(`OFFSET 100000` lukee ja hylkää 100 000 riviä), ja rivit voivat
siirtyä sivulta toiselle, kun listaan lisätään. Suurissa ja
päättymättömissä listoissa käytetään *avainsivutusta* (*keyset* tai
*cursor pagination*): asiakas saa vastauksen mukana kohdistimen,
esimerkiksi viimeisen rivin `(nimi, id)`, ja seuraava sivu haetaan
ehdolla `WHERE (nimi, id) > (:nimi, :id)`. Taito *SQL ja
relaatiotietokannat* näyttää indeksien yhteydessä, miksi tämä on
nopeaa.

## Virheet: RFC 9457

Virheillä on yksi muoto koko rajapinnassa. Standardi *Problem Details
for HTTP APIs* (RFC 9457, aiemmin RFC 7807) määrittelee sisältötyypin
`application/problem+json` ja kentät:

| Kenttä | Sisältö |
|--------|---------|
| `type` | virhetyypin URI; asiakas haarautuu tämän mukaan |
| `title` | lyhyt ihmisluettava otsikko |
| `status` | HTTP-tilakoodi |
| `detail` | tämän tapauksen kuvaus |
| `instance` | pyynnön polku tai tunniste |
| muut | koneluettavat lisätiedot, esim. `tuote` |

Spring tuottaa omat virheensä (validointi, väärä sisältötyyppi, puuttuva
polku) tässä muodossa asetuksella `spring.mvc.problemdetails.enabled`.
Sovelluksen omat poikkeukset muunnetaan samaan muotoon
*ohjainneuvojassa* (`@RestControllerAdvice`):

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/virheet/Ongelmat.java" osa="ongelmat"}
```

Saldovirhe näyttää asiakkaalle tältä; integraatiotesti luvussa 6
tarkistaa kentät:

```text
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{"type": "https://kauppa.example/ongelmat/saldo",
 "title": "Conflict", "status": 409,
 "detail": "tuotteen 3 saldo ei riitä",
 "tuote": 3, "pyydetty": 5}
```

Virheviestiin ei koskaan laiteta pinojälkeä, SQL-lausetta tai
sisäistä luokan nimeä. Ne kuuluvat lokiin, jossa korrelaatiotunnus
(luku 9) yhdistää ne pyyntöön.

## Versiointi ja yhteensopivuus

Taaksepäin yhteensopivia muutoksia ovat uuden kentän, uuden
valinnaisen parametrin ja uuden polun lisääminen. Rikkovia ovat kentän
poisto tai uudelleennimeäminen, tyypin tai merkityksen muutos ja
pakollisen kentän lisääminen pyyntöön. Asiakas puolestaan on
*suvaitseva lukija* (*tolerant reader*): se ohittaa tuntemattomat
kentät eikä oleta kenttien järjestystä.

Rikkova muutos julkaistaan uutena versiona, ja vanhaa ylläpidetään
sovitun ajan. Polussa oleva versio (`/api/v1/`) on yleisin, koska se
näkyy lokeissa ja välimuisteissa ja sen voi reitittää
kuormantasaajassa. Vaihtoehtoja ovat otsake
(`API-Version: 2`) ja mediatyyppi (`Accept:
application/vnd.kauppa.v2+json`); Spring Framework 7 tukee kaikkia
kolmea ohjainmetodien `version`-määreellä. Poistuvasta versiosta
kerrotaan otsakkeilla `Deprecation` ja `Sunset`.

## Rajapinnan kuvaus: OpenAPI

OpenAPI (ennen Swagger) on koneluettava kuvaus poluista, parametreista,
skeemoista ja virheistä. Siitä tuotetaan dokumentaatio,
asiakaskirjastot ja sopimustestit. Kaksi tapaa:

- *Koodi ensin*: springdoc-openapi tuottaa kuvauksen ohjaimista ja
  DTO:ista ajossa (`/v3/api-docs`, Swagger UI). Nopea aloittaa, mutta
  kuvaus muuttuu aina, kun koodi muuttuu, joten rikkova muutos voi
  livahtaa julkaisuun huomaamatta.
- *Sopimus ensin*: YAML-kuvaus kirjoitetaan ja katselmoidaan ensin, ja
  palvelimen rajapinnat ja asiakkaat generoidaan siitä
  (openapi-generator). Hitaampi aloittaa, mutta sopii, kun rajapintaa
  käyttää moni tiimi.

Kumpikin tapa hyötyy CI-tarkistuksesta, joka vertaa kuvausta edelliseen
julkaistuun versioon ja hylkää rikkovat muutokset (esim. oasdiff).
Kuvauksen kirjoittaminen, validointi ja esimerkkien testaaminen
käydään läpi taidossa *Tekninen dokumentaatio*.

## Käytännössä

- **Suunnittele rajapinta käyttötapauksista**, ei tauluista: mitä
  näkymä tarvitsee yhdellä kutsulla. Yleiskäyttöinen CRUD kaikille
  tauluille siirtää liiketoimintasäännöt asiakkaille.
- **DTO rajalla.** Entiteetti ja rajapinnan esitys ovat eri luokat,
  vaikka ne aluksi näyttävät samalta. Muunnos on halpa, rikkoutunut
  rajapinta kallis.
- **Kaikki listat sivutetaan ja kaikki syötteet rajataan**:
  sivukoko, merkkijonojen pituus, rivien määrä.
- **Yksi virhemuoto**, jonka `type` on vakaa tunniste. Asiakas ei
  jäsennä `detail`-tekstiä.
- **Lisää, älä muuta.** Uusi kenttä on halpa; vanhan merkityksen
  muuttaminen vaatii uuden version.
- **Hinta:** "keskustelevat" rajapinnat (*chatty*), joissa näkymä
  tarvitsee kymmeniä kutsuja, ovat mobiiliverkossa hitaita. Toisaalta
  yksi jättikutsu, joka palauttaa kaiken, tekee jokaisesta muutoksesta
  rikkovan. Ratkaisu on käyttötapauksen mukainen resurssi tai
  erillinen taustapalvelu käyttöliittymälle (*backend for frontend*).

## Itsearviointi

- Osaat suunnitella resurssit ja polut sekä valita metodit ja
  tilakoodit tavallisille toiminnoille.
- Osaat perustella, miksi rajapinnassa on erilliset DTO:t ja miten raha
  ja ajat esitetään JSONissa.
- Osaat vertailla sivunumero- ja avainsivutusta.
- Osaat tuottaa virheet RFC 9457 -muodossa ja tunnistaa taaksepäin
  yhteensopivat ja rikkovat muutokset.

# Injektiot ja SSRF

Injektio syntyy, kun syöte liitetään toisen kielen lauseeseen
merkkijonona: SQL:ään, komentotulkin komentoon, tietokannan
kyselyolioon tai URL-osoitteeseen. Tulkki ei erota, mikä osa oli
ohjelmoijan koodia ja mikä käyttäjän dataa. Tässä luvussa on neljä
injektiota ja niiden rakenteellinen torjunta.

## SQL-injektio

*Tietoturvan perusteet* näytti SQL-injektion periaatteen.
Web-sovelluksessa se löytyy tavallisimmin hakuehdoista, lajittelusta ja
raporteista, joissa kysely kootaan pala palalta:

```{.typescript tiedosto="esimerkit/src/02-injektiot/sql.ts" osa="haavoittuva"}
```

Syöte `x' OR '1'='1` sulkee merkkijonon ja lisää ehdon, joka on aina
tosi. Korjaus on **parametrisoitu kysely**: tietokanta saa lauseen ja
arvot erikseen, joten arvo ei voi muuttaa lauseen rakennetta. Kaikkea
ei kuitenkaan voi parametroida. Sarakkeiden nimet, lajittelun suunta
ja taulujen nimet ovat lauseen rakennetta, joten ne valitaan
**sallittujen luettelosta**:

```{.typescript tiedosto="esimerkit/src/02-injektiot/sql.ts" osa="korjattu"}
```

```{.typescript tiedosto="esimerkit/src/02-injektiot/injektiot.test.ts" osa="sql"}
```

Näytösajo tekee saman haun kummallekin versiolle. Haavoittuva versio
palauttaa hyökkäyssyötteellä kaikkien asiakkaiden tilaukset, korjattu
etsii asiakasta, jonka nimi on koko syöte:

```{.tuloste tiedosto="esimerkit/naytos/02-sql.odotettu"}
```

ORM-kirjastot (Prisma, Drizzle, TypeORM) parametroivat tavalliset
kyselyt itse, mutta jokaisessa on myös raakakyselyn mahdollisuus
(`$queryRawUnsafe`, `sql.raw`), joka palauttaa ongelman.

## NoSQL-operaattori-injektio

Dokumenttitietokantojen kyselyt ovat olioita, ja arvon paikalle voi
kirjoittaa operaattorin. Jos palvelin välittää JSON-rungon kentät
sellaisenaan kyselyyn, salasanaksi kelpaa `{"$ne": null}`, "mikä
tahansa paitsi tyhjä":

```{.typescript tiedosto="esimerkit/src/02-injektiot/nosql.ts" osa="haavoittuva"}
```

Korjaus on **jäsentää syöte reunalla**: kenttien tyypit tarkistetaan
ennen kuin niitä käytetään. TypeScriptin tyyppi ei auta, koska
`JSON.parse` palauttaa ajon aikana mitä tahansa. Tuotannossa
tarkistus tehdään skeemakirjastolla (zod, valibot) tai rajapinnan
skeemasta generoidulla validoinnilla.

```{.typescript tiedosto="esimerkit/src/02-injektiot/nosql.ts" osa="korjattu"}
```

```{.typescript tiedosto="esimerkit/src/02-injektiot/injektiot.test.ts" osa="nosql"}
```

```{.tuloste tiedosto="esimerkit/naytos/02-nosql.odotettu"}
```

## Komentoinjektio

Kun palvelin käynnistää ulkoisen ohjelman komentotulkin kautta,
syötteen merkit `;`, `|`, `&`, `$( )` ja välilyönti ovat
komentotulkin syntaksia:

```{.typescript tiedosto="esimerkit/src/02-injektiot/komento.ts" osa="haavoittuva"}
```

Nimi `raportti.txt; touch PWNED` ajaa kaksi komentoa. Korjauksessa
ohjelma käynnistetään **ilman komentotulkkia** (`execFile`,
`spawn`), jolloin argumentit menevät ohjelmalle sellaisinaan.
Valitsimen injektio on oma vaaransa: nimi `-rf` olisi ohjelmalle
valitsin. Siksi argumenttien eteen tulee `--` ja nimi tarkistetaan
sallitulla muodolla.

```{.typescript tiedosto="esimerkit/src/02-injektiot/komento.ts" osa="korjattu"}
```

```{.typescript tiedosto="esimerkit/src/02-injektiot/injektiot.test.ts" osa="komento"}
```

Kolmas rivi on valitsimen injektio. Haavoittuvassa versiossa `wc` saa
nimen `-rf` valitsimena ja päättyy virheeseen; vaarallisemmalla
ohjelmalla sama syöte muuttaisi sen toimintaa.

```{.tuloste tiedosto="esimerkit/naytos/02-komento.odotettu"}
```

## SSRF

Palvelinpuolen pyyntöväärennöksessä (*server-side request forgery*)
palvelin hakee käyttäjän antaman osoitteen: linkin esikatselun,
webhookin tai kuvan URL:sta. Hyökkääjä antaa osoitteeksi palvelun,
johon vain palvelin pääsee: sisäverkon hallintaliittymän,
tietokannan HTTP-rajapinnan tai pilvipalvelun metatietopalvelun
`169.254.169.254`, joka antaa palvelimen tunnistetiedot. Vuoden 2019
Capital Onen tietomurto alkoi juuri näin.

```{.typescript tiedosto="esimerkit/src/02-injektiot/ssrf.ts" osa="haavoittuva"}
```

Torjunta on tarkistaa **kohteen IP-osoite**, ei osoitteen tekstiä.
Merkkijonon vertailu ohitetaan monella tavalla: `http://2130706433/`
on sama kuin `http://127.0.0.1/`, `localhost` ratkeaa loopbackiin, ja
julkinen palvelin voi uudelleenohjata sisäverkkoon. Siksi osoite
jäsennetään, nimi ratkaistaan, IP verrataan yksityisten verkkojen
estolistaan, eikä uudelleenohjauksia seurata:

```{.typescript tiedosto="esimerkit/src/02-injektiot/ssrf.ts" osa="estolista"}
```

```{.typescript tiedosto="esimerkit/src/02-injektiot/ssrf.ts" osa="korjattu"}
```

Testissä "sisäverkko" on osoite 127.0.0.1 ja "julkinen" palvelin
osoitteessa 127.0.0.2, joka ohjaa sisäverkkoon:

```{.typescript tiedosto="esimerkit/src/02-injektiot/injektiot.test.ts" osa="ssrf"}
```

Tulosteessa portit ovat `P` ja `Q`, koska ne vaihtuvat ajosta toiseen.
Toinen rivi on sama osoite kokonaislukuna, ja kolmannella "julkinen"
palvelin vastaa uudelleenohjauksella sisäverkkoon:

```{.tuloste tiedosto="esimerkit/naytos/02-ssrf.odotettu"}
```

Esimerkin tarkistus jättää yhden aukon: nimipalvelu voi palauttaa
tarkistuksessa julkisen osoitteen ja varsinaisessa yhteydessä
sisäisen (*DNS rebinding*). Tuotannossa yhteys avataan suoraan
tarkistettuun IP-osoitteeseen tai kaikki ulospäin lähtevät pyynnöt
kulkevat välityspalvelimen kautta, joka tekee tarkistuksen. Paras
puolustus on verkkotasolla: palvelin, joka hakee käyttäjän osoitteita,
ei pääse sisäverkkoon lainkaan.

## Sama virhe muissa tulkeissa

Injektio ei rajoitu näihin neljään. Sama rakenne toistuu aina, kun
syöte päätyy tulkille, joka ei erota sitä koodista:

| Tulkki | Hyökkäys | Rakenteellinen torjunta |
|--------|----------|-------------------------|
| XML-jäsennin | ulkoinen entiteetti lukee palvelimen tiedoston tai tekee pyynnön (XXE) | ulkoiset entiteetit ja DTD pois jäsentimen asetuksista |
| mallipohjakieli | käyttäjän teksti käännetään mallipohjaksi (SSTI) | syöte on mallipohjan muuttuja, ei koskaan mallipohjan lähdettä |
| LDAP-hakusuodatin, XPath | syöte muuttaa hakuehtoa | kirjaston parametrointi tai koodaus |
| HTTP-jäsennin | kaksi palvelinta tulkitsee pyynnön rajat eri tavoin (pyyntöjen salakuljetus) | HTTP/2 päästä päähän, sama jäsennin, epäselvät pyynnöt hylätään |

Pyyntöjen salakuljetus ja välimuistin myrkytys ovat välityspalvelimen
ja sovelluksen yhteispelin virheitä. Ne korjataan palvelinten
asetuksilla ja päivityksillä, ei sovelluskoodissa; lähteissä mainittu
PortSwiggerin materiaali käy ne läpi.

## Käytännössä

- **Erota koodi ja data rakenteellisesti.** Parametrit, ohjelmakutsu
  ilman komentotulkkia, tyyppitarkistettu kyselyolio. Mustat listat
  ("poista heittomerkit") häviävät aina koodauksille ja erikoistapauksille.
- **Tunnisteet sallittujen luettelosta.** Sarakkeet, lajittelu,
  taulut ja tiedostonimet eivät ole arvoja; niille ei ole parametria.
- **Jäsennä reunalla.** Kun JSON on tarkistettu skeemaa vasten, sisempi
  koodi voi luottaa tyyppeihin. Tarkistamaton `JSON.parse` on
  `any`-tyyppiä ajon aikana, vaikka koodi väittäisi muuta.
- **SSRF:ssä tarkista IP, älä tekstiä**, äläkä seuraa
  uudelleenohjauksia. Rajaa lisäksi palvelimen verkkoyhteydet: palvelu
  ilman pääsyä sisäverkkoon ei voi vuotaa sitä.
- **Hinta on pieni.** Parametrisoitu kysely on yhtä nopea kuin
  merkkijonokysely (tietokanta voi jopa välimuistittaa suunnitelman),
  ja `execFile` on nopeampi kuin komentotulkin käynnistys.

## Itsearviointi

- Osaat kirjoittaa parametrisoidun kyselyn ja valita dynaamisen
  lajittelun sallittujen luettelosta.
- Osaat selittää NoSQL-operaattori-injektion ja torjua sen
  tyyppitarkistuksella reunalla.
- Osaat käynnistää ulkoisen ohjelman ilman komentotulkkia ja estää
  valitsimen injektion.
- Osaat tunnistaa SSRF-riskin ja luetella, miksi osoitteen
  merkkijonovertailu ei riitä.
- Osaat tunnistaa saman virheen XML-jäsentimessä ja mallipohjakielessä
  ja nimetä niiden rakenteellisen torjunnan.

# HTTP ja REST ilman kehystä

Kehys piilottaa HTTP:n, mutta sen virheet näkyvät HTTP:nä: väärä
tilakoodi, puuttuva otsake tai toistuva POST. Siksi ensimmäinen
palvelu tehdään pelkällä JDK:lla. Moduli `http-perusteet` on
muistiinpanojen rajapinta, joka käyttää JDK:n `HttpServer`-luokkaa,
ja sen testit kutsuvat sitä `java.net.http.HttpClient`-asiakkaalla.

## Pyyntö ja vastaus ovat tekstiä

HTTP/1.1 on tekstiprotokolla TCP-yhteyden päällä. Pyyntö on rivi
`METODI polku versio`, otsakkeet, tyhjä rivi ja valinnainen runko.
Testi `RaakaHttpTest` kirjoittaa tämän pyynnön suoraan sokettiin:

```{.text tiedosto="esimerkit/http-perusteet/src/test/resources/pyynto-post.txt"}
```

ja vertaa palvelimen vastausta tähän tiedostoon (päiväys on korvattu,
koska se vaihtuu):

```{.tuloste tiedosto="esimerkit/http-perusteet/src/test/resources/vastaus-post.txt"}
```

Vastauksen tilarivi kertoo tuloksen (`201 Created`), otsakkeet
metatiedot ja runko itse sisällön. `Content-Length` kertoo rungon
pituuden tavuina, jotta yhteys voidaan käyttää uudelleen seuraavaan
pyyntöön. Otsakkeiden nimissä kirjainkoolla ei ole väliä: JDK
kirjoittaa `Content-type`, selain `content-type`. HTTP/2 ja HTTP/3
välittävät samat kentät binäärikehyksinä, mutta merkitys on sama, ja
sovelluksen näkökulmasta ero on vain suorituskyvyssä.

## Metodit ja niiden lupaukset

Metodi on lupaus siitä, mitä pyyntö tekee. Välityspalvelimet,
välimuistit, selaimet ja asiakaskirjastot luottavat lupaukseen, joten
sitä ei saa rikkoa.

| Metodi | Turvallinen | Idempotentti | Tyypillinen käyttö |
|--------|-------------|--------------|--------------------|
| `GET` | kyllä | kyllä | resurssin tai listan haku |
| `HEAD` | kyllä | kyllä | kuten GET ilman runkoa |
| `POST` | ei | **ei** | uusi resurssi, toiminto |
| `PUT` | ei | kyllä | resurssin korvaus tunnetulla osoitteella |
| `PATCH` | ei | ei (yleensä) | osittainen muutos |
| `DELETE` | ei | kyllä | poisto |

*Turvallinen* tarkoittaa, ettei pyyntö muuta palvelimen tilaa. Siksi
hakukone ja selaimen esilataus voivat tehdä GET-pyyntöjä vapaasti, ja
`GET /poista?id=5` on vakava virhe. *Idempotentti* tarkoittaa, että
saman pyynnön toistaminen jättää palvelimen samaan tilaan kuin yksi
pyyntö. Se on verkossa tärkein ominaisuus: jos vastaus katoaa,
asiakas ei tiedä, menikö pyyntö perille, ja idempotentin pyynnön voi
turvallisesti lähettää uudelleen.

Palvelimen reititys valitsee käsittelijän polun ja metodin mukaan:

```{.java tiedosto="esimerkit/http-perusteet/src/main/java/fi/tutoriaalit/http/MuistioPalvelin.java" osa="reititys"}
```

POST luo uuden muistion, jonka tunnisteen palvelin valitsee. Vastaus on
`201 Created`, ja `Location`-otsake kertoo uuden resurssin osoitteen:

```{.java tiedosto="esimerkit/http-perusteet/src/main/java/fi/tutoriaalit/http/MuistioPalvelin.java" osa="luo"}
```

PUT taas tallentaa asiakkaan valitsemaan osoitteeseen. Testi näyttää
eron: kaksi samaa PUT-pyyntöä jättävät yhden muistion, kaksi samaa
POST-pyyntöä luovat kaksi.

```{.java tiedosto="esimerkit/http-perusteet/src/test/java/fi/tutoriaalit/http/MuistioPalvelinTest.java" osa="idempotenssi"}
```

POST-pyynnön voi tehdä idempotentiksi asiakkaan antamalla avaimella;
luku 6 toteuttaa sen tilauksille.

## Tilakoodit

Tilakoodin ensimmäinen numero kertoo luokan: 2xx onnistui, 3xx
asiakkaan pitää tehdä jotain muuta, 4xx asiakas teki virheen ja 5xx
palvelin epäonnistui. Ero 4xx:n ja 5xx:n välillä on asiakkaalle
olennainen: 5xx-virheen jälkeen saman pyynnön voi yrittää myöhemmin
uudelleen, 4xx-virheen jälkeen ei, ennen kuin pyyntöä muutetaan.

| Koodi | Merkitys | Esimerkki |
|-------|----------|-----------|
| 200 | OK | haku onnistui |
| 201 | Created | POST loi resurssin; `Location` |
| 204 | No Content | DELETE onnistui, ei runkoa |
| 304 | Not Modified | välimuistin kopio kelpaa |
| 400 | Bad Request | runko ei kelpaa |
| 401 | Unauthorized | tunnistautuminen puuttuu tai on väärä |
| 403 | Forbidden | tunnistettu, mutta ei oikeutta |
| 404 | Not Found | resurssia ei ole |
| 405 | Method Not Allowed | `Allow`-otsake luettelee sallitut |
| 406 | Not Acceptable | pyydettyä esitysmuotoa ei ole |
| 409 | Conflict | ristiriita tilan kanssa, esim. saldo |
| 412 | Precondition Failed | `If-Match`-ehto ei täyty |
| 415 | Unsupported Media Type | väärä `Content-Type` |
| 422 | Unprocessable Content | muoto oikein, sisältö ei kelpaa |
| 428 | Precondition Required | palvelin vaatii ehdollisen pyynnön |
| 429 | Too Many Requests | kuormanrajoitus; `Retry-After` |
| 500 | Internal Server Error | odottamaton virhe |
| 503 | Service Unavailable | tilapäisesti poissa; `Retry-After` |

Virheiden testi tarkistaa kolme tavallisinta asiakkaan virhettä:

```{.java tiedosto="esimerkit/http-perusteet/src/test/java/fi/tutoriaalit/http/MuistioPalvelinTest.java" osa="virheet"}
```

## Sisältöneuvottelu

Sama resurssi voi olla eri *esitysmuodoissa*. Asiakas kertoo
`Accept`-otsakkeella, mitä se ymmärtää, ja palvelin kertoo
`Content-Type`-otsakkeella, mitä se lähetti. Jos sopivaa muotoa ei ole,
vastaus on 406.

```{.java tiedosto="esimerkit/http-perusteet/src/main/java/fi/tutoriaalit/http/MuistioPalvelin.java" osa="hae"}
```

```{.java tiedosto="esimerkit/http-perusteet/src/test/java/fi/tutoriaalit/http/MuistioPalvelinTest.java" osa="neuvottelu"}
```

Palvelin kirjoittaa JSONin käsin, jotta merkkijonon koodaus näkyy:
lainausmerkki ja kenoviiva pitää suojata. Oikeassa palvelussa
JSON-kirjasto (Jackson) tekee tämän, ja käsin kootut JSON-merkkijonot
ovat injektiovirheiden lähde samaan tapaan kuin käsin kootut
SQL-lauseet. Sama koskee pyynnön lukua: palvelin lukee rungosta
enintään 10 000 tavua, koska rajoittamaton luku antaa kenen tahansa
täyttää palvelimen muistin.

## Ehdolliset pyynnöt ja ETag

`ETag` on resurssin version tunniste. Asiakas voi lähettää sen takaisin
kahdella tavalla:

- `If-None-Match: "v1"` GET-pyynnössä: "lähetä vain, jos on muuttunut".
  Vastaus `304 Not Modified` ilman runkoa säästää kaistaa, ja
  välimuistit perustuvat tähän.
- `If-Match: "v1"` muuttavassa pyynnössä: "muuta vain, jos versio on
  yhä tämä". Jos joku muu on ehtinyt muuttaa resurssia, vastaus on
  `412 Precondition Failed`.

Jälkimmäinen ratkaisee *kadonneen päivityksen* (*lost update*): kaksi
käyttäjää avaa saman lomakkeen, ja jälkimmäisenä tallentava kumoaisi
huomaamattaan ensimmäisen muutoksen. Kun muutos on sidottu versioon,
jälkimmäinen saa virheen ja voi hakea tuoreen version:

```{.dot otsikko="Kadonnut päivitys estetään: Pekan muutos perustuu vanhaan versioon"}
digraph {
  nodesep=0.6; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=0.9, label="Anna"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5 -> t0_6 -> t0_7;
  t1 [shape=box, width=0.9, label="palvelin"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5 -> t1_6 -> t1_7;
  t2 [shape=box, width=0.9, label="Pekka"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3 -> t2_4 -> t2_5 -> t2_6 -> t2_7;
  {rank=same; t0; t1; t2;}
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0_4; t1_4; t2_4;}
  {rank=same; t0_5; t1_5; t2_5;}
  {rank=same; t0_6; t1_6; t2_6;}
  {rank=same; t0_7; t1_7; t2_7;}
  t0 -> t1 -> t2 [style=invis];
  t0_0 -> t1_0 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="GET /muistiot/b"];
  t1_1 -> t0_1 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="ETag \"v1\""];
  t2_2 -> t1_2 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="GET /muistiot/b"];
  t1_3 -> t2_3 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="ETag \"v1\""];
  t0_4 -> t1_4 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="PUT, If-Match \"v1\""];
  t1_5 -> t0_5 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="200, ETag \"v2\""];
  t2_6 -> t1_6 [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, label="PUT, If-Match \"v1\""];
  t1_7 -> t2_7 [style=solid, arrowhead=normal, color="#B4532A", constraint=false, label="412: versio on jo v2", fontcolor="#B4532A"];
}
```

Palvelin toteuttaa ehdon näin, ja testi ajaa saman tapahtumasarjan:

```{.java tiedosto="esimerkit/http-perusteet/src/main/java/fi/tutoriaalit/http/MuistioPalvelin.java" osa="korvaa"}
```

```{.java tiedosto="esimerkit/http-perusteet/src/test/java/fi/tutoriaalit/http/MuistioPalvelinTest.java" osa="ehdolliset"}
```

`ConcurrentHashMap.compute` tekee tarkistuksen ja päivityksen
atomisesti yhdelle avaimelle. Ilman sitä kaksi samanaikaista
pyyntöä voisivat molemmat lukea version 1 ja molemmat tallentaa. Sama
kysymys tulee vastaan tietokannassa luvussa 6: tarkistuksen ja
muutoksen on oltava yksi atominen toimenpide.

## Mitä kehys tekee

Sata riviä JDK-koodia tekee kehyksen keskeiset tehtävät huonosti:

| Tehtävä | Käsin | Kehyksessä |
|---------|-------|------------|
| Reititys | `split("/")` ja `switch` | `@GetMapping("/{id}")` |
| Rungon muunnos | merkkijonot | Jackson, `@RequestBody` |
| Validointi | `if`-lauseet | Bean Validation, `@Valid` |
| Virhemuoto | vapaa teksti | RFC 9457 |
| Sisältöneuvottelu | `contains` | `produces`, viestimuuntimet |
| ETag ja 304 | käsin | `checkNotModified`, suodattimet |
| Säikeet | oletussuoritin | säieallas tai virtuaalisäikeet |
| Turva | ei mitään | suodatinketju |

JDK:n `HttpServer` on kuitenkin hyödyllinen testien valepalvelimena ja
pienissä työkaluissa, joissa riippuvuuksia halutaan välttää.

## Käytännössä

- **Metodin semantiikka on sopimus.** GET ei muuta tilaa, ja PUT ja
  DELETE ovat idempotentteja. Asiakaskirjastot ja välityspalvelimet
  yrittävät idempotentteja pyyntöjä uudelleen automaattisesti.
- **Tilakoodi kertoo, kenen vika ja kannattaako yrittää uudelleen.**
  Älä palauta virheestä 200:aa ja virhetekstiä rungossa: valvonta,
  uudelleenyritykset ja välimuistit eivät näe virhettä.
- **Rajaa syöte.** Rungon koko, otsakkeiden määrä ja aikakatkaisut
  rajataan aina; rajaton luku on palvelunestohaavoittuvuus.
- **ETag ja If-Match kadonneita päivityksiä vastaan.** Mikä tahansa
  lomake, jota kaksi ihmistä voi muokata, tarvitsee version.
- **Hinta:** jokainen HTTP-kutsu on verkon edestakainen matka
  (konesalissa alle millisekunti, mantereiden välillä satoja). Rajapinta,
  joka vaatii kymmenen kutsua yhteen näkymään, on hidas, vaikka
  palvelin olisi nopea.

## Itsearviointi

- Osaat lukea ja kirjoittaa raa'an HTTP/1.1-pyynnön ja -vastauksen.
- Osaat selittää turvallisuuden ja idempotenssin eron ja sen, miksi
  POST ei ole idempotentti.
- Osaat valita oikean tilakoodin tavallisiin onnistumisiin ja
  virheisiin ja perustella 4xx:n ja 5xx:n eron.
- Osaat toteuttaa sisältöneuvottelun ja ehdolliset pyynnöt (ETag,
  `If-None-Match`, `If-Match`).

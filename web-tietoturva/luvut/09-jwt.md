# JWT oikein ja väärin

JSON Web Token (RFC 7519) on kolme base64url-koodattua osaa pisteillä
erotettuna: otsake, väitteet (*claims*) ja allekirjoitus. Se kulkee
ID-tokenina, access-tokenina ja palvelujen välisissä kutsuissa.
JWT:n vahvuus on, että vastaanottaja voi tarkistaa sen ilman
tietokantahakua. Heikkous on sama: tarkistuksen on oltava täydellinen,
ja token on voimassa vanhenemiseensa asti.

## Haavoittuva tarkistus

Kaksi vanhaa mutta toistuvaa virhettä johtuvat siitä, että tarkistaja
luottaa tokenin otsakkeen `alg`-kenttään:

```{.typescript tiedosto="esimerkit/src/09-jwt/jwt.ts" osa="haavoittuva"}
```

- **`alg: none`**: standardi määrittelee allekirjoituksettoman
  tokenin. Tarkistaja, joka hyväksyy sen, hyväksyy mitä tahansa.
- **Avainsekaannus** (*algorithm confusion*): palvelu odottaa RS256-
  tokenia ja tarkistaa sen julkisella avaimella. Hyökkääjä tekee
  HS256-tokenin, jonka HMAC-salaisuus on sama julkinen avain. Jos
  tarkistus valitsee algoritmin otsakkeesta ja käyttää samaa
  "avainta", väärennös kelpaa. Julkinen avain on nimensä mukaisesti
  kaikkien saatavilla, esimerkiksi tunnistuspalvelun JWKS-osoitteesta.

## Oikea tarkistus

Algoritmi, avaimet ja odotetut väitteet tulevat tarkistajalta, eivät
tokenista:

```{.typescript tiedosto="esimerkit/src/09-jwt/jwt.ts" osa="korjattu"}
```

| Väite | Tarkistus |
|-------|-----------|
| `alg` (otsake) | kiinteä luettelo, ei `none` |
| `kid` (otsake) | avain luotetusta avainjoukosta, ei tokenin osoittamasta URL:sta (`jku`, `x5u`) |
| `iss` | odotettu myöntäjä |
| `aud` | tämä palvelu; muuten toiselle palvelulle myönnetty token kelpaa |
| `exp`, `nbf` | voimassaolo pienellä marginaalilla kellojen eroille |
| `jti` | tarvittaessa kertakäyttöisyys tai kumoaminen |

```{.typescript tiedosto="esimerkit/src/09-jwt/jwt.test.ts" osa="hyokkaykset"}
```

Näytösajo antaa samat kuusi tokenia kummallekin tarkistajalle.
Haavoittuva hyväksyy ne kaikki; korjattu kertoo jokaisesta, mikä
tarkistus sen pysäytti:

```{.tuloste tiedosto="esimerkit/naytos/09-jwt.odotettu"}
```

Tuotannossa tarkistus tehdään kirjastolla, kuten `jose`, ja sille
annetaan kiinteät odotukset, esimerkiksi
`jwtVerify(token, JWKS, { algorithms: ["RS256"], issuer, audience })`.

## Kumoaminen ja elinaika

Allekirjoitettu token ei tiedä, onko käyttäjä kirjautunut ulos,
vaihtanut salasanaa tai menettänyt oikeutensa. Vaihtoehdot:

- **Lyhyt elinaika** (5–15 min) access-tokenille ja pidempi
  *refresh token*, joka on palvelimen tiedossa ja kumottavissa. Refresh
  token kierretään jokaisella käytöllä. Jos vanhaa käytetään
  uudelleen, koko ketju kumotaan, koska token on varastettu.
- **Kumottujen luettelo** `jti`-arvoista vanhenemiseen asti. Tämä
  palauttaa tietokantahaun, jota JWT:llä yritettiin välttää.
- **Introspektio**: rajapinta kysyy tunnistuspalvelulta tokenin
  tilan (RFC 7662). Tätä käytetään erityisesti läpinäkymättömillä
  tokeneilla.

Selainistuntoihin JWT on harvoin oikea valinta: palvelimen istunto
(luku 5) on yksinkertaisempi ja kumottavissa heti. JWT sopii
palvelujen välisiin kutsuihin ja tunnistuspalvelun ID-tokeniksi.

## Muita sudenkuoppia

- **JWT ei ole salattu.** Väitteet ovat base64url-koodattua JSONia,
  jonka kuka tahansa voi lukea. Henkilötunnukset ja salaisuudet eivät
  kuulu tokeniin (salattu JWE on eri asia).
- **Heikko HMAC-salaisuus** arvataan: HS256:n salaisuuden on oltava
  vähintään 256 bittiä satunnaista dataa, ei sana.
- **Väitteiden luottamus.** `role: admin` tokenissa on yhtä luotettava
  kuin sen myöntäjä ja tarkistus. Valtuutuspäätös tehdään silti
  palvelussa (luku 10).

## Käytännössä

- **Kiinteä algoritmi, avainjoukko, `iss`, `aud` ja `exp`**
  jokaisessa tarkistuksessa, kirjastolla.
- **Epäsymmetrinen allekirjoitus** (RS256, ES256, EdDSA), kun
  tarkistajia on monta: vain myöntäjä voi allekirjoittaa.
- **Lyhyt elinaika ja kierrettävä refresh token.**
- **Ei JWT:tä selainistunnoksi**, ellei sille ole erityistä syytä.
- **Hinta:** allekirjoituksen tarkistus maksaa mikrosekunteja
  (ES256) tai kymmeniä mikrosekunteja (RS256). Kumottujen luettelo
  ja introspektio maksavat verkkokutsun. Valitse sen mukaan, kuinka
  nopeasti oikeuksien menetyksen on vaikutettava.

## Itsearviointi

- Osaat selittää `alg: none`- ja avainsekaannushyökkäyksen.
- Osaat luetella JWT:n tarkistuksessa tarkistettavat kohdat.
- Osaat suunnitella tokenien elinajat ja kumoamisen.
- Osaat perustella, milloin JWT ei ole oikea valinta.

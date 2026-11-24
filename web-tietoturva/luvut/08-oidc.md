# OAuth 2.0 ja OpenID Connect

OAuth 2.0 on valtuutuskehys: käyttäjä antaa sovellukselle oikeuden
käyttää resurssia (esimerkiksi kalenteria) ilman salasanansa
luovuttamista. OpenID Connect (OIDC) lisää sen päälle tunnistuksen:
*ID-token* kertoo, kuka käyttäjä on. "Kirjaudu Googlella",
yritysten kertakirjautuminen (Entra ID, Okta, Keycloak) ja
Suomi.fi-tunnistus perustuvat näihin.

## Valtuutuskoodivirta ja PKCE

Kaikille sovelluksille, myös selain- ja mobiilisovelluksille,
suositeltu virta on **valtuutuskoodivirta PKCE:llä** (*authorization
code flow with Proof Key for Code Exchange*). OAuth 2.1 tekee siitä
ainoan sallitun virran.

1. Sovellus luo satunnaiset arvot `state`, `nonce` ja
   `code_verifier` ja ohjaa selaimen tunnistuspalveluun. Mukana on
   `code_verifier`-arvon SHA-256-tiiviste (`code_challenge`).
2. Käyttäjä kirjautuu tunnistuspalveluun, joka ohjaa selaimen
   sovelluksen paluuosoitteeseen koodin ja `state`-arvon kanssa.
3. Sovellus tarkistaa `state`-arvon ja vaihtaa koodin tokeneihin
   lähettämällä alkuperäisen `code_verifier`-arvon.
4. Sovellus tarkistaa ID-tokenin: allekirjoitus, myöntäjä, yleisö,
   vanheneminen ja `nonce`.

```{.typescript tiedosto="esimerkit/src/08-oidc/asiakas.ts" osa="aloitus"}
```

```{.typescript tiedosto="esimerkit/src/08-oidc/asiakas.ts" osa="paluu"}
```

Jokaisella tarkistuksella on oma hyökkäyksensä:

| Tarkistus | Ilman sitä |
|-----------|------------|
| `state` | kirjautumis-CSRF: uhri kirjautuu hyökkääjän tilille |
| PKCE | kaapattu koodi kelpaa hyökkääjälle |
| `redirect_uri` täsmälleen | koodi ohjautuu hyökkääjän palvelimelle |
| `nonce` | vanha ID-token toistetaan |
| ID-tokenin `aud` ja `iss` | toiselle sovellukselle myönnetty token kelpaa |

## Kirjautumis-CSRF

Hyökkääjä aloittaa virran omilla tunnuksillaan ja pysähtyy ennen
paluuta. Paluuosoite koodeineen on ansalinkki: uhri, joka avaa sen,
kirjautuu sovellukseen hyökkääjän tilille. Jos uhri sitten tallentaa
tilille korttitietonsa tai tiedostojaan, ne päätyvät hyökkääjälle.
`state` sitoo paluun selaimeen, joka aloitti virran:

```{.typescript tiedosto="esimerkit/src/08-oidc/oidc.test.ts" osa="kirjautumis-csrf"}
```

## PKCE ja kaapattu koodi

Valtuutuskoodi kulkee selaimen osoitteessa ja voi vuotaa:
välityspalvelimen lokiin, `Referer`-otsakkeeseen, selaimen
historiaan tai mobiililaitteella toiselle sovellukselle, joka on
rekisteröinyt saman paluuosoitteen. PKCE:ssä koodin vaihtaminen
vaatii arvon, joka ei koskaan kulkenut selaimen osoitteessa:

```{.typescript tiedosto="esimerkit/src/08-oidc/tarjoaja.ts" osa="pkce-vaatimus"}
```

```{.typescript tiedosto="esimerkit/src/08-oidc/tarjoaja.ts" osa="pkce-tarkistus"}
```

```{.typescript tiedosto="esimerkit/src/08-oidc/oidc.test.ts" osa="pkce"}
```

## Paluuosoitteen tarkistus

Tunnistuspalvelu lähettää koodin vain rekisteröityyn paluuosoitteeseen.
Vertailu tehdään merkkijonona täsmälleen. Alkuosan, säännöllisen
lausekkeen tai jokerimerkin vertailu on toistuvasti johtanut
tunnistuspalvelujen haavoittuvuuksiin:

```{.typescript tiedosto="esimerkit/src/08-oidc/tarjoaja.ts" osa="paluuosoite"}
```

```{.typescript tiedosto="esimerkit/src/08-oidc/oidc.test.ts" osa="paluuosoite-testi"}
```

## Tokenien säilytys ja BFF

Selainsovelluksen suurin OAuth-kysymys on, missä tokenit
säilytetään. `localStorage` on jokaisen sivulla ajettavan skriptin
luettavissa, joten XSS (luku 3) vie tokenit. Muistissa pidetty token
katoaa sivun latauksessa, ja sen uusiminen vaatii kolmannen
osapuolen evästeitä, joita selaimet rajoittavat.

Suositus on **BFF-malli** (*backend for frontend*): sovelluksen oma
palvelin hoitaa koko virran luottamuksellisena asiakkaana
(*confidential client*), säilyttää tokenit ja antaa selaimelle vain
`HttpOnly`-istuntoevästeen (luku 5). Rajapintakutsut kulkevat BFF:n
kautta, joka liittää access-tokenin. Esimerkin asiakas on BFF. Selain
ei näe tokeneita lainkaan, ja istunnon voi mitätöidä palvelimella.
Hinta on se, että CSRF-suojaus tulee jälleen tarpeelliseksi (luku 4).

## Valmiit kirjautumispalvelut

Oman tunnistuspalvelun rakentaminen on harvoin järkevää. Valmiit
palvelut (Keycloak itse ylläpidettynä, Entra ID, Auth0, Cognito,
Suomi.fi-tunnistus) hoitavat salasanat, MFA:n, pääsyavaimet,
palautuksen ja valvonnan. Sovellus toteuttaa vain OIDC-asiakkaan
valmiilla kirjastolla (`openid-client`, Spring Security,
`oidc-client-ts`). Hinta on riippuvuus palveluntarjoajasta ja sen
käytettävyydestä.

## Käytännössä

- **Valtuutuskoodivirta + PKCE + `state` + `nonce`**, myös
  luottamuksellisille asiakkaille. Implisiittinen virta ja
  salasanavirta (*resource owner password*) ovat vanhentuneita.
- **Paluuosoitteet täsmälleen**, ei jokerimerkkejä. Tunnistuspalvelun
  asetuksissa tämä on usein oletus; tarkista.
- **BFF selainsovelluksille**: tokenit palvelimelle, selaimelle
  `HttpOnly`-eväste.
- **Tarkista ID-token kirjastolla** ja kiinteillä odotuksilla
  (luku 9). Access-tokenin sisältöä asiakas ei tulkitse; se on
  tarkoitettu rajapinnalle.
- **Pienet oikeudet:** pyydä vain tarvittavat `scope`-arvot.

## Itsearviointi

- Osaat kuvata valtuutuskoodivirran PKCE:llä vaihe vaiheelta.
- Osaat kertoa, minkä hyökkäyksen kukin tarkistus (`state`, PKCE,
  `redirect_uri`, `nonce`, `aud`) torjuu.
- Osaat perustella, miksi selainsovelluksen tokenit kuuluvat
  palvelimelle (BFF).
- Osaat arvioida, milloin kannattaa käyttää valmista
  kirjautumispalvelua.

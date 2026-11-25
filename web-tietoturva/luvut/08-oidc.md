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

```{.dot otsikko="Valtuutuskoodivirta PKCE:llä. Yhtenäiset nuolet kulkevat selaimen osoiterivin kautta ja voivat vuotaa; katkoviivalla piirretty koodin vaihto (6–7) on sovelluksen ja tunnistuspalvelun suora yhteys. Arvo code_verifier kulkee vain siinä."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  a0 [label="sovellus (BFF)", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  aL [pos="0.00,-3.28!"];
  a0 -> aL [arrowhead=none, style=dotted];
  s0 [label="selain", shape=box, style="rounded,filled", width=0, height=0.3, pos="2.50,0!"];
  sL [pos="2.50,-3.28!"];
  s0 -> sL [arrowhead=none, style=dotted];
  i0 [label="tunnistuspalvelu", shape=box, style="rounded,filled", width=0, height=0.3, pos="5.00,0!"];
  iL [pos="5.00,-3.28!"];
  i0 -> iL [arrowhead=none, style=dotted];
  s1 [pos="2.50,-0.51!"]; a1_ [pos="0.00,-0.51!"];
  s1 -> a1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. GET /kirjaudu", pos="1.25,-0.41!"];
  a2 [pos="0.00,-0.87!"]; s2_ [pos="2.50,-0.87!"];
  a2 -> s2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. 302: state, nonce, code_challenge", pos="1.25,-0.77!"];
  s3 [pos="2.50,-1.23!"]; i3_ [pos="5.00,-1.23!"];
  s3 -> i3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. GET /authorize?state&code_challenge", pos="3.75,-1.13!"];
  i4 [pos="5.00,-1.59!"]; s4_ [pos="2.50,-1.59!"];
  i4 -> s4_ [];
  t4 [shape=plain, style="", fontsize=9, label="4. kirjautuminen; 302: code, state", pos="3.75,-1.49!"];
  s5 [pos="2.50,-1.95!"]; a5_ [pos="0.00,-1.95!"];
  s5 -> a5_ [];
  t5 [shape=plain, style="", fontsize=9, label="5. GET /paluu?code&state", pos="1.25,-1.85!"];
  a6 [pos="0.00,-2.31!"]; i6_ [pos="5.00,-2.31!"];
  a6 -> i6_ [style=dashed];
  t6 [shape=plain, style="", fontsize=9, label="6. POST /token: code + code_verifier", pos="1.25,-2.21!"];
  i7 [pos="5.00,-2.67!"]; a7_ [pos="0.00,-2.67!"];
  i7 -> a7_ [style=dashed];
  t7 [shape=plain, style="", fontsize=9, label="7. ID-token ja access-token", pos="3.75,-2.57!"];
  a8 [pos="0.00,-3.03!"]; s8_ [pos="2.50,-3.03!"];
  a8 -> s8_ [];
  t8 [shape=plain, style="", fontsize=9, label="8. Set-Cookie: istunto (HttpOnly)", pos="1.25,-2.93!"];
}
```

Kaavion numerot eivät ole samat kuin luettelon: luettelon vaihe 1 on
kaavion nuolet 1–3, vaihe 2 nuolet 4–5, vaihe 3 nuolet 6–7 ja vaihe 4
tapahtuu sovelluksessa ennen nuolta 8.

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

```{.tuloste tiedosto="esimerkit/naytos/08-kirjautumis-csrf.odotettu"}
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

```{.tuloste tiedosto="esimerkit/naytos/08-pkce.odotettu"}
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

Rekisteröity osoite kelpaa kummallekin versiolle. Alkuosaa vertaava
versio lähettää koodin myös osoitteeseen, joka vain alkaa samoin:

```{.tuloste tiedosto="esimerkit/naytos/08-paluuosoite.odotettu"}
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

```{.dot otsikko="BFF-malli. Tokenit pysyvät katkoviivan rajaamalla palvelinpuolella. Sivulle ujutettu skripti voi tehdä pyyntöjä käyttäjän istunnolla, mutta se ei saa tokenia mukaansa eikä voi käyttää rajapintaa muualta."}
digraph {
  rankdir=LR; nodesep=0.5;
  selain [label="selain\n(vain HttpOnly-eväste)"];
  subgraph cluster_p {
    label="palvelinpuoli"; style="rounded,dashed"; fontsize=10;
    bff [label="BFF\n(istunnot ja tokenit)"];
    api [label="rajapinta"];
  }
  idp [label="tunnistuspalvelu"];
  selain -> bff [label="istuntoeväste"];
  bff -> api [label="access-token"];
  bff -> idp [label="koodin vaihto,\ntokenin uusiminen"];
}
```

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

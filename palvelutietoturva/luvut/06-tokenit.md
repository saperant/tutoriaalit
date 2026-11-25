# Palvelutokenit ja tokenien vaihto

mTLS kertoo, mikä palvelu kutsuu. Usein pitää tietää myös, kenen
puolesta: tilauspalvelu kutsuu laskutusta asiakkaan 7 tilauksen
vuoksi, ja laskutuksen pitää näyttää vain asiakkaan 7 laskut.
Käyttäjän identiteetti kulkee palvelujen läpi allekirjoitettuna
tokenina.

## Allekirjoitettu token

Token on JWT (JSON Web Token), jonka myöntäjä on allekirjoittanut
(JWS). Esimerkissä allekirjoitus on ES256 eli ECDSA P-256 -käyrällä:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Tokenit.java" osa="myontaja"}
```

Väitteet (*claims*) ovat RFC 7519:n mukaiset: `iss` myöntäjä, `sub`
kenestä on kyse, `aud` kenelle token on tarkoitettu, `exp`
vanhenemisaika ja `scope` oikeudet. RFC 8693 lisää väitteen `act`:
kuka toimii aiheen puolesta.

## Tarkistus

Allekirjoituksen tarkistus ei riitä. Vastaanottajan pitää tarkistaa:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Tokenit.java" osa="tarkistaja"}
```

- **Algoritmi on kiinnitetty.** Token kertoo itse algoritminsa
  otsakkeessa. Jos tarkistaja uskoo sitä, `alg: none` ohittaa
  allekirjoituksen ja `HS256` julkisella avaimella HMAC-avaimena
  väärentää sen (ks. *Web-sovellusten tietoturva*).
- **Myöntäjä tunnetaan** ja avain valitaan myöntäjän mukaan.
- **Vanhenemisaika** tarkistetaan palvelun omaa kelloa vasten.
- **Yleisö on tämä palvelu.** Tämä unohtuu useimmin.

## Sekaantunut sijainen

Ilman yleisön tarkistusta mikä tahansa samalle myöntäjälle kelpaava
token käy kaikkialla. Käyttäjän selaimelle myönnetty token päätyy
tilauspalveluun, josta se voidaan lähettää laskutukseen,
hallintaan tai mihin tahansa muuhun. Murrettu suosituspalvelu, jolle
käyttäjän token on kerran välitetty, voi käyttää sitä kaikkialla
käyttäjän nimissä. Tämä on *sekaantuneen sijaisen* (*confused deputy*)
ongelma: oikeutettu välittäjä tulee käyttäneeksi toisen oikeuksia
tavalla, jota ei tarkoitettu.

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/TokenitTest.java" osa="sijainen"}
```

## Tokenien vaihto

Ratkaisu on, ettei käyttäjän tokenia välitetä eteenpäin. Tilauspalvelu
pyytää vaihtopalvelulta (*security token service*, STS) uuden tokenin
laskutukselle. Vaihtopalvelu tietää tilauspalvelun identiteetin
mTLS-yhteydestä ja päättää käytännön mukaan:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Vaihtopalvelu.java" osa="vaihto"}
```

```{.dot otsikko="Tokenien vaihto. Käyttäjän token A päättyy tilauspalveluun. Laskutus saa tokenin B, joka on myönnetty vain sille ja jossa näkyvät sekä käyttäjä (sub) että välittäjä (act)."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  y0 [label="yhdyskäytävä", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  yL [pos="0.00,-2.20!"];
  y0 -> yL [arrowhead=none, style=dotted];
  i0 [label="tilaus", shape=box, style="rounded,filled", width=0, height=0.3, pos="1.75,0!"];
  iL [pos="1.75,-2.20!"];
  i0 -> iL [arrowhead=none, style=dotted];
  v0 [label="vaihtopalvelu", shape=box, style="rounded,filled", width=0, height=0.3, pos="3.50,0!"];
  vL [pos="3.50,-2.20!"];
  v0 -> vL [arrowhead=none, style=dotted];
  l0 [label="laskutus", shape=box, style="rounded,filled", width=0, height=0.3, pos="5.25,0!"];
  lL [pos="5.25,-2.20!"];
  l0 -> lL [arrowhead=none, style=dotted];
  y1 [pos="0.00,-0.51!"]; i1_ [pos="1.75,-0.51!"];
  y1 -> i1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. token A: aud=kauppa-api", pos="0.88,-0.41!"];
  i2 [pos="1.75,-0.87!"]; v2_ [pos="3.50,-0.87!"];
  i2 -> v2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. vaihda A laskutukselle", pos="2.62,-0.77!"];
  v3 [pos="3.50,-1.23!"]; i3_ [pos="1.75,-1.23!"];
  v3 -> i3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. token B: aud=laskutus", pos="2.62,-1.13!"];
  i4 [pos="1.75,-1.59!"]; l4_ [pos="5.25,-1.59!"];
  i4 -> l4_ [];
  t4 [shape=plain, style="", fontsize=9, label="4. pyyntö + token B (mTLS)", pos="2.62,-1.49!"];
  l5 [pos="5.25,-1.95!"]; i5_ [pos="1.75,-1.95!"];
  l5 -> i5_ [];
  t5 [shape=plain, style="", fontsize=9, label="5. asiakkaan 7 laskut", pos="4.38,-1.85!"];
}
```

Uusi token on rajattu joka suunnasta: se kelpaa vain laskutukselle,
sisältää vain oikeuksien leikkauksen, kertoo välittäjän ja vanhenee
viidessä minuutissa:

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/TokenitTest.java" osa="vaihtoTesti"}
```

Näytösajo tulostaa kummankin tokenin väitteet ja sen, mitä laskutus
niistä päättää. Viimeinen rivi on murrettu suosituspalvelu, jolla ei
ole lupaa pyytää tokenia laskutukselle:

```{.tuloste tiedosto="esimerkit/naytos/06-tokenit.odotettu"}
```

Laskutus näkee nyt sekä käyttäjän (`sub`) että välittäjän (`act`) ja
voi päättää molempien perusteella. Kirjautumispalvelut (Keycloak,
Entra ID, Okta) ja palveluverkot tukevat vaihtoa RFC 8693:n
mukaisesti.

## Tokenin varastaminen

Allekirjoitettu token on haltijatoken (*bearer token*): kuka tahansa,
jolla se on, voi käyttää sitä. Vahinkoa rajaavat lyhyt elinikä, kapea
yleisö ja kapeat oikeudet. Vielä parempi on sitoa token avaimeen:
mTLS-sidotussa tokenissa (RFC 8705) on asiakkaan varmenteen tiiviste,
ja vastaanottaja hyväksyy sen vain samasta mTLS-yhteydestä. DPoP
(RFC 9449) tekee saman sovellustasolla. Varastettu token on silloin
hyödytön ilman yksityistä avainta.

## Käytännössä

- **Tarkista `aud` aina.** Jokainen palvelu on oma yleisönsä. Yhteinen
  yleisö kaikille sisäisille palveluille tekee tokenista yleisavaimen.
- **Älä välitä käyttäjän tokenia.** Vaihda se kohdekohtaiseksi tai,
  jos vaihtoa ei ole, välitä vain tieto käyttäjästä mTLS-yhteyden
  yli ja anna vastaanottajan päättää välittäjän perusteella.
- **Kapeat oikeudet, lyhyt elinikä.** Palvelujen väliset tokenit
  elävät minuutteja. Uuden pyytäminen on halpaa.
- **Käytä kirjastoa.** JOSE-kirjastot (Nimbus, jose4j, Spring
  Securityn resurssipalvelin) tekevät tarkistukset oikein, kun
  algoritmi, myöntäjä ja yleisö on konfiguroitu.
- **Kirjaa välittäjäketju.** `act`-väite kertoo auditointilokissa,
  minkä palvelujen kautta pyyntö kulki.

## Itsearviointi

- Osaat luetella tokenin tarkistukset ja selittää, miksi pelkkä
  allekirjoitus ei riitä.
- Osaat kuvata sekaantuneen sijaisen ongelman palvelukokonaisuudessa.
- Osaat toteuttaa tokenien vaihdon niin, että uusi token on rajattu
  yleisöltään, oikeuksiltaan ja eliniältään.
- Osaat kertoa, miten mTLS-sidotut tokenit ja DPoP vähentävät
  varastetun tokenin arvoa.

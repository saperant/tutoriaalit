# Palvelujen välinen mTLS

Tavallisessa TLS:ssä vain palvelin todistaa henkilöllisyytensä.
Molemminpuolisessa TLS:ssä (*mutual TLS*, mTLS) myös asiakas esittää
varmenteen ja todistaa omistavansa sen avaimen. Kättelyn jälkeen
molemmat tietävät, kenen kanssa puhuvat, ja yhteys on salattu.

## TLS-konteksti identiteetistä

Sama konteksti kelpaa palvelimelle ja asiakkaalle. Se esittää oman
varmenteen ja luottaa vain luottamusnipun juuriin, ei järjestelmän
julkisiin varmentajiin:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Identiteetti.java" osa="konteksti"}
```

Julkisiin varmentajiin luottaminen olisi vakava virhe: kuka tahansa
voi hankkia julkiselta varmentajalta varmenteen omalle
verkkotunnukselleen ja esittäytyä sillä.

## Palvelin, joka vaatii varmenteen

JDK:n HTTPS-palvelimelle kerrotaan, että asiakkaan varmenne on
pakollinen. Kutsujan identiteetti luetaan TLS-istunnosta:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Palvelin.java" osa="mtls"}
```

`setNeedClientAuth(true)` hylkää kättelyn, jos varmenne puuttuu tai
sitä ei ole myöntänyt luotettu varmentaja. Vaihtoehto
`setWantClientAuth` pyytää varmennetta mutta hyväksyy yhteyden
ilmankin, ja silloin jokaisen käsittelijän pitäisi muistaa tarkistaa
se. Turvallinen oletus on vaatia.

## Todennus ei ole valtuutus

mTLS kertoo, kuka kutsuu. Se ei kerro, saako kutsuja tehdä pyytämänsä.
Korjattu palvelu luettelee sallitut kutsujat nimeltä:

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/MtlsTest.java" osa="korjattu"}
```

Testi kokeilee neljää kutsujaa. Laskutus saa tiedot. Suositukset on
todennettu, mutta sillä ei ole oikeutta. Hyökkääjän omalla
varmentajalla tekemä laskutuksen varmenne ei kelpaa kättelyssä
lainkaan:

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/MtlsTest.java" osa="mtls"}
```

Jos palvelu olisi tyytynyt tarkistamaan, että varmenteen on myöntänyt
oma varmentaja, suosituspalvelun murtanut hyökkääjä olisi saanut
maksutiedot. Luottamusalueen jäsenyys ei ole oikeus mihinkään.

## Nimen tarkistus

Selain tarkistaa, että palvelimen varmenteen nimi vastaa osoitetta.
Palvelujen välillä sama tarkistus koskee identiteettiä: tilauspalvelun
pitää varmistaa, että se puhuu laskutukselle eikä vain jollekin
luotetulle palvelulle. Esimerkkien JDK:n HTTP-asiakas tarkistaa
DNS-nimen (`localhost`). Palveluverkoissa ja SPIFFE-kirjastoissa
asiakas tarkistaa odotetun SPIFFE-tunnisteen, koska DNS-nimet ja
IP-osoitteet ovat konttiympäristössä tilapäisiä.

## Kuka hoitaa mTLS:n

mTLS:n voi toteuttaa kolmella tavalla:

| Tapa | Hyvä | Huono |
|------|------|-------|
| sovellus itse | ei lisäosia, sovellus tietää kutsujan | jokainen kieli ja kehys erikseen |
| sivuvaunu (Envoy, Linkerd-proxy) | sovellus ei muutu, keskitetty käytäntö | lisäviive ja -prosessi, identiteetti otsakkeena sovellukselle |
| ytimessä (Cilium, ambient mesh) | ei sivuvaunua | alusta rajoittaa, vianetsintä vaikeampaa |

Palveluverkossa sovellus saa kutsujan identiteetin otsakkeena
sivuvaunulta. Otsakkeeseen saa luottaa vain, jos sovellukseen ei pääse
ohi sivuvaunun: palvelu kuuntelee vain paikallista osoitetta, ja
sivuvaunu poistaa saapuvista pyynnöistä samannimiset otsakkeet.

## Käytännössä

- **Vaadi varmenne, älä pyydä.** `need` eikä `want`; ilman varmennetta
  ei synny yhteyttä, jolloin unohtunut tarkistus ei avaa reikää.
- **Luota vain omaan luottamusnippuun.** Palvelujen välisessä TLS:ssä
  julkiset varmentajat eivät kuulu luotettuihin.
- **Valtuuta nimellä.** Salli lueteltu joukko identiteettejä
  resurssikohtaisesti. "Kuka tahansa luotettu" on harvoin oikea
  vastaus.
- **Tarkista vastapuoli myös asiakkaana.** Asiakas varmistaa, että
  vastapuoli on odotettu palvelu, jottei murrettu palvelu voi
  esittäytyä toisena ja kerätä pyyntöjä.
- **TLS 1.3.** Vanhemmat versiot ja heikot salausalgoritmit kytketään
  pois. TLS 1.3 salaa myös asiakkaan varmenteen kättelyssä.

## Itsearviointi

- Osaat rakentaa TLS-kontekstin, joka esittää oman identiteetin ja
  luottaa vain omiin juuriin.
- Osaat vaatia palvelimella asiakasvarmenteen ja lukea kutsujan
  identiteetin TLS-istunnosta.
- Osaat erottaa todennuksen ja valtuutuksen ja perustella, miksi
  luotetun varmentajan varmenne ei yksin oikeuta mihinkään.
- Osaat vertailla mTLS:n toteutusta sovelluksessa, sivuvaunussa ja
  ytimessä.

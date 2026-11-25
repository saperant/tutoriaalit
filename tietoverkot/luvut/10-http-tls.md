# HTTP ja TLS

HTTP on Webin ja lähes kaikkien rajapintojen protokolla. TLS salaa ja
todentaa yhteyden, ja HTTPS on HTTP TLS:n sisällä. Tämä luku näyttää
protokollat langalta katsottuina. Rajapintojen suunnittelu kuuluu
taitoon *Taustapalvelut* ja selaimen näkökulma taitoon
*Web-sovellukset*.

## HTTP/1.1 tekstinä

HTTP/1.1-viesti on tekstiä: pyyntörivi tai tilarivi, otsakkeet,
tyhjä rivi ja runko. Rivit päättyvät merkkeihin `\r\n`. Koska TCP on
tavuvirta, vastaanottaja tietää rungon pituuden otsakkeesta
`Content-Length` (tai `Transfer-Encoding: chunked`, jossa runko tulee
paloina):

```{.python tiedosto="esimerkit/10-http.py" osa="lue"}
```

```{.python tiedosto="esimerkit/10-http.py" osa="pyynto"}
```

```{.tuloste tiedosto="esimerkit/10-http.odotettu"}
```

Kaksi pyyntöä kulki samassa TCP-yhteydessä: HTTP/1.1:n yhteydet ovat
oletuksena pysyviä (*keep-alive*), joten kättelyn hinta maksetaan
kerran. `Host`-otsake on pakollinen, koska samassa osoitteessa voi olla
monta sivustoa.

Tilakoodien ryhmät: 2xx onnistui, 3xx uudelleenohjaus, 4xx asiakkaan
virhe (400 virheellinen pyyntö, 401 ei todennettu, 403 ei oikeutta, 404
ei löydy, 429 liikaa pyyntöjä), 5xx palvelimen virhe (502 ja 504
tarkoittavat, että välityspalvelin ei saanut vastausta taustalta).

## HTTP/2 ja HTTP/3

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|--|----------|--------|--------|
| Muoto | teksti | binäärikehykset | binäärikehykset |
| Rinnakkaisuus | yksi pyyntö kerrallaan yhteydessä | monta virtaa yhdessä yhteydessä | monta virtaa |
| Kuljetus | TCP | TCP (käytännössä TLS) | QUIC (UDP) |
| Otsakkeiden pakkaus | ei | HPACK | QPACK |

HTTP/2:n virrat jakavat yhden TCP-yhteyden, joten yksi kadonnut paketti
pysäyttää kaikki virrat (*head-of-line blocking*). HTTP/3 siirtää virrat
QUICiin, joka toteuttaa luotettavuuden virroittain UDP:n päällä ja
yhdistää kättelyn TLS 1.3:n kanssa, joten yhteys on valmis yhden
edestakaisen viiveen jälkeen. Semantiikka (metodit, otsakkeet,
tilakoodit) on kaikissa sama, joten sovellus ei yleensä huomaa versiota.

## TLS

TLS tarjoaa kolme asiaa: **luottamuksellisuuden** (salaus),
**eheyden** (muuttaminen havaitaan) ja **todennuksen** (palvelin on se,
joka väittää olevansa). Kaksi ensimmäistä ovat helppoja. Todennus on
vaikea osa, ja siinä tehdään virheet.

TLS 1.3 -kättely lyhyesti:

1. Asiakas lähettää *ClientHello*-viestin: tuetut salausmenetelmät,
   avaintenvaihdon julkinen osuus ja palvelimen nimi (SNI).
2. Palvelin vastaa omalla avaintenvaihdon osuudellaan, varmenteellaan
   ja allekirjoituksella, joka todistaa, että sillä on varmenteen
   yksityinen avain.
3. Asiakas tarkistaa varmenteen: ketju luotettuun varmentajaan,
   voimassaoloaika ja nimi. Sen jälkeen kaikki on salattua.

Kättely vie yhden edestakaisen viiveen; TCP:n kanssa yhteensä kaksi
ennen ensimmäistä HTTP-pyyntöä. Algoritmit selitetään taidossa
*Kryptografia*.

```{.dot tiedosto="kaaviot/10-tls.dot" otsikko="TCP- ja TLS 1.3 -kättely. Ensimmäinen HTTP-pyyntö lähtee kahden edestakaisen viiveen jälkeen. ServerHellon jälkeen kaikki on salattua, myös palvelimen varmenne."}
```

Varmenneketju laboratoriossa: oma varmentaja allekirjoittaa palvelimen
varmenteen, jonka *Subject Alternative Name* -laajennuksessa on nimi
`api.example`:

```{.python tiedosto="esimerkit/10-tls.py" osa="varmenteet"}
```

```{.python tiedosto="esimerkit/10-tls.py" osa="asiakas"}
```

```{.python tiedosto="esimerkit/10-tls.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/10-tls.odotettu"}
```

Kolme tulosta, kolme opetusta:

1. **Oikea nimi ja luotettu varmentaja**: yhteys muodostuu (TLS 1.3,
   AES-256-GCM).
2. **Väärä nimi**: varmenne on aito, mutta se on myönnetty toiselle
   nimelle. Ilman nimen tarkistusta kuka tahansa, jolla on *jokin*
   kelvollinen varmenne, voisi esiintyä palvelimena.
3. **Tuntematon varmentaja**: järjestelmän luottamat varmentajat eivät
   tunne omaa varmentajaamme. Sisäverkoissa oma varmentaja asennetaan
   luotetuksi tai annetaan asiakkaalle (`cafile`).

`curl` toimii samoin: `curl --cacert ca.crt https://api.example/` tai
nimen ohjaus testiosoitteeseen `--resolve api.example:443:192.0.2.80`.
`openssl s_client -connect palvelin:443 -servername nimi` näyttää
ketjun ja kättelyn vianetsinnässä.

## Käytännössä

- **Älä koskaan kytke varmenteen tarkistusta pois** (`verify=False`,
  `-k`, `InsecureSkipVerify`). Väliaikainen kiertotie päätyy tuotantoon.
  Korjaa sen sijaan luottamus: lisää oma varmentaja tai hanki oikea
  varmenne (esim. Let's Encrypt).
- **Nimi on SAN-laajennuksessa**, ei CN-kentässä. Nykyiset asiakkaat
  eivät katso CN-kenttää.
- **Seuraa varmenteiden vanhenemista** ja uusi automaattisesti
  (ACME). Vanhentunut varmenne on yleisimpiä palvelukatkoja.
- **Uudelleenkäytä yhteyksiä.** TCP- ja TLS-kättely maksavat 2 RTT;
  yhteysallas ja HTTP/2 säästävät ne.
- **Aseta aikarajat erikseen** yhteyden muodostukselle, TLS-kättelylle
  ja vastauksen lukemiselle.

## Itsearviointi

- Osaat kirjoittaa HTTP/1.1-pyynnön ja jäsentää vastauksen sekä kertoa,
  miten rungon pituus selviää.
- Osaat vertailla HTTP/1.1:tä, HTTP/2:ta ja HTTP/3:a ja kertoa, mitä
  QUIC ratkaisee.
- Osaat kuvata TLS 1.3 -kättelyn päävaiheet ja sen, mitä varmenteen
  tarkistus tarkistaa.
- Osaat luoda testivarmentajan ja palvelinvarmenteen sekä tulkita
  tavallisimmat varmennevirheet.

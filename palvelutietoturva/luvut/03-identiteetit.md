# Työkuormien identiteetit

Ihminen todistaa henkilöllisyytensä salasanalla, pääsyavaimella tai
toisella tekijällä. Palvelulla ei ole sormia eikä puhelinta. Sen
identiteetti on kryptografinen avainpari ja varmenne, jonka joku
luotettu taho on myöntänyt sille.

## Miksi ei jaettua salaisuutta

Yksinkertaisin tapa tunnistaa palvelu on API-avain: laskutus antaa
tilaukselle avaimen, jonka tilaus lähettää jokaisen pyynnön mukana.
Tavassa on kolme ongelmaa:

- **Avain on salaisuus, joka pitää jakaa.** Se pitää toimittaa
  palvelulle jotenkin, ja jokainen toimitustapa on vuotokohta.
- **Avain kulkee jokaisessa pyynnössä.** Jos liikenne tai loki
  vuotaa, avain vuotaa sen mukana.
- **Avain on pitkäikäinen.** Kierto vaatii koordinointia kahden
  palvelun välillä, joten sitä lykätään.

Avainparissa yksityinen avain ei poistu palvelulta koskaan. Palvelu
todistaa omistavansa sen allekirjoittamalla TLS-kättelyn, eikä mitään
uudelleenkäytettävää kulje verkossa.

## SPIFFE

SPIFFE (*Secure Production Identity Framework for Everyone*) on
avoin standardi työkuormien identiteeteille. Sen osat:

- **SPIFFE-tunniste** on URI muotoa `spiffe://luottamusalue/polku`,
  esimerkiksi `spiffe://kauppa.example/laskutus`. Luottamusalue on
  organisaatio tai ympäristö, polku nimeää työkuorman.
- **SVID** (*SPIFFE Verifiable Identity Document*) on todiste
  identiteetistä: X.509-varmenne, jonka SAN-kentässä on tunniste, tai
  allekirjoitettu JWT.
- **Luottamusnippu** (*trust bundle*) on luottamusalueen
  varmentajien juurivarmenteet. Palvelu luottaa niihin ja vain niihin.
- **Työkuorman API** on paikallinen rajapinta, josta palvelu hakee
  oman SVID:nsä ja luottamusnipun. Palvelu ei siis tarvitse
  alkusalaisuutta.

SPIRE on SPIFFE:n viitetoteutus. SPIRE-agentti toimii jokaisella
solmulla ja **todentaa työkuorman** (*attestation*) ennen kuin antaa
sille identiteetin: se tarkistaa esimerkiksi Kubernetesin
palvelutilin, nimiavaruuden ja kontin kuvan tiivisteen. Identiteetti
perustuu siis siihen, mikä työkuorma on, eikä mihinkään sen
tietämään salaisuuteen. Palveluverkot (Istio, Linkerd) ja pilvien
omat ratkaisut toimivat samalla periaatteella.

## Oma varmentaja testiä varten

Esimerkkien varmentaja luo juuren BouncyCastlella. Juuri saa
allekirjoittaa varmenteita, mutta ei muita varmentajia (`pathLen 0`):

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Varmentaja.java" osa="juuri"}
```

Palvelulle myönnetään varmenne, jonka SAN-kentässä on SPIFFE-tunniste
ja jonka elinikä on tunteja:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Varmentaja.java" osa="myonna"}
```

Varmenteessa ei ole aihetta (*subject*), vaan identiteetti on
SAN-kentässä, joka on siksi merkitty kriittiseksi. Laajennettu
avaimen käyttö sallii sekä palvelimen että asiakkaan roolin, koska
mTLS:ssä sama palvelu on kumpaakin.

Vastaanottaja lukee tunnisteen varmenteesta näin:

```{.java tiedosto="esimerkit/luottamus/src/main/java/fi/tutoriaalit/palveluturva/luottamus/Identiteetti.java" osa="tunniste"}
```

## Lyhyt elinikä

Perinteiset palvelinvarmenteet ovat voimassa vuoden. Työkuormien
varmenteet ovat voimassa tunteja, SPIREssä oletuksena tunnin. Lyhyt
elinikä korvaa suurimman osan kumoamisesta: vuotanut avain kelpaa
enintään tunnin, eikä kumoamislistoja tarvitse jakaa ja tarkistaa.
Hinta on se, että uusiminen on automatisoitava täysin. Ihminen ei
uusi varmenteita tunnin välein, ja jos automaatio pysähtyy, palvelut
pysähtyvät sen mukana.

```{.java tiedosto="esimerkit/luottamus/src/test/java/fi/tutoriaalit/palveluturva/luottamus/MtlsTest.java" osa="vanhentunut"}
```

## Käytännössä

- **Identiteetti työkuormalle, ei koneelle.** Saman solmun eri
  palveluilla on eri identiteetit. IP-osoite tai solmun nimi ei
  erottele niitä.
- **Nimeä tunnisteet merkityksen mukaan.** `spiffe://kauppa.example/
  laskutus` kertoo valtuutukselle tarpeellisen. Ympäristö kuuluu
  luottamusalueeseen (`kauppa-tuotanto.example`), jotta testiympäristön
  identiteetti ei kelpaa tuotannossa.
- **Yksityinen avain syntyy siellä, missä sitä käytetään.** Palvelu
  luo avainparin ja pyytää varmenteen (CSR). Avain ei kulje missään.
- **Juuriavain on kokonaisuuden arvokkain salaisuus.** Se kuuluu
  laitteistoon (HSM tai pilven KMS), ja sen alla käytetään
  välivarmentajia, joita voidaan vaihtaa.
- **Testaa vanheneminen.** Lyhytikäisillä varmenteilla vanheneminen on
  tavallinen tapahtuma, ei poikkeus. Testaa, että palvelu uusii
  varmenteensa ja hylkää vanhentuneet.

## Itsearviointi

- Osaat selittää, miksi avainpari on parempi työkuorman identiteetti
  kuin jaettu API-avain.
- Osaat kuvata SPIFFE-tunnisteen, SVID:n, luottamusnipun ja
  työkuorman todennuksen.
- Osaat myöntää testiä varten palveluvarmenteen, jossa identiteetti on
  SAN-kentässä.
- Osaat perustella lyhyen eliniän ja sen vaatimukset automaatiolle.

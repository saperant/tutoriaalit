# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Verkon sijainti ei todista mitään.** Jokainen pyyntö todennetaan
   ja valtuutetaan erikseen.
2. **Identiteetti työkuormalle, avain pysyy työkuormalla.**
   Lyhytikäinen varmenne, jossa SPIFFE-tunniste SAN-kentässä.
3. **mTLS vaaditaan, valtuutus nimetään.** Luotetun varmentajan
   varmenne ei yksin oikeuta mihinkään.
4. **Kierto automaattiseksi ja harjoitelluksi**: varmenteet,
   varmentajat, avaimet ja jaetut salaisuudet.
5. **Tarkista tokenin yleisö**, älä välitä käyttäjän tokenia
   eteenpäin; vaihda se kohdekohtaiseksi.
6. **Salaisuudet ajon aikana identiteetillä**, arkaluonteinen data
   kirjekuorisalattuna ja kontekstiin sidottuna.
7. **Dynaamiset tunnukset** tietokantoihin; kumoaminen kohdennetusti.
8. **Oletuksena estetty, vähimmät oikeudet, organisaation
   suojakaiteet.** Kavenna käytön perusteella.
9. **Yhdyskäytävä karsii, palvelu päättää.** Sisäiset otsakkeet
   siivotaan reunalla.
10. **Auditointilokit peitettyinä, korreloituina ja muuttumattomina**
    muualle kuin tuotantoon.
11. **Rajaa nopeasti ja kohdennetusti**: valtuutus, salaisuudet,
    identiteetti, verkko.

## Mallit

| Malli | Ongelma | Luku |
|-------|---------|------|
| nollaluottamus (PDP/PEP) | sisäverkkoon luotetaan | 2 |
| työkuorman identiteetti (SPIFFE) | jaetut API-avaimet | 3 |
| mTLS ja nimetty valtuutus | kutsujan väärentäminen | 4 |
| kolmivaiheinen kierto | katko varmentajan vaihdossa | 5 |
| lyhyt elinikä kumoamisen sijaan | CRL ja OCSP eivät toimi | 3, 5 |
| tokenien vaihto (RFC 8693) | sekaantunut sijainen | 6 |
| kirjekuorisalaus ja konteksti | avainpalvelun kuorma, siirretyt arvot | 7 |
| kryptografinen tuhoaminen | poisto varmuuskopioista | 7 |
| dynaamiset tunnukset | yhteiset pitkäikäiset salasanat | 8 |
| kaksoisavain | jaetun avaimen kierto | 8 |
| organisaation suojakaide | liian laajat oikeudet | 9 |
| politiikat koodina | käytäntövirheet tuotannossa | 9 |
| otsakkeiden siivous reunalla | sisäisten otsakkeiden väärennys | 10 |
| allekirjoitettu tarkistuspiste | lokien muokkaus | 12 |
| kumoamislista | murretun palvelun eristys | 13 |

## Mihin tästä eteenpäin

- *Hajautetut järjestelmät* ja *Järjestelmäsuunnittelu*:
  saatavuus ja skaalautuvuus, joita tietoturvaratkaisut eivät saa
  heikentää (varmentaja ja salaisuusvarasto ovat kriittisiä
  riippuvuuksia).
- *Palvelinympäristöt*: hakemistopalvelut, koventaminen ja valvonta.
- *Sulautettujen järjestelmien tietoturva*: laitteiden identiteetit ja
  luottamusketju, joissa samat periaatteet toteutetaan raudassa.

## Lähteet ja dokumentaatio

- NIST SP 800-207: *Zero Trust Architecture*.
  <https://csrc.nist.gov/pubs/sp/800/207/final>
- SPIFFE-määrittelyt ja SPIRE.
  <https://spiffe.io/docs/latest/spiffe-about/overview/>
- RFC 8446 *TLS 1.3*, RFC 5280 *X.509 PKI*.
- RFC 7519 *JWT*, RFC 8725 *JWT Best Current Practices*, RFC 8693
  *OAuth 2.0 Token Exchange*, RFC 8705 *mTLS-sidotut tokenit*, RFC
  9449 *DPoP*.
- OWASP: *Microservices Security Cheat Sheet* ja *Secrets
  Management Cheat Sheet*. <https://cheatsheetseries.owasp.org/>
- HashiCorp Vault -dokumentaatio: *Dynamic Secrets*, *Transit*.
  <https://developer.hashicorp.com/vault/docs>
- AWS: *IAM policy evaluation logic*, *KMS concepts (envelope
  encryption, encryption context)*. <https://docs.aws.amazon.com/>
- Open Policy Agent. <https://www.openpolicyagent.org/docs/latest/>
- Spring Boot: *SSL*. <https://docs.spring.io/spring-boot/reference/features/ssl.html>
- Spring Security: *X.509 Authentication*.
  <https://docs.spring.io/spring-security/reference/servlet/authentication/x509.html>
- Kyberturvallisuuskeskus: *Pilvipalvelujen turvallisuus*.
  <https://www.kyberturvallisuuskeskus.fi/>

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkikoodia saa
käyttää samoin ehdoin.

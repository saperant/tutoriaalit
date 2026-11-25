# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

Valinnat:

1. Salattu yhteys: TLS 1.3 kirjaston oletusasetuksilla. Salattu viesti
   tai tiedosto: AEAD (AES-256-GCM tai ChaCha20-Poly1305), mieluiten
   valmiin reseptin tai työkalun (`Fernet`, libsodium, `age`) kautta.
2. Tiiviste SHA-256, MAC HMAC-SHA256, avainten johtaminen HKDF,
   salasanat Argon2id.
3. Avaintenvaihto X25519 (siirtymäkaudella hybridinä ML-KEM:n kanssa),
   allekirjoitus Ed25519. RSA vain yhteensopivuuden vuoksi, OAEP:lla ja
   PSS:llä.
4. Satunnaisuus aina käyttöjärjestelmän CSPRNG:stä (`secrets`).

Toteutus:

5. Ei omia algoritmeja, protokollia eikä toteutuksia; opetuskoodi
   pysyy opetuksessa.
6. Nonce on yksilöllinen avainta kohti; tietueet ja kontekstit sidotaan
   liitettynä datana.
7. Eheys tarkistetaan ennen kuin purettua dataa käytetään, ja virheet
   käsitellään yhdellä tavalla.
8. Salaisuuksia verrataan vakioaikaisesti.
9. Varmennetarkistusta ei ohiteta; testeihin tehdään testivarmentaja.
10. Formaatteihin versio ja avaimen tunniste, jotta algoritmit ja avaimet
    voidaan vaihtaa.

Avaimet:

11. Avaimet eivät ole koodissa eivätkä versionhallinnassa; ne ovat
    salaisuusvarastossa, KMS:ssä tai HSM:ssä.
12. Avaimilla on yksi käyttötarkoitus, vähimmät oikeudet ja harjoiteltu
    kierto.

## Valintataulukko

| Tarve | Python (`cryptography`) | Komentorivi |
|-------|-------------------------|-------------|
| tunniste, avain | `secrets.token_urlsafe(32)` | `openssl rand -base64 32` |
| salaus | `AESGCM`, `ChaCha20Poly1305` | `age`, ei `openssl enc` |
| tiiviste | `hashlib.sha256` | `sha256sum`, `openssl dgst -sha256` |
| MAC | `hmac.new(k, m, "sha256")` | `openssl dgst -sha256 -hmac` |
| avainten johtaminen | `HKDF` | – |
| salasana | `Argon2id`, `hashlib.scrypt` | – |
| avaintenvaihto | `X25519PrivateKey`, `mlkem` | – |
| allekirjoitus | `Ed25519PrivateKey` | `openssl pkeyutl`, `minisign` |
| varmenteet | `x509.CertificateBuilder` | `openssl req`, `openssl x509` |
| TLS | `ssl.create_default_context()` | `openssl s_client` |

## Jatkotaidot

- *Tietoturva kehitystyössä*: salaisuuksien hallinta, allekirjoitetut
  julkaisut ja toimitusketju.
- *Web-sovellusten tietoturva*: istunnot, tokenit, JWT, OAuth 2.0 ja
  pääsyavaimet.
- *Sulautettujen järjestelmien tietoturva*: turvallinen käynnistys,
  avainten säilytys laitteessa ja sivukanavahyökkäykset.
- *Palveluarkkitehtuurin tietoturva*: mTLS, työkuormien identiteetit ja
  avaintenhallinta tuotannossa.

## Lähteet ja jatkolukeminen

- **`cryptography`-kirjaston dokumentaatio**
  (<https://cryptography.io>) kuvaa reseptit ja primitiivit sekä niiden
  turvallisen käytön.
- **Pythonin dokumentaatio:** moduulit `secrets`, `hashlib`, `hmac` ja
  `ssl` (<https://docs.python.org/3/library/crypto.html>).
- **libsodiumin dokumentaatio** (<https://doc.libsodium.org>) on
  käytännönläheinen johdatus siihen, mitä kukin rakenne takaa.
- **Standardit:** RFC 8446 (TLS 1.3), RFC 8439 (ChaCha20-Poly1305),
  RFC 5869 (HKDF), RFC 2104 ja 4231 (HMAC), RFC 9106 (Argon2),
  RFC 7748 (X25519), RFC 8032 (Ed25519), RFC 5280 (X.509), RFC 8555
  (ACME), RFC 9180 (HPKE) sekä FIPS 197 (AES), 203, 204 ja 205
  (kvanttiturvalliset menetelmät).
- **OWASP Cheat Sheet Series** (<https://cheatsheetseries.owasp.org>):
  *Password Storage*, *Cryptographic Storage*, *Key Management* ja
  *Transport Layer Security*.
- **Mozilla SSL Configuration Generator**
  (<https://ssl-config.mozilla.org>) TLS-palvelinasetuksiin.
- **Kirjat:** Jean-Philippe Aumassonin *Serious Cryptography* (2. painos
  2024) on tiivis ja käytännönläheinen yleisesitys. David Wongin
  *Real-World Cryptography* (2021) keskittyy protokolliin ja käyttöön.
  Dan Bonehin ja Victor Shoupin *A Graduate Course in Applied
  Cryptography* on vapaasti saatavilla oleva perusteellinen oppikirja
  (<https://toc.cryptobook.us>).
- **Kurssit ja harjoitukset:** CryptoPals (<https://cryptopals.com>)
  opettaa hyökkäykset toteuttamalla ne itse; tämän tutoriaalin
  hyökkäysesimerkit ovat samaa perinnettä.
- **Kyberturvallisuuskeskus** (<https://www.kyberturvallisuuskeskus.fi>)
  ja ENISA julkaisevat salausratkaisujen suosituksia, myös
  kvanttiturvalliseen siirtymään.

### Työkalut

- **OpenSSL** ja sen johdannaiset (**LibreSSL**, **BoringSSL**) sekä
  **step**-komentorivityökalu varmenteille.
- **age** (<https://age-encryption.org>) tiedostojen salaukseen,
  **minisign** allekirjoituksiin, **Sigstore** ohjelmistojakeluun.
- **testssl.sh** ja **SSL Labs** TLS-asetusten arviointiin.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Testivektorit ovat
viitatuista RFC-dokumenteista.

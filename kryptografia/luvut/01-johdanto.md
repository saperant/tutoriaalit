# Johdanto {.runko-johdanto}

Kryptografia on tietoturvan matemaattinen työkalupakki. Sillä
suojataan tiedon *luottamuksellisuus* (ulkopuolinen ei voi lukea),
*eheys* (muutos huomataan), *aitous* (tiedetään, kuka viestin lähetti)
ja *kiistämättömyys* (lähettäjä ei voi jälkikäteen kiistää
allekirjoitustaan). Saatavuutta kryptografia ei suojaa: salattu
palvelu kaatuu yhtä helposti kuin salaamaton.

Tutoriaali olettaa taidot *Tietoturvan perusteet* (uhkamallinnus ja
tietoturvan käsitteet), *Diskreetti matematiikka* (modulaariaritmetiikka)
ja *Python*. Tavoitteena on ymmärtää, mitä kukin menetelmä takaa ja mitä
ei, valita oikea menetelmä ja käyttää sitä oikein. Algoritmien sisäistä
rakennetta käsitellään vain sen verran kuin oikea käyttö vaatii.

## Älä keksi omaa kryptografiaa

Kryptografia on ala, jossa toimivalta näyttävä ratkaisu voi olla
täysin rikki. Testi, joka salaa ja purkaa viestin, menee läpi yhtä
hyvin rikkinäisellä kuin turvallisella toteutuksella. Siksi
ammattilaiset noudattavat kolmea sääntöä:

1. **Ei omia algoritmeja.** Käytetään julkisesti analysoituja
   standardeja (AES, ChaCha20, SHA-2, X25519, Ed25519, ML-KEM).
   *Kerckhoffsin periaate*: järjestelmän on oltava turvallinen, vaikka
   kaikki muu kuin avain on julkista.
2. **Ei omia protokollia.** Kun tarvitaan salattu yhteys, käytetään
   TLS:ää; kun tarvitaan salattu viesti, käytetään valmista rakennetta
   kuten AEAD-salausta tai `age`-, `libsodium`- tai HPKE-rakennetta.
3. **Ei omia toteutuksia.** Käytetään ylläpidettyjä kirjastoja, joissa
   sivukanavat ja reunatapaukset on hoidettu.

Tämän tutoriaalin *opetusesimerkit* rikkovat sääntöjä tarkoituksella:
niissä on RSA pienillä luvuilla, elliptinen käyrä 17 alkion kunnassa ja
SHA-256 puhtaalla Pythonilla. Ne on merkitty selvästi, eikä niitä
käytetä muuhun kuin ymmärtämiseen.

## Primitiivit ja protokollat

| Tarve | Primitiivi | Oletusvalinta |
|-------|------------|---------------|
| salaus jaetulla avaimella | AEAD | AES-256-GCM, ChaCha20-Poly1305 |
| sormenjälki | tiivistefunktio | SHA-256, SHA-3, BLAKE2 |
| aitous jaetulla avaimella | MAC | HMAC-SHA256 |
| avaimet salaisuudesta | KDF | HKDF |
| salasanojen tallennus | salasanatiiviste | Argon2id |
| avaintenvaihto | DH / KEM | X25519, ML-KEM-768 |
| allekirjoitus | allekirjoitus | Ed25519, ECDSA P-256, RSA-PSS |
| satunnaisuus | CSPRNG | `secrets`, `os.urandom` |

*Primitiivi* on yksi rakennuspalikka. *Protokolla* yhdistää niitä:
TLS käyttää avaintenvaihtoa, allekirjoituksia, KDF:ää ja AEAD:ta.
Useimmat käytännön virheet syntyvät palikoiden yhdistämisessä, eivät
palikoissa itsessään.

## Työkalut

Esimerkit käyttävät Pythonin `cryptography`-kirjastoa (versio 50) ja
vakiokirjaston moduuleita `hashlib`, `hmac`, `secrets` ja `ssl`.
`cryptography` jakaa rajapintansa kahteen osaan: *resepteihin*
(esim. `Fernet`), joita on vaikea käyttää väärin, ja `hazmat`-osaan
(*hazardous materials*), jossa ovat primitiivit. Tutoriaali käyttää
`hazmat`-osaa, koska tarkoitus on ymmärtää primitiivejä. Komentorivillä
käytetään OpenSSL 3:a.

Muita kirjastoja: **libsodium** (C, sidokset lähes kaikkiin kieliin;
helppokäyttöinen ja turvallinen oletus), **BoringSSL** ja **AWS-LC**
(OpenSSL:n johdannaiset), **RustCrypto** ja **ring** (Rust), Javan
**JCA** ja **Bouncy Castle**, Go:n `crypto`-paketti sekä selainten
**Web Crypto API**.

## Ensimmäinen esimerkki

Autentikoitu salaus kirjastolla: avain arvotaan, jokaiselle viestille
arvotaan uusi *nonce*, ja salattuun viestiin liitetään tunniste, jonka
avulla muutos huomataan purettaessa.

```{.python tiedosto="esimerkit/01-perusteet.py" osa="salaus"}
```

```{.python tiedosto="esimerkit/01-perusteet.py" osa="purku"}
```

```{.tuloste tiedosto="esimerkit/01-perusteet.odotettu"}
```

Yhden bitin muutos hylätään. Tämä on se, mitä "salaus" nykyään
tarkoittaa: luottamuksellisuus ja eheys yhdessä. Seuraavat luvut
selittävät, miksi kumpikin tarvitaan ja mitä tapahtuu, jos toinen
puuttuu.

## Tutoriaalin rakenne

Luvut 2–6 käsittelevät symmetristä kryptografiaa: satunnaisuutta,
salausta, tiivisteitä ja salasanoja. Luvut 7–8 käsittelevät julkisen
avaimen menetelmiä ja luvut 9–10 niiden käyttöä varmenteissa ja
TLS:ssä. Luku 11 kokoaa yleiset virheet ja sivukanavat ja luku 12
kvanttiturvallisen kryptografian.

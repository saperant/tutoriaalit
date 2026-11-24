# Kvanttiturvallinen kryptografia

Riittävän suuri kvanttitietokone murtaisi nykyiset julkisen avaimen
menetelmät. *Shorin algoritmi* ratkaisee tekijöihinjaon ja diskreetin
logaritmin polynomisessa ajassa, jolloin RSA, Diffie–Hellman ja
elliptiset käyrät menettävät turvallisuutensa kokonaan. Symmetrinen
kryptografia selviää paremmin: *Groverin algoritmi* puolittaa
avainavaruuden bittimäärän, joten AES-256 ja SHA-256 tarjoavat yhä
riittävän marginaalin.

| Menetelmä | Kvanttitietokoneen vaikutus | Toimenpide |
|-----------|-----------------------------|------------|
| RSA, DH, ECDH, ECDSA, Ed25519 | murtuu | korvataan |
| AES-128 | turvallisuus ~64 bittiä | AES-256 |
| AES-256, SHA-256, HMAC | riittävä | ei muutosta |

Tällaista kvanttitietokonetta ei vielä ole, eikä sen aikataulua
tiedetä. Siirtymä on silti aloitettu, koska salattua liikennettä voi
tallentaa nyt ja purkaa myöhemmin (*harvest now, decrypt later*).
Avaintenvaihto on siksi kiireellisin korjattava; allekirjoitukset
riittää vaihtaa ennen kuin kvanttitietokone on olemassa.

## Uudet standardit

NIST julkaisi elokuussa 2024 ensimmäiset kvanttiturvalliset standardit:

| Standardi | Algoritmi | Tarkoitus | Perusta |
|-----------|-----------|-----------|---------|
| FIPS 203 | ML-KEM (Kyber) | avaimen kapselointi | moduulihilat |
| FIPS 204 | ML-DSA (Dilithium) | allekirjoitus | moduulihilat |
| FIPS 205 | SLH-DSA (SPHINCS+) | allekirjoitus | tiivistefunktiot |

Lisäksi HQC valittiin vuonna 2025 varalle ML-KEM:lle, ja FN-DSA
(Falcon) on tulossa pienikokoisemmaksi allekirjoitukseksi.

## ML-KEM

ML-KEM on *avaimen kapselointimekanismi* (KEM). Rajapinta poikkeaa
Diffie–Hellmanista: vastaanottaja julkaisee avaimen, lähettäjä
*kapseloi* sillä satunnaisen salaisuuden, ja vastaanottaja *avaa*
kapselin.

```{.python tiedosto="esimerkit/12-mlkem.py" osa="kem"}
```

Siirtymäkaudella käytetään *hybridiä*: klassisen ja kvanttiturvallisen
menetelmän salaisuudet yhdistetään, jolloin avain on turvassa, jos edes
toinen menetelmä kestää. Hilapohjaiset menetelmät ovat uusia, eikä
niiden toteutuksista ole yhtä pitkää kokemusta kuin elliptisistä
käyristä.

```{.python tiedosto="esimerkit/12-mlkem.py" osa="hybridi"}
```

```{.tuloste tiedosto="esimerkit/12-mlkem.odotettu"}
```

TLS 1.3:ssa sama yhdistelmä on avaintenvaihto X25519MLKEM768. Se on
käytössä oletuksena Chromessa, Firefoxissa, Cloudflaressa ja OpenSSL
3.5:ssä, ja suuri osa verkon liikenteestä on jo kvanttiturvallista.
OpenSSH käyttää vastaavaa hybridiä (`mlkem768x25519-sha256`).

## ML-DSA

```{.python tiedosto="esimerkit/12-mldsa.py" osa="mldsa"}
```

```{.tuloste tiedosto="esimerkit/12-mldsa.odotettu"}
```

Kvanttiturvallisten menetelmien hinta on koko: ML-DSA:n allekirjoitus
on noin 50-kertainen Ed25519:ään verrattuna, ja varmenneketjussa niitä
on useita. Tämä vaikuttaa kättelyjen kokoon, sulautettujen laitteiden
muistiin ja protokollien pakettikokoihin. Laskenta sen sijaan on nopeaa.

## Siirtymän suunnittelu

1. **Inventaario:** missä järjestelmä käyttää julkisen avaimen
   kryptografiaa? TLS, SSH, VPN, allekirjoitetut päivitykset,
   varmenteet, salatut varmuuskopiot, laitteiden tunnistus.
2. **Elinikä:** kuinka kauan suojatun tiedon on pysyttävä salassa ja
   kuinka kauan laitteet ovat käytössä? Pitkäikäiset laitteet, joiden
   allekirjoitusavaimia ei voi vaihtaa, ovat suurin riski.
3. **Ketteryys:** algoritmit ja avainten koot eivät saa olla
   kovakoodattuja formaatteihin ja protokolliin.
4. **Kirjastot ajan tasalle:** suurin osa siirtymästä tapahtuu
   päivittämällä TLS- ja SSH-toteutukset.

## Käytännössä

- **Avaintenvaihto hybridiksi nyt**, kun käytetty kirjasto tukee sitä:
  TLS:ssä X25519MLKEM768, SSH:ssa `mlkem768x25519-sha256`.
- **Symmetriset avaimet 256-bittisiksi.** AES-256 ja SHA-256 tai
  SHA-384 kestävät myös kvanttitietokoneen.
- **Ei omia toteutuksia.** Hilapohjaisissa menetelmissä on uusia
  sivukanavariskejä; käytä kirjastojen toteutuksia (OpenSSL 3.5+,
  BoringSSL, AWS-LC, liboqs).
- **Sääntely:** EU:n ja Yhdysvaltojen viranomaissuositukset edellyttävät
  kriittisen infrastruktuurin siirtymää 2030-luvun alkuun mennessä.
  Kyberturvallisuuskeskus ja ENISA julkaisevat ajantasaiset suositukset.

## Itsearviointi

- Osaat selittää, mitkä menetelmät kvanttitietokone murtaa ja miksi
  symmetrinen kryptografia selviää.
- Osaat käyttää ML-KEM:ää ja yhdistää sen klassiseen avaintenvaihtoon
  hybridiksi.
- Osaat arvioida ML-DSA:n kokovaikutukset omaan järjestelmääsi.
- Osaat laatia siirtymäsuunnitelman inventaariosta kirjastopäivityksiin.

---
title: Kryptografia
subtitle: Pikaopas · Python cryptography 50 · OpenSSL 3
---

# Oletusvalinnat

| Tarve | Valinta | Ei |
|-------|---------|----|
| satunnaisuus | `secrets`, `os.urandom` | `random`, `Math.random` |
| salaus | AES-256-GCM, ChaCha20-Poly1305 | ECB, CBC/CTR ilman MAC:ia |
| tiiviste | SHA-256, SHA-3, BLAKE2 | MD5, SHA-1 |
| MAC | HMAC-SHA256 | `sha256(avain + viesti)` |
| avainten johtaminen | HKDF | sama avain moneen tarkoitukseen |
| salasana | Argon2id (19 MiB, t=2) | SHA-256, MD5, suolaton |
| avaintenvaihto | X25519 (+ ML-KEM-768) | todentamaton DH |
| allekirjoitus | Ed25519, ECDSA P-256, RSA-PSS | oppikirja-RSA |
| julkinen salaus | HPKE, RSA-OAEP | RSA PKCS#1 v1.5 |
| yhteys | TLS 1.3 (1.2 AEAD:lla) | TLS 1.0/1.1, `verify=False` |

# Reseptit

```{.python tiedosto="esimerkit/pikaopas.py" osa="satunnaisuus"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="aead"}
```

- Nonce 12 tavua, yksilöllinen avainta kohti; satunnaisena enintään
  ~2^32^ viestiä avainta kohti.
- Liitettyyn dataan konteksti: tietueen tunniste, omistaja, versio.
- Tallennusmuoto: `versio | avain-id | nonce | salattu + tunniste`.

```{.python tiedosto="esimerkit/pikaopas.py" osa="mac"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="salasana"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="allekirjoitus"}
```

```{.python tiedosto="esimerkit/pikaopas.py" osa="vaihto"}
```

# OpenSSL

| Tehtävä | Komento |
|---------|---------|
| satunnaiset tavut | `openssl rand -hex 32` |
| tiiviste, HMAC | `openssl dgst -sha256 [-hmac avain] -r tiedosto` |
| Ed25519-avain | `openssl genpkey -algorithm ed25519 -out k.pem` |
| julkinen avain | `openssl pkey -in k.pem -pubout -out p.pem` |
| allekirjoitus | `openssl pkeyutl -sign -rawin -inkey k.pem -in f -out f.sig` |
| tarkistus | `openssl pkeyutl -verify -rawin -pubin -inkey p.pem -in f -sigfile f.sig` |
| varmenne tekstinä | `openssl x509 -in c.crt -noout -text` |
| ketjun tarkistus | `openssl verify -CAfile ca.crt [-verify_hostname n] c.crt` |
| palvelimen ketju | `openssl s_client -connect h:443 -servername h` |

# Hinnat ja koot

| Operaatio | Koko | Aika (suuruusluokka) |
|-----------|------|----------------------|
| AES-GCM | +28 tavua/viesti | > 1 Gt/s laitteistolla |
| SHA-256 | 32 tavua | > 1 Gt/s |
| Argon2id (19 MiB, t=2) | PHC ~100 merkkiä | 20–100 ms |
| X25519 | avain 32 tavua | ~50 µs |
| Ed25519 | allek. 64, avain 32 tavua | ~20–50 µs |
| RSA-3072 | allek. 384 tavua | allekirjoitus ms, tarkistus µs |
| ML-KEM-768 | avain 1 184, kapseli 1 088 | ~50 µs |
| ML-DSA-65 | allek. 3 309, avain 1 952 | ~100–300 µs |

# Sudenkuopat

- Noncen toisto paljastaa selvätekstien XORin ja GCM:ssä MAC-avaimen.
- CBC + erotettavat virheet = täyteoraakkeli: tarkista eheys ensin.
- `==` salaisuuksille vuotaa ajoituksen: `hmac.compare_digest`.
- ECDSA:n satunnaisluvun toisto paljastaa salaisen avaimen.
- Kovakoodattu avain on julkinen avain. Vuotanut avain vaihdetaan,
  historian siivous ei riitä.
- Itse allekirjoitettu palvelinvarmenne opettaa ohittamaan varoitukset:
  oma CA sisäverkkoon, ACME julkisiin palveluihin.
- Testaa myös hylkäys: väärä avain, muutettu viesti, väärä nimi.

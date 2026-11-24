# Kryptografia

Tiivis suomenkielinen tutoriaali salausmenetelmien toiminnasta ja
oikeasta käytöstä. Esimerkit käyttävät Pythonin
[`cryptography`](https://cryptography.io)-kirjastoa (versio 50.0.1),
vakiokirjastoa ja OpenSSL 3:n komentoriviä. Valmiit dokumentit:
[kryptografia.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kryptografia.pdf) ja pikaopas
[kryptografia-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kryptografia-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä kryptografia takaa, älä keksi omaa, oletusvalinnat
2. Satunnaisuus – Mersenne Twisterin ennustaminen, `secrets`
3. Symmetrinen salaus – toimintatilat, ECB:n vuoto, muokattavuus,
   noncen toisto
4. Autentikoitu salaus – AES-GCM, ChaCha20-Poly1305, liitetty data,
   kirjekuorisalaus
5. Tiivisteet, MAC ja HKDF – pituuslaajennus, HMAC, avainten johtaminen
6. Salasanojen tallennus – suola, Argon2id, scrypt, bcrypt, pippuri
7. RSA – opetustoteutus, oppikirja-RSA:n heikkoudet, OAEP ja PSS
8. Diffie–Hellman, elliptiset käyrät ja allekirjoitukset – X25519,
   Ed25519, välimieshyökkäys
9. Varmenteet ja PKI – oma CA, ketjun tarkistus, ACME, CT
10. TLS 1.3 – kättely, avainaikataulu, TLS Pythonilla
11. Sivukanavat ja yleiset virheet – ajoitus, täyteoraakkeli,
    avaintenhallinta
12. Kvanttiturvallinen kryptografia – ML-KEM, ML-DSA, hybridit
13. Lopuksi – nyrkkisäännöt, valintataulukko, lähteet

Opetusesimerkit (RSA pienillä luvuilla, pieni elliptinen käyrä,
SHA-256 puhtaalla Pythonilla, hyökkäysesimerkit) on merkitty
tiedostojen alussa; niitä ei käytetä tuotannossa.

## Rakentaminen

```text
make testaa   # tarkistaa rakenteen ja ajaa esimerkit (ruff, mypy,
              # ShellCheck) ja vertaa tulosteet
make pdf      # kryptografia.pdf ja kryptografia-pikaopas.pdf
```

Esimerkit tarvitsevat Python 3.12:n tai uudemman, `cryptography`-paketin
(`pip install cryptography==50.0.1`) ja OpenSSL 3:n. Kehityskontti
`.devcontainer/kryptografia` sisältää kaiken tarvittavan.

## Lisenssi

CC BY-SA 4.0.

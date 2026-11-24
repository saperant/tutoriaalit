# Palveluarkkitehtuurin tietoturva

Hajautetun palvelukokonaisuuden suojaaminen: nollaluottamus,
työkuormien identiteetit ja mTLS, varmenteiden kierto, palvelutokenit
ja tokenien vaihto, salaisuuksien hallinta tuotannossa, dynaamiset
tunnukset, pääsynhallinta pilvessä, yhdyskäytävä ja segmentointi,
auditointi sekä poikkeamien käsittely. Valmis dokumentti:
[palvelutietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelutietoturva.pdf), pikaopas:
[palvelutietoturva-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/palvelutietoturva-pikaopas.pdf).

Esitiedot: taidot *Palveluarkkitehtuurit* ja *Kryptografia*.

## Sisältö

1. Johdanto – esimerkkijärjestelmä ja uhkamalli
2. Nollaluottamus – periaatteet, PDP ja PEP, pyyntökohtainen päätös
3. Työkuormien identiteetit – SPIFFE, oma varmentaja, lyhyt elinikä
4. Palvelujen välinen mTLS – todennus ja nimetty valtuutus
5. Varmenteiden kierto ja kumoaminen
6. Palvelutokenit ja tokenien vaihto – yleisö, sekaantunut sijainen
7. Salaisuuksien hallinta – varasto, kirjekuorisalaus, avainten kierto
8. Dynaamiset tunnukset ja jaetut avaimet
9. Pääsynhallinta pilvessä – käytäntömoottori, vähimmät oikeudet,
   politiikat koodina
10. Segmentointi ja yhdyskäytävä
11. mTLS Spring Boot -palvelussa
12. Auditointi ja havainnointi – peittäminen, muuttumaton loki
13. Tietoturvapoikkeamien käsittely
14. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

`esimerkit/` on Maven-projekti (Java 21, Spring Boot 4.2,
BouncyCastle), jossa on viisi modulia: `luottamus`, `salaisuudet`,
`kaytannot`, `havainnointi` ja `palvelu`. Testit eivät tarvitse
Dockeria eivätkä verkkoa riippuvuuksien latauksen jälkeen.

```text
cd esimerkit
make            # ./mvnw -B -q verify
```

Kehityskontti: `.devcontainer/palvelutietoturva`.

## Rakentaminen

```text
make testaa     # rakenteen tarkistus ja esimerkkien testit
make pdf        # tutoriaali ja pikaopas PDF:ksi
```

Lisenssi: CC BY-SA 4.0.

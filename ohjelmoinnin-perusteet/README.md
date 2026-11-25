# Ohjelmoinnin perusteet

Tiivis suomenkielinen johdatus ohjelmointiin lukijalle, joka ei ole
ohjelmoinut aiemmin. Kielenä on Python 3.12. Esimerkit ratkaisevat
pieniä oikeita tehtäviä, ja ne on kirjoitettu ammattimaisin tavoin:
kuvaavat nimet, pienet funktiot, syötteen tarkistus ja testit.
Sisältölukujen lopussa on *Kokeile itse* -tehtäviä (31 kpl), joiden
ratkaisun voi tarkistaa komennolla `python3 tarkista.py TUNNUS`
hakemistossa `esimerkit`.
Valmiit dokumentit: [ohjelmoinnin-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/ohjelmoinnin-perusteet.pdf)
ja pikaopas
[ohjelmoinnin-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/ohjelmoinnin-perusteet-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä ohjelmointi on, ympäristö, ensimmäinen ohjelma,
   ruff ja mypy, tehtävien tarkistin
2. Arvot, tyypit ja muuttujat – operaattorit, nimeäminen, muotoilu,
   syöte, liukulukujen tarkkuus
3. Ehdot ja toisto – `if`, `while`, `for`, `range`, silmukan
   jäljitys, syötteen kysyminen uudelleen
4. Funktiot – pilkkominen, paluuarvo vai tulostus, oletusarvot,
   näkyvyys, rekursio ja kutsupino
5. Kokoelmat – lista, sanakirja, joukko, monikko, sisäkkäiset
   rakenteet, viittaukset
6. Merkkijonot ja tiedostot – metodit, `with open`, UTF-8, CSV, JSON
7. Virheet ja poikkeukset – virheilmoituksen lukeminen, `try`,
   `raise`, validointi, virheen etsiminen
8. Luokat ja oliot – invariantti, kapselointi, dataluokat,
   koostaminen
9. Modulit ja standardikirjasto – oma moduli, `__main__`,
   `sys.argv`, `datetime`, virtuaaliympäristö
10. Testaus – pytest, parametrisointi, testitapausten valinta, testit
    ensin
11. Ohjelman suunnittelu – esimerkit, pilkkominen, datan mallinnus;
    budjettiohjelma alusta loppuun
12. Lopuksi – nyrkkisäännöt, jatkopolut ja lähteet

## Rakentaminen

```text
make testaa   # ruff, mypy, esimerkkien ajo, pytest-testit ja
              # tehtävien malliratkaisut
make pdf      # rakentaa PDF:t
```

Tehtävien pohjat ovat hakemistossa `esimerkit/tehtavat/pohjat`,
malliratkaisut hakemistossa `ratkaisut` ja testitapaukset tiedostossa
`tehtavat.toml`. Omat ratkaisut (`tehtavat/omat`) eivät kuulu
versionhallintaan.

Esimerkit voi ajaa kehityskontissa `.devcontainer/ohjelmoinnin-perusteet`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

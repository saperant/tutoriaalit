# Ohjelmoinnin perusteet

Tiivis suomenkielinen johdatus ohjelmointiin lukijalle, joka ei ole
ohjelmoinut aiemmin. Kielenä on Python 3.12. Esimerkit ratkaisevat
pieniä oikeita tehtäviä, ja ne on kirjoitettu ammattimaisin tavoin:
kuvaavat nimet, pienet funktiot, syötteen tarkistus ja testit.
Valmiit dokumentit: [ohjelmoinnin-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/ohjelmoinnin-perusteet.pdf)
ja pikaopas
[ohjelmoinnin-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/ohjelmoinnin-perusteet-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä ohjelmointi on, ympäristö, ensimmäinen ohjelma,
   ruff ja mypy
2. Arvot, tyypit ja muuttujat – operaattorit, nimeäminen, muotoilu,
   syöte, liukulukujen tarkkuus
3. Ehdot ja toisto – `if`, `while`, `for`, `range`, syötteen
   kysyminen uudelleen
4. Funktiot – pilkkominen, paluuarvo vai tulostus, oletusarvot,
   näkyvyys
5. Kokoelmat – lista, sanakirja, joukko, monikko, viittaukset
6. Merkkijonot ja tiedostot – metodit, `with open`, UTF-8, CSV
7. Virheet ja poikkeukset – virheilmoituksen lukeminen, `try`,
   `raise`, validointi
8. Luokat ja oliot – invariantti, kapselointi, dataluokat,
   koostaminen
9. Modulit ja standardikirjasto – oma moduli, `__main__`,
   `datetime`, virtuaaliympäristö
10. Testaus – pytest, parametrisointi, testitapausten valinta, testit
    ensin
11. Ohjelman suunnittelu – esimerkit, pilkkominen, datan mallinnus,
    debuggaus; budjettiohjelma alusta loppuun
12. Lopuksi – nyrkkisäännöt, jatkopolut ja lähteet

## Rakentaminen

```text
make testaa   # ruff, mypy, esimerkkien ajo ja pytest-testit
make pdf      # rakentaa PDF:t
```

Esimerkit voi ajaa kehityskontissa `.devcontainer/ohjelmoinnin-perusteet`.

Lisenssi: CC BY-SA 4.0.

# Integraatiotestaus ja Testcontainers

Sovelluksen testaaminen oikeita riippuvuuksia vasten kertakäyttöisissä
konteissa: testipyramidi ja saumat, joita yksikkötesti ei näe,
Testcontainersin kontit ja odotusstrategiat, pytest-fixturet ja
laajuudet, migraatiot ja testien eristys, testikaksoiset ja
sopimustestein todennetut väärennökset, välimuisti ja viestijono,
verkkovikojen simulointi, palvelujen välinen sopimustestaus sekä
integraatiotestit CI:ssä. Valmis dokumentti:
[integraatiotestaus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/integraatiotestaus.pdf),
pikaopas:
[integraatiotestaus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/integraatiotestaus-pikaopas.pdf).

Esitiedot: taidot *SQL ja relaatiotietokannat*, *Kontit ja pilvi-infrastruktuuri* ja
*Python-työkalut*.

## Sisältö

1. Johdanto – esimerkkisovellus ja sen riippuvuudet
2. Testipyramidi ja integraatiotestien paikka – SQLite vastaan PostgreSQL
3. Testcontainers – elinkaari, odotusstrategiat, moduulit, oma kuva
4. Pytest-fixturet ja konttien elinkaari – laajuudet, transaktio testille
5. Testidata, migraatiot ja eristys – peruutus, tyhjennys, pohjakanta
6. Testikaksoiset vai oikea riippuvuus – mock, väärennös, sopimustestit
7. Välimuisti ja viestijonot – Redis, Redis Streams, vähintään kerran
8. Verkkovikojen simulointi – vikaproxy, aikarajat, yhteysallas
9. Sopimustestaus – kuluttajavetoinen sopimus, JSON Schema, Pact
10. Integraatiotestit CI:ssä – GitHub Actions, peilit, Ryuk, epävakaus
11. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/`:

- `varasto/` – esimerkkisovellus: tallennus PostgreSQLiin, hinta-asiakas,
  Redis-välimuisti, varaustapahtumat ja palvelu
- `testiapu/` – konttikuvat, konttien luonti ja testidatan rakentajat
- `apukuva/` – testien apupalvelut kuvana: hintapalvelun väärennös ja
  vikaproxy
- `testit/` – yksikkö-, sopimus- ja integraatiotestit
- `sopimukset/` – hintapalvelun vastauksen sopimus (JSON Schema)
- `luku02/` … `luku10/` – lukujen esimerkit ja odotetut tulosteet

```text
make -C esimerkit                 # tarkistukset, testit, esimerkit
make -C esimerkit pytest
make -C esimerkit luku06/valehteleva
```

Esimerkit tarvitsevat Dockerin. Kuvat haetaan Docker Hubin
Google-peilistä (`mirror.gcr.io`); peilin voi vaihtaa muuttujalla
`TESTIKUVAT_PEILI`. Kehityskontti (`.devcontainer/integraatiotestaus`)
käyttää isännän Docker-sokettia ja verkkoa, ja Python-paketit
(testcontainers, SQLAlchemy, psycopg, redis, jsonschema) ovat valmiina.

Lisenssi: CC BY-SA 4.0.

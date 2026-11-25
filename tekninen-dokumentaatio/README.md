# Tekninen dokumentaatio

Dokumentaatio osana koodia: lukijat ja dokumenttityypit (Diátaxis),
selkeä tekninen teksti, docs as code, Sphinx ja MkDocs,
rajapintadokumentaatio koodista (docstringit, Doxygen, OpenAPI),
arkkitehtuurin kuvaus (C4, arc42, päätösloki), kaaviot koodina sekä
dokumentaation testaus ja ylläpito. Valmis dokumentti:
[tekninen-dokumentaatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tekninen-dokumentaatio.pdf),
pikaopas:
[tekninen-dokumentaatio-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tekninen-dokumentaatio-pikaopas.pdf).

Esitiedot: taidot *Python työkaluohjelmointiin* ja *Versionhallinta
(Git)*.

## Sisältö

1. Johdanto – esimerkkijärjestelmä ja tarkistusten periaate
2. Lukijat ja dokumenttityypit – Diátaxis, README, muutosloki,
   toimintaohje
3. Selkeä tekninen teksti – rakenne, virke, termit, proosan tarkistin
4. Dokumentaatio koodina – Markdown ja reST, tämä tutoriaalisarja
   tapausesimerkkinä
5. Sphinx – autodoc, ristiviittaukset, doctest, varoitukset virheinä
6. MkDocs ja julkaisu – tiukka tila, upotetut tulosteet, versiot
7. Rajapintadokumentaatio koodista – docstringit, kattavuus, ajautuminen
8. Doxygen ja muiden kielten työkalut – C-otsake, varoitukset, vertailu
9. HTTP-rajapinnan kuvaus – OpenAPI toteutusta vasten
10. Arkkitehtuurin kuvaus – C4, arc42, laatuskenaariot, päätösloki
11. Kaaviot koodina – Graphviz, Mermaid, PlantUML, kaavio koodista
12. Testaus ja ylläpito – linkit, omistajuus, elinkaari
13. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on yksi pieni järjestelmä, sääasemapalvelu,
dokumentoituna usealla tavalla:

- `saa/` – Python-kirjasto docstringeineen, komentoriviohjelma ja
  HTTP-käsittelijä
- `sphinx/` – kirjaston dokumentaatio: opas, ohjeet, selitys, viite
- `mkdocs/` – komentoriviohjelman käsikirja
- `c/` – rengaspuskuri C:llä, Doxygen-kuvaukset ja asetukset
- `openapi/` – rajapintakuvaus ja sen tarkistin
- `dokumentit/` – README, muutosloki, osallistumisohje, toimintaohje
- `adr/` – arkkitehtuuripäätökset ja niiden malli
- `kaaviot/` – C4-kaaviot ja koodista tuotettu riippuvuusverkko
- `tyokalut/` – tarkistimet: linkit, proosa, muutosloki, kattavuus,
  päätösloki, upotetut tulosteet
- `naytteet/` – tahallisesti vialliset näytteet, joiden on jäätävä
  kiinni

```text
make -C esimerkit            # kaikki tarkistukset ja rakennukset
make -C esimerkit sphinx     # yksi kohde
make -C esimerkit paivita    # kirjoittaa odotetut tulosteet uudelleen
```

Tarvittavat työkalut: Python 3.12, Sphinx 8.2, MkDocs 1.6, Doxygen 1.9,
Graphviz, openapi-spec-validator, jsonschema, PyYAML, ruff, mypy,
pytest ja GCC 14. Kehityskontissa
(`.devcontainer/tekninen-dokumentaatio`) ne ovat valmiina.

Lisenssi: CC BY-SA 4.0.

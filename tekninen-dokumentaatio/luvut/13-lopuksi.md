# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Lukija ja hänen kysymyksensä ensin.** Dokumentti, jolle ei osaa
   nimetä lukijaa, jää kirjoittamatta tai lukematta.
2. **Yksi sivu, yksi tyyppi.** Opas, ohje, viite ja selitys
   palvelevat eri tilannetta, eivätkä ne mahdu samalle sivulle.
3. **Koodin viereen.** Sama repositorio, sama muutos, sama
   katselmointi.
4. **Viite koodista.** Kuvaus kirjoitetaan määrittelyn viereen, ja
   työkalu tuottaa viitteen ja varoittaa ristiriidasta.
5. **Miksi, ei mitä.** Koodi kertoo, mitä tehdään. Kommentti,
   selitys ja päätösloki kertovat, miksi.
6. **Kaikki näytetty on ajettu.** Esimerkit, tulosteet ja
   rajapintapyynnöt tulevat testatuista tiedostoista.
7. **Varoitukset ovat virheitä.** Rikkinäinen linkki pysäyttää
   rakennuksen kuten käännösvirhe.
8. **Vähemmän ja oikein.** Väärä dokumentaatio on pahempi kuin
   puuttuva. Poista se, mitä et pysty ylläpitämään.

## Jatkotaidot

- *Versionhallinta (Git)*: julkaisut, semanttinen versiointi ja
  katselmointi, joihin dokumentaation elinkaari nojaa.
- *Jatkuva integraatio ja toimitus*: putki, joka rakentaa, tarkistaa
  ja julkaisee dokumentaation.
- *Testivetoinen kehitys ja testisuunnittelu*: suoritettavat
  määrittelyt ovat dokumentaatiota, joka ei voi vanhentua.
- *Taustapalvelut* ja *Palveluarkkitehtuurit*: HTTP-rajapintojen ja
  palvelujaon suunnittelu, joita tässä vain dokumentoitiin.
- *Ohjelmistoprojektin hallinta* sekä *Tiimit ja organisaatiomallit*:
  valmiin määritelmä, omistajuus ja tiimien väliset rajapinnat.
- *Laitteiston kuvausstandardit (SystemRDL, IP-XACT)*: sama yhden
  totuuden lähteen periaate laitteiston rekistereille.

## Lähteet

Dokumentaation rakenne ja kirjoittaminen:

- Daniele Procida: *Diátaxis – A systematic approach to technical
  documentation authoring*, <https://diataxis.fr>. Neljän
  dokumenttityypin malli.
- Jared Bhatti ym.: *Docs for Developers: An Engineer's Field Guide to
  Technical Writing*. Apress, 2021.
- *Google developer documentation style guide*,
  <https://developers.google.com/style>. Laaja englanninkielisen
  teknisen tekstin tyyliopas.
- Write the Docs, <https://www.writethedocs.org>. Yhteisö ja opas
  docs as code -käytäntöihin.
- Kotimaisten kielten keskus: *Kielitoimiston ohjepankki*,
  <https://www.kielitoimistonohjepankki.fi>. Suomen kielen
  oikeinkirjoitus ja virkakielen ohjeet.
- *Keep a Changelog*, <https://keepachangelog.com>, ja *Semantic
  Versioning 2.0.0*, <https://semver.org>.

Työkalut:

- Sphinx, <https://www.sphinx-doc.org>. BSD-lisenssi.
- MkDocs, <https://www.mkdocs.org>. BSD-lisenssi.
- Doxygen, <https://www.doxygen.nl>. GPL-lisenssi; generoitu
  dokumentaatio ei ole sen alainen.
- *OpenAPI Specification 3.1*, <https://spec.openapis.org>.
- Graphviz, <https://graphviz.org>; Mermaid, <https://mermaid.js.org>;
  PlantUML, <https://plantuml.com>.
- Python Software Foundation: *PEP 257 – Docstring Conventions* ja
  moduulin `doctest` dokumentaatio, <https://docs.python.org/3/>.
- *Google Python Style Guide*, luku docstringeistä,
  <https://google.github.io/styleguide/pyguide.html>.

Arkkitehtuurin kuvaus:

- Simon Brown: *The C4 model for visualising software architecture*,
  <https://c4model.com>.
- Gernot Starke ja Peter Hruschka: *arc42*, <https://arc42.org>.
- Michael Nygard: *Documenting Architecture Decisions*, 2011, ja
  <https://adr.github.io>.
- Len Bass, Paul Clements ja Rick Kazman: *Software Architecture in
  Practice*, 4. painos. Addison-Wesley, 2021. Laatuvaatimukset
  skenaarioina.

Tämän tutoriaalin esimerkit ja teksti ovat omaa tuotantoa. Lähteiden
sisältöä ei ole kopioitu; viitatut mallit (Diátaxis, C4, arc42, ADR,
Keep a Changelog) ovat avoimesti julkaistuja käytäntöjä.

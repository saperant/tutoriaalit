# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

- **Vuo on dataa.** Vaiheet, testit, sallitut varoitukset, rekisterit
  ja CI-putki kuvataan tiedostoissa. Koodi lukee kuvaukset, eikä uuden
  testin lisääminen vaadi koodimuutosta.
- **Kaikki tulokseen vaikuttava on näkyvissä.** Komento, parametrit,
  ympäristö, työkaluversio ja syötteiden sisältö kuuluvat leimaan ja
  manifestiin.
- **Virhe ei katoa.** Paluuarvo, tulosrivi, aikakatkaisu ja
  jäsentimen hylkäys pysäyttävät vuon. Mikään ei ole onnistunut
  ennen kuin se on todettu onnistuneeksi.
- **Raakalokia ei verrata.** Jäsennetään sovitut rivit yhteiseen
  malliin ja verrataan mallia. Työkaluversiosta riippuvat luvut
  arvioidaan raja-arvoina.
- **Tuotettu koodi tarkistetaan.** Generaattorin tuotos verrataan
  tallennettuun, ja ero kaataa putken.
- **Historia kertoo enemmän kuin yksi ajo.** Ensimmäinen hylkäävä
  versio, epävakaat testit ja hidastumiset löytyvät vain historiasta.

## Työkaluista

Tämän taidon kirjasto on opetusta varten kirjoitettu, ja se on
tarkoituksella pieni. Samat ajatukset löytyvät valmiista työkaluista,
joihin kannattaa tutustua ennen oman vuokehyksen kirjoittamista:

| Työkalu | Mihin |
|---------------------|---------------------------------------|
| FuseSoC ja Edalize | IP-ytimien kuvaus ja työkaluriippumaton ajo |
| SiliconCompiler | koko RTL-to-GDS-vuo Pythonista |
| OpenLane ja OpenROAD flow scripts | avoin ASIC-vuo Makella ja Tcl:llä |
| cocotb | testipenkit Pythonilla (taito *Laitteiston verifiointi*) |
| PeakRDL, SystemRDL Compiler | rekisterikuvaukset SystemRDL-muodossa |
| Bazel, Buck2 | sisältötiivisteisiin perustuva inkrementaalinen rakentaminen |

## Jatkotaidot

- *Laitteiston verifiointi*: testipenkkien rakenne, kattavuusmallit,
  formaali verifiointi ja regressioiden sisältö.
- *FPGA-toteutus* ja *ASIC-toteutus*: vuon vaiheet, joita tässä
  ohjattiin. Kaupallisten työkalujen Tcl-skriptit noudattavat luvun 4
  mallia.
- *SoC-integraatio*: rekisterilohkot väylässä ja ohjelmiston ja
  laitteiston rajapinta.
- *Laitteiston kuvausstandardit (SystemRDL, IP-XACT)*: luvun 9
  rekisterikuvaus standardimuodoilla ja valmiilla generaattoreilla.
- *Jatkuva integraatio ja toimitus*: putken suunnittelu, artefaktit ja
  julkaisukäytännöt yleisesti; luku 10 käsitteli vain laitteiston
  erityispiirteet.

## Lähteet ja lisälukemista

- Yosys-käsikirja ja komentojen ohjeet: <https://yosyshq.readthedocs.io/>
- Verilatorin käyttöohje ja varoituskoodit:
  <https://verilator.org/guide/latest/>
- Icarus Verilog: <https://steveicarus.github.io/iverilog/>
- Tcl-komentojen ohjeet: <https://www.tcl-lang.org/man/>
- Pythonin dokumentaatio: `subprocess`, `graphlib`, `tomllib`,
  `sqlite3` ja `concurrent.futures`: <https://docs.python.org/3/library/>
- SQLiten ikkunafunktiot: <https://www.sqlite.org/windowfunctions.html>
- GitHub Actions -dokumentaatio: työnkulut, välimuisti ja artefaktit:
  <https://docs.github.com/actions>
- Accellera: SystemRDL 2.0 -standardi. IEEE 1685: IP-XACT.
- FuseSoC: <https://fusesoc.readthedocs.io/>
- SiliconCompiler: <https://docs.siliconcompiler.com/>
- A. Mokhov, N. Mitchell, S. Peyton Jones: *Build Systems à la Carte*.
  ICFP 2018. Rakennusjärjestelmien teoria: leimat, varhainen katkaisu
  ja riippuvuudet.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Opetus-sta ja muut
esimerkkien työkalut on kirjoitettu tätä tutoriaalia varten.

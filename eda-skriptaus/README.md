# EDA-työkaluketjujen automatisointi

Tiivis suomenkielinen johdatus laitteistosuunnittelun työkalujen
ohjaamiseen ja niiden tulosten käsittelyyn Tcl- ja Python-skripteillä:
suunnitteluvuon vaiheet ja inkrementaalisuus, työkalujen eräajo, Tcl
työkalun sisällä, raporttien jäsentäminen ja koosteet, varoitusten
laatuportit, regressiot ja niiden historia, rekisterikuvauksista
tuotettu koodi sekä CI laitteistoprojekteille. Esitietoina ovat taidot
*RTL-suunnittelu SystemVerilogilla*, *Python työkaluohjelmointiin*,
*Käännösjärjestelmät, testaus ja CI* ja *Tcl*.
Valmis dokumentti: [eda-skriptaus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/eda-skriptaus.pdf),
pikaopas: [eda-skriptaus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/eda-skriptaus-pikaopas.pdf).

## Sisältö

1. Johdanto – esitiedot, esimerkkiprojekti ja työkalut
2. Suunnitteluvuon rakenne – vaiheet, riippuvuusverkko kuvana, tasot,
   leimat ja varhainen katkaisu, Make vai Python, lähdeluettelo
   yhdestä paikasta, ajohakemistot ja manifestit
3. Työkalujen ohjaus – eräajo, lokit, paluuarvot, aikakatkaisu,
   työkaluversiot, kaksi simulaattoria yhden rajapinnan takana
4. Tcl työkalun sisällä – Yosysin Tcl-tila, virheensieto ja
   kaupallisen työkalun eräajon malli
5. Raporttien jäsentäminen – yhteinen tietomalli, Yosys, STA,
   Verilator, Icarus, simulointi ja kattavuus, VCD-aaltomuotojen
   jäsennys ja tarkistus, Markdown- ja HTML-koosteet, jäsentimien
   testit
6. Varoitukset ja laatuportit – vakavuus, sallitut varoitukset
   perusteluineen ja voimassaoloaikoineen, räikkä
7. Regressioajot – testilista, rinnakkaisuus, siemenet ja
   virheallekirjoitukset
8. Historia ja trendit – SQLite, ensimmäinen hylkäävä versio,
   epävakaat testit, bisect
9. Rekisterikuvauksista generoitu koodi – RTL, C-otsake,
   dokumentaatio ja testipenkki yhdestä kuvauksesta, tahdin tarkistus
10. CI laitteistoprojekteille – putki vuon kuvauksesta, työkalukontit,
    lisenssipalvelimet, välimuisti ja artefaktit
11. Lopuksi – nyrkkisäännöt, valmiit työkalut ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on pieni laitteistoprojekti (laskuri, ALU,
ohjainlohko ja testipenkki), sen vuota ohjaava Python-kirjasto `vuo/`,
Tcl-skriptit Yosysille ja tätä tutoriaalia varten kirjoitetulle
opetus-sta-ajoitusanalysaattorille sekä 15 esimerkkiohjelmaa. Ne ajavat
Verilatorin, Icarus Verilogin, Yosysin ja Tcl-tulkin oikeasti.
Työkalujen versioista riippuvat luvut tulostetaan vain arvioina, joten
odotetut tulosteet eivät muutu työkalupäivityksissä. Python
tarkistetaan ruffilla ja mypyllä (`--strict`), ja jäsentimillä on
pytest-testit.

```text
make testaa        # rakenne, esimerkit ja tulosteet
make pdf           # eda-skriptaus.pdf ja eda-skriptaus-pikaopas.pdf
make kuvat         # piirtää kuvat/-hakemiston kuvaajat (Matplotlib)
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Tarvittavat työkalut: Python 3.12, ruff, mypy, pytest, Verilator,
Icarus Verilog, Yosys ja Tcl 8.6 sekä C-kääntäjä. Ne ovat valmiina
kehityskontissa `.devcontainer/eda-skriptaus`.

## Lisenssi

CC BY-SA 4.0.

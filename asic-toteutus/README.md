# ASIC-toteutus

Tiivis suomenkielinen johdatus siihen, miten RTL muuttuu valmistettavaksi
mikropiiriksi: solukirjastot, logiikkasynteesi, staattinen
ajoitusanalyysi, SDC-rajoitteet ja kulmat, testattavuus, pohjapiirros ja
sijoittelu, kellopuu ja reititys, tehonkulutus, sign-off, valmistus ja
kotelointi sekä asynkroniset piirit lyhyesti. Esitietona on taito
*RTL-suunnittelu SystemVerilogilla*.
Valmis dokumentti: [asic-toteutus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/asic-toteutus.pdf),
pikaopas: [asic-toteutus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/asic-toteutus-pikaopas.pdf).

## Sisältö

1. Johdanto – toteutusvuo, ASIC vai FPGA, työkalut ja mitä ajetaan
2. Standardisolut ja Liberty – solun rakenne, NLDM-taulukot,
   RC-viivemalli, kiikun rajoitteet, ajurin koko
3. Logiikkasynteesi – Yosys ja ABC, summainten arkkitehtuurit,
   ekvivalenssi simuloimalla ja SAT:lla
4. Staattinen ajoitusanalyysi – kuorma, eteneminen, kriittinen polku,
   vinous ja pitoaika
5. SDC-rajoitteet ja kulmat – monisykli- ja väärät polut, johdetut
   kellot, nollauksen vapautus, PVT ja OCV
6. Testattavuus – juuttumisviat, vikasimulointi, scan-ketju, BIST, JTAG
7. Pohjapiirros ja sijoittelu – HPWL, simuloitu jäähdytys, ruuhka
8. Kellopuu ja reititys – Elmore-viive, H-puu, Leen reititin
9. Tehonkulutus – aktiivisuus VCD:stä, kellon portitus, UPF
10. Sign-off – parasiittien poiminta, DRC, antenni, LVS, IR-pudotus,
    EM, ECO
11. Tapeout, valmistus ja kotelointi – saanto, maapomppu, IO-rengas
12. Asynkroniset piirit lyhyesti – C-elementti, Muller-liukuhihna
13. Lopuksi – nyrkkisäännöt, avoin RTL-to-GDS-vuo, mallit, jatkotaidot
    ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on 24 Python-ohjelmaa ja 3 SystemVerilog-
esimerkkiä sekä niiden käyttämät Verilog-suunnitelmat, testipenkit ja
SDC-tiedostot. Synteesi ajetaan oikeasti Yosysilla tätä tutoriaalia
varten kirjoitettua solukirjastoa `opetus.lib` vasten, ja porttitason
simuloinnit Icarus Verilogilla. Ajoitusanalyysi, vikasimulointi,
sijoittelu, kellopuu, reititys, tehoarvio, parasiittien poiminta, DRC
ja IR-pudotus ovat pieniä Python-opetustoteutuksia, jotka käyttävät samoja tietomuotoja
kuin oikeat työkalut (Liberty, Yosysin JSON-netlista, SDC, VCD).
Python tarkistetaan ruffilla ja mypyllä (`--strict`), SystemVerilog
Verilatorilla.

Täysi avoin RTL-to-GDS-vuo (OpenLane, OpenROAD, SKY130-PDK) kuvataan
tekstinä luvussa 13, koska se on useita gigatavuja.

Tekstin kuvaajat ja piirikuviot (sijoittelu, kellopuu, reititys, DRC,
IR-pudotus, kiekkokartta) piirretään samoista esimerkeistä skriptillä
`kuvat/piirra.py`; PNG-tiedostot ovat versionhallinnassa.

```text
make testaa        # rakenne, esimerkit ja tulosteet
make pdf           # asic-toteutus.pdf ja asic-toteutus-pikaopas.pdf
make kuvat         # piirtää kuvat uudelleen (Matplotlib, Yosys)
```

Tarvittavat työkalut: Python 3.12, ruff, mypy, Yosys, Icarus Verilog ja
Verilator. Ne ovat valmiina kehityskontissa `.devcontainer/asic-toteutus`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.

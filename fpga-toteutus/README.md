# FPGA-toteutus

Tiivis suomenkielinen johdatus siihen, miten RTL-suunnitelmasta tulee
toimiva FPGA-piiri: FPGA:n rakenne (logiikkasolut, kantoketju,
lohko-RAM, DSP, kellot ja IO), avoin työkaluketju Yosys → nextpnr →
IceStorm, synteesiraportit ja koodaustyyli, sijoittelu ja reititys,
ajoitusanalyysi ja liukuhihnoitus, PLL ja nollaukset,
kellotusalueiden ylitykset käytännössä, resurssien ja ajoituksen
optimointi, simuloitu kortti (painikkeet, ledit, sarjaportti ja
VGA-näyttö Verilatorilla) sekä testaus oikealla kortilla. Korttia ei
tarvita: koko suunnitelma ajetaan simuloidulla kortilla, ja valmis
bittivirta todennetaan muuntamalla se takaisin Verilogiksi. Esitietona
on taito *RTL-suunnittelu SystemVerilogilla*.
Valmis dokumentti: [fpga-toteutus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/fpga-toteutus.pdf),
pikaopas: [fpga-toteutus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/fpga-toteutus-pikaopas.pdf).

## Sisältö

1. Johdanto – FPGA, ASIC vai mikrokontrolleri, iCE40UP5K ja
   iCEBreaker, ensimmäinen suunnitelma
2. FPGA:n rakenne – logiikkasolu, kantoketju, lohko-RAM, DSP, kellot,
   IO ja konfigurointi
3. Avoin työkaluketju – Yosys, nextpnr, icepack, Make-vuo ja raportit
4. Synteesi ja koodaustyyli – muistin ja kertojan päättely, mallit
5. Sijoittelu ja reititys – nextpnr:n vaiheet, siemen, rajoitteet,
   ruuhka
6. Ajoitusanalyysi FPGA:lla – kriittinen polku, liukuhihnoitus,
   uudelleenajoitus
7. Kellot ja nollaukset – PLL, nollaus lukituksen jälkeen, sallinnat
8. Kellotusalueet käytännössä – asynkroninen FIFO, raportti,
   SDC/XDC-rajoitteet, MTBF
9. Resurssien ja ajoituksen optimointi – rinnakkainen ja jaettu
   FIR-suodin, keinot mittareittain
10. Simuloitu kortti – kortin malli C++:lla, kosketinvärähtely,
    VGA-näyttö, sarjaportti, bittivirta takaisin Verilogiksi
11. Testaus kortilla – lataus, käyttöönotto, UART-virheenjäljitysydin,
    ILA, vikojen jäljitys
12. Lopuksi – nyrkkisäännöt, mallit ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on yhdeksän SystemVerilog-esimerkkiä
testipenkkeineen. Jokainen simuloidaan Verilatorilla ja verrataan
odotettuun tulosteeseen. Lisäksi `esimerkit/Makefile` ajaa jokaisen
suunnitelman oikean vuon läpi iCE40UP5K-piirille (Yosys
`synth_ice40`, `nextpnr-ice40`, vilkulle myös `icepack`) ja vertaa
raportin tiivistelmää (solutyypit, logiikkasolujen raja-arvot, Fmax)
hakemiston `esimerkit/raportit/` odotettuihin tiedostoihin. Tarkat
solumäärät ja taajuudet vaihtelevat työkaluversioittain, joten ne
tarkistetaan raja-arvoja vasten. Kortille lataus (`iceprog`) kuvataan
tekstinä, eikä sitä testata.

Hakemistossa `esimerkit/10-kortti/` on luvun 10 esittelysuunnitelma
(`rtl/`), simuloitu kortti (`malli/kortti.cpp`) ja bittivirran
paluumatkan kääre (`bittivirta/`). Sama Makefile ajaa suunnitelman
simuloidulla kortilla, vertaa tapahtumalokia ja näytön kehysten
tarkisteita odotettuun, piirtää ajoituskaaviot mallin nastoista ja
ajaa lopuksi saman testin bittivirrasta palautetulle piirille.

```text
make testaa        # rakenne, simulaatiot, simuloitu kortti ja FPGA-vuo
make kuvat         # kuvat/*.png raporteista ja simuloidusta kortista
make pdf           # fpga-toteutus.pdf ja fpga-toteutus-pikaopas.pdf
```

Hakemiston `kuvat/` kuvat (resurssit, kriittinen polku, sijoittelu,
Yosysin piirikaaviot ja näytön kehykset) ovat versionhallinnassa.
`kuvat/piirra.py` piirtää ne uudelleen samoista raporteista, jotka
testit tarkistavat.

Tarvittavat työkalut: Verilator, Yosys, nextpnr-ice40, IceStorm
(`fpga-icestorm`) sekä Python 3, ruff ja mypy raporttien apuohjelmaa
varten. Kuvien piirtämiseen tarvitaan lisäksi Matplotlib ja Graphviz.
Kaikki ovat valmiina kehityskontissa `.devcontainer/fpga-toteutus`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.

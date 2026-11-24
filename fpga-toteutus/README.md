# FPGA-toteutus

Tiivis suomenkielinen johdatus siihen, miten RTL-suunnitelmasta tulee
toimiva FPGA-piiri: FPGA:n rakenne (logiikkasolut, kantoketju,
lohko-RAM, DSP, kellot ja IO), avoin työkaluketju Yosys → nextpnr →
IceStorm, synteesiraportit ja koodaustyyli, sijoittelu ja reititys,
ajoitusanalyysi ja liukuhihnoitus, PLL ja nollaukset,
kellotusalueiden ylitykset käytännössä, resurssien ja ajoituksen
optimointi sekä testaus kortilla. Esitietona on taito
*RTL-suunnittelu SystemVerilogilla*.
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
10. Testaus kortilla – lataus, käyttöönotto, UART-virheenjäljitysydin,
    ILA, vikojen jäljitys
11. Lopuksi – nyrkkisäännöt, mallit ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on kymmenen SystemVerilog-esimerkkiä
testipenkkeineen. Jokainen simuloidaan Verilatorilla ja verrataan
odotettuun tulosteeseen. Lisäksi `esimerkit/Makefile` ajaa jokaisen
suunnitelman oikean vuon läpi iCE40UP5K-piirille (Yosys
`synth_ice40`, `nextpnr-ice40`, vilkulle myös `icepack`) ja vertaa
raportin tiivistelmää (solutyypit, logiikkasolujen raja-arvot, Fmax)
hakemiston `esimerkit/raportit/` odotettuihin tiedostoihin. Tarkat
solumäärät ja taajuudet vaihtelevat työkaluversioittain, joten ne
tarkistetaan raja-arvoja vasten. Kortille lataus (`iceprog`) kuvataan
tekstinä, eikä sitä testata.

```text
make testaa        # rakenne, simulaatiot ja FPGA-vuo
make pdf           # fpga-toteutus.pdf ja fpga-toteutus-pikaopas.pdf
```

Tarvittavat työkalut: Verilator, Yosys, nextpnr-ice40, IceStorm
(`fpga-icestorm`) sekä Python 3, ruff ja mypy raporttien apuohjelmaa
varten. Ne ovat valmiina kehityskontissa `.devcontainer/fpga-toteutus`.

## Lisenssi

CC BY-SA 4.0.

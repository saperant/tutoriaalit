# DSP-algoritmien laitteistototeutus

Signaalinkäsittelyalgoritmien toteutus laitteistoksi bittitarkasta
mallista RTL:ään: kiinteän pilkun bittitarkka malli Pythonilla, FIR-
ja IIR-rakenteet, CORDIC, numeerisesti ohjattu oskillaattori,
CIC- ja polyfaasidesimaattorit, liukuhihnoitus ja resurssien
jakaminen, verifiointi cocotb:llä ja Verilatorilla sekä resurssit ja
ajoitus iCE40-FPGA:lla. Valmis dokumentti:
[dsp-laitteisto.pdf](https://saperant.github.io/tutoriaalit/materiaalit/dsp-laitteisto.pdf),
pikaopas:
[dsp-laitteisto-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/dsp-laitteisto-pikaopas.pdf).

Esitiedot: taidot *Digitaalinen signaalinkäsittely*, *Lukujen esitys
ja kiinteän pilkun aritmetiikka*, *Laitteiston verifiointi* ja
*FPGA-toteutus*.

## Sisältö

1. Johdanto – työnkulku, esimerkit, ensimmäinen ajo
2. Bittitarkka malli referenssinä – rajaukset, pyöristys,
   bittikasvu, kertoimet, pyöristys vai katkaisu
3. FIR-rakenteet – suora, transponoitu, symmetrinen ja systolinen
4. IIR-rakenteet – DF1-lohko, silmukka, kaskadi, ylivuoto, kuollut
   kaista
5. CORDIC – rotaatio ja vektori, tarkkuus, iteratiivinen ja
   liukuhihnoitettu
6. Numeerisesti ohjattu oskillaattori – vaiheakkumulaattori,
   neljännestaulukko, kannuspiikit
7. Monitaajuusrakenteet – CIC, Hogenauerin bittikasvu, polyfaasi,
   interpolointi
8. Liukuhihnoitus ja resurssien jakaminen – kriittinen polku,
   vastapaine, aikamultipleksointi, taittaminen
9. Verifiointi – ajuri ja vastaanottaja, bittitarkka vertailu,
   taajuusvaste, istutettu vika, Verilator, mallin testit
10. Resurssit ja ajoitus FPGA:lla – DSP-lohkot, rakenteiden
    vertailu, ajoitusraportin rajat
11. Lopuksi – nyrkkisäännöt, lähteet

## Esimerkit

`esimerkit/` sisältää bittitarkat mallit (`malli/`), RTL:n (`rtl/`),
cocotb-testipenkit (`penkit/`), Verilatorin C++-testipenkin
(`verilator/`), mallin testit (`testit/`), analyysit (`analyysit/`)
ja synteesivuon (`synteesi/`, `tyokalut/`). Ajojen tulosteet verrataan
hakemistojen `odotetut/` ja `raportit/` tiedostoihin.

```text
make -C esimerkit                     # kaikki esimerkit
make -C esimerkit cocotb-fir-suora    # yksi kohde
make -C esimerkit siivoa              # poistaa rakennus/-hakemiston
PAIVITA=1 make -C esimerkit ...       # kirjoittaa odotetut uudelleen
make kuvat                            # kuvaajat malleista (Matplotlib)
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Työkalut: Icarus Verilog 12, Verilator 5.020, Yosys 0.33 ja
nextpnr-ice40 (Ubuntu 24.04) sekä cocotb 2.1, NumPy, SciPy 1.18,
pytest, ruff ja mypy (pip). Kehityskontti
`.devcontainer/dsp-laitteisto` sisältää ne.

Lisenssi: CC BY-SA 4.0.

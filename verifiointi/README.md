# Laitteiston verifiointi

RTL-suunnitelman oikeellisuuden osoittaminen simuloinnilla, väitteillä
ja formaaleilla menetelmillä: verifiointisuunnitelma, kerroksellinen
testipenkki ja referenssimallit, rajoitettu satunnaistus ja siemenet,
koodi- ja toiminnallinen kattavuus, SystemVerilog-väitteet (SVA),
cocotb-testipenkit Pythonilla, formaali tarkistus Yosysilla (BMC,
induktio, cover), UVM:n käsitteet sekä regressiot ja epäonnistumisten
luokittelu. Valmis dokumentti:
[verifiointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verifiointi.pdf),
pikaopas:
[verifiointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/verifiointi-pikaopas.pdf).

Esitiedot: taidot *RTL-suunnittelu SystemVerilogilla* ja
*Python työkaluohjelmointiin*.

## Sisältö

1. Johdanto – menetelmät, esimerkkien lohkot ja istutetut viat,
   ensimmäinen testi
2. Verifiointisuunnitelma – ominaisuudet, menetelmän valinta,
   valmiuskriteerit, suunnitelma tiedostona
3. Testipenkin rakenne – transaktio, ajuri, monitori, malli,
   tulostaulu
4. cocotb – testipenkin kerrokset Pythonilla: malli, ajuri, monitori,
   tulostaulu
5. Satunnaistus ja siemenet – rajoitteet, painot, toistettavuus
6. Kattavuus – koodikattavuus Verilatorilla, toiminnallinen kattavuus,
   aukkojen sulkeminen
7. SystemVerilogin väitteet – ominaisuudet, `bind`, Verilatorin tuki
8. Formaali verifiointi – BMC, induktio ja invariantit, cover,
   reiluus
9. UVM:n käsitteet – komponentit, vaiheet, sekvenssit ja niiden
   vastineet cocotb:ssä
10. Regressiot ja virheiden luokittelu – vikamatriisi, tunnisteet,
    vian tutkiminen
11. Lopuksi – menetelmät ja viat, nyrkkisäännöt, lähteet

## Esimerkit

`esimerkit/` verifioi kahta lohkoa: synkronista FIFOa
(`rtl/fifo.sv`) ja vuorottelevaa arbiteria (`rtl/arbiteri.sv`).
Molemmissa on `BUGI_*`-makroilla istutettuja vikoja, ja jokainen
menetelmä ajetaan sekä ehjälle että viallisille versioille. Viallisen
version kohteen on epäonnistuttava.

```text
make -C esimerkit                 # kaikki esimerkit, tulosteet verrataan
make -C esimerkit formaali-taysi  # yksi esimerkki
make -C esimerkit regressio       # vikamatriisi ja luokittelu
make -C esimerkit siivoa          # poistaa rakennus/-hakemiston
```

Työkalut: Verilator 5.020, Icarus Verilog 12, Yosys 0.33 ja
yosys-smtbmc, Z3 (Ubuntu 24.04) sekä cocotb 2.1, ruff ja mypy (pip).
Kehityskontti `.devcontainer/verifiointi` sisältää ne. Kuvat
(`kuvat/*.png`) tuottaa `make kuvat`, joka tarvitsee lisäksi
Matplotlibin.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

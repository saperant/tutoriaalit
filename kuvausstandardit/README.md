# Laitteiston kuvausstandardit (SystemRDL, IP-XACT)

Tiivis suomenkielinen johdatus rekisterien, komponenttien ja
rajapintojen koneluettaviin kuvauksiin, joista RTL, ohjelmisto,
dokumentaatio ja verifiointimallit tuotetaan: SystemRDL 2.0 ja sen
työkaluketju PeakRDL, IP-XACT (IEEE 1685), CMSIS-SVD, laitepuu,
UVM-rekisterimalli sekä suunnitteluvuon muut kuvaukset (SDC, UPF,
Liberty, LEF/DEF, VCD). Esitietoina ovat taidot *SoC-integraatio* ja
*EDA-työkaluketjujen automatisointi*.
Valmis dokumentti: [kuvausstandardit.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kuvausstandardit.pdf),
pikaopas: [kuvausstandardit-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kuvausstandardit-pikaopas.pdf).

## Sisältö

1. Johdanto – kuluttajat, esimerkit, työkalut ja lisenssit
2. Yksi totuuden lähde – oma muoto vai standardi, siirtymä
   TOML-kuvauksesta SystemRDL:ään
3. SystemRDL:n perusteet – komponentit, pääsy, kääntäjä ja malli
   Pythonissa
4. Kenttien käyttäytyminen – W1C, lukemalla nollautuvat kentät,
   kertapulssit, laskurit, ilmoitukset ja keskeytykset
5. Parametrit, taulukot ja tarkistukset – rekisteriryhmät, omat
   ominaisuudet, kääntäjän virheet
6. Rekisterilohko RTL:ksi PeakRDL:llä – väyläliitännät, tuotettu
   logiikka, testipenkit ja lint-poikkeukset
7. Ohjelmisto ja dokumentaatio – C-otsake, ajuri, Markdown ja HTML
8. UVM-rekisterimalli
9. IP-XACT – rakenne, XML Pythonilla, vienti ja tuonti
10. CMSIS-SVD ja laitepuu
11. Työkaluketju ja CI – tahdin tarkistus ja rekisterikartan
    versiointi
12. Muut kuvaukset suunnitteluvuossa – liitteenomainen katsaus: SDC,
    UPF, Liberty, LEF/DEF, SPEF, GDSII, VCD/FST
13. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` ovat kolmen lohkon SystemRDL-kuvaukset
(ajastin, tapahtumalaskuri ja DMA-ohjain) ja niistä koottu piiri,
Python-kirjasto omille generaattoreille, PeakRDL:llä ja omilla
generaattoreilla tuotetut tiedostot (`tuotettu/`), testipenkit
Verilatorille, C-ajuri sekä SDC- ja UPF-esimerkit. Numeroidut
ohjelmat `01-malli.py` … `13-muut.py` tulostavat lukujen tulokset, ja
niitä verrataan tiedostoihin `.odotettu`. Python tarkistetaan
ruffilla ja mypyllä (`--strict`), ja apukirjastolla on pytest-testit.

```text
make testaa        # rakenne, esimerkit ja tulosteet
make pdf           # kuvausstandardit.pdf ja kuvausstandardit-pikaopas.pdf
make -C esimerkit tuota   # tuottaa hakemiston tuotettu/ uudelleen
```

Tarvittavat työkalut: Python 3.12, ruff, mypy, pytest,
systemrdl-compiler, PeakRDL (regblock, cheader, uvm, ipxact),
Verilator, GCC tai Clang, xmllint, dtc ja tclsh. Ne ovat valmiina
kehityskontissa `.devcontainer/kuvausstandardit`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.

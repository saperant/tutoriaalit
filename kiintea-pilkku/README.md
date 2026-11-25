# Kiinteän pilkun aritmetiikka

Tiivis suomenkielinen tutoriaali lukujen esityksestä
laitteistosuunnittelijan näkökulmasta: Q-formaatit, bittikasvu ja
vartijabitit, pyöristys ja sen harha, saturaatio ja kierto,
kvantisointikohina ja SQNR, bittitarkat mallit C:llä ja Pythonilla,
kiinteä pilkku vai liukuluku laitteistossa sekä sanaleveyksien valinta
virhebudjetilla.
Valmis dokumentti: [kiintea-pilkku.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kiintea-pilkku.pdf),
pikaopas: [kiintea-pilkku-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kiintea-pilkku-pikaopas.pdf).

## Sisältö

1. Johdanto – miksi kiinteä pilkku, ensimmäinen Q1.15-luku
2. Q-formaatit – arvoalue, tarkkuus, muunnokset ja muodon vaihto
3. Yhteen- ja kertolasku – bittikasvu, $-1 \times -1$, vartijabitit,
   jako vakiolla
4. Pyöristys ja katkaisu – tavat, harha mitattuna, kuollut alue
5. Saturaatio ja kierto – virhe ylivuodossa, Jacksonin sääntö,
   ylivuotovärähtely
6. Kvantisointivirhe ja SQNR – 6 dB bittiä kohti, dither, kertoimet
7. Bittitarkat mallit – sama FIR C:llä, Pythonilla ja
   SystemVerilogilla, CORDIC
8. Kiinteä pilkku vai liukuluku laitteistossa – pinta-ala,
   dynamiikka, lohkoliukuluku
9. Sanaleveyden valinta ja virhebudjetti
10. Yleiset sudenkuopat – etumerkkilaajennus, kapea tyyppi, C:n ylivuoto
11. Lopuksi – nyrkkisäännöt, mallit, jatkotaidot ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on C- ja Python-ohjelmia. Testaaja kääntää
C-esimerkit GCC 14:llä ja Clang 20:llä (C23, varoitukset virheinä,
AddressSanitizer ja UndefinedBehaviorSanitizer) ja tarkistaa
Python-esimerkit ruffilla ja mypyllä (`--strict`). NumPy tarvitaan
kohina- ja taajuusvastelaskuihin. FIR-suodattimen C-toteutus
(`07-fir.c`), Python-malli (`07-fir-malli.py`) ja
SystemVerilog-toteutus (`07-fir-rtl.sv`, Verilator) tuottavat bitilleen
saman tuloksen.

## Rakentaminen

```text
make testaa    # rakenne ja esimerkit
make pdf       # tutoriaali ja pikaopas
make kuvat     # kuvaajat esimerkkien funktioilla (Matplotlib)
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

# Korkean tason synteesi

Tiivis suomenkielinen tutoriaali laitteiston tuottamisesta C++-kuvauksesta:
HLS-työkalun vaiheet (jäsennys, tietovuograafi, ajoitus, sidonta ja
tilakoneen tuottaminen), silmukoiden avaaminen ja liukuhihnoitus,
muistirajapinnat ja taulukoiden jako, riippuvuudet muistin kautta,
rajapintaprotokollat (`ap_ctrl_hs`, `ap_memory`, AXI-Stream) sekä C++-mallin
ja tuotetun RTL:n verifiointi. Esimerkit käyttävät tätä tutoriaalia varten
kirjoitettua opetustyökalua **minihls**, jonka pragmat ja porttien nimet
noudattavat Vitis HLS:ää. Valmis dokumentti:
[hls.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hls.pdf),
pikaopas
[hls-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/hls-pikaopas.pdf).

## Sisältö

1. Johdanto – HLS:n käyttökohteet, työkalut, työnkulku, minihls
2. Etupää ja välikieli – syntetisoitava C++, jäsennys, tietovuograafi,
   if-conversion
3. Ajoitus – ASAP, ALAP, liikkuvuus, listaajoitus, ketjutus,
   kellojakso
4. Sidonta ja ohjaus – yksiköiden jakaminen, rekisterit, tuotettu
   Verilog
5. Silmukat ja avaaminen – osittainen ja täysi avaus, muistikaista
6. Liukuhihnoitus – aloitusväli, modulo-ajoitus, takaisinkytkentä,
   vaiherekisterit
7. Muistit ja taulukoiden jako – portit, syklinen ja lohkojako
8. Riippuvuudet muistin kautta – histogrammi, `dependence`,
   osahistogrammit
9. Rajapintaprotokollat – `ap_ctrl_hs`, `ap_memory`, AXI-Stream,
   pysäytys
10. Verifiointi – C-testipenkki, sanitoijat, yhteissimulaatio,
    formaali ekvivalenssi
11. Lopuksi – työnkulku, nyrkkisäännöt, pragmat eri työkaluissa,
    lähteet

## Rakentaminen

```text
make testaa   # tarkistaa tekstin ja ajaa kaikki esimerkit
make pdf      # rakentaa hls.pdf:n ja pikaoppaan
```

Esimerkit tarvitsevat Python 3.12:n (minihls ja sen tarkistukseen ruffin
ja mypyn), GCC 14:n (`g++-14`), Verilator 5:n, Yosysin ja ShellCheckin.
Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`: tiedoston
`asetukset` rivit ovat minihls-ajoja, `testi.cpp` on C-testipenkki ja
`odotettu` vuon odotettu tuloste. `esimerkit/testaa.sh` ajaa C-simulaation,
synteesin, Verilatorin lintin ja C/RTL-yhteissimulaation. Kehityskontti on
hakemistossa `.devcontainer/hls`.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit ja
minihls.

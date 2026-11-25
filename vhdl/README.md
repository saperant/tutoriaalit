# RTL-suunnittelu VHDL:llä

Tiivis suomenkielinen opas synteesikelpoiseen VHDL-2008:aan ja
itsetarkistaviin testipenkkeihin. Esimerkit simuloidaan GHDL 4.1:llä.
Valmiit dokumentit: [vhdl.pdf](https://saperant.github.io/tutoriaalit/materiaalit/vhdl.pdf) ja pikaopas
[vhdl-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/vhdl-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, standardit, työkalut, GHDL:n vaiheet,
   ensimmäinen malli
2. Entiteetit, arkkitehtuurit ja hierarkia – kirjastot, portit,
   suora instanssi, komponentit
3. Tyypit – `std_logic`, ratkaistut tyypit, `numeric_std`,
   muunnokset, leveydet, tietueet
4. Kombinaatiologiikka – `process (all)`, `case`, salvat,
   herkkyyslistat
5. Sekvenssilogiikka – kellotettu prosessi, deltasyklit, signaalit ja
   muuttujat, kellon deltaviive
6. Tilakoneet – luettelotyyppi, UART-vastaanotin, kattavuus,
   turvallinen tilakone
7. Generic-parametrit, generate ja muistit – rajoittamattomat portit,
   geneeriset tyypit, parametrien tarkistus, RAM, ROM ja FIFO
8. Paketit, funktiot ja proseduurit – CRC-paketti, puhtaus,
   standardipaketit
9. Testipenkit – malli, jono suojattuna tyyppinä, satunnaisuus,
   aikakatkaisut, testikehykset
10. Testit Pythonilla: cocotb – GHDL, ajuri ja monitori, mutaatiot
11. VHDL ja SystemVerilog rinnakkain
12. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # analysoi, elaboroi ja simuloi esimerkit GHDL:llä
make pdf      # rakentaa vhdl.pdf:n ja vhdl-pikaopas.pdf:n
```

Ajoituskaaviot tuotetaan simulaatiosta: `make -C esimerkit` tarkistaa
ne ja `make -C esimerkit paivita` kirjoittaa ne uudelleen.

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/vhdl`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

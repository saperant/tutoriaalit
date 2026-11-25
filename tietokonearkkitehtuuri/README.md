# Tietokonearkkitehtuuri

Suomenkielinen tutoriaali tietokonearkkitehtuurista oman
RISC-V-simulaattorin avulla: käskykanta ja käskyjen koodaus, datapolku
ja ohjaus, viisivaiheinen liukuhihna, riippuvuudet ja
eteenpäinkytkentä, haarautumisen ennustus, välimuistit ja
kirjoituspolitiikat, virtuaalimuisti ja MMU, poikkeukset, keskeytykset
ja I/O, moniytimisyys ja MESI-koherenssi, superskalaarinen
epäjärjestyssuoritus sekä RISC, CISC ja mikro-operaatiot. Esitietoina
ovat taidot *Digitaalitekniikka* ja *Assembly*.
Valmis dokumentti: [tietokonearkkitehtuuri.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearkkitehtuuri.pdf),
pikaopas: [tietokonearkkitehtuuri-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietokonearkkitehtuuri-pikaopas.pdf).

## Sisältö

1. Johdanto – rautalaki, Amdahl, teho ja energia, simulaattorin
   rakenne, testiohjelmat
2. Käskykanta – lataa–talleta, RISC-V:n laajennukset, R/I/S/B/U/J-
   koodaus ja purku, pseudokäskyt
3. Datapolku ja ohjaus – yksijaksoinen datapolku, ohjaussignaalit,
   monijaksoinen toteutus ja mikro-ohjelmointi
4. Liukuhihna – riippuvuudet, eteenpäinkytkentä, load–use,
   käskyjen ajoitus, syvyyden rajat
5. Haarautumisen ennustus – staattiset, 1- ja 2-bittiset, gshare,
   BTB ja paluuosoitepino; tarkkuus ja CPI mitattuina
6. Välimuistit – osoitteen jako, suora kuvaus ja joukkoassosiatiivisuus,
   korvauspolitiikat, 3C, esihaku
7. Kirjoitus ja muistihierarkia – WB/WT, AMAT, silmukoiden järjestys,
   DRAM ja kaista
8. Virtuaalimuisti ja MMU – Sv32-sivutaulun kävely, Sv39, sivuvirheet,
   TLB ja suuret sivut, VIPT
9. Poikkeukset, keskeytykset ja I/O – mtvec, mcause, mepc,
   ajastinkeskeytys, MMIO, DMA ja väylät
10. Moniytimet ja koherenssi – MESI, väärä jakaminen, atomiset
    operaatiot, muistimallit, NUMA
11. Superskalaarisuus ja epäjärjestys – nimeäminen, ROB, ILP-rajatutkimus,
    Spectre
12. RISC, CISC ja mikro-operaatiot – historia, µop-purku, fuusio,
    purun hinta
13. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on 19 C++23-esimerkkiä. Ne rakentuvat
yhteisen simulaattorin varaan (`esimerkit/yhteinen/`): RV32I-osajoukon
kokoaja ja purkaja, käskytason simulaattori, jälkiohjattu
liukuhihnamalli ennustimineen ja parametrisoitava välimuistimalli.
Simulaattori on deterministinen, joten käskymäärät, jaksot, CPI:t ja
osumasuhteet ovat joka ajolla samat. Testeissä jokainen esimerkki
käännetään GCC 14:llä ja Clang 20:llä varoitukset virheinä ja
sanitoijien kanssa, ja tulostetta verrataan `.odotettu`-tiedostoon.

```text
make testaa                # kaikki testit
make pdf                   # PDF:t
```

Kehityskontissa (`.devcontainer/tietokonearkkitehtuuri`) ovat
kääntäjät. Kuvaajat piirretään esimerkkien testatuista tulosteista
komennolla `make kuvat` (vaatii Matplotlibin); valmiit kuvat ovat
hakemistossa `kuvat/`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0.

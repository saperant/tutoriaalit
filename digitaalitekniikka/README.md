# Digitaalitekniikka

Tiivis suomenkielinen johdatus digitaalitekniikkaan: lukujen esitys
laitteistossa, logiikkaportit ja CMOS, Boolen algebra ja sieventäminen,
kombinaatiologiikka, summaimet ja ALU, viiveet ja hasardit, salvat ja
kiikut, rekisterit, tilakoneet, ajoitus ja pieni datapolku. Esitietona
on taito *Diskreetti matematiikka*.
Valmis dokumentti: [digitaalitekniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/digitaalitekniikka.pdf),
pikaopas: [digitaalitekniikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/digitaalitekniikka-pikaopas.pdf).

## Sisältö

1. Johdanto – abstraktiotasot, työkalut, invertteriketjun viive
2. Luvut bitteinä – kahden komplementti laitteistossa, Gray-koodi, BCD
3. Logiikkaportit – totuustaulut ja symbolit, NAND-universaalisuus,
   CMOS-kytkinmalli, kolmitila ja avoin nielu
4. Boolen algebra ja sieventäminen – lait, Karnaugh, Quine–McCluskey
5. Kombinaatiologiikan lohkot – multiplekseri, dekooderi,
   prioriteettikooderi, vertailija
6. Summaimet ja ALU – ripple-carry, carry-lookahead, liput N Z C V,
   siirrin ja kertoja
7. Viive ja hasardit – tapahtumapohjainen simulaattori, staattinen
   hasardi, summaimen viive simuloituna, kombinatorinen silmukka
8. Salvat ja kiikut – SR-salpa, D-salpa ja D-kiikku, metastabiilisuus
   ja MTBF
9. Rekisterit ja laskurit – sallinta, siirtorekisteri, rengas- ja
   Johnson-laskuri
10. Tilakoneet – Moore ja Mealy, taulusta logiikaksi, SystemVerilog
11. Ajoitus ja kellotus – kriittinen polku, pitoaika, liukuhihnoitus,
    kellon vino
12. Muistit ja datapolku – ROM, rekisteritiedosto, Fibonaccia laskeva
    datapolku
13. Lopuksi – nyrkkisäännöt, mallit ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on 15 Python-ohjelmaa ja 9 SystemVerilog-
esimerkkiä. Python-esimerkit (totuustaulut, Quine–McCluskey,
ajoitusanalyysi ja oma tapahtumapohjainen porttisimulaattori
`porttisim.py`) tarkistetaan ruffilla ja mypyllä (`--strict`).
SystemVerilog-esimerkit simuloidaan Verilatorilla (`-Wall`, varoitukset
virheinä), ja jokaisella on itsetarkistava testipenkki.

Kirjan ajoituskaaviot ovat tiedostoja `esimerkit/kaaviot/*.json`. Ne
tuotetaan simulaatiosta tai esimerkin tulosteesta, ja testi vertaa
tulosta tallennettuun. Porttisymbolit, CMOS-piirit ja kuvaajat piirtää
`kuvat/piirra.py` (`make kuvat`, vaatii Matplotlibin); kuvat ovat
versionhallinnassa.

## Rakentaminen

```text
make testaa    # rakenne ja esimerkit
make pdf       # tutoriaali ja pikaopas
make kuvat     # piirtää kuvat/*.png uudelleen
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

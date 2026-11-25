# Virtauslaskenta

Tiivis suomenkielinen tutoriaali nesteiden ja kaasujen virtauksen
laskennasta: säilymislaeista kontrollitilavuusmenetelmään,
advektiokaavioihin ja kokoonpuristumattoman virtauksen
Navier–Stokesin yhtälöihin. Kaikki toteutetaan itse NumPyllä ja
SciPyllä pienissä kaksiulotteisissa tehtävissä, ja jokainen tulos
tarkistetaan tarkkaa ratkaisua, tasetta tai hilavertailua vasten.
Tavoite on ymmärtää, mitä virtauslaskentaohjelma tekee, ja osata
arvioida sen tulosten luotettavuus. Valmiit dokumentit:
[virtauslaskenta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/virtauslaskenta.pdf)
ja pikaopas
[virtauslaskenta-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/virtauslaskenta-pikaopas.pdf).

Esitietona on *Fysikaalinen mallinnus ja simulointi*.

## Sisältö

1. Johdanto – rajakerros levyn yllä, esitiedot ja rajaus
2. Virtauksen yhtälöt – massan ja liikemäärän tase,
   kokoonpuristumattomuus, Reynoldsin luku
3. Kontrollitilavuusmenetelmä – ruutujen tase, säilyvyys, savuvana
   tuulessa
4. Advektio – neljä kaaviota, numeerinen diffuusio, rajoittimet
5. Advektio ja diffuusio yhdessä – hilan Péclet'n luku, väärä
   diffuusio
6. Paine ja porrastettu hila – shakkilautaongelma, projektio
7. Projektiomenetelmä – kirjasto `virta`, Taylorin ja Greenin pyörre,
   aika-askeleen rajat
8. Reunaehdot – seinä, sisään- ja ulosvirtaus, reunan paikan vaikutus
9. Kansivetoinen onkalo – vakiotehtävä, kolme hilaa, virhearvio
10. Virtaus esteen ohi – pyörrerata, Strouhalin luku, kaavion vaikutus
11. Turbulenssi – mittakaavat, suoran simuloinnin hinta, mallien
    periaate, seinän läheisyys
12. Ratkaisijat ja suppeneminen – jäännös, monihila, mitä oikeat
    ohjelmat tekevät toisin
13. Lopuksi – tarkistuslista, käsitteet valmiissa ohjelmissa,
    jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien tulosteet
make pdf      # virtauslaskenta.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit tarvitsevat Python-kirjastot NumPy ja SciPy (versiot
tiedostossa `pyproject.toml`). Kehityskontissa
(`.devcontainer/virtauslaskenta`) ne ovat valmiina. Esimerkkien
testiajo kestää runsaan minuutin; raskaimmat ovat onkalo ja
pyörrerata.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).

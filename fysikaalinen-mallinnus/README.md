# Fysikaalinen mallinnus ja simulointi

Tiivis suomenkielinen tutoriaali fysikaalisten ilmiöiden
mallintamisesta osittaisdifferentiaaliyhtälöillä: säilymislaista
yhtälöksi, diskretointi differenssi- ja elementtimenetelmällä,
yhtälöryhmän ratkaisu ja tuloksen tarkistaminen. Esimerkkeinä ovat
lämmönjohtuminen, värähtelevä kieli ja kalvo sekä lineaarinen
elastisuus. Jokainen menetelmä toteutetaan ensin itse NumPyllä ja
SciPyllä ja sitten scikit-fem-kirjastolla, ja jokainen tulos
tarkistetaan tarkkaa ratkaisua, tasetta tai kirjallisuusarvoa vasten.
Valmiit dokumentit:
[fysikaalinen-mallinnus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/fysikaalinen-mallinnus.pdf)
ja pikaopas
[fysikaalinen-mallinnus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/fysikaalinen-mallinnus-pikaopas.pdf).

Esitiedot ovat *Numeeriset menetelmät* ja *Differentiaaliyhtälöt ja
Laplace-muunnos*.

## Sisältö

1. Johdanto – mallinnuksen ketju, koko ketju yhdessä esimerkissä
2. Säilymislaista yhtälöksi – kontrollitilavuus, säilyvä muoto, lämpö-
   ja aaltoyhtälö, reunaehdot, dimensiottomat luvut
3. Differenssimenetelmä: tasapainotila – rajapinnat, haamupiste,
   viiden pisteen kaava
4. Lämpöyhtälö ajassa – stabiilisuusraja, implisiittinen Euler,
   Crank–Nicolson, Biot'n luku
5. Aallot ja CFL-ehto – kieli, dispersio, energian säilyminen, kalvon
   ominaistaajuudet spektristä
6. Elementtimenetelmä yhdessä ulottuvuudessa – heikko muoto,
   kantafunktiot, kokoaminen, virheen normit
7. Elementtimenetelmä tasossa – oma kirjasto `pienfem`, paikkatesti,
   kulmasingulariteetti, vuo- ja konvektioreunat
8. Sama kirjastolla – scikit-fem, toisen asteen elementit
9. Lineaarinen elastisuus – ulokepalkki, lukkiutuminen,
   jännityskeskittymä reiän reunalla
10. Ominaisvärähtelyt ja aikariippuvat tehtävät – massamatriisi,
    ominaisarvotehtävä, lämpeneminen ajassa
11. Verkot ja ratkaisijat – kolmion muoto, porrastettu verkko,
    täyttyminen ja iteraatiot
12. Verifiointi ja validointi – valmistettu ratkaisu, Richardsonin
    ekstrapolointi ja GCI, malli vastaan mittaus
13. Lopuksi – työnkulku, tarkistukset koottuna, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien tulosteet
make pdf      # fysikaalinen-mallinnus.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit tarvitsevat Python-kirjastot NumPy, SciPy, SymPy ja
scikit-fem (versiot tiedostossa `pyproject.toml`). Kehityskontissa
(`.devcontainer/fysikaalinen-mallinnus`) ne ovat valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).

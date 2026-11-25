# Differentiaaliyhtälöt ja Laplace-muunnos

Tiivis suomenkielinen tutoriaali dynaamisten järjestelmien
mallintamisesta ja ratkaisemisesta: taseet, ensimmäisen ja toisen
kertaluvun yhtälöt, värähtelijät ja resonanssi, yhtälöryhmät ja
tilaesitys, Laplace-muunnos ja siirtofunktio, stabiilisuus sekä
numeeriset ratkaisijat. Jokainen asia ratkaistaan analyyttisesti
SymPyllä ja Maximalla ja numeerisesti SciPyllä ja GNU Octavella, ja
tuloksia verrataan keskenään. Valmiit dokumentit:
[differentiaaliyhtalot.pdf](https://saperant.github.io/tutoriaalit/materiaalit/differentiaaliyhtalot.pdf)
ja pikaopas
[differentiaaliyhtalot-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/differentiaaliyhtalot-pikaopas.pdf).

Esitiedot ovat *Differentiaali- ja integraalilaskenta* ja
*Lineaarialgebra*.

## Sisältö

1. Johdanto – jäähtyvä kahvi kolmella työkalulla
2. Mallintaminen – kasvu, sekoitussäiliö, RC-piiri, aikavakio
3. Ensimmäisen kertaluvun yhtälöt – erottelu, integroiva tekijä,
   suuntakenttä, tasapainot, yksikäsitteisyys
4. Toisen kertaluvun yhtälöt – vaimennus, resonanssi, jousi-massa ja RLC
5. Yhtälöryhmät ja tilaesitys – ominaisarvot, matriisieksponentti,
   vaihetaso, heiluri
6. Laplace-muunnos – taulukko, alkuarvotehtävä, osamurrot, konvoluutio
7. Siirtofunktio ja vasteet – navat, askel- ja taajuusvaste, s- ja
   z-taso
8. Stabiilisuus – takaisinkytkentä, Routh–Hurwitz, Jacobin matriisi
9. Numeeriset ratkaisijat – Euler, RK4, `solve_ivp`, jäykät yhtälöt
10. Lopuksi – nyrkkisäännöt, työkalut rinnakkain, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkit, Maxima ja Octave
make pdf      # differentiaaliyhtalot.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Kehityskontissa (`.devcontainer/differentiaaliyhtalot`) kaikki työkalut
ovat valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).

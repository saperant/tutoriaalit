# Differentiaali- ja integraalilaskenta

Tiivis suomenkielinen tutoriaali insinöörimatematiikan ytimestä: raja-arvo
ja jatkuvuus, derivaatta ja sen sovellukset, integraali ja sen
sovellukset, sarjat ja Taylorin polynomit sekä usean muuttujan
derivaatat ja integraalit. Jokainen asia lasketaan käsin, tarkistetaan
symbolisesti SymPyllä ja Maximalla ja numeerisesti NumPylla ja SciPyllä.
Valmiit dokumentit:
[analyysi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/analyysi.pdf)
ja pikaopas
[analyysi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/analyysi-pikaopas.pdf).

Esitieto on *Matematiikan perusteet ohjelmallisesti*, jonka luku 2
esittelee työkalut.

## Sisältö

1. Johdanto – paikasta nopeus ja nopeudesta matka
2. Raja-arvo ja jatkuvuus – toispuoleiset raja-arvot, l'Hôpital,
   liukulukujen sudenkuopat
3. Derivaatta – erotusosamäärä ja sen virheet, derivoimissäännöt,
   implisiittinen derivointi
4. Derivaatan sovelluksia – ääriarvot, Newtonin menetelmä,
   linearisointi ja herkkyys
5. Integraali – Riemannin summat, analyysin peruslause,
   integrointitekniikat, epäoleelliset integraalit
6. Integraalin sovelluksia – numeerinen integrointi, ala, keskiarvo ja
   tehollisarvo, työ, energia ja todennäköisyys
7. Sarjat ja Taylorin polynomit – suppeneminen, jäännöstermi,
   approksimaatiot ja kirjastofunktiot
8. Usean muuttujan derivaatat – gradientti, gradienttimenetelmä,
   Hessen ja Jacobin matriisit
9. Moninkertaiset integraalit – integrointijärjestys, napakoordinaatit,
   Monte Carlo
10. Lopuksi – nyrkkisäännöt, työkalut rinnakkain, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkit ja Maxima-skriptit
make pdf      # analyysi.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Kehityskontissa (`.devcontainer/analyysi`) kaikki työkalut ovat valmiina.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).

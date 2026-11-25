# Matematiikan perusteet ohjelmallisesti

Tiivis suomenkielinen tutoriaali lukion pitkän matematiikan keskeisistä
sisällöistä insinööri- ja ohjelmointiopintojen alkuun: lausekkeet ja
yhtälöt, funktiot ja kuvaajat, eksponentti ja logaritmi, trigonometria,
vektorit ja analyyttinen geometria sekä lukujonot ja summat. Jokainen asia
lasketaan myös avoimen lähdekoodin työkaluilla: SymPyllä, NumPylla,
Matplotlibilla ja Maximalla. Luku 2 on työkalujen käsikirja, johon muut
tutoriaalit voivat viitata. Valmiit dokumentit:
[matematiikan-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/matematiikan-perusteet.pdf)
ja pikaopas
[matematiikan-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/matematiikan-perusteet-pikaopas.pdf).

## Sisältö

1. Johdanto – työkalut ja käsinlaskun tarkistus
2. Työkalut – SymPy, tarkat luvut ja liukuluvut, NumPy, Matplotlib,
   Maxima ja GNU Octave
3. Lausekkeet, yhtälöt ja epäyhtälöt – polynomit, rationaalilausekkeet,
   toisen asteen yhtälö ja kumoutuminen, yhtälöparit, itseisarvo;
   sovellus: pysähtymismatka
4. Funktiot ja kuvaajat – määrittely- ja arvojoukko, käänteisfunktio,
   paloittain määritelty funktio, puolitushaku, kuvaajan sudenkuopat
5. Eksponentti- ja logaritmifunktiot – kasvu, logaritmisäännöt,
   logaritminen asteikko, aikavakio mittauksista, desibelit
6. Trigonometria – yksikköympyrä, kaavojen tarkistus, yhtälöt,
   harmoninen värähtely ja vaihe
7. Vektorit ja analyyttinen geometria – pistetulo ja projektio, suorat,
   ympyrä; sovellus: törmäyksen tunnistus
8. Lukujonot, summat ja induktio – suljetut muodot, algoritmin työmäärä,
   koronkorko ja annuiteettilaina, induktion tarkistus
9. Lopuksi – nyrkkisäännöt, työkalut rinnakkain, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkit ja Maxima-skriptit
make pdf      # matematiikan-perusteet.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla, ja ne tarvitsevat
SymPyn (1.14), NumPyn ja Matplotlibin. Maxima-skriptit tarvitsevat
Maximan (Ubuntussa paketti `maxima`). Kehityskontissa kaikki on valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

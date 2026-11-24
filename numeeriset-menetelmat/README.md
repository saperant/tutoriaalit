# Numeeriset menetelmät

Tiivis suomenkielinen tutoriaali numeeristen menetelmien ytimestä:
virheet ja stabiilisuus, epälineaariset yhtälöt, interpolointi ja
sovitus, numeerinen derivointi ja integrointi, lineaariset yhtälöryhmät
suorin ja iteratiivisin menetelmin, differentiaaliyhtälöiden ratkaisijat
sekä optimointi. Jokainen menetelmä toteutetaan ensin itse ja sitten
kirjastolla, ja virheitä verrataan teoreettisiin rajoihin. Työkaluina
ovat NumPy, SciPy ja GNU Octave.
Valmiit dokumentit:
[numeeriset-menetelmat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/numeeriset-menetelmat.pdf)
ja pikaopas
[numeeriset-menetelmat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/numeeriset-menetelmat-pikaopas.pdf).

Esitiedot ovat *Differentiaali- ja integraalilaskenta* ja
*Lineaarialgebra*.

## Sisältö

1. Johdanto – virheen lähteet, työkalut, sama luku kahdella algoritmilla
2. Virheet ja stabiilisuus – ehtoluku, epästabiili rekursio,
   kumoutuminen, eteen- ja taaksepäinvirhe, Kahanin summa
3. Epälineaariset yhtälöt – puolitus, kiintopiste, Newton ja sekantti,
   kertaluvun mittaus, Wilkinsonin polynomi, yhtälöryhmät
4. Interpolointi ja sovitus – Newtonin muoto, Rungen ilmiö ja
   Tšebyšovin solmut, splinit, normaaliyhtälöt vs. QR
5. Numeerinen derivointi ja integrointi – optimaalinen askel,
   Richardson, kompleksiaskel, Gaussin kvadratuuri, adaptiivisuus,
   singulariteetit
6. Lineaariset yhtälöryhmät – tuenta, LU, Cholesky, QR ja SVD,
   ehtoluku ja virheraja
7. Harvat matriisit ja iteratiiviset menetelmät – CSR, Jacobi,
   Gauss–Seidel, liittogradientti, esiehdostus
8. Differentiaaliyhtälöiden ratkaisijat – kertaluvut, stabiilisuus,
   jäykkyys, adaptiivinen askel
9. Optimointi – kultainen leikkaus, gradientti- ja Newtonin menetelmä,
   BFGS, lineaarinen ja kokonaislukuoptimointi
10. Lopuksi – nyrkkisäännöt, Python ja Octave rinnakkain, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkit ja Octave-skriptit
make pdf      # numeeriset-menetelmat.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Kehityskontissa (`.devcontainer/numeeriset-menetelmat`) kaikki työkalut,
myös GNU Octave, ovat valmiina.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).

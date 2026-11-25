# Python ja C/C++ yhteen

Tiivis suomenkielinen tutoriaali C- ja C++-koodin liittämisestä
Python-ohjelmiin: milloin natiivikoodia tarvitaan, `ctypes` ja
C-rajapinnat, laajennusmoduulit pybind11:llä ja nanobindilla,
tyyppimuunnokset ja elinajat, NumPy-taulukot ilman kopiota, kutsun
hinta, tulkkilukko ja säikeet, Pythonin C-API ja viitelaskenta sekä
paketointi pyöriksi. Valmiit dokumentit:
[python-c-integraatio.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-c-integraatio.pdf)
ja pikaopas
[python-c-integraatio-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/python-c-integraatio-pikaopas.pdf).

Esitiedot: taidot *Python työkaluohjelmointiin* ja *Moderni C++*.

## Sisältö

1. Johdanto – milloin kielten rajaa tarvitaan, välineet ja liput
2. Mittaa ensin – profilointi, vektorointi, Numba ja Cython
3. C-kirjasto ctypesillä – tyypit, puskurit, `errno`,
   takaisinkutsut, kirjaston varaama muisti, cffi
4. C-rajapinta C++-kirjastolle – läpinäkymätön kahva, virhekoodit,
   näkyvyys, `weakref.finalize`
5. Laajennusmoduuli pybind11:llä – luokat, ominaisuudet,
   poikkeukset, tynkätiedostot
6. Muunnokset ja elinajat – kopio vai viite, paluuarvopolitiikat,
   `keep_alive`, Python-takaisinkutsut ja trampoliinit
7. nanobind – erot pybind11:een ja kutsun hinta
8. NumPy-taulukot ilman kopiota – askeleet, `noconvert`,
   C++:n muisti näkymänä, `nb::ndarray`
9. Kutsun hinta – alkio kerrallaan, lista ja taulukko
10. Tulkkilukko ja säikeet – GIL:n vapautus, C++-säikeet,
    vapaasäikeinen Python
11. Pythonin C-API ja viitelaskenta – uudet ja lainatut viitteet,
    virheet, rajoitettu API, kaatuneen tulkin tutkiminen
12. Paketointi ja jakelu – `pyproject.toml`, pyörät, manylinux,
    cibuildwheel, vakaa ABI
13. Lopuksi – nyrkkisäännöt, lähteet ja jatkotaidot

## Rakentaminen

```text
make testaa     # rakenne ja esimerkit (käännös, ruff, mypy --strict,
                # ajot, pyörän rakennus ja pytest)
make pdf        # tutoriaali ja pikaopas PDF:ksi
```

Esimerkit tarvitsevat Python 3.12:n kehitysotsakkeineen, GCC:n
(C++20), pybind11 3.1:n, nanobind 3.1:n, NumPyn, setuptoolsin (77 tai
uudempi) ja wheelin; tarkistukset ruffin, mypyn ja pytestin.
Kehityskontti: `.devcontainer/python-c-integraatio`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

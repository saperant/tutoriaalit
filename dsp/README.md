# Digitaalinen signaalinkäsittely

Tiivis suomenkielinen tutoriaali signaalinkäsittelyn menetelmistä
ohjelmoijalle ja insinöörille: FIR- ja IIR-suotimien suunnittelu
vaatimuksista, toteutus C:llä toisen asteen lohkoina ja
rengaspuskureilla, oma FFT, monitaajuuskäsittely, LMS-adaptiiviset
suotimet sekä lohkopohjainen reaaliaikakäsittely kiinteän pilkun
aritmetiikalla. Jokainen suodin suunnitellaan ja tarkistetaan Pythonilla
(NumPy, SciPy), toteutetaan C:llä ja verrataan Python-referenssiin
numeerisella toleranssilla. Valmiit dokumentit:
[dsp.pdf](https://saperant.github.io/tutoriaalit/materiaalit/dsp.pdf)
ja pikaopas
[dsp-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/dsp-pikaopas.pdf).

## Sisältö

1. Johdanto – työnkulku vaatimuksista C-toteutukseen
2. Vaatimukset ja toleranssit – vaatimukset tietona, liukulukujen erot
3. FIR: ikkunamenetelmä – Gibbsin ilmiö, ikkunat, Kaiserin kaavat
4. FIR: taajuusnäytteistys ja Parks–McClellan – tasavärähtely,
   lineaarivaiheiset tyypit I–IV, Hilbert-muunnin ja analyyttinen signaali
5. FIR-suodin C:llä – rengaspuskuri, tila, symmetria, ctypes-vertailu
6. IIR-suunnittelu – bilineaarimuunnos, esivääristys, suodintyypit
7. IIR-toteutus – toisen asteen lohkot, suoramuodot, kertoimien
   kvantisointi, rajasyklit
8. FFT, nopea konvoluutio ja Goertzel – radix-2 C:llä, overlap-save
9. Monitaajuuskäsittely – desimointi, interpolointi, polyfaasi,
   rationaalinen muunnos, CIC
10. Adaptiiviset suotimet – LMS, NLMS, askelkoko, häiriönpoisto
11. Reaaliaikakäsittely C:llä – lohkot, jonot, Q15, budjetti, latenssi
12. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, GCC ja Clang sanitoijineen,
              # esimerkkien ajot, C vs. Python -vertailu ja pytest
make pdf      # dsp.pdf ja dsp-pikaopas.pdf
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Python-esimerkit tarvitsevat Python 3.12:n, NumPyn ja SciPyn;
tarkistukseen tarvitaan ruff, mypy, scipy-stubs ja pytest. C-esimerkit
käännetään C23:lla (GCC 14 ja Clang 20). Kehityskontissa
(`.devcontainer/dsp`) kaikki on valmiina.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

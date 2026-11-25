# Signaalit ja järjestelmät

Tiivis suomenkielinen tutoriaali diskreettiaikaisista signaaleista ja
lineaarisista aikainvarianteista järjestelmistä ohjelmoijalle ja
insinöörille: näytteistys ja aliasointi, LTI-järjestelmät ja
impulssivaste, konvoluutio käytännössä, differenssiyhtälöt ja
rekursiiviset suotimet, Z-muunnos, navat ja nollat, taajuusvaste sekä
DFT:n ja STFT:n käytännön kysymykset. Jokainen tulos tarkistetaan
Pythonilla, NumPylla ja SciPyllä, ja luvun 11 suodinkirjasto testataan
pytestillä. Valmiit dokumentit:
[signaalit-ja-jarjestelmat.pdf](https://saperant.github.io/tutoriaalit/materiaalit/signaalit-ja-jarjestelmat.pdf)
ja pikaopas
[signaalit-ja-jarjestelmat-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/signaalit-ja-jarjestelmat-pikaopas.pdf).

## Sisältö

1. Johdanto – musta laatikko, merkinnät, työkalut
2. Diskreettiaikaiset signaalit – perussignaalit, energia ja teho,
   jaksollisuus, taajuuksien monikäsitteisyys
3. Näytteistys ja aliasointi – näytteistysteoreema, sinc-rekonstruktio,
   nollannen asteen pito, desimointi, kvantisointi
4. LTI-järjestelmät ja impulssivaste – ominaisuuksien testaus,
   konvoluutio, askelvaste, BIBO-stabiilisuus
5. Konvoluutio järjestelmissä – Toeplitz-matriisi, dekonvoluutio,
   overlap-add ja suotimen tila, ristikorrelaatio
6. Differenssiyhtälöt – FIR ja IIR, eksponentiaalinen keskiarvo,
   alkutila, resonaattori
7. Z-muunnos – suppenemisalue, siirtofunktio, navat ja nollat,
   stabiilisuus, toisen asteen lohkot, osamurrot
8. Taajuusvaste – DTFT, `freqz`, desibelit, geometria, ryhmäviive,
   lovisuodin (myös äänitiedostona)
9. DFT ja FFT käytännössä – resoluutio, vuotaminen, ikkunat, nollilla
   täyttö, nopea konvoluutio, Welchin menetelmä
10. Lyhytaikainen spektri – STFT ja aika–taajuus-kompromissi
11. Testaus – pytest, ominaisuus- ja referenssitestit, toleranssit
12. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkkien ajot ja pytest
make pdf      # signaalit-ja-jarjestelmat.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat NumPyn
ja SciPyn. Tarkistukseen tarvitaan ruff, mypy, scipy-stubs ja pytest
(kehityskontissa valmiina).

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

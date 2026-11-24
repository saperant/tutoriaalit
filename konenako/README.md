# Konenäkö (OpenCV)

Tiivis suomenkielinen tutoriaali konenäön klassisista menetelmistä
OpenCV:llä: kuvan rakenne ja värit, suodatus, reunat ja morfologia,
piirteet ja sovittaminen, geometriset muunnokset ja homografia,
kameramalli ja kalibrointi, epipolaarigeometria ja stereonäkö,
segmentointi ja seuranta, suorituskyky ja C++ sekä koneoppimisen
rajapinta. Kaikki kuvat ovat synteettisiä, joten jokainen tulos
tarkistetaan tunnettua vastausta vasten. Valmiit dokumentit:
[konenako.pdf](https://saperant.github.io/tutoriaalit/materiaalit/konenako.pdf)
ja pikaopas
[konenako-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/konenako-pikaopas.pdf).

## Sisältö

1. Johdanto – kolikoiden laskeminen, työkalut ja versiot
2. Digitaalinen kuva – taulukko, ylivuoto, BGR, HSV ja Lab,
   histogrammit, kynnystys
3. Suodatus – 2D-konvoluutio, reunakäsittely, erottuvat ytimet,
   kohinanpoisto, taajuustaso ja aliasointi
4. Reunat, morfologia ja muodot – Sobel, Canny, morfologia, ääriviivat,
   Hu-momentit
5. Piirteet ja sovittaminen – kulmat, alipikselitarkkuus, ORB ja SIFT,
   ratio-testi, RANSAC
6. Geometriset muunnokset – affiini, homografia ja DLT, interpolointi,
   panoraaman periaate
7. Kameramalli ja kalibrointi – neulanreikämalli, vääristymä,
   synteettinen kamera, kalibrointi, PnP
8. Epipolaarigeometria ja stereonäkö – essentiaalimatriisi, kameran
   liike, rektifiointi, SGBM ja syvyys
9. Segmentointi ja seuranta – watershed, Lucas–Kanade, Kalman-suodin
10. Suorituskyky ja C++ – vektorointi, sama ketju C++:lla
11. Koneoppimisen rajapinta – klassinen luokittelija, arviointi ja
    jakauman muutos, `dnn`-esikäsittely, IoU ja NMS
12. Lopuksi – nyrkkisäännöt, lähitaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkkien ajot, pytest, C++
make pdf      # konenako.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen esimerkeistä
```

Python-esimerkit toimivat Python 3.12:lla ja uudemmilla, ja ne
tarvitsevat NumPyn ja paketin `opencv-python-headless` (5.1).
C++-esimerkki käyttää Ubuntun pakettia `libopencv-dev` (OpenCV 4.6) ja
kääntäjiä GCC 14 ja Clang 20. Tarkistukseen tarvitaan ruff, mypy ja
pytest (kehityskontissa `.devcontainer/konenako` valmiina).

Lisenssi: CC BY-SA 4.0.

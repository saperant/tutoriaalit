# Kompleksiluvut ja Fourier-analyysi

Tiivis suomenkielinen signaalimatematiikan tutoriaali ohjelmoijalle ja
insinöörille: kompleksiluvut ja Eulerin kaava, sinimuotoiset signaalit
ja osoittimet, summat, sarjat ja ortogonaalisuus, Fourier-sarja ja
Fourier-muunnos, konvoluutio sekä diskreetti Fourier-muunnos
kannanvaihtona ja FFT:n idea. Jokainen analyyttinen tulos tarkistetaan
numeerisesti Pythonilla ja NumPylla. Valmiit dokumentit:
[signaalimatematiikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/signaalimatematiikka.pdf)
ja pikaopas
[signaalimatematiikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/signaalimatematiikka-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä taajuuksia signaalissa on, merkinnät, työkalut
2. Kompleksiluvut – laskutoimitukset, napaesitys, kertolasku kiertona,
   NumPy
3. Eulerin kaava ja kompleksinen eksponentti – sarja, yhtälö
   $z' = iz$, trigonometria, ykkösen juuret
4. Sinimuotoiset signaalit ja osoittimet – osoitinsumma, mittaus
   korrelaatiolla, interferenssi, huojunta
5. Summat, sarjat ja integraalit – geometrinen summa, Dirichlet'n ydin,
   ortogonaalisuus, teho, Parseval, desibelit
6. Fourier-sarja – kertoimet, kantti- ja saha-aalto, osasummat,
   energia, Gibbsin ilmiö
7. Fourier-muunnos – parit rect–sinc ja Gauss–Gauss, ominaisuudet,
   aika–taajuus-epätarkkuus
8. Konvoluutio – määritelmä, liukuva keskiarvo, konvoluutiolause,
   syklinen konvoluutio, taajuusvaste
9. DFT kannanvaihtona – DFT-matriisi, oma toteutus, taajuusindeksit,
   FFT
10. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien ajot
make pdf      # signaalimatematiikka.pdf ja pikaopas
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat
NumPyn. Tarkistukseen tarvitaan ruff ja mypy (kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.

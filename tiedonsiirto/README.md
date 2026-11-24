# Digitaalinen tiedonsiirto

Tiivis suomenkielinen tutoriaali siitä, miten bitit siirretään
kohinaisen kanavan yli: kantataajuusesitys, AM ja FM, PSK-, QAM- ja
FSK-modulaatiot, pulssinmuokkaus ja sovitettu suodin, kohina ja
bittivirhesuhde, OFDM, kantoaallon ja symbolien synkronointi sekä
kanavakoodauksen perusteet Viterbi-dekooderiin asti. Jokainen vaihe
simuloidaan Pythonilla kiinteällä satunnaissiemenellä ja verrataan
teoreettiseen tulokseen, ja lopuksi osat kootaan testatuksi
pakettilinkiksi. Valmiit dokumentit:
[tiedonsiirto.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tiedonsiirto.pdf)
ja pikaopas
[tiedonsiirto-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tiedonsiirto-pikaopas.pdf).

## Sisältö

1. Johdanto – koko siirtoketju pienenä, merkinnät
2. Kantataajuus ja kaistanpäästö – IQ-esitys, sekoitus, peilitaajuus
3. Analogiset modulaatiot – AM, DSB-SC, FM, Carsonin sääntö
4. Digitaaliset modulaatiot – PSK, QAM, Gray-koodaus, FSK ja MSK
5. Pulssinmuokkaus – Nyquistin ehto, RC ja RRC, silmäkuvio,
   sovitettu suodin
6. Kohina ja bittivirhesuhde – Eb/N0 ja SNR, teoria ja simulaatio,
   Shannonin raja, Rayleigh-häipymä ja diversiteetti
7. OFDM – IFFT, syklinen etuliite, taajuuskorjaus, huipputeho
8. Kantoaallon synkronointi – vaihe- ja taajuusvirhe, Costas-silmukka
9. Symboli- ja kehystahdistus – Gardnerin ilmaisin, korrelaatio
10. Kanavakoodaus – koodausvahvistus, pehmeä päätös, Viterbi, lomitus
11. Kokonainen linkki – pakettivastaanotin ja simulaation testaus
12. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict, esimerkkien ajot ja pytest
make pdf      # tiedonsiirto.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (matplotlib)
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat NumPyn
ja SciPyn. Tarkistukseen tarvitaan ruff, mypy, scipy-stubs ja pytest
(kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.

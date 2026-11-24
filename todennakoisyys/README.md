# Todennäköisyys ja tilastot

Tiivis suomenkielinen tutoriaali todennäköisyydestä ja tilastoista
insinöörille ja ohjelmoijalle: ehdollinen todennäköisyys ja Bayes,
diskreetit ja jatkuvat jakaumat, odotusarvo ja varianssi,
raja-arvolauseet, kohina, satunnaislukugeneraattorit, Monte Carlo,
estimointi ja luottamusvälit, A/B-testit sekä suorituskykymittausten
tulkinta. Jokainen kaava lasketaan koodilla ja tarkistetaan
simuloimalla. Valmiit dokumentit:
[todennakoisyys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/todennakoisyys.pdf)
ja pikaopas
[todennakoisyys-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/todennakoisyys-pikaopas.pdf).

## Sisältö

1. Johdanto – mihin todennäköisyyttä tarvitaan, merkinnät
2. Tapahtumat ja todennäköisyys – aksioomat, komplementti,
   syntymäpäiväongelma ja tunnisteiden törmäykset
3. Ehdollinen todennäköisyys ja Bayesin kaava – testitulokset,
   hälytykset, naiivi Bayes, riippumattomuus ja yhteiset vikasyyt
4. Diskreetit jakaumat – binomi, geometrinen ja Poisson
5. Jatkuvat jakaumat – tasainen, eksponentti ja normaali
6. Odotusarvo ja varianssi – lineaarisuus, toleranssien kasautuminen
7. Raja-arvolauseet – suurten lukujen laki, keskeinen raja-arvolause
8. Normaalijakauma ja kohina – SNR, keskiarvoistus, kohinan summautuminen
9. Satunnaislukugeneraattorit ja otanta – LCG, siemenet, käänteisfunktio
   ja hylkäysmenetelmä
10. Monte Carlo -menetelmät – virhe $1/\sqrt{n}$, ositus, korkeat ulottuvuudet
11. Estimointi ja luottamusvälit – harhattomuus, ML, bootstrap
12. Hypoteesitestaus ja A/B-testit – z- ja permutaatiotesti, sudenkuopat
13. Suorituskykymittausten tulkinta – persentiilit, toistot, häntäviive
14. Lopuksi – nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat Python-ohjelmia hakemistossa `esimerkit/`. Ne käyttävät
standardikirjastoa ja NumPya, ja jokainen simulaatio käyttää kiinteää
siementä. Kaikki tarkistetaan ruffilla ja mypyllä tiukassa tilassa,
ja tulosteita verrataan talletettuihin tulosteisiin:

```text
make testaa    # rakenne, tarkistukset ja esimerkkien ajo
make pdf       # tutoriaali ja pikaopas PDF:ksi
```

Kehityskontti: `.devcontainer/todennakoisyys`.

Lisenssi: CC BY-SA 4.0.

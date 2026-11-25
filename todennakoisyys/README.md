# Todennäköisyys ja tilastot

Tiivis suomenkielinen tutoriaali todennäköisyydestä ja tilastoista
insinöörille ja ohjelmoijalle: ehdollinen todennäköisyys ja Bayes,
diskreetit ja jatkuvat jakaumat, odotusarvo ja varianssi,
kovarianssi, korrelaatio ja regressio, raja-arvolauseet, kohina, satunnaislukugeneraattorit, Monte Carlo,
estimointi ja luottamusvälit, A/B-testit sekä suorituskykymittausten
tulkinta. Jokainen kaava lasketaan koodilla ja tarkistetaan
simuloimalla. Valmiit dokumentit:
[todennakoisyys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/todennakoisyys.pdf)
ja pikaopas
[todennakoisyys-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/todennakoisyys-pikaopas.pdf).

## Sisältö

1. Johdanto – mihin todennäköisyyttä tarvitaan, merkinnät
2. Tapahtumat ja todennäköisyys – aksioomat, komplementti, simulointi
   ja siemen, syntymäpäiväongelma ja tunnisteiden törmäykset
3. Ehdollinen todennäköisyys ja Bayesin kaava – testitulokset,
   hälytykset, riippumattomuus ja yhteiset vikasyyt, naiivi Bayes
4. Diskreetit jakaumat – odotusarvo ja varianssi, binomi, geometrinen
   ja Poisson
5. Jatkuvat jakaumat – tiheys- ja kertymäfunktio, tasainen,
   eksponentti ja normaali
6. Odotusarvo ja varianssi – laskusäännöt, toleranssien kasautuminen
7. Kaksi muuttujaa – yhteisjakauma, kovarianssi, korrelaatio,
   sekoittava tekijä, lineaarinen regressio ja jäännökset
8. Raja-arvolauseet – suurten lukujen laki, keskeinen raja-arvolause
9. Kohina ja signaali-kohinasuhde – SNR, keskiarvoistus, kohinan
   summautuminen, virhe kynnysilmaisussa
10. Satunnaislukugeneraattorit ja otanta – LCG, rinnakkaiset virrat,
    käänteisfunktio ja hylkäysmenetelmä
11. Monte Carlo -menetelmät – virhe $1/\sqrt{n}$, ositus, korkeat
    ulottuvuudet
12. Estimointi ja luottamusvälit – harhattomuus, ML, bootstrap
13. Hypoteesitestaus ja A/B-testit – z- ja permutaatiotesti, testin
    voima ja otoskoko, kahden keskiarvon vertailu, sudenkuopat
14. Suorituskykymittausten tulkinta – persentiilit, toistot, häntäviive
15. Lopuksi – nyrkkisäännöt, jatkotaidot ja lähteet

## Esimerkit

Esimerkit ovat Python-ohjelmia hakemistossa `esimerkit/`. Ne käyttävät
standardikirjastoa ja NumPya, ja jokainen simulaatio käyttää kiinteää
siementä. Kaikki tarkistetaan ruffilla ja mypyllä tiukassa tilassa,
ja tulosteita verrataan talletettuihin tulosteisiin:

```text
make testaa    # rakenne, tarkistukset ja esimerkkien ajo
make pdf       # tutoriaali ja pikaopas PDF:ksi
make kuvat     # piirtää kuvat uudelleen (Matplotlib)
```

Kehityskontti: `.devcontainer/todennakoisyys`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

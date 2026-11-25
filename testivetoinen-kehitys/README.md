# Testivetoinen kehitys ja testisuunnittelu

Miten testit kirjoitetaan niin, että ne löytävät virheet ja ohjaavat
suunnittelua: testivetoinen kehitys vaihe vaiheelta, tilan ja
vuorovaikutuksen testaus, ekvivalenssiluokat ja raja-arvot, päätöstaulut,
tilasiirtymät ja parittainen testaus, suoritettavat määrittelyt
(Gherkin ja pytest-bdd), ominaisuuspohjainen testaus (Hypothesis),
kattavuuden rajat ja mutaatiotestaus, testattava suunnittelu,
perintökoodin karakterisointi sekä testien laatu. Menetelmät esitetään
perusteluineen, rajoineen ja kritiikkeineen. Valmis dokumentti:
[testivetoinen-kehitys.pdf](https://saperant.github.io/tutoriaalit/materiaalit/testivetoinen-kehitys.pdf),
pikaopas:
[testivetoinen-kehitys-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/testivetoinen-kehitys-pikaopas.pdf).

Esitiedot: taidot *Python työkaluohjelmointiin* ja *Versionhallinta
(Git)*. Jatkotaito: *Jatkuva integraatio ja toimitus*.

## Sisältö

1. Johdanto – menetelmät, rajaus, sanasto, esimerkkien ajaminen
2. Testivetoinen kehitys – punainen, vihreä, refaktorointi; kolmiointi
3. TDD suunnittelun välineenä – sisältä ulos ja ulkoa sisään, mockit,
   milloin TDD ei kannata, tutkimusnäyttö
4. Ekvivalenssiluokat ja raja-arvot
5. Päätöstaulut, tilat ja parit
6. Suoritettavat määrittelyt ja BDD – esimerkkikartoitus, Gherkin,
   askelmäärittelyt, hyvä ja huono tapaus
7. Ominaisuuspohjainen testaus – edestakaisuus, invariantti, oraakkeli,
   pienentäminen, tilakonetesti
8. Kattavuus ja mutaatiotestaus – oma mutaattori, ekvivalentti mutantti
9. Testattava suunnittelu – saumat, puhdas ydin ja ohut kuori, aika ja
   satunnaisuus
10. Perintökoodi ja karakterisointitestit – kultainen tiedosto
11. Hyvä testi – testihajut, rakenne, nimeäminen, testidata
12. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on yksi pytest-projekti aihetta kohden:

- `02-tdd/` – ostoskori kahdeksassa vaiheessa
- `03-tyylit/` – kassa: tilan ja vuorovaikutuksen testit ennen
  refaktorointia ja sen jälkeen
- `04-rajat/`, `05-paatostaulu/`, `05-tilat/`, `05-parit/` – sama
  testisarja oikeaa ja viallista toteutusta vasten
- `06-bdd/` – suomenkielinen Gherkin ja pytest-bdd
- `07-ominaisuudet/`, `07-tilakone/` – Hypothesis
- `08-mutaatiot/` – sadan rivin mutaatiotestaaja ja kaksi testisarjaa
- `09-saumat/` – sama logiikka ennen ja jälkeen riippuvuuksien erottamisen
- `10-perinto/` – kultainen tiedosto ja refaktorointi sen turvin
- `11-hajut/` – haiseva testi ja sen siistitty versio

Useassa esimerkissä on tarkoituksella epäonnistuvia testejä: ne
näyttävät, minkä vian menetelmä löytää. Siksi tarkistus vertaa testien
tuloksia tallennettuihin (`odotettu`) eikä katso pytestin paluuarvoa.

```text
make -C esimerkit              # ruff, mypy ja kaikki esimerkit
make -C esimerkit 04-rajat     # yksi esimerkki
make -C esimerkit paivita      # kirjoita odotetut tulokset uudelleen
```

Esimerkit tarvitsevat Python 3.12:n tai uudemman sekä paketit pytest,
pytest-bdd 9.0.1, hypothesis 6.170.17 ja coverage 7.17.5; tarkistukseen
lisäksi ruff ja mypy. Kehityskontissa
(`.devcontainer/testivetoinen-kehitys`) ne ovat valmiina.

## Rakentaminen

```text
make testaa     # esimerkit ja rakenteen tarkistus
make pdf        # testivetoinen-kehitys.pdf ja pikaopas
make kuvat      # piirtää kuvan kuvat/parit.png uudelleen
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.

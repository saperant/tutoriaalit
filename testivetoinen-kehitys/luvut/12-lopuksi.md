# Lopuksi {.runko-lahteet}

Tutoriaalin menetelmät vastaavat eri kysymyksiin, ja siksi ne
täydentävät toisiaan:

| Kysymys | Menetelmä | Luku |
|--------------------------------|--------------------------------|:----:|
| Miten pidän askeleet pieninä ja koodin testattavana? | TDD | 2, 3 |
| Mitkä tapaukset valitsen? | luokat, rajat, taulut, tilat, parit | 4, 5 |
| Ymmärsimmekö vaatimuksen samoin? | esimerkkikartoitus ja Gherkin | 6 |
| Mitä en tullut ajatelleeksi? | ominaisuustestit | 7 |
| Huomaisivatko testit virheen? | mutaatiotestaus | 8 |
| Miksi tätä on vaikea testata? | saumat, puhdas ydin | 9 |
| Miten muutan koodia, jolla ei ole testejä? | karakterisointi | 10 |
| Voiko tähän testiin luottaa? | testien laatu | 11 |

## Nyrkkisäännöt

1. **Katso testin epäonnistuvan.** Testi, joka ei ole koskaan ollut
   punainen, ei ole todistanut mitään.
2. **Pieni askel, nopea palaute.** Tutkimusnäytön mukaan tämä on
   TDD:n vaikuttava osa.
3. **Testaa käytöstä, älä toteutusta.** Tulos julkisen rajapinnan
   kautta; vuorovaikutus vain, kun kutsu itse on vaatimus.
4. **Virheet asuvat rajoilla.** Jokainen raja molemmilta puolilta, myös
   ne, joita määrittely ei mainitse.
5. **Tee taulu ennen koodia.** Päätöstaulu ja siirtymätaulu paljastavat
   aukot määrittelystä.
6. **Esimerkit ensin, työkalu sitten.** BDD:n hyöty on keskustelussa.
7. **Kirjoita väite kaikista syötteistä, kun sellainen on.**
   Edestakaisuus, invariantti, oraakkeli.
8. **Kattavuudesta luetaan aukot, mutanteista testien heikkoudet.**
   Kumpikaan luku ei ole tavoite.
9. **Päätökset ytimeen, sivuvaikutukset kuoreen.** Aika ja satunnaisuus
   argumentteina.
10. **Ennen kuin muutat, kirjaa nykyinen käytös.** Refaktorointi ja
    käytöksen muutos erikseen.
11. **Epävakaa testi korjataan tai poistetaan.** Testisarjan arvo on
    siinä, että punaiseen luotetaan.

## Mitä jäi pois

- **Fuzzaus.** Ominaisuustestin sukulainen, jossa syötteitä ohjaa
  kattavuus ja väite on yleensä "ohjelma ei kaadu": taito
  *Haavoittuvuuksien analyysi ja torjunta*.
- **Suorituskyky- ja kuormatestit** sekä tutkiva testaus, jossa ihminen
  etsii vikoja ilman käsikirjoitusta. Automaattiset testit eivät korvaa
  kumpaakaan.
- **Muodollinen todistaminen.** Ominaisuustesti kokeilee satoja
  syötteitä, todistus kattaa kaikki. Laitteistopuolella menetelmä on
  arkipäivää: taito *Laitteiston verifiointi*.

## Jatkotaidot

- *Integraatiotestaus ja Testcontainers*: testit oikeaa tietokantaa ja
  muita palveluja vasten. Tämä tutoriaali pysyi yksikkötason
  tekniikoissa.
- *Jatkuva integraatio ja toimitus*: testien ajaminen toimitusputkessa
  eli mitä ajetaan milloin, miten hitaat testit jaetaan ja miten
  epäonnistunut ajo pysäyttää toimituksen.

## Lähteet

Kirjat:

- Beck, K. *Test-Driven Development: By Example.* Addison-Wesley, 2002.
- Freeman, S. ja Pryce, N. *Growing Object-Oriented Software, Guided by
  Tests.* Addison-Wesley, 2009. (Ulkoa sisään -tyyli.)
- Feathers, M. *Working Effectively with Legacy Code.* Prentice
  Hall, 2004. (Saumat, karakterisointitestit.)
- Fowler, M. *Refactoring: Improving the Design of Existing Code.*
  Toinen painos. Addison-Wesley, 2018.
- Meszaros, G. *xUnit Test Patterns: Refactoring Test Code.*
  Addison-Wesley, 2007. (Testihajut, testikaksoisten nimet.)
- Khorikov, V. *Unit Testing Principles, Practices, and Patterns.*
  Manning, 2020. (Hyvän testin neljä ominaisuutta.)
- Myers, G. J., Sandler, C. ja Badgett, T. *The Art of Software
  Testing.* 3. painos. Wiley, 2011. (Ekvivalenssiluokat ja raja-arvot.)
- Adzic, G. *Specification by Example.* Manning, 2011.
- ISTQB. *Certified Tester Foundation Level Syllabus*, versio 4.0, 2023.
  (Testisuunnittelutekniikoiden nimet.) <https://www.istqb.org/>

Artikkelit ja esitykset:

- Fowler, M. *Mocks Aren't Stubs.* martinfowler.com, 2007.
- Fowler, M. *StranglerFigApplication.* martinfowler.com, 2004.
- Bernhardt, G. *Boundaries.* Esitys, SCNA 2012. (Puhdas ydin ja
  imperatiivinen kuori.)
- North, D. *Introducing BDD.* Better Software, 2006.
- Wynne, M. *Introducing Example Mapping.* cucumber.io, 2015.
- Kuhn, D. R., Wallace, D. R. ja Gallo, A. M. *Software Fault
  Interactions and Implications for Software Testing.* IEEE
  Transactions on Software Engineering 30(6), 2004. (Parittaisen
  testauksen perustelu.)
- Claessen, K. ja Hughes, J. *QuickCheck: A Lightweight Tool for Random
  Testing of Haskell Programs.* ICFP 2000.
- MacIver, D. R., Hatfield-Dodds, Z. ym. *Hypothesis: A new approach to
  property-based testing.* Journal of Open Source Software 4(43), 2019.
- DeMillo, R. A., Lipton, R. J. ja Sayward, F. G. *Hints on Test Data
  Selection: Help for the Practicing Programmer.* IEEE Computer
  11(4), 1978. (Mutaatiotestauksen perusta.)
- Just, R. ym. *Are Mutants a Valid Substitute for Real Faults in
  Software Testing?* FSE 2014.
- Inozemtseva, L. ja Holmes, R. *Coverage Is Not Strongly Correlated
  with Test Suite Effectiveness.* ICSE 2014.
- Petrović, G. ja Ivanković, M. *State of Mutation Testing at Google.*
  ICSE-SEIP 2018.

Tutkimus TDD:n vaikutuksista:

- Nagappan, N., Maximilien, E. M., Bhat, T. ja Williams, L. *Realizing
  quality improvement through test driven development: results and
  experiences of four industrial teams.* Empirical Software Engineering
  13(3), 2008.
- Rafique, Y. ja Mišić, V. B. *The Effects of Test-Driven Development on
  External Quality and Productivity: A Meta-Analysis.* IEEE Transactions
  on Software Engineering 39(6), 2013.
- Fucci, D., Erdogmus, H., Turhan, B., Oivo, M. ja Juristo, N. *A
  Dissection of the Test-Driven Development Process: Does It Really
  Matter to Test-First or to Test-Last?* IEEE Transactions on Software
  Engineering 43(7), 2017.

Työkalujen dokumentaatio:

- pytest. <https://docs.pytest.org/>
- pytest-bdd. <https://pytest-bdd.readthedocs.io/>
- Cucumber. *Gherkin Reference.* <https://cucumber.io/docs/gherkin/>
- Hypothesis. <https://hypothesis.readthedocs.io/>
- coverage.py. <https://coverage.readthedocs.io/>
- Python. *ast – Abstract Syntax Trees* ja *unittest.mock.*
  <https://docs.python.org/3/library/>

Esimerkkien kirjastot: pytest (MIT), pytest-bdd (MIT), Hypothesis
(MPL-2.0), coverage.py (Apache-2.0), mypy (MIT) ja ruff (MIT).

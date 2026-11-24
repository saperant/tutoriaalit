# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

- **Tarkista väite koodilla.** Pienillä arvoilla luettelo on hidas
  mutta ilmeisen oikea. Se ei todista mitään, mutta se kumoaa väärän
  väitteen sekunnissa.
- **Todista kaikille, testaa esimerkeillä.** Induktio ja invariantit
  perustelevat, miksi koodi toimii kaikilla syötteillä; testit
  varmistavat, että toteutus vastaa perustelua.
- **Kysy kaksi kysymystä ennen laskemista.** Merkitseekö järjestys?
  Sallitaanko toisto? Ne valitsevat kombinatoriikan kaavan.
- **Nimeä rakenne.** Kun tunnistat ongelmasta joukon, relaation,
  graafin, puun tai kongruenssin, saat käyttöösi sen teorian ja
  valmiit algoritmit.
- **Erota helppo ja vaikea.** Euler ja Hamilton, kaksijakoisuus ja
  väritys: samannäköiset ongelmat voivat olla eri vaikeusluokissa.
  Tunnista NP-vaikea ongelma ennen kuin yrität tarkkaa ratkaisua.
- **Käytä tarkkaa aritmetiikkaa.** Kombinatoriikka ja lukuteoria
  lasketaan kokonaisluvuilla; liukuluvut kuuluvat jatkuvaan
  matematiikkaan.

## Yhteenveto käsitteistä

| Käsite | Ohjelmointivastine | Luku |
|--------|-------------------|------|
| ekvivalenssi, De Morgan | ehtojen refaktorointi | Propositiologiikka |
| $\forall$, $\exists$ | `all`, `any` | Predikaatit ja SAT |
| CNF, SAT | rajoiteratkaisijat | Predikaatit ja SAT |
| joukko, potenssijoukko | `set`, bittimaskit | Joukot ja funktiot |
| injektio, bijektio | koodaus ja purku, hajautus | Joukot ja funktiot |
| ekvivalenssirelaatio | ryhmittely avaimella | Relaatiot |
| osittainen järjestys | topologinen järjestys | Relaatiot |
| induktio, invariantti | rekursion ja silmukan oikeellisuus | Todistaminen |
| rekursioyhtälö | aikavaativuus | Rekursio |
| $\binom{n}{k}$, $n^k$ | testitapaukset, salasanat | Kombinatoriikka |
| $a \bmod m$, $a^{-1}$ | tarkisteet, salaus | Modulaariaritmetiikka |
| graafi, väritys | verkot, aikataulut | Graafit |
| puu | hakemistot, jäsennyspuut | Puut |

## Jatkotaidot taitopuussa

- *Tietorakenteet* ja *Algoritmit*: hakupuut, keot, hajautustaulut,
  lyhimmät polut, dynaaminen ohjelmointi ja vaativuusanalyysi
  rakentuvat suoraan tämän tutoriaalin rekursioyhtälöille, graafeille
  ja puille.
- *Todennäköisyys ja tilastot*: kombinatoriikka on diskreetin
  todennäköisyyden perusta.
- *Kryptografia* (valmis): modulaariaritmetiikka, käänteisalkiot,
  Fermat'n lause ja kiinalainen jäännöslause ovat RSA:n ja
  Diffie–Hellmanin perusta.
- *Digitaalitekniikka* (valmis): Boolen algebra ja normaalimuodot ovat
  logiikkapiirien suunnittelun kieli.
- *Kääntäjätekniikka*: jäsennyspuut, graafien väritys rekisterien
  varauksessa ja kiintopisteiteraatio.

## Lähteet ja lisälukemista

- Eric Lehman, F. Thomson Leighton ja Albert R. Meyer: *Mathematics for
  Computer Science*. MIT, avoin oppikirja (CC BY-SA 3.0),
  <https://courses.csail.mit.edu/6.042/spring18/mcs.pdf>. Tämän
  tutoriaalin aihepiirit kattava perusteos.
- Oscar Levin: *Discrete Mathematics: An Open Introduction*. Avoin
  oppikirja (CC BY-SA 4.0), <https://discrete.openmathbooks.org/>.
- Kenneth H. Rosen: *Discrete Mathematics and Its Applications*.
  McGraw-Hill. Laaja ja esimerkkirikas oppikirja.
- Ronald L. Graham, Donald E. Knuth ja Oren Patashnik: *Concrete
  Mathematics*. Addison-Wesley, 1994. Summat, rekursioyhtälöt ja
  kombinatoriikka syvällisesti.
- Thomas H. Cormen ym.: *Introduction to Algorithms*. MIT Press.
  Master-lause, silmukkainvariantit ja graafialgoritmit.
- Armin Biere ym. (toim.): *Handbook of Satisfiability*. IOS Press,
  2021. SAT-ratkaisijoiden tekniikat.
- Python-dokumentaatio: `itertools`-, `math`- ja `functools`-moduulit,
  <https://docs.python.org/3/library/>.
- Finanssiala: viitenumeron ja IBANin tarkisteet,
  <https://www.finanssiala.fi/>; Digi- ja väestötietovirasto:
  henkilötunnuksen rakenne, <https://dvv.fi/henkilotunnus>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähteiden sisältöä ei ole kopioitu; niihin viitataan.

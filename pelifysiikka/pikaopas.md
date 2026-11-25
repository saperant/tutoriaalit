---
title: Pelifysiikka
subtitle: Jäykät kappaleet, rajoitteet ja pehmeät kappaleet tiiviisti
lang: fi
---

# Tavoite

Uskottava, stabiili ja ajoissa. Tarkkuus ei ole tavoite; räjähtämätön
simulaatio kiinteässä aikabudjetissa on.

# Jäykän kappaleen tila

| Suure | Tallennus |
|-------|-----------|
| paikka, asento | massakeskipiste, yksikkökvaternio |
| nopeudet | $\mathbf v$, $\boldsymbol\omega$ maailmassa |
| massa | käänteismassa; 0 = liikkumaton |
| hitaus | päähitausmomentit; maailmassa $R\,I\,R^{\mathsf T}$ |

- Pisteen nopeus: $\mathbf v + \boldsymbol\omega \times \mathbf r$.
- Impulssi $\mathbf J$ pisteeseen: $\Delta\mathbf v = \mathbf J/m$,
  $\Delta\boldsymbol\omega = I^{-1}(\mathbf r \times \mathbf J)$.
- Vääntömomentti: $\boldsymbol\tau = \mathbf r \times \mathbf F$.

# Askel

1. Voimat nopeuksiin (puoli-implisiittinen Euler).
2. Laaja vaihe: AABB-parit, aina samassa järjestyksessä.
3. Kapea vaihe: monisto = normaali + pisteet + syvyydet.
4. Valmistelu: teholliset massat, tavoitenopeudet, lämmin käynnistys.
5. Kierrokset: nivelet, kitka, normaalit viimeisenä.
6. Paikat ja asennot uusilla nopeuksilla; normalisoi kvaternio.
7. Saaret ja lepotila.

Kiinteä askel (1/60 s) ja kerryttäjä. Renderöinti interpoloi.

# Kosketukset

| Pari | Menetelmä |
|------|-----------|
| pallo–pallo, pallo–taso | etäisyys ja säde |
| pallo–laatikko | lähin piste laatikon koordinaatistossa |
| laatikko–laatikko | 15 erotteluakselia; tahkon leikkaus tai särmäpari |
| yleinen kupera | GJK (etäisyys) ja EPA (syvyys) |

Marginaali: kosketus luodaan jo ennen pintojen kohtaamista.
Sama piste askeleesta toiseen = impulssin voi periä.

# Ratkaisija

```{.cpp tiedosto="esimerkit/yhteinen/ratkaisija.hpp" osa="normaali"}
```

- Rajaa **kertynyt** impulssi: normaali ≥ 0, kitka ≤ μ · normaali.
- Tavoitenopeus: kimmoisuus (vain kovat osumat), Baumgarte
  `beta / dt * max(0, syvyys - vara)`, rako `syvyys / dt`.
- Lämmin käynnistys: edellisen askeleen impulssit heti alussa.
- Kitkapyramidi: kaksi tangenttia; vinoon jopa 41 % liikaa.

# Nivelet

| Nivel | Rivejä | Poistaa |
|-------|--------|---------|
| etäisyys | 1 | etäisyyden muutoksen |
| pallonivel | 3 | kiinnityspisteiden eron |
| sarana | 5 | lisäksi kaksi kiertoakselia |

Yksirivisen rajoitteen kertymä on skalaari. Nivelellä yhdistetyt
kappaleet eivät törmää toisiinsa.

# Oire ja korjaus

| Oire | Korjaus |
|------|---------|
| pino valuu tai kaatuu | lämmin käynnistys, kierroksia, aliaskeleita |
| kappale tärisee levossa | marginaali, vara, pysyvä monisto |
| ponnahdus limityksestä | pienempi beta, korjausnopeuden katto |
| ketju venyy | aliaskeleet, massasuhde < 10:1 |
| energia kasvaa | tarkista integrointijärjestys ja impulssien rajaus |
| luoti menee läpi | pyyhkäisy ja osuma-aika nopeille kappaleille |
| lepäävä pino kuluttaa aikaa | saaret ja nukahtaminen |

# Lepotila

- Saari: kosketusten ja nivelten yhdistämät kappaleet; liikkumaton
  kappale ei yhdistä.
- Saari nukahtaa, kun jokainen kappale on ollut kynnysten alla
  lepoajan. Herätys: osuma, nivelen muutos, voima, alta poistuva tuki.

# Nopeat kappaleet

- Diskreetti testi pettää, kun matka askeleessa ylittää säteen ja
  esteen puolipaksuuden summan.
- Osuma-aika: säde säteellä paisutettua estettä vastaan; siirrä vain
  osumaan asti. Ota käyttöön kappalekohtaisesti.
- Ennakoiva kosketus: rivi sallii lähestymisen vain raon verran.

# Kangas ja köysi (PBD)

1. Ennusta paikat nopeuksista.
2. Toista: siirrä hiukkasia, kunnes etäisyydet ja törmäykset
   toteutuvat; jaa korjaus käänteismassojen suhteessa.
3. Nopeus = (uusi paikka − vanha paikka) / dt.

Jäykkä jousi + eksplisiittinen askel räjähtää, kun
$\sqrt{k/m}\,\Delta t \gtrsim 2$. PBD ei räjähdä; jäykkyys tulee
kierroksista (XPBD: myötäävyydestä).

# Vesi ja hiukkaset

- Korkeuskenttä: `v += dt * c² / dx² * (naapurit − 4h)`, sitten
  `h += dt * v`. Ehto: $c\,\Delta t/\Delta x \le 1/\sqrt2$.
- Noste = syrjäytetyn veden paino; lisää vastus.
- Hiukkasallas: kiinteä koko, kuollut korvataan viimeisellä elävällä,
  oma satunnaislukugeneraattori.

# Determinismi

- Kiinteä askel, kiinteä käsittelyjärjestys, ei osoitinjärjestystä.
- Tilannevedokseen myös kertyneet impulssit, lepolaskurit ja
  satunnaislukujen tila.
- FMA pois (`-ffp-contract=off`), ei `-ffast-math`; kirjastofunktiot
  pois simulaatiopolulta.
- Testi: tilan tiiviste samasta syötteestä joka alustalla.

# Asetukset moottoreissa

| Asetus | Vastine |
|--------|---------|
| *velocity / position iterations*, *substeps* | kierrokset, aliaskeleet |
| *contact offset*, *speculative distance* | kosketusmarginaali |
| *slop*, *contact hertz* | sallittu tunkeuma, sijainnin korjaus |
| *sleep threshold* | lepokynnys ja lepoaika |
| CCD, *bullet*, *motion quality* | jatkuva törmäystunnistus |
| *collision layers*, *filter* | parien suodatus laajassa vaiheessa |

# Fysiikkatestit

liikemäärä ja liikemäärämomentti säilyvät · energia ei kasva · pino
pysyy levossa · heilurin jakso vastaa kaavaa · sama syöte, samat bitit

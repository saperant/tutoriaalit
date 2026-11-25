# Propositiologiikka

Propositio on väite, joka on joko tosi tai epätosi: ”tilaus on
maksettu”, ”asiakas on kanta-asiakas”. Propositiologiikka tutkii,
miten tällaisista väitteistä rakennetaan monimutkaisempia
konnektiiveilla ja milloin kaksi rakennelmaa tarkoittaa samaa.
Ohjelmoijalle tämä on arkea: jokainen `if`-lause on propositio, ja
jokainen ehdon uudelleenkirjoitus on loogisen ekvivalenssin käyttöä,
oli se tietoista tai ei.

## Konnektiivit ja totuustaulut

Propositiomuuttujat $p, q, r, \ldots$ saavat arvon tosi (1) tai
epätosi (0). Niistä muodostetaan kaavoja konnektiiveilla:

| Konnektiivi | Merkintä | Tosi, kun | Python |
|-------------|----------|-----------|--------|
| negaatio | $\neg p$ | $p$ on epätosi | `not p` |
| konjunktio | $p \land q$ | molemmat tosia | `p and q` |
| disjunktio | $p \lor q$ | ainakin toinen tosi | `p or q` |
| implikaatio | $p \to q$ | ei ($p$ tosi ja $q$ epätosi) | `(not p) or q` |
| ekvivalenssi | $p \leftrightarrow q$ | samat arvot | `p == q` |
| poissulkeva tai | $p \oplus q$ | eri arvot | `p != q` |

Kaavan merkitys määritellään **totuustaululla**, joka luettelee kaikki
muuttujien arvoyhdistelmät. Muuttujia ollessa $n$ rivejä on $2^n$.
Johdannon funktio `totuustaulu` tuotti implikaation taulun:

```{.tuloste tiedosto="esimerkit/02-totuustaulu.odotettu" rivit="1-5"}
```

Implikaatio yllättää usein:
$p \to q$ on tosi aina, kun $p$ on epätosi. Väite ”jos sataa, kadut
kastuvat” ei valehtele poutapäivänä, vaikka kadut olisivat kuivat tai
märät. Ohjelmassa implikaatio näkyy ehtona ”jos alennus on käytössä,
alennusprosentin on oltava välillä 0–100”: tarkistus on läpäisty
aina, kun alennusta ei käytetä.

## Ekvivalenssit

Kaavat $A$ ja $B$ ovat **loogisesti ekvivalentit**, $A \equiv B$, jos
niillä on sama totuusarvo kaikilla muuttujien arvoilla. **Tautologia**
on tosi kaikilla arvoilla ja **ristiriita** epätosi kaikilla. Koska
muuttujia on äärellinen määrä, ekvivalenssin voi aina tarkistaa
käymällä läpi kaikki $2^n$ yhdistelmää:

```{.python tiedosto="esimerkit/02-totuustaulu.py" osa="ekvivalenssi"}
```

```{.tuloste tiedosto="esimerkit/02-totuustaulu.odotettu" rivit="6-"}
```

Tuloste vahvistaa tärkeimmät lait ja paljastaa yleisen
virheen: implikaation **käänteinen** $q \to p$ ei ole sama kuin
$p \to q$, mutta **kontrapositio** $\neg q \to \neg p$ on. Kolme
viimeistä riviä ovat päättelysääntöjä, joihin palataan luvussa
*Todistaminen ja invariantit*. Keskeiset
lait kannattaa osata ulkoa, koska ne ovat refaktoroinnin perustyökaluja:

| Laki | Muoto |
|------|-------|
| De Morgan | $\neg(p \land q) \equiv \neg p \lor \neg q$, $\neg(p \lor q) \equiv \neg p \land \neg q$ |
| kaksoisnegaatio | $\neg\neg p \equiv p$ |
| osittelu | $p \land (q \lor r) \equiv (p \land q) \lor (p \land r)$ |
| absorptio | $p \lor (p \land q) \equiv p$ |
| implikaatio | $p \to q \equiv \neg p \lor q$ |
| kontrapositio | $p \to q \equiv \neg q \to \neg p$ |
| vaihdanta ja liitäntä | $p \land q \equiv q \land p$, $(p \lor q) \lor r \equiv p \lor (q \lor r)$ |

De Morganin laki on käytännössä tärkein: negaation vieminen sulkeiden
sisään vaihtaa jokaisen ”ja”-sanan ”tai”-sanaksi ja päinvastoin. Ehto
`not (on_kirjautunut and on_admin)` tarkoittaa ”ei ole kirjautunut tai
ei ole ylläpitäjä”, ei ”ei ole kirjautunut eikä ylläpitäjä”.

## Ehtolausekkeen sieventäminen

Vuosien muutokset jättävät koodiin ehtoja, joiden merkitystä on
vaikea nähdä. Seuraava funktio päättää, onko toimitus ilmainen:

```{.python tiedosto="esimerkit/02-ehtolauseke.py" osa="alkuperainen"}
```

Totuustaulusta näkee, että kanta-asiakas saa aina ilmaisen
toimituksen ja muut vain suurilla kotimaan tilauksilla. Ehto
sievenee yhdeksi lausekkeeksi:

```{.python tiedosto="esimerkit/02-ehtolauseke.py" osa="sievennetty"}
```

Sievennyksen oikeellisuutta ei tarvitse uskoa: kolmella muuttujalla
syötteitä on kahdeksan, ja ne kaikki voi verrata. Sama totuustaulu
antaa myös kaavan **disjunktiivisen normaalimuodon** (DNF): jokainen
rivi, jolla tulos on tosi, on yksi konjunktio, ja konjunktiot
yhdistetään disjunktiolla.

```{.python tiedosto="esimerkit/02-ehtolauseke.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/02-ehtolauseke.odotettu"}
```

Normaalimuodot ovat kaavojen vakiomuotoja:

- **DNF** on konjunktioiden disjunktio, esimerkiksi
  $(p \land \neg q) \lor (\neg p \land q)$. Jokainen kaava voidaan
  kirjoittaa DNF:ään suoraan totuustaulusta, mutta tulos voi olla
  eksponentiaalisen pitkä, kuten yllä viisi termiä yhden lyhyen
  lausekkeen sijaan.
- **CNF** (konjunktiivinen normaalimuoto) on disjunktioiden
  konjunktio, esimerkiksi $(p \lor q) \land (\neg p \lor \neg q)$.
  SAT-ratkaisijat ja monet verifiointityökalut syövät kaavat CNF:ssä
  (luku *Predikaatit ja SAT*).

Pienimmän vastaavan lausekkeen löytäminen on laskennallisesti vaikeaa.
Pienillä kaavoilla käytetään Karnaugh-karttoja ja Quine–McCluskeyn
menetelmää, jotka käsitellään taidossa *Digitaalitekniikka*, sillä
logiikkapiirien suunnittelu on täsmälleen tämä ongelma.

## Logiikka ja Boolen algebra koneessa

Totuusarvot ja bitit ovat sama asia: Pythonin `True` ja `False`
käyttäytyvät aritmetiikassa kuin 1 ja 0, ja bittioperaatiot `&`, `|`,
`^` ja `~` soveltavat konnektiiveja kaikkiin bitteihin rinnakkain.
Lyhytkytkentä (*short-circuit evaluation*) on ohjelmointikielten
lisäys logiikkaan: `p and q` jättää $q$:n arvioimatta, jos $p$ on
epätosi. Lauseke `x is not None and x.arvo > 0` on turvallinen juuri
siksi, mutta järjestyksen vaihtaminen kaataa ohjelman, vaikka
konjunktio on logiikassa vaihdannainen.

## Käytännössä

- **Tarkista refaktorointi totuustaululla.** Kun ehto kirjoitetaan
  uudelleen, vertaa uutta ja vanhaa kaikilla syötteillä. Muutaman
  totuusarvomuuttujan ehdolle tämä on yhden rivin testi, joka on
  luotettavampi kuin päättely.
- **Vie negaatio sisään De Morganilla.** `not (a and b)` on
  vaikeampi lukea kuin `not a or not b`. Positiivinen muoto
  (`if on_voimassa`) on helpompi kuin kaksoisnegaatio
  (`if not ei_vanhentunut`).
- **Nimeä osaehdot.** Pitkä ehto jaetaan nimettyihin muuttujiin
  (`saa_alennuksen = kanta or suuri`). Nimi dokumentoi tarkoituksen,
  ja jokaisen osan voi testata erikseen.
- **Muista lyhytkytkentä.** Ehtojen järjestys on merkitsevä, kun
  jälkimmäinen osa voi kaatua tai on kallis. Tarkistus ensin, käyttö
  sitten.
- **Älä sekoita implikaatiota ja käänteistä.** ”Jos maksu onnistui,
  tilaus on tilassa *maksettu*” ei tarkoita, että jokainen maksettu
  tilaus on onnistuneen maksun tulos. Testaa molemmat suunnat
  erikseen, jos tarvitset ekvivalenssin.

## Itsearviointi

- Osaat muodostaa kaavan totuustaulun ja selittää implikaation
  totuusarvot.
- Osaat soveltaa De Morganin lakeja ja tunnistaa, milloin kaksi ehtoa
  ovat ekvivalentit, ja tarkistaa sen ohjelmallisesti.
- Osaat sieventää ohjelman ehtolausekkeen ja muuttaa kaavan
  disjunktiiviseen normaalimuotoon totuustaulusta.
- Osaat selittää lyhytkytkennän ja sen, miksi ehtojen järjestys on
  ohjelmassa merkitsevä.

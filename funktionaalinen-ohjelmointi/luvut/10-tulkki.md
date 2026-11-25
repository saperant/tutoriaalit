# Oma tulkki

Tämän luvun lopputulos on pienen Scheme-murteen tulkki, noin 80 riviä
Racketia. Tulkin kirjoittaminen on Lisp-perinteen tunnetuin harjoitus,
ja se kokoaa koko tutoriaalin: rekursion syntaksipuun yli,
hahmontunnistuksen, sulkeumat ja ympäristöt. Kun tulkki on tehty itse,
muuttujien näkyvyys, sulkeumat ja häntäkutsut eivät enää ole mustia
laatikoita, vaan muutaman rivin koodia. Luku valmistaa taitoon
*Kääntäjätekniikka*.

## Kieli

Tulkittava kieli on Schemen ydin:

| Muoto | Merkitys |
|-------|----------|
| luku, totuusarvo, merkkijono | vakio |
| `nimi` | muuttujan arvo ympäristöstä |
| `(quote x)` | data arvioimatta |
| `(if e1 e2 e3)` | ehto |
| `(lambda (x ...) e)` | funktio |
| `(define nimi e)` | sidonta nykyiseen kehykseen |
| `(f e ...)` | kutsu |
| `(let ([x e] ...) e)`, `(cond ...)` | syntaktista sokeria |

Jäsennintä ei tarvita. Racketin `read` lukee lähdekoodin valmiiksi
S-lausekkeiksi, joten syntaksipuu on tavallinen lista. Kääntäjän
etuosa (leksikaalinen analyysi ja jäsennys) on siten valmiina, ja luku keskittyy
semantiikkaan.

## Ympäristöt

**Ympäristö** kertoo, mihin arvoon kukin nimi viittaa. Se on kehysten
ketju: funktiokutsu luo uuden kehyksen parametreille, ja kehys osoittaa
ympäristöön, jossa funktio *määriteltiin*. Tämä on leksikaalisen
näkyvyyden määritelmä.

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="ymparisto"}
```

Funktioarvo on **sulkeuma**: parametrit, runko ja määrittelyn ympäristö.
Luvun 4 sulkeumat ovat siis yksinkertaisesti tietue, jossa on viite
ympäristöön. Primitiivit käärivät Racketin funktiot.

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="arvot"}
```

```{.dot otsikko="Ympäristöt, kun luvun lopun ohjelma arvioi lauseketta `((lisaaja 5) 10)` (periaatekuva). Kutsu `(lisaaja 5)` loi kehyksen, jossa `n` on 5, ja palautti sulkeuman, joka osoittaa siihen. Sulkeuman kutsu loi kehyksen `x`:lle. Runko `(+ x n)` löytää `x`:n omasta kehyksestään, `n`:n sulkeuman kehyksestä ja `+`:n globaalista."}
digraph {
  rankdir=BT; nodesep=0.9; ranksep=0.55;
  node [shape=plain, style=""];
  g [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>globaali kehys</i></td></tr>
    <tr><td bgcolor="#EEF1F6">+</td><td bgcolor="#EEF1F6">primitiivi</td></tr>
    <tr><td bgcolor="#EEF1F6">lisaaja</td><td bgcolor="#EEF1F6">sulkeuma →</td></tr></table>>];
  s1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>sulkeuma: lisaaja</i></td></tr>
    <tr><td bgcolor="#FFFFFF">parametrit</td><td bgcolor="#FFFFFF">(n)</td></tr>
    <tr><td bgcolor="#FFFFFF">runko</td><td bgcolor="#FFFFFF">(lambda (x) (+ x n))</td></tr></table>>];
  k1 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>kehys: kutsu (lisaaja 5)</i></td></tr>
    <tr><td bgcolor="#EEF1F6">n</td><td bgcolor="#EEF1F6">5</td></tr></table>>];
  s2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>sulkeuma: kutsun (lisaaja 5) arvo</i></td></tr>
    <tr><td bgcolor="#FFFFFF">parametrit</td><td bgcolor="#FFFFFF">(x)</td></tr>
    <tr><td bgcolor="#FFFFFF">runko</td><td bgcolor="#FFFFFF">(+ x n)</td></tr></table>>];
  k2 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>kehys: kutsu ((lisaaja 5) 10)</i></td></tr>
    <tr><td bgcolor="#EEF1F6">x</td><td bgcolor="#EEF1F6">10</td></tr></table>>];
  { rank=same; g -> s1 [label="lisaaja"]; }
  s1 -> g [label="ymp", constraint=false];
  k1 -> g [label="vanhempi"];
  { rank=same; k1; s2; }
  s2 -> k1 [label="ymp", constraint=false];
  k2 -> k1 [label="vanhempi"];
}
```

Nimen haku etenee kehyksestä vanhempaan, kunnes nimi löytyy. Kuvasta
näkyy myös, miksi `n` säilyy: kutsun `(lisaaja 5)` kehys ei katoa
kutsun päättyessä, koska palautettu sulkeuma osoittaa siihen.

## eval ja apply

Tulkin ydin on kaksi toisiaan kutsuvaa funktiota. `arvioi` (*eval*)
käsittelee kunkin lausekelajin, ja `sovella` (*apply*) kutsuu funktiota.
Rakenne on suoraan luvun 3 rakenteellista rekursiota: haara jokaista
syntaksipuun solmulajia kohti.

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="arvioi"}
```

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="sovella"}
```

Muutama ratkaisu kannattaa huomata:

- `lambda` ei arvioi runkoaan. Se tallentaa rungon ja *nykyisen*
  ympäristön, ja runko arvioidaan vasta kutsuttaessa.
- `if` arvioi vain toisen haaran. Siksi `if` on erikoismuoto eikä
  primitiivi (luku 2).
- `sovella` arvioi rungon häntäasemassa. Racket takaa häntäkutsut, joten
  tulkittu kieli saa ne ilmaiseksi: alla oleva miljoonan kierroksen
  silmukka ei kasvata pinoa.

## Sokerin purku

`let` ja `cond` eivät ole ydinkieltä. Ne muunnetaan ydinkielelle ennen
arviointia: `let` on lambdan välitön kutsu ja `cond` on sisäkkäisiä
`if`-lausekkeita. Kääntäjät tekevät saman (*desugaring*), jotta
myöhempien vaiheiden tarvitsee tuntea vain pieni ydinkieli.

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="purku"}
```

```{.scheme tiedosto="esimerkit/10-tulkki/tulkki.rkt" osa="globaali"}
```

## Ohjelman ajaminen

Pääohjelma lukee lausekkeita syötteestä ja tulostaa niiden arvot:

```{.scheme tiedosto="esimerkit/10-tulkki/main.rkt" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/10-tulkki.syote"}
```

```{.tuloste tiedosto="esimerkit/10-tulkki.odotettu"}
```

`kertoma` löytää itsensä, koska `define` lisää sidonnan globaaliin
kehykseen ennen kuin funktiota kutsutaan, ja sulkeuma viittaa samaan
kehykseen. `lisaaja` palauttaa sulkeuman, joka muistaa `n`:n arvon.
Viimeinen rivi tulostaa sulkeumatietueen.

Tulkki kertoo virheet tulkittavan kielen käsittein:

```{.scheme tiedosto="esimerkit/10-sitomaton.kaatuu.rkt" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/10-sitomaton.virhe"}
```

## Mihin tästä jatketaan

Tulkkia on helppo laajentaa, ja jokainen laajennus opettaa jotakin
kielten toteuttamisesta:

- **`set!` ja `begin`**: muuttuva tila ja peräkkäisyys.
- **Dynaaminen näkyvyys**: kun sulkeuman kehys osoittaa kutsujan
  ympäristöön, saadaan varhaisten Lispien dynaaminen näkyvyys. Ero
  näkyy heti `lisaaja`-esimerkissä.
- **Staattinen analyysi**: ennen arviointia tehtävä läpikäynti voi
  löytää sitomattomat muuttujat jo ennen ajoa.
- **Kääntäminen**: sen sijaan että `arvioi` laskee arvon, se voi palauttaa
  sulkeuman, joka laskee arvon (*closure compilation*). Tämä
  ensimmäinen askel tulkista kääntäjään on usein moninkertaisesti
  nopeampi.
- **Jatkeet**: kun tulkki kirjoitetaan jatkeenvälitystyyliin (CPS),
  `call/cc`, poikkeukset ja generaattorit voidaan toteuttaa itse.

## Käytännössä

- **Puuta kävelevä tulkki on oikea toteutustapa.** Monet
  konfiguraatio- ja skriptikielet sekä varhaiset Ruby- ja
  JavaScript-moottorit ovat puuta käveleviä tulkkeja. Nopeammat
  toteutukset kääntävät puun ensin tavukoodiksi (CPython, Lua, JVM)
  ja kuumat osat konekoodiksi (JIT). Semantiikka on silti sama kuin
  tässä luvussa.
- **Sulkeumat ja ympäristöt toteutuksessa.** Kääntäjä analysoi,
  mitkä muuttujat sulkeuma käyttää, ja tallentaa vain ne
  (*closure conversion*). C++:n ja Rustin lambdat ovat juuri tällaisia
  kääntäjän tuottamia tietueita, joissa siepatut muuttujat ovat kenttiä.
- **Sokerin purku pitää toteutuksen pienenä.** Pythonin `with` ja
  `for`, Javan tehostettu `for` ja Kotlinin `?.` määritellään
  ydinkielen avulla. Kun ominaisuus puretaan aikaisin, myöhemmät
  vaiheet (tyyppitarkistus, optimointi, koodin tuotto) eivät tarvitse
  sille omaa käsittelyä.
- **Tulkki on hyvä tapa toteuttaa sovelluksen sisäinen kieli.**
  Sääntömoottorit, kyselykielet ja konfiguraatiokielet ovat pieniä
  tulkkeja. `eval`/`apply`-rakenne ja ympäristöketju toimivat missä
  tahansa kielessä. Jäsentäjä tarvitaan, jos syntaksi ei ole
  S-lauseke.

## Itsearviointi

- Osaat selittää, mitä ympäristö ja kehys ovat ja miten leksikaalinen
  näkyvyys seuraa sulkeuman tallentamasta ympäristöstä.
- Osaat kirjoittaa `eval`/`apply`-tulkin pienelle lausekekielelle ja
  lisätä siihen uuden erikoismuodon.
- Osaat purkaa syntaktisen sokerin ydinkielelle ja perustella, miksi
  toteutukset tekevät niin.
- Osaat selittää, miksi tulkittu kieli perii häntäkutsut Racketilta ja
  miksi sama tulkki C:llä tai Pythonilla ei perisi niitä.

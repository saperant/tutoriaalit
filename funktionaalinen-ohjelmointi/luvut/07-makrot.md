# Koodi datana ja makrot

Lisp-ohjelma kirjoitetaan kielen omana tietorakenteena: S-lauseke
`(+ 1 2)` on lista, jossa on symboli ja kaksi lukua. Tätä kutsutaan
**homoikonisuudeksi**. Koska koodi on dataa, ohjelma voi rakentaa,
tutkia ja muuntaa koodia samoilla välineillä kuin muuta dataa. Makrot
käyttävät tätä kielen laajentamiseen.

## Lainaus ja puolilainaus

`quote` (`'`) palauttaa lausekkeen arvioimatta. **Puolilainaus**
(*quasiquote*, `` ` ``) on mallipohja: se lainaa rungon, mutta `,`
(*unquote*) lisää arvioidun arvon ja `,@` (*unquote-splicing*) liittää
listan alkiot paikalleen.

Racketin xml-kirjasto esittää HTML:n listoina (*X-expression*), joten
sivupohja on tavallinen puolilainattu lauseke:

```{.scheme tiedosto="esimerkit/07-lainaus.rkt" osa="puolilainaus"}
```

Koska lauseke on dataa, sen voi myös arvioida. `eval` tarvitsee
nimiavaruuden, josta nimet haetaan:

```{.scheme tiedosto="esimerkit/07-lainaus.rkt" osa="eval"}
```

```{.tuloste tiedosto="esimerkit/07-lainaus.odotettu"}
```

`eval` on harvoin oikea ratkaisu sovelluskoodissa. Se ohittaa
käännösaikaiset tarkistukset ja on injektioriski, jos lauseke sisältää
syötettä. Luvun 10 tulkki näyttää, miten `eval` toimii sisältä.

## Makrot

Makro on käännösaikainen funktio syntaksista syntaksiin. Racket laajentaa
makrot ennen ohjelman kääntämistä, joten makron käyttö ei maksa ajon
aikana mitään. `define-syntax-rule` määrittelee makron yhdellä
hahmolla ja mallilla.

Makrolla voi tehdä kaksi asiaa, joihin funktio ei pysty: se voi
**viivästää tai estää arvioinnin** ja **nähdä argumenttinsa koodina**.
Alla `varmista` tulostaa epäonnistuneen ehdon lähdekoodin:

```{.scheme tiedosto="esimerkit/07-makrot.rkt" osa="tarkista"}
```

### Hygienia

C:n esikääntäjän makro on tekstikorvaus, jolla on kaksi tunnettua
ongelmaa. Makron apumuuttuja voi peittää käyttäjän samannimisen
muuttujan, ja makron sisällä käytetty nimi voi viitata käyttäjän
uudelleen määrittelemään nimeen. Racketin makrot ovat **hygieenisiä**:
jokainen nimi viittaa siihen sidontaan, joka oli näkyvissä nimen
kirjoituskohdassa. Alla makron sisäinen `tmp` ja käyttäjän `tmp` eivät
sekoitu:

```{.scheme tiedosto="esimerkit/07-makrot.rkt" osa="vaihda"}
```

### Hahmot ja ellipsi

`syntax-rules` sallii monta hahmoa ja toistuvat osat. Ellipsi `...`
tarkoittaa "edellistä hahmoa nolla tai useampi kertaa", ja mallissa se
toistaa vastaavat osat. Näin kieleen saa uuden ohjausrakenteen:

```{.scheme tiedosto="esimerkit/07-makrot.rkt" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/07-makrot.odotettu"}
```

## Kielensisäinen kieli

Makron tavallisin hyvä käyttö on **kielensisäinen kieli** (*embedded
DSL*): tiivis, aihealueen mukainen kuvaus, jonka makro kääntää
tavalliseksi koodiksi. Tilakoneen kuvaus tuottaa käännösaikana
sisäkkäiset `match`-lausekkeet. Sisäkkäiset ellipsit toistavat tilat
ja kunkin tilan siirtymät.

```{.scheme tiedosto="esimerkit/07-tilakone.rkt" osa="makro"}
```

```{.scheme tiedosto="esimerkit/07-tilakone.rkt" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-tilakone.odotettu"}
```

Racketin `#lang`-rivi vie saman ajatuksen pidemmälle: koko tiedosto voi
olla eri kieltä, kuten Scribble-dokumentaatio, Typed Racket tai
opetuskielet, ja kieli toteutetaan makroina ja lukijana.

## Virheilmoitukset käännösaikana

`syntax-rules` tarkistaa vain hahmon muodon. Kun makroa käytetään
väärin, virhe voi syntyä laajennoksen sisältä, ja ilmoitus on
käyttäjälle käsittämätön. `syntax-parse` lisää hahmoihin
**syntaksiluokat**, kuten `a:id` (nimi) ja `e:expr` (lauseke), ja
antaa virheen käyttäjän koodin kohdasta.

```{.scheme tiedosto="esimerkit/07-syntaksi.ei-kaanny.rkt" osa="parse"}
```

`raco expand` hylkää rivin `(vaihda! x 5)` ilmoituksella `vaihda!:
expected identifier`, ennen kuin ohjelmaa ajetaan. Ilman virheriviä
tuloste on:

```{.tuloste tiedosto="esimerkit/07-syntaksi.odotettu"}
```

## Käytännössä

- **Makron kultainen sääntö: älä käytä makroa, jos funktio riittää.**
  Funktio on arvo, sen voi antaa argumenttina ja testata, ja sen
  virheilmoitukset ovat selkeitä. Makroa tarvitaan vain arvioinnin
  hallintaan, uusiin sidontamuotoihin, käännösaikaiseen tarkistukseen
  ja kielensisäisiin kieliin.
- **Valtavirran makrot ovat Lispin perillisiä.** Rustin
  `macro_rules!` on suora `syntax-rules`-jälkeläinen hahmoineen,
  toistoineen ja osittaisine hygienioineen. Rustin proseduraaliset
  makrot vastaavat Racketin `syntax-parse`-makroja. Julia, Elixir,
  Scala 3 ja Nim tarjoavat myös syntaksipuuhun perustuvat makrot.
- **C:n esikääntäjä on tekstikorvaus, ei makrojärjestelmä.** Sen
  ongelmat ovat moninkertainen arviointi (`MAX(i++, j)`),
  nimitörmäykset ja sulkeiden puute. C++:ssa korvaavat välineet ovat
  `constexpr`-funktiot, templatet ja `consteval`. Ne laskevat
  käännösaikana mutta eivät voi luoda uutta syntaksia.
- **Koodi datana elää konfiguraatiossa ja työkaluissa.** JSON on
  pohjimmiltaan S-lauseke aaltosulkein. Syntaksipuuhun perustuvat
  työkalut, kuten linterit, muotoilijat, Babel ja codemodit, käsittelevät
  koodia datana.
- **Kielensisäisiä kieliä on joka paikassa.** Kotlinin rakentajat
  (Gradle Kotlin DSL), Rubyn RSpec, SQLAlchemyn lausekkeet ja Reactin
  JSX ovat kielensisäisiä kieliä. Ne toteutetaan lambdoilla,
  operaattoreiden ylikuormituksella tai käännösvaiheella, kun
  makroja ei ole.

## Itsearviointi

- Osaat rakentaa dataa ja koodia puolilainauksella (`` ` ``, `,` ja `,@`).
- Osaat selittää, mihin makro pystyy ja funktio ei, ja milloin makroa ei
  pidä käyttää.
- Osaat selittää hygienian ja kertoa, miten C:n esikääntäjän makrot
  rikkovat sen.
- Osaat kirjoittaa `syntax-rules`-makron, jossa on ellipsi, ja
  `syntax-parse`-makron, joka tarkistaa argumenttiensa lajin.
- Osaat tunnistaa kielensisäisen kielen ja arvioida, toteutetaanko se
  funktioilla vai makroilla.

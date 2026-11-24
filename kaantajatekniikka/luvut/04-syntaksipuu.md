# Abstrakti syntaksipuu

Jäsennin rakentaa tokeneista **abstraktin syntaksipuun** (*abstract
syntax tree*, AST). Puu on *abstrakti*, koska siitä puuttuu kaikki,
mikä ei vaikuta merkitykseen: sulkeet, puolipisteet ja avainsanat.
Lauseke `(a + b) * c` on puu, jonka juuressa on kertolasku ja
vasemmassa lapsessa yhteenlasku; sulkeiden tehtävä oli vain kertoa
jäsentimelle, millainen puusta tulee.

Ennen jäsentämistä kannattaa suunnitella puu, koska kaikki myöhemmät
vaiheet käsittelevät sitä. Tämä luku esittelee Kiden puun ja tavan
käydä se läpi.

## Puu algebrallisena tietotyyppinä

Funktionaalisissa kielissä syntaksipuu kirjoitetaan
**algebrallisena tietotyyppinä**: lauseke on *joko* luku, nimi,
binäärioperaatio *tai* kutsu, ja jokaisella vaihtoehdolla on omat
kenttänsä. Taidon *Funktionaalinen ohjelmointi* Racket-esimerkeissä
sama rakenne tehtiin tietueilla ja hahmonsovituksella. C++:ssa
vastine on `std::variant`:

```{.cpp tiedosto="esimerkit/kide/ast.hpp" osa="lausekkeet"}
```

Variantti on *summatyyppi*: siinä on tasan yksi vaihtoehdoista, ja
kääntäjä tietää, mitkä vaihtoehdot ovat mahdollisia. Lapset ovat
`std::unique_ptr`-osoittimia, koska tyyppi ei voi sisältää itseään
suoraan (koko olisi ääretön), ja `unique_ptr` ilmaisee omistajuuden:
puu omistaa lapsensa, ja koko puu vapautuu, kun juuri vapautuu.

Kaksi kenttää on tyhjiä jäsentimen jäljiltä ja täytetään myöhemmin:
`Nimi::muuttuja` kertoo, mihin esittelyyn nimi viittaa, ja
`Lauseke::tyyppi` lausekkeen tyypin. Molemmat kirjoittaa semanttinen
analyysi (luku 7). Toinen tapa olisi rakentaa analyysin jälkeen uusi,
*tyypitetty* puu; isot kääntäjät tekevät usein niin (rustc:n HIR ja
THIR), mutta pienessä kääntäjässä yksi puu riittää.

Lauseet ja koko ohjelma noudattavat samaa mallia:

```{.cpp tiedosto="esimerkit/kide/ast.hpp" osa="lauseet"}
```

```{.cpp tiedosto="esimerkit/kide/ast.hpp" osa="ohjelma"}
```

Kide ei tarvitse `else if` -rakenteelle omaa solmua: jäsennin
tuottaa `Jos`-lauseen, jonka epätosi-haarassa on toinen `Jos`.
Samoin `for`-silmukka, jos se lisättäisiin, voitaisiin *purkaa*
(*desugar*) jo jäsentimessä `while`-silmukaksi. Mitä vähemmän
solmutyyppejä puussa on, sitä vähemmän tapauksia jokaisen myöhemmän
vaiheen täytyy käsitellä.

## Läpikäynti vierailijalla

Varianttia käsitellään `std::visit`-funktiolla, joka kutsuu oikeaa
käsittelijää variantin sisällön tyypin mukaan. Kun käsittelijät
kirjoitetaan lambdoina, ne kootaan yhdeksi olioksi pienellä
apuluokalla:

```{.cpp tiedosto="esimerkit/kide/ast.hpp" osa="kaikki"}
```

`Kaikki` periytyy kaikista lambdoista ja tuo niiden `operator()`:t
samaan näkyvyysalueeseen, joten ylikuormitusten valinta tekee
hahmonsovituksen. Jos jokin vaihtoehto puuttuu, käännös epäonnistuu:
kääntäjä tarkistaa *kattavuuden* kuten funktionaalisten kielten
hahmonsovitus. Se on varianttien suurin etu perinteiseen
perintähierarkiaan ja virtuaalisiin funktioihin verrattuna: kun
puuhun lisätään uusi solmutyyppi, jokainen läpikäynti, joka ei sitä
käsittele, on käännösvirhe.

Esimerkki on puun tulostus **S-lausekkeina** eli Lisp-tyylisessä
sulkumuodossa, jossa operaattori on ensin:

```{.cpp tiedosto="esimerkit/kide/ast.cpp" osa="tulosta"}
```

Kertomaohjelman puu (`--vaihe=ast`):

```{.tuloste tiedosto="esimerkit/naytteet/ast-kertoma.txt"}
```

Sulkumuoto näyttää puun rakenteen yksiselitteisesti. Se on sama muoto,
jolla Racket-ohjelmat kirjoitetaan, eikä se ole sattumaa: Lisp-kielissä
ohjelma *on* syntaksipuu, ja siksi niissä on helppo kirjoittaa
ohjelmia, jotka käsittelevät ohjelmia (makrot).

## Vaihtoehtoja

Variantti ei ole ainoa tapa. Yleisimmät vaihtoehdot ovat:

| Tapa | Hyvää | Huonoa | Käyttäjiä |
|------|-------|--------|-----------|
| `std::variant` + `visit` | kattavuustarkistus, ei virtuaalikutsuja | lapset kekomuistissa, `visit` vaatii lambdat | pienet kääntäjät |
| luokkahierarkia + vierailija | tuttu olio-ohjelmointi | uusi solmu vaatii muutoksia moneen paikkaan | Clang, javac |
| solmut taulukossa, viitteet indekseinä | nopea, välimuistiystävällinen, helppo sarjallistaa | indeksit eivät ole tyyppiturvallisia | Zig, rustc:n osat |

Tuotantokääntäjät suosivat taulukkoihin tallennettuja solmuja, koska
miljoonien pienten varausten vapauttaminen ja seuraaminen on
hidasta. Pienessä kääntäjässä selkeys on tärkeämpää.

## Käytännössä

- **Suunnittele puu ennen jäsennintä.** Puu on kaikkien vaiheiden
  rajapinta; jäsennin on vain yksi sen tuottaja (toinen voi olla
  testien generaattori).
- **Pidä puu pienenä.** Pura syntaktinen sokeri jäsentimessä, jotta
  myöhemmät vaiheet käsittelevät vähemmän tapauksia.
- **Säilytä sijainnit solmuissa.** Semanttiset virheet ja
  debuggaustieto tarvitsevat ne.
- **Tee puusta tulostettava.** Tekstimuoto on paras jäsentimen
  testi: kultainen tuloste näyttää heti, jos presedenssi tai
  assosiatiivisuus muuttuu.

## Itsearviointi

- Osaat selittää konkreettisen ja abstraktin syntaksipuun eron ja
  sen, mitä abstraktista puusta jätetään pois.
- Osaat mallintaa syntaksipuun `std::variant`-tyypeillä ja
  `unique_ptr`-lapsilla ja käydä sen läpi `std::visit`-funktiolla.
- Osaat perustella, miksi kattavuustarkistus on vierailijamallin
  tärkein etu solmutyyppejä lisättäessä.
- Osaat tulostaa puun S-lausekkeina ja lukea niistä lausekkeen
  rakenteen.

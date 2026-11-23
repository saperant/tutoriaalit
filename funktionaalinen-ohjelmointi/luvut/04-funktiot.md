# Korkeamman asteen funktiot ja sulkeumat

Funktio on Racketissa arvo samoin kuin luku tai lista. Sen voi antaa
argumenttina, palauttaa, tallentaa tietorakenteeseen ja luoda ajon
aikana. **Korkeamman asteen funktio** ottaa tai palauttaa funktion.
Juuri ne tekevät funktionaalisesta ohjelmoinnista tiivistä: toistuva
rakenne kirjoitetaan kerran, ja muuttuva osa annetaan funktiona.

## lambda

`(lambda (x) (* x x))` eli lyhyesti `(λ (x) (* x x))` luo nimettömän
funktion. `(define (nelio x) ...)` on lyhenne muodosta `(define nelio
(lambda (x) ...))`. Nimetty funktio on siis vain nimeen sidottu
`lambda`.

## map, filter ja fold

Useimmat listan läpikäynnit kuuluvat kolmeen kaavaan:

| Kaava | Tekee | Racket | Muualla |
|-------|-------|--------|---------|
| muunnos | jokaiselle alkiolle uusi arvo | `map` | `map`, `Select`, `transform` |
| suodatus | ehdon täyttävät alkiot | `filter` | `filter`, `Where`, `copy_if` |
| kokoaminen | alkiot yhdeksi arvoksi | `foldl`, `foldr` | `reduce`, `Aggregate`, `accumulate` |

Valmiit funktiot ovat tavallista rakenteellista rekursiota, jossa
vaihtuva osa on parametrina:

```{.scheme tiedosto="esimerkit/04-tilastot.rkt" osa="omat"}
```

Tavallinen tehtävä kirjoitetaan kaavojen ketjuna. Kukin vaihe on helppo
lukea ja testata erikseen:

```{.scheme tiedosto="esimerkit/04-tilastot.rkt" osa="tilastot"}
```

`foldl` kokoaa vasemmalta ja on häntärekursiivinen. `foldr` kokoaa
oikealta, säilyttää järjestyksen ja sopii listan rakentamiseen, mutta
käyttää pinoa listan pituuden verran.

```{.scheme tiedosto="esimerkit/04-tilastot.rkt" osa="suunta"}
```

```{.tuloste tiedosto="esimerkit/04-tilastot.odotettu"}
```

## Sulkeumat

Funktio, joka viittaa ympäröivän näkyvyysalueen nimiin, **sulkee**
ne sisäänsä. Syntyvä sulkeuma (*closure*) muistaa sidonnat silloinkin,
kun sen luonut funktio on jo palannut. `lisaaja` on **funktiotehdas**:

```{.scheme tiedosto="esimerkit/04-sulkeuma.rkt" osa="tehdas"}
```

Sulkeuma voi myös kapseloida muuttuvan tilan. Laskuriin pääsee käsiksi
vain palautetun funktion kautta, joten jokainen generaattori on
eristetty muista:

```{.scheme tiedosto="esimerkit/04-sulkeuma.rkt" osa="tila"}
```

Kun sulkeuma valitsee toimintonsa viestin perusteella, se on **olio**:
yksityinen tila ja julkiset metodit. Tämä on SICP:n tunnettu
havainto: oliot ja sulkeumat ovat saman asian kaksi esitystapaa.

```{.scheme tiedosto="esimerkit/04-sulkeuma.rkt" osa="olio"}
```

```{.tuloste tiedosto="esimerkit/04-sulkeuma.odotettu"}
```

## Funktioiden yhdistäminen

Kun funktiot ovat arvoja, niistä voi koota uusia funktioita ja
tietorakenteita. Validointisäännöt ovat alla dataa: lista viestejä ja
predikaatteja. Uuden säännön lisääminen ei muuta tarkistavaa koodia.

```{.scheme tiedosto="esimerkit/04-koostaminen.rkt" osa="validointi"}
```

`compose` yhdistää funktiot (`(compose f g)` on `(λ (x) (f (g x)))`), ja
`curry` kiinnittää osan argumenteista (*osittainen soveltaminen*):

```{.scheme tiedosto="esimerkit/04-koostaminen.rkt" osa="compose"}
```

Funktio voi myös palauttaa funktion, joka on rakennettu argumenttien
perusteella. Lajittelun vertailija syntyy avainfunktiosta:

```{.scheme tiedosto="esimerkit/04-koostaminen.rkt" osa="avain"}
```

```{.tuloste tiedosto="esimerkit/04-koostaminen.odotettu"}
```

## for-muodot

Racketin `for`-perhe on **kooste** (*comprehension*): se käy läpi yhden
tai useamman sekvenssin ja kokoaa tuloksen ilman eksplisiittistä
rekursiota. `#:when` suodattaa, ja muodon nimi kertoo, mitä kootaan
(`for/list`, `for/sum`, `for/hash`, `for/and`, `for/first` ...).

```{.scheme tiedosto="esimerkit/04-for.rkt" osa="muodot"}
```

`for/fold` on yleisin muoto. Se kuljettaa yhtä tai useampaa kertymää ja
palauttaa ne lopuksi. Se on `foldl` usealla kertymällä ja on usein
luettavampi kuin käsin kirjoitettu nimetty `let`.

```{.scheme tiedosto="esimerkit/04-for.rkt" osa="fold"}
```

`for` käy sekvenssejä läpi rinnakkain ja pysähtyy lyhimmän loppuessa.
`for*` käy läpi kaikki yhdistelmät.

```{.scheme tiedosto="esimerkit/04-for.rkt" osa="sisakkaiset"}
```

```{.tuloste tiedosto="esimerkit/04-for.odotettu"}
```

Sekvenssin tyyppi kannattaa kertoa (`in-list`, `in-range`, `in-hash`,
`in-string`). Silloin Racket kääntää silmukan suoraan sen tyypille
sopivaksi koodiksi. Ilman sitä tyyppi tarkistetaan ajon aikana, ja silmukka on
selvästi hitaampi.

## Käytännössä

- **map/filter/reduce on valtavirtaa.** JavaScriptin taulukkometodit,
  Javan Stream API, C#:n LINQ, C++20:n `std::ranges` ja Rustin
  iteraattorit ovat kaikki saman kaavan toteutuksia. Pythonissa sama
  kirjoitetaan useimmiten listakoosteena `[f(x) for x in xs if p(x)]`,
  joka vastaa Racketin `for/list`-muotoa.
- **Ketju on luettavampi kuin silmukka, kun vaiheet ovat erillisiä.**
  Jos silmukka tekee monta asiaa yhtä aikaa (suodattaa, muuntaa,
  laskee ja tulostaa), jaa se vaiheisiin. Jos yksi läpikäynti kokoaa
  monta arvoa, `for/fold` tai tavallinen silmukka on selkeämpi kuin
  monta erillistä ketjua.
- **Sulkeumat ovat takaisinkutsujen perusta.** Tapahtumankäsittelijät
  JavaScriptissä, Javan `Runnable`, C++:n lambdat ja Rustin `Fn`-piirteet
  ovat sulkeumia. C++:ssa ja Rustissa on kerrottava, otetaanko sidonta
  arvona vai viittauksena (`[=]`/`[&]`, `move`). Racketissa
  roskienkeruu pitää sidonnat hengissä, eikä kysymystä tarvitse
  ratkaista.
- **Silmukkamuuttujan sieppaus on klassinen virhe.** Vanhassa
  JavaScriptissä `var`-muuttuja oli yhteinen kaikille silmukan
  kierroksille, ja Pythonissa sulkeuma sitoo nimen eikä arvoa
  (`lambda: i` palauttaa silmukan viimeisen arvon). Racketin `for`
  luo jokaiselle kierrokselle uuden sidonnan, kuten JavaScriptin `let`.
- **Strategia-, komento- ja tehdasmallit ovat funktioita.** Oliokielen
  suunnittelumalli, jossa rajapinnalla on yksi metodi, on
  funktionaalisessa kielessä pelkkä funktioarvo. Javan funktionaaliset
  rajapinnat ja Kotlinin lambdat ovat tuoneet saman tiiviyden
  JVM:lle.

## Itsearviointi

- Osaat kirjoittaa `map`-, `filter`- ja `foldl`-funktiot itse ja
  valita, milloin käytät `foldl`- ja milloin `foldr`-funktiota.
- Osaat selittää, mitä sulkeuma muistaa ja miksi laskurin tila on
  eristetty.
- Osaat esittää säännöt tai strategiat datana (funktioiden listana) ja
  rakentaa funktioita funktioista (`compose`, `curry`, funktiotehdas).
- Osaat kirjoittaa saman laskennan `for/fold`-muodolla, nimetyllä
  `let`-lausekkeella ja `foldl`-kutsulla.
- Osaat tunnistaa saman kaavan JavaScriptin, Javan Stream API:n,
  Pythonin koosteiden ja Rustin iteraattoreiden koodista.

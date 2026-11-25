# Funktionaalinen ohjelmointi (Racket)

Lispin perinteen ajattelutavat, joista monet nykykielten mallit ovat
peräisin: rekursio, korkeamman asteen funktiot ja sulkeumat,
muuttumaton data ja hahmontunnistus, makrot, laiska laskenta ja oma
tulkki. Kielenä on Racket 8.10. Jokainen luku kertoo, missä sama malli
näkyy Pythonissa, JavaScriptissä, Javassa, C++:ssa ja Rustissa.
Valmiit dokumentit:
[funktionaalinen-ohjelmointi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/funktionaalinen-ohjelmointi.pdf) ja
pikaopas
[funktionaalinen-ohjelmointi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/funktionaalinen-ohjelmointi-pikaopas.pdf).

## Sisältö

1. Johdanto – Lispin historia ja perintö, Racket, työkalut
2. Lausekkeet ja listat – arviointisäännöt, tarkat luvut, parit,
   lainaus, yhtäsuuruus
3. Rekursio – rakenteellinen rekursio, häntäkutsut ja laskennan
   jäljitys, puurekursio ja kutsupuu
4. Korkeamman asteen funktiot ja sulkeumat – map/filter/fold,
   funktiotehtaat, oliot sulkeumina, `for`-koosteet
5. Muuttumaton data ja hahmontunnistus – `struct`, `match`,
   lausekeongelma, symbolinen derivointi, pysyvät rakenteet
6. Testaus, sopimukset ja virheet – rackunit, `contract-out` ja
   syyllinen, poikkeukset
7. Koodi datana ja makrot – puolilainaus, hygienia, kielensisäinen
   kieli, `syntax-parse`
8. Laiska laskenta, virrat ja generaattorit – lupaukset, äärettömät
   virrat, jatkeet, laiska syöte
9. Tila ja ohjelman rakenne – muistaminen, parametrit, funktionaalinen
   ydin ja imperatiivinen kuori
10. Oma tulkki – ympäristöt, `eval` ja `apply`, sokerin purku
11. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```sh
make testaa   # rakenne ja kaikki esimerkit
make pdf      # tutoriaali ja pikaopas
```

Esimerkit voi ajaa kehityskontissa (`.devcontainer/funktionaalinen-ohjelmointi`),
jossa on Racket. Yksittäinen esimerkki ajetaan komennolla
`racket esimerkit/03-puu.rkt` ja syötteelliset esimerkiksi
`racket esimerkit/01-sanat.rkt < esimerkit/01-sanat.syote`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

CC BY-SA 4.0. Ks. repositorion juuren `LICENSE`.

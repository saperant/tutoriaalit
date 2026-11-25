# Tila ja ohjelman rakenne

Funktionaalinen ohjelmointi ei tarkoita, ettei ohjelmassa olisi tilaa tai
sivuvaikutuksia. Ohjelma lukee syötettä, kirjoittaa tiedostoja ja
muistaa asioita. Tavoite on rajata tila ja sivuvaikutukset pieneen,
näkyvään osaan ohjelmaa, jotta muu ohjelma voi olla puhdasta. Tässä
luvussa on kolme välinettä tähän: piilotettu paikallinen tila,
dynaamiset parametrit ja funktionaalisen ytimen ja imperatiivisen
kuoren jako.

## Paikallinen tila: muistaminen

**Muistaminen** (*memoization*) välimuistittaa funktion tulokset.
Se on turvallista vain puhtaalle funktiolle, koska sama syöte antaa
aina saman tuloksen. Muuttuva taulu on piilossa sulkeumassa, joten
ulospäin funktio on edelleen puhdas.

```{.scheme tiedosto="esimerkit/09-muistaminen.rkt" osa="muista"}
```

Levenshteinin etäisyys on tyypillinen dynaamisen ohjelmoinnin tehtävä.
Rekursiivinen määritelmä on luettava, mutta ilman muistamista sen
aikavaativuus on eksponentiaalinen. Muistettuna jokainen indeksipari
lasketaan kerran.

```{.scheme tiedosto="esimerkit/09-muistaminen.rkt" osa="editointi"}
```

Komentorivityökalut käyttävät etäisyyttä ehdotuksiin, kun käyttäjä
kirjoittaa komennon väärin:

```{.scheme tiedosto="esimerkit/09-muistaminen.rkt" osa="ehdotus"}
```

```{.tuloste tiedosto="esimerkit/09-muistaminen.odotettu"}
```

## Dynaamiset parametrit

**Parametri** on arvo, jonka `parameterize` asettaa lohkon ajaksi.
Asetus näkyy kaikissa lohkosta kutsutuissa funktioissa, vaikka niille ei
välitetä argumenttia. Lohkon päättyessä vanha arvo palaa, myös
poikkeuksen jälkeen. Parametri on säiekohtainen.

```{.scheme tiedosto="esimerkit/09-parametrit.rkt" osa="loki"}
```

Standardikirjasto käyttää parametreja tulostusportille, nykyiselle
hakemistolle ja satunnaislukugeneraattorille. Siksi tulosteen voi
kaapata testissä muuttamatta testattavaa funktiota:

```{.scheme tiedosto="esimerkit/09-parametrit.rkt" osa="tuloste"}
```

```{.tuloste tiedosto="esimerkit/09-parametrit.odotettu"}
```

Parametri on hallittu globaali muuttuja. Se sopii poikkileikkaaviin
asetuksiin, kuten lokitasoon, tulostuskohteeseen tai pyynnön
kontekstiin. Se ei sovi tavallisen datan välittämiseen, koska
riippuvuus ei näy funktion argumenteista.

## Funktionaalinen ydin, imperatiivinen kuori

Ohjelman rakenne, jossa **ydin** tekee kaikki päätökset puhtailla
funktioilla ja ohut **kuori** hoitaa I/O:n, on funktionaalisen
ohjelmoinnin tärkein arkkitehtuurimalli (*functional core, imperative
shell*). Ydin on tilakone: se saa nykyisen tilan ja syötteen ja palauttaa
uuden tilan ja tulosteen.

```{.dot otsikko="Ydin ja kuori esimerkissä `09-kuori.rkt`. Kaikki I/O on kuoressa; ydin on funktio, jonka tulos riippuu vain argumenteista."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.5;
  syote [label="syöte", fillcolor="#FFFFFF"];
  tuloste [label="tuloste", fillcolor="#FFFFFF"];
  subgraph cluster_kuori {
    label="kuori (I/O)"; color="#C9CED6"; style=rounded;
    lue [label="lue komento"];
    tulosta [label="tulosta viesti"];
    subgraph cluster_ydin {
      label="ydin (puhdas)"; color="#C9CED6"; style="rounded,filled"; fillcolor="#F7F1E5";
      ydin [label="kasittele:\n(tilit, komento) →\n(tilit′, viesti)", fillcolor="#F3E2C7"];
    }
  }
  syote -> lue; lue -> ydin [label="komento"]; ydin -> tulosta [label="viesti"];
  tulosta -> tuloste;
  ydin -> ydin [label="tilit′ seuraavalle\nkierrokselle"];
}
```

```{.scheme tiedosto="esimerkit/09-kuori.rkt" osa="ydin"}
```

Kuori lukee komennot syötteestä S-lausekkeina, ajaa ytimen ja tulostaa.
`read` jäsentää syötteen suoraan Racketin dataksi, joten erillistä
jäsennintä ei tarvita.

```{.scheme tiedosto="esimerkit/09-kuori.rkt" osa="kuori"}
```

```{.tuloste tiedosto="esimerkit/09-kuori.syote"}
```

```{.tuloste tiedosto="esimerkit/09-kuori.odotettu"}
```

Ytimen voi testata ilman tiedostoja, verkkoa tai valekomponentteja:
testi antaa tilan ja komennon ja tarkistaa tuloksen. Koska tila on
arvo, sen voi tallentaa, lähettää verkon yli tai toistaa
tapahtumalokista (*event sourcing*).

## Käytännössä

- **Ydin ja kuori on yleinen arkkitehtuuri.** Reduxin ja Elmin
  arkkitehtuuri (`reducer: (tila, toiminto) → tila`), heksagonaalinen
  arkkitehtuuri (*ports and adapters*) ja tapahtumalähteinen
  tallennus ovat saman ajatuksen muunnelmia. Kun liiketoimintalogiikka
  ei tee I/O:ta, sen testit ovat nopeita ja deterministisiä.
- **Muistaminen kirjastoissa.** Pythonissa `functools.cache` ja
  `lru_cache`, JavaScriptissä Reactin `useMemo` ja Lodashin `memoize`.
  Välimuistilla on oltava koko- tai aikaraja, jos argumenttien joukko
  on rajaton. Muuten muistaminen on muistivuoto.
- **Parametreja vastaavat valtavirrassa säiekohtaiset muuttujat ja
  kontekstit.** Pythonin `contextvars`, Javan `ThreadLocal` ja
  `ScopedValue` (esikatselu Java 21:ssä, valmis 25:ssä), Go:n `context.Context` ja Reactin
  `Context` ratkaisevat saman ongelman. Go välittää kontekstin
  eksplisiittisenä argumenttina, jolloin riippuvuus näkyy.
- **Muuttuvuus on hyväksyttävää, kun se on paikallista.** Funktio, joka
  käyttää sisäisesti muuttuvaa taulukkoa mutta palauttaa uuden arvon
  eikä muuta argumenttejaan, on ulospäin puhdas. Clojuren *transients*
  ja Haskellin `ST`-monadi tekevät tästä käytännöstä kielen ominaisuuden.

## Itsearviointi

- Osaat toteuttaa muistamisen korkeamman asteen funktiona ja selittää,
  miksi se vaatii puhtaan funktion.
- Osaat käyttää parametria ja `parameterize`-muotoa poikkileikkaavaan
  asetukseen ja kertoa, milloin argumentti on parempi.
- Osaat jakaa ohjelman puhtaaseen ytimeen ja I/O-kuoreen ja testata
  ytimen ilman valekomponentteja.
- Osaat tunnistaa saman mallin Reduxista, Elmistä ja
  tapahtumalähteisestä tallennuksesta.

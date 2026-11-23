# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

Tutoriaalin ajattelutavat koottuina kielestä riippumattomiksi
säännöiksi:

1. **Kirjoita lausekkeita, älä lauseita.** Kun haara tai lohko
   tuottaa arvon, muuttujaa ei tarvitse esitellä tyhjänä ja täyttää
   myöhemmin.
2. **Anna datan rakenteen ohjata funktion rakennetta.** Kutakin datan
   tapausta vastaa yksi haara. Puut käsitellään rekursiolla tai
   visitorilla, summatyypit hahmontunnistuksella.
3. **Erota muunnos, suodatus ja kokoaminen.** `map`/`filter`/`fold`-
   ketju tai kooste on luettavampi kuin silmukka, joka tekee kaiken
   kerralla.
4. **Tee arvoista muuttumattomia oletuksena.** Muutos tuottaa uuden
   arvon. Muuttuvuus on paikallinen optimointi, jota kukaan muu ei näe.
5. **Esitä vaihtuva osa funktiona.** Strategia, takaisinkutsu ja
   validointisääntö ovat funktioita, eivät luokkahierarkioita.
6. **Pidä sivuvaikutukset reunoilla.** Puhdas ydin tekee päätökset, ohut
   kuori hoitaa I/O:n. Ydin testataan ilman valekomponentteja.
7. **Tarkista rajalla, luota sisällä.** Sopimus tai validointi
   moduulin rajalla, ja virheilmoitus nimeää syyllisen.
8. **Käytä laiskuutta suuriin ja äärettömiin sekvensseihin**, mutta
   älä yhdistä sitä sivuvaikutuksiin.
9. **Älä käytä makroa, jos funktio riittää.** Makro on kielen
   laajentamista varten, ei koodin lyhentämiseksi.
10. **Tunne hinnat.** Häntäkutsuja ei taata useimmissa kielissä,
    muuttumattomuus maksaa allokaatioita ja laiskuus voi pitää
    muistia varattuna.

## Mihin tästä eteenpäin

Taitopuussa tämä taito on esitietona taidolle *Kääntäjätekniikka*, jossa
luvun 10 tulkki kasvaa jäsentimeksi, tyyppitarkistimeksi ja koodin
tuottajaksi. Funktionaalisen ajattelun hyödyt näkyvät myös
kielipaketeissa: Rustin iteraattorit, `enum` ja `match`, Javan Stream API
ja `record`, Pythonin koosteet ja generaattorit sekä JavaScriptin
taulukkometodit ja sulkeumat.

Seuraava askel funktionaalisessa ohjelmoinnissa on **staattinen
tyyppijärjestelmä**: algebralliset tietotyypit, tyyppipäättely ja
parametrinen polymorfismi. Ne opitaan parhaiten OCamlilla, F#:lla tai
Haskellilla. Racketissa samaan pääsee Typed Racketilla
(`#lang typed/racket`).

## Lähteet

Kaikki tutoriaalin teksti ja koodi on kirjoitettu tätä tutoriaalia
varten. Alla luetellut teokset ovat taustalukemistoa ja jatko-opiskelun
lähteitä.

### Kirjat

- **Harold Abelson, Gerald Jay Sussman: *Structure and Interpretation
  of Computer Programs*** (2. painos, MIT Press 1996). Ohjelmoinnin
  klassikko: abstraktio, sulkeumat, virrat ja metasirkulaarinen tulkki.
  Teksti on lisensoitu CC BY-SA 4.0 -lisenssillä
  (<https://mitpress.mit.edu/sites/default/files/sicp/>).
- **Matthias Felleisen ym.: *How to Design Programs*** (2. painos, MIT
  Press 2018, <https://htdp.org>). Suunnittelureseptit ja
  rakenteellinen rekursio, Racketin opetuskielillä. Vapaasti luettavissa.
- **Daniel P. Friedman, Matthias Felleisen: *The Little Schemer*** (MIT
  Press 1995). Rekursio kysymys–vastaus-muodossa.
- **Shriram Krishnamurthi: *Programming Languages: Application and
  Interpretation*** (<https://www.plai.org>). Ohjelmointikielten
  semantiikka tulkkien avulla. Vapaasti luettavissa.
- **Robert Nystrom: *Crafting Interpreters*** (<https://craftinginterpreters.com>).
  Tulkin ja tavukoodikoneen toteutus Javalla ja C:llä. Hyvä jatko
  luvulle 10.
- **Chris Okasaki: *Purely Functional Data Structures*** (Cambridge
  University Press 1998). Pysyvät tietorakenteet ja tasoitettu analyysi.

### Dokumentaatio ja muut lähteet

- **The Racket Guide** ja **The Racket Reference**
  (<https://docs.racket-lang.org>). Opas on hyvä lukujärjestys, ja
  käsikirja on kattava.
- **Fear of Macros** (Greg Hendershott,
  <https://www.greghendershott.com/fear-of-macros/>). Käytännönläheinen
  johdatus Racketin makroihin ja `syntax-parse`-kirjastoon.
- **Beautiful Racket** (Matthew Butterick, <https://beautifulracket.com>).
  Omien kielten tekeminen `#lang`-mekanismilla.
- **Gary Bernhardt: *Boundaries*** (esitelmä, 2012). Funktionaalisen
  ytimen ja imperatiivisen kuoren malli.

### Työkalut ja kirjastot

- **DrRacket**: Racketin kehitysympäristö, jossa on askeltava
  suorittaja ja makrojen tarkastelija.
- **Magic Racket** (VS Code) ja **racket-mode** (Emacs).
- **rackunit** (testaus), **racket/contract** (sopimukset),
  **syntax/parse** (makrot), **racket/stream** ja **racket/generator**
  sisältyvät Racketin jakeluun.
- Pakettihakemisto: <https://pkgs.racket-lang.org>.

## Lisenssi

Tämä tutoriaali ja sen esimerkkikoodit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0,
<https://creativecommons.org/licenses/by-sa/4.0/deed.fi>). Teosta saa
kopioida, levittää ja muokata, kunhan alkuperäinen lähde mainitaan ja
muokatut versiot jaetaan samalla lisenssillä.

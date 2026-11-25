# Milloin assemblyä ei kannata kirjoittaa

Edellisissä luvuissa assemblyä ja sisäisiä funktioita kirjoitettiin,
koska siitä oli opittavaa. Tuotantokoodissa oletus on päinvastainen:
C on oikea valinta, kunnes on osoitettu, ettei se riitä. Tämä luku
näyttää kaksi syytä, miksi käsin kirjoitettu koodi häviää usein
kääntäjälle, ja kokoaa perusteet, joilla assemblyä silti tarvitaan.

## Kääntäjä tuntee temput

Jakolasku on suorittimen hitaimpia kokonaislukukäskyjä: 64-bittinen
jako vie nykyisillä x86-64-suorittimilla kymmeniä kellojaksoja, kun
kertolasku vie kolme. Jako vakiolla voidaan korvata kertolaskulla
vakion "käänteisluvulla" ja siirrolla. Käsin kirjoittaja tuskin
muistaa oikeaa vakiota; kääntäjä laskee sen jokaiselle jakajalle:

```{.c tiedosto="esimerkit/07-kaantaja/main.c" osa="jako"}
```

```{.bash tiedosto="esimerkit/07-kaantaja/tarkistus.sh" osa="pura"}
```

```{.tuloste tiedosto="esimerkit/07-kaantaja/tarkistus.odotettu"}
```

x86-64-versiossa ei ole jakokäskyä lainkaan. `0xcccccccccccccccd` on
2⁶⁷ / 10 ylöspäin pyöristettynä, ja `mul` laskee 128-bittisen
tulon, jonka yläpuolisko `rdx`:ssä siirretään kolme bittiä oikealle. RISC-V-ristikääntäjä
taas käyttää `divu`-käskyä, koska sen oletuskustannusmalli
(`-mtune=rocket`, yksinkertainen järjestyksessä suorittava ydin)
arvioi jakolaskun riittävän halvaksi. Kumpikaan valinta ei ole
yleisesti oikea, mutta molemmat ovat kääntäjän tietoisia päätöksiä
kohdeprosessorin perusteella, ja `-mtune` muuttaa niitä. Käsin
kirjoitettu versio tekee saman päätöksen kerran ja yhdelle
prosessorille.

## Assembly on optimoijalle musta laatikko

Toinen syy näkyy tulosteen loppuosassa. Sama yhteenlasku on kirjoitettu
C:nä ja inline-assemblynä, ja molemmat saavat vakioargumentit:

```{.c tiedosto="esimerkit/07-kaantaja/main.c" osa="musta"}
```

```{.tuloste tiedosto="esimerkit/07-kaantaja/odotettu"}
```

C-versiosta jäi jäljelle `mov $0x2a, %eax` (42): kääntäjä laski
tuloksen valmiiksi käännösaikana. Assembly-version se joutui
suorittamaan sellaisenaan, koska se ei tiedä, mitä `add` tekee.
Sama koskee kaikkea, mitä optimoija tekee asm-lauseen ympärillä:
vakioiden laskemista, yhteisten alilausekkeiden poistoa, silmukan
invarianttien siirtämistä, vektorointia ja funktioiden avaamista
(*inlining*) kutsukohtaan. Pieni asm-lause kuumassa silmukassa voi siksi
hidastaa koodia, vaikka käsky itsessään olisi nopein mahdollinen.
Sisäiset funktiot välttävät ongelman, koska kääntäjä tuntee niiden
merkityksen.

## Muut kustannukset

Käsin kirjoitetulla assemblyllä on lisäksi hinta, joka ei näy
käskymäärissä:

- **Jokainen arkkitehtuuri erikseen.** Tämän tutoriaalin jokainen
  esimerkki on kirjoitettu kahdesti, ja C-varapolku tarvitaan
  kolmanneksi. Jokainen versio tarvitsee testit.
- **ABI-virheet.** Kutsusopimus, tasaus, purkutiedot ja pinomerkintä
  ovat käsin pidettäviä lupauksia (luvut 2 ja 3), ja niiden rikkominen
  näkyy usein kaukana virheestä.
- **Tietoturvakovennukset.** Kääntäjä lisää C-funktioihin
  kovennukset automaattisesti, assembly-funktioihin ei kukaan. Intelin
  CET-epäsuorien hyppyjen suojaus vaatii jokaisen epäsuorasti
  kutsuttavan funktion alkuun käskyn `endbr64` ja objektitiedostoon
  `.note.gnu.property`-merkinnän. Edellisen tulosteen C-funktioiden
  ensimmäinen käsky on juuri `endbr64`, mutta tämän tutoriaalin
  assembly-funktioissa sitä ei ole, joten CET-suojaus ei olisi
  käytössä ohjelmassa, johon ne linkitetään. GCC:n otsake `<cet.h>`
  tarjoaa makron `_CET_ENDBR` tätä varten.
- **Vanheneminen.** Vuonna 2010 optimaalinen silmukka voi olla
  hitaampi kuin kääntäjän tuottama koodi nykyprosessorilla, jonka
  ajoitus ja välimuistit ovat erilaiset. C-koodi paranee jokaisella
  kääntäjäversiolla, käsin kirjoitettu ei.

## Milloin assemblyä tarvitaan

Asiat, joita C ei voi ilmaista, ovat assemblyn varsinainen käyttöalue:

| Tarve | Tyypillinen keino |
|-------|-------------------|
| Erikoiskäsky ilman sisäistä funktiota (`cpuid`, CSR-rekisterit) | inline-assembly |
| Ohjelman tai säikeen alku ennen C-ympäristöä (`_start`, pinon asetus) | `.S`-tiedosto |
| Kontekstinvaihto, korutiinit, `setjmp` | `.S`-tiedosto |
| Keskeytysten ja poikkeusten sisääntulo | `.S`-tiedosto |
| Vakioaikainen kryptografia, jossa kääntäjä ei saa lisätä haaroja | `.S`-tiedosto tai sisäiset funktiot |
| Mitatusti kuuma silmukka, jota kääntäjä ei saa tehokkaaksi | ensin sisäiset funktiot, sitten `.S` |

```{.dot otsikko="Portaat suorituskykyongelmassa. Seuraavalle portaalle siirrytään vain, jos mittaus osoittaa, ettei edellinen riitä."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.35;
  c [label="C"]; lue [label="lue kääntäjän\nkoodi"]; vek [label="vektoroitava C\n(restrict, yksinkertainen\nsilmukka)"];
  sis [label="sisäiset\nfunktiot"]; inl [label="inline-\nassembly", fillcolor="#F3E2C7"]; s [label=".S-tiedosto", fillcolor="#F3E2C7"];
  c -> lue -> vek -> sis -> inl -> s [label="mittaa"];
}
```

Viimeinen rivi on ainoa suorituskykyperuste, ja siihenkin edetään
vaiheittain: ensin C ja kääntäjän tuottaman koodin lukeminen, sitten
C:n muokkaus niin, että kääntäjä vektoroi (`restrict`, yksinkertaiset
silmukat), sitten sisäiset funktiot ja vasta viimeisenä assembly.
Jokaisen vaiheen jälkeen mitataan oikealla datalla, ja vaihe
hyväksytään vain, jos ero on merkittävä.

## Käytännössä

- **Lue ennen kuin kirjoitat.** `gcc -O2 -S`, `objdump -d` ja
  Compiler Explorer näyttävät, mitä kääntäjä jo tekee. Usein vastaus
  on "parempaa kuin aioit kirjoittaa".
- **Mittaa, älä arvaa.** `perf stat` kertoo käskyt, jaksot ja
  haaraennustusvirheet; `perf record` näyttää, missä aika kuluu.
  Mittaa koko ohjelma, ei vain eristettyä silmukkaa, koska
  välimuistit ja muistikaista muuttavat tulosta.
- **Pidä C-versio aina.** Se on viite testeille, varapolku muille
  arkkitehtuureille ja tapa mitata, vieläkö assembly on nopeampi
  seuraavalla kääntäjäversiolla.
- **Kirjoita perustelu koodiin.** Jokaisen assembly-tiedoston alussa
  on kommentti: miksi tämä on assemblyä, millä mitattiin ja mitä
  tuli tulokseksi. Ilman sitä seuraava ylläpitäjä ei tiedä, uskaltaako
  tiedoston poistaa.
- **Sisäiset funktiot ennen assemblyä.** Ne säilyttävät
  optimoinnit, toimivat Clangilla ja ovat kääntäjän tarkistamia.

## Itsearviointi

- Osaat lukea kääntäjän tuottamasta koodista, miten jako vakiolla
  toteutetaan, ja selittää, miksi valinta riippuu kohdeprosessorista.
- Osaat selittää, miksi inline-assembly estää optimointeja, joita
  sisäinen funktio ei estä.
- Osaat luetella käsin kirjoitetun assemblyn piilokustannukset
  (arkkitehtuurit, ABI, kovennukset, vanheneminen).
- Osaat nimetä tehtävät, joihin assemblyä todella tarvitaan, ja
  edetä suorituskykyongelmassa vaiheittain C:stä assemblyyn.

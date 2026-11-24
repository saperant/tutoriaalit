# Johdanto {.runko-johdanto}

Lähes kaikki konekieli, jota nykyään kirjoitetaan käsin, elää
C-ohjelman sisällä. Käyttöjärjestelmän ydin on C:tä, mutta sen
kontekstinvaihto ja keskeytysten sisääntulo ovat assemblyä.
Kryptografiakirjastot ovat C:tä, mutta AES- ja SHA-ytimet käyttävät
prosessorin erikoiskäskyjä. Videokoodekit, pakkauskirjastot ja
merkkijonofunktiot (`memcpy`, `strlen`) valitsevat käynnistyessään
prosessorille parhaiten sopivan SIMD-toteutuksen. Kaikissa näissä on
sama ongelma: kaksi kieltä, joista toinen ei tiedä toisen
olemassaolosta, pitää saada toimimaan yhdessä niin, että kääntäjän
optimoija ei riko kumpaakaan.

Tämä tutoriaali käsittelee kolme tapaa yhdistää C ja konekieli:

1. **Erillinen assembly-tiedosto** (`.S`), joka kootaan ja linkitetään
   C-ohjelmaan. Rajapintana on C-prototyyppi ja kutsusopimus. Tapa
   sopii kokonaisille funktioille: kontekstinvaihtoon, käynnistyskoodiin
   ja käsin ajoitettuihin silmukoihin.
2. **Inline-assembly**: yksittäisiä käskyjä C-funktion keskellä GCC:n
   `__asm__`-laajennuksella. Tapa sopii käskyihin, joilla ei ole
   C-vastinetta, kuten `cpuid`, muistiesteet ja erikoisrekisterien
   luku.
3. **Kääntäjän sisäiset funktiot** (*intrinsics* ja *builtins*):
   C-funktioilta näyttäviä kutsuja, jotka kääntäjä muuttaa suoraan
   konekäskyiksi. Tapa sopii SIMD-koodiin ja bittioperaatioihin, ja
   se on yleensä paras vaihtoehto, koska optimoija ymmärtää ne.

Lisäksi käsitellään sitä, miten ohjelma valitsee ajon aikana
prosessorin ominaisuuksien mukaisen toteutuksen, ja sitä, milloin
assemblyä ei kannata kirjoittaa lainkaan.

## Esitiedot ja rajaus

Tutoriaali jatkaa *Assembly*-tutoriaalia, jonka asiat oletetaan
tunnetuiksi: rekisterit, osoitusmuodot, hypyt, pino, kutsukonventioiden
perusteet (System V AMD64 ja RISC-V psABI), järjestelmäkutsut ja
SIMD-käskyjen perusajatus. Niitä ei toisteta. Lisäksi oletetaan
C-kieli, käännösprosessi (esikääntäjä, kääntäjä, kokoaja, linkkeri)
ja Linux-komentorivi.

Tutoriaali ei käsittele assemblyn kirjoittamista ilman C:tä,
käyttöjärjestelmän ytimen erityispiirteitä, muita kääntäjiä kuin
GCC:tä (Clang tukee samoja laajennuksia lähes sellaisenaan, MSVC ei
tue x86-64:llä inline-assemblyä lainkaan) eikä suorituskyvyn
mittaamista. Mittaaminen on oma taitonsa; tässä vertailut tehdään
käskymäärinä ja purettuna koodina, koska ne ovat toistettavia.

## Kaksi arkkitehtuuria

Kaikki esimerkit tehdään rinnakkain **x86-64**:llä (natiivisti, GCC 14)
ja **RISC-V**:llä (RV64GC, ristikääntäjä `riscv64-linux-gnu-gcc` ja
QEMU:n käyttäjätilan emulaattori). Rinnakkaisuus näyttää, mikä on
GCC:n ja C:n rajapinnan ominaisuutta ja mikä yhden käskykannan
erikoisuutta: inline-assemblyn rajoitteet ovat samat, mutta
rekisterien nimet, välittömien arvojen koot ja SIMD-mallit eroavat.
RISC-V:n vektorilaajennus (V) on käytössä yhdessä esimerkissä, ja
QEMU emuloi sitä ympäristömuuttujalla
`QEMU_CPU=rv64,v=true,vlen=128,vext_spec=v1.0`.

## Esimerkit ja työkalut

Esimerkit ovat hakemistossa `esimerkit/`, kukin omassa
alihakemistossaan. Hakemistossa voi olla C-lähteitä, x86-64-toteutus
`x86.S`, RISC-V-toteutus `rv.S`, odotettu tuloste sekä tarkistus
(`tarkistus.sh`), joka tutkii tuotettua koodia `objdump`- tai
`readelf`-työkalulla. Komento `make` hakemistossa `esimerkit/` kääntää
kaiken optimoinnilla `-O2`, ajaa ohjelmat molemmilla arkkitehtuureilla
ja vertaa tulosteita odotettuihin:

```text
$ cd esimerkit
$ make
OK: 10 esimerkkiä x86-64:llä ja RISC-V:llä
```

Optimointi on valittu tarkoituksella. Monet tämän tutoriaalin
virheistä eivät näy lainkaan ilman optimointia, koska `-O0`:lla
kääntäjä tallentaa jokaisen muuttujan muistiin ja lukee sen sieltä
uudelleen. Tuotantokoodi käännetään optimoiden, joten esimerkitkin
käännetään.

Ohjelmat linkitetään staattisesti (`-static`), jotta QEMU ei tarvitse
RISC-V-version jaettuja kirjastoja. Kehityskontissa
(`.devcontainer/c-asm-integraatio`) kaikki työkalut ovat valmiina.
Tärkeimmät komennot:

| Tarkoitus | Komento |
|-----------|---------|
| Käännä ja linkitä | `gcc -O2 main.c x86.S` |
| RISC-V | `riscv64-linux-gnu-gcc -O2 -static main.c rv.S` |
| Kääntäjän assembly | `gcc -O2 -S tiedosto.c` |
| Puretut käskyt | `objdump -d --disassemble=funktio ohjelma` |
| Symbolit ja osiot | `readelf -sW tiedosto.o`, `readelf -lW ohjelma` |
| Ajo RISC-V:llä | `qemu-riscv64 ./ohjelma` |

Kääntäjän tuottamaa koodia kannattaa tutkia myös Compiler Explorerissa
(godbolt.org), joka näyttää lähderivin ja sen käskyt rinnakkain monella
kääntäjällä ja arkkitehtuurilla.

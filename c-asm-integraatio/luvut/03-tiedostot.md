# Assembly-tiedostot projektissa

Edellisen luvun funktio toimi, mutta toimiva funktio ei vielä ole
hyvä projektin osa. Assembly-tiedosto pitää koota samoilla
valitsimilla kuin muu koodi, sen symbolien näkyvyys pitää hallita, ja
siitä pitää syntyä samat metatiedot kuin kääntäjän tuottamasta
koodista: pinon oikeudet ja purkutiedot. Ilman niitä ohjelma toimii
testeissä, mutta debuggeri, profiloija, poikkeukset ja
tietoturvakovennukset hajoavat.

## `.S` ja `.s`

GCC päättelee tiedoston tyypin päätteestä:

| Pääte | Esikääntäjä | Tyypillinen käyttö |
|-------|-------------|--------------------|
| `.S` (iso) | ajetaan (`#include`, `#define`, `#ifdef`) | käsin kirjoitettu assembly |
| `.s` (pieni) | ei ajeta | kääntäjän tuottama assembly (`gcc -S`) |
| `.sx` | ajetaan | sama kuin `.S` järjestelmissä, joiden tiedostonimet eivät erottele kirjainkokoa |

Käsin kirjoitettu koodi kannattaa aina tallentaa `.S`-tiedostoon. Silloin
se voi jakaa otsakkeen C:n kanssa, käyttää vakioita ja valita
toteutuksen `#ifdef`-ehdoilla. Kääntäjä välittää kokoajalle myös
valitsimet `-D`, `-I` ja `-march`. Saman tiedoston kokoaminen pienellä
s:llä ei anna varoitusta vaan oudon virheen, koska x86-64- ja
RISC-V-kokoajat tulkitsevat `#`-merkillä alkavan rivin kommentiksi:

```{.bash tiedosto="esimerkit/03-kokoaminen/tarkistus.sh" osa="pieni-s"}
```

```{.tuloste tiedosto="esimerkit/03-kokoaminen/tarkistus.odotettu"}
```

`#include` hävisi hiljaa kommenttina, joten makroja `FUNKTIO`, `LOPPU`
ja `PINO_EI_SUORITETTAVA` ei ollut määritelty. Jos virheilmoituksessa
on isoilla kirjaimilla kirjoitettu makron nimi pienillä kirjaimilla,
syy on lähes aina puuttuva esikääntäjä.

Esikääntäjällä on assemblyssä kaksi sudenkuoppaa. Ensinnäkin C:n
kommentit (`//` ja `/* */`) poistetaan, mutta `#`-alkuiset
kommenttirivit voivat näyttää esikääntäjän direktiiveiltä: rivi
`# if alla on silmukka` on esikääntäjälle virheellinen `#if`. Kirjoita
kommentit siksi muotoon `# ` ja sana, joka ei ole direktiivi, tai
käytä `//`-kommentteja. Toiseksi makron argumentit erotetaan
pilkuilla, joten käskyn kirjoittaminen makron argumentiksi vaatii
vaihtuvan argumenttimäärän makron (`#define PURKU(...) __VA_ARGS__`),
kuten edellisen luvun otsakkeessa.

## Symbolit ja niiden näkyvyys

Kokoajan nimiöt ovat oletuksena paikallisia: ne näkyvät vain samassa
tiedostossa, kuten C:n `static`-funktiot. Direktiivit muuttavat tätä:

| Merkintä | Merkitys | C-vastine |
|----------|----------|-----------|
| `nimi:` | paikallinen symboli objektitiedostossa | `static` |
| `.L1:`, `1:` | ei symbolia lainkaan, vain hyppykohde | silmukan nimiö |
| `.globl nimi` | näkyy linkkerille | tavallinen funktio |
| `.hidden nimi` | näkyy linkkerille, mutta ei jaetun kirjaston ulkopuolelle | `__attribute__((visibility("hidden")))` |
| `.weak nimi` | heikko: toinen määrittely voi korvata | `__attribute__((weak))` |

Jaetun kirjaston sisäiset assembly-apufunktiot merkitään
`.hidden`-direktiivillä. Silloin ne eivät näy kirjaston rajapinnassa,
eivätkä kirjaston omat kutsut kulje proseduurien linkitystaulun (PLT)
kautta. `.L`-alkuiset ja numeroidut nimiöt (`1:`, viittaukset `1b` ja
`1f`) eivät päädy symbolitauluun lainkaan, joten niitä käytetään
silmukoissa ja haaroissa. Numeronimiöt sopivat erityisesti makroihin,
koska sama numero saa esiintyä monta kertaa.

Assembly-funktiolla ei ole automaattisia osioita kuten C-koodilla.
`.text` valitsee koodiosion; vakiotaulukot kuuluvat osioon
`.section .rodata`, kirjoitettava data osioon `.data` ja nollattu data
osioon `.bss`. Vakiotaulukon sijoittaminen `.text`-osioon toimii,
mutta haittaa välimuisteja ja estää tietoturvakovennuksia, jotka
olettavat koodin ja datan olevan erillään.

## Pinon suoritusoikeus

Linuxin ELF-ohjelmassa on ohjelmaotsake `GNU_STACK`, joka kertoo,
tarvitseeko pino suoritusoikeuden. Linkkeri päättelee sen
objektitiedostojen tyhjistä `.note.GNU-stack`-osioista. Kääntäjä lisää
osion jokaiseen C-tiedostoon, mutta käsin kirjoitetun
assembly-tiedoston pitää lisätä se itse. Jos yksikin objektitiedosto
ei kerro kantaansa, linkkeri olettaa varmuuden vuoksi, että pinon on
oltava suoritettava, ja koko ohjelma menettää suojan, joka estää
pinoon kirjoitetun koodin suorittamisen:

```{.bash tiedosto="esimerkit/03-kokoaminen/tarkistus.sh" osa="merkinta"}
```

Edellä näytetyn tulosteen loppu näyttää eron: oikeudet ovat `RW` merkinnän kanssa ja
`RWE` ilman. Nykyiset binutils-versiot varoittavat tästä, mutta varoitus
hukkuu helposti käännöslokiin. Siksi otsakkeen makro
`PINO_EI_SUORITETTAVA` kirjoitetaan jokaisen `.S`-tiedoston loppuun,
ja projektin CI:ssä voi tarkistaa kaikista ohjelmista, ettei
`GNU_STACK`-rivillä ole `E`-kirjainta. Saman voi pakottaa linkkerille
valitsimella `-Wl,-z,noexecstack`, mutta se vain peittää puuttuvan
merkinnän eikä korjaa sitä.

## Purkutiedot ja CFI

Kun C++-poikkeus etenee pinossa ylöspäin, kun `gdb` näyttää
kutsupinon komennolla `bt` tai kun `perf` kerää kutsuketjuja, ohjelma
*purkaa pinoa* (*stack unwinding*). Purkaja tarvitsee jokaisesta
funktiosta tiedon siitä, miten edellisen kehyksen rekisterit ja
paluuosoite löytyvät kunkin käskyn kohdalla. Tieto on osiossa
`.eh_frame`, ja kääntäjä tuottaa sen C-koodista automaattisesti.
Assemblyssä sen kirjoittavat *CFI-direktiivit* (*Call Frame
Information*):

| Direktiivi | Merkitys |
|------------|----------|
| `.cfi_startproc`, `.cfi_endproc` | funktion purkutietojen alku ja loppu |
| `.cfi_def_cfa_offset n` | kehyksen perusosoite (CFA) on nyt `sp + n` |
| `.cfi_offset rek, n` | rekisterin vanha arvo on tallennettu osoitteeseen CFA + n |
| `.cfi_restore rek` | rekisteri on palautettu |
| `.cfi_def_cfa_register rek` | CFA lasketaan nyt toisesta rekisteristä (kehysosoitin) |

CFA (*Canonical Frame Address*) on pino-osoittimen arvo juuri ennen
funktion kutsua. x86-64:llä funktion alussa CFA on `rsp + 8`, koska
`call` työnsi paluuosoitteen pinoon; RISC-V:llä alussa CFA on `sp`, ja
paluuosoite on rekisterissä `ra`. Jokaisen pino-osoitinta muuttavan
käskyn jälkeen tulee direktiivi, joka kertoo uuden etäisyyden.

Esimerkissä C-funktio kutsuu assembly-funktiota, joka kutsuu takaisin
C-funktiota. Sisin funktio purkaa pinon libgcc:n funktiolla
`_Unwind_Backtrace`, samalla koneistolla, jota C++:n poikkeukset
käyttävät, ja tunnistaa kunkin kehyksen funktion alkuosoitteesta:

```{.c tiedosto="esimerkit/04-pinonpurku/main.c" osa="purku"}
```

Assembly-funktio on kirjoitettu niin, että CFI-direktiivit voi kytkeä
pois makrolla:

```{.gnuassembler tiedosto="esimerkit/04-pinonpurku/x86.S" osa="kutsu"}
```

```{.gnuassembler tiedosto="esimerkit/04-pinonpurku/rv.S" osa="kutsu"}
```

Direktiivien kanssa (`-DCFI`) purku etenee `main`iin asti
kummallakin arkkitehtuurilla:

```{.tuloste tiedosto="esimerkit/04-pinonpurku/odotettu"}
```

Ilman niitä purkaja ei löydä `kutsu_kautta`-funktion paluuosoitteelle
purkutietoja ja pysähtyy:

```{.tuloste tiedosto="esimerkit/04-pinonpurku/tarkistus.odotettu"}
```

Toinen `syvin`-rivi on purkajan viimeinen, epäonnistunut askel: se ei
pystynyt päivittämään kehyksen tietoja, joten takaisinkutsu sai
saman funktion uudelleen. C++-ohjelmassa sama tilanne tarkoittaa,
että assembly-funktion läpi kulkeva poikkeus kutsuu `std::terminate`.
Debuggerissa kutsupino katkeaa tai näyttää roskaa, ja profiloija
kirjaa ajan väärälle funktiolle.

CFI on helppo jättää pois, koska ilman sitä kaikki toimii, kunnes
joku tarvitsee pinonpurkua. Lehtifunktiolle, joka ei muuta
pino-osoitinta, riittävät `.cfi_startproc` ja `.cfi_endproc`, koska
oletussäännöt kuvaavat juuri funktion alun tilan. Direktiivien
oikeellisuuden voi tarkistaa komennolla `readelf --debug-dump=frames`
tai askeltamalla funktion läpi `gdb`:ssä ja kokeilemalla komentoa `bt`
jokaisessa kohdassa.

## Kokoaminen käännösjärjestelmässä

Make ja CMake tuntevat `.S`-tiedostot. Makessa sisäänrakennettu sääntö
kokoaa ne kääntäjällä ja välittää `CPPFLAGS`- ja `ASFLAGS`-muuttujat;
CMakessa kieli `ASM` otetaan käyttöön projektin määrittelyssä:

```text
# Makefile: ARCH on x86 tai rv, sisäänrakennettu sääntö kokoaa .S:n
ohjelma: main.o $(ARCH).o
	$(CC) $(LDFLAGS) -o $@ $^

# CMakeLists.txt
project(laskin C ASM)
add_executable(laskin main.c)
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
    target_sources(laskin PRIVATE x86.S)
else()
    target_sources(laskin PRIVATE rv.S)
endif()
```

Kokoa assembly aina kääntäjäajurilla (`gcc -c x86.S`), älä suoraan
kokoajalla (`as`). Ajuri ajaa esikääntäjän, välittää arkkitehtuuri- ja
ABI-valitsimet ja käyttää samaa kokoajaa kuin C-koodi.

## Käytännössä

- **Yksi kehys kaikille funktioille.** Kokoa `.globl`, `.type`,
  `.size`, `.cfi_startproc` ja `.cfi_endproc` makroihin, kuten
  glibc:n `ENTRY`- ja `END`-makroissa ja Linuxin
  `SYM_FUNC_START`-makroissa. Yksikään funktio ei silloin unohdu ilman
  metatietoja.
- **`.note.GNU-stack` jokaiseen tiedostoon.** Tarkista CI:ssä
  `readelf -lW` -komennolla, ettei yhdenkään ohjelman pino ole
  suoritettava. Valitsin `-Wl,--fatal-warnings` tekee linkkerin
  varoituksesta virheen.
- **CFI aina, kun funktio muuttaa pinoa.** Ilman sitä poikkeukset,
  debuggerit ja profiloijat pysähtyvät assembly-funktioon. GCC:n
  tuottama `gcc -S` -tuloste on hyvä malli: kirjoita vastaava
  C-funktio ja katso, mitkä direktiivit kääntäjä tuottaa.
- **Piilota sisäiset symbolit.** Kirjaston sisäiset apufunktiot ovat
  `.hidden`; paikalliset hyppykohteet ovat `.L`- tai numeronimiöitä.
- **Valitse toteutus käännösjärjestelmässä, ei lähteessä.** Kullekin
  arkkitehtuurille oma tiedosto ja C-toteutus varalle on selkeämpi kuin
  yksi tiedosto täynnä `#ifdef`-haaroja.

## Itsearviointi

- Osaat selittää `.S`- ja `.s`-tiedostojen eron ja tunnistaa puuttuvan
  esikääntäjän virheilmoituksesta.
- Osaat hallita symbolin näkyvyyttä direktiiveillä `.globl`,
  `.hidden` ja `.L`-nimiöillä ja kertoa, milloin kutakin käytetään.
- Osaat kertoa, mitä `.note.GNU-stack` tekee ja miten sen puuttuminen
  näkyy ohjelmaotsakkeissa.
- Osaat kirjoittaa CFI-direktiivit funktiolle, joka tallentaa
  rekistereitä pinoon, ja selittää, mitä ilman niitä tapahtuu
  pinonpurussa.

# Johdanto {.runko-johdanto}

Suoritin ei ymmärrä C:tä, Pythonia eikä Rustia. Se suorittaa
*konekieltä*: muistissa olevia tavuja, joista jokainen käsky kertoo
yhden pienen operaation, kuten "laske rekisterit yhteen" tai "hyppää,
jos tulos oli nolla". *Assembly* eli symbolinen konekieli on näiden
käskyjen ihmisen luettava kirjoitusasu. Kokoaja (*assembler*) muuntaa
sen tavuiksi lähes yksi yhteen.

Assemblyä kirjoitetaan nykyään harvoin kokonaisina ohjelmina. Sitä
*luetaan* sitäkin useammin: kun etsitään vikaa optimoidusta
koodista, arvioidaan kääntäjän tuottamaa koodia suorituskykyä varten,
tutkitaan kaatumisen pinojälkeä ilman lähdekoodia tai analysoidaan
haittaohjelmaa. Kirjoittamista tarvitaan käynnistyskoodissa,
keskeytyskäsittelijöissä, kontekstin vaihdossa, kryptografian
vakioaikaisissa rutiineissa ja muutamissa kuumissa silmukoissa.

Tämä tutoriaali opettaa molemmat taidot kahdella käskykannalla
rinnakkain:

- **x86-64** (AMD64): työasemien ja palvelinten valtakäskykanta. Se
  on CISC-tyyppinen: käskyt ovat eripituisia (1–15 tavua), ja ne voivat
  lukea muistia ja laskea samassa käskyssä.
- **RISC-V** (RV64GC): avoin RISC-käskykanta, jota käytetään
  mikro-ohjaimista palvelimiin ja joka on opetuksen standardi. Käskyt
  ovat 32-bittisiä (tiivistetyt 16-bittisiä), ja muistia käsitellään
  vain lataus- ja tallennuskäskyillä.

Kahden käskykannan rinnakkain lukeminen erottaa toisistaan sen, mikä on
konekielelle yleistä (rekisterit, osoitteet, hypyt, pino), ja sen,
mikä on yhden arkkitehtuurin erityispiirre (liput, osoitusmuodot,
käskyjen pituus). Tutoriaali ei opeta käskykantojen kaikkia käskyjä;
täydelliset luettelot ovat valmistajien käsikirjoissa (luku Lopuksi).

## Esitiedot ja rajaus

Esitiedoiksi oletetaan taidot *C-kieli* (osoittimet, tietueet ja
kääntäminen) ja *Digitaalitekniikka* (bitit, kahden komplementti ja
rekisterit).

Tutoriaalin ulkopuolelle jäävät:

- suorittimen sisäinen toiminta (liukuhihna, välimuistit, hypyn
  ennustus): taito *Tietokonearkkitehtuuri*
- objektitiedostot, linkitys, relokaatiot ja dynaamiset kirjastot:
  *Objektitiedostot, linkitys ja ABI*
- inline-assembly ja kääntäjän sisäiset funktiot: *C ja assembly
  yhteen*
- ohjelmien analyysi ilman lähdekoodia: *Takaisinmallinnus*
- muut käskykannat. AArch64 esitellään luvussa 7 vain vertailuna.

## Työkalut

Esimerkit kootaan GNU-työkaluilla ja ajetaan Linuxissa:

| Työkalu | x86-64 | RISC-V |
|---------|--------|--------|
| Kääntäjä ja kokoaja | `gcc-14` | `riscv64-linux-gnu-gcc` |
| Disassembleri | `objdump -d` | `riscv64-linux-gnu-objdump -d` |
| Ajo | suoraan | `qemu-riscv64` (käyttäjätilan emulaattori) |

QEMU:n käyttäjätilan emulaattori suorittaa RISC-V-ohjelman tavallisena
prosessina x86-64-koneella ja välittää sen järjestelmäkutsut isäntänä
toimivalle Linuxille. Ohjelmat linkitetään staattisesti, jotta
emulaattori ei tarvitse RISC-V-version jaettuja kirjastoja.

Assembly kirjoitetaan `.S`-tiedostoihin (iso S), jotka kääntäjä ajaa
C:n esikääntäjän läpi ennen kokoamista. Tutoriaali käyttää GNU-kokoajan
syntaksia molemmilla arkkitehtuureilla. x86-64:llä se tarkoittaa
**AT&T-syntaksia**, joka eroaa valmistajan käsikirjojen Intel-
syntaksista:

| Asia | AT&T (GNU) | Intel |
|---------------------|--------------------------------|-------------------------------|
| Operandien järjestys | `add %rsi, %rax` (lähde, kohde) | `add rax, rsi` (kohde, lähde) |
| Rekisterit | `%rax` | `rax` |
| Vakiot | `$1` | `1` |
| Muistiosoite | `8(%rdi,%rsi,4)` | `[rdi+rsi*4+8]` |
| Operandin koko | käskyn pääte: `movb`, `movl`, `movq` | `byte ptr` jne. |

Kun luet Intelin tai AMD:n käsikirjaa, käännä operandien järjestys
mielessäsi. `objdump -M intel` näyttää disassemblyn Intel-syntaksilla.

Esimerkit ovat hakemistossa `esimerkit/`, jokainen omassa
alihakemistossaan. Hakemistossa on x86-64-toteutus `x86.S`,
RISC-V-toteutus `rv.S`, usein C-pääohjelma `main.c` ja odotettu
tuloste. Komento `make` kokoaa ja ajaa kaikki esimerkit molemmilla
arkkitehtuureilla ja vertaa tulosteita odotettuihin. Kehityskontissa
(`.devcontainer/assembly`) työkalut ovat valmiina.

## Ensimmäinen ohjelma

Ensimmäinen ohjelma ei käytä C-kirjastoa lainkaan. Se kirjoittaa rivin
käyttöjärjestelmän `write`-kutsulla ja lopettaa `exit`-kutsulla.
Ohjelma alkaa symbolista `_start`, johon käyttöjärjestelmä hyppää
ladattuaan ohjelman:

```{.gnuassembler tiedosto="esimerkit/01-hei/x86.S" osa="ohjelma"}
```

```{.gnuassembler tiedosto="esimerkit/01-hei/rv.S" osa="ohjelma"}
```

```{.tuloste tiedosto="esimerkit/01-hei/odotettu"}
```

Rakenne on sama: argumentit asetetaan sovittuihin rekistereihin,
järjestelmäkutsun numero omaansa ja suoritin siirtyy ytimeen käskyllä
`syscall` tai `ecall`. Erot ovat yksityiskohdissa: rekisterien nimet,
järjestelmäkutsujen numerot (write on x86-64:llä 1, RISC-V:llä 64)
ja se, että RISC-V-kokoaja tarvitsee pituuden arvon ennen käyttöä
(siksi data on tiedoston alussa). Rivit, jotka alkavat pisteellä, ovat
*direktiivejä* kokoajalle, eivät käskyjä: `.text` ja `.section
.rodata` valitsevat osion, `.globl` tekee symbolista näkyvän
linkittäjälle, `.ascii` sijoittaa tavuja ja `.set pituus, . - viesti`
laskee merkkijonon pituuden (`.` on nykyinen osoite).

Kokoaminen ja ajo käsin:

```text
gcc-14 -nostdlib -static -o hei x86.S && ./hei
riscv64-linux-gnu-gcc -nostdlib -static -o hei-rv rv.S
qemu-riscv64 ./hei-rv
```

Jokaisen tiedoston lopussa on rivi `.section .note.GNU-stack`, joka
kertoo linkittäjälle, ettei koodi tarvitse suoritettavaa pinoa. Ilman
sitä linkittäjä varoittaa ja tekee pinosta suoritettavan, mikä
heikentää tietoturvaa.

## Käskyt ovat tavuja

Kokoaja muuntaa käskyt tavuiksi. Disassembleri tekee saman toiseen
suuntaan: se lukee tavut ja näyttää käskyt. Kaksi pientä funktiota:

```{.gnuassembler tiedosto="esimerkit/01-tavut/x86.S"}
```

```{.tuloste tiedosto="esimerkit/01-tavut/odotettu-x86"}
```

Jokaisella rivillä on osoite, käskyn tavut ja käsky. x86-64:n käskyt
ovat eripituisia: `lea` on neljä tavua, `mov` kolme ja `ret` yksi.
Tavu `48` on *REX-etuliite*, joka tekee käskystä 64-bittisen.
Eripituiset käskyt säästävät muistia, mutta suoritin joutuu
selvittämään käskyjen rajat ennen kuin voi purkaa useita käskyjä
rinnakkain.

```{.gnuassembler tiedosto="esimerkit/01-tavut/rv.S"}
```

```{.tuloste tiedosto="esimerkit/01-tavut/odotettu-rv"}
```

RISC-V:n peruskäskyt ovat aina neljä tavua (`summaa_pitka`). C-laajennus
lisää kahden tavun tiivistetyt muodot yleisimmille käskyille, ja
kokoaja käyttää niitä automaattisesti (`952e` on `c.add`). `ret` on
*pseudokäsky*: kokoaja kirjoittaa sen tilalle hypyn paluuosoitteeseen
(`jalr x0, 0(ra)`). Pseudokäskyjä on paljon (`li`, `la`, `mv`, `j`,
`ble`), ja ne helpottavat lukemista.

## Tutoriaalin rakenne

Luvut 2–5 käyvät läpi konekielen peruskäsitteet: rekisterit ja muistin,
aritmetiikan ja liput, hypyt ja silmukat sekä pinon ja kutsukonventiot.
Luvussa 5 on myös debuggerin käyttö käsky kerrallaan; siihen
kannattaa tarttua heti, kun oma koodi kaatuu. Luku 6 lukee kääntäjän
tuottamaa koodia, luku 7 vertaa käskykantoja
saman algoritmin avulla ja luku 8 käyttää järjestelmäkutsuja ilman
C-kirjastoa. Luku 9 esittelee SIMD-käskyt ja luku 10 kokoaa kaiken
yhteen tarkistussumman toteutuksessa. Viimeisessä luvussa ovat nyrkkisäännöt
ja lähteet. Esimerkkihakemiston numero kertoo luvun: `05-pino` kuuluu
lukuun 5.

# Käskykanta

Käskykanta (ISA, *instruction set architecture*) on sopimus ohjelmiston
ja laitteiston välillä. Se määrää, mitä ohjelmoija ja kääntäjä saavat
olettaa, ja jättää kaiken muun toteutuksen päätettäväksi. Samaa
käskykantaa voi toteuttaa pieni mikro-ohjain, jossa ei ole edes
välimuistia, ja palvelinsuoritin, joka suorittaa satoja käskyjä
yhtäaikaa. Molemmilla sama binääri tuottaa saman tuloksen.

## Mitä käskykanta määrää

| Osa | Sisältö | RISC-V:ssä |
|-----|---------|------------|
| Tila | rekisterit, ohjelmalaskuri, muisti | x0–x31, pc, tavuosoitteinen muisti |
| Käskyt | operaatiot ja niiden merkitys | RV32I: 40 peruskäskyä |
| Koodaus | käskyjen bittiesitys | 32-bittiset käskyt, 6 muotoa |
| Datatyypit | sanan leveys, tavujärjestys | 32 tai 64 bittiä, little-endian |
| Osoitustavat | miten muistiosoite muodostetaan | rekisteri + 12-bittinen siirtymä |
| Etuoikeustasot | mitä käyttäjäkoodi saa tehdä | M-, S- ja U-tila, CSR:t |
| Poikkeukset | mitä virhetilanteessa tapahtuu | mtvec, mcause, mepc |
| Muistimalli | rinnakkaisten säikeiden näkymä | RVWMO, `fence` |

Käskykanta *ei* määrää liukuhihnan pituutta, välimuistien kokoa,
ennustimia eikä sitä, montako käskyä jaksossa suoritetaan. Nämä ovat
*mikroarkkitehtuuria*. Raja on tärkeä: kun ohjelma luottaa vain
käskykantaan, se toimii kaikilla toteutuksilla. Kun se luottaa
mikroarkkitehtuuriin (esimerkiksi ajoitukseen), se on joko optimointi
tai tietoturva-aukko (Spectre, luku 11).

## Lataa–talleta-arkkitehtuuri

RISC-V on *lataa–talleta*-arkkitehtuuri (load–store): laskutoimitukset
tehdään vain rekistereillä, ja muistiin viitataan vain lataus- ja
talletuskäskyillä. Lauseke `a[i] += x` vaatii siis neljä käskyä:
osoitteen laskun, latauksen, yhteenlaskun ja talletuksen. x86:ssa sama
on yksi käsky `add [rbx+rcx*4], eax`. Luvussa 12 nähdään, että
nykyaikainen x86-suoritin purkaa senkin sisäisesti lähes samoiksi
neljäksi operaatioksi.

Lataa–talleta-mallin etu on säännöllisyys: jokainen käsky tekee
enintään yhden muistiviitteen, lukee enintään kaksi rekisteriä ja
kirjoittaa enintään yhden. Liukuhihna voidaan siksi rakentaa niin, että
jokainen vaihe tekee jokaiselle käskylle saman asian (luku 4).

## RISC-V lyhyesti

RISC-V on avoin käskykanta, jonka Berkeleyn yliopisto julkaisi 2010 ja
jota nykyään ylläpitää RISC-V International. Se on modulaarinen:
peruskäskykanta (RV32I tai RV64I) on pieni ja jäädytetty, ja
laajennukset lisätään kirjaimin:

| Laajennus | Sisältö | Esimerkki |
|-----------|---------|-----------|
| M | kerto- ja jakolasku | `mul`, `div`, `rem` |
| A | atomiset operaatiot | `lr.w`, `sc.w`, `amoadd.w` |
| F, D | yksin- ja kaksoistarkkuuden liukuluvut | `fadd.d` |
| C | 16-bittiset tiivistetyt käskyt | `c.addi`, `c.lw` |
| V | vektorikäskyt | `vadd.vv` |
| Zicsr | ohjaus- ja tilarekisterit (CSR) | `csrrw` |

Tavallinen Linux-kelpoinen ydin on RV64GC, missä G = IMAFD + Zicsr +
Zifencei. Tämän tutoriaalin simulaattori toteuttaa RV32I:n
olennaisimmat käskyt sekä `mul`-käskyn M-laajennuksesta ja
muutaman CSR-käskyn poikkeuksia varten.

Rekistereitä on 32, ja `x0` on aina nolla: kirjoitus siihen hylätään.
Tämä yksinkertaistaa käskykantaa, sillä moni käsky saadaan
erikoistapauksena: `mv a0, a1` on `addi a0, a1, 0`, `nop` on
`addi x0, x0, 0` ja `j kohde` on `jal x0, kohde`.

## Käskymuodot

Kaikki RV32I-käskyt ovat 32-bittisiä ja kuuluvat johonkin kuudesta
muodosta. Bitit 6..0 ovat aina opcode, ja rekisterikentät ovat aina
samoissa paikoissa:

| Muoto | 31..25 | 24..20 | 19..15 | 14..12 | 11..7 | 6..0 |
|-------|--------|--------|--------|--------|-------|------|
| R | funct7 | rs2 | rs1 | funct3 | rd | opcode |
| I | imm[11:5] | imm[4:0] | rs1 | funct3 | rd | opcode |
| S | imm[11:5] | rs2 | rs1 | funct3 | imm[4:0] | opcode |
| B | imm[12,10:5] | rs2 | rs1 | funct3 | imm[4:1,11] | opcode |
| U | imm[31:25] | imm[24:20] | imm[19:15] | imm[14:12] | rd | opcode |
| J | imm[20,10:5] | imm[4:1,11] | imm[19:15] | imm[14:12] | rd | opcode |

Käyttötarkoitukset:

- **R**: rekisteri–rekisteri-laskut (`add`, `sub`, `and`, `sll`, `mul`).
- **I**: välitön operandi (`addi`, `slli`), lataukset (`lw`), `jalr`
  ja järjestelmäkäskyt.
- **S**: talletukset (`sw`). Välitön arvo on jaettu kahteen osaan,
  jotta rs1 ja rs2 pysyvät paikoillaan.
- **B**: ehdolliset haarat (`beq`, `blt`). Siirtymä on parillinen, joten
  bitti 0 jätetään pois ja alue on ±4 KiB.
- **U**: 20-bittinen yläosa (`lui`, `auipc`).
- **J**: `jal`, 21-bittinen parillinen siirtymä, ±1 MiB.

Välittömien arvojen bittien järjestys näyttää oudolta, mutta se on
tarkoituksellinen. Etumerkkibitti on *aina* bitissä 31, joten
etumerkkilaajennus voidaan aloittaa ennen kuin muoto on edes selvillä.
Rekisterikentät ovat aina samoissa paikoissa, joten rekisteritiedoston
luku voi alkaa samassa jaksossa kuin dekoodaus. B- ja J-muodon bitit on
sekoitettu niin, että mahdollisimman moni bitti on samassa paikassa kuin
S- ja I-muodossa: laitteistossa tarvitaan vähemmän multipleksereitä.
Ohjelmistossa sama sekoitus näyttää tältä:

```{.cpp tiedosto="esimerkit/yhteinen/rv32i.hpp" osa="kentat"}
```

Koodaus on purun peilikuva: samat bitit siirretään takaisin
paikoilleen (`koodaa_r` … `koodaa_j` samassa tiedostossa).

Esimerkki kokoaa yhden käskyn kustakin muodosta ja purkaa konekoodin
takaisin kentiksi. Kenttä, jota muodossa ei ole, näytetään viivana:
niiden bitit kuuluvat välittömään arvoon.

```{.cpp tiedosto="esimerkit/02-koodaus.cpp" osa="kentat"}
```

```{.tuloste tiedosto="esimerkit/02-koodaus.odotettu"}
```

Huomioita tulosteesta:

- `addi t0, t0, -1` on `fff28293`: välittömän arvon kaikki 12 bittiä
  ovat ykkösiä, ja etumerkkilaajennus tekee niistä −1:n.
- `sw ra, -4(sp)` jakaa siirtymän −4 kahteen osaan: bitit 11..5 ovat
  käskyn yläosassa ja bitit 4..0 rd-kentän paikalla.
- Haaran ja hypyn siirtymä lasketaan käskyn omasta osoitteesta: `beq`
  osoitteessa 16 hyppää osoitteeseen 28 (+12), ja `jal` osoitteesta 24
  osoitteeseen 0 (−24).
- `lui a5, 0x12345` sijoittaa arvon 0x12345000 = 305 418 240.

Viimeinen rivi on *kierrostesti* (round trip): jokainen mahdollinen
haarasiirtymä ja jokainen hyppysiirtymä koodataan ja puretaan, ja
tulosta verrataan alkuperäiseen. Bittikenttien käsittelyssä kierrostesti
on paras tapa löytää virheet, koska se kattaa koko arvoalueen eikä
vaadi käsin laskettuja odotusarvoja.

```{.cpp tiedosto="esimerkit/02-koodaus.cpp" osa="takaisin"}
```

## Suuret vakiot ja pseudokäskyt

Välitön arvo on enintään 12 bittiä, joten 32-bittinen vakio vaatii kaksi
käskyä: `lui` asettaa ylimmät 20 bittiä ja `addi` alimmat 12. Koska
`addi` laajentaa etumerkin, yläosaan on lisättävä yksi, kun alaosan
bitti 11 on ykkönen. Kokoaja tekee tämän laskemalla yläosan muodossa
`(arvo + 0x800) >> 12`. Esimerkiksi `li t1, 0x02004000` on pelkkä `lui`,
mutta `li t0, 0x12345fff` on `lui t0, 0x12346` ja `addi t0, t0, -1`.

Samalla tavalla `call` on `auipc ra, yläosa` ja `jalr ra, alaosa(ra)`:
kaukokutsu, joka toimii mistä osoitteesta tahansa, koska `auipc` lisää
yläosan omaan osoitteeseensa (pc-suhteellinen koodi). Disassembler
näyttää pseudokäskyt todellisina käskyinä:

```{.cpp tiedosto="esimerkit/02-purku.cpp"}
```

```{.tuloste tiedosto="esimerkit/02-purku.odotettu"}
```

`li a0, 16` on `addi a0, zero, 16`, `mv s0, a0` on `addi s0, a0, 0` ja
`ret` on `jalr zero, 0(ra)`. Rekursiivinen `fib` tallettaa pinoon
paluuosoitteen, tallennettavan rekisterin ja argumentin: jokainen kutsu
maksaa kuusi muistiviitettä. Tämä näkyy myöhemmin välimuisti- ja
ennustinluvuissa.

## Koodin tiheys

Kiinteäpituiset 32-bittiset käskyt ovat helppoja purkaa, mutta ne vievät
tilaa. Käskyvälimuisti on pieni (tyypillisesti 32–64 KiB), ja
sulautetuissa järjestelmissä koodi on usein kalliissa flash-muistissa.
RISC-V:n C-laajennus lisää 16-bittiset muodot yleisimmille käskyille,
ja sen avulla koodi pienenee noin 25–30 %. Pituus selviää käskyn kahdesta
alimmasta bitistä (`11` = 32-bittinen), joten purkaja tietää heti,
missä seuraava käsky alkaa. x86:n 1–15 tavun käskyissä pituus selviää
vasta useamman tavun tutkimisen jälkeen, mikä tekee rinnakkaisesta
purusta vaikeaa (luku 12).

## Käytännössä

- **Lue disassemblya.** Kun koodi on hidas, katso, mitä kääntäjä
  tuotti: `objdump -d`, `riscv64-unknown-elf-objdump -d` tai Compiler
  Explorer. Käskymäärä ja muistiviitteiden määrä silmukassa ovat
  ensimmäiset asiat, jotka kannattaa tarkistaa.
- **Käskykanta on pysyvä lupaus.** Siksi uudet käskyt lisätään
  laajennuksina eikä vanhoja muuteta. Ohjelma voi tarkistaa
  laajennukset ajonaikaisesti (`misa`-CSR, Linuxissa `hwprobe`-kutsu)
  ja valita nopeimman toteutuksen.
- **Kierrostestaa bittikentät.** Koodaa–pura–vertaa koko arvoalueella
  löytää etumerkki- ja siirtovirheet, joita käsin valitut esimerkit eivät
  löydä.
- **Kääntäjän kohde ratkaisee.** `-march=rv64gc` sallii tiivistetyt ja
  liukulukukäskyt; väärä kohde tuottaa joko hitaampaa koodia tai
  binäärin, joka kaatuu laittomaan käskyyn.

## Itsearviointi

- Osaat erottaa käskykannan ja mikroarkkitehtuurin ja kertoa, mitkä
  ominaisuudet kuuluvat kumpaankin.
- Osaat purkaa RV32I-käskyn heksaesityksestä kentiksi kaikissa kuudessa
  muodossa ja laskea haaran kohdeosoitteen.
- Osaat selittää, miksi etumerkkibitti on aina bitissä 31 ja miksi
  rekisterikentät eivät liiku.
- Osaat muodostaa 32-bittisen vakion `lui`- ja `addi`-käskyillä,
  myös kun alaosan bitti 11 on ykkönen.

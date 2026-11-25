---
title: Takaisinmallinnus
subtitle: Pikaopas · Linux x86-64, ELF · objdump, radare2, gdb
---

# Staattinen tutkiminen

| Kysymys | Komento |
|---------|---------|
| tiedoston tyyppi, kone, tulokohta | `readelf -h f`, `file f` |
| osiot ja segmentit | `readelf -SW f`, `readelf -lW f` |
| dynaamiset symbolit (tuonnit, viennit) | `nm -D f`, `readelf --dyn-syms f` |
| puretut C++-nimet | `nm -C f`, `c++filt NIMI` |
| merkkijonot | `strings -n 6 f`, radare2 `iz` |
| riippuvuudet, RUNPATH | `readelf -d f`, `ldd f` |
| funktioiden rajat riisutusta | `readelf --debug-dump=frames f` |
| purku (Intel, ei osoitteita) | `objdump -d -M intel --no-addresses f` |
| yhden funktion purku | `objdump -d --disassemble=NIMI f` |

# radare2 eräajona

| Komento | Merkitys |
|---------|----------|
| `r2 -q -c 'KOMENNOT' f` | aja komennot ja lopeta |
| `aaa` | analysoi funktiot, viittaukset, argumentit |
| `afl` | funktiot: osoite, lohkot, koko, nimi |
| `pdf @ f`, `pdc @ f` | purku, karkea pseudokoodi |
| `agf @ f` | ohjausvuograafi ASCII-kuvana |
| `axt @ x`, `axf @ x` | viittaukset kohteeseen / kohteesta |
| `iz`, `izz` | merkkijonot data-osioista / koko tiedostosta |
| `afn nimi @ x`, `s x` | nimeä funktio, siirry |

# Konekielen lukeminen (System V, x86-64)

| Kohde | Missä |
|-------|-------|
| argumentit 1–6 | `rdi rsi rdx rcx r8 r9` |
| liukuluvut 1–8 | `xmm0`–`xmm7` |
| paluuarvo | `rax` (liukuluku `xmm0`) |
| pinoargumentti | `[rbp+0x10]`, `[rbp+0x18]`, … |
| kutsuttu säilyttää | `rbx rbp r12`–`r15` |
| etumerkitön vertailu | `jb ja jbe jae` |
| etumerkillinen vertailu | `jl jg jle jge` |
| kanarialintu (pinopuskuri) | `fs:0x28`, `__stack_chk_fail` |
| CET-merkintä (ohita luettaessa) | `endbr64` |

# Kuviot

| Konekieli | Lähdekoodi |
|-----------|------------|
| taaksepäin hyppäävä `jXX` | silmukka |
| `cmp` rajaan, epäsuora `jmp` taulusta | `switch` (hyppytaulu) |
| `jmp` toiseen funktioon | häntäkutsu (kutsu + paluu) |
| vakiosiirtymät samasta osoittimesta | rakenteen kentät |
| `imul` suurella vakiolla + `shr`/`sar` | jako vakiolla ($d=2^s/M$) |
| `xmm`-käskyt + skalaarinen jäännös | vektoroitu silmukka |
| olion 1. sana → `.data.rel.ro` | C++ vptr → vtable |

# Dynaaminen analyysi

| Tehtävä | Komento |
|---------|---------|
| järjestelmäkutsut | `strace -f -e trace=GRUPPI ./f` |
| kirjastokutsut | `ltrace -e FUNKTIO ./f` |
| gdb eräajona | `gdb -q -batch -nx -x s.gdb --args ./f` |
| katkaisu, ehdollinen | `break F`, `break F if $rsi>100` |
| rekisteri, muisti | `p/x $rdi`, `x/8xb $rsi`, `p (char*)$rdi` |
| paluuarvon muutos | `FinishBreakpoint` → `set $rax = 0` |
| vahtipiste | `watch *(long*)&muuttuja` |
| funktion korvaus | `LD_PRELOAD=./koukku.so ./f` |

# Muotojen ja protokollien päättely

| Vaihe | Keino |
|-------|-------|
| rakenne | heksavedos (`od -A x -t x1z`), tunniste |
| salattu vs. rakenne | entropia (lähellä 8 = satunnainen) |
| kentät | aikaleimat (kasvavat), pituudet, tarkisteet lopussa |
| varmistus | jäsennin, joka kirjoittaa tiedoston uudelleen samaksi |
| protokolla | kaappaus: vakiotavut, pituus, numero, pyyntö/vastaus |

# Obfuskoinnin tunnistus ja purku

| Tekniikka (tunnistus) | Purku tai johtopäätös |
|-----------------------|-----------------------|
| salatut merkkijonot (`strings` tyhjä) | lue muistista ajossa, tai pura `.rodata` skriptillä |
| ohjausvuon litistys (välittäjä) | lue välittäjän tila → lohko ja seuraajat |
| läpinäkymätön predikaatti | todista ehto vakioksi, etsi kuollut haara |
| debuggerin havaitseminen (`ptrace`, `TracerPid`) | yksi haara konekielessä: ei suojaa mitään |

# Muista

Havainnoi ennen purkua · etene ristiviittauksin · nimeä heti ·
dekompilaattori kartoittaa, konekieli ratkaisee · varmista
toteutuksella · skriptaa kaikki · salaisuus ei kuulu asiakaskoodiin.

**Vastuulauseke.** Vain omat ohjelmat ja kohteet, joihin on lain tai
kirjallisen luvan antama oikeus; ei toisten ohjelmien suojausten
kiertämiseen. Harjoituskohteet: pääoppaan luku 12.

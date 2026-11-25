# Johdanto {.runko-johdanto}

Kääntäjä muuntaa ohjelman kielestä toiseen niin, että ohjelman
merkitys säilyy. Tavallisimmin lähdekieli on ihmisen kirjoittama
ohjelmointikieli ja kohdekieli suorittimen konekieli, mutta sama
tekniikka on kaikkialla: SQL-kysely käännetään suoritussuunnitelmaksi,
TypeScript JavaScriptiksi, shaderi GPU:n käskyiksi, laitteistokuvaus
porttiverkoksi ja säännöllinen lauseke tilakoneeksi. Kääntäjätekniikka
on siksi yleistaito: sen avulla rakennetaan konfiguraatiokielten
tulkit, koodigeneraattorit, staattiset analysaattorit, lintterit,
muotoilijat ja kielipalvelimet.

Tässä tutoriaalissa rakennetaan kokonainen kääntäjä pienelle
**Kide**-kielelle. Kääntäjä on kirjoitettu C++23:lla, ja se tuottaa
RISC-V-assemblyä (RV64IM), joka kootaan ristikääntäjällä ja ajetaan
QEMU-emulaattorissa. Kääntäjässä on noin 3000 riviä, joten sen voi
lukea kokonaan; jokainen luku esittelee yhden vaiheen ja sen koodin.

## Esitiedot ja rajaus

Esitiedoiksi oletetaan *Algoritmit* (verkot, syvyyshaku,
kiintopisteiteraatio), *Assembly* (RISC-V-käskyt, kutsukonventio ja
pino), *Funktionaalinen ohjelmointi (Racket)* (rekursiiviset
tietotyypit ja hahmonsovitus, joita syntaksipuun käsittely muistuttaa)
ja *Moderni C++*, jolla kääntäjä on kirjoitettu: `std::variant`,
`std::unique_ptr`, lambdat ja designoidut alustajat.

Kääntäjä on pidetty noin 3000 rivissä, joten osa aiheista on rajattu
pois. Kide-kielessä on vain kokonaislukuja ja funktioita, joten
ajonaikainen ympäristö jää pinokehykseen: taulukot, keko ja
muistinhallinta eivät ole mukana (taulukot ovat luvun 17
harjoituksena). SSA-muoto rakennetaan, mutta optimoinnit tehdään
tavallisella välikielellä, eikä takaosassa ole käskyjen valinnan
viimeistelyä (kurkistusoptimointia). Jäsenningeneraattorit ja
LR-jäsennys esitellään vain vertailuna. Luku 16 näyttää, mitä
tuotantokääntäjä tekee toisin.

Läheisiä taitoja ovat *Suorituskyvyn analyysi ja optimointi*,
*Takaisinmallinnus* ja *Korkean tason synteesi*, joissa kääntäjän
tuottamaa koodia luetaan, arvioidaan ja ohjataan.

## Kääntäjän vaiheet

Kääntäjä jaetaan perinteisesti kolmeen osaan:

| Osa | Vaihe | Syöte | Tuloste | Luku |
|-----|-------|-------|---------|------|
| Etuosa | selaus | merkit | tokenit | 3 |
| | jäsennys | tokenit | syntaksipuu | 4–6 |
| | semanttinen analyysi | syntaksipuu | tarkistettu puu | 7 |
| Keskiosa | alentaminen | puu | välikieli | 9 |
| | analyysit ja optimoinnit | välikieli | välikieli | 10–12 |
| Takaosa | koodingenerointi | välikieli | assembly | 13 |
| | rekisterien varaus | välikieli | rekisterit | 14 |

```{.dot otsikko="Kide-kääntäjän vaiheet ja niiden väliesitykset"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.55;
  edge [fontsize=8];
  lahde [label=".kide", shape=note, fillcolor="#FFFFFF"];
  asm [label=".s", shape=note, fillcolor="#FFFFFF"];
  subgraph cluster_etu { label="etuosa"; color="#D9E0E3";
    {rank=same; sem [label="semanttinen\nanalyysi"];
     jasennys [label="jäsennys"]; selaus;} }
  subgraph cluster_keski { label="keskiosa"; color="#D9E0E3";
    {rank=same; opt [label="SSA ja\noptimoinnit"];
     alennus [label="alentaminen"];} }
  subgraph cluster_taka { label="takaosa"; color="#D9E0E3";
    {rank=same; varaus [label="rekisterien\nvaraus"];
     koodi [label="koodin-\ngenerointi"];} }
  lahde -> selaus [label="merkit"];
  selaus -> jasennys [label="tokenit"];
  jasennys -> sem [label="puu"];
  sem -> alennus [label="puu"];
  alennus -> opt [label="IR"];
  opt -> koodi [label="IR"];
  koodi -> varaus;
  varaus -> asm;
}
```

**Etuosa** (*front end*) tuntee lähdekielen: sen kieliopin, nimien
näkyvyyden ja tyypit. Se hylkää virheelliset ohjelmat ja kertoo
virheiden paikat. **Keskiosa** (*middle end*) käsittelee ohjelmaa
kielestä ja kohteesta riippumattomassa *välikielessä* (*intermediate
representation*, IR), jossa optimoinnit on helpointa tehdä.
**Takaosa** (*back end*) tuntee kohdekoneen: käskyt, rekisterit ja
kutsukonvention.

Jako on tärkeä myös ohjelmistotekniikan kannalta. GCC ja LLVM
kääntävät kymmeniä lähdekieliä kymmenille arkkitehtuureille; ilman
yhteistä välikieltä tarvittaisiin jokaiselle kieli–kone-parille oma
kääntäjä. Rust, Swift, Zig ja Julia käyttävät LLVM:n keski- ja
takaosaa ja kirjoittavat itse vain etuosan.

## Kide-kieli

Kide on tarkoituksella pieni: siinä on 64-bittiset kokonaisluvut ja
totuusarvot, muuttujat, `if`, `while`, funktiot ja rekursio sekä
tulostus. Pienuus on valinta: jokainen vaihe näkyy kokonaan, ja
jokaista vaihetta voi testata ohjelmilla, joiden tuloksen tietää.
Esimerkki:

```{.rust tiedosto="esimerkit/ohjelmat/kertoma.kide"}
```

Ohjelma tulostaa kertomat 1!–10!:

```{.tuloste tiedosto="esimerkit/ohjelmat/kertoma.odotettu"}
```

Kide-koodi näytetään tässä tutoriaalissa Rustin korostuksella, koska
syntaksit muistuttavat toisiaan: `fn`, nuoli paluutyypin edessä ja
ehto ilman sulkeita. Merkitys on kuitenkin yksinkertaisempi kuin
Rustissa; luku 2 määrittelee sen tarkasti.

## Työkalut ja hakemistot

| Työkalu | Käyttö |
|---------|--------|
| `g++-14`, `clang++-20` | kääntäjän kääntäminen sanitoijien kanssa |
| `riscv64-linux-gnu-gcc` | assemblyn kokoaminen ja linkitys |
| `qemu-riscv64` | RISC-V-ohjelman ajo x86-64-koneella |
| `python3` | satunnaisten testiohjelmien generointi |

Esimerkkihakemistossa `esimerkit/` ovat kääntäjän lähdekoodi
(`kide/`), testiohjelmat (`ohjelmat/`, `virheet/`), tekstissä näytetyt
välitulosteet (`naytteet/`), ajonaikainen kirjasto ja testiajuri
`testaa.sh`. Komento `make` kääntää kääntäjän ja ajaa kaikki testit.

Kääntäjällä on valinta jokaisen vaiheen tulosteelle, joten jokaisen
luvun esimerkit voi toistaa itse:

```{.cpp tiedosto="esimerkit/kide/main.cpp" osa="kaytto"}
```

## Ensimmäinen käännös

Testiajuri kääntää ohjelman assemblyksi, linkittää sen
ajonaikaisen kirjaston kanssa ja ajaa sen QEMU:n käyttäjätilan
emulaattorissa, joka välittää ohjelman järjestelmäkutsut isäntäkoneen
Linuxille:

```{.bash tiedosto="esimerkit/testaa.sh" osa="kaanna"}
```

Ajonaikainen kirjasto on tavallista C:tä. Se tarjoaa `print`-lauseen
toteutuksen ja C:n `main`-funktion, joka kutsuu Kide-ohjelman
`main`-funktiota. Kide-funktiot saavat etuliitteen `k_`, jotta
käyttäjän funktio ei voi törmätä C-kirjaston nimiin:

```{.c tiedosto="esimerkit/ajonaikainen.c" osa="kirjasto"}
```

Kääntäjän tuottama koodi noudattaa RISC-V:n kutsukonventiota (psABI),
joten se voi kutsua C-funktioita ja C voi kutsua sitä. Kertomafunktio
näyttää käännettynä tältä:

```{.gnuassembler tiedosto="esimerkit/naytteet/asm-kertoma.txt"}
```

Koodi on oikeaa mutta ei vielä hyvää: vertailu `n <= 1` lasketaan
kolmella käskyllä ennen haaraa, ja vakio 1 ladataan rekisteriin
moneen kertaan. Luvussa 16 sitä verrataan GCC:n tuottamaan koodiin, ja
erot kertovat, mitä tuotantokääntäjät tekevät lisää.

Kääntäjän pääohjelma (`kide/main.cpp`) on koko kääntäjän
sisällysluettelo: se ajaa vaiheet peräkkäin, ja kukin ajetaan vain, jos
edelliset onnistuivat. Siinä näkyy kolme kääntäjien yleistä
suunnitteluperiaatetta. Ensinnäkin jokaisella vaiheella on oma, tulostettava tietorakenne, joten
vian voi paikantaa vaiheeseen katsomalla välitulosteita. Toiseksi
optimoinnit ovat valinnaisia: `-O0` tuottaa suoraviivaisen koodin, jota
on helppo verrata lähdekoodiin. Kolmanneksi takaosa on vaihdettavissa:
rekisterien varauksesta on kaksi toteutusta, ja niiden on tuotettava
samoin toimiva ohjelma. Testit (luku 15) nojaavat kaikkiin kolmeen.

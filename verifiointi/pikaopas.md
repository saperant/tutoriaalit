---
title: Laitteiston verifiointi
subtitle: Pikaopas · testipenkki, satunnaistus, kattavuus, SVA, cocotb, formaali, UVM
---

# Testipenkin osat

| Osa | Tehtävä | UVM |
|-----|---------|-----|
| transaktio | toimenpide tietueena | `uvm_sequence_item` |
| generaattori, sekvenssi | tuottaa transaktioita | `uvm_sequence` |
| ajuri | transaktio → signaalit | `uvm_driver` |
| monitori | signaalit → havainnot | `uvm_monitor` |
| referenssimalli | ennuste määrittelystä | (tulostaulun osa) |
| tulostaulu | havainto vs. ennuste | `uvm_scoreboard` |
| kattavuus | mitä tapahtui | `uvm_subscriber` |
| agentti, ympäristö, testi | kokoaa ja valitsee | `uvm_agent`, `uvm_env`, `uvm_test` |

- Ajuri asettaa tulot laskevalla reunalla, monitori lukee nousevalla.
- Malli päättää omasta tilastaan, ei DUT:n lipuista.
- Vertailu `!==`, jotta `x` havaitaan.
- Tulosta muutama ensimmäinen virhe, laske loput, päätä `$error`-kutsuun.

# Satunnaistus

| Keino | Tarkoitus |
|-------|-----------|
| rajoite | estää vain laittoman ärsykkeen |
| paino | ohjaa kohti kulmia (täysi, tyhjä, samanaikainen) |
| vaihe, purske, sekvenssi | syvät tilat nopeasti |
| siemen | toistettavuus: `+siemen=N`, `SIEMEN=N` |
| oma generaattori virtaa kohden | satunnaisstabiilisuus |

```text
void'($value$plusargs("siemen=%d", siemen));
void'($urandom(siemen));
x = $urandom_range(99);                 // 0..99
rng = random.Random(siemen)             # Python: oma olio
```

Verilator 5.020: `randomize()` arpoo `rand`-kentät, rajoitteet
ohitetaan (CONSTRAINTIGN).

# Kattavuus

| Laji | Mittari |
|------|---------|
| koodi | rivi, haara, ehto/lauseke, bitti (toggle), tilakone |
| toiminnallinen | piste, lokerot, laittomat ja ohitettavat lokerot, risti |
| väite | `cover property`, formaali `cover` |

```text
verilator --cc --exe --build --timing --coverage ... paa.cpp
./sim +kattavuus=a.dat
verilator_coverage --write yhdistetty.dat a.dat b.dat
verilator_coverage --annotate merkitty/ yhdistetty.dat
verilator_coverage --write-info kattavuus.info a.dat   # lcov
```

- `--binary` ei kirjoita kattavuutta: oma pääohjelma kutsuu
  `coveragep()->write(polku)`.
- Täysi koodikattavuus ≠ testattu: samanaikaisuus vaatii ristin tai
  ehtokattavuuden.
- Aukko: generaattori ei tuota → muuta rajoitteita; mahdoton →
  ohitettava lokero perusteluineen; malli väärin → korjaa.

# SVA

| Rakenne | Merkitys |
|---------|----------|
| `assert property (@(posedge clk) disable iff (rst) p)` | samanaikainen väite |
| `a \|-> b`, `a \|=> b` | sama jakso, seuraava jakso |
| `$past`, `$stable`, `$rose`, `$fell` | edellinen jakso, muutos |
| `$onehot`, `$onehot0` | tasan / korkeintaan yksi bitti |
| `cover property (...)` | esiehdon kattavuus |
| `bind fifo fifo_sva sva (.*);` | liitä väitteet muuttamatta lähdettä |

| Verilator 5.020 tukee | Ei tue |
|-----------------------|--------|
| `property`, `\|->`, `\|=>`, `disable iff` | `sequence`, `##n`, `##[m:n]` |
| `$past`, `$stable`, `$onehot0` ym. | `[*n]`, `[->n]`, `and`, `or`, `throughout` |
| `assert`, `assume`, `cover property` | `covergroup` |

Monijaksoinen sääntö ilman `##`: apulaskuri + väite laskurin rajasta.

# cocotb

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="aloitus"}
```

| Liipaisin | Käyttö |
|-----------|--------|
| `FallingEdge(clk)` | ajuri asettaa tulot |
| `RisingEdge(clk)` | monitori: arvot ennen rekisterien päivitystä |
| `ReadOnly()` | asettuneet arvot; ei kirjoituksia |
| `ClockCycles(clk, n)` | odota n jaksoa |
| `cocotb.start_soon(c)` | rinnakkainen korutiini |

- `dut: Any`; muu koodi `mypy --strict`.
- `x`: tarkista `value.is_resolvable` ennen `int()`.
- Ajaja: `get_runner("icarus").build(...)` ja `.test(...)`,
  JUnit-XML tulokseksi. cocotb 2 vaatii Verilator 5.036+.

# Formaali

```text
read_verilog -sv -formal fifo.sv     # makro FORMAL, assume, cover
prep -top fifo; async2sync; dffunmap
write_smt2 -wires malli.smt2
yosys-smtbmc -s z3 -t 10 malli.smt2          # BMC
yosys-smtbmc -s z3 -i -t 8 malli.smt2        # induktio
yosys-smtbmc -s z3 -c -t 10 --dump-vcd j%.vcd malli.smt2  # cover
```

```text
logic alku = 1'b1;                       // ainoa alkuarvo
always_ff @(posedge clk) alku <= 1'b0;
always_comb if (alku) assume (rst);      // alkaa nollauksesta
always_comb if (!alku) assert (maara <= 4);
always_ff @(posedge clk) if (!alku && !$past(rst))
    if ($past(push && taysi && !pop)) assert ($stable(maara));
```

| Tulos | Tulkinta |
|-------|----------|
| BMC failed | aito vika, lyhin polku nollauksesta |
| induction failed | aito vika tai puuttuva invariantti: onko alkutila saavutettava? |
| cover unreached | oletukset liian tiukat tai tila mahdoton |

- Kellotetun lohkon väite raportoidaan seuraavalla askeleella.
- Pienet parametrit; reiluus rajattuna ("4 jakson kuluessa").
- Ubuntu 24.04: ei `sby`-pakettia; Boolector 1.5 liian vanha.

# Regressio ja luokittelu

| Taso | Sisältö |
|------|---------|
| savutesti | jokainen muutos, kiinteät siemenet, minuutteja |
| yöajo | kaikki testit, satoja siemeniä, kattavuus yhteen |
| viikkoajo | pitkät testit, syvä formaali |

1. **Ryhmittele** tunnisteella (viesti ilman lukuja).
2. **Toista** pienimmällä siemenellä ja lyhimmällä testillä.
3. **Ensimmäinen poikkeama** DUT:n ja mallin välillä.
4. **Kumpi on väärässä**: RTL, malli, testipenkki vai määrittely?
5. **Korjaa ja lukitse** kattavuuskohteella, väitteellä tai testillä.

- Jokainen ajo omaan hakemistoonsa; toistokomento raporttiin.
- Normalisoi tuloste (polut, aikaleimat) ja vertaa kultaiseen.
- Epävakaa testi on vika, ei sattuma.
- Istuta vika jokaiselle tarkistukselle (`BUGI_*`, `--virhe`).

# Sudenkuopat

| Oire | Syy |
|------|-----|
| testi läpi, vika jää | ylirajoitettu generaattori, malli lukee DUT:n lippuja |
| väite ei koskaan epäonnistu | tyhjästi tosi: esiehto ei toteudu |
| formaali vihreä heti | liian tiukka `assume`; tarkista `cover` |
| induktio kaatuu, BMC läpi | mahdoton alkutila, puuttuva invariantti |
| tulos vaihtelee samalla siemenellä | kilpatilanne, alustamaton muuttuja |
| havainto jaksolla myöhässä | monitori luki `ReadOnly`-vaiheessa |

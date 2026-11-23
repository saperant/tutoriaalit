---
title: RTL-suunnittelu SystemVerilogilla
subtitle: Pikaopas kokeneelle kehittäjälle · IEEE 1800-2023 · Verilator 5.020
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Lint | `verilator --lint-only -Wall x.sv` |
| Simulointi | `verilator --binary --assert -Wall --top-module testipenkki *.sv` |
| Ajo | `./obj_dir/Vtestipenkki` |
| Aaltomuoto | `--trace` + `$dumpfile`/`$dumpvars`, katselu GTKWave |
| Väittämät | `--assert` (myös `unique`/`priority`-tarkistus) |
| Satunnainen alkutila | `--x-initial unique`, ajossa `+verilator+rand+reset+2` |
| Synteesi (Yosys) | `yosys -p "read_verilog -sv x.sv; synth -top x; stat"` |
| Verilog-2005:ksi | `sv2v x.sv > x.v` |
| Muotoilu | `verible-verilog-format --inplace x.sv` |

Varoitus vaiennetaan paikallisesti ja perustellaan:
`/* verilator lint_off UNUSEDSIGNAL */` … `/* verilator lint_on ... */`.

# Moduuli ja tyypit

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="moduuli"}
```

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="tyypit"}
```

- `logic` kaikkialle; `wire` vain usealle ajajalle. `int` silmukoihin
  ja parametreihin, `bit`/`byte` testipenkkiin.
- Literaalit: `8'hA5`, `4'b1010`, `-8'sd20`, `'0`, `'1`. Ilman leveyttä
  32 bittiä.
- Osavalinta: `v[7:4]`, `v[i*4 +: 4]`. Liitos `{a, b}`, toisto
  `{4{2'b10}}`, redusointi `^v`, `&v`, `|v`.
- Muunnokset: `N'(x)`, `signed'(x)`, `$signed(x)`, `tyyppi'(x)`.
- Instanssi: `laskuri #(.LEVEYS(8)) u_l (.clk, .rst_n, .arvo(a));`
- Toisto: `for (genvar i = 0; i < N; i++) begin : g_x ... end`
- Valinta: `if (N == 8) begin : g_8 ... end else begin ... end`
- Parametrin tarkistus: `if (...) begin : g_e $error("..."); end`

# Sijoitussäännöt

| Lohko | Sijoitus | Syntyy |
|-------|----------|--------|
| `always_ff @(posedge clk or negedge rst_n)` | `<=` | kiikkuja |
| `always_comb` | `=` | logiikkaa (salpa, jos arvo puuttuu polulta) |
| `assign y = ...;` | – | logiikkaa |

- Ei-estävä `<=` lukee reunaa edeltävät arvot: `a <= b; b <= a;`
  vaihtaa arvot.
- Yksi signaali, yksi ajaja, yksi lohko.
- `always_comb` alkaa oletussijoituksilla; `case` kattaa kaikki arvot
  tai sillä on `default`.
- `unique case`: haarat poissulkevia; `priority case`: järjestys
  ratkaisee.

# Mallipohjat

Rekisteri, asynkroninen nollaus ja sallinta:

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="rekisteri"}
```

Tilakone kaksiprosessityylillä:

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="tilakone"}
```

Pulssi: `p <= 1'b0; if (ehto) p <= 1'b1;`. Nouseva reuna:
`assign r = s & ~s_ed;` (`s_ed` on `s` viivästettynä).

Muisti (lohkomuisti päätellään):

```{.systemverilog tiedosto="esimerkit/08-ram.sv" osa="ram"}
```

FIFO: osoittimet `AW+1` bittiä, tyhjä `k == l`, täynnä
`k[AW] != l[AW] && k[AW-1:0] == l[AW-1:0]`.

Tahdistimet:

```{.systemverilog tiedosto="esimerkit/10-tahdistimet.sv" osa="taso"}
```

```{.systemverilog tiedosto="esimerkit/09-nollaus.sv" osa="tahdistin"}
```

# Testipenkki

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- Kello: `initial while (kaynnissa) #5 clk = ~clk;`, pysäytys
  `kaynnissa = 1'b0`.
- Syötteet ja näytteet reunan jälkeen: `@(posedge clk); #1;`.
- Virhe: `$fatal(1, "...")`. Viitemalli jonona: `logic [7:0] m[$];`,
  `m.push_back(x)`, `m.pop_front()`.
- `@(posedge clk iff ehto)` odottaa reunaa, jolla ehto on tosi.

# Kellotusalueiden ylitys

| Data | Rakenne |
|------|---------|
| hidas yksittäinen bitti | 2 kiikun tahdistin |
| pulssi | taso vaihtuu, tahdistin, reunantunnistus |
| satunnainen monibittinen arvo | nelivaiheinen kättely, data vakaana |
| jatkuva virta | asynkroninen FIFO, Gray-osoittimet |
| laskuri | Gray-koodi `b ^ (b >> 1)` + tahdistin |
| nollauksen vapautus | nollauksen tahdistin jokaiselle kellolle |

Rajan ylittävä signaali lähtee suoraan kiikusta. Simulaattori ei
mallinna metastabiiliutta.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| bittioperaatiot, vakiosiirrot (johdotusta) | jakolasku, `%` (ei RTL:ään) |
| `+`, `-`, vertailu | `*` ilman DSP-lohkoa |
| hierarkia, parametrit, `struct packed` | muuttuva siirto (`log2(W)` tasoa) |
| sallinta | muisti kiikuista (pinta-ala) |
| rekisteröity ulostulo | pitkä `if`-ketju (kriittinen polku) |
| datarekisteri ilman nollausta | nollausverkko kaikille kiikuille |

# Sudenkuopat

- Puuttuva `else` tai `default` → salpa (`LATCH`, `CASEINCOMPLETE`).
- `=` kellotetussa lohkossa → väärä viive, kilpailu (`BLKSEQ`).
- Sekalauseke etumerkillinen + etumerkitön → koko lauseke etumerkitön.
- Leveys määräytyy kontekstista; liitoksen osat itsemääräytyviä.
- Kirjoitusvirhe porttikytkennässä → implisiittinen 1-bittinen johto;
  käytä `` `default_nettype none``.
- Viive `#n` RTL:ssä: simuloi, mutta synteesi jättää pois.
- Kello jaettu kiikulla tai portitettu AND-portilla → uusi
  kellotusalue, piikit.
- `kelvollinen` riippuu `valmis`-signaalista → kombinatorinen silmukka.
- Kaksi bittiä tahdistettu erikseen → hetkellinen väärä yhdistelmä.
- Kaksitilainen simulaattori (Verilator) ei näytä `X`:ää: puuttuva
  nollaus voi jäädä huomaamatta.

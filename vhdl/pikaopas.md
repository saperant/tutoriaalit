---
title: RTL-suunnittelu VHDL:llä
subtitle: Pikaopas · VHDL-2008 · GHDL
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Analyysi | `ghdl -a --std=08 paketti.vhd lohko.vhd tb.vhd` |
| Elaborointi | `ghdl -e --std=08 testipenkki` |
| Simulointi | `ghdl -r --std=08 testipenkki --stop-time=1ms` |
| Aaltomuodot | `--wave=a.ghw` tai `--vcd=a.vcd`; GTKWave, Surfer |
| Riippuvuudet | `ghdl -i *.vhd` ja `ghdl -m testipenkki` |
| Salpatarkistus | `ghdl --synth --std=08 lohko.vhd -e lohko` |
| Varoitukset | `--warn-error`, `-Wsensitivity`; ajossa `--ieee-asserts=disable-at-0` |

# Entiteetti

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="entiteetti"}
```

- Suora instanssi: `u : entity work.lohko generic map (N => 4) port
  map (clk => clk, a => s, y => open);`
- Arkkitehtuurin valinta: `entity work.lohko(rtl)`.
- `out`-portin saa lukea VHDL-2008:ssa; `in`-porttiin ei voi sijoittaa.

# Tyypit

| Tyyppi | Käyttö |
|--------|--------|
| `std_logic`, `std_logic_vector` | bitit, rajapinnat |
| `std_ulogic(_vector)` | yksi ajuri: kaksoisajuri on elaborointivirhe |
| `unsigned`, `signed` | luvut (`ieee.numeric_std`) |
| `natural range 0 to N - 1` | laskurit, indeksit; alue tarkistetaan |
| `type t is (A, B)` | tilat, operaatiot |
| `record`, `array` | väylät, muistit |

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="muunnokset"}
```

| Operaatio | Leveys |
|-----------|--------|
| `a + b` | leveämpi; kanto katoaa → `resize(a, n + 1) + b` |
| `a * b` | summa |
| `resize(s, n)` | `signed`: etumerkin laajennus; kavennus säilyttää etumerkkibitin |

Vakiot: `x"F6"`, `12x"800"`, `8d"246"`, `(others => '0')`.
Ei `std_logic_arith`/`_unsigned`/`_signed`-paketteja.

# Kombinaatiologiikka

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="kombinaatio"}
```

- Rinnakkain: `y <= a when s = '1' else b;`, `with s select y <= ...`.
- Aina `process (all)`; oletussijoitukset ensin (ei salpoja).
- `case` luettelotyypille ilman `others`; vektorille `when others`.
- Yhdentekevä vertailu: `?=`, `std_match`, ei `=` merkin `'-'` kanssa.

# Tilakone ja rekisterit

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="tilakone"}
```

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="rekisteri"}
```

- Asynkroninen nollaus: `process (clk, rst_n)`, `if rst_n = '0' then
  ... elsif rising_edge(clk) then`.
- Signaali päivittyy deltasyklin lopussa, muuttuja heti.
- Ei `clk_b <= clk`: deltaviive kelloon rikkoo simuloinnin.
- Pulssi: oletus `'0'` prosessin alussa, `'1'` tapahtumassa.

# Parametrointi

| Rakenne | Esimerkki |
|---------|-----------|
| generic | `generic (N : positive := 8)` |
| rajoittamaton portti | `d : in std_logic_vector` + `d'length`, `d'range` |
| geneerinen tyyppi | `generic (type alkio_t)` |
| monistus | `g : for i in 0 to N - 1 generate ... end generate;` |
| valinta | `g : if N = 0 generate ... else generate ... end generate;` |
| tarkistus | `assert N mod 2 = 0 report "..." severity failure;` |

# Paketit

| Rakenne | Huomio |
|---------|--------|
| `package` / `package body` | esittely / toteutus; analysoidaan ennen käyttäjiä |
| `function` | puhdas oletuksena, ei `wait`-lauseita |
| `impure function` | saa lukea ulkoista tilaa |
| `procedure` | `wait` sallittu; testipenkin väylämallit |
| `type t is protected` | jaettu muuttuja testipenkissä |

Standardipaketit: `numeric_std`, `fixed_pkg`, `float_pkg`, `math_real`
(vakiot, `uniform`), `std.textio`, `std.env` (`finish`, `stop`).

# Testipenkki

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="tb-alku"}
```

```{.vhdl tiedosto="esimerkit/pikaopas.vhd" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

- Kello: `clk <= not clk after T / 2 when ajossa;`
- Odotus aikarajalla: `wait until valmis = '1' for 1 us;`
- Tuloste: `write(rivi, "x = " & to_hstring(v)); writeline(output, rivi);`
- Tarkistus: `assert x = y report "..." severity failure;`
- Satunnaisuus: `uniform(s1, s2, r)` kiinteällä siemenellä.
- Kehykset: VUnit, OSVVM, UVVM, cocotb.

# Sudenkuopat

| Oire | Syy |
|------|-----|
| arvo `'X'` | kaksi ajuria `std_logic`-signaalilla |
| arvo jää päälle | puuttuva sijoitus kombinaatioprosessissa → salpa |
| simulointi ja laitteisto eroavat | puutteellinen herkkyyslista; delta kellossa |
| `bound check failure` | leveys ei täsmää tai arvo karkaa alueelta |
| vanha arvo samassa prosessissa | signaali luettu sijoituksen jälkeen; käytä muuttujaa |
| `metavalue detected` | `'U'` numeric_std-funktiolle; alusta tai ohita hetkellä 0 |
| simulointi ei pääty | odotus ilman aikarajaa, kello käy ikuisesti |

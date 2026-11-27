---
title: Kääntäjätekniikka
subtitle: Pikaopas · vaiheet, jäsennys, välikieli, SSA, optimoinnit ja RISC-V
---

# Vaiheet

| Vaihe | Tuloste | Kide |
|-------|---------|------|
| selaus | tokenit | `--vaihe=tokenit` |
| jäsennys | syntaksipuu | `--vaihe=ast` |
| semanttinen analyysi | sidottu, tyypitetty puu | virheet |
| tulkki | ohjelman tuloste | `--vaihe=aja` |
| alentaminen | välikieli | `--vaihe=ir -O0` |
| optimoinnit (`-O1`) | välikieli | `--vaihe=passit` |
| SSA-optimoinnit (`-O2`) | välikieli | `--vaihe=ssapassit` |
| analyysit | elävyys, dominanssi, SSA | `--vaihe=elavyys` ... |
| rekisterien varaus | elinvälit | `--vaihe=valit` |
| koodingenerointi | RISC-V-assembly | oletus |

# Kide-kieli

```{.rust tiedosto="esimerkit/ohjelmat/syt.kide"}
```

Tyypit `int` (64-bittinen, kiertävä) ja `bool`. Ehto on aina `bool`.
`&&` ja `||` oikosulkevat. `x / 0 = -1`, `x % 0 = x`, kuten RISC-V:n
`div` ja `rem`.

# Jäsennys

| Menetelmä | Idea |
|-----------|------|
| rekursiivinen eteneminen | yksi funktio kielioppisääntöä kohden |
| ennakointi | vaihtoehto valitaan 1–2 seuraavasta tokenista |
| Pratt | sitovuus; jatka, kun `voima > minimi` |
| vasen assosiatiivisuus | oikea puoli rajalla `voima` |
| oikea assosiatiivisuus | oikea puoli rajalla `voima - 1` |
| paniikkitila | ohita tokeneita `;`:een tai lauseen alkuun |
| virhetyyppi | tuntematon tyyppi kelpaa kaikkialle |

```{.cpp tiedosto="esimerkit/kide/jasennin.cpp" osa="sitovuus"}
```

# Välikieli ja SSA

- **Peruslohko**: sisään vain alusta, ulos vain lopusta
  (`jmp`, `br`, `ret`).
- **Hyppykoodi**: `a && b` ehdossa = kaksi haaraa, ei totuusarvoa.
- **Dominanssi**: A dom B, jos jokainen polku alusta B:hen kulkee A:n
  kautta. **DF(B)**: missä B:n dominanssi päättyy.
- **SSA**: jokainen rekisteri kirjoitetaan kerran; phi
  yhtymäkohdissa, iteroidulle dominanssirajalle; karsittu SSA vain
  eläville.
- **Pois SSA:sta**: kopiot edeltäjiin; jaa kriittiset kaaret
  (kadonnut kopio), järjestä phien kopiot rinnakkaisina (vaihto),
  sulauta kopiot, jos kohde ja lähde eivät häiritse toisiaan.

| SSA-passi | Idea | Ei saa |
|-----------|------|--------|
| vakioiden eteneminen | hila ylä → vakio → ala; vain suoritettavat kaaret | phi eri vakioista |
| arvonumerointi | taulu dominaattoripuuta pitkin | laskenta ei dominoi; kutsu |
| kuollut koodi | merkitse vaikutuksista, lakaise loput | kutsu, tulostus, haara |

# Datavuoanalyysi

| Analyysi | Suunta | Yhdistys | Käyttö |
|----------|--------|----------|--------|
| elävyys | taakse | yhdiste | kuollut koodi, varaus |
| saavuttavat määrittelyt | eteen | yhdiste | vakioiden eteneminen |
| saatavilla olevat lausekkeet | eteen | leikkaus | yhteiset alilausekkeet |

Elävyys: $\text{ulos}(B) = \bigcup_{S} \text{sisään}(S)$,
$\text{sisään}(B) = \text{käyttö}(B) \cup (\text{ulos}(B) \setminus
\text{määr}(B))$. Iteroi kiintopisteeseen; monotoninen siirtofunktio ja
äärellinen hila takaavat päättymisen.

# Optimoinnit

| Optimointi | Esimerkki |
|------------|-----------|
| laskostus | `6 * 7` → `42` |
| vakioiden eteneminen | `x = 42; y = x + 1` → `y = 43` |
| kopioiden eteneminen | `x = y; z = x` → `z = y` |
| yhteiset alilausekkeet | `(a+b)*(a+b)` → `t*t` |
| algebra | `x*1`, `x+0`, `x*0` |
| haaran sievennys | `br 1, A, B` → `jmp A` |
| kuollut koodi | tulos ei elävä eikä sivuvaikutuksia |
| ohjausvuo | tyhjät lohkot, ketjut, saavuttamattomat |
| kopioiden yhdistäminen | `t = a+b; x = t` → `x = a+b` |

Säännön on pädettävä kielen semantiikassa (ylivuoto, nolla, NaN).

# RISC-V LP64

| Rekisteri | Tehtävä | Tallentaa |
|-----------|---------|-----------|
| `ra` | paluuosoite | kutsuja |
| `sp` | pino, 16:lla jaollinen | kutsuttu |
| `s0` | kehysosoitin | kutsuttu |
| `s1`–`s11` | tallennettavat | kutsuttu |
| `a0`–`a7` | argumentit, `a0` paluuarvo | kutsuja |
| `t0`–`t6` | väliaikaiset | kutsuja |

Vertailut `slt`:stä: `a > b` = `slt b, a`; `a <= b` = `!(b < a)`;
`a == b` = `seqz (a - b)`. Siirtymä 12 bittiä (±2048).

# Rekisterien varaus

| Menetelmä | Laatu | Nopeus |
|-----------|-------|--------|
| kaikki pinoon | huono | erittäin nopea |
| lineaarinen pyyhkäisy | kohtuullinen | nopea (JIT) |
| graafinväritys (Chaitin–Briggs) | hyvä | hitaampi |

Lineaarinen: välit alun mukaan; vapauta päättyneet; pulassa pinoon
pisimpään elävä. Paremmin: viennin hinta ~ käytöt × $10^{\text{syvyys}}$.

# Testaus

- Kääntäjä sanitoijin (ASan, UBSan) kahdella kääntäjällä.
- Kultaiset tulosteet: ohjelmat, virheet, välitulosteet.
- Differentiaalitestaus: tulkki vs. käännetty, satunnaiset
  määritellyt ja päättyvät ohjelmat, siemen toistaa.
- Testien teho: istutettu vika (`KIDE_VIKA`) on löydyttävä.
- Pienennä löydetty ohjelma (C-Reduce) ja lisää kultaisiin.

```{.bash tiedosto="esimerkit/testaa.sh" osa="valinnat"}
```

# Työkalut

| Komento | Näyttää |
|---------|---------|
| `gcc -fdump-tree-all` | GIMPLE passeittain |
| `clang -S -emit-llvm` | LLVM IR |
| `opt -print-after-all` | LLVM-passit |
| `riscv64-linux-gnu-gcc -O2 -S` | RISC-V-assembly |
| `qemu-riscv64 ohjelma` | RISC-V-ohjelman ajo |

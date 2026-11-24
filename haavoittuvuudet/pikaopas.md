---
title: Haavoittuvuuksien analyysi ja torjunta
subtitle: Pikaopas · C, Linux x86-64 · sanitoijat, suojaukset, fuzzaus
---

# Vastuulauseke

Vain omat ohjelmat ja järjestelmät tai kirjallisella luvalla testattavat
kohteet. Luvaton tunkeutuminen on rikos (rikoslain 38. luku). Laillinen
harjoittelu: picoCTF, OverTheWire, pwn.college, Hack The Box,
TryHackMe, CTFtime, OWASP Juice Shop.

# Sanitoijat

| Valitsin | Löytää |
|----------|--------|
| `-fsanitize=address` | yli- ja alivuodot, käyttö vapautuksen jälkeen, kaksoisvapautus |
| `-fsanitize=undefined` | etumerkillinen ylivuoto, rajat (`bounds`), väärä tasaus |
| `-fno-sanitize-recover=all` | pysähtyy ensimmäiseen virheeseen |
| `-fno-omit-frame-pointer -g` | luettavat pinot |
| `-fsanitize=thread` | datakilpailut (ei yhdessä ASanin kanssa) |
| `ASAN_OPTIONS=detect_leaks=0` | vuotojen tarkistus pois |

ASan ei näe tietueen sisäistä ylivuotoa; UBSan:n `bounds` näkee.

```{.bash tiedosto="esimerkit/yhteinen.sh" osa="liput"}
```

# Raportin lukeminen

| Rivi | Kertoo |
|------|--------|
| `ERROR: AddressSanitizer: X` | virheen laji |
| `READ/WRITE of size N` | operaatio ja koko |
| ensimmäinen oma kehys | kaatumiskohta (ei välttämättä juurisyy) |
| `located N bytes after M-byte region` | mihin varaukseen osui |
| `allocated by`, `freed by` | varaus- ja vapautuspino |
| varjotavut `00`, `fa`, `fd`, `f1`–`f3` | käytettävä, keon vyöhyke, vapautettu, pinon vyöhykkeet |

# Turvallinen C

| Vältä | Käytä |
|-------|-------|
| `gets` | `fgets`, `getline` |
| `strcpy`, `strcat`, `sprintf` | `memcpy` tunnetulla pituudella, `snprintf` |
| `atoi` | `strtol` + `errno` + loppuosoitin |
| `malloc(a * b)` | `ckd_mul`, `calloc`, `reallocarray` |
| `printf(x)` | `printf("%s", x)` |
| `int` koolle | `size_t`, rajat ennen muunnosta |

```{.c tiedosto="esimerkit/02-turvallinen-c/koko.c" osa="koko"}
```

# Varoitukset ja analyysi

| Komento | Tarkoitus |
|---------|-----------|
| `-Wall -Wextra -Wconversion -Wformat=2 -Werror` | perustaso |
| `-Wformat-security`, `-Wuse-after-free` | muotoilu, vapautettu muisti |
| `gcc -fanalyzer` | polkuanalyysi, CWE-luokat |
| `clang-tidy` + `.clang-tidy` | `bugprone-*`, `cert-*`, `clang-analyzer-*` |
| `bugprone-implicit-widening-of-multiplication-result` | koon laskennan variaatiot |

# Suojaukset

| Suojaus | Valitsin | Tarkistus (`readelf -W`) |
|----------|-----------------------------|------------------------|
| PIE + ASLR | `-fPIE -pie` | `-h`: `DYN` |
| NX | oletus; ei `-z execstack` | `-l`: `GNU_STACK` ilman `E` |
| pinokanari | `-fstack-protector-strong` | `--dyn-syms`: `__stack_chk_fail` |
| täysi RELRO | `-Wl,-z,relro,-z,now` | `-l`: `GNU_RELRO`, `-d`: `BIND_NOW` |
| FORTIFY | `-O2 -D_FORTIFY_SOURCE=3` | `--dyn-syms`: `*_chk` |
| CET | `-fcf-protection=full` | `-n`: `IBT, SHSTK` |
| PAC/BTI | `-mbranch-protection=standard` | `paciasp`, `autiasp` |
| CFI (Clang) | `-flto -fvisibility=hidden -fsanitize=cfi` | ajonaikainen |

| Laukeaa | Viesti |
|---------|--------|
| pinokanari | `*** stack smashing detected ***` |
| FORTIFY | `*** buffer overflow detected ***` |
| FORTIFY ja `%n` | `*** %n in writable segment detected ***` |
| glibc tcache | `free(): double free detected in tcache 2` |
| NX | SIGSEGV hypyssä dataan |

# Kaatumisen luokittelu

| Kohta | Arvio |
|-------|-------|
| `ret`, paluuosoitteessa syötettä | ohjausvuo syötteen vallassa |
| kirjoitus varauksen yli | todennäköisesti koodin suoritus |
| käyttö vapautuksen jälkeen | todennäköisesti koodin suoritus |
| rajaton luku | tietovuoto, voi kumota ASLR:n |
| nollaosoitin | yleensä palvelunesto |

# Fuzzaus

```{.c tiedosto="esimerkit/08-fuzzaus/fuzz_tlv.c" osa="kohde"}
```

| Komento | Tarkoitus |
|---------|-----------|
| `clang -fsanitize=fuzzer,address,undefined` | libFuzzer-kohde |
| `./fuzz korpus/ -max_len=N -runs=N -seed=S` | ajo, korpus kasvaa |
| `./fuzz -minimize_crash=1 -runs=N loydos` | minimointi |
| `./fuzz tiedosto...` | regressiotesti ilman fuzzausta |
| `-dict=sanat.txt` | rakenteiset syötteet |
| `afl-clang-fast -fsanitize=fuzzer` | sama kohde AFL++:lle |
| `afl-fuzz -i korpus -o tulos -- ./kohde` | AFL++-ajo |

# Juurisyystä ilmoitukseen

1. Toista minimoidulla syötteellä kaikilla sanitoijilla.
2. Kaatumiskohdasta juurisyyhyn: mikä arvo väärä, mistä se tuli, mikä
   oletus petti.
3. Arvioi primitiivi, syötteen hallinta, suojaukset ja oikeudet.
4. Korjaa juurisyy, lisää regressiotesti, etsi variaatiot.
5. CWE-luokka ja CVSS-vektori; ilmoitus valmistajalle
   (`security.txt`), 90 päivän lähtökohta.

| CWE | Virhe |
|-----|-------|
| 787 / 125 | kirjoitus / luku puskurin ulkopuolelle |
| 416 / 415 | käyttö vapautuksen jälkeen / kaksoisvapautus |
| 190 | kokonaisluvun ylivuoto |
| 134 | hallitsematon muotoilumerkkijono |

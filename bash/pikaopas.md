---
title: Bash-skriptaus
subtitle: Pikaopas kokeneelle kehittäjälle · Bash 5.2 · ShellCheck, bats
---

# Skriptipohja

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="pohja"}
```

- Logiikka funktioihin, viimeinen rivi `main "$@"`; testattava
  versio `[[ ${BASH_SOURCE[0]} == "$0" ]] && main "$@"`.
- Shebang `#!/usr/bin/env bash`; `#!/bin/sh` on Debianissa dash.
- Paluuarvot: 0 ok, 1 virhe, 2 käyttövirhe, 126 ei suoritettava,
  127 ei löydy, 128+n signaali (130 INT, 141 PIPE, 143 TERM).

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Staattinen analyysi | `shellcheck -x main.sh lib/*.sh` |
| Vaiennus (perustele!) | `# shellcheck disable=SC2086` |
| Muotoilu | `shfmt -d -i 4 -ci *.sh`, `-w` kirjoittaa |
| Syntaksi | `bash -n x.sh` |
| Jäljitys | `bash -x x.sh`, `PS4='+ ${FUNCNAME[0]:-main}:${LINENO}: '` |
| Jälki tiedostoon | `exec {fd}> jalki; BASH_XTRACEFD=$fd; set -x` |
| Ajoitus | `time x.sh`, `PS4='+ $EPOCHREALTIME '` |
| Testit | `bats testit/`, `bats --formatter tap x.bats` |
| Ohje | `help read`, `man bash` (`/^ *Parameter Expansion`) |

# Lainaus

- Lainaa jokainen laajennus: `"$x"`, `"$(k)"`, `"${a[@]}"`.
  Lainaamaton jaetaan `IFS`:stä ja globataan.
- `'…'` kirjaimellinen, `"…"` laajentaa `$`, `` ` `` ja `\`,
  `$'\t\n'` ANSI-C.
- `--` ennen operandeja: `rm -- "$f"`, `grep -- "$k" "$f"`.
- `printf '%s\n' "$x"` datalle; `%q` uudelleensyötettävä muoto.

# Laajennukset

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="laajennukset"}
```

| Muoto | Merkitys |
|-------|----------|
| `${x:-o}` `${x:=o}` | oletus; oletus ja sijoitus |
| `${x:?viesti}` | virhe, jos tyhjä tai asettamaton |
| `${x:+a}` | `a`, jos `x` ei tyhjä |
| `${x@Q}` | lainattu muoto (4.4) |
| `$(( a * b / 100 ))` | 64-bittinen kokonaislukuaritmetiikka |
| `$(( 10#$kk ))` | etunolla ei tee oktaalilukua |

# Ehdot ja silmukat

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="ehdot"}
```

- Testit: `-f -d -e -s -r -w -x`, `-n -z`, `-v nimi`, `a -nt b`.
- `=~`:n oikea puoli lainaamatta; osumat `BASH_REMATCH`.
- `while IFS= read -r rivi || [[ -n $rivi ]]; do …; done < t`
- `while IFS= read -r -d '' f; do …; done < <(find . -print0)`
- `shopt -s nullglob`; `for f in ./*.log`; ei `$(ls)`.
- `case $x in a|b) … ;; *) … ;; esac`

# Funktiot

- Tulos tulosteena `x=$(f)`, onnistuminen `return 1`,
  taulukko `local -n viite=$1`.
- `local x; x=$(k)`, ei `local x=$(k)` (peittää paluuarvon).
- `if x=$(f "$a"); then …` tarkistaa ja kaappaa kerralla.
- Predikaatti: viimeisen komennon paluuarvo on funktion paluuarvo.

# Taulukot

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="taulukot"}
```

- `mapfile -t a < t` rivit taulukkoon; ei `a=($(cat t))`.
- Komento taulukkona: `k=(rsync -a); k+=(--dry-run); "${k[@]}"`.
- `local IFS=,; echo "${a[*]}"` yhdistää erottimella.
- `unset 'a[i]'` jättää aukon; `a=("${a[@]}")` tiivistää.

# Virheet ja siivous

| Asetus | Vaikutus |
|--------|----------|
| `set -e` | lopettaa epäonnistuneeseen komentoon |
| `set -u` | asettamaton muuttuja on virhe |
| `set -o pipefail` | putki epäonnistuu, jos mikä tahansa osa |
| `set -E` | ERR-ansa periytyy funktioihin |
| `shopt -s inherit_errexit` | `$(…)` perii `-e`:n (4.4) |

- `set -e` ei toimi `if`/`while`-ehdossa, `&&`/`||`-listassa, `!`:n
  jälkeen eikä **funktioissa, joita kutsutaan niistä**.
- `trap siivoa EXIT` heti resurssin jälkeen; `trap '…' ERR` riville
  ja komennolle (`$LINENO`, `$BASH_COMMAND`).
- `PIPESTATUS` heti putken jälkeen: `a | b || t=("${PIPESTATUS[@]}")`.
- `pipefail` + `head` → SIGPIPE (141) alkupäässä.

# Syöte ja tiedostot

| Merkintä | Merkitys |
|----------|----------|
| `> t 2>&1`, `&> t` | molemmat virrat tiedostoon |
| `>&2` | viesti virhetulosteeseen |
| `<<< "$x"` | here-merkkijono |
| `<<'LOPPU'` | here-dokumentti ilman laajennuksia |
| `< <(k)` | prosessikorvaus: silmukka ilman alikuorta |
| `exec {fd}> t` | vapaa tiedostokuvaaja muuttujaan |

- Atominen päivitys: `t=$(mktemp "$kohde.XXXXXX")`, kirjoitus,
  `mv -f -- "$t" "$kohde"`.
- awk riveille: `awk -v raja="$r" '$3 > raja { n[$1]++ } END {…}'`.

# Argumentit ja kirjastot

- `while getopts ':k:nh' o; do case $o in k) …="$OPTARG";; :|?) …;;
  esac; done; shift $((OPTIND - 1))`
- Pitkät: `while (( $# )); do case $1 in --x=*) …="${1#*=}";;
  --x) …="$2"; shift;; --) shift; break;; esac; shift; done`
- `source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/lib.sh"`
  ja `# shellcheck source-path=SCRIPTDIR`.
- Kirjasto: latausvartija, etuliitteelliset nimet, ei `set`/`trap`.
- Asetustiedosto jäsennetään, ei `source`:ta.

# Prosessit ja rinnakkaisuus

- `( … )`, `$(…)`, putken osat ja `&` ovat alikuoria: muuttujat eivät
  palaa.
- Rajoitus: `(( ${#t[@]} < N )) || { wait -n -p pid || …; }` (5.1).
- `find … -print0 | xargs -0 -P 4 -n 1 komento`; funktio:
  `export -f f; xargs -0 -I {} bash -c 'f "$1"' _ {}`.
- `exec {fd}> lukko; flock -n "$fd" || exit 1` estää päällekkäiset
  ajot.
- `trap 'lopeta=1' TERM`; konttiskriptin lopussa `exec palvelu`.
- `timeout 30 curl …` → 124, kun aika loppui.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| sisäänrakennetut: `printf`, `read`, `[[ ]]`, `(( ))` | ulkoinen komento: `fork` + `exec`, ~1 ms |
| parametrilaajennus `${x##*/}` | `$(basename "$x")` silmukassa |
| yksi `awk`/`sed` koko tiedostolle | ulkoinen komento joka riville |
| `printf -v x`, nimiviittaus | `$(f)`: alikuori joka kutsulla |
| assosiatiivinen taulukko (hajautus) | suuri tavallinen taulukko hajasaannilla |

# Vaihda kieltä, kun

yli ~200 riviä omaa logiikkaa · sisäkkäiset rakenteet · liukuluvut ·
JSON/YAML/lainattu CSV · eri virheille eri käsittely · Windows.

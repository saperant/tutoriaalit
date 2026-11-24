---
title: EDA-työkaluketjujen automatisointi
subtitle: Pikaopas · vuo, eräajot, Tcl, raportit, regressiot, rekisterit ja CI
---

# Vuo

| Käsite | Sisältö |
|-------------|-----------------------------------------------|
| vaihe | komento, syötteet, tulosteet, riippuvuudet, ympäristö |
| leima | tiiviste: komento + ympäristö + työkaluversio + syötteiden sisältö |
| ajan tasalla | sama leima ja tulosteet olemassa |
| ohitettu | riippuvuus epäonnistui tai ohitettiin |
| varhainen katkaisu | vaihe ajettiin, tulos ei muuttunut: seuraavat eivät vanhene |
| taso | vaiheet, joiden riippuvuudet on käsitelty: rinnakkain |
| ajohakemisto | kaikki tulosteet, lokit, leimat ja manifesti |

- `graphlib.TopologicalSorter`: `prepare()` (kehä → `CycleError`),
  `get_ready()`, `done()`.
- Make ei näe parametreja: kirjoita ne tiedostoon, joka muuttuu vain
  sisällön muuttuessa, ja lisää se riippuvuuksiin.
- Ulomman Maken `MAKEFLAGS`, `MFLAGS` ja `MAKELEVEL` pois työkalun
  omasta ympäristöstä.

# Eräajo

| Työkalu | Komento |
|--------------|----------------------------------------------|
| Verilator, lint | `verilator --lint-only -Wall [-GLEVEYS=8] x.sv` |
| Verilator, simulointi | `verilator --binary -Wall --top-module tb -Mdir obj -o sim ...` |
| Icarus | `iverilog -g2012 -s tb -o sim.vvp ...` ja `vvp -n sim.vvp +siemen=3` |
| Yosys, komennot | `yosys -q -p "read_verilog -sv x.sv; synth -top x"` |
| Yosys, Tcl | `yosys -q -c skripti.tcl` (parametrit `$::env(...)`) |
| Tcl-tulkki | `tclsh8.6` (Debian), muualla `tclsh` |
| kaupallinen malli | `tyokalu -mode batch -source kulku.tcl -log kulku.log` |

- Komento listana, ei kuorta. `stderr` samaan lokiin. Komento lokin
  ensimmäiselle riville. Aikaraja jokaiseen ajoon.
- Simulaattori palauttaa 0 myös hylätystä testistä: tulos
  testipenkin tulosriviltä, puuttuva tulosrivi on virhe.
- Versio: `verilator --version`, `yosys -V`, Tcl `info patchlevel`.

# Yosys Tcl-tilassa

| Komento | Tarkoitus |
|---------|-----------|
| `yosys -import` | Yosysin komennot Tcl-komennoiksi |
| `design -reset` | tyhjä tietokanta kierrosten välillä |
| `chparam -set LEVEYS 16 laskuri` | parametrin arvo |
| `tee -q -o f.json stat -json` | tuloste tiedostoon, ei lokiin |
| `tee -q -o f.txt ltp -noff` | pisin polku, `(length=N)` |
| `write_blif -impltf f.blif` | netlista toiselle työkalulle |
| `catch {read_verilog ...}` | Yosysin virhe on Tcl-virhe |

- Komennot eivät palauta arvoja Tcl:lle (0.33): tulokset tiedostoista.
- Kaupallisissa työkaluissa komennot palauttavat kokoelmia:
  `foreach_in_collection`, `get_cells -filter`.

# Jäsentäminen

| Raportti | Tapa |
|-------------|-----------------------------------------------|
| Yosys `stat -json` | `json.loads`, `modules`, `num_cells_by_type` |
| `ltp` | `\(length=(\d+)\)` |
| STA | kenttä kerrallaan; tarkista slack = vaadittu − saapuminen |
| Verilator | `^%Warning-KOODI: tiedosto:rivi:sarake: viesti`, jatkorivit sisennetty |
| Icarus | `^tiedosto:rivi: laji: viesti`, laji `sorry`, `warning` tai `error` |
| simulointi | `^TESTI OK`, `^TESTI EPÄONNISTUI n`, aikakatkaisu, muuten virhe |

- Yksi jäsennin raporttityyppiä kohden, yksi tietomalli kaikille.
- Hylkää, älä arvaa. Polut suhteellisiksi projektin juureen.
- Näyteraportit versionhallintaan, pytest jäsentimille.

# Varoitukset

| Luokka | Laatuportti |
|--------|-------------|
| uusi | hylkää |
| sallittu, voimassa | läpi |
| sallittu, vanhentunut | hylkää |
| tarpeeton sallinta | raportoi, poista listalta |

- Sallinta: koodi, tiedosto, viestin lauseke, peruste, voimassa-päivä.
- Tunnista viestistä, ei rivinumerosta.
- Koodiin `/* verilator lint_off KOODI */` vain rakenteellisesti
  pysyvät tapaukset.

# Regressio

- Testilista TOMLina: nimi, siemenet, makrot, plusargit, aikaraja.
- Käännös kerran makroyhdistelmää kohden, ajot säiepoolissa,
  tulokset järjestettynä (testi, siemen).
- Allekirjoitus: data-arvot `<n>`, tunnisteet (operaatio, lohko)
  säilytetään.
- Oma satunnaislukugeneraattori: tulos riippuu vain siemenestä.

# Historia (SQLite)

```text
-- trendi: viimeisin ajo versiosta
SELECT versio, SUM(tila = 'ok'), COUNT(*) ... GROUP BY versio
-- ensimmäinen hylkäävä versio
ROW_NUMBER() OVER (PARTITION BY allekirjoitus ORDER BY jarjestys)
-- epävakaat: sama versio, testi ja siemen, eri tulos
GROUP BY versio, testi, siemen HAVING COUNT(DISTINCT tila = 'ok') = 2
```

- `git bisect run`: 0 = hyvä, 1–127 (paitsi 125) = huono, 125 = ohita.

# Rekisterit

| Pääsy | RTL | Testi |
|--------|----------------------|-------------------------------|
| `rw` | lähtö, kirjoitus väylältä | nollaus, kirjoitus ja luku |
| `ro` | tulo, vain luku | kuvio `0101...` luetaan, kirjoitus ei vaikuta |
| `w1c` | laitteisto asettaa, 1 nollaa | asetus, luku, nollaus |

- Tarkistus ennen tuottamista: päällekkäisyys maskeilla, leveys,
  tasaus, kaksoisosoite, nollausarvon leveys, nimet.
- CI: `tuota()` muistiin ja vertaa tallennettuihin.

# CI

| Asia | Ratkaisu |
|------------|------------------------------------------------|
| työkalut | konttikuva tai jaettu asennus, versio tunnisteessa |
| lisenssi | `LM_LICENSE_FILE=portti@palvelin` salaisuudesta, rinnakkaisuus rajattu |
| välivaiheet | ajohakemisto artefaktina, leimat mukana |
| välimuisti | avain: kuvan versio + `hashFiles(lähteet)` |
| artefaktit | `if: always()`, myös hylätyistä ajoista |
| tuotetut tiedostot | tuota uudelleen ja vertaa, ero kaataa |

- YAML 1.1: `on` on totuusarvo yleisissä kirjastoissa.
- Sama komento CI:ssä ja paikallisesti: `python3 aja_vuo.py kohde`.

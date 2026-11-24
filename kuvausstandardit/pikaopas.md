---
title: Laitteiston kuvausstandardit
subtitle: Pikaopas · SystemRDL, PeakRDL, IP-XACT, SVD, laitepuu, SDC ja UPF
---

# SystemRDL

| Komponentti | Merkitys |
|-------------|----------------------------------|
| `addrmap` | osoitekartta: lohko tai piiri |
| `regfile` | rekisteriryhmä, usein taulukkona |
| `reg` | rekisteri (`regwidth`) |
| `field` | kenttä: `NIMI[ylin:alin] = nollaus` |
| `mem`, `signal` | muistialue, ulkoinen signaali |

```{.systemverilog tiedosto="esimerkit/rdl/ajastin.rdl" osa="ajastin"}
```

- `@ osoite`, taulukko `X[N] @ alku += askel`.
- `default sw = rw; default hw = r;` oletukset näkyvyysalueelle.
- Dynaaminen sijoitus `REK.KENTTA->enable = CTRL.IE;`.
- Parametri `addrmap dma #(longint unsigned N = 4)`,
  instanssissa `dma #(.N(2)) DMA0`.
- Oma ominaisuus: `property nimi { type = ...; component = ...; };`

# Pääsy ja käyttäytyminen

| Kuvaus | UVM | SVD / IP-XACT |
|----------------------------|------|-------------------------------|
| `sw = rw` | RW | read-write |
| `sw = r` | RO | read-only |
| `sw = w` | WO | write-only |
| `onwrite = woclr` | W1C | modifiedWriteValues oneToClear |
| `onwrite = woset` | W1S | oneToSet |
| `onread = rclr` | RC | readAction clear |

| Laitteisto | Syntyy |
|-------------------|------------------------------------|
| `hw = w` | tulo `next`, ei tallennusta |
| `hwset`, `hwclr` | tulo, joka asettaa tai nollaa |
| `counter` | tulo `incr`; `incrsaturate` pysähtyy |
| `singlepulse` | yhden jakson pulssi lähtöön |
| `swmod`, `swacc` | ilmoitus kirjoituksesta, luvusta |
| `intr` | rekisterin `intr`-lähtö; `enable`, `mask` |
| `precedence` | samanaikaisessa kirjoituksessa voittaja (oletus `sw`) |

# PeakRDL

| Komento | Tuote |
|-------------------------------|------------------------------|
| `peakrdl regblock X.rdl -o d --cpuif apb4-flat` | SV-lohko ja paketti |
| `peakrdl c-header X.rdl -o x.h` | C-otsake (`_bm _bp _bw _reset`) |
| `peakrdl uvm X.rdl -o x_uvm.sv` | UVM-rekisterimalli |
| `peakrdl ip-xact X.rdl -o x.xml` | IP-XACT 2014 (`--standard 2009`) |
| `peakrdl html X.rdl -o kansio` | HTML-sivusto |
| `peakrdl dump X.rdl` | osoitteet tekstinä |

- `--type-style hier`: vakaat nimet ilman tiivisteitä.
- `--err-if-bad-rw`, `--err-if-bad-addr`: virhevastaukset väylälle.
- `--hwif-report`: laitteiston signaaliluettelo.
- `-I hakemisto`, `-P NIMI=arvo`, `-t ylin`.
- `c-header --testcase`: siirtymien testiohjelma.

# Python-rajapinta

```{.python tiedosto="esimerkit/kuvaus/kaanna.py" osa="kaanna"}
```

- `ylin.descendants(unroll=True)`, `reg.fields()`.
- `solmu.get_property("sw")`, `absolute_address`, `get_rel_path(ylin)`.
- `orig_type_name`: tyyppi ennen parametreja.

# IP-XACT, SVD ja laitepuu

| Muoto | Ydin |
|-----------|----------------------------------------------|
| IP-XACT | VLNV; `component`: `model`, `busInterfaces`, `memoryMaps`, `fileSets` |
| SVD | `device` → `peripheral` (`derivedFrom`) → `register` / `cluster` (`dim`) → `field` |
| laitepuu | `compatible`, `reg = <osoite koko>`, `interrupts` |

- IP-XACT ja SVD eivät kanna käyttäytymistä (`hwset`, `counter`,
  `intr`): SystemRDL lähteeksi.
- Tarkistus: `xmllint --noout`, `dtc -I dts -O dtb`.

# Muut kuvaukset

| Muoto | Kuvaa |
|-------------|---------------------------------------|
| SDC | kellot, viiveet, poikkeukset (Tcl) |
| UPF | tehoalueet, kytkimet, eristys (Tcl) |
| Liberty | solujen ajoitus ja teho |
| LEF / DEF | fyysiset muodot / sijoiteltu piiri |
| SPEF | parasiitit |
| VCD / FST | aaltomuodot |

# CI

- Yksi `tuota()` kirjoittaa ja tarkistaa.
- Tallennetut tuotteet verrataan tuoreisiin ennen simulointia.
- Generaattorien versiot lukittuina; päivitys omana muutoksenaan.
- Versiorekisteri, varatut bitit nollina, pääversio
  yhteensopimattomille muutoksille.

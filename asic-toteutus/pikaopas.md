---
title: ASIC-toteutus
subtitle: Pikaopas · vuo, Liberty, synteesi, STA, SDC, DFT ja fyysinen toteutus
---

# Vuo

| Vaihe | Tulos | Tarkistus |
|-------|-------|-----------|
| RTL | Verilog | simulointi, lint |
| Synteesi | netlista | ekvivalenssi, STA |
| DFT | scan, BIST | vikakattavuus |
| Pohjapiirros | ydin, IO, teho | IR-arvio |
| Sijoittelu | paikat | ruuhka, STA |
| CTS | kellopuu | vinous, STA |
| Reititys | metallit | DRC, STA |
| Sign-off | GDSII | DRC, LVS, STA, IR, EM |

# Yosys

```text
read_verilog -sv rtl.v
synth -top ylin -flatten
dfflibmap -liberty kirjasto.lib
abc -liberty kirjasto.lib
opt_clean -purge
stat -liberty kirjasto.lib
write_verilog -noattr netlista.v
```

- ABC:n oletusskripti optimoi pinta-alaa; rakenne säilyy skriptillä
  `abc -liberty kirjasto.lib -script +strash;map`.
- Ekvivalenssi: `miter -equiv -flatten kultainen portti miter;`
  `sat -prove trigger 0 -show-inputs miter`.

# Liberty

| Ryhmä/attribuutti | Merkitys |
|-------------------|----------|
| `cell (X) { area }` | solu ja pinta-ala µm² |
| `pin { capacitance }` | tulon kuorma pF |
| `function : "!(A&B)"` | logiikka synteesille |
| `timing { related_pin }` | ajoituskaari tulosta lähtöön |
| `cell_rise/fall` | viive (slew × kuorma) |
| `rise/fall_transition` | lähdön siirtymäaika |
| `setup/hold_rising` | kiikun rajoitteet |
| `ff { next_state }` | kiikku |

- Taulukot: rivit tulon siirtymäaika, sarakkeet lähdön kuorma.
  Väliarvot interpoloidaan bilineaarisesti; taulukon ulkopuolella
  ekstrapoloitu arvo on epätarkka (`max_capacitance`, `max_transition`).

# STA

$$t_{saap,max} \leq T + t_{kello,v} - t_{asetus} - t_{\text{epävarmuus}}$$

$$t_{saap,min} \geq t_{kello,v} + t_{pito} + t_{\text{epävarmuus}}$$

- Marginaali = vaadittu − saapuminen (asetus); saapuminen − vaadittu
  (pito). Negatiivinen = rike.
- Asetus: hidas kulma, myöhäiset polut hidastettuna (OCV).
- Pito: nopea kulma, aikaiset polut nopeutettuna. Korjaus: viive
  datapolulle CTS:n jälkeen.
- Vinous $+\Delta$ vastaanottajalla: asetus $+\Delta$, pito $-\Delta$.

# SDC

```{.text tiedosto="esimerkit/kertoja2.sdc" osa="perus"}
```

```{.text tiedosto="esimerkit/kertoja2_mc.sdc" osa="monisykli"}
```

# DFT

| Menetelmä | Mitä |
|-----------|------|
| Juuttumisvika | johdin pysyvästi 0/1 |
| Viivevika | siirtymä liian hidas (kaksi vektoria) |
| Scan | SE=1: siirto, SE=0: kaappaus |
| ATPG | vektorit algoritmisesti, tiivistys |
| BIST | LFSR-vektorit, MISR-allekirjoitus |
| JTAG | TAP, boundary scan, debug |

# Fyysinen toteutus

| Käsite | Muistisääntö |
|--------|--------------|
| Käyttöaste | 60–80 % solujen ala / ydin |
| HPWL | rajaavan suorakulmion puolikas piiri |
| Elmore | $\sum R_e \cdot C_{alavirta}$ |
| Kellopuu | pieni vinous, puskurit haaroihin |
| Reititys | globaali → yksityiskohtainen, rip-up |
| IR-pudotus | alle ~5 % syötöstä |
| Antenni | metalli/hila-ala ≤ raja, diodi tai hyppy |

# Teho

- $P_{dyn} = \alpha C V^2 f$, vuoto kirjastosta (`cell_leakage_power`).
- Kello 30–50 % dynaamisesta tehosta: portitus ICG:llä, ei JA-portilla.
- Tehoalueet UPF:llä: kytkin, eristys, tasonsiirrin, säilytys.

# Valmistus

- Saanto: Poisson $e^{-AD}$, Murphy $\left(\frac{1-e^{-AD}}{AD}\right)^2$.
- Maapomppu $L \cdot di/dt$: lankabondaus ~2 nH, flip-chip ~0,1 nH.
- Nastarajoitteinen: IO-rengas vaatii enemmän tilaa kuin ydin.

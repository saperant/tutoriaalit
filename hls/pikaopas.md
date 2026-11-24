---
title: Korkean tason synteesi
subtitle: Pikaopas · ajoitus, liukuhihnat, muistit ja rajapinnat
---

# Työnkulku

| Vaihe | Todentaa | minihls-vuossa |
|----------------------|--------------------------|----------------------------|
| C-simulaatio | algoritmin | `g++ -fsanitize=...` + `testi.cpp` |
| synteesi | latenssi, II, resurssit | `python3 -m minihls ydin.cpp --top f` |
| C/RTL-yhteissimulaatio | RTL = C samoilla vektoreilla | Verilator + tuotettu `tb.sv` |
| toteutus | kellotaajuus | Yosys, nextpnr |

| minihls-valitsin | Tulostaa |
|----------------------|------------------------------|
| `--dfg [alue]` | tietovuograafin |
| `--asap [alue]` | ASAP, ALAP ja liikkuvuuden |
| `--ajoitus [alue]` | operaatioiden jaksot ja valmistumisajat |
| `--kello ns` | kellojakso (oletus 10 ns) |
| `--ulos hak` | RTL:n ja testipenkin hakemistoon |
| `--paine` | satunnaisen vastapaineen testipenkkiin |

# Kaavat

| Suure | Kaava |
|------------------------------|------------------------------------|
| silmukka ilman liukuhihnaa | *N · L* |
| liukuhihnoitettu silmukka | *(N − 1) · II + L* |
| läpäisy | *1 / II* kierrosta jaksossa |
| ResMII | $\lceil \text{käytöt} / \text{yksiköt} \rceil$ resurssia kohti |
| RecMII | $\lceil \text{viive} / \text{etäisyys} \rceil$ |
| avaus kertoimella *F* | *N / F* kierrosta, *F* kopiota rungosta |

*N* on kierrosmäärä ja *L* kierroksen pituus jaksoina.

# Pragmat

```{.cpp tiedosto="esimerkit/06-liukuhihna/mac_putki.cpp" osa="pragma"}
```

```{.cpp tiedosto="esimerkit/05-avaus/mac_2.cpp" osa="pragma"}
```

```{.cpp tiedosto="esimerkit/07-matriisi/matmul_jaettu.cpp" osa="jako"}
```

```{.cpp tiedosto="esimerkit/04-jakaminen/diffeq_1.cpp" osa="pragma"}
```

```{.cpp tiedosto="esimerkit/08-histogrammi/hist_vaara.cpp" osa="pragma"}
```

| Pragma | Vaikutus | Hinta |
|----------------------------------|------------------------------|------------------------------|
| `pipeline II=k` | kierrokset limittyvät, sisäsilmukat avataan | rekisterit, ohjaus |
| `unroll [factor=F]` | runko *F* kertaa tai kokonaan | yksiköt, muistiportit |
| `array_partition type=cyclic` | alkio *i* pankkiin *i mod F* | muistit, portit |
| `array_partition type=block` | peräkkäiset lohkot pankkeihin | muistit, portit |
| `array_partition type=complete` | alkiot rekistereiksi | rekisterit, multiplekserit |
| `allocation instances=mul limit=k` | enintään *k* kertojaa | latenssi, multiplekserit |
| `dependence ... dependent=false` | riippuvuus ohitetaan | väärä tulos, jos riippuvuus on |
| `interface mode=...` | portin protokolla | – |

# II:n esteet

| Raportin syy | Korjaus |
|------------------------------|------------------------------------|
| `a: lukuportti, n käyttöä` | jaa `a` *n* pankkiin |
| `muuttuja s` | lyhennä takaisinkytkentää, useampi akku |
| `taulukko h (tallenna -> lataa)` | osahistogrammit, välitys |
| `mul, n käyttöä` | lisää kertojia tai hyväksy II |
| `virta x` | yksi luku tai kirjoitus kierroksessa |

# Rajapinnat

| Parametri | Protokolla | Portit |
|----------------------|------------------|----------------------------------|
| funktio | `ap_ctrl_hs` | `ap_start`, `ap_done`, `ap_idle`, `ap_ready` |
| `int k` | `ap_none` | `k`, vakaa koko ajon |
| `int a[N]` | `ap_memory` | `a_address0`, `a_ce0`, `a_q0`; `a_address1`, `a_we1`, `a_d1` |
| `virta<int>& x` | `axis` | `x_TDATA`, `x_TVALID`, `x_TREADY` |
| paluuarvo | `ap_return` | voimassa, kun `ap_done` |
| (Vitis) skalaarit prosessorilta | `s_axilite` | rekisterikartta, ohjaus osoitteessa 0 |
| (Vitis) DRAM | `m_axi` | AXI4-pursket |

AXI-Stream: siirto, kun `TVALID` ja `TREADY` ovat 1; `TVALID` ei saa
odottaa `TREADY`:tä; data pysyy, kunnes siirto tapahtuu.

# Synteesikelpoinen C++

| Vältä | Käytä |
|------------------------------|------------------------------|
| `new`, `malloc`, `std::vector` | kiinteän kokoinen taulukko |
| rekursio | silmukka |
| osoitinaritmetiikka | indeksi |
| datasta riippuva kierrosmäärä | vakioraja ja ehto |
| `/`, `%` muuttujalla | siirto, kertolasku käänteisluvulla |
| `float`, `double` | `ap_fixed`, `ac_fixed` |
| `printf` ytimessä | testipenkissä |

# Verifiointi

- Viitemalli eri tavalla kirjoitettuna kuin ydin.
- Sanitoijat: `-fsanitize=address,undefined -fno-sanitize-recover=all`.
- Yhteissimulaatio jokaisen pragman jälkeen; väärä `dependence`
  läpäisee C-simulaation.
- Toistuvat arvot, ääriarvot ja satunnainen vastapaine testivektoreihin.
- Latenssi simulaatiosta, vertaa raporttiin.

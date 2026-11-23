<!-- Tämä tiedosto on generoitu tiedostosta taitopuu.toml
     komennolla `make readme`. Älä muokkaa käsin. -->

# Opintopolut

Tutoriaalit muodostavat taitopuun: jokainen tutoriaali on yksi taito, ja taidot rakentuvat toistensa päälle. Roolit ovat ammattiprofiileja, joiden polku kulkee puun läpi.

Taitoja on 72, yhteensä noin 317 op. Valmis PDF: [opintopolut.pdf](opintopolut.pdf). Taitopuun lähdetiedosto: [taitopuu.toml](taitopuu.toml).

## Roolit

| Rooli | Tavoitteet | Taitoja | op |
|-------|------------|--------:|---:|
| Laitteistoarkkitehti | Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen, EDA-työkaluketjujen automatisointi, FPGA-toteutus, Laitteiston verifiointi | 25 | 105 |
| Sulautettujen ohjelmistojen kehittäjä | Linux-laiteajurit, Reaaliaikakäyttöjärjestelmät | 17 | 72 |
| Signaalinkäsittelyn ja ohjelmistoradion kehittäjä | Ohjelmistoradio | 13 | 61 |
| Grafiikkaohjelmoija | GPU-laskenta, Säteenseuranta ja fysikaalinen valaistus | 19 | 87 |
| Hajautettujen järjestelmien kehittäjä | Skaalautuvien järjestelmien suunnittelu, Säiliöt ja pilvi-infrastruktuuri | 18 | 86 |
| Takaisinmallintaja ja tietoturva-analyytikko | Haavoittuvuuksien analyysi ja hyödyntäminen, Laiteohjelmiston takaisinmallinnus | 15 | 69 |
| Algoritmiikan ja ohjelmistokehityksen perusta | Edistyneet algoritmit ja tietorakenteet, Käännösjärjestelmät, testaus ja CI | 10 | 41 |
| Web-kehittäjä | Web-sovellukset | 7 | 29 |
| Taustajärjestelmäkehittäjä | Säiliöt ja pilvi-infrastruktuuri, Taustapalvelut | 7 | 31 |
| Mobiilikehittäjä (Android) | Android-sovellukset | 4 | 18 |

## Taitopuu

Valmiit tutoriaalit on merkitty merkillä ✓.

```mermaid
flowchart LR
  subgraph perusta["Perusta"]
    ohjelmoinnin_perusteet["✓ Ohjelmoinnin perusteet (Python)"]
    komentorivi["✓ Komentorivi ja Linux"]
    versionhallinta["Versionhallinta (Git)"]
    c_kieli["✓ C-kieli"]
    moderni_cpp["✓ Moderni C++"]
    python["✓ Python"]
    bash["✓ Bash-skriptaus"]
    python_tyokalut["Python työkaluohjelmointiin"]
    rakennus_ja_testaus["Käännösjärjestelmät, testaus ja CI"]
  end
  subgraph matematiikka["Matematiikka"]
    diskreetti_matematiikka["Diskreetti matematiikka"]
    lineaarialgebra["Lineaarialgebra"]
    signaalimatematiikka["Kompleksiluvut ja Fourier-analyysi"]
    todennakoisyys["Todennäköisyys ja tilastot"]
  end
  subgraph algoritmit["Algoritmit ja tietorakenteet"]
    tietorakenteet["Tietorakenteet"]
    algoritmit["Algoritmit"]
    edistyneet_algoritmit["Edistyneet algoritmit ja tietorakenteet"]
    kaantajatekniikka["Kääntäjätekniikka"]
  end
  subgraph jarjestelmat["Tietokonejärjestelmät"]
    digitaalitekniikka["Digitaalitekniikka"]
    assembly["Assembly"]
    tietokonearkkitehtuuri["Tietokonearkkitehtuuri"]
    binaarit_ja_linkitys["Objektitiedostot, linkitys ja ABI"]
    kayttojarjestelmat["Käyttöjärjestelmät"]
    rinnakkaisohjelmointi["Rinnakkaisohjelmointi"]
    suorituskyky["Suorituskyvyn analyysi ja optimointi"]
  end
  subgraph laitteisto["Laitteistosuunnittelu"]
    kiintea_pilkku["Lukujen esitys ja kiinteän pilkun aritmetiikka"]
    rtl_suunnittelu["✓ RTL-suunnittelu SystemVerilogilla"]
    vhdl["RTL-suunnittelu VHDL:llä"]
    verifiointi["Laitteiston verifiointi"]
    fpga_toteutus["FPGA-toteutus"]
    hlm_mallinnus["Korkean tason mallinnus (SystemC/TLM)"]
    arkkitehtuurin_tutkiminen["Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen"]
    eda_skriptaus["EDA-työkaluketjujen automatisointi"]
    hls["Korkean tason synteesi"]
    dsp_laitteisto["DSP-algoritmien laitteistototeutus"]
  end
  subgraph signaalit["Signaalinkäsittely ja radiot"]
    signaalit_ja_jarjestelmat["Signaalit ja järjestelmät"]
    dsp["Digitaalinen signaalinkäsittely"]
    tiedonsiirto["Digitaalinen tiedonsiirto"]
    sdr["Ohjelmistoradio"]
  end
  subgraph sulautetut["Sulautetut järjestelmät"]
    mikrokontrollerit["Mikrokontrollerit ja bare-metal-ohjelmointi"]
    oheislaitevaylat["Oheislaiteväylät"]
    rtos["Reaaliaikakäyttöjärjestelmät"]
    embedded_linux["Sulautettu Linux"]
    linux_ajurit["Linux-laiteajurit"]
  end
  subgraph hajautetut["Verkot ja hajautetut järjestelmät"]
    tietoverkot["Tietoverkot"]
    verkko_ohjelmointi["Verkko-ohjelmointi"]
    hajautetut_jarjestelmat["Hajautetut järjestelmät"]
    jarjestelmasuunnittelu["Skaalautuvien järjestelmien suunnittelu"]
    kontit_ja_pilvi["Säiliöt ja pilvi-infrastruktuuri"]
  end
  subgraph grafiikka["Tietokonegrafiikka"]
    renderoinnin_perusteet["Renderöinnin perusteet"]
    sateenseuranta["Säteenseuranta ja fysikaalinen valaistus"]
    gpu_ohjelmointi["GPU-ohjelmointi ja grafiikkarajapinnat"]
    gpu_laskenta["GPU-laskenta"]
  end
  subgraph tietoturva["Tietoturva ja takaisinmallinnus"]
    tietoturvan_perusteet["Tietoturvan perusteet"]
    takaisinmallinnus["Takaisinmallinnus"]
    haavoittuvuudet["Haavoittuvuuksien analyysi ja hyödyntäminen"]
    laiteohjelmiston_takaisinmallinnus["Laiteohjelmiston takaisinmallinnus"]
  end
  subgraph kielet["Ohjelmointikielet"]
    rust["✓ Rust"]
    go["Go"]
    java["Java"]
    kotlin["Kotlin"]
    javascript["JavaScript"]
    typescript["TypeScript"]
    tcl["Tcl"]
    funktionaalinen_ohjelmointi["✓ Funktionaalinen ohjelmointi (Racket)"]
    cpp_suorituskyky["C++:n suorituskyky"]
    c_asm_integraatio["C ja assembly yhteen"]
    python_c_integraatio["Python ja C/C++ yhteen"]
  end
  subgraph sovellukset["Sovelluskehitys"]
    sql["✓ SQL ja relaatiotietokannat"]
    html_css["HTML ja CSS"]
    web_sovellukset["Web-sovellukset"]
    taustapalvelut["Taustapalvelut"]
    android_sovellukset["Android-sovellukset"]
  end
  komentorivi --> versionhallinta
  ohjelmoinnin_perusteet --> c_kieli
  komentorivi --> c_kieli
  c_kieli --> moderni_cpp
  ohjelmoinnin_perusteet --> python
  komentorivi --> bash
  ohjelmoinnin_perusteet --> bash
  python --> python_tyokalut
  komentorivi --> python_tyokalut
  c_kieli --> rakennus_ja_testaus
  versionhallinta --> rakennus_ja_testaus
  bash --> rakennus_ja_testaus
  ohjelmoinnin_perusteet --> lineaarialgebra
  lineaarialgebra --> signaalimatematiikka
  diskreetti_matematiikka --> todennakoisyys
  c_kieli --> tietorakenteet
  diskreetti_matematiikka --> tietorakenteet
  tietorakenteet --> algoritmit
  algoritmit --> edistyneet_algoritmit
  algoritmit --> kaantajatekniikka
  assembly --> kaantajatekniikka
  funktionaalinen_ohjelmointi --> kaantajatekniikka
  diskreetti_matematiikka --> digitaalitekniikka
  c_kieli --> assembly
  digitaalitekniikka --> assembly
  assembly --> tietokonearkkitehtuuri
  assembly --> binaarit_ja_linkitys
  tietokonearkkitehtuuri --> kayttojarjestelmat
  kayttojarjestelmat --> rinnakkaisohjelmointi
  moderni_cpp --> rinnakkaisohjelmointi
  tietokonearkkitehtuuri --> suorituskyky
  algoritmit --> suorituskyky
  digitaalitekniikka --> kiintea_pilkku
  c_kieli --> kiintea_pilkku
  digitaalitekniikka --> rtl_suunnittelu
  digitaalitekniikka --> vhdl
  rtl_suunnittelu --> verifiointi
  python_tyokalut --> verifiointi
  rtl_suunnittelu --> fpga_toteutus
  moderni_cpp --> hlm_mallinnus
  tietokonearkkitehtuuri --> hlm_mallinnus
  kiintea_pilkku --> hlm_mallinnus
  hlm_mallinnus --> arkkitehtuurin_tutkiminen
  suorituskyky --> arkkitehtuurin_tutkiminen
  todennakoisyys --> arkkitehtuurin_tutkiminen
  rtl_suunnittelu --> eda_skriptaus
  python_tyokalut --> eda_skriptaus
  rakennus_ja_testaus --> eda_skriptaus
  tcl --> eda_skriptaus
  hlm_mallinnus --> hls
  fpga_toteutus --> hls
  dsp --> dsp_laitteisto
  kiintea_pilkku --> dsp_laitteisto
  verifiointi --> dsp_laitteisto
  fpga_toteutus --> dsp_laitteisto
  signaalimatematiikka --> signaalit_ja_jarjestelmat
  python_tyokalut --> signaalit_ja_jarjestelmat
  signaalit_ja_jarjestelmat --> dsp
  c_kieli --> dsp
  dsp --> tiedonsiirto
  todennakoisyys --> tiedonsiirto
  tiedonsiirto --> sdr
  tietokonearkkitehtuuri --> mikrokontrollerit
  binaarit_ja_linkitys --> mikrokontrollerit
  mikrokontrollerit --> oheislaitevaylat
  mikrokontrollerit --> rtos
  kayttojarjestelmat --> rtos
  kayttojarjestelmat --> embedded_linux
  rakennus_ja_testaus --> embedded_linux
  embedded_linux --> linux_ajurit
  oheislaitevaylat --> linux_ajurit
  komentorivi --> tietoverkot
  tietoverkot --> verkko_ohjelmointi
  kayttojarjestelmat --> verkko_ohjelmointi
  verkko_ohjelmointi --> hajautetut_jarjestelmat
  rinnakkaisohjelmointi --> hajautetut_jarjestelmat
  algoritmit --> hajautetut_jarjestelmat
  hajautetut_jarjestelmat --> jarjestelmasuunnittelu
  sql --> jarjestelmasuunnittelu
  tietoverkot --> kontit_ja_pilvi
  lineaarialgebra --> renderoinnin_perusteet
  moderni_cpp --> renderoinnin_perusteet
  renderoinnin_perusteet --> sateenseuranta
  todennakoisyys --> sateenseuranta
  algoritmit --> sateenseuranta
  renderoinnin_perusteet --> gpu_ohjelmointi
  rinnakkaisohjelmointi --> gpu_ohjelmointi
  gpu_ohjelmointi --> gpu_laskenta
  suorituskyky --> gpu_laskenta
  tietoverkot --> tietoturvan_perusteet
  c_kieli --> tietoturvan_perusteet
  binaarit_ja_linkitys --> takaisinmallinnus
  kayttojarjestelmat --> takaisinmallinnus
  tietoturvan_perusteet --> takaisinmallinnus
  takaisinmallinnus --> haavoittuvuudet
  takaisinmallinnus --> laiteohjelmiston_takaisinmallinnus
  mikrokontrollerit --> laiteohjelmiston_takaisinmallinnus
  c_kieli --> rust
  ohjelmoinnin_perusteet --> go
  ohjelmoinnin_perusteet --> java
  java --> kotlin
  ohjelmoinnin_perusteet --> javascript
  javascript --> typescript
  ohjelmoinnin_perusteet --> tcl
  ohjelmoinnin_perusteet --> funktionaalinen_ohjelmointi
  moderni_cpp --> cpp_suorituskyky
  suorituskyky --> cpp_suorituskyky
  assembly --> c_asm_integraatio
  python_tyokalut --> python_c_integraatio
  moderni_cpp --> python_c_integraatio
  ohjelmoinnin_perusteet --> sql
  typescript --> web_sovellukset
  html_css --> web_sovellukset
  tietoverkot --> web_sovellukset
  java --> taustapalvelut
  sql --> taustapalvelut
  tietoverkot --> taustapalvelut
  kotlin --> android_sovellukset
```

## Taidot alueittain

### Perusta

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Komentorivi ja Linux | 3 | – | [valmis](../komentorivi/) |
| Ohjelmoinnin perusteet (Python) | 5 | – | [valmis](../ohjelmoinnin-perusteet/) |
| Bash-skriptaus | 3 | Komentorivi ja Linux, Ohjelmoinnin perusteet (Python) | [valmis](../bash/) |
| C-kieli | 5 | Komentorivi ja Linux, Ohjelmoinnin perusteet (Python) | [valmis](../c-kieli/) |
| Python | 5 | Ohjelmoinnin perusteet (Python) | [valmis](../python/) |
| Versionhallinta (Git) | 2 | Komentorivi ja Linux | suunniteltu |
| Käännösjärjestelmät, testaus ja CI | 3 | Bash-skriptaus, C-kieli, Versionhallinta (Git) | suunniteltu |
| Moderni C++ | 5 | C-kieli | [valmis](../moderni-cpp/) |
| Python työkaluohjelmointiin | 5 | Komentorivi ja Linux, Python | suunniteltu |

### Matematiikka

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Diskreetti matematiikka | 5 | – | suunniteltu |
| Lineaarialgebra | 5 | Ohjelmoinnin perusteet (Python) | suunniteltu |
| Todennäköisyys ja tilastot | 3 | Diskreetti matematiikka | suunniteltu |
| Kompleksiluvut ja Fourier-analyysi | 5 | Lineaarialgebra | suunniteltu |

### Algoritmit ja tietorakenteet

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Tietorakenteet | 5 | C-kieli, Diskreetti matematiikka | suunniteltu |
| Algoritmit | 5 | Tietorakenteet | suunniteltu |
| Edistyneet algoritmit ja tietorakenteet | 5 | Algoritmit | suunniteltu |
| Kääntäjätekniikka | 5 | Algoritmit, Assembly, Funktionaalinen ohjelmointi (Racket) | suunniteltu |

### Tietokonejärjestelmät

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Digitaalitekniikka | 5 | Diskreetti matematiikka | suunniteltu |
| Assembly | 5 | C-kieli, Digitaalitekniikka | suunniteltu |
| Objektitiedostot, linkitys ja ABI | 3 | Assembly | suunniteltu |
| Tietokonearkkitehtuuri | 5 | Assembly | suunniteltu |
| Käyttöjärjestelmät | 5 | Tietokonearkkitehtuuri | suunniteltu |
| Suorituskyvyn analyysi ja optimointi | 3 | Algoritmit, Tietokonearkkitehtuuri | suunniteltu |
| Rinnakkaisohjelmointi | 5 | Käyttöjärjestelmät, Moderni C++ | suunniteltu |

### Laitteistosuunnittelu

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Lukujen esitys ja kiinteän pilkun aritmetiikka | 3 | C-kieli, Digitaalitekniikka | suunniteltu |
| RTL-suunnittelu SystemVerilogilla | 5 | Digitaalitekniikka | [valmis](../rtl-suunnittelu/) |
| RTL-suunnittelu VHDL:llä | 5 | Digitaalitekniikka | suunniteltu |
| EDA-työkaluketjujen automatisointi | 3 | Käännösjärjestelmät, testaus ja CI, Python työkaluohjelmointiin, RTL-suunnittelu SystemVerilogilla, Tcl | suunniteltu |
| FPGA-toteutus | 5 | RTL-suunnittelu SystemVerilogilla | suunniteltu |
| Laitteiston verifiointi | 5 | Python työkaluohjelmointiin, RTL-suunnittelu SystemVerilogilla | suunniteltu |
| Korkean tason mallinnus (SystemC/TLM) | 5 | Lukujen esitys ja kiinteän pilkun aritmetiikka, Moderni C++, Tietokonearkkitehtuuri | suunniteltu |
| Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen | 5 | Korkean tason mallinnus (SystemC/TLM), Suorituskyvyn analyysi ja optimointi, Todennäköisyys ja tilastot | suunniteltu |
| DSP-algoritmien laitteistototeutus | 5 | Digitaalinen signaalinkäsittely, FPGA-toteutus, Laitteiston verifiointi, Lukujen esitys ja kiinteän pilkun aritmetiikka | suunniteltu |
| Korkean tason synteesi | 5 | FPGA-toteutus, Korkean tason mallinnus (SystemC/TLM) | suunniteltu |

### Signaalinkäsittely ja radiot

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Signaalit ja järjestelmät | 5 | Kompleksiluvut ja Fourier-analyysi, Python työkaluohjelmointiin | suunniteltu |
| Digitaalinen signaalinkäsittely | 5 | C-kieli, Signaalit ja järjestelmät | suunniteltu |
| Digitaalinen tiedonsiirto | 5 | Digitaalinen signaalinkäsittely, Todennäköisyys ja tilastot | suunniteltu |
| Ohjelmistoradio | 5 | Digitaalinen tiedonsiirto | suunniteltu |

### Sulautetut järjestelmät

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Mikrokontrollerit ja bare-metal-ohjelmointi | 5 | Objektitiedostot, linkitys ja ABI, Tietokonearkkitehtuuri | suunniteltu |
| Oheislaiteväylät | 3 | Mikrokontrollerit ja bare-metal-ohjelmointi | suunniteltu |
| Reaaliaikakäyttöjärjestelmät | 5 | Käyttöjärjestelmät, Mikrokontrollerit ja bare-metal-ohjelmointi | suunniteltu |
| Sulautettu Linux | 5 | Käyttöjärjestelmät, Käännösjärjestelmät, testaus ja CI | suunniteltu |
| Linux-laiteajurit | 5 | Oheislaiteväylät, Sulautettu Linux | suunniteltu |

### Verkot ja hajautetut järjestelmät

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Tietoverkot | 5 | Komentorivi ja Linux | suunniteltu |
| Säiliöt ja pilvi-infrastruktuuri | 3 | Tietoverkot | suunniteltu |
| Verkko-ohjelmointi | 5 | Käyttöjärjestelmät, Tietoverkot | suunniteltu |
| Hajautetut järjestelmät | 5 | Algoritmit, Rinnakkaisohjelmointi, Verkko-ohjelmointi | suunniteltu |
| Skaalautuvien järjestelmien suunnittelu | 5 | Hajautetut järjestelmät, SQL ja relaatiotietokannat | suunniteltu |

### Tietokonegrafiikka

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Renderöinnin perusteet | 5 | Lineaarialgebra, Moderni C++ | suunniteltu |
| Säteenseuranta ja fysikaalinen valaistus | 5 | Algoritmit, Renderöinnin perusteet, Todennäköisyys ja tilastot | suunniteltu |
| GPU-ohjelmointi ja grafiikkarajapinnat | 5 | Renderöinnin perusteet, Rinnakkaisohjelmointi | suunniteltu |
| GPU-laskenta | 3 | GPU-ohjelmointi ja grafiikkarajapinnat, Suorituskyvyn analyysi ja optimointi | suunniteltu |

### Tietoturva ja takaisinmallinnus

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Tietoturvan perusteet | 3 | C-kieli, Tietoverkot | suunniteltu |
| Takaisinmallinnus | 5 | Käyttöjärjestelmät, Objektitiedostot, linkitys ja ABI, Tietoturvan perusteet | suunniteltu |
| Haavoittuvuuksien analyysi ja hyödyntäminen | 5 | Takaisinmallinnus | suunniteltu |
| Laiteohjelmiston takaisinmallinnus | 5 | Mikrokontrollerit ja bare-metal-ohjelmointi, Takaisinmallinnus | suunniteltu |

### Ohjelmointikielet

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| Funktionaalinen ohjelmointi (Racket) | 5 | Ohjelmoinnin perusteet (Python) | [valmis](../funktionaalinen-ohjelmointi/) |
| Go | 5 | Ohjelmoinnin perusteet (Python) | suunniteltu |
| Java | 5 | Ohjelmoinnin perusteet (Python) | suunniteltu |
| JavaScript | 5 | Ohjelmoinnin perusteet (Python) | suunniteltu |
| Tcl | 2 | Ohjelmoinnin perusteet (Python) | suunniteltu |
| Kotlin | 3 | Java | suunniteltu |
| Rust | 5 | C-kieli | [valmis](../rust/) |
| TypeScript | 3 | JavaScript | suunniteltu |
| C ja assembly yhteen | 2 | Assembly | suunniteltu |
| Python ja C/C++ yhteen | 3 | Moderni C++, Python työkaluohjelmointiin | suunniteltu |
| C++:n suorituskyky | 3 | Moderni C++, Suorituskyvyn analyysi ja optimointi | suunniteltu |

### Sovelluskehitys

| Taito | op | Edellyttää | Tila |
|-------|---:|------------|------|
| HTML ja CSS | 3 | – | suunniteltu |
| SQL ja relaatiotietokannat | 5 | Ohjelmoinnin perusteet (Python) | [valmis](../sql/) |
| Taustapalvelut | 5 | Java, SQL ja relaatiotietokannat, Tietoverkot | suunniteltu |
| Android-sovellukset | 5 | Kotlin | suunniteltu |
| Web-sovellukset | 5 | HTML ja CSS, Tietoverkot, TypeScript | suunniteltu |

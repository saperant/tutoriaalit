# Johdanto {.runko-johdanto}

Laitteistoprojektissa ajetaan kymmeniä työkaluja: lint, simulaattorit,
synteesi, ajoitusanalyysi, formaali verifiointi, sijoittelu ja reititys
sekä niiden ympärillä rekisterigeneraattorit ja raporttien käsittely.
Jokainen työkalu ajetaan satoja tai tuhansia kertoja eri parametreilla,
siemenillä ja koodiversioilla. Kukaan ei aja niitä käsin. Ajot
tehdään skripteillä, ja niiden laatu ratkaisee, voiko tuloksiin luottaa.

Huono vuoskripti toimii kerran tekijänsä koneella. Hyvä vuoskripti
toimii samoin kaikilla koneilla ja CI:ssä. Se ajaa uudelleen vain sen,
mikä on muuttunut, eikä tulkitse kaatunutta ajoa onnistuneeksi. Siitä
näkee jälkikäteen, millä komennoilla, parametreilla ja työkaluversioilla
tulos syntyi. Tämä taito käsittelee juuri näitä ominaisuuksia:

- **Suunnitteluvuo** jaetaan vaiheiksi, joilla on syötteet, tulosteet
  ja riippuvuudet. Vaihe ajetaan uudelleen vain, kun jokin sen
  tulokseen vaikuttava asia muuttuu.
- **Työkaluja ohjataan** eräajona. Paluuarvot, lokit ja aikakatkaisut
  käsitellään niin, ettei mikään virhe katoa.
- **Tcl on työkalujen sisäinen kieli.** Lähes kaikki kaupalliset
  EDA-työkalut ja Yosys ajavat Tcl-skriptejä. Ulkoinen vuo kirjoitetaan
  yleensä Pythonilla.
- **Raportit jäsennetään** yhteiseen tietomalliin, josta tehdään
  koosteet, laatuportit ja trendit.
- **Regressiot** ajetaan rinnakkain monella siemenellä. Virheet
  ryhmitellään allekirjoittain, ja historia tallennetaan tietokantaan.
- **Rekisterikuvauksesta tuotetaan** RTL, C-otsake, dokumentaatio ja
  testit, ja CI tarkistaa, että ne ovat samassa tahdissa.
- **CI laitteistoprojektille** tarvitsee työkalukontit,
  lisenssipalvelimet, artefaktit ja välimuistit.

## Esitiedot ja rajaus

Taito rakentuu neljän edeltäjänsä päälle, eikä niiden asioita toisteta:

| Taito | Mitä tästä oletetaan |
|------------------|------------------------------------------|
| RTL-suunnittelu SystemVerilogilla | moduulit, testipenkit, Verilator ja Yosys perustasolla |
| Python työkaluohjelmointiin | argparse, subprocess, pathlib, säännölliset lausekkeet, dataclassit, tyypitys |
| Käännösjärjestelmät, testaus ja CI | Make, riippuvuudet, pytest, CI-putken perusajatus |
| Tcl | Tcl-kielen perusteet: korvaukset, listat, proseduurit, `catch` |

Taidot *Laitteiston verifiointi*, *FPGA-toteutus*, *ASIC-toteutus* ja
*SoC-integraatio* kertovat, mitä vuon vaiheissa tapahtuu. Tässä
keskitytään siihen, miten vaiheet kytketään toisiinsa ja miten niiden
tuloksia käsitellään. Yleinen CI:n ja toimitusputken suunnittelu on
taidossa *Jatkuva integraatio ja toimitus*, ja rekisterikuvausten
standardimuodot (SystemRDL, IP-XACT) taidossa *Laitteiston
kuvausstandardit (SystemRDL, IP-XACT)*.

## Esimerkkiprojekti

Kaikki esimerkit käyttävät samaa pientä projektia hakemistossa
`esimerkit/`:

| Hakemisto | Sisältö |
|------------|------------------------------------------------|
| `rtl/` | parametroitu laskuri, pieni ALU (makrolla `VIKA` viallinen) ja lint-varoituksia sisältävä ohjainlohko |
| `tb/` | itsetarkistava ALU-testipenkki, joka käyttää omaa satunnaislukugeneraattoria ja tulostaa toiminnallisen kattavuuden |
| `tcl/` | Yosysin Tcl-skriptit ja opetus-sta, pieni Tcl:llä kirjoitettu ajoitusanalysaattori, joka käyttäytyy kuten kaupalliset työkalut |
| `vuo/` | Python-kirjasto: vaiheet, työkalujen ajo, jäsentimet, varoitukset, regressio, historia, rekisterit ja CI |
| `asetukset/` | TOML-muotoiset testilista, sallitut varoitukset, rekisterikuvaus ja CI-putken kuvaus |
| `naytteet/` | tallennettuja raportteja jäsentimien testeihin |
| `tuotettu/` | rekisterikuvauksesta tuotetut tiedostot |

Suunnitelmat ovat tarkoituksella pieniä, koska huomio on niiden
ympärillä olevassa vuossa. Laskuri on synteesin ja ajoitusanalyysin
kohde, ja sen leveys `LEVEYS` on parametri, jolla vuota ajetaan eri
asetuksilla. ALU on regressioiden kohde. Makro `VIKA` tuo XOR-operaatioon virheen,
joka näkyy vain osalla satunnaisista syötteistä, kuten oikeat viat:

```{.systemverilog tiedosto="esimerkit/rtl/alu.sv"}
```

Esimerkit ajavat Verilatorin, Icarus Verilogin, Yosysin ja Tcl-tulkin
oikeasti. Niiden numerot riippuvat työkalujen versioista: uudempi Yosys
voi tuottaa eri solumäärän ja eri pituisen polun. Siksi esimerkit
tulostavat työkalujen tuloksista vain arvioita, kuten "ajoitus MET" tai
"kiikkuja LEVEYS + 1". Täsmälliset luvut näytetään vain silloin, kun ne
luetaan tallennetusta raportista. Samaa periaatetta kannattaa noudattaa
omissakin vuon testeissä.

## Työkalut

Vuon ensimmäinen tehtävä on tarkistaa, että työkalut löytyvät. Muuten
kaatuminen tulee vasta keskellä vuota ja näyttää työkalun virheeltä:

```{.python tiedosto="esimerkit/01-tyokalut.py" osa="tyokalut"}
```

```{.tuloste tiedosto="esimerkit/01-tyokalut.odotettu" asti="Kaikki työkalut"}
```

Sama ohjelma tulostaa lopuksi vuon vaiheet tasoittain. Ne esitellään
luvussa 2.

## Esimerkkien ajaminen

Esimerkkihakemiston Makefile tarkistaa Python-koodin ruffilla ja
mypyllä (`--strict`), ajaa jäsentimien yksikkötestit pytestillä ja
ajaa jokaisen esimerkin verraten tulostetta tiedostoon `*.odotettu`:

```text
cd esimerkit
make -j4              # kaikki
make 07-regressio     # yksi esimerkki
```

Työkalut ovat valmiina kehityskontissa `.devcontainer/eda-skriptaus`.
Ubuntu 24.04:n paketit riittävät: `verilator`, `yosys`, `iverilog` ja
`tcl8.6` sekä Pythonin `ruff`, `mypy` ja `pytest`.

# VHDL ja SystemVerilog rinnakkain

VHDL ja SystemVerilog kuvaavat samaa laitteistoa, ja synteesityökalu
tuottaa niistä saman netlistan. Erot ovat kielen filosofiassa: VHDL
tarkistaa paljon käännösvaiheessa ja vaatii eksplisiittisyyttä,
SystemVerilog on tiiviimpi ja sallivampi. Tämä luku on tarkoitettu
suunnittelijalle, joka osaa toisen kielen ja lukee tai kirjoittaa
toista. Se toimii myös kertauksena koko tutoriaalille.

## Sama laskuri molemmilla kielillä

Taidon *RTL-suunnittelu SystemVerilogilla* ensimmäinen esimerkki on
laskuri, jolla on asynkroninen nollaus ja sallinta. VHDL-versio:

```{.vhdl tiedosto="esimerkit/11-laskuri.vhd" osa="entiteetti"}
```

Testipenkki tekee saman kuin SystemVerilog-versio ja tulostaa
täsmälleen saman tuloksen:

```{.vhdl tiedosto="esimerkit/11-laskuri.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/11-laskuri.odotettu"}
```

Asynkroninen nollaus kirjoitetaan VHDL:ssä niin, että nollaus on
herkkyyslistassa ja tarkistetaan ennen kellon reunaa (`if rst_n = '0'
then ... elsif rising_edge(clk) then`). SystemVerilogissa sama on
`always_ff @(posedge clk or negedge rst_n)`. Laskurin yli kierto on
molemmissa luonnollinen, koska `unsigned`-tyypin ja `logic`-vektorin
yhteenlasku tapahtuu operandin levyisenä.

## Vastaavuudet

| Asia | VHDL | SystemVerilog |
|------|------|---------------|
| rajapinta | `entity` + `architecture` | `module` |
| parametri | `generic (N : positive := 8)` | `parameter int N = 8` |
| instanssi | `u : entity work.x generic map (...) port map (a => s)` | `x #(.N(8)) u (.a(s));` |
| bittityyppi | `std_logic` (9 arvoa) | `logic` (4 arvoa: 0, 1, X, Z) |
| luku | `unsigned`, `signed`, `integer range` | `logic [7:0]`, `logic signed`, `int` |
| kombinaatio | `process (all)` | `always_comb` |
| kiikku | `process (clk)` + `rising_edge` | `always_ff @(posedge clk)` |
| sijoitus | signaali `<=`, muuttuja `:=` | ei-estävä `<=`, estävä `=` |
| ehdollinen | `y <= a when s else b;` | `assign y = s ? a : b;` |
| tilat | `type tila_t is (A, B);` | `typedef enum logic [1:0] {A, B} tila_t;` |
| tietue | `record` | `struct packed` |
| monistus | `for ... generate` | `for (genvar i ...)` |
| jaettu koodi | `package` | `package` |
| väittämä | `assert ... severity failure` | `assert` / `$fatal` |
| tuloste | `textio`, `to_string` | `$display` |
| lopetus | `std.env.finish` | `$finish` |

## Missä VHDL on tiukempi

- **Leveydet.** VHDL ei katkaise eikä laajenna hiljaa. SystemVerilog
  sallii `logic [7:0] a = 9'h1FF;` ja katkaisee; lint-työkalu
  (Verilator `-Wall`) varoittaa, mutta kieli ei estä.
- **Etumerkki.** VHDL:ssä etumerkki on tyypissä. SystemVerilogissa
  lauseke on etumerkitön, jos yksikin operandi on, mikä tuottaa
  yllättäviä vertailuja.
- **`case`-kattavuus.** VHDL vaatii kaikki valinnat käännösvaiheessa.
  SystemVerilogin `unique case` tarkistaa saman simuloinnissa.
- **Moninkertaiset ajurit.** `std_ulogic` havaitsee ne elaboroinnissa;
  SystemVerilogissa `always_ff`- ja `always_comb`-lohkot estävät saman
  signaalin ohjaamisen kahdesta lohkosta.
- **Arvoalueet.** `integer range 0 to 9` tarkistetaan simuloinnissa;
  SystemVerilogissa vastaavaa ei ole.

## Missä SystemVerilog on edellä

- **Verifiointi.** Luokat, rajoitettu satunnaistus, kattavuusryhmät,
  SVA-väittämät ja UVM tekevät SystemVerilogista verifioinnin
  valtakielen. VHDL:n vastine on OSVVM- ja UVVM-kirjastoissa sekä
  PSL-väittämissä.
- **Rajapinnat.** SystemVerilogin `interface` ja `modport` niputtavat
  väylän signaalit ja suunnat. VHDL-2019 toi vastaavan `view`-
  rakenteen, mutta sen tuki työkaluissa on vielä vähäistä; VHDL-2008:ssa
  käytetään tietueita, yksi kumpaankin suuntaan.
- **Tiiviys.** Sama logiikka on SystemVerilogilla usein kolmanneksen
  lyhyempi. Tämä on sekä etu että riski.

## Simulointisemantiikka

VHDL:n deltasykli ja SystemVerilogin tapahtuma-alueet (active, NBA)
ratkaisevat saman ongelman: kiikut näytteistävät ennen kuin mikään
päivittyy. VHDL:ssä ratkaisu on kielessä itsessään, koska signaali
päivittyy aina vasta deltasyklin lopussa. SystemVerilogissa
suunnittelijan on noudatettava sääntöä "`<=` kiikkuihin, `=`
kombinaatiologiikkaan", tai simulointi voi riippua lohkojen
suoritusjärjestyksestä. VHDL:n vastaava ansa on kellon viivästyminen
deltasyklillä (luku 5), joka SystemVerilogissa on harvinaisempi.

## Sekakielinen suunnittelu

Simulaattorit ja synteesityökalut käsittelevät molempia kieliä samassa
projektissa. Rajapinnan yli kannattaa käyttää yksinkertaisia tyyppejä:
`std_logic` ja `std_logic_vector` VHDL:n puolella, `logic` ja
`logic [N-1:0]` SystemVerilogin puolella. Tietueet, luettelotyypit,
rajoittamattomat portit ja `integer`-portit eivät siirry kielestä
toiseen luotettavasti. VHDL:stä Verilog-moduuli instansioidaan
komponenttiesittelyllä (luku 2).

## Valinta

Kieli valitaan yleensä organisaation, asiakkaan tai olemassa olevan
koodin perusteella, ei teknisin perustein. Kun valinta on vapaa,
nyrkkisääntö on:

| Tilanne | Suositus |
|---------|----------|
| FPGA-tuote, eurooppalainen tai turvallisuuskriittinen ala | VHDL |
| ASIC tai suuri verifiointiympäristö | SystemVerilog |
| Avoimen lähdekoodin työkaluketju (Verilator, Yosys) | SystemVerilog tai VHDL GHDL:n kautta |
| Testipenkit Pythonilla | kumpi tahansa ja cocotb |

Molempien lukutaito kuuluu ammattilaisen perustaitoihin, koska IP-
lohkot, valmistajan esimerkit ja asiakkaan koodi tulevat kummalla
tahansa kielellä.

## Käytännössä

- **Ajattele laitteistoa, kirjoita kielellä.** Kiikku, multiplekseri
  ja tilarekisteri ovat samat molemmissa kielissä. Kun luet vierasta
  kieltä, piirrä rakenne ja vertaa sitä tuttuun.
- **Tuo kielen hyvät tavat mukanasi.** VHDL-tausta opettaa
  ajattelemaan leveyksiä ja etumerkkiä; SystemVerilogissa sama
  huolellisuus ja lint-työkalu korvaavat kielen tarkistukset.
  SystemVerilog-tausta opettaa erottamaan `always_comb`- ja
  `always_ff`-lohkot; VHDL:ssä sama kuri tarkoittaa, että prosessi on
  joko `process (all)` tai kellotettu, ei koskaan sekoitus.
- **Yksinkertaiset tyypit kielten rajalla.** Sekakielisessä
  hierarkiassa porttien tyypit pidetään bitteinä ja bittivektoreina.

## Itsearviointi

- Osaat kääntää yksinkertaisen RTL-lohkon VHDL:stä SystemVerilogiksi
  ja takaisin.
- Osaat luetella kolme virheluokkaa, jotka VHDL havaitsee
  käännösvaiheessa mutta SystemVerilog vasta lint-työkalulla tai
  simuloinnissa.
- Osaat kertoa, miten deltasykli ja SystemVerilogin NBA-alue ratkaisevat
  saman ongelman.
- Osaat suunnitella kielten rajan yli kulkevan rajapinnan.

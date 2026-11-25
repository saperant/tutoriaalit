# Verilog-2005-yhteensopivuus

Verilog-2005 on edelleen käytössä: vanhoissa IP-lohkoissa, avoimen
lähdekoodin projekteissa, opetuksessa ja työkaluissa, jotka eivät tue
SystemVerilogia kokonaan. Lähes kaikki Verilog-2005-koodi on myös
SystemVerilogia, joten vanhaa koodia voi käyttää uuden rinnalla.
Poikkeus ovat SystemVerilogin uudet varatut sanat (`logic`, `bit`,
`do`, `unique`, `priority`, `var` ja muut): vanha koodi, joka käyttää
niitä signaalien niminä, ei käänny, ellei tiedostoa rajata vanhaan
kieleen direktiivillä `` `begin_keywords "1364-2005" ``. Toisin päin
yhteensopivuus ei toimi lainkaan. Tämä luku kertoo, mitkä erot RTL-
suunnittelija kohtaa ja miten kirjoitetaan koodia, joka kelpaa
molempiin.

## Erot

| SystemVerilog | Verilog-2005 |
|---------------|--------------|
| `logic` | `wire` (ajetaan `assign`illa) tai `reg` (sijoitetaan `always`-lohkossa) |
| `always_ff @(posedge clk)` | `always @(posedge clk)` |
| `always_comb` | `always @*` |
| `typedef enum ... tila_t` | `localparam`-vakiot ja `reg [N:0] tila` |
| `struct packed` | bittivälit ja `localparam`-indeksit |
| `unique case`, `priority case` | `case` ja `default` |
| `int`, `bit` | `integer`, `reg` |
| `'0`, `'1` | `{N{1'b0}}`, `{N{1'b1}}` |
| `N'(x)` | `x[N-1:0]` tai apumuuttuja |
| `for (int i = 0; ...)` | `integer i;` erikseen, tai `genvar` |
| `package`, `import` | `` `include`` |
| `.portti` (implisiittinen nimi) | `.portti(portti)` |

Verilog-2005:ssä ei ole `always_comb`-lohkon tarkistuksia, joten salvat
ja useat ajajat paljastuvat vasta lintissä tai synteesissä. `always @*`
toimii yleensä samoin kuin `always_comb`, mutta se ei suorita lohkoa
simuloinnin alussa eikä huomaa funktion kautta luettuja signaaleja.

## Sama tilakone kahdella kielellä

Sekvenssintunnistin etsii bittivirrasta kuvion 1011. Verilog-2005-versiossa
tilat ovat nimettyjä vakioita, tilarekisteri on `reg` ja
kombinaatiologiikka on `always @*`-lohkossa:

```{.systemverilog tiedosto="esimerkit/12-verilog2005.sv" osa="v2005"}
```

SystemVerilog-versio on lähes sama, mutta tilatyyppi on luettelo,
sijoitusten oikeellisuus tarkistetaan ja simulaattori näyttää tilojen
nimet:

```{.systemverilog tiedosto="esimerkit/12-verilog2005.sv" osa="sv"}
```

Testipenkki syöttää saman bittivirran molemmille ja vertaa ulostuloja
jakso jaksolta:

```{.tuloste tiedosto="esimerkit/12-verilog2005.odotettu"}
```

Molemmat ovat Moore-koneita: osuma näkyy tilasta, kun kuvion viimeinen
bitti on vastaanotettu. Päällekkäiset osumat ovat sallittuja, koska
tilasta `S1011` siirrytään tilaan, joka vastaa osuman loppuosaa (`1` tai
`10`).

## Implisiittiset johdot

Verilogin vaarallisin oletus on *implisiittinen johto*: jos
porttikytkennässä tai `assign`-lauseen vasemmalla puolella on
tuntematon nimi, kääntäjä luo hiljaa yksibittisen johtimen.
Kirjoitusvirhe ei siis ole käännösvirhe:

```{.systemverilog tiedosto="esimerkit/12-implisiittinen.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/12-implisiittinen.odotettu"}
```

Direktiivi `` `default_nettype none`` poistaa implisiittiset johdot
käytöstä, jolloin tuntematon nimi on käännösvirhe. Direktiivi on
voimassa tiedoston loppuun ja seuraaviin tiedostoihin, joten tiedoston
lopussa palautetaan oletus `` `default_nettype wire``. Muuten
direktiivi rikkoisi muiden tiedostojen vanhaa koodia, joka luottaa
implisiittisiin johtoihin. Direktiivi kuuluu myös SystemVerilog-koodiin,
jossa sama oletus on yhä voimassa.

## Työkalutuki ja muunnokset

SystemVerilogin synteesikelpoista osajoukkoa tukevat nykyään kaikki
kaupalliset synteesityökalut (Vivado, Quartus, Design Compiler) ja
Yosys. Tuki on silti epätasaista uusimmissa piirteissä, kuten
rajapinnoissa (`interface`), paketeissa ja parametroiduissa tyypeissä.
Jos työkaluketjussa on vain Verilog-2005:tä ymmärtävä työkalu, kuten
vanha simulaattori tai jokin avoin ASIC-vuo, on kaksi vaihtoehtoa:

1. **Kirjoitetaan Verilog-2005:n ja SystemVerilogin yhteistä
   osajoukkoa.** Taulukon vasemmasta sarakkeesta luovutaan, ja
   lint ajetaan molemmissa tiloissa (Verilatorissa valitsin
   `--language 1364-2005`).
2. **Muunnetaan automaattisesti.** Työkalu `sv2v` muuntaa
   synteesikelpoisen SystemVerilogin Verilog-2005:ksi. Lähdekoodi
   pysyy SystemVerilogina, ja muunnos tehdään käännösvuossa.

Ensimmäinen vaihtoehto sopii pieneen IP-lohkoon, joka jaetaan laajalle
käyttäjäkunnalle. Toinen sopii omaan projektiin, jossa vain yksi
työkalu vaatii Verilogia.

## Käytännössä

- **Uusi koodi SystemVerilogina.** `logic`, `always_ff`,
  `always_comb` ja `enum` löytävät virheitä, jotka Verilogissa
  paljastuvat vasta piirissä. Verilog-2005:een palataan vain työkalun
  pakosta.
- **`default_nettype none` jokaiseen tiedostoon.** Se maksaa kaksi
  riviä ja poistaa kokonaisen virheluokan. Tiedoston lopussa oletus
  palautetaan, jotta muiden tiedostojen vanha koodi ei rikkoudu.
- **Vanhaa koodia ei käännetä uudelleen huvikseen.** Toimiva ja
  testattu Verilog-moduuli kääritään tarvittaessa
  SystemVerilog-moduuliin, mutta sitä ei kirjoiteta uudelleen ilman
  testejä, jotka todistavat käyttäytymisen samaksi.
- **`reg` ei ole rekisteri.** Verilog-koodia lukiessa `reg`
  tarkoittaa vain muuttujaa, jota sijoitetaan `always`-lohkossa. Rekisteri
  syntyy vain kellotetusta lohkosta.
- **Vertaa vanhaa ja uutta rinnakkain.** Kun moduuli muunnetaan
  kieleltä toiselle, molemmat versiot simuloidaan samalla syötteellä
  ja ulostuloja verrataan jaksoittain, kuten edellä.

## Itsearviointi

- Osaat lukea Verilog-2005-koodia ja kertoa, mitä `wire`, `reg` ja
  `always @*` vastaavat SystemVerilogissa.
- Osaat kirjoittaa tilakoneen sekä Verilog-2005:llä että
  SystemVerilogilla.
- Osaat selittää implisiittisen johdon vaaran ja estää sen
  direktiivillä `` `default_nettype none``.
- Osaat valita yhteisen osajoukon ja automaattisen muunnoksen välillä,
  kun työkaluketju vaatii Verilog-2005:tä.

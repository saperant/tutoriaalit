# Kutsusopimus rajapintana

Kun C-ohjelma kutsuu assemblyllä kirjoitettua funktiota, kääntäjä ei
näe funktion sisään. Se tietää vain prototyypin ja olettaa, että
toteutus noudattaa alustan kutsusopimusta (*calling convention*,
osa ABI:a): mistä argumentit löytyvät, minne paluuarvo laitetaan,
mitkä rekisterit säilyvät kutsun yli ja missä tilassa pino on. Tässä
luvussa kutsusopimusta käsitellään *rajapintana*, jonka kumpikin osapuoli
lupaa pitää, ja tutkitaan, mitä tapahtuu, kun lupaus rikotaan.

## Prototyyppi ja toteutus

Rajapinta kirjoitetaan otsaketiedostoon kuten minkä tahansa
C-kirjaston rajapinta. Sama otsake kelpaa myös assembly-tiedostolle:
kun GCC kokoaa `.S`-päätteisen tiedoston (iso S), se ajaa sen ensin
C:n esikääntäjän läpi ja määrittelee makron `__ASSEMBLER__`. Otsake
voi siis tarjota C:lle prototyypit ja assemblylle makrot:

```{.c tiedosto="esimerkit/02-rajapinta/funktio.h" osa="prototyyppi"}
```

```{.c tiedosto="esimerkit/02-rajapinta/funktio.h" osa="makrot"}
```

Makrot hoitavat jokaisen funktion vakiokehyksen: `.globl` tekee
symbolista näkyvän linkkerille, `.type` merkitsee sen funktioksi ja
`.size` kirjaa sen koon symbolitauluun. Debuggeri, profiloija ja
`objdump` käyttävät tyyppiä ja kokoa, joten ne kannattaa merkitä aina.
Pinomerkinnästä ja purkutiedoista (`CFI_ALKU` ja `PURKU`) kerrotaan
seuraavassa luvussa.

Toteutus laskee tavun esiintymät nollaan päättyvässä merkkijonossa:

```{.gnuassembler tiedosto="esimerkit/02-rajapinta/x86.S" osa="laske"}
```

```{.gnuassembler tiedosto="esimerkit/02-rajapinta/rv.S" osa="laske"}
```

Funktio käyttää vain rekistereitä, jotka kutsuja on joka tapauksessa
varautunut menettämään (x86-64:llä `rax`, `rdx`, `rdi`; RISC-V:llä
`t0`, `t1`, `a0`), eikä kutsu muita funktioita. Tällainen
*lehtifunktio* ei tarvitse pinokehystä lainkaan.

## Testaa C-viitettä vastaan

Assembly-funktiolle kirjoitetaan aina C-viitetoteutus, ja testit
vertaavat niitä toisiinsa. Viite on helppo lukea ja todeta oikeaksi;
assemblyä ei ole.

```{.c tiedosto="esimerkit/02-rajapinta/main.c" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/02-rajapinta/odotettu"}
```

Viimeinen tapaus on valittu tarkoituksella. C:n `char` on x86-64:llä
etumerkillinen ja RISC-V:llä etumerkitön, ja kutsusopimus määrää,
miten pieni argumentti välitetään. System V AMD64 määrittelee vain
rekisterin alimman tavun (`sil`); ylemmät bitit voivat olla mitä
tahansa. Siksi x86-64-versio vertaa tavurekisteriä `%sil` eikä koko
rekisteriä. RISC-V psABI taas vaatii, että kutsuja laajentaa arvon
64-bittiseksi tyypin mukaan: etumerkittömällä `char`illa nollilla.
Siksi RISC-V-versio voi verrata koko rekisteriä `a1`, mutta vain
koska tavu luetaan etumerkittömänä (`lbu`). Jos joku kääntäisi
kutsujan valitsimella `-fsigned-char`, `a1` saisi arvon
`0xFFFF…FFC3`, eikä yksikään tavu täsmäisi. Tämä on kutsusopimuksen
tyypillinen hiljainen virhe: kaikki ASCII-testit menevät läpi, ja vika
näkyy vasta ensimmäisellä ääkkösellä.

Symbolitaulusta voi tarkistaa, että makrot tekivät tehtävänsä:

```{.bash tiedosto="esimerkit/02-rajapinta/tarkistus.sh" osa="symbolit"}
```

```{.tuloste tiedosto="esimerkit/02-rajapinta/tarkistus.odotettu"}
```

Ilman `.type`-direktiiviä tyyppi olisi `NOTYPE` ja ilman `.size`-direktiiviä
koko 0. Ohjelma toimisi silti, mutta esimerkiksi `perf` ja `gdb`
eivät osaisi liittää näytteitä ja osoitteita funktioon.

## Kutsun yli säilyvät rekisterit

Kutsusopimus jakaa rekisterit kahteen ryhmään. Kutsujan tallennettavat
(*caller-saved*) rekisterit kutsuttu funktio saa sotkea vapaasti.
Kutsun yli säilyvät (*callee-saved*) rekisterit sen pitää palauttaa
ennalleen: x86-64:llä `rbx`, `rbp` ja `r12`–`r15`, RISC-V:llä
`s0`–`s11`. Kääntäjä sijoittaa muuttujat, joita tarvitaan kutsun
jälkeen, mieluiten näihin rekistereihin, koska silloin sen ei tarvitse
tallentaa niitä pinoon jokaisen kutsun ympärillä.

```{.dot otsikko="Kokonaislukurekisterien roolit kutsussa. Tummennetut säilyvät kutsun yli: kutsuttu funktio saa käyttää niitä vain, jos se palauttaa vanhan arvon."}
digraph {
  rankdir=TB; nodesep=0.2; ranksep=0.25;
  node [shape=plain, style=""];
  x [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="4"><i>x86-64 (System V)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">argumentit</td><td bgcolor="#FFFFFF">rdi rsi rdx rcx r8 r9</td><td bgcolor="#FFFFFF">paluuarvo</td><td bgcolor="#FFFFFF">rax (rdx)</td></tr>
    <tr><td bgcolor="#FFFFFF">muut sotkettavat</td><td bgcolor="#FFFFFF">r10 r11</td><td bgcolor="#C9D6E8">säilyvät</td><td bgcolor="#C9D6E8">rbx rbp r12–r15, rsp</td></tr></table>>];
  r [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="4"><i>RISC-V (LP64D)</i></td></tr>
    <tr><td bgcolor="#FFFFFF">argumentit</td><td bgcolor="#FFFFFF">a0–a7</td><td bgcolor="#FFFFFF">paluuarvo</td><td bgcolor="#FFFFFF">a0 (a1)</td></tr>
    <tr><td bgcolor="#FFFFFF">muut sotkettavat</td><td bgcolor="#FFFFFF">t0–t6, ra</td><td bgcolor="#C9D6E8">säilyvät</td><td bgcolor="#C9D6E8">s0–s11, sp</td></tr></table>>];
  x -> r [style=invis];
}
```

Sopimuksen noudattamista voi testata *rekisterivahdilla*: funktiolla,
joka täyttää kaikki säilyvät rekisterit tunnetuilla arvoilla, kutsuu
testattavaa funktiota ja tarkistaa, ovatko arvot ennallaan:

```{.gnuassembler tiedosto="esimerkit/02-rekisterivahti/x86.S" osa="vahti"}
```

GAS-makro `tarkista` (`.macro` … `.endm`) toistaa saman vertailun
kullekin rekisterille; `9:` on paikallinen numeronimiö, johon `9f`
viittaa eteenpäin. RISC-V-versio käyttää lisäksi `.irp`-toistoa, joka
kirjoittaa saman rivin kullekin luettelon arvolle:

```{.gnuassembler tiedosto="esimerkit/02-rekisterivahti/rv.S" osa="vahti"}
```

Vahti itse noudattaa sopimusta: se tallentaa kaikki säilyvät
rekisterit ennen kuin täyttää ne ja palauttaa ne lopuksi. x86-64:llä
seitsemäs `push` on tasausta varten. Funktioon tultaessa pino on 8
tavua sivussa 16:n rajasta (paluuosoite), ja seitsemän 8 tavun
työntöä tuo sen takaisin rajalle ennen `call`-käskyä.

```{.dot otsikko="Pino funktiossa `vahdi` juuri ennen kutsua. Pino kasvaa alaspäin, ja jokainen ruutu on 8 tavua. x86-64:llä `call` työnsi paluuosoitteen, joten 16 tavun rajalle päästään parittomalla määrällä työntöjä. RISC-V:llä paluuosoite on rekisterissä `ra`, ja kehys varataan kerralla 16:lla jaollisena."}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.4;
  node [shape=plain, style=""];
  x [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" colspan="2" align="left"><i>x86-64</i></td></tr>
    <tr><td bgcolor="#FFFFFF">paluuosoite</td><td border="0" align="left">← rsp funktion alussa (16n + 8)</td></tr>
    <tr><td bgcolor="#EEF1F6">rbx</td><td border="0" align="left">1. työntö: raja</td></tr>
    <tr><td bgcolor="#EEF1F6">rbp</td><td border="0"></td></tr>
    <tr><td bgcolor="#EEF1F6">r12</td><td border="0" align="left">3. työntö: raja</td></tr>
    <tr><td bgcolor="#EEF1F6">r13</td><td border="0"></td></tr>
    <tr><td bgcolor="#EEF1F6">r14</td><td border="0" align="left">5. työntö: raja</td></tr>
    <tr><td bgcolor="#EEF1F6">r15</td><td border="0"></td></tr>
    <tr><td bgcolor="#F3E2C7">rdx (muuttuneet)</td><td border="0" align="left">← rsp ennen call-käskyä: 7. työntö, raja</td></tr></table>>];
  r [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" colspan="2" align="left"><i>RISC-V</i></td></tr>
    <tr><td bgcolor="#FFFFFF">kutsujan kehys</td><td border="0" align="left">← sp funktion alussa (16n)</td></tr>
    <tr><td bgcolor="#EEF1F6">ra</td><td border="0" align="left">104(sp)</td></tr>
    <tr><td bgcolor="#EEF1F6">s0 … s11</td><td border="0" align="left">96(sp) … 8(sp)</td></tr>
    <tr><td bgcolor="#F3E2C7">a2 (muuttuneet)</td><td border="0" align="left">← sp = alku − 112 (16n)</td></tr></table>>];
  x -> r [style=invis];
}
```

Testattavina on kaksi funktiota, jotka käyttävät säilyvää rekisteriä.
Toinen tallentaa sen, toinen ei:

```{.gnuassembler tiedosto="esimerkit/02-rekisterivahti/x86.S" osa="testattavat"}
```

```{.gnuassembler tiedosto="esimerkit/02-rekisterivahti/rv.S" osa="testattavat"}
```

Vahti löytää rikkojan kummallakin arkkitehtuurilla:

```{.tuloste tiedosto="esimerkit/02-rekisterivahti/odotettu-x86"}
```

## Mitä rikkomus tekee kutsujalle

Tulosteen kaksi viimeistä riviä näyttävät, miksi virhe on vaarallinen.
Rikkova funktio palauttaa oikean arvon. Vika näkyy kutsujassa, joka
luotti siihen, että rekisterissä oleva muuttuja säilyy:

```{.c tiedosto="esimerkit/02-rekisterivahti/main.c" osa="seuraus"}
```

GCC siirtää kertolaskun kutsun jälkeen ja pitää sitä varten `a`:n
kutsun ajan säilyvässä rekisterissä `rbx` (RISC-V:llä `s0`).
`kasvata_rikki` kirjoittaa samaan rekisteriin arvon 6, joten kutsun
jälkeen kääntäjä laskee 3 · 6 + 6 = 24 eikä 3 · 5 + 6 = 21.
Jos funktio olisi sotkenut eri rekisterin, tulos
olisi voinut olla oikein, ja virhe olisi tullut esiin vasta toisella
kääntäjäversiolla tai optimointitasolla. Siksi rekisterivahti on
parempi testi kuin pelkkä tulosten vertailu: se löytää rikkomuksen
riippumatta siitä, sattuuko kutsuja käyttämään juuri sitä rekisteriä.

## Pinon tasaus

Toinen helposti rikottava lupaus on pinon tasaus. System V AMD64
vaatii, että pino-osoitin on 16:lla jaollinen juuri ennen
`call`-käskyä, joten kutsutun funktion alussa `rsp + 8` on 16:lla
jaollinen. RISC-V vaatii, että `sp` on aina 16:lla jaollinen.
Kääntäjä luottaa tähän ja sijoittaa vektorimuuttujat pinoon käskyillä,
jotka vaativat tasauksen. Seuraava assembly-funktio kutsuu C-funktiota
korjaamatta pinoa:

```{.gnuassembler tiedosto="esimerkit/02-rekisterivahti/x86.S" osa="tasaamatta"}
```

```{.c tiedosto="esimerkit/02-rekisterivahti/main.c" osa="tasaus"}
```

```{.bash tiedosto="esimerkit/02-rekisterivahti/tarkistus.sh" osa="kaatuu"}
```

```{.tuloste tiedosto="esimerkit/02-rekisterivahti/tarkistus.odotettu"}
```

Ohjelma kaatuu C-funktiossa käskyyn `movaps`, jonka muistioperandin on
oltava 16 tavun rajalla. Virheen tehnyt funktio on jo pinossa
kutsujana, eikä kaatumiskohdassa ole mitään väärää. Kaatuminen ei
myöskään ole varmaa: jos `kayttaa_vektoria` ei käyttäisi
vektorimuuttujaa, sama virhe jäisi piiloon, kunnes joku lisää
funktioon liukulukulaskentaa tai `printf`-kutsun. RISC-V-laitteisto ei
tarkista `sp`:n tasausta lainkaan, joten siellä rikkomus näkyy
tyypillisesti vasta väärin tasattuina atomisina operaatioina tai
toisten kirjastojen virheinä.

Vaihtuva-argumenttisen C-funktion, kuten `printf`in, kutsussa on
x86-64:llä vielä yksi lupaus: rekisterin `al` on kerrottava, montako
vektorirekisteriä argumentteihin käytettiin (yläraja riittää). Kun
liukulukuargumentteja ei ole, ennen kutsua tarvitaan `xor %eax, %eax`.
Unohdus toimii usein sattumalta, koska `rax`:ssä on pieni luku.
RISC-V:llä vastaavaa rekisteriä ei ole.

## Käytännössä

- **Kirjoita prototyyppi ensin ja dokumentoi rekisterit.** Jokaisen
  assembly-funktion alussa on kommentti, joka toistaa C-prototyypin ja
  kertoo, missä rekisterissä kukin argumentti on. Lukija ei muuten
  tiedä, onko `rsi` merkkijono vai pituus.
- **Pidä rajapinta yksinkertaisena.** Kokonaisluvut, osoittimet ja
  `size_t`. Tietueiden välittäminen arvona ja liukulukujen ja
  kokonaislukujen sekoittaminen tekevät rekisterijaosta monimutkaisen.
  Jos assembly lukee tietueen kenttiä, lukitse kenttien siirtymät C:n
  puolella `_Static_assert(offsetof(...) == 8, ...)`-tarkistuksilla.
- **Älä luota alle 64-bittisten argumenttien yläbitteihin.**
  x86-64:llä ne ovat määrittelemättömät, RISC-V:llä ne laajennetaan
  tyypin mukaan, ja `char`in etumerkki vaihtelee alustoittain. Laajenna
  argumentti itse (`movzbl`, `movslq`) tai käytä rajapinnassa
  `unsigned char`-, `uint8_t`- tai 64-bittisiä tyyppejä.
- **Testaa rekisterivahdilla.** Vahti on muutaman kymmenen rivin
  testiapu, joka löytää säilyvien rekisterien rikkomukset ennen kuin
  ne näkyvät satunnaisina virheinä. Glibc ja monet kryptokirjastot
  testaavat assembly-funktionsa juuri näin.
- **Tarkista tasaus jokaisessa kutsussa.** Laske työnnöt ja
  pinovaraukset funktion alusta `call`-käskyyn. x86-64:llä parittoman
  määrän 8 tavun työntöjä jälkeen pino on rajalla.
- **Nollaa `eax` ennen `printf`-kutsua** ja muita
  vaihtuva-argumenttisia funktioita x86-64:llä.

## Itsearviointi

- Osaat kirjoittaa otsakkeen, joka antaa C:lle prototyypin ja
  assemblylle makrot, ja selittää `__ASSEMBLER__`-makron roolin.
- Osaat kertoa, miten alle 64-bittiset argumentit välitetään
  x86-64:llä ja RISC-V:llä, ja miksi `char`in etumerkki vaikuttaa
  assembly-funktioon.
- Osaat nimetä kutsun yli säilyvät rekisterit kummallakin
  arkkitehtuurilla ja selittää, miksi niiden rikkominen näkyy
  kutsujassa eikä rikkovassa funktiossa.
- Osaat kirjoittaa rekisterivahdin ja käyttää sitä testinä.
- Osaat laskea pinon tasauksen ennen `call`-käskyä ja tunnistaa
  tasausvirheen `movaps`-kaatumisesta.

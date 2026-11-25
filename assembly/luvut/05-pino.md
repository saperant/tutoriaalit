# Pino ja kutsukonventiot

Funktiokutsu on konekielessä sopimus. Kutsuja asettaa argumentit
sovittuihin paikkoihin ja hyppää funktioon tallentaen paluuosoitteen.
Funktio palauttaa arvon sovitussa rekisterissä ja jättää osan
rekistereistä ennalleen. Sopimus on *kutsukonventio*, ja se on osa
alustan ABI:ta (*application binary interface*). Sen ansiosta eri
kääntäjillä ja kielillä tehdyt funktiot voivat kutsua toisiaan.
Linuxin x86-64 noudattaa System V AMD64 -ABI:ta, RISC-V RISC-V psABI:ta.

## Sopimus rekistereistä

| Asia | System V AMD64 | RISC-V psABI |
|---------------------------|-------------------------------------|------------------------------|
| Kokonaislukuargumentit | `rdi`, `rsi`, `rdx`, `rcx`, `r8`, `r9` | `a0`–`a7` |
| Liukulukuargumentit | `xmm0`–`xmm7` | `fa0`–`fa7` |
| Loput argumentit | pinossa | pinossa |
| Paluuarvo | `rax` (ja `rdx`), `xmm0` | `a0` (ja `a1`), `fa0` |
| Kutsujan tallennettavat | `rax`, `rcx`, `rdx`, `rsi`, `rdi`, `r8`–`r11` | `t0`–`t6`, `a0`–`a7`, `ra` |
| Kutsutun tallennettavat | `rbx`, `rbp`, `r12`–`r15` | `s0`–`s11`, `sp` |
| Pinon tasaus kutsuhetkellä | 16 tavua | 16 tavua |

*Kutsujan tallennettavat* rekisterit (*caller-saved*) funktio saa
muuttaa vapaasti. Jos kutsuja tarvitsee niiden arvoja kutsun jälkeen,
sen on tallennettava ne itse. *Kutsutun tallennettavat* rekisterit
(*callee-saved*) funktion on palautettava ennalleen ennen paluuta.
Jako on kompromissi: väliaikaisia arvoja ei tarvitse tallentaa, ja
pitkäikäisille arvoille on rekisterejä, jotka säilyvät kutsujen yli.

## Kutsu ja paluu

x86-64:n `call kohde` työntää paluuosoitteen pinoon ja hyppää. `ret`
poimii osoitteen pinosta ja hyppää siihen. RISC-V:n `call` on
pseudokäsky, joka tallentaa paluuosoitteen rekisteriin `ra` ja hyppää,
ja `ret` hyppää `ra`:n osoitteeseen. Pinoon ei kosketa. Kokoaja purkaa
`call`:n käskypariksi `auipc ra` + `jalr ra`, joka yltää mihin tahansa,
ja linkkeri lyhentää parin yhdeksi `jal`-käskyksi, kun kohde on
lähellä. *Lehtifunktio*, joka ei kutsu muita,
ei RISC-V:llä tarvitse pinoa lainkaan. Funktion, joka kutsuu muita,
on tallennettava `ra` itse, koska seuraava `call` korvaa sen.

Pino kasvaa molemmilla alaspäin, kohti pienempiä osoitteita. Funktion
*pinokehys* on sen oma alue pinossa paluuosoitteen alapuolella:
tallennetut rekisterit, paikalliset muuttujat ja seuraaville kutsuille
pinossa välitettävät argumentit.

## Rekursio

Rekursiivinen kertoma tarvitsee arvon `n` kutsun jälkeen. Se
tallennetaan kutsun yli säilyvään rekisteriin, ja rekisterin
alkuperäinen arvo tallennetaan pinoon:

```{.gnuassembler tiedosto="esimerkit/05-pino/x86.S" osa="kertoma"}
```

```{.gnuassembler tiedosto="esimerkit/05-pino/rv.S" osa="kertoma"}
```

RISC-V:llä kehys varataan vähentämällä `sp`:tä, ja tallennettavat
rekisterit (`ra` ja `s0`) kirjoitetaan siihen. Kehyksen koko on 16:n
monikerta, koska pinon on oltava 16 tavun rajalla. Perustapaus `n <= 1`
palaa ennen kehyksen varaamista: kääntäjät tekevät saman
(*shrink-wrapping*), koska ilmaisesta polusta ei kannata maksaa.

## Pinossa välitetyt argumentit

Kun argumentteja on enemmän kuin rekisterejä, loput ovat kutsujan
pinokehyksessä. x86-64:llä seitsemäs argumentti on kohdassa `8(%rsp)`,
koska `call` työnsi paluuosoitteen sen päälle. RISC-V:llä yhdeksäs on
kohdassa `0(%sp)`:

```{.gnuassembler tiedosto="esimerkit/05-pino/x86.S" osa="summa9"}
```

```{.gnuassembler tiedosto="esimerkit/05-pino/rv.S" osa="summa9"}
```

Vaihtuva-argumenttinen funktio, kuten `printf`, lisää x86-64:llä
yhden säännön: kutsujan on kerrottava rekisterissä `al`, montako
vektorirekisteriä argumentteihin käytettiin. Kun assembly kutsuu
`printf`:ää pelkillä kokonaisluvuilla, ennen kutsua tarvitaan
`xor %eax, %eax`.

Tietueet ja liukuluvut noudattavat omia sääntöjään: pieni tietue
välitetään rekistereissä kentittäin, suuri muistissa osoittimen kautta.
Säännöt ovat ABI-dokumenteissa (luku Lopuksi). Käytännössä
assembly-funktion rajapinta kannattaa pitää yksinkertaisena:
kokonaislukuja ja osoittimia.

## Takaisinkutsu C:hen

Kun assembly-funktio kutsuu toista funktiota, kaikki sopimuksen kohdat
tulevat vastaan: argumentit, kutsun yli säilyvät rekisterit, kehys ja
tasaus. `kay_lapi` kutsuu C-funktiota jokaiselle taulukon alkiolle ja
summaa tulokset:

```{.gnuassembler tiedosto="esimerkit/05-pino/x86.S" osa="kay_lapi"}
```

```{.gnuassembler tiedosto="esimerkit/05-pino/rv.S" osa="kay_lapi"}
```

Taulukon osoitin, jäljellä olevien määrä, funktio-osoitin ja summa
pidetään kutsutun tallennettavissa rekistereissä, koska takaisinkutsu
saa muuttaa kaikkia muita. Niiden alkuperäiset arvot tallennetaan ensin
ja palautetaan lopuksi käänteisessä järjestyksessä.

```{.dot otsikko="Funktion kay_lapi pinokehys takaisinkutsun hetkellä. Osoitteet kasvavat ylöspäin, pino alaspäin; jokainen ruutu on 8 tavua."}
digraph {
  nodesep=0.25;
  node [shape=plaintext, style=""];
  x86 [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>x86-64</b></td><td border="0"></td></tr>
    <tr><td bgcolor="#EEF1F2" width="112">kutsujan kehys</td><td border="0"></td></tr>
    <tr><td bgcolor="#F1E3CC">paluuosoite</td><td border="0" align="left"><font point-size="9">← rsp alussa: 16n + 8</font></td></tr>
    <tr><td bgcolor="#E4DCF0">tallennettu rbx</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">tallennettu r12</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">tallennettu r13</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">tallennettu r14</td><td border="0"></td></tr>
    <tr><td>täyte (sub $8)</td><td border="0" align="left"><font point-size="9">← rsp ennen kutsua: 16n</font></td></tr>
    <tr><td bgcolor="#F1E3CC">call: paluuosoite</td><td border="0" align="left"><font point-size="9">← rsp f:n alussa: 16n + 8</font></td></tr>
  </table>>];
  rv [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>RISC-V</b></td><td border="0"></td></tr>
    <tr><td bgcolor="#EEF1F2" width="112">kutsujan kehys</td><td border="0" align="left"><font point-size="9">← sp alussa: 16n</font></td></tr>
    <tr><td bgcolor="#F1E3CC">ra, 40(sp)</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">s0, 32(sp)</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">s1, 24(sp)</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">s2, 16(sp)</td><td border="0"></td></tr>
    <tr><td bgcolor="#E4DCF0">s3, 8(sp)</td><td border="0"></td></tr>
    <tr><td>täyte, 0(sp)</td><td border="0" align="left"><font point-size="9">← sp ennen kutsua: 16n</font></td></tr>
    <tr><td border="0"> </td><td border="0"></td></tr>
  </table>>];
}
```

Kuvasta näkyy kolme asiaa. Paluuosoite on x86-64:llä pinossa heti
kutsujan kehyksen alla, RISC-V:llä funktio tallentaa sen itse
rekisteristä `ra`. Kumpikin kehys päättyy täytteeseen, jolla ei ole
muuta tehtävää kuin tasaus. Ja x86-64:llä `call` siirtää pino-osoitinta
vielä kahdeksan tavua, joten kutsuttu funktio näkee aina arvon
16n + 8.

**Pinon tasaus** on kohta, jossa käsin kirjoitettu assembly useimmin
pettää. System V -ABI vaatii, että `rsp` on 16:n monikerta juuri ennen
`call`-käskyä. Funktion alussa `rsp` on siis 16:n monikerta plus 8
(paluuosoite). `kay_lapi` työntää neljä rekisteriä (32 tavua) ja
vähentää vielä 8, jolloin pino on tasattu. C-puolen takaisinkutsu
tulostaa liukuluvun:

```{.c tiedosto="esimerkit/05-pino/main.c" osa="takaisinkutsu"}
```

```{.tuloste tiedosto="esimerkit/05-pino/odotettu"}
```

Väärin tasattu pino ei näy useimmissa funktioissa, mutta kaataa
ohjelman, kun kutsuttu funktio käyttää tasausta vaativia SSE-käskyjä.
glibc:n `printf` tallentaa liukulukurekisterit pinoon `movaps`-käskyllä,
joka vaatii 16 tavun rajan. Seuraava funktio kutsuu takaisinkutsua
tasaamatta pinoa:

```{.gnuassembler tiedosto="esimerkit/05-tasaus-kaatuu/x86.S" osa="vaarin"}
```

Ohjelma kaatuu (`Segmentation fault`) `printf`:n sisällä, kaukana
virheellisestä käskystä. Testi `05-tasaus-kaatuu` varmistaa, että
kaatuminen todella tapahtuu. Korjaus on varata pinosta 8 tavua ennen
kutsua (`sub $8, %rsp`) ja vapauttaa ne jälkeenpäin, kuten
`kay_lapi` tekee.

## Debuggeri käsky kerrallaan

Tällaista kaatumista ei löydä lukemalla, koska virheellinen käsky ja
kaatumiskohta ovat eri funktioissa. Debuggeri näyttää, missä ohjelma
kaatui ja mitä rekistereissä silloin oli. Assemblyä debugataan käsky
kerrallaan, ei rivi kerrallaan:

| gdb-komento | Tehtävä |
|-------------|---------|
| `break kay_lapi` | pysähdy funktion alkuun |
| `stepi`, `nexti` | yksi käsky; `nexti` ei mene kutsun sisään |
| `x/i $pc` | näytä seuraava käsky |
| `info registers rbx r12` | rekisterien arvot |
| `p/x $rsp` | lausekkeen arvo heksana |
| `x/6xg $rsp` | kuusi 8 tavun sanaa muistista osoitteesta `rsp` |
| `bt` | pinojälki |
| `layout asm` | käskyt ja nykyinen kohta näkyviin |

Kaatuva esimerkki eräajona (`gdb -batch -ex run -ex 'x/i $pc' -ex
'p/x $rbp' -ex bt build/05-tasaus-kaatuu/x86`). Tuloste on yhdestä
ajosta; osoitteet ja kirjaston sisäiset nimet vaihtelevat koneittain:

```text
Program received signal SIGSEGV, Segmentation fault.
0x00000000004123ef in __printf_chk ()
=> 0x4123ef <__printf_chk+47>:  movaps %xmm0,-0x80(%rbp)
$1 = 0x7fffffffc148
#0  0x00000000004123ef in __printf_chk ()
#1  0x0000000000401817 in kutsu ()
#2  0x00000000004016dc in main ()
```

Kaatunut käsky on `movaps`, joka vaatii 16 tavun rajalle tasatun
osoitteen, ja `rbp` päättyy kahdeksaan eikä nollaan. Pinojäljen
seuraava kehys on oma funktiomme `kutsu`: vika on siellä, ei
kirjastossa.

Sama väline näyttää, miltä oikein tehty kehys näyttää. Funktion
`kay_lapi` alussa `rsp` päättyy kahdeksaan. Viiden käskyn (neljä
`push`-käskyä ja `sub`) jälkeen se päättyy nollaan, ja muistissa ovat
ylhäältä lukien täyte, `r14`, `r13`, `r12`, `rbx` ja paluuosoite, kuten
edellä kuvassa:

```text
(gdb) break kay_lapi
(gdb) run
(gdb) p/x $rsp
$1 = 0x7fffffffc138
(gdb) stepi 5
(gdb) p/x $rsp
$2 = 0x7fffffffc110
(gdb) x/6xg $rsp
0x7fffffffc110: 0x0000000000000013      0x00000000004a8f68
0x7fffffffc120: 0x00007fffffffc298      0x00007fffffffc288
0x7fffffffc130: 0x0000000000000019      0x000000000040178d
```

RISC-V-ohjelman voi debugata QEMU:n gdb-palvelimen kautta:
`qemu-riscv64 -g 1234 ./ohjelma` ja toisessa ikkunassa
`gdb-multiarch ./ohjelma` sekä `target remote :1234`. Komennot ovat
samat, rekisterien nimet RISC-V:n.

## Paluuosoite datan vieressä: pinosuoja

Pinokehyksen kuvasta näkyy myös, miksi puskurin ylivuoto on vaarallinen.
Paikallinen taulukko on samassa kehyksessä kuin tallennetut rekisterit
ja paluuosoite, ja taulukon indeksit kasvavat kohti niitä. Jos funktio
kirjoittaa taulukon lopun yli, se korvaa paluuosoitteen, ja `ret`
hyppää osoitteeseen, jonka kirjoittaja valitsi.

Kääntäjä torjuu tätä *pinosuojalla* (*stack protector*, *canary*).
Funktion alussa paikallisten taulukoiden ja paluuosoitteen väliin
kirjoitetaan satunnainen arvo, ja ennen paluuta tarkistetaan, että se
on ennallaan. Ubuntun GCC lisää suojan oletuksena jokaiseen funktioon,
jossa on paikallinen taulukko tai jonka paikallisen muuttujan osoite
annetaan eteenpäin (`-fstack-protector-strong`):

```{.c tiedosto="esimerkit/05-suoja-naytteet/puskuri.c"}
```

```{.gnuassembler tiedosto="esimerkit/05-suoja-naytteet/puskuri-x86.s"}
```

Suojan tunnistaa kolmesta kohdasta. Alussa arvo luetaan säiekohtaisesta
muistista (`%fs:40`) ja tallennetaan kehyksen yläpäähän (`24(%rsp)`),
puskurin ja paluuosoitteen väliin. Lopussa tallennetusta arvosta
vähennetään alkuperäinen. Jos erotus ei ole nolla, funktio ei palaa
vaan kutsuu funktiota `__stack_chk_fail`, joka lopettaa ohjelman.
RISC-V:llä rakenne on sama, mutta vertailuarvo on globaalissa
muuttujassa `__stack_chk_guard`.

Kun luet oman ohjelmasi `gcc -S` -tulostetta, nämä rivit ovat mukana.
Luvun 6 näytteistä ne on poistettu valitsimella
`-fno-stack-protector`, jotta varsinainen koodi erottuu. Ylivuotojen
hyödyntäminen ja muut suojaukset käsitellään taidossa
*Haavoittuvuuksien analyysi ja torjunta*.

## Kehysosoitin ja pinojälki

Kääntäjä voi käyttää kehysosoitinta (`rbp`, RISC-V:llä `s0`/`fp`),
joka osoittaa funktion kehyksen alkuun. Kehysosoitinten ketjusta
debuggeri ja profiloija voivat koota pinojäljen. Optimoitu koodi jättää
kehysosoittimen yleensä pois (`-fomit-frame-pointer`) ja vapauttaa
rekisterin muuhun käyttöön. Pinojälki kootaan silloin
DWARF-purkutiedoista (`.eh_frame`), jotka kääntäjä tuottaa
`.cfi`-direktiiveillä. Käsin kirjoitettuun assemblyyn ne joutuu
lisäämään itse, jos pinojäljen halutaan kulkevan sen läpi (taito
*Objektitiedostot, linkitys ja ABI*).

## Käytännössä

- **Kirjoita prologi ja epilogi peilikuviksi.** Tallennetut
  rekisterit palautetaan käänteisessä järjestyksessä ja samoista
  kohdista. Pidä ne funktion alussa ja lopussa, älä hajauta.
- **Tasaa pino ennen jokaista kutsua.** x86-64:llä laske
  `call`-hetken siirtymä: 8 (paluuosoite) + työnnetyt rekisterit +
  varattu tila on oltava 16:n monikerta. RISC-V:llä kehyksen koko on
  16:n monikerta.
- **Pidä arvot kutsun yli kutsutun tallennettavissa rekistereissä.**
  Älä oleta, että `rcx` tai `t0` säilyy kutsun yli, vaikka kutsuttu
  funktio nyt sattuisi jättämään sen rauhaan.
- **Lehtifunktio ilman kehystä.** RISC-V:n lehtifunktio ei tarvitse
  pinoa, ja x86-64:n lehtifunktio voi käyttää 128 tavun *red zone*
  -aluetta `rsp`:n alapuolella ilman `sub`-käskyä (ei ytimen koodissa).
- **Aloita kaatumisen selvitys pinojäljestä ja `rsp`:stä.** Kun
  ohjelma kaatuu kirjastofunktiossa heti oman assembly-funktion
  jälkeen, katso kaatunut käsky (`x/i $pc`) ja pino-osoittimen viimeinen
  numero ennen kuin epäilet kirjastoa.
- **Testaa takaisinkutsulla.** Kun assembly-funktio kutsuu C:tä, kutsu
  testissä funktiota, joka käyttää liukulukuja ja `printf`:ää. Se
  paljastaa tasausvirheet heti.

## Itsearviointi

- Osaat luetella System V AMD64- ja RISC-V-kutsukonventioiden
  argumenttirekisterit, paluuarvorekisterit ja kutsun yli säilyvät
  rekisterit.
- Osaat kirjoittaa funktion, joka varaa pinokehyksen, tallentaa ja
  palauttaa tarvitsemansa rekisterit ja kutsuu toista funktiota.
- Osaat lukea pinossa välitetyt argumentit oikeista siirtymistä.
- Osaat selittää 16 tavun pinon tasauksen ja tunnistaa sen
  rikkomisesta johtuvan kaatumisen.
- Osaat piirtää funktion pinokehyksen: paluuosoitteen, tallennetut
  rekisterit, täytteen ja pino-osoittimen paikan.
- Osaat ajaa ohjelmaa debuggerissa käsky kerrallaan ja tutkia
  rekistereitä ja pinoa.
- Osaat tunnistaa pinosuojan kääntäjän tuottamasta koodista ja kertoa,
  mitä se suojaa.

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
poimii osoitteen pinosta ja hyppää siihen. RISC-V:n `call` (pseudo
`jal ra, kohde`) tallentaa paluuosoitteen rekisteriin `ra`, ja `ret`
hyppää siihen. Pinoon ei kosketa. *Lehtifunktio*, joka ei kutsu muita,
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

```{.gnuassembler tiedosto="esimerkit/06-pino/x86.S" osa="kertoma"}
```

```{.gnuassembler tiedosto="esimerkit/06-pino/rv.S" osa="kertoma"}
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

```{.gnuassembler tiedosto="esimerkit/06-pino/x86.S" osa="summa9"}
```

```{.gnuassembler tiedosto="esimerkit/06-pino/rv.S" osa="summa9"}
```

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

```{.gnuassembler tiedosto="esimerkit/06-pino/x86.S" osa="kay_lapi"}
```

```{.gnuassembler tiedosto="esimerkit/06-pino/rv.S" osa="kay_lapi"}
```

Taulukon osoitin, jäljellä olevien määrä, funktio-osoitin ja summa
pidetään kutsutun tallennettavissa rekistereissä, koska takaisinkutsu
saa muuttaa kaikkia muita. Niiden alkuperäiset arvot tallennetaan ensin
ja palautetaan lopuksi käänteisessä järjestyksessä.

**Pinon tasaus** on kohta, jossa käsin kirjoitettu assembly useimmin
pettää. System V -ABI vaatii, että `rsp` on 16:n monikerta juuri ennen
`call`-käskyä. Funktion alussa `rsp` on siis 16:n monikerta plus 8
(paluuosoite). `kay_lapi` työntää neljä rekisteriä (32 tavua) ja
vähentää vielä 8, jolloin pino on tasattu. C-puolen takaisinkutsu
tulostaa liukuluvun:

```{.c tiedosto="esimerkit/06-pino/main.c" osa="takaisinkutsu"}
```

```{.tuloste tiedosto="esimerkit/06-pino/odotettu"}
```

Väärin tasattu pino ei näy useimmissa funktioissa, mutta kaataa
ohjelman, kun kutsuttu funktio käyttää tasausta vaativia SSE-käskyjä.
glibc:n `printf` tallentaa liukulukurekisterit pinoon `movaps`-käskyllä,
joka vaatii 16 tavun rajan. Seuraava funktio kutsuu takaisinkutsua
tasaamatta pinoa:

```{.gnuassembler tiedosto="esimerkit/06-tasaus-kaatuu/x86.S" osa="vaarin"}
```

Ohjelma kaatuu (`Segmentation fault`) `printf`:n sisällä, kaukana
virheellisestä käskystä. Testi `06-tasaus-kaatuu` varmistaa, että
kaatuminen todella tapahtuu. Korjaus on varata pinosta 8 tavua ennen
kutsua (`sub $8, %rsp`) ja vapauttaa ne jälkeenpäin, kuten
`kay_lapi` tekee.

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

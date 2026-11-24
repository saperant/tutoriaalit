# Kokonainen esimerkki: Adler-32

Tässä luvussa toteutetaan Adler-32-tarkistussumma molemmilla
käskykannoilla. zlib käyttää sitä pakattujen tietojen eheyden
tarkistukseen (RFC 1950). Esimerkki kokoaa aiempien lukujen asiat:
silmukan, tavujen laajennuksen, jakolaskun, kutsukonvention ja
paluuarvon säännöt. Lisäksi se näyttää työtavan, jolla assembly-koodia
kannattaa kehittää: C-viitetoteutus, tunnetut testivektorit ja
vertailu.

## Algoritmi ja viitetoteutus

Adler-32 laskee kaksi summaa modulo 65521, joka on suurin lukua
65 536 pienempi alkuluku. `a` on yksi plus tavujen summa, `b` on `a`:n arvojen summa
jokaisen tavun jälkeen. Tulos on `b`:n ja `a`:n yhdistelmä
`(b << 16) | a`. Viitetoteutus C:llä on lyhyt ja ilmeinen:

```{.c tiedosto="esimerkit/11-adler/main.c" osa="viite"}
```

Viitetoteutus on tarkoituksella suoraviivainen eikä nopea. Sen tehtävä
on olla niin selvä, että sen oikeellisuus on helppo todeta lukemalla.

## Toteutus x86-64:llä

```{.gnuassembler tiedosto="esimerkit/11-adler/x86.S"}
```

Jakojäännös lasketaan `div`-käskyllä, joka jakaa `edx:eax`:n ja
jättää jakojäännöksen `edx`:ään. `edx` nollataan ennen jokaista jakoa
(luku 3). Argumentti `n` on `rsi`:ssä, joten `rdx`:n käyttö jakoon ei
tuhoa sitä. Kaikki käytetyt rekisterit ovat kutsujan tallennettavia,
joten pinokehystä ei tarvita.

## Toteutus RISC-V:llä

```{.gnuassembler tiedosto="esimerkit/11-adler/rv.S"}
```

`remu` laskee etumerkittömän jakojäännöksen suoraan. Funktion lopussa
on käsky, jota x86-64-versiossa ei ole: `sext.w`. RISC-V psABI vaatii,
että 32-bittinen paluuarvo palautetaan 64-bittisessä rekisterissä
**etumerkillä laajennettuna**, myös `uint32_t`. Kutsuja saa luottaa
siihen ja verrata arvoja 64-bittisinä ilman laajennusta. Ilman
`sext.w`:tä tulos, jonka bitti 31 on asetettu (kuten testin
`d43b9aef`), olisi rekisterissä väärässä muodossa, ja virhe näkyisi
vasta, kun kutsuja sattuu käyttämään ylimpiä bittejä. x86-64:llä ylimmät
32 bittiä ovat määrittelemättömät, ja kutsuja laajentaa itse.

## Testaus

Pääohjelma vertaa assembly-toteutusta viitetoteutukseen tunnetuilla ja
rajatapauksia koettelevilla syötteillä:

```{.c tiedosto="esimerkit/11-adler/main.c"}
```

```{.tuloste tiedosto="esimerkit/11-adler/odotettu"}
```

Testisyötteet on valittu tarkoituksella:

- **Tyhjä syöte** (tulos 1): silmukka ei suoritu kertaakaan.
- **`"Wikipedia"`** (`11e60398`): julkaistu testivektori, joka
  varmistaa, että viitetoteutuskin on oikein.
- **100 000 tavua vaihtelevaa dataa**: pitkä syöte, jossa moduloinnit
  tapahtuvat monta kertaa, ja tulos, jonka bitti 31 on asetettu.
- **5552 tavua arvoa `0xff`**: zlib tunnetusti viivästää
  modulointia ja laskee enintään 5552 tavua ennen sitä, koska se on
  suurin määrä, jolla 32-bittinen summa ei vuoda yli. Raja-arvo on
  hyvä testitapaus optimoidulle versiolle.

Sama tuloste tarkistetaan molemmilla arkkitehtuureilla, joten testi
todistaa myös, että toteutukset vastaavat toisiaan.

## Optimointi

Toteutus laskee kaksi jakoa jokaista tavua kohden, ja jako on hidas
(luku 3). zlib laskee 5552 tavua ilman jakoa ja moduloi vasta sitten,
jolloin jakoja on tuhansia kertoja vähemmän. Nopeimmat toteutukset
käyttävät SIMD-käskyjä (luku 9). Optimoitu versio on helppo tehdä
turvallisesti, koska viitetoteutus ja testivektorit ovat valmiina:
muutos on oikein, kun testit menevät läpi. Ennen optimointia kannattaa
kuitenkin katsoa, mitä kääntäjä tekee viitetoteutukselle. GCC korvaa
jakolaskun vakiolla kertolaskulla (luku 3), joten C-versio voi olla jo
nopeampi kuin yllä oleva käsin kirjoitettu `div`-versio.

## Debuggaus

Kun assembly-funktio palauttaa väärän tuloksen, debuggeri näyttää
rekisterit käsky kerrallaan. Natiivisti x86-64:llä:

```text
gdb ./build/11-adler/x86
(gdb) break adler32
(gdb) run
(gdb) layout asm          # käskyt näkyviin
(gdb) stepi               # yksi käsky
(gdb) info registers r8 r9 rcx
(gdb) x/16xb $rdi         # 16 tavua osoitteesta rdi
```

RISC-V-ohjelman voi debugata QEMU:n gdb-palvelimen kautta:
`qemu-riscv64 -g 1234 ./ohjelma` ja toisessa ikkunassa
`gdb-multiarch ./ohjelma` sekä `target remote :1234`. Komennot ovat
samat. Rekisteriarvojen seuraaminen käsky kerrallaan ja vertaaminen
viitetoteutuksen muuttujiin löytää useimmat virheet nopeasti.

## Käytännössä

- **Viitetoteutus ensin.** Kirjoita algoritmi selvästi C:llä ja testaa
  se tunnetuilla testivektoreilla ennen assemblyä.
- **Testaa rajatapaukset.** Tyhjä syöte, yksi alkio, pituus joka ei
  ole silmukan askeleen monikerta, suurimmat arvot ja tulokset, joiden
  ylin bitti on asetettu.
- **Noudata ABI:ta paluuarvoissa.** 32-bittinen arvo 64-bittisessä
  rekisterissä: RISC-V laajentaa etumerkillä, x86-64:llä ylimmät bitit
  ovat määrittelemättömät.
- **Vertaa kääntäjään.** Käsin kirjoitettu assembly on perusteltua vain,
  jos se on mitatusti nopeampi tai tekee jotain, mitä C ei voi ilmaista.

## Itsearviointi

- Osaat toteuttaa yksinkertaisen algoritmin assemblyllä molemmilla
  käskykannoilla ja testata sen C-viitetoteutusta vastaan.
- Osaat valita testisyötteet, jotka koettelevat assembly-koodin
  rajatapauksia.
- Osaat soveltaa RISC-V psABI:n etumerkkilaajennussääntöä 32-bittisiin
  paluuarvoihin.
- Osaat debugata assembly-funktiota gdb:llä käsky kerrallaan, myös
  QEMU:lla ajettavaa RISC-V-ohjelmaa.

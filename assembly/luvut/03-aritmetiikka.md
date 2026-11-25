# Aritmetiikka ja liput

Laskukäskyt ovat molemmilla käskykannoilla samankaltaisia: yhteen- ja
vähennyslasku, kertolasku, bittioperaatiot ja siirrot. Erot tulevat
siitä, miten käsky kertoo tuloksen ominaisuuksista, kuten kantoluvusta,
ylivuodosta ja nollasta. x86-64 käyttää *lippuja*, RISC-V ei.

## Kolmen ja kahden operandin käskyt

RISC-V:n käskyillä on kolme operandia: `add a0, a1, a2` laskee
`a0 = a1 + a2`, eivätkä lähteet muutu. x86-64:n käskyillä on kaksi
operandia, ja kohde on myös toinen lähde: `add %rsi, %rax` laskee
`rax = rax + rsi`. Jos alkuperäistä arvoa tarvitaan myöhemmin, se on
kopioitava ensin (`mov`). Siksi x86-64-koodissa on paljon `mov`-käskyjä,
ja kääntäjä käyttää `lea`-käskyä kolmen operandin yhteenlaskuna.

| Toiminto | x86-64 | RISC-V |
|----------|--------|--------|
| Yhteenlasku | `add %rsi, %rax` | `add a0, a0, a1` |
| Vähennys | `sub %rsi, %rax` | `sub a0, a0, a1` |
| Vakio | `add $5, %rax` | `addi a0, a0, 5` |
| Kertolasku | `imul %rsi, %rax` | `mul a0, a0, a1` |
| Jako | `div %rcx` (rdx:rax) | `div` / `divu` / `rem` / `remu` |
| Bitit | `and`, `or`, `xor`, `not` | `and`, `or`, `xor`, `xori a0, a0, -1` |
| Siirrot | `shl`, `shr` (looginen), `sar` (aritm.) | `sll`, `srl`, `sra` |
| Nollaus | `xor %eax, %eax` | `li a0, 0` (`addi a0, zero, 0`) |

`xor %eax, %eax` on x86-64:n vakiotapa nollata rekisteri: käsky on
lyhyt, suoritin tunnistaa sen riippumattomaksi edellisestä arvosta, ja
32-bittinen kirjoitus nollaa koko rekisterin. RISC-V:llä nollarekisteri
`zero` hoitaa saman.

Jakolasku on x86-64:llä poikkeuksellinen: `div %rcx` jakaa 128-bittisen
luvun `rdx:rax` ja jättää osamäärän `rax`:iin ja jakojäännöksen
`rdx`:iin. `rdx` on nollattava ennen etumerkitöntä jakoa (`xor %edx,
%edx`) tai laajennettava etumerkillä ennen etumerkillistä (`cqo`).
Jako nollalla on x86-64:llä poikkeus, joka kaataa ohjelman. RISC-V:llä
se palauttaa määritellyn arvon (osamäärä −1, jakojäännös osoittaja)
eikä kaada mitään.

## Liput

x86-64:n aritmeettiset käskyt asettavat `rflags`-rekisterin liput
tuloksen mukaan:

| Lippu | Merkitys | Tulkinta |
|-------|----------|----------|
| ZF | tulos oli nolla | yhtä suuret |
| SF | tuloksen ylin bitti | negatiivinen tulos |
| CF | kanto tai lainaus ylimmästä bitistä | etumerkitön ylivuoto |
| OF | etumerkillinen ylivuoto | tulos väärä kahden komplementtina |

Sama yhteenlasku tuottaa molemmat liput, koska bittitasolla etumerkitön
ja etumerkillinen yhteenlasku ovat sama operaatio. Tulkinnan valitsee
lippua lukeva käsky. `setc` kirjoittaa kantolipun tavuun, `seto`
ylivuotolipun:

```{.gnuassembler tiedosto="esimerkit/03-liput/x86.S" osa="lisaa"}
```

`mov` ei muuta lippuja, joten tuloksen voi tallentaa ennen lipun
lukemista. Useimmat muut käskyt muuttavat, joten lipun on oltava
lukevan käskyn välittömässä läheisyydessä.

RISC-V:ssä ei ole lippuja. Kantoluku ja ylivuoto lasketaan tuloksesta
tavallisilla käskyillä:

```{.gnuassembler tiedosto="esimerkit/03-liput/rv.S" osa="lisaa"}
```

Etumerkitön yhteenlasku vuotaa yli täsmälleen silloin, kun tulos on
pienempi kuin kumpi tahansa yhteenlaskettava, joten yksi `sltu` riittää
(*set if less than, unsigned*). Etumerkillinen ylivuoto syntyy, kun
kahden samanmerkkisen luvun summa on erimerkkinen: tuloksen etumerkki
eroaa molempien yhteenlaskettavien etumerkistä. Lippujen puute on
RISC-V:n suunnitteluvalinta: liput ovat piilotettu yhteinen tila, joka
luo riippuvuuksia käskyjen välille ja vaikeuttaa käskyjen suorittamista
eri järjestyksessä.

```{.c tiedosto="esimerkit/03-liput/main.c"}
```

```{.tuloste tiedosto="esimerkit/03-liput/odotettu"}
```

C:ssä etumerkillinen ylivuoto on määrittelemätöntä käyttäytymistä,
joten kääntäjä saa olettaa, ettei sitä tapahdu. Konekielessä ylivuoto
on täysin määritelty: tulos kiertää. Tarkistetun aritmetiikan
(`__builtin_add_overflow`, C23:n `ckd_add`) kääntäjä toteuttaa juuri
näillä käskyillä (tietokonearitmetiikasta lisää taidossa *Miten
tietokone laskee*).

## Vertailu

x86-64 vertaa käskyllä `cmp b, a`, joka laskee `a - b` vain lippuja
varten ja heittää tuloksen pois. Ehdollinen käsky lukee liput:
etumerkilliset vertailut (`setl`, `setg`, `jl`, `jg`) käyttävät SF:ää
ja OF:ää, etumerkittömät (`setb`, `seta`, `jb`, `ja`; *below*, *above*)
CF:ää. RISC-V:llä vertailu tuottaa arvon 0 tai 1 rekisteriin: `slt`
etumerkillisesti, `sltu` etumerkittömästi. Kolmitasoinen vertailu,
kuten `strcmp`:n ja lajittelun vertailufunktion paluuarvo:

```{.gnuassembler tiedosto="esimerkit/03-liput/x86.S" osa="vertaa"}
```

```{.gnuassembler tiedosto="esimerkit/03-liput/rv.S" osa="vertaa"}
```

Vertailun suunta on AT&T-syntaksissa helppo kääntää väärin:
`cmp %rsi, %rdi` vertaa `rdi`:tä `rsi`:hin, ja `setg` on tosi, kun
`rdi > rsi`. Lue käsky "vertaa rdi:tä rsi:hin" eli kohde ensin.

## Siirrot ja kertolasku vakiolla

Kertolasku kahden potenssilla on siirto vasemmalle, ja etumerkitön
jako on siirto oikealle. Etumerkillinen jako ei ole pelkkä
aritmeettinen siirto, koska siirto pyöristää kohti miinus ääretöntä,
mutta C:n jako pyöristää kohti nollaa. Siksi kääntäjä lisää ennen
siirtoa korjaustermin, ja koodissa näkyy yllättävä `shr $63` tai
`srli 63`. Kääntäjä korvaa myös jakolaskun vakiolla kertolaskulla
"maagisella" käänteisluvulla, koska jako on kertolaskua useita kertoja
hitaampi, vanhemmilla suorittimilla kymmeniä kertoja. Nämä muunnokset
tunnistaa kääntäjän koodista, ja ne selittävät, miksi `x / 10` näkyy
kertolaskuna. Luvussa 6 molemmista on kääntäjän tuottama näyte.

## Käytännössä

- **Valitse etumerkillinen tai etumerkitön vertailu tietoisesti.**
  Konekielessä tyyppiä ei ole: sama bittijono on −1 tai
  18 446 744 073 709 551 615 sen mukaan, luetaanko se `jl`:llä vai
  `jb`:llä. Väärä valinta on klassinen virhe silmukan rajoissa ja
  pituuksissa.
- **Lue lippu heti.** x86-64:llä lähes jokainen aritmeettinen käsky
  korvaa liput. Pidä lippuja asettava ja lukeva käsky vierekkäin, tai
  tallenna tulos `setcc`-käskyllä rekisteriin.
- **Nollaa `rdx` ennen jakoa.** `div` jakaa 128-bittisen luvun.
  Unohtunut `rdx` tuottaa väärän tuloksen tai kaatumisen (osamäärä ei
  mahdu).
- **Hinnat.** Yhteen-, vähennys- ja bittioperaatiot ovat yhden
  kellojakson käskyjä. Kertolasku kestää muutaman jakson. 64-bittinen
  jako kestää uusimmilla suorittimilla 10–20 jaksoa ja vanhemmilla
  kymmeniä, ja kääntäjät välttävät sitä. Konekieltä
  kirjoittaessa sama pätee: jakoa ei käytetä kuumassa silmukassa, jos
  sen voi välttää.
- **RISC-V:n "liput" ovat tavallisia rekisterejä.** Kanto ja ylivuoto
  lasketaan, kun niitä tarvitaan. Se on muutama käsky enemmän mutta
  helpompi lukea ja rinnakkaistaa.

## Itsearviointi

- Osaat kertoa x86-64:n lippujen ZF, SF, CF ja OF merkityksen ja sen,
  mitkä ehdolliset käskyt lukevat niitä.
- Osaat tunnistaa etumerkittömän ja etumerkillisen ylivuodon ja laskea
  ne RISC-V:llä ilman lippuja.
- Osaat valita oikean ehtokäskyn (`jl`/`jb`, `slt`/`sltu`)
  etumerkillisille ja etumerkittömille arvoille.
- Osaat käyttää x86-64:n `div`-käskyä oikein ja tiedät, miksi kääntäjä
  korvaa jakolaskun vakiolla kertolaskulla.

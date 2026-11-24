# Optimoinnit konekielessä

Julkaistut ohjelmat käännetään optimoiden, ja optimoitu koodi poikkeaa
lähdekoodista enemmän kuin luvun 4 esimerkit: funktioita katoaa,
silmukat muuttuvat, ja jakolaskun paikalla on kertolasku oudolla
vakiolla. Tässä luvussa sama ohjelma käännetään kolmella tasolla ja
verrataan tuloksia:

```{.bash tiedosto="esimerkit/04-optimoinnit/aja.sh" osa="kaanna"}
```

Skripti `vertaa.py` laskee kunkin funktion käskyt ja kutsut kummastakin
käännöksestä:

```{.bash tiedosto="esimerkit/04-optimoinnit/aja.sh" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t1"}
```

## Upotus

```{.c tiedosto="esimerkit/04-optimoinnit/optimoi.c" osa="upotus"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t2"}
```

`-O0`:ssa `etaisyys2` kutsuu `nelio`-funktiota kahdesti, `-O2`:ssa
kutsuja ei ole: funktio on *upotettu* (*inlined*). Pienet staattiset
funktiot, joita kutsutaan kerran tai joiden runko on lyhyt, katoavat
lähes aina, eikä niitä löydy symbolitaulustakaan. Takaisinmallinnuksessa
tämä tarkoittaa, että yksi konekielen funktio voi vastata useaa
lähdekoodin funktiota, ja sama koodinpätkä voi toistua monessa
paikassa.

## Häntäkutsut

```{.c tiedosto="esimerkit/04-optimoinnit/optimoi.c" osa="hanta"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t3"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t4"}
```

Rekursiivinen `syt` on muuttunut silmukaksi (`div` ja `jne` taaksepäin),
koska rekursiivinen kutsu on funktion viimeinen toimenpide. `ilmoita`
on pelkkä `jmp puts@plt`: *häntäkutsu* (*tail call*) hyppää funktioon
kutsumatta sitä, jolloin `puts` palaa suoraan `ilmoita`-funktion
kutsujalle. Jäljityksessä (luku 8) tämä näkyy niin, että `ilmoita` ei
koskaan palaa, ja kutsupinosta puuttuu kehys. Purussa `jmp` toiseen
funktioon tarkoittaa siis kutsua ja paluuta.

## Silmukoiden avaus ja vektorointi

```{.c tiedosto="esimerkit/04-optimoinnit/optimoi.c" osa="silmukat"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t5"}
```

Kahdeksan alkion summassa ei ole silmukkaa eikä yhtään skalaarista
yhteenlaskua. Kaksi `movdqu`-käskyä lukevat neljä 32-bittistä kokonaislukua
kerrallaan, `paddd` laskee ne pareittain yhteen, ja `psrldq` sekä
`paddd` laskevat vektorin osat yhteen (*horisontaalinen summa*). Kääntäjä
on avannut silmukan ja vektoroinut sen (*SLP-vektorointi*).

Tuntemattoman pituinen silmukka vektoroidaan GCC 14:llä vasta `-O3`:lla
(`-O2` käyttää varovaista kustannusmallia). Vektoroitu runko käsittelee
neljä alkiota kerrallaan:

```{.bash tiedosto="esimerkit/04-optimoinnit/aja.sh" osa="vektori"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t6"}
```

SSE2:ssa ei ole 32-bittistä kertolaskua neljälle alkiolle, joten
kääntäjä kertoo parilliset ja parittomat alkiot erikseen
(`pmuludq`) ja yhdistää tulokset (`pshufd`, `punpckldq`). Runkoa ympäröi
koodi, joka käsittelee loput alkiot yksi kerrallaan ja tarkistaa, onko
alkioita alle neljä. Funktio kasvaa 13 käskystä 50:een. Kun purussa
näkee pitkän funktion, jossa on `xmm`-käskyjä ja niiden perässä
skalaarinen versio samasta laskusta, kyse on lähes aina yksinkertaisesta
silmukasta.

## Jakolasku vakiolla

Jakolasku on hidas (`div` kestää kymmeniä kellojaksoja), joten
kääntäjä korvaa jakolaskun vakiolla kertolaskulla ja siirrolla:
$x / d = (x \cdot M) \gg s$, missä $M \approx 2^s / d$ on pyöristetty
ylöspäin. Kahden potenssilla jako on pelkkä siirto.

```{.c tiedosto="esimerkit/04-optimoinnit/optimoi.c" osa="jako"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t8"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t9"}
```

`jaa10`: kerroin `0x66666667`, kertolaskun ylempi puolisko ja siirto
kahdella eli kokonaissiirto 34. Etumerkillisessä jaossa tulokseen
lisätään yksi, jos `x` on negatiivinen: `sar edi,0x1f` tuottaa
negatiiviselle luvulle −1, ja `sub eax,edi` lisää yhden. Näin jako
pyöristyy kohti nollaa kuten C:ssä. Jakojäännös lasketaan
osamäärästä: `x - 10 * (x / 10)`.

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t10"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t7"}
```

Seitsemällä jaettaessa 32-bittinen kerroin ei riitä, joten kääntäjä
käyttää 33-bittistä kerrointa $2^{32} + \mathtt{0x24924925}$ ja
laskee sen ylivuodon välttävällä *lisäysmuodolla*: `t = (x * M) >> 32`,
sitten `((x - t) >> 1) + t` ja lopuksi siirto kahdella.

Jakajan voi laskea takaisin kertoimesta: $d = 2^s / M$ pyöristettynä.
Skripti `taikaluku.py` etsii purusta kertoimen ja siirrot, laskee
jakajan ja tarkistaa tuloksen vertaamalla kaavaa jakolaskuun yli
10 000 arvolla, myös rajatapauksissa:

```{.python tiedosto="esimerkit/04-optimoinnit/taikaluku.py" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/04-optimoinnit/odotettu" osa="t11"}
```

Kertoimia kannattaa muistaa muutama: `0x66666667` (10, 5, 20 siirron
mukaan), `0xcccccccd` (etumerkitön 10), `0x55555556` (3),
`0x92492493` (7) ja `0x2aaaaaab` (6). Ghidra ja IDA näyttävät
dekompiloidussa koodissa yleensä valmiiksi `x / 10`.

## Käytännössä

- **Älä odota funktiorakennetta lähdekoodista.** Upotus ja häntäkutsut
  yhdistävät ja jakavat funktioita; symbolitaulun puuttuvat funktiot on
  usein upotettu.
- **Lue `jmp` toiseen funktioon kutsuna**, joka palaa kutsujan
  kutsujalle.
- **Tunnista vektorisilmukka kokonaisuutena.** `xmm`- tai
  `ymm`-käskyt, alkulaskelma ja skalaarinen jäännössilmukka kuuluvat
  samaan lähdekoodin silmukkaan; analysoi skalaarinen versio, se on
  helpompi.
- **Muunna taikaluvut jakolaskuiksi** heti, kun näet `imul`-käskyn
  suurella vakiolla ja sitä seuraavan siirron. Laske jakaja ja
  tarkista se.
- **Vertaa optimointitasoja omalla koodilla.** Kun tiedät, miltä tuttu
  koodi näyttää `-O2`:lla, tunnistat kuviot vieraasta.

## Itsearviointi

- Osaat tunnistaa upotetut funktiot, häntäkutsut ja silmukaksi
  muutetun rekursion.
- Osaat tunnistaa avatun ja vektoroidun silmukan sekä sen
  jäännössilmukan.
- Osaat laskea jakajan kertoimesta ja siirrosta sekä selittää
  etumerkillisen jaon korjauksen.
- Osaat verrata saman ohjelman optimointitasoja skriptillä.

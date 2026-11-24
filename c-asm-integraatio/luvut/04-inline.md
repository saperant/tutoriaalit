# Inline-assembly

Erillinen assembly-tiedosto sopii kokonaisille funktioille, mutta
yksittäinen käsky ei kannata funktiokutsun hintaa. Kun C-koodin
keskelle tarvitaan käsky, jolla ei ole C-vastinetta, GCC:n
*laajennettu inline-assembly* kirjoittaa sen suoraan funktion sisään.
Kääntäjä ei ymmärrä käskyä: se kopioi tekstin kokoajalle ja luottaa
täysin siihen, mitä ohjelmoija on kertonut käskyn syötteistä,
tulosteista ja sivuvaikutuksista. Tämä luku käsittelee sitä
kertomista. Lähes kaikki inline-assemblyn virheet ovat valheita
kääntäjälle.

## Rakenne

```text
__asm__ [volatile] ("käskypohja"
                    : tulosteet
                    : syötteet
                    : sotkettavat);
```

Käskypohja on merkkijono, jossa `%0`, `%1`, … tai nimetyt `%[nimi]`
viittaavat operandeihin. Kääntäjä valitsee operandeille rekisterit
tai muistiosoitteet ja kirjoittaa ne pohjaan ennen kokoamista.
Tulosteet numeroidaan ensin, sitten syötteet. Avainsana `asm` on
GNU-laajennus, joka puuttuu tiukasta standarditilasta (`-std=c17`),
joten siirrettävässä koodissa kirjoitetaan `__asm__`. Jos käskyjä on
useita, ne erotetaan merkeillä `\n\t`, jotta kääntäjän
assembly-tulosteesta tulee luettava.

Jokainen operandi on muotoa `[nimi] "rajoite"(C-lauseke)`. Rajoite
kertoo, millainen operandi käskylle kelpaa:

| Rajoite | Merkitys | Esimerkki |
|---------|----------|-----------|
| `r` | mikä tahansa yleisrekisteri | `"r"(x)` |
| `m` | muistioperandi | `"m"(*p)` |
| `i` | käännösaikainen kokonaislukuvakio | `"i"(100)` |
| `g` | rekisteri, muisti tai vakio | harvoin hyödyllinen |
| `0`, `1`, … | sama paikka kuin numeroitu operandi | `"0"(x)` |
| `=` (etuliite) | pelkkä tuloste | `"=r"(t)` |
| `+` (etuliite) | sekä syöte että tuloste | `"+r"(x)` |
| `&` (etuliite) | kirjoitetaan ennen kuin syötteet on luettu | `"=&r"(t)` |

Lisäksi kummallakin arkkitehtuurilla on omat rajoitteensa.
x86-64:llä `a`, `b`, `c`, `d`, `S` ja `D` valitsevat rekisterin
`rax`, `rbx`, `rcx`, `rdx`, `rsi` tai `rdi`, mikä on tarpeen
käskyille, joiden operandit ovat kiinteissä rekistereissä (`cpuid`,
`mul`, `rdtsc`). RISC-V:llä `I` on 12-bittinen etumerkillinen vakio
(kelpaa `addi`-käskyyn) ja `f` liukulukurekisteri; RISC-V:n käskyt
ovat säännöllisiä, joten kiinteitä rekisterejä tarvitaan harvoin.

## Tulosteet ja syötteet

Yksinkertaisin tapaus: yksi rekisteri, joka on sekä syöte että
tuloste, ja toinen, joka on pelkkä syöte. Nimetyt operandit tekevät
pohjasta luettavan:

```{.c tiedosto="esimerkit/05-inline/main.c" osa="lisaa"}
```

`"i"`-rajoite kirjoittaa vakion käskyyn välittömänä arvona. Kääntäjä
lisää x86-64:llä `$`-merkin itse, joten sama C-lauseke kelpaa
kummallekin syntaksille:

```{.c tiedosto="esimerkit/05-inline/main.c" osa="vakio"}
```

Jos lauseke ei ole käännösaikainen vakio, käännös epäonnistuu. Jos vakio
ei mahdu käskyyn (RISC-V:n `addi` hyväksyy vain arvot −2048…2047),
virheen antaa vasta kokoaja. Tarkempi rajoite `I` siirtää tarkistuksen
kääntäjälle.

Muistioperandi annetaan rajoitteella `m`. x86-64:n käskyt voivat
käsitellä muistia suoraan, RISC-V:n eivät, joten RISC-V-versio
tarvitsee aputulosteen väliarvolle:

```{.c tiedosto="esimerkit/05-inline/main.c" osa="muisti"}
```

```{.tuloste tiedosto="esimerkit/05-inline/odotettu"}
```

Aputulosteen voisi korvata sotkettavalla rekisterillä (`: "t0"`), mutta
silloin rekisterin valitsee ohjelmoija eikä kääntäjä. Aputuloste
antaa kääntäjän valita vapaan rekisterin, ja se on yleensä parempi.

## Sotkettavat ja `volatile`

Kolmas kaksoispiste luettelee asiat, jotka käsky muuttaa, mutta jotka
eivät ole tulosteita:

- **rekisterit nimeltä**, esimerkiksi `"t0"` tai `"rcx"`: kääntäjä ei
  pidä niissä mitään asm-lauseen yli;
- **`"cc"`**: käsky muuttaa ehtolippuja. x86-64:llä GCC olettaa tämän
  aina, mutta merkintä dokumentoi aikeen ja on pakollinen joillain
  muilla arkkitehtuureilla;
- **`"memory"`**: käsky lukee tai kirjoittaa muistia, jota operandit
  eivät kuvaa. Kääntäjä kirjoittaa rekistereissä pitämänsä muuttujat
  muistiin ennen lausetta ja lukee ne uudelleen sen jälkeen. Pelkkä
  `__asm__ volatile("" ::: "memory")` on siksi *kääntäjän muistieste*:
  se estää kääntäjää siirtämästä muistioperaatioita sen yli, mutta ei
  vaikuta prosessoriin.

Kääntäjä käsittelee asm-lausetta kuin puhdasta funktiota: jos tulosteita
ei käytetä, lauseen saa poistaa, ja kahdesta samanlaisesta lauseesta
saa jättää toisen pois. `volatile` kieltää tämän. Lause, jolla ei ole
tulosteita lainkaan, on automaattisesti `volatile`.

```{.c tiedosto="esimerkit/05-inline/main.c" osa="poisto"}
```

```{.bash tiedosto="esimerkit/05-inline/tarkistus.sh" osa="kaskyt"}
```

```{.tuloste tiedosto="esimerkit/05-inline/tarkistus.odotettu"}
```

Ilman `volatile`-sanaa funktiosta jäi jäljelle vain `ret` (ja
x86-64:llä Ubuntun oletuksena päällä olevan CET-suojauksen
`endbr64`). `volatile` kuuluu käskyille, joilla on sivuvaikutus tai
joiden tulos vaihtelee kutsukerroittain: ajastimen luku (`rdtsc`,
`rdtime`), `cpuid`, laitteistorekisterit ja muistiesteet. Se ei tee
lauseesta atomista eikä estä prosessoria järjestämästä muistiosoituksia
uudelleen.

## Kaksi tavallista virhettä

Molemmat seuraavista virheistä menevät läpi ilman optimointia ja
hajottavat ohjelman `-O2`:lla. Ensimmäisessä asm-lause kirjoittaa
muistiin osoittimen kautta, mutta kertoo kääntäjälle vain, että se
lukee osoittimen arvon:

```{.c tiedosto="esimerkit/06-inline-virheet/main.c" osa="muisti"}
```

Toisessa tuloste kirjoitetaan ensimmäisellä käskyllä, ennen kuin
viimeinen syöte on luettu, mutta tulosteelta puuttuu `&`:

```{.c tiedosto="esimerkit/06-inline-virheet/main.c" osa="aikainen"}
```

```{.tuloste tiedosto="esimerkit/06-inline-virheet/odotettu"}
```

Ensimmäisessä tapauksessa kääntäjä tietää, että `x` on 1, eikä sen
mielestä mikään ole muuttanut sitä, joten se palauttaa vakion 1 ja
jättää asm-lauseen kirjoittaman arvon lukematta. `"memory"`-sotkettava
pakottaa lukemaan `x`:n uudelleen. Parempi korjaus on kuvata muisti
operandina (`"=m"(x)`), jolloin kääntäjä tietää tarkalleen, mikä
muuttui, eikä joudu hylkäämään kaikkea muuta.

Toisessa tapauksessa ilman `&`-merkkiä kääntäjä saa olettaa, että
tuloste kirjoitetaan vasta, kun kaikki syötteet on luettu, ja antaa
sille saman rekisterin kuin syötteelle `b`. Purettu koodi näyttää sen:

```{.bash tiedosto="esimerkit/06-inline-virheet/tarkistus.sh" osa="purettu"}
```

```{.tuloste tiedosto="esimerkit/06-inline-virheet/tarkistus.odotettu"}
```

Tuloste ja `b` ovat kumpikin `rdi`:ssä, joten `mov %rsi, %rdi`
ylikirjoittaa `b`:n `a`:lla. Sen jälkeen molemmat yhteenlaskut
tuplaavat saman rekisterin, ja tulos on 4. Saman ohjelman `-O0`-versio
antaa oikeat tulokset, koska ilman optimointia kääntäjä lataa
syötteet muistista eri rekistereihin, eikä virhe pääse näkyviin. Siksi
inline-assembly testataan aina samalla optimointitasolla kuin
tuotantokoodi, mieluiten useammalla.

## Muita keinoja

- **Rekisterimuuttujat.** Jos operandin pitää olla tietyssä
  rekisterissä, jolle ei ole rajoitetta (esimerkiksi RISC-V:n
  järjestelmäkutsun `a7`), käytetään paikallista rekisterimuuttujaa:
  `register long nro __asm__("a7") = 64;` ja operandina `"r"(nro)`.
  Tae on voimassa vain asm-lauseen operandina.
- **`asm goto`** saa hypätä C-nimiöön, joka luetellaan neljännen
  kaksoispisteen jälkeen. Linux käyttää sitä staattisiin haaroihin,
  joita muokataan ajon aikana.
- **Perus-asm** (`__asm__("nop")` ilman kaksoispisteitä) ei saa
  käyttää C-muuttujia eikä kertoa sivuvaikutuksista. Sitä käytetään
  vain funktioiden ulkopuolella, esimerkiksi tiedoston tasolla
  määriteltäviin symboleihin.

## Käytännössä

- **Pienin mahdollinen lause.** Vain se käsky, jolle ei ole
  C-vastinetta tai sisäistä funktiota; kaikki muu C:nä. Pitkä
  inline-assembly on vaikeampi lukea kuin erillinen `.S`-tiedosto ja
  estää optimointia (luku 7).
- **Kerro kaikki.** Jokainen kirjoitettu rekisteri on tuloste tai
  sotkettava, jokainen luettu tai kirjoitettu muistipaikka operandi tai
  `"memory"`, jokainen ennenaikaisesti kirjoitettu tuloste `&`.
  Kääntäjä ei tarkista mitään näistä.
- **Kääri lause `static inline` -funktioon**, jolla on kuvaava nimi ja
  tyypitetyt parametrit, kuten esimerkeissä. Silloin rajoitteet
  kirjoitetaan ja tarkistetaan kerran.
- **Testaa `-O2`:lla ja `-O3`:lla.** Virheelliset rajoitteet tulevat
  esiin vasta, kun optimoija alkaa uudelleenkäyttää rekistereitä ja
  poistaa lauseita.
- **Suosi sisäisiä funktioita.** Jos kääntäjällä on käskylle
  sisäinen funktio (`__rdtsc`, `_mm_pause`, `__builtin_riscv_pause`), se on aina parempi kuin inline-assembly,
  koska optimoija ymmärtää sen.

## Itsearviointi

- Osaat kirjoittaa laajennetun inline-assemblyn tulosteineen,
  syötteineen ja sotkettavineen ja käyttää nimettyjä operandeja.
- Osaat valita rajoitteen (`r`, `m`, `i`, `+r`, `=&r`, kiinteä
  rekisteri) käskyn operandien mukaan.
- Osaat selittää, mitä `"memory"`-sotkettava ja `volatile` tekevät ja
  mitä ne eivät tee.
- Osaat tunnistaa puuttuvan `"memory"`-sotkettavan ja puuttuvan
  `&`-merkin oireet ja selittää, miksi ne näkyvät vasta optimoidessa.

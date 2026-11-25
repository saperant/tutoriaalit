# Hypyt, ehdot ja silmukat

Konekielessä ei ole `if`-, `while`- eikä `for`-rakennetta. On vain
hyppykäskyjä: ehdoton hyppy (`jmp`, `j`) ja ehdollinen hyppy, joka
hyppää vain, jos ehto on tosi. Kaikki rakenteiset ohjausrakenteet
rakennetaan niistä.

## Ehdolliset hypyt

| Ehto | x86-64 (lippujen jälkeen) | RISC-V (vertaa ja hyppää) |
|------|---------------------------|---------------------------|
| yhtä suuri | `je` / `jz` | `beq a, b, kohde` |
| eri suuri | `jne` / `jnz` | `bne a, b, kohde` |
| pienempi, etumerkillinen | `jl` | `blt a, b, kohde` |
| suurempi tai yhtä suuri | `jge` | `bge a, b, kohde` |
| pienempi, etumerkitön | `jb` | `bltu a, b, kohde` |
| suurempi, etumerkitön | `ja` | `bgtu` (pseudo: `bltu b, a`) |
| nolla | `test %rax, %rax` + `je` | `beqz a0, kohde` |

x86-64 tarvitsee kaksi käskyä, vertailun (`cmp` tai `test`) ja hypyn.
RISC-V:n haarautumiskäsky vertaa kahta rekisteriä itse. `test %rax,
%rax` laskee bittitason JA-operaation itsensä kanssa vain lippuja
varten. Se on tavallisin tapa kysyä "onko rekisteri nolla".

GNU-kokoajan *paikalliset numeroidut nimiöt* helpottavat lyhyitä
silmukoita: `1:` on nimiö, ja `1b` (*backward*) viittaa lähimpään
taaksepäin olevaan nimiöön `1`, `1f` (*forward*) eteenpäin.
Samaa numeroa voi käyttää uudelleen joka funktiossa.

## Silmukka: merkkijonon pituus

`strlen` on yksinkertaisin hyödyllinen silmukka: etsi nollatavu ja
palauta etäisyys alusta.

```{.gnuassembler tiedosto="esimerkit/04-ehdot/x86.S" osa="pituus"}
```

```{.gnuassembler tiedosto="esimerkit/04-ehdot/rv.S" osa="pituus"}
```

Rakenne vastaa C:n `while`-silmukkaa: ehto testataan ennen runkoa, ja
silmukan lopussa hypätään takaisin alkuun. Kierrosta kohden on kaksi
hyppyä. Kääntäjä kääntää silmukan yleensä muotoon, jossa ehto on
lopussa (`do`-`while`), ja tarkistaa ensimmäisen kierroksen erikseen
(*loop rotation*). Silloin kierrosta kohden on vain yksi hyppy. Sen
tunnistaa luvun 6 kääntäjän koodista.

```{.c tiedosto="esimerkit/04-ehdot/main.c"}
```

```{.tuloste tiedosto="esimerkit/04-ehdot/odotettu"}
```

Tavu luetaan nollilla laajentaen (`lbu`). x86-64 vertaa muistissa
olevaa tavua suoraan vakioon (`cmpb $0, (%rax)`) ilman erillistä
latausta. Käskyn pääte `b` kertoo operandin koon, koska vakiosta ja
muistiosoitteesta kokoaja ei voi päätellä sitä.

## Ehdollinen siirto haarautumisen sijaan

Suoritin arvaa ehdollisen hypyn suunnan ennen kuin ehto on laskettu
(*branch prediction*), jotta liukuhihna pysyy täynnä. Väärä arvaus
maksaa nykysuorittimella noin 15–20 kellojaksoa. Satunnaiseen dataan
perustuvat haarat arvataan usein väärin. Silloin hypyn voi korvata
*ehdollisella siirrolla*, joka valitsee arvon ilman hyppyä:

```{.gnuassembler tiedosto="esimerkit/04-ehdot/x86.S" osa="rajaa"}
```

`cmovl` kopioi lähteen kohteeseen vain, jos ehto `l` on tosi.
Suoritettavien käskyjen virta on aina sama, joten arvattavaa ei ole.
Perus-RISC-V:ssä ehdollista siirtoa ei ole, joten rajaus tehdään
hypyillä:

```{.gnuassembler tiedosto="esimerkit/04-ehdot/rv.S" osa="rajaa"}
```

`ble` on pseudokäsky (`bge` operandit vaihdettuina). Uudemmat
laajennukset (Zicond) lisäävät RISC-V:hen ehdollisen nollauksen, jolla
saman voi tehdä ilman hyppyjä.

Ehdollinen siirto ei ole aina parempi. Se tekee molempien vaihtoehtojen
työn ja luo riippuvuuden ehdosta, kun taas hyvin arvattu hyppy on
käytännössä ilmainen. Kääntäjät valitsevat profiilin ja heuristiikan
perusteella, ja oikean valinnan voi tehdä vain mittaamalla (taito
*Suorituskyvyn analyysi ja optimointi*).

## Etumerkitön vertailu välin tarkistuksena

Kaksi vertailua voi korvata yhdellä etumerkittömällä vertailulla.
Ehto `'a' <= c && c <= 'z'` on sama kuin `(unsigned)(c - 'a') <= 25`:
jos `c` on pienempi kuin `'a'`, vähennys kiertää suureksi
etumerkittömäksi luvuksi. Tekniikka on yleinen kääntäjän koodissa ja
`switch`-lauseiden rajatarkistuksissa, ja sitä käytetään luvun 8
esimerkissä.

## Käytännössä

- **Testaa tyhjä tapaus.** Silmukka, joka testaa ehdon vasta lopussa,
  suorittaa rungon vähintään kerran. Tyhjä merkkijono, nolla-alkioinen
  taulukko ja `n <= 0` tarkistetaan ennen silmukkaa (luvun 2
  `varaston_arvo`).
- **Laskuri vai loppuosoitin.** Silmukan voi ohjata laskurilla tai
  vertaamalla osoitinta loppuosoitteeseen. Osoitinmuoto säästää
  rekisterin ja käskyn ja on kääntäjien suosima (luku 6).
- **Haarojen hinta.** Väärin arvattu hyppy on kallis, oikein arvattu
  lähes ilmainen. Ehdollinen siirto kannattaa ennalta arvaamattomassa
  datassa, ei pitkän laskennan valinnassa.
- **Numeroidut nimiöt lyhyisiin hyppyihin.** Merkitsevät nimet
  (`.Lsilmukka`) kannattavat pidemmissä funktioissa. `.L`-alkuiset
  nimet ovat paikallisia eivätkä näy symbolitaulussa.
- **Kommentoi ehto, ei käskyä.** `jle 3f  # t[j-1] <= x: paikka
  löytyi` kertoo enemmän kuin `jle 3f  # hyppää jos pienempi tai yhtä`.

## Itsearviointi

- Osaat kirjoittaa `if`-, `while`- ja `for`-rakenteen
  ehdollisilla hypyillä kummallakin käskykannalla.
- Osaat valita oikean ehdollisen hypyn etumerkillisille ja
  etumerkittömille vertailuille.
- Osaat selittää haarautumisen ennustuksen hinnan ja milloin
  ehdollinen siirto (`cmov`) kannattaa.
- Osaat tarkistaa arvon välille yhdellä etumerkittömällä vertailulla.

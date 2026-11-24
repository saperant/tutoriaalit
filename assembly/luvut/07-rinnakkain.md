# x86-64 ja RISC-V rinnakkain

Edellisissä luvuissa käskykantoja on käytetty rinnakkain. Tässä luvussa
verrataan niitä saman algoritmin avulla ja kootaan erot. Ne
selittävät, miksi konekieli näyttää kummallakin erilaiselta ja miksi
suunnittelijat ovat valinneet eri tavoin.

## Sama algoritmi kahdesti

Lisäyslajittelu on lajittelualgoritmien sisäsilmukka: pienet
taulukot lajitellaan sillä, ja monet nopeammat algoritmit (esimerkiksi
introsort) vaihtavat siihen, kun osa on tarpeeksi pieni.

```{.gnuassembler tiedosto="esimerkit/08-rinnakkain/x86.S" osa="lajittele"}
```

```{.gnuassembler tiedosto="esimerkit/08-rinnakkain/rv.S" osa="lajittele"}
```

```{.c tiedosto="esimerkit/08-rinnakkain/main.c"}
```

x86-64:llä:

```{.tuloste tiedosto="esimerkit/08-rinnakkain/odotettu-x86"}
```

RISC-V:llä:

```{.tuloste tiedosto="esimerkit/08-rinnakkain/odotettu-rv"}
```

Funktion koko lasketaan symbolien `lajittele_loppu` ja `lajittele`
osoitteiden erotuksena. x86-64-versio on 17 käskyä ja 51 tavua,
RISC-V-versio 15 käskyä ja 46 tavua, kun kokoaja on käyttänyt
tiivistettyjä käskyjä. Ilman C-laajennusta RISC-V-versio olisi
60 tavua. Käskymäärä on lähes sama, vaikka x86-64:n muistiosoite on
yhden käskyn sisällä (`mov -8(%rdi,%rdx,8), %r8`) ja RISC-V laskee
osoitteen erikseen. RISC-V-versio kompensoi käyttämällä osoitinta
indeksin sijaan, jolloin silmukassa ei tarvita kertolaskua. Sama
muunnos, joka kääntäjältä nähtiin luvussa 6.

## Erot koottuna

| Ominaisuus | x86-64 | RISC-V |
|----------------------|------------------------------|------------------------------|
| Tyyppi | CISC | RISC, lataus–tallennus-arkkitehtuuri |
| Käskyn pituus | 1–15 tavua | 4 tavua (C-laajennuksella 2) |
| Operandit | kaksi, kohde on myös lähde | kolme |
| Muisti laskukäskyissä | kyllä (`add (%rdi), %rax`) | ei, vain `l*`/`s*` |
| Osoitusmuodot | `siirtymä(kanta, indeksi, kerroin)`, RIP-suhteellinen | `siirtymä(kanta)` |
| Yleisrekisterit | 16 | 31 + nolla |
| Liput | kyllä | ei, vertailu tuottaa arvon |
| Paluuosoite | pinossa | rekisterissä `ra` |
| Laajennukset | historiallisesti kertyneet (x87, MMX, SSE, AVX …) | modulaariset: I, M, A, F, D, C, V … |
| Muistimalli | vahva (TSO) | heikko (RVWMO), `fence`-käskyt |

**Käskyjen pituus.** Vaihteleva pituus tekee x86-64-koodista
tiivistä, mutta suorittimen on purettava käskyjen rajat ennen
rinnakkaista purkua. Nykyiset x86-64-suorittimet muuntavat käskyt
sisäisiksi RISC-tyyppisiksi mikro-operaatioiksi ja tallentavat ne
välimuistiin. RISC-V:n kiinteät 32-bittiset käskyt ovat helppoja purkaa,
ja C-laajennus palauttaa suuren osan koodin tiiviydestä.

**Rekisterien määrä.** 31 yleisrekisteriä riittää useimmiten pitämään
kaikki silmukan muuttujat rekistereissä. x86-64:n 16 rekisteriä
loppuvat nopeammin, jolloin kääntäjä joutuu tallentamaan arvoja pinoon
(*spill*). Toisaalta x86-64 voi käyttää muistioperandia suoraan, mikä
lieventää haittaa.

**Muistimalli.** x86-64 takaa, että muut ytimet näkevät yhden ytimen
kirjoitukset kirjoitusjärjestyksessä (*total store order*). RISC-V
sallii suorittimen järjestää muistioperaatioita uudelleen, ja
järjestys pakotetaan erikseen `fence`-käskyillä tai atomisten käskyjen
järjestysbiteillä. Tällä on merkitystä vasta rinnakkaisessa koodissa:
x86-64:llä toimiva, ilman atomisia operaatioita kirjoitettu rinnakkainen
koodi voi rikkoutua RISC-V:llä tai ARMilla (taito
*Rinnakkaisohjelmointi*).

**Laajennukset.** x86-64:n käskykanta on kerrostunut neljässä
vuosikymmenessä, ja jokaisen ohjelman on tarkistettava ajossa, mitkä
laajennukset suoritin tukee (luvun 9 `cpu_supports`). RISC-V määrittelee
pienen pakollisen ytimen (RV64I) ja nimetyt laajennukset. Tavallinen
Linux-järjestelmä käyttää profiilia RV64GC: I + M (kerto- ja jako) +
A (atomiset) + F ja D (liukuluvut) + C (tiivistetyt) sekä Zicsr ja
Zifencei.

## Kumpi on parempi?

Käskykanta ei yksin ratkaise suorituskykyä. Suorituskyky syntyy
mikroarkkitehtuurissa: kuinka monta käskyä suoritin purkaa ja
suorittaa kellojaksossa, kuinka hyvin se ennustaa hypyt ja kuinka
suuret ja nopeat välimuistit ovat. x86-64:n monimutkaisuus maksaa
piipinta-alaa ja tehoa purkuvaiheessa, ja RISC-V:n yksinkertaisuus
helpottaa toteutusta erityisesti pienissä suorittimissa. Molemmilla
voi tehdä nopeita suorittimia. Ohjelmoijalle tärkeämpää on osata lukea
kumpaakin ja tunnistaa, mikä koodissa on käskykannan ja mikä
algoritmin ominaisuus.

## Käytännössä

- **Kirjoita algoritmi ensin C:llä.** Sama C-viitetoteutus testaa
  molemmat assembly-versiot (luku 10). Arkkitehtuurikohtainen koodi on
  helppo pitää oikeana, kun vertailukohta on yhteinen.
- **Valitse osoitin- tai indeksimuoto käskykannan mukaan.** x86-64:n
  skaalattu indeksi tekee indeksistä halvan, RISC-V:llä osoitin säästää
  käskyjä.
- **Mittaa koko ja käskymäärä, älä arvaa.** `objdump -d`, `size` ja
  symbolien erotus kertovat koodin koon. Suorituskyvyn ratkaisee vasta
  mittaus oikealla suorittimella.
- **Rinnakkainen koodi heikolla muistimallilla.** Koodi, joka
  "toimii x86:lla", ei todista mitään RISC-V:n tai ARMin käytöksestä.
  Käytä kielen atomisia operaatioita, älä oletuksia laitteistosta.

## Itsearviointi

- Osaat kirjoittaa saman algoritmin x86-64:llä ja RISC-V:llä ja
  testata molemmat samalla C-pääohjelmalla.
- Osaat luetella CISC- ja RISC-käskykantojen keskeiset erot ja
  perustella niiden seuraukset.
- Osaat mitata funktion koodin koon ja käskymäärän.
- Osaat selittää, mitä muistimallien ero (TSO ja RVWMO) tarkoittaa
  rinnakkaiselle koodille.

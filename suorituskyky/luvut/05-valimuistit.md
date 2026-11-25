# Välimuistit käytännössä

Tietokonearkkitehtuurin tutoriaali rakensi välimuistin simulaattorissa:
osoite jaetaan tunnisteeseen, joukkoon ja siirtymään, hutit jaetaan
pakollisiin, kapasiteetti- ja konfliktihuteihin, ja silmukoiden
järjestys ratkaisee hutien määrän. Tässä luvussa samat asiat mitataan
oikealla suorittimella. Ohjelmoijan kannalta muistihierarkiasta
riittää muistaa kolme asiaa: data siirtyy 64 tavun riveinä, lähellä
oleva on nopeaa ja kaukana oleva hidasta, ja peräkkäinen läpikäynti
on paljon nopeampaa kuin hyppivä, koska suoritin osaa hakea seuraavat
rivit etukäteen.

## Riveittäin vai sarakkeittain

C tallentaa kaksiulotteisen taulukon riveittäin: alkio $(i, j)$ on
kohdassa $i \cdot n + j$. Saman summan voi laskea kahdessa
järjestyksessä:

```{.c tiedosto="esimerkit/05-lapikaynti.c" osa="summat"}
```

Riveittäin kulkeva silmukka lukee peräkkäisiä osoitteita, joten yksi
64 tavun rivi palvelee kahdeksaa double-lukua. Sarakkeittain kulkeva
silmukka hyppää joka kerta $8n$ tavua eteenpäin, joten jokainen luku
on eri rivillä. Kun matriisi ei mahdu välimuistiin, rivi on poistunut
ennen kuin sen seuraavaa lukua tarvitaan. Cachegrind simuloi 32 KiB
L1-välimuistin ja laskee hudit:

```{.makefile tiedosto="esimerkit/Makefile" osa="cachegrind"}
```

```{.makefile tiedosto="esimerkit/Makefile" osa="valimuisti"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-lapikaynti.txt"}
```

Miljoonan alkion matriisi tuottaa riveittäin $2^{20}/8 = 131\,072$
L1-hutia, eli tasan yhden jokaista riviä kohden, ja sarakkeittain
$2^{20}$ hutia, yhden jokaista lukua kohden. Simuloidut luvut ovat
samat joka ajolla, joten Makefile tarkistaa, että suhde on vähintään 4.
Sarakkeittainen versio suorittaa myös enemmän käskyjä, koska
osoitteen laskenta ei sievene. Ajassa ero näyttää tältä:

```{.tuloste tiedosto="esimerkit/tulokset/05-lapikaynti.txt"}
```

Kun matriisi mahtuu L2-välimuistiin (512 KiB), ero on pieni. Kun se on
muistissa (128 MiB), sarakkeittainen läpikäynti on noin kymmenen
kertaa hitaampi. Sama koskee kaikkia moniulotteisia rakenteita:
kuvan pikselit, taulukkolaskennan solut ja tietokannan rivit. Sisin
silmukka kulkee aina sitä indeksiä pitkin, joka vaihtuu muistissa
nopeimmin.

## Välimuistirivi

Rivin koon voi mitata. Seuraava silmukka kertoo joka $k$:nnen alkion
kolmella:

```{.c tiedosto="esimerkit/05-askel.c" osa="paivita"}
```

Kun $k$ kasvaa yhdestä kuuteentoista, laskentaa on 16 kertaa vähemmän,
mutta jokainen 64 tavun rivi on yhä luettava ja kirjoitettava, koska
jokaisella rivillä on ainakin yksi päivitettävä alkio. Kun $k$ ylittää
16 (64 tavua neljän tavun lukuina), joka toinen rivi jää koskematta,
ja aika puolittuu jokaisella kaksinkertaistuksella:

```{.tuloste tiedosto="esimerkit/tulokset/05-askel.txt"}
```

![Kierroksen aika askeleen funktiona (sama data kuin tulosteessa).
Katkoviiva näyttää, miten aika laskisi, jos se riippuisi vain
päivitysten määrästä. Askeleeseen 16 asti jokainen rivi on yhä
haettava muistista.](kuvat/askel.png){width=76%}

Askeleilla 1–16 aika laskee vain noin puoleen, vaikka työ vähenee
kuudestoistaosaan: ohjelma on muistirajoitteinen, ja muistista
siirretty data on sama. Askeleesta 16 alkaen aika puolittuu jokaisella
kaksinkertaistuksella, kunnes taulukko on niin harva, että
TLB-hudit ja sivujen rajat alkavat näkyä. Luvuista voi päätellä rivin
koon ilman dokumentaatiota.

## Viive työjoukon koon mukaan

Peräkkäinen läpikäynti piilottaa viiveen, koska suoritin hakee rivit
etukäteen ja pitää monta latausta käynnissä yhtä aikaa. Viiveen
mittaamiseen tarvitaan lataukset, jotka riippuvat toisistaan:
*osoitinjahti*, jossa seuraavan solmun osoite luetaan edellisestä.

```{.c tiedosto="esimerkit/05-latenssi.c" osa="solmu"}
```

Solmut kytketään satunnaiseksi sykliksi, jotta esihaku ei osaa
arvata seuraavaa osoitetta:

```{.c tiedosto="esimerkit/05-latenssi.c" osa="sattolo"}
```

```{.c tiedosto="esimerkit/05-latenssi.c" osa="jahti"}
```

Toiminnallinen testi varmistaa, että sykli todella kattaa kaikki
solmut. Muuten jahti voisi kiertää pientä silmukkaa välimuistissa ja
antaa liian hyvän tuloksen.

```{.tuloste tiedosto="esimerkit/05-latenssi.odotettu"}
```

Kun työjoukon kokoa kasvatetaan, viive nousee portaittain:

```{.tuloste tiedosto="esimerkit/tulokset/05-latenssi.txt"}
```

![Latauksen viive työjoukon koon funktiona (sama data kuin
tulosteessa). Pystyviivat ovat kirjoittajan koneen L1- ja
L2-välimuistin koot.](kuvat/latenssi.png){width=76%}

16 KiB mahtuu L1-välimuistiin, ja lataus kestää alle kaksi
nanosekuntia eli noin neljä jaksoa. 64 KiB–1 MiB on L2:ssa
(noin 10–20 ns), muutama megatavu jaetussa L3:ssa ja kymmenet
megatavut keskusmuistissa (150–200 ns). Viimeisen rivin pienempi luku
ei ole uusi porras vaan mittauksen vaihtelua: jaetulla koneella
keskusmuistin viive muuttuu ajosta toiseen kymmeniä prosentteja muun
kuorman ja sivujen sijoittelun mukaan. Muistihuti maksaa siis
satoja jaksoja, joiden aikana suoritin voisi tehdä tuhat käskyä.
Satunnainen saanti suureen tietorakenteeseen, kuten linkitettyyn
listaan, hajautustauluun tai puuhun, maksaa tämän hinnan jokaisella
askeleella.

Portaiden paikat kertovat välimuistien todelliset koot. Pilvessä
virtuaalikoneen ilmoittama L3-koko (tässä 260 MiB) on usein koko
fyysisen suorittimen jaettu välimuisti, josta yksi virtuaalikone saa
vain osan; mittaus kertoo, mitä todella on käytettävissä.

## Esihaku ja TLB

Suorittimen *esihakija* (engl. prefetcher) tunnistaa peräkkäiset ja
vakioaskeleiset saantijonot ja hakee rivejä ennen kuin niitä
pyydetään. Siksi riveittäinen läpikäynti saavuttaa lähes
muistiväylän kaistan, vaikka jokainen rivi tulee muistista. Esihaku ei
auta, kun osoitteet riippuvat datasta, kuten osoitinjahdissa.
`__builtin_prefetch` antaa ohjelmoijalle tavan pyytää riviä etukäteen,
mutta siitä on hyötyä vain, kun osoite tiedetään hyvissä ajoin ja
esihakija ei sitä itse arvaa.

TLB (engl. translation lookaside buffer) on virtuaaliosoitteiden
muunnosten välimuisti. Sillä on vain muutamia satoja tai tuhansia
paikkoja, joten 4 KiB:n sivuilla se kattaa muutaman megatavun. Kun
satunnainen saanti hajoaa satoihin megatavuihin, jokainen lataus voi
vaatia myös sivutaulun kävelyn. Suuret sivut (2 MiB, Linuxissa
*transparent huge pages* tai `madvise(MADV_HUGEPAGE)`) kasvattavat
TLB:n kattavuuden 512-kertaiseksi.

## Käytännössä

- **Kulje muistissa peräkkäin.** Sisin silmukka käy läpi sen indeksin,
  joka on muistissa vierekkäin.
- **Mittaa yksiköissä rivi ja sivu.** 64 tavua ja 4 KiB ovat ne määrät,
  joita laitteisto siirtää ja kääntää kerralla.
- **Pienennä työjoukkoa.** Mitä pienempi data, sitä ylemmällä
  välimuistitasolla se pysyy: pienemmät tyypit, tiiviit rakenteet ja
  vain tarvittavat kentät.
- **Vältä osoitinjahtia kuumilla poluilla.** Taulukko voittaa
  linkitetyn listan lähes aina, vaikka lisäys keskelle olisi
  teoriassa kalliimpaa.
- **Älä luota mikrovertailuun, jonka data mahtuu L1:een**, jos
  todellinen data ei mahdu.

## Itsearviointi

- Osaat selittää, miksi sarakkeittainen läpikäynti on hidas, ja laskea
  hutien määrän rivikoon avulla.
- Osaat simuloida välimuistin Cachegrindilla ja lukea sen tulosteesta
  L1- ja viimeisen tason hudit.
- Osaat mitata välimuistirivin koon ja välimuistitasojen viiveet ja
  selittää, miksi viiveen mittaus vaatii riippuvat lataukset.
- Osaat kertoa, milloin esihaku auttaa ja milloin ei, ja miten suuret
  sivut vaikuttavat TLB:hen.

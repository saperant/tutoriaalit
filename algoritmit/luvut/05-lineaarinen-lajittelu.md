# Alaraja ja lineaarinen lajittelu

Kaikki edellisten lukujen nopeat lajittelut ovat $\Theta(n \log n)$.
Onko se sattumaa, vai voisiko joku keksiä nopeamman? Vastaus riippuu
siitä, mitä algoritmi saa tehdä avaimille. Jos se saa vain verrata
kahta avainta keskenään, $n \log n$ on ehdoton raja. Jos avaimet ovat
pieniä kokonaislukuja tai tavujonoja, niitä voi käyttää taulukon
indekseinä, ja lajittelu onnistuu lineaarisessa ajassa.

## Vertailulajittelun alaraja

Vertailulajittelu saa tietoa syötteestä vain vertailuista
$a_i < a_j$. Sen toiminnan voi kuvata *päätöspuuna*: jokainen sisäsolmu
on vertailu, kaksi haaraa ovat sen tulokset, ja jokainen lehti on
yksi lopullinen järjestys. Jotta algoritmi lajittelisi jokaisen
syötteen oikein, puussa on oltava lehti jokaiselle $n!$ järjestykselle.
Binääripuussa, jonka korkeus on $h$, on enintään $2^h$ lehteä, joten

$$h \ge \log_2 n! = n \log_2 n - n \log_2 e + O(\log n)
\approx n \log_2 n - 1{,}44\,n.$$

Puun korkeus on pahimman tapauksen vertailujen määrä. Arvio seuraa
Stirlingin kaavasta, mutta raja on helppo laskea myös suoraan:
$\log_2 n! = \ln \Gamma(n + 1) / \ln 2$.

```{.c tiedosto="esimerkit/05-alaraja.c"}
```

```{.tuloste tiedosto="esimerkit/05-alaraja.odotettu"}
```

Luvun 2 mittauksessa lomituslajittelu teki 1000 alkiolla 8704 vertailua,
kun alaraja on 8530. Lomituslajittelu on siis vain kahden prosentin
päässä optimista. Sama päättely antaa alarajan myös keskimääräiselle
tapaukselle: lehtien keskimääräinen syvyys on vähintään
$\log_2 n!$.

Alaraja koskee kaikkia vertailuihin perustuvia algoritmeja, myös niitä,
joita ei ole vielä keksitty. Se on Ω-tulos, ja se kertoo, milloin
optimointi kannattaa lopettaa: vertailulajittelua ei voi parantaa
asymptoottisesti, vain vakiokertoimilla.

## Laskemislajittelu

Jos avaimet ovat kokonaislukuja välillä $0 \ldots k - 1$, ne voi laskea.
Kurssin koepisteet ovat välillä 0–60, ja jokaisella tuloksella on
opiskelijanumero. Laskemislajittelu laskee kunkin pistemäärän
esiintymät, muuttaa ne *etuliitesummiksi* eli kunkin pistemäärän
ensimmäiseksi paikaksi tuloksessa ja sijoittaa alkiot paikoilleen:

```{.c tiedosto="esimerkit/05-laskeminen.c" osa="laskeminen"}
```

Työtä on $\Theta(n + k)$: yksi kierros syötteen yli laskentaan, yksi
laskuritaulukon yli ja yksi sijoitukseen. Yhtään vertailua ei tehdä,
joten alaraja ei koske tätä algoritmia. Sijoitus käy syötteen läpi
alusta loppuun ja kasvattaa paikkaa joka alkion jälkeen, joten yhtä
suuret avaimet säilyttävät järjestyksensä: lajittelu on vakaa.
Tulosteen ensimmäisellä rivillä 42 pisteen opiskelijat 1, 3 ja 8 ovat
alkuperäisessä järjestyksessään.

```{.tuloste tiedosto="esimerkit/05-laskeminen.odotettu"}
```

Laskemislajittelu kannattaa, kun $k$ on enintään samaa
suuruusluokkaa kuin $n$. Kun avaimet ovat 32-bittisiä, $k = 2^{32}$, ja
laskuritaulukko veisi 16 gigatavua.

## Kantalukulajittelu

Kantalukulajittelu (engl. radix sort) lajittelee suuret avaimet osissa.
32-bittinen avain on neljä tavua, ja jokainen tavu on laskemislajittelulle
sopiva avain, $k = 256$. LSD-versio (engl. least significant digit)
lajittelee ensin vähiten merkitsevän tavun mukaan, sitten seuraavan ja
viimeisenä eniten merkitsevän:

```{.c tiedosto="esimerkit/05-laskeminen.c" osa="kantaluku"}
```

Oikeellisuus perustuu vakauteen. Kierroksen $d$ jälkeen taulukko on
järjestyksessä $d$ alimman tavun mukaan: kierros järjestää uuden tavun
mukaan, ja vakaus säilyttää yhtä suurten tavujen kesken edellisten
kierrosten järjestyksen. Neljän kierroksen jälkeen koko avain on
järjestyksessä. Työtä on $\Theta(4(n + 256))$ eli lineaarisesti, ja
lisämuistia tarvitaan $n$ alkion aputaulukko. Esimerkki vertaa tulosta
`qsort`-funktion tulokseen 100 000 satunnaisella avaimella.

Kantalukulajittelu sopii kiinteänmittaisille avaimille: kokonaisluvuille,
IP-osoitteille ja päivämäärille. Etumerkilliset luvut käsitellään
kääntämällä etumerkkibitti, ja liukuluvut sopivalla bittimuunnoksella.
Vaihtelevan mittaisille merkkijonoille sopii paremmin MSD-versio, joka
aloittaa eniten merkitsevästä merkistä ja jakaa taulukon lohkoihin.

## Mittaus kellolla

Lineaarinen algoritmi ei ole automaattisesti nopeampi. Kantalukulajittelu
käy datan läpi kahdeksan kertaa ja kirjoittaa hajanaisiin kohtiin, kun
pikalajittelu käy välimuistissa olevia osataulukkoja läpi peräkkäin.
Ainoa tapa tietää on mitata. Mittaus on erillinen ohjelma, joka
käännetään optimoinneilla (`-O2`) ilman sanitoijia, koska ne
vääristäisivät algoritmien välisiä eroja:

```{.c tiedosto="esimerkit/mittaus/src/aika.c" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/mittaus/aika.odotettu"}
```

Ohjelma tulostaa vain vertailujen tulokset väljillä rajoilla, jotta
testi ei ole herkkä koneen kuormalle. Todelliset erot ovat
suurempia: kirjoittajan koneella 40 000 alkiolla lisäyslajittelu oli
noin 50 kertaa hitaampi kuin lomituslajittelu, ja neljällä miljoonalla
avaimella kantalukulajittelu oli noin 10 kertaa nopeampi kuin `qsort`,
joka kutsuu vertailijaa funktio-osoittimen kautta jokaisella
vertailulla. Mittauksen ajaa komento `make -C esimerkit`.

## Käytännössä

- **$n \log n$ on raja vain vertailuille.** Jos avaimet ovat pieniä
  kokonaislukuja tai kiinteänmittaisia, laskemis- tai
  kantalukulajittelu voi olla moninkertaisesti nopeampi.
- **Vakaus tekee monivaiheisen lajittelun mahdolliseksi.**
  Kantalukulajittelu on yhtä kuin vakaa lajittelu numero kerrallaan.
- **Mittaa todellisella datalla.** Asymptoottisesti parempi algoritmi
  voi hävitä välimuistille ja vakiokertoimille.

## Itsearviointi

- Osaat johtaa vertailulajittelun alarajan $\log_2 n!$ päätöspuusta ja
  selittää, miksi se ei koske laskemislajittelua.
- Osaat kirjoittaa vakaan laskemislajittelun etuliitesummilla.
- Osaat kirjoittaa LSD-kantalukulajittelun ja perustella sen
  oikeellisuuden vakaudella.

# Datan asettelu ja lohkominen

Edellinen luku muutti läpikäynnin järjestystä. Tämä luku muuttaa
datan järjestystä: miten kentät sijoitetaan rakenteisiin ja
taulukoihin, jotta jokainen muistista haettu rivi käytetään
mahdollisimman tarkasti, ja miten laskenta pilkotaan paloiksi, jotka
mahtuvat välimuistiin.

## Rakenteiden taulukko ja taulukoiden rakenne

Hiukkassimulaatiossa jokaisella hiukkasella on paikka, nopeus, massa,
varaus ja muita tietoja. Luonteva esitys on rakenteiden taulukko (engl.
*array of structures*, AoS):

```{.c tiedosto="esimerkit/06-hiukkaset.c" osa="aos"}
```

Paikan päivitys tarvitsee vain kentät `x` ja `vx`, eli 16 tavua 80:stä.
Muistista haetaan kuitenkin kokonaisia rivejä, joten neljä viidesosaa
siirretystä datasta on turhaa. Taulukoiden rakenne (engl. *structure of
arrays*, SoA) tallentaa jokaisen kentän omaan taulukkoonsa:

```{.c tiedosto="esimerkit/06-hiukkaset.c" osa="soa"}
```

Nyt jokainen haettu rivi sisältää kahdeksan peräkkäistä
`x`-koordinaattia tai nopeutta, ja kaikki niistä käytetään. Testi
päivittää molemmat esitykset kahdeksan kertaa ja vertaa paikat:

```{.c tiedosto="esimerkit/06-hiukkaset.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/06-hiukkaset.odotettu"}
```

Cachegrindin mukaan molemmat versiot suorittavat yhtä monta käskyä ja
latausta, mutta AoS tekee viisi kertaa enemmän L1-hutia:
$100\,000 \cdot 80 / 64 = 125\,000$ riviä päivitystä kohden, kun SoA
koskee vain $100\,000 \cdot 16 / 64 = 25\,000$ riviin.

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-hiukkaset.txt"}
```

```{.tuloste tiedosto="esimerkit/tulokset/06-hiukkaset.txt"}
```

Ajoissa ero on vielä suurempi, koska SoA-silmukka myös vektoroituu:
peräkkäiset `x[i]`-luvut voi ladata yhdellä vektorikäskyllä, AoS:n
luvut eivät ole vierekkäin. SoA on pelimoottoreiden
entiteettijärjestelmien, sarakepohjaisten tietokantojen (Parquet,
DuckDB) ja numeeristen kirjastojen perusta. Se ei ole aina parempi:
jos jokainen käsittely tarvitsee kaikki kentät, AoS pitää yhden
olion tiedot samalla rivillä. Välimuoto *AoSoA* tallentaa esimerkiksi
kahdeksan hiukkasen paketteja, joiden sisällä kentät ovat taulukoina.

## Rakenteen täyte

Kääntäjä sijoittaa kentät niiden tasausvaatimusten mukaisiin osoitteisiin:
`double` kahdeksalla ja `int` neljällä jaollisiin. Kenttien väliin jää
täytettä (engl. padding), jonka määrä riippuu järjestyksestä:

```{.c tiedosto="esimerkit/06-asettelu.c" osa="tayte"}
```

```{.c tiedosto="esimerkit/06-asettelu.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/06-asettelu.odotettu"}
```

`Huono` vie 24 tavua, koska `char tyyppi` jättää seitsemän tavun
aukon ennen kenttää `arvo`. Kun kentät järjestetään suurimmasta
pienimpään, sama sisältö mahtuu 16 tavuun, ja miljoonan alkion taulukko
pienenee 8 megatavua. Työkalu `pahole` näyttää rakenteiden aukot
debug-tiedoista. Muuta järjestystä vain, kun rakennetta on paljon:
yksittäisen rakenteen kenttäjärjestys kannattaa valita
luettavuuden mukaan.

## Väärä jakaminen

Monisäikeisessä ohjelmassa rivin koko vaikuttaa toisellakin tavalla.
Välimuistin koherenssi pitää kirjaa riveistä, ei muuttujista (taito
*Tietokonearkkitehtuuri*). Jos kaksi säiettä kirjoittaa kahteen
eri muuttujaan samalla rivillä, rivi siirtyy ytimeltä toiselle jokaisen
kirjoituksen jälkeen, vaikka säikeet eivät jaa dataa:

```{.c tiedosto="esimerkit/06-asettelu.c" osa="jakaminen"}
```

`alignas(64)` sijoittaa kummankin laskurin omalle rivilleen, kuten
testin tuloste yllä näyttää (`b @64`). Hinta on tila: 16 tavun rakenne
kasvaa 128 tavuun. C++17:n `std::hardware_destructive_interference_size`
kertoo rivin koon kääntäjän tietämänä.

Esimerkin mittaustilassa kaksi säiettä kasvattaa kumpikin omaa
laskuriaan 50 miljoonaa kertaa. Fyysisillä koneilla väärä jakaminen
hidastaa tällaista silmukkaa tyypillisesti moninkertaisesti.
Kirjoittajan virtuaalikoneessa ero jäi pieneksi: kuormittamattomalla
koneella eri riveille sijoitettu versio oli toistetuissa ajoissa
1,0–1,3 kertaa niin nopea kuin vierekkäinen, ja kuormitetulla koneella
vaihteluväli oli vielä laajempi. Yksi ajo näytti tältä:

```{.tuloste tiedosto="esimerkit/tulokset/06-asettelu.txt"}
```

Tulos on opettavainen sinänsä. Silmukan kirjoitus on tavallinen
`add`-käsky. Todennäköinen selitys pienelle erolle on, että suoritin
jättää tällaiset kirjoitukset kirjoituspuskuriinsa, lukee uuden arvon
sieltä ja purkaa monta kirjoitusta kerralla aina, kun rivi on sen
hallussa: rivi kulkee ytimeltä toiselle, mutta harvoin suhteessa
kirjoitusten määrään. Kun sama koe tehdään atomisilla laskureilla,
joiden jokainen kasvatus vaatii rivin yksinomistuksen, sama kone
näyttää kahdella säikeellä noin kymmenkertaisen ja neljällä yli
kaksikymmenkertaisen eron (taito *Rinnakkaisohjelmointi*, jonka aihe
rinnakkaisuus kokonaisuudessaan on). Väärän jakamisen hinta riippuu
siis siitä, millaisia kirjoitukset ovat, eikä sitä voi päätellä
mittaamatta.

## Matriisitulo

Matriisitulo $C = AB$ on roofline-mallin laskentarajoitteinen
esimerkki: $2n^3$ operaatiota $3n^2$ luvulle. Suoraviivainen
toteutus ei kuitenkaan pääse lähellekään kattoa:

```{.c tiedosto="esimerkit/06-matriisitulo.c" osa="ijk"}
```

Sisin silmukka kulkee $B$:tä sarakkeittain, joten jokainen $B$:n luku
on eri rivillä, kuten edellisen luvun sarakkeittaisessa summassa.
Silmukoiden järjestyksen vaihtaminen muotoon $i, k, j$ tekee
sisimmästä silmukasta riveittäisen sekä $B$:lle että $C$:lle:

```{.c tiedosto="esimerkit/06-matriisitulo.c" osa="ikj"}
```

Järjestys ikj käy kuitenkin koko $B$:n läpi jokaista $i$:n arvoa
kohden. Kun $B$ ei mahdu välimuistiin, se luetaan muistista $n$
kertaa. *Lohkominen* (engl. tiling, blocking) jakaa $k$- ja
$j$-silmukat paloiksi, joiden $B$:n osa mahtuu välimuistiin, ja käyttää
samaa palaa kaikilla $i$:n arvoilla ennen siirtymistä seuraavaan:

```{.c tiedosto="esimerkit/06-matriisitulo.c" osa="lohkottu"}
```

Kaikki kolme toteutusta lasketaan pienillä kokonaisluvuilla, joten
tulokset ovat bitilleen samat järjestyksestä riippumatta, ja testi
vertaa ne `memcmp`-funktiolla. Testin $n = 200$ ei ole lohkon
monikerta, joten myös reunapalat testataan.

```{.tuloste tiedosto="esimerkit/06-matriisitulo.odotettu"}
```

Cachegrind simuloi pientä 256 KiB viimeisen tason välimuistia, johon
$256 \times 256$ -matriisi (512 KiB) ei mahdu:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-matriisitulo.txt"}
```

Järjestys ikj vähentää L1-hutia kahdeksasosaan. Lohkominen ei juuri
muuta L1-hutien määrää, mutta vähentää viimeisen tason hutia eli
muistiliikennettä noin 25-kertaisesti. Ajoissa kirjoittajan koneella:

```{.tuloste tiedosto="esimerkit/tulokset/06-matriisitulo.txt"}
```

Silmukoiden järjestys toi noin viisinkertaisen nopeuden. Lohkominen
ei tuonut lisää: toistetuissa ajoissa lohkottu versio oli 15–20 %
ikj-järjestystä hitaampi. Syy näkyy roofline-mallista: skalaarikoodi
on laskentarajoitteinen jo ikj-järjestyksessä, koska tämän koneen
2 MiB:n L2-välimuisti ja esihaku syöttävät riveittäistä dataa
riittävän nopeasti, ja lohkojen lisäsilmukat ovat silloin pelkkää
lisätyötä. Kun laskenta vektoroidaan (`-O3 -march=native`),
ikj-järjestyksen nopeus yli kaksinkertaistuu ja versiot ovat
käytännössä yhtä nopeita: ajosta riippuen kumpi tahansa oli hieman
edellä. Tämän kokoinen matriisi mahtuu vielä L3-välimuistiin, joten
Cachegrindin näyttämä muistiliikenteen säästö näkyisi ajassa vasta
suuremmilla matriiseilla ja tehokkaammalla laskennalla:

```{.tuloste tiedosto="esimerkit/tulokset/06-matriisitulo-O3.txt"}
```

Tuotantotason matriisitulo (OpenBLAS, BLIS, Intel MKL) yhdistää
useita lohkotasoja (L1, L2, L3), rekisteritason mikroytimen, joka
laskee esimerkiksi $8 \times 6$ -palan $C$:tä kokonaan rekistereissä, ja
pakkaa $A$:n ja $B$:n palat peräkkäisiksi puskureiksi. Se saavuttaa
yli 90 % koneen laskentahuipusta. Oma matriisitulo kannattaa kirjoittaa
vain opetustarkoituksessa; tuotannossa käytetään kirjastoa.

## Käytännössä

- **Järjestä data käsittelyn mukaan.** Kentät, jotka käsitellään
  yhdessä, kuuluvat samalle riville; kentät, joita kuuma silmukka ei
  tarvitse, kuuluvat muualle (kuuman ja kylmän datan erottelu).
- **Valitse AoS tai SoA kuuman silmukan mukaan.** SoA, kun silmukka
  käsittelee yhtä kenttää monesta oliosta; AoS, kun se käsittelee
  monta kenttää yhdestä.
- **Järjestä kentät koon mukaan** taulukoissa, joissa on paljon
  rakenteita, ja tarkista tulos `sizeof`- tai `pahole`-työkalulla.
- **Erota säikeiden kirjoittamat muuttujat eri riveille**
  (`alignas(64)`), mutta älä tee niin varmuuden vuoksi kaikelle: tila
  kasvaa.
- **Lohko laskenta, joka käyttää samaa dataa monta kertaa.** Lohkon koko
  valitaan välimuistin koon mukaan ja varmistetaan mittaamalla.
- **Käytä kirjastoa lineaarialgebraan.** BLAS-toteutukset ovat
  vuosikymmenten optimointityön tulos.

## Itsearviointi

- Osaat muuttaa rakenteiden taulukon taulukoiden rakenteeksi ja
  perustella, milloin muutos kannattaa.
- Osaat laskea rakenteen koon täytteineen ja pienentää sitä
  kenttien järjestyksellä.
- Osaat selittää väärän jakamisen ja estää sen tasauksella.
- Osaat kirjoittaa matriisitulon välimuistia hyödyntävässä
  järjestyksessä ja lohkottuna sekä selittää Cachegrindin luvuilla,
  mitä kumpikin muutos säästää.

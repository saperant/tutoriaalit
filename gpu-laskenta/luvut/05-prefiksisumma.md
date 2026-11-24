# Prefiksisumma

**Prefiksisumma** eli **skannaus** (scan) laskee jokaiselle alkiolle
sitä edeltävien alkioiden summan. *Kattava* (inclusive) skannaus
sisältää alkion itsensä, *poissulkeva* (exclusive) ei:

| Syöte | 3 | 1 | 4 | 1 | 5 |
|-------|---|---|---|---|---|
| kattava | 3 | 4 | 8 | 9 | 14 |
| poissulkeva | 0 | 3 | 4 | 8 | 9 |

CPU:lla skannaus on peräkkäinen silmukka, jossa jokainen tulos riippuu
edellisestä. Silti se voidaan laskea rinnakkain, ja se on GPU-laskennan
tärkein rakennuspalikka. Kun jokainen säie tuottaa vaihtelevan määrän
tulosta, poissulkeva skannaus kertoo, mihin kohtaan säie kirjoittaa
omansa. Tällä tavalla rakennetaan virran tiivistys, kantalukulajittelu
(luku 7), harvan matriisin käsittely, puskurien varaus ja monet
grafiikan algoritmit, kuten valojen jakaminen ruutuihin.

## Kaksi algoritmia

**Hillisin ja Steelen** algoritmi tekee $\log_2 n$ kierrosta. Kierroksella
$d$ jokainen alkio lisää itseensä $2^d$ paikan päässä vasemmalla olevan
arvon. Kierroksia on vähän, mutta jokaisella kierroksella lähes kaikki
$n$ säiettä tekevät työtä, joten yhteenlaskuja on $O(n \log n)$.

**Blellochin** algoritmi on *työtehokas*: se tekee saman kuin
peräkkäinen silmukka, $O(n)$ yhteenlaskua, mutta kaksinkertaisella
määrällä kierroksia. Ylösvaihe rakentaa summapuun kuten reduktio
(luku 4). Alasvaihe korvaa juuren nollalla ja valuttaa summat
takaisin alas, jolloin jokainen lehti saa vasemmalla olevien summan.

Esimerkki toteuttaa molemmat ensin CPU:lla samassa järjestyksessä kuin
varjostimet ja laskee työn:

```{.cpp tiedosto="esimerkit/05-skannaus.cpp" osa="tyomaara"}
```

```{.tuloste tiedosto="esimerkit/05-skannaus.odotettu"}
```

512 alkion lohkolle Hillis–Steele tekee 4 097 yhteenlaskua
yhdeksällä kierroksella ja Blelloch 1 022 yhteenlaskua 18
kierroksella. Kumpi on nopeampi, riippuu siitä, onko laitteella
toimettomia kaistoja. Aliryhmän sisällä kaistat ovat olemassa joka
tapauksessa, joten Hillis–Steele on siellä parempi: kierroksia on vähän,
eikä ylimääräinen työ maksa mitään. Laitteiston aliryhmäskannaus
`subgroupInclusiveAdd` toimii juuri näin. Suurille lohkoille työ alkaa
maksaa, ja Blelloch voittaa.

## Hillis–Steele jaetussa muistissa

Jos jokainen säie päivittäisi arvonsa paikallaan, se voisi lukea
naapurin jo päivitetyn arvon. Varjostin käyttää siksi kahta puskuria
vuorotellen ja estettä jokaisen kierroksen jälkeen:

```{.glsl tiedosto="esimerkit/varjostimet/skannaus_hs.comp" osa="hs"}
```

## Blelloch jaetussa muistissa

Blellochin lohkoskannaus käsittelee 512 alkiota 256 säikeellä.
Ylösvaiheessa aktiivisten säikeiden määrä puolittuu kierroksittain, ja
alasvaiheessa se kaksinkertaistuu:

```{.glsl tiedosto="esimerkit/varjostimet/skannaus_lohko.comp" osa="ylos"}
```

```{.glsl tiedosto="esimerkit/varjostimet/skannaus_lohko.comp" osa="alas"}
```

Ennen alasvaihetta säie 0 tallentaa juuren eli lohkon kokonaissumman
taulukkoon `summat` ja korvaa sen nollalla. Kokonaissummia tarvitaan
seuraavalla tasolla.

Indeksointi `vali * (2 * oma + 1) - 1` aiheuttaa jaetussa muistissa
pankkikonflikteja (luku 8): ylempien tasojen säikeet osuvat samoihin
pankkeihin. Tunnettu korjaus on lisätä indeksiin täyte
`indeksi / 32`, joka levittää osoitteet pankeille. Se jätetään tästä
pois selkeyden vuoksi.

## Monitasoinen skannaus

Lohkoskannaus antaa jokaiselle lohkolle oman skannauksen, joka alkaa
nollasta. Koko taulukon skannaukseen tarvitaan kolme vaihetta:

1. Skannaa jokainen 512 alkion lohko ja kirjoita lohkon summa.
2. Skannaa lohkojen summat (rekursiivisesti, jos niitä on yli 512).
3. Lisää jokaisen lohkon alkioihin edeltävien lohkojen summa.

```{.glsl tiedosto="esimerkit/varjostimet/skannaus_lisaa.comp" osa="lisaa"}
```

Apukirjaston `Skannaus`-luokka rakentaa tasot kerran ja tallentaa
vaiheet komentopuskuriin. Miljoonan alkion skannaus tarvitsee kolme
tasoa (1 954, 4 ja 1 lohkoa) ja viisi ajoa: kolme ylös ja kaksi alas.
Sama olio käytetään luvun 7 kantalukulajittelun jokaisella
kierroksella.

```{.cpp tiedosto="esimerkit/yhteinen/skannaus.hpp" osa="skannaus"}
```

Kolmella tasolla data luetaan ja kirjoitetaan kahdesti: ensin
lohkoskannauksessa ja sitten lisäyksessä. Muistisidonnaisessa
operaatiossa tämä tarkoittaa, että nopeus on noin puolet
mahdollisesta. Nykyiset kirjastot (CUB) käyttävät yksivaiheista
skannausta, jossa lohkot välittävät summansa toisilleen muistin kautta
lippujen avulla (*decoupled look-back*). Työryhmät odottavat siinä
toisiaan, mikä on turvallista vain, jos laite takaa edistymisen
kaikille aiemmin aloitetuille työryhmille. Vulkan ei takaa sitä, joten
siirrettävä koodi käyttää monitasoista versiota.

## Virran tiivistys

**Virran tiivistys** (stream compaction) poimii taulukosta ehdon
täyttävät alkiot uuteen tiiviiseen taulukkoon. Se tehdään kolmella
ajolla: liputus (1 tai 0), lippujen poissulkeva skannaus ja hajautus,
jossa jokainen valittu alkio kirjoitetaan skannauksen antamaan
paikkaan:

```{.glsl tiedosto="esimerkit/varjostimet/tiivista.comp" osa="tiivista"}
```

```{.cpp tiedosto="esimerkit/05-skannaus.cpp" osa="suuri"}
```

Valittujen alkioiden määrä on viimeinen skannattu arvo plus viimeinen
lippu. Tulos on vakaa: alkiot ovat samassa järjestyksessä kuin
syötteessä, koska skannaus säilyttää järjestyksen. Esimerkissä
miljoonasta luvusta valitaan 334 933 kolmella jaollista lukua, ja
tulos on sama kuin `std::ranges::copy_if`-funktiolla.

Luvussa 3 todettiin, että hajaantuminen kannattaa välttää
järjestämällä data. Virran tiivistys on siihen yleinen keino: kallista
käsittelyä tarvitsevat alkiot kootaan ensin yhteen, ja seuraava ajo
käsittelee vain ne ilman hajaantumista.

## Käytännössä

- **Skannaus on vastaus kysymykseen "mihin kirjoitan".** Kun säikeet
  tuottavat vaihtelevan määrän tulosta, laske määrät, skannaa ne ja
  kirjoita. Atominen laskuri (`atomicAdd` paikan varaamiseen) on
  vaihtoehto, mutta se ei säilytä järjestystä eikä ole
  deterministinen.
- **Aliryhmäskannaus ensin.** `subgroupExclusiveAdd` ja
  `subgroupInclusiveAdd` hoitavat alimmat tasot ilman jaettua muistia
  ja esteitä, ja jaettua muistia tarvitaan vain aliryhmien summille.
- **Monitasoinen skannaus on siirrettävä.** Yksivaiheinen skannaus on
  nopeampi, mutta se vaatii edistymistakuun, jota Vulkan ei anna.
- **Tarkista skannaus aina CPU:lla.** Skannauksen virhe näkyy
  harvoin itse skannauksessa, vaan kaukana myöhemmin väärään paikkaan
  kirjoitettuna datana. Testi `std::exclusive_scan`-funktiota vastaan
  epätasaisilla koilla löytää reunavirheet heti.

## Itsearviointi

- Osaat selittää kattavan ja poissulkevan prefiksisumman ja
  kertoa, mihin niitä käytetään GPU-algoritmeissa.
- Osaat verrata Hillisin ja Steelen sekä Blellochin algoritmeja
  työn ja kierrosten määrällä ja kertoa, kumpi sopii mihinkin.
- Osaat rakentaa monitasoisen skannauksen lohkoskannauksesta ja
  lisäysvaiheesta.
- Osaat toteuttaa virran tiivistyksen liputuksella, skannauksella ja
  hajautuksella.

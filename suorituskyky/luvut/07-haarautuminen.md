# Haarautuminen

Liukuhihnoitettu suoritin noutaa käskyjä kymmeniä jaksoja ennen kuin
ne suoritetaan, joten sen on arvattava jokaisen ehdollisen haaran
suunta. Tietokonearkkitehtuurin luku 5 rakensi ennustimet kaksibittisistä
laskureista gshareen. Nykyiset ennustimet osuvat oikeaan yli 95 %:ssa
tavallisen ohjelman haaroista, mutta väärä arvaus tyhjentää
liukuhihnan ja maksaa 15–20 jaksoa. Satunnaisesta datasta riippuva
haara on ennustamaton, ja sellainen haara kuumassa silmukassa voi
hallita koko ajoaikaa.

## Lajiteltu ja lajittelematon data

Klassinen koe laskee taulukon suurten arvojen summan:

```{.c tiedosto="esimerkit/07-haarat.c" osa="haarautuva"}
```

Kun tavut ovat satunnaisia, ehto on tosi puolella kierroksista
satunnaisessa järjestyksessä, eikä mikään ennustin voi tehdä parempaa
kuin arvata. Kun sama data on lajiteltu, ehto on ensin aina epätosi ja
sitten aina tosi, ja ennustin erehtyy vain kerran. Cachegrind
simuloi yksinkertaista ennustinta ja laskee ehdolliset haarat (Bc) ja
väärät ennusteet (Bcm):

```{.makefile tiedosto="esimerkit/Makefile" osa="haarat"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-haarat.txt"}
```

Molemmat ajot suorittavat täsmälleen samat käskyt. Lajittelemattomalla
datalla joka neljäs haara (500 000 kahdesta miljoonasta, joista puolet
on silmukan ehtoja) ennustetaan väärin, lajitellulla datalla
kahdeksantoista. Ajassa ero näkyy, kun haara pakotetaan pysymään
konekoodissa:

```{.tuloste tiedosto="esimerkit/tulokset/07-haarat-haara.txt"}
```

Lajittelematon data on kahdeksan kertaa hitaampaa kuin lajiteltu,
vaikka työ on sama. Jos tavu kestää 5 ns ja puolet niistä ennustetaan
väärin, yksi väärä ennuste maksaa noin 10 ns eli parikymmentä jaksoa.

## Haaraton muoto

Haaran voi poistaa laskemalla ehdon arvon ja käyttämällä sitä datana:

```{.c tiedosto="esimerkit/07-haarat.c" osa="haaraton"}
```

Vertailun tulos 0 tai 1 muutetaan maskiksi 0 tai $-1$, jonka kaikki
bitit ovat ykkösiä. `x & maski` on joko `x` tai 0. Haarattoman
version aika ei riipu datasta, ja se on nopeampi kuin haarautuva
versio lajitellullakin datalla, koska silmukassa ei ole muita
haaroja kuin silmukan ehto. Testi varmistaa, että kaikki versiot
antavat saman summan:

```{.tuloste tiedosto="esimerkit/07-haarat.odotettu"}
```

## Kääntäjä tekee saman

Edellinen ajo käännettiin lipuilla, jotka estävät kääntäjää
muuttamasta haaraa. Tavallisella `-O2`-käännöksellä tulos on toinen:

```{.tuloste tiedosto="esimerkit/tulokset/07-haarat.txt"}
```

GCC muutti haarautuvan version ehdolliseksi siirroksi (`cmov`), jonka
aika ei riipu datasta, ja haarattoman version se vektoroi. Clang
vektoroi molemmat. Tämä on tavallinen tilanne: kääntäjä poistaa
yksinkertaiset haarat itse, ja käsin kirjoitettu haaraton koodi on
hyödyllistä vain, kun kääntäjä ei siihen pysty. Ennen kuin muuttaa
koodia, kannattaa tarkistaa konekoodista (`objdump -d`, Compiler
Explorer), onko haara ylipäätään olemassa.

Haaraton muoto ei ole aina parempi. Ehdollinen siirto laskee
molemmat vaihtoehdot ja odottaa molempien syötteitä, kun ennustettu
haara voi jatkaa toista polkua odottamatta. Jos haara on lähes aina
samaan suuntaan, haarautuva koodi on yleensä nopeampi. Siksi
kääntäjät muuttavat haaroja harkiten, ja profiiliohjattu optimointi
(luku 9) auttaa niitä valitsemaan oikein.

## Muita keinoja

- **Lajittele tai ositus.** Jos data käsitellään monta kertaa,
  ehdon mukaan lajiteltu tai ositettu data tekee haarasta
  ennustettavan. Usein osituksen jälkeen haaraa ei tarvita lainkaan,
  koska kumpikin osa käsitellään omalla silmukallaan.
- **Hakutaulukko.** Monihaarainen päätös pienestä syötteestä, kuten
  merkin luokittelu, on taulukon indeksointi:
  `luokka[(unsigned char)c]`.
- **Todennäköisyysvihjeet.** `__builtin_expect(ehto, 0)` (C++20:ssä
  `[[unlikely]]`) kertoo kääntäjälle, että virhepolku on harvinainen.
  Kääntäjä sijoittaa yleisen polun peräkkäin ja harvinaisen
  kauemmas, mikä parantaa käskyvälimuistin käyttöä. Vihje ei muuta
  laitteiston ennustinta.
- **Epäsuorat hypyt.** Funktio-osoittimet, virtuaalifunktiot ja
  `switch`-hyppytaulukot ennustetaan kohdeosoitteen mukaan. Jos sama
  kutsukohta kutsuu vuorotellen eri funktioita satunnaisesti, ennuste
  epäonnistuu samalla tavalla. Lajittelu tyypin mukaan auttaa tässäkin.

## Käytännössä

- **Etsi haarat, jotka riippuvat satunnaisesta datasta.** `perf stat`
  näyttää väärien ennusteiden osuuden; Cachegrind (`--branch-sim=yes`)
  näyttää ne funktioittain.
- **Tarkista konekoodi ennen käsin optimointia.** Kääntäjä on usein
  jo poistanut haaran.
- **Käytä haaratonta muotoa ennustamattomissa haaroissa**, kun
  molemmat vaihtoehdot ovat halpoja laskea.
- **Pidä ennustettavat haarat haaroina.** Virhetarkistukset ja
  harvinaiset erikoistapaukset maksavat lähes nolla, kun niitä ei
  tapahdu.
- **Muuta datan järjestystä, älä koodia,** kun samaa dataa käydään
  läpi monta kertaa.

## Itsearviointi

- Osaat selittää, miksi väärä ennuste on kallis ja miksi lajittelu
  nopeuttaa ehdollista silmukkaa.
- Osaat mitata väärät ennusteet Cachegrindilla ja arvioida yhden
  väärän ennusteen hinnan ajoitusmittauksesta.
- Osaat kirjoittaa ehdon haarattomasti maskilla ja tarkistaa
  konekoodista, tekeekö kääntäjä saman.
- Osaat kertoa, milloin haaraton koodi on hitaampi kuin haarautuva.

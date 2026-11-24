# Mittaaminen C++:ssa

Mittauksen tilastot, eli toistot, mediaani, hajonta ja lämmittely,
käsitellään taidossa *Suorituskyvyn analyysi ja optimointi*. Tässä
luvussa ne toteutetaan C++:lla, ja lisäksi rakennetaan kaksi
determinististä mittaria: muistinvarausten laskuri ja Cachegrindin
käskymäärät operaatiota kohden. Ensin kuitenkin ongelma, joka on
C++:ssa tavallista pahempi: kääntäjä poistaa mitattavan koodin.

## Kääntäjä poistaa mittauksen

C++-kääntäjä näkee mallien ja `inline`-funktioiden rungot, joten se
sisällyttää ne kutsukohtaan ja poistaa laskennan, jonka tulosta ei
käytetä. Mittaus näyttää silloin nollaa. Esimerkkinä keskiarvo:

```{.cpp tiedosto="esimerkit/02-poistettu.cpp" osa="keskiarvo"}
```

Ratkaisu on kertoa kääntäjälle, että arvoa käytetään, tuottamatta
silti yhtään käskyä. GCC:n ja Clangin laajennettu `asm`-lause sopii
tähän: tyhjä assembly-lohko, joka "lukee" arvon tai "muuttaa" sitä.

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="pida"}
```

`pida` vastaa Google Benchmarkin funktiota `DoNotOptimize` ja
`sotke_muisti` funktiota `ClobberMemory`. `piilota` tekee syötteestä
tuntemattoman, jotta kääntäjä ei voi laskea tulosta etukäteen.
`volatile` estää poistamasta itse `asm`-lausetta, ja `"memory"`
kertoo, että lause voi lukea tai kirjoittaa mitä tahansa muistia.

Esimerkki mittaa keskiarvon neljällä tavalla. Kukin tapa on lambda,
jonka mittauskehys toistaa:

```{.cpp tiedosto="esimerkit/02-poistettu.cpp" osa="tavat"}
```

Cachegrind laskee suoritetut käskyt kierrosta kohden:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-poistettu.txt"}
```

Hylätty tulos maksaa nolla käskyä: koko kierros on poistettu, ja
jäljelle jää vain silmukan laskuri. Vakiosyötteellä kääntäjä laski
keskiarvon käännöksessä ja tallentaa vain valmiin luvun. Vasta kun
syöte on piilotettu, keskiarvo todella lasketaan. Ajoituksessa
hylätty mittaus näyttää yhtä nollalta:

```{.tuloste tiedosto="esimerkit/tulokset/02-poistettu.txt"}
```

Nollan lähellä oleva tulos on aina syytä epäillä: nykyprosessori ei
käsittele miljoonaa alkiota alle mikrosekunnissa.

## Mittauskehys

Mittauskehys ajaa funktion kerran lämmittelyksi ja sitten halutun
määrän kertoja. Se palauttaa mediaanin ja mediaanin absoluuttisen
poikkeaman, jotka kestävät yksittäisiä häiriöitä paremmin kuin
keskiarvo ja keskihajonta.

```{.cpp tiedosto="esimerkit/mittari.hpp" osa="mittaa"}
```

`std::chrono::steady_clock` on monotoninen kello: se ei hyppää, vaikka
järjestelmän kellonaikaa säädettäisiin. `system_clock` ei sovi
mittaamiseen, ja `high_resolution_clock` on libstdc++:ssa vain
`system_clock`in toinen nimi. Malliparametri `F` sallii minkä tahansa
kutsuttavan ilman `std::function`in kustannusta (luku 4).

## Muistinvarausten laskuri

C++ sallii ohjelman korvata globaalit `operator new`- ja `operator
delete`-funktiot. Korvaava määrittely voi laskea varaukset ennen kuin
se pyytää muistin `malloc`illa:

```{.cpp tiedosto="esimerkit/laskuri.hpp" osa="laskuri"}
```

Korvaavia funktioita saa olla ohjelmassa vain yksi kappale, joten
otsake otetaan mukaan yhteen käännösyksikköön. Kaikki
standardikirjaston säiliöt varaavat oletusallokaattorin kautta
`operator new`illa, joten laskuri näkee jokaisen vektorin,
merkkijonon, solmun ja `std::function`in varauksen. `malloc`ia
suoraan kutsuvat C-kirjastot jäävät laskematta.

Laskuri on deterministinen: sama ohjelma tekee aina yhtä monta
varausta, kun standardikirjaston toteutus on sama. Toteutusten välillä
luvut voivat erota, koska esimerkiksi lyhyen merkkijonon puskurin koko
ja vektorin kasvukerroin eivät ole standardin määräämiä. Tämän
tutoriaalin luvut ovat libstdc++:n (GCC 14), jota myös Ubuntun Clang
käyttää. Tuotannossa sama tieto saadaan ilman koodimuutoksia
työkaluilla, kuten `heaptrack` ja Valgrindin `massif` tai `dhat`.

## Käskyt operaatiota kohden

Valgrind ajaa ohjelman omassa virtuaalikoneessaan ja laskee jokaisen
suoritetun käskyn. Cachegrind lisäksi simuloi välimuistit. Tulokset
ovat täsmälleen samat joka ajossa, mutta Cachegrind laskee myös
ohjelman käynnistyksen ja syötteen rakentamisen. Ne supistuvat pois,
kun ohjelma ajetaan kahdesti, toistoilla 0 ja K, ja erotus jaetaan:

```{.makefile tiedosto="esimerkit/Makefile" osa="kaskyt"}
```

Siksi esimerkit tukevat argumenttia `--kerran TAPA K`. Ohjelma
rakentaa joka kerta saman syötteen, valitsee tavan yhden kerran ja
toistaa sitä K kertaa:

```{.makefile tiedosto="esimerkit/Makefile" osa="poistettu"}
```

`--suhde A B MIN` tarkistaa, että tavan A tulos on vähintään MIN
kertaa tavan B tulos. Näin tekstin väitteet, kuten "piilotettu syöte
tekee enemmän työtä kuin vakiosyöte", testataan joka käännöksellä.

Käskymäärä ei ole aika. Välimuistihutia, väärin ennustettuja haaroja ja
riippuvuusketjuja se ei näe, joten sama käskymäärä voi kestää
kymmenkertaisesti eri ajan. Siksi Cachegrindilla lasketaan tarvittaessa
myös välimuistihudit (luku 8), ja lopullinen tulos mitataan aina
kellolla.

## Käytännössä

- **Mittaa optimoitu käännös**, `-O2` tai `-O3` kuten tuotannossa.
  Optimoimattomassa C++:ssa jokainen `std::vector`in `operator[]` ja
  iteraattorin askel on funktiokutsu, joten `-O0`-mittaus kertoo
  abstraktioista väärää.
- **Estä poisto `pida`- ja `piilota`-tyyppisillä funktioilla** tai
  kirjaston vastineilla. Älä käytä `volatile`-muuttujia: ne estävät
  myös optimoinnit, jotka tuotantokoodissa tapahtuvat.
- **Nolla tai epäuskottavan pieni aika** tarkoittaa lähes aina, että
  kääntäjä poisti tai laski laskennan valmiiksi.
- **Varauslaskuri on halvin profiloija.** Varausten määrä kertoo
  kopioista, kasvusta ja solmusäiliöistä suoraan, ja se toimii myös
  sanitoijien kanssa ja testeissä.
- **Käskymäärät sopivat regressiotesteihin.** Ajoitus ei sovi
  CI-palvelimelle, jonka kuormaa ei tunneta; käskymäärä samalla
  kääntäjällä sopii.

## Itsearviointi

- Osaat selittää, miksi kääntäjä voi poistaa mitattavan koodin, ja
  estää sen `asm`-lauseella tuottamatta ylimääräisiä käskyjä.
- Osaat korvata globaalin `operator new`in ja laskea ohjelman osan
  muistinvaraukset.
- Osaat laskea Cachegrindilla käskyt operaatiota kohden niin, että
  käynnistys ja syötteen rakentaminen supistuvat pois.
- Osaat valita mittauksen kellon ja perustella, miksi mediaani on
  keskiarvoa parempi.

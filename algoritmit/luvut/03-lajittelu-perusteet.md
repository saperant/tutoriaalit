# Lajittelun perusteet

Lajittelu on algoritmien perustehtävä, koska järjestetystä datasta
moni muu tehtävä ratkeaa helposti. Duplikaatit ovat järjestetyssä
taulukossa vierekkäin, mediaani on keskellä, ja haku onnistuu
logaritmisessa ajassa (luku 6). Lajittelualgoritmeissa näkyvät myös
lähes kaikki suunnittelumenetelmät: inkrementaalinen rakentaminen,
hajota ja hallitse, satunnaistus ja tietorakenteen hyödyntäminen.

Tässä luvussa on kaksi algoritmia, joiden ominaisuudet ovat
vastakkaiset. Lisäyslajittelu on yksinkertainen ja nopea lähes
järjestetylle datalle, mutta neliöllinen pahimmassa tapauksessa.
Lomituslajittelu on aina $\Theta(n \log n)$, mutta se tarvitsee
aputaulukon.

## Lisäyslajittelu

Lisäyslajittelu toimii kuin korttipakan järjestäminen kädessä:
alkuosa on jo järjestyksessä, ja seuraava alkio siirretään sen
oikealle paikalle. Silmukan invariantti kertoo, miksi algoritmi on
oikein:

```{.c tiedosto="esimerkit/03-lisays.c" osa="lisays"}
```

Invariantti pätee alussa, koska yhden alkion osa `a[0..1)` on
järjestyksessä. Kierros säilyttää sen: suuremmat alkiot siirtyvät
yhden pykälän oikealle, ja `x` asettuu ensimmäisen itseään
pienemmän tai yhtä suuren alkion perään. Kun silmukka päättyy,
`i == n`, ja invariantin mukaan koko taulukko on järjestyksessä.
Tämä on diskreetin matematiikan luvun 6 induktiotodistus
ohjelmakoodina.

Vertailujen määrä riippuu syötteen järjestyksestä:

```{.tuloste tiedosto="esimerkit/03-lisays.odotettu"}
```

Järjestetyllä syötteellä jokainen alkio vertautuu vain edeltäjäänsä:
$n - 1 = 1999$ vertailua. Käänteisellä jokainen alkio siirtyy alkuun
asti: $n(n-1)/2 = 1\,999\,000$ vertailua. Satunnainen syöte on näiden
puolivälissä, noin $n^2/4$.

Tarkka sääntö on, että sisin silmukka siirtää alkiota kerran jokaista
*inversiota* kohden. Inversio on pari $i < j$, jossa $a_i > a_j$, eli
väärässä järjestyksessä oleva pari. Lisäyslajittelun työ on
$\Theta(n + I)$, missä $I$ on inversioiden määrä. Lähes järjestetyssä
taulukossa, jossa 20 satunnaista vaihtoa on tehty, inversioita on
vähän, ja työ on noin kolmaskymmenesosa satunnaisen syötteen työstä.
Inversioiden määrän voi laskea tehokkaasti; se tehdään luvussa 7.

Siksi lisäyslajittelu on oikea valinta, kun data on valmiiksi lähes
järjestyksessä: aikaleimoja, jotka saapuvat lähes oikeassa
järjestyksessä, tai järjestetty taulukko, johon on lisätty muutama
alkio. Se on myös pienten osataulukoiden lajittelija nopeampien
algoritmien sisällä.

## Lomituslajittelu

Lomituslajittelu on *hajota ja hallitse* -algoritmi (luku 7). Se
jakaa taulukon kahteen puoliskoon, lajittelee kummankin rekursiivisesti
ja *lomittaa* järjestetyt puoliskot yhdeksi järjestetyksi taulukoksi.
Lomitus vertaa puoliskojen pienimpiä jäljellä olevia alkioita ja siirtää
pienemmän tulokseen:

```{.c tiedosto="esimerkit/03-lomitus.c" osa="lomitus"}
```

Lomitus on lineaarinen, koska jokainen vertailu siirtää yhden alkion.
Rekursiopuussa on $\lceil \log_2 n \rceil$ tasoa, ja jokaisella tasolla
lomitetaan yhteensä $n$ alkiota. Työtä on siis $\Theta(n \log n)$
riippumatta syötteen järjestyksestä. Luvun 2 kasvumittaus näytti
saman kokeellisesti.

```{.dot otsikko="Lomituslajittelun rekursiopuu: jako alaspäin, lomitus ylöspäin"}
digraph {
  nodesep=0.15; ranksep=0.3;
  node [shape=box, fontname="DejaVu Sans Mono", fontsize=9];
  a [label="5 2 4 7 1 3 2 6"];
  b [label="5 2 4 7"]; c [label="1 3 2 6"];
  d [label="5 2"]; e [label="4 7"]; f [label="1 3"]; g [label="2 6"];
  a -> b; a -> c; b -> d; b -> e; c -> f; c -> g;
  node [fillcolor="#FFFFFF"];
  d2 [label="2 5"]; e2 [label="4 7"]; f2 [label="1 3"]; g2 [label="2 6"];
  b2 [label="2 4 5 7"]; c2 [label="1 2 3 6"];
  a2 [label="1 2 2 3 4 5 6 7", penwidth=1.6];
  d -> d2; e -> e2; f -> f2; g -> g2;
  d2 -> b2; e2 -> b2; f2 -> c2; g2 -> c2; b2 -> a2; c2 -> a2;
}
```

Hinta on $\Theta(n)$ lisämuistia aputaulukolle. Esimerkki varaa
aputaulukon kerran ja antaa sen jokaiselle rekursiotasolle; jos
jokainen kutsu varaisi omansa, varausten määrä olisi $\Theta(n)$ ja
niiden hinta hallitsisi pienillä osataulukoilla. Taulukon paikallaan
lomittaminen ilman lisämuistia on mahdollista, mutta monimutkaista ja
käytännössä hitaampaa.

Lomituslajittelu sopii myös datalle, joka ei mahdu muistiin. Ulkoinen
lajittelu lajittelee muistiin mahtuvat palat erikseen ja lomittaa
lajitellut tiedostot lukemalla niitä peräkkäin. Linkitetyille listoille
lomitus on luonteva, koska listan voi lomittaa siirtämällä osoittimia
ilman lisämuistia.

## Vakaus

Lajittelu on *vakaa*, jos yhtä suurten avainten alkiot säilyttävät
keskinäisen järjestyksensä. Vakaus on merkityksellinen, kun
lajiteltavilla alkioilla on muutakin tietoa kuin avain. Esimerkissä
tilaukset ovat aikajärjestyksessä, ja ne lajitellaan asiakkaan mukaan.
Vakaa lajittelu pitää kunkin asiakkaan tilaukset aikajärjestyksessä:

```{.tuloste tiedosto="esimerkit/03-lomitus.odotettu"}
```

Lomituslajittelu on vakaa, koska tasapelissä se ottaa vasemman
puoliskon alkion, joka oli alun perin edellä. Yksi merkki, `<` eikä
`<=`, ratkaisee asian. Valintalajittelu, joka vaihtaa pienimmän
alkion paikalleen, ei ole vakaa: vaihto voi heittää alkion yhtä
suurten ohi. Tulosteessa B:n tilaukset 6 ja 3 ovat vaihtaneet
paikkaa.

Vakaus testataan satunnaistetusti. Pieni avainalue (neljä asiakasta)
tuottaa paljon yhtä suuria avaimia, ja tarkistus vaatii, että avaimet
ovat järjestyksessä ja yhtä suurten avainten kellonajat kasvavat:

```{.c tiedosto="esimerkit/03-lomitus.c" osa="vakaus"}
```

Vakaudesta on käytännön hyötyä, kun lajitellaan useamman avaimen
mukaan. Taulukko, joka lajitellaan ensin päivämäärän ja sitten vakaasti
asiakkaan mukaan, on asiakkaittain ja asiakkaan sisällä päivämäärän
mukaan. Taulukko-ohjelmat ja tietokannat käyttävät tätä, kun käyttäjä
klikkaa sarakeotsikoita peräkkäin. Kantalukulajittelu (luku 5) perustuu
kokonaan samaan ajatukseen.

C:n `qsort` ei lupaa vakautta. Jos vakaus tarvitaan, avaimeen lisätään
alkuperäinen indeksi tasapelin ratkaisijaksi, kuten esimerkin kenttä
`kello`, tai käytetään omaa lomituslajittelua.

## Vertailijan sudenkuoppa

Kirjaston `qsort` tarvitsee vertailufunktion, joka palauttaa
negatiivisen, nollan tai positiivisen luvun. Lyhin kirjoitustapa on
tavallinen virhe:

```{.c tiedosto="esimerkit/03-vertailija.kaatuu.c" osa="vaarin"}
```

Erotus $a - b$ ylivuotaa, kun luvut ovat eri merkkisiä ja kaukana
toisistaan, esimerkiksi $3 - (-2^{31})$. Etumerkillisen ylivuoto on
C:ssä määrittelemätöntä käyttäytymistä. Käytännössä tulos kiertyy
negatiiviseksi, `qsort` saa väärän vastauksen ja järjestää taulukon
väärin, mitään virheilmoitusta antamatta. UBSan pysäyttää ohjelman
ensimmäiseen ylivuotoon:

```text
runtime error: signed integer overflow: 3 - -2147483648 cannot be
represented in type 'int'
```

Oikea muoto on `(a > b) - (a < b)`, joka palauttaa aina $-1$, $0$
tai $1$ eikä voi ylivuotaa. Vertailijan on myös oltava johdonmukainen:
jos $a < b$ ja $b < c$, on oltava $a < c$, eikä tulos saa riippua
kutsujärjestyksestä. Liukulukujen `NaN` rikkoo tämän, koska se ei ole
pienempi, yhtä suuri eikä suurempi kuin mikään luku. Epäjohdonmukainen
vertailija voi saada lajittelun silmukoimaan tai lukemaan taulukon ohi.

## Käytännössä

- **Lajittele ennen kuin keksit monimutkaisempaa.** Järjestetty data
  tekee duplikaatit, mediaanin ja haun helpoiksi. $\Theta(n \log n)$
  on harvoin pullonkaula.
- **Lisäyslajittelu lähes järjestetylle datalle ja pienille
  taulukoille.** Sen työ on $\Theta(n + I)$, ja pienellä $n$:llä sen
  vakiokerroin on paras.
- **Perustele invariantilla.** Silmukan invariantti on kirjoitettava
  kommenttiin: se kertoo lukijalle, mitä silmukka tekee, ja sen voi
  tarkistaa testissä.
- **Varaa aputaulukko kerran.** Rekursiivinen algoritmi, joka varaa
  muistia jokaisessa kutsussa, maksaa varaajalle enemmän kuin itse
  työstä.
- **Tiedä, tarvitsetko vakauden.** Jos alkiolla on muutakin tietoa
  kuin avain, kirjoita vakausvaatimus näkyviin ja testaa se.
- **Vertailija on `(a > b) - (a < b)`.** Erotus ylivuotaa, ja
  ylivuoto on määrittelemätöntä käyttäytymistä. Sanitoija löytää
  virheen, testit eivät välttämättä.
- **Vertailijan on oltava johdonmukainen.** `NaN` tai satunnainen
  tasapelin ratkaisu voi rikkoa lajittelun.

## Itsearviointi

- Osaat kirjoittaa lisäyslajittelun ja perustella sen oikeellisuuden
  silmukan invariantilla.
- Osaat selittää, miksi lisäyslajittelun työ on $\Theta(n + I)$ ja
  mitä inversiot ovat.
- Osaat kirjoittaa lomituslajittelun, jossa aputaulukko varataan
  kerran, ja johtaa sen $\Theta(n \log n)$-ajan rekursiopuusta.
- Osaat määritellä vakauden, tunnistaa vakaan ja epävakaan
  algoritmin ja testata vakauden satunnaistetusti.
- Osaat kirjoittaa oikean `qsort`-vertailijan ja selittää, miksi
  erotus on virhe.

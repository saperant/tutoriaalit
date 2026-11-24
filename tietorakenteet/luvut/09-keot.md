# Keot ja prioriteettijonot

*Prioriteettijono* on abstrakti tietotyyppi, jossa on kaksi
pääoperaatiota: lisää alkio ja ota pienin (tai suurin). Luvun 4
järjestetty lista toteutti sen niin, että ottaminen oli $O(1)$ mutta
lisäys $O(n)$. Hakupuu antaisi molemmat $O(\log n)$-ajassa, mutta vain
tasapainotettuna ja osoittimien hinnalla. *Binäärikeko* (engl. binary
heap) antaa samat hinnat yksinkertaisemmin: se on tavallinen taulukko.

Prioriteettijonoja käytetään ajastimissa, tapahtumapohjaisissa
simulaatioissa, käyttöjärjestelmän vuorontajassa ja
graafialgoritmeissa (Dijkstran lyhimmät polut, Primin virittävä puu).

## Keko taulukkona

Binäärikeko on *täydellinen* binääripuu: kaikki tasot ovat täynnä
viimeistä lukuun ottamatta, ja viimeinen täytetään vasemmalta. Sen
voi tallentaa taulukkoon tasoittain ilman osoittimia, ja solmun $i$
sukulaiset löytyvät laskemalla:

| Solmu | Indeksi (alkaen 0) |
|-------|--------------------|
| vanhempi | $\lfloor (i - 1) / 2 \rfloor$ |
| vasen lapsi | $2i + 1$ |
| oikea lapsi | $2i + 2$ |

*Kekoehto* vaatii, että vanhempi on aina vähintään yhtä pieni kuin
lapsensa. Silloin pienin alkio on juuressa, indeksissä 0. Ehto koskee
vain vanhempia ja lapsia: sisarukset ja eri haarat ovat keskenään
missä järjestyksessä tahansa. Juuri tämä löysyys tekee keosta halvan
ylläpitää verrattuna hakupuuhun, jossa koko järjestys on määrätty.

Esimerkki on ajastinjono. Vertailufunktio ratkaisee tasapelit
tunnisteella, jotta ottojärjestys on aina määrätty:

```{.c tiedosto="esimerkit/09-keko.c" osa="rakenne"}
```

## Lisäys ja otto

Lisäys kirjoittaa uuden alkion taulukon loppuun – puun seuraavaan
vapaaseen lehteen – ja *nostaa* sitä (engl. sift up), kunnes vanhempi
on pienempi. Otto palauttaa juuren, siirtää viimeisen alkion juureen
ja *laskee* sitä (engl. sift down) vaihtamalla sen pienempään
lapseensa, kunnes kekoehto on voimassa. Kumpikin kulkee yhden polun
juuren ja lehden välillä, joten molemmat ovat $O(\log n)$.

```{.c tiedosto="esimerkit/09-keko.c" osa="nosta"}
```

```{.tuloste tiedosto="esimerkit/09-keko.odotettu"}
```

Tulosteen ensimmäinen rivi näyttää ajastimet erääntymisjärjestyksessä;
kaksi 120 ms:n ajastinta tulevat tunnisteen mukaan. Ilman tasapelin
ratkaisua niiden järjestys riippuisi lisäysjärjestyksestä ja keon
sisäisestä tilasta, koska keko ei ole *vakaa*.

Keosta ei voi tehokkaasti hakea mielivaltaista alkiota: kekoehto ei
kerro, kummassa alipuussa se on. Jos ajastimen pitää voida perua,
tavallinen ratkaisu on tallentaa jokaiseen ajastimeen sen indeksi
keossa ja päivittää indeksiä jokaisessa vaihdossa. Silloin ajastimen
voi poistaa siirtämällä viimeisen alkion sen paikalle ja nostamalla tai
laskemalla sitä. Toinen vaihtoehto on merkitä ajastin peruutetuksi ja
ohittaa se, kun se tulee juureen.

## Kekoutus

Jos kaikki alkiot ovat valmiina taulukossa, keon voi rakentaa
lisäämättä niitä yksitellen. *Kekoutus* (engl. heapify) laskee jokaisen
sisäsolmun alhaalta ylös:

```{.c tiedosto="esimerkit/09-keko.c" osa="kekoutus"}
```

Yksittäiset lisäykset maksavat yhteensä $O(n \log n)$, kekoutus vain
$O(n)$. Syy on puun muodossa: puolet solmuista on lehtiä, jotka eivät
laskeudu lainkaan, neljännes laskeutuu enintään yhden tason ja niin
edelleen. Summa $\sum_h h \cdot n/2^{h+1}$ on alle $n$. Yksittäisessä
lisäyksessä taas jokainen uusi alkio voi joutua nousemaan juureen
asti, ja useimmat alkiot lisätään syvimmälle tasolle.

Mittaus laskee vaihdot kummallakin tavalla, kun ajat ovat satunnaisia
ja kun ne tulevat laskevassa järjestyksessä – pahin tapaus
lisäykselle, koska jokainen uusi alkio on pienin tähän asti:

```{.c tiedosto="esimerkit/09-keko.c" osa="vertailu"}
```

Satunnaisella datalla ero on alle kaksinkertainen, koska satunnainen
alkio nousee keskimäärin vain vakiomäärän tasoja. Laskevalla datalla
yksittäiset lisäykset tekevät lähes 1,5 miljoonaa vaihtoa
($\approx n \log_2 n$), kekoutus alle 100 000. Tulosteen viimeinen
rivi on vertailutesti: molemmat keot antavat samat alkiot samassa
järjestyksessä.

Kekoutettu taulukko kelpaa myös lajitteluun. Kun juuri vaihdetaan
viimeiseen alkioon ja keko kutistetaan yhdellä, pienin alkio siirtyy
taulukon loppuun; $n$ toistoa lajittelee taulukon paikallaan
$O(n \log n)$-ajassa. Tämä on *kekolajittelu*, jota käsitellään
tarkemmin taidossa *Algoritmit*.

## Invariantti

Keon invariantti on kekoehto jokaiselle solmulle: kaikilla
$i \geq 1$ alkio `t[(i - 1) / 2]` ei ole alkion `t[i]` jälkeen.
Tarkistus on yksi silmukka taulukon yli, $O(n)$. Vertailutestissä
referenssiksi kelpaa lajiteltu taulukko: keosta otettujen alkioiden on
tultava samassa järjestyksessä kuin lajitellun taulukon.

## Käytännössä

- **Keko on taulukko.** Ei osoittimia, ei solmuvarauksia, ja
  kasvatus toimii kuten vektorissa.
- **Kekouta valmis data.** $O(n)$ yksittäisten lisäysten
  $O(n \log n)$ sijaan.
- **Ratkaise tasapelit,** jos ottojärjestyksen on oltava
  toistettava: keko ei ole vakaa.
- **Perumista varten indeksi alkioon** tai laiska poisto merkinnällä.
- **Suurelle keolle neljä lasta.** Leveämpi keko (d-ary heap) on
  matalampi, ja yhden solmun lapset ovat samassa välimuistirivissä.

## Itsearviointi

- Osaat laskea taulukkoon tallennetun binäärikeon solmun vanhemman ja
  lasten indeksit.
- Osaat toteuttaa lisäyksen nostamalla ja oton laskemalla.
- Osaat rakentaa keon valmiista taulukosta kekoutuksella ja perustella,
  miksi se on $O(n)$.
- Osaat kertoa, miksi keko ei ole vakaa ja miten tasapelit ratkaistaan.

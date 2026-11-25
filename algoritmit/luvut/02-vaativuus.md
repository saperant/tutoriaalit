# Aika- ja tilavaativuus

Algoritmin *aikavaativuus* kertoo, miten sen työmäärä kasvaa syötteen
koon $n$ mukana. Tarkka sekuntimäärä riippuu koneesta, kääntäjästä ja
välimuistista, joten sen sijaan lasketaan *perusoperaatioita*:
vertailuja, yhteenlaskuja tai taulukon alkioiden siirtoja. Oletus on,
että jokainen perusoperaatio vie vakioajan. Silloin työmäärä on
funktio $T(n)$, ja kiinnostavaa on sen kasvunopeus eikä tarkka arvo.

*Tilavaativuus* kertoo samalla tavalla, paljonko lisämuistia algoritmi
tarvitsee syötteen lisäksi. Rekursiivisen algoritmin tilaan lasketaan
myös kutsupino: rekursio, jonka syvyys on $n$, vie $O(n)$ muistia,
vaikka yksikään kutsu ei varaisi mitään.

## O, Ω ja Θ

Merkinnät ovat tuttuja taidosta *Diskreetti matematiikka*. Tässä ne
kerrataan lyhyesti, koska koko tutoriaali käyttää niitä, ja luvun
lopussa niiden ennusteet tarkistetaan mittaamalla.

Kolme merkintää kuvaa kasvunopeutta:

| Merkintä | Määritelmä | Tulkinta |
|----------|------------|----------|
| $T(n) = O(f(n))$ | $T(n) \le c\,f(n)$, kun $n \ge n_0$ | kasvaa enintään kuten $f$ |
| $T(n) = \Omega(f(n))$ | $T(n) \ge c\,f(n)$, kun $n \ge n_0$ | kasvaa vähintään kuten $f$ |
| $T(n) = \Theta(f(n))$ | sekä $O(f(n))$ että $\Omega(f(n))$ | kasvaa kuten $f$ |

Vakiot $c > 0$ ja $n_0$ saa valita vapaasti. Siksi vakiokertoimet ja
alemman asteen termit katoavat: $3n^2 + 100n + 7 = \Theta(n^2)$, koska
riittävän suurella $n$:llä $n^2$-termi hallitsee. Samasta syystä
logaritmin kantaluvulla ei ole väliä: $\log_2 n$ ja $\log_{10} n$
eroavat vain vakiokertoimella $\log_2 10$.

Arkikielessä "algoritmi on $O(n^2)$" tarkoittaa usein $\Theta(n^2)$:
O on yläraja, ja $O(n^2)$-algoritmi on muodollisesti myös $O(n^3)$.
Kun tarkkuudella on väliä, kannattaa sanoa Θ. Ω on hyödyllinen
*alarajoissa*, jotka koskevat kaikkia algoritmeja: luvussa 5 todetaan,
että jokainen vertailuihin perustuva lajittelu tekee pahimmillaan
$\Omega(n \log n)$ vertailua.

Yleisimmät kasvuluokat ja niiden käytännön raja:

| Luokka | Tyypillinen algoritmi | Suurin $n$ sekunnissa |
|--------|-----------------------|-----------------------|
| $\Theta(1)$ | taulukon indeksointi | rajaton |
| $\Theta(\log n)$ | binäärihaku | rajaton |
| $\Theta(n)$ | lineaarihaku, Kadane | noin $10^8$ |
| $\Theta(n \log n)$ | lomituslajittelu | noin $10^7$ |
| $\Theta(n^2)$ | lisäyslajittelu | noin $10^4$ |
| $\Theta(n^3)$ | kaikkien jaksojen summat | noin $500$ |
| $\Theta(2^n)$ | kaikki osajoukot | noin $27$ |
| $\Theta(n!)$ | kaikki järjestykset | noin $11$ |

Sarake olettaa noin $10^8$ perusoperaatiota sekunnissa, mikä on
tavallisen C-ohjelman suuruusluokka. Luvut ovat karkeita, mutta niistä
näkee, miksi eksponentiaalinen algoritmi ei pelasta suurta syötettä
nopeammallakaan koneella: tuhat kertaa nopeampi kone kasvattaa $2^n$:n
rajaa vain kymmenellä.

## Silmukoiden analyysi

Useimmat analyysit ovat silmukoiden laskemista. Peräkkäiset osat
lasketaan yhteen ja sisäkkäiset kerrotaan:

- Silmukka, joka käy $n$ alkiota läpi ja tekee kullekin vakiotyön, on
  $\Theta(n)$.
- Kaksi sisäkkäistä silmukkaa, joissa sisempi käy läpi indeksit
  $i \ldots n-1$, tekevät $\sum_{i=0}^{n-1} (n - i) = n(n+1)/2$
  kierrosta, siis $\Theta(n^2)$.
- Silmukka, joka puolittaa välin joka kierroksella, päättyy
  $\lceil \log_2 (n + 1) \rceil$ kierroksen jälkeen: $\Theta(\log n)$.
- Peräkkäin $\Theta(n \log n)$ ja $\Theta(n)$ on yhteensä
  $\Theta(n \log n)$: suurempi termi hallitsee.

Luvun 1 kuutiollinen osasumma on kolme sisäkkäistä silmukkaa. Sen
yhteenlaskujen määrä on tarkalleen $\sum_{i \le j} (j - i + 1) =
n(n+1)(n+2)/6$, joka on $n = 400$:lla $10\,746\,800$, sama luku kuin
tulosteessa. Laskuri ja kaava kannattaa aina verrata: jos ne eroavat,
joko analyysi tai toteutus on väärin.

Rekursiivisten algoritmien työ kuvataan rekursioyhtälöllä.
Lomituslajittelu jakaa taulukon kahtia, lajittelee puolikkaat ja
lomittaa ne lineaarisessa ajassa: $T(n) = 2\,T(n/2) + \Theta(n)$.
Diskreetin matematiikan luvun 7 master-lause ratkaisee tällaiset
yhtälöt suoraan:

| Yhtälö | Ratkaisu | Algoritmi |
|--------|----------|-----------|
| $T(n) = T(n/2) + \Theta(1)$ | $\Theta(\log n)$ | binäärihaku |
| $T(n) = 2\,T(n/2) + \Theta(n)$ | $\Theta(n \log n)$ | lomituslajittelu |
| $T(n) = 3\,T(n/2) + \Theta(n)$ | $\Theta(n^{\log_2 3})$ | Karatsuba (luku 7) |
| $T(n) = T(n - 1) + \Theta(n)$ | $\Theta(n^2)$ | pikalajittelun pahin tapaus |

Viimeinen ei ole master-lauseen muotoa, mutta sen ratkaisee suoraan
summaamalla: $n + (n-1) + \cdots + 1$.

## Pahin, keskimääräinen ja tasoitettu tapaus

Sama algoritmi voi tehdä eri määrän työtä samankokoisilla syötteillä.
Lisäyslajittelu käy valmiiksi järjestetyn taulukon läpi kerran, mutta
käänteisessä järjestyksessä olevassa siirtää jokaista alkiota kaikkien
edeltäjien ohi. Siksi puhutaan kolmesta tapauksesta:

- **Pahin tapaus** on suurin työmäärä kaikista $n$:n kokoisista
  syötteistä. Se on takuu: algoritmi ei koskaan ole tätä hitaampi.
  Takuuta tarvitaan aina, kun syöte voi olla vihamielinen, esimerkiksi
  verkosta tuleva pyyntö.
- **Keskimääräinen tapaus** on odotusarvo jonkin syötejakauman, yleensä
  satunnaisen järjestyksen, yli. Lisäyslajittelu tekee satunnaisella
  syötteellä keskimäärin $n^2/4$ vertailua, puolet pahimmasta.
  Keskiarvo on hyödyllinen vain, jos todelliset syötteet todella
  muistuttavat oletettua jakaumaa.
- **Satunnaistettu algoritmi** tekee itse satunnaisia valintoja, jolloin
  odotusarvo otetaan algoritmin valintojen yli *jokaiselle* syötteelle.
  Satunnaisen jakoalkion pikalajittelu (luku 4) on keskimäärin
  $O(n \log n)$ jokaisella syötteellä, jonka alkiot ovat erisuuria;
  huonoa järjestystä ei voi rakentaa etukäteen.
- **Tasoitettu tapaus** (engl. amortized) on pisimmän mahdollisen
  operaatiosarjan kokonaistyö jaettuna operaatioiden määrällä.
  Dynaamisen taulukon lisäys on joskus $\Theta(n)$, kun taulukko
  kasvatetaan, mutta $n$ lisäyksen sarja on $\Theta(n)$, joten lisäys on
  tasoitetusti vakioaikainen (taito *Tietorakenteet*). Tasoitettu takuu
  on aito takuu koko sarjalle, ei todennäköisyyslaskelma.

## Kasvun mittaaminen

Analyysin voi tarkistaa kokeellisesti. Kun syötteen koko
kaksinkertaistetaan, suhde $T(2n)/T(n)$ paljastaa kasvuluokan:
lineaarisella se on 2, neliöllisellä 4, kuutiollisella 8 ja
$n \log n$ -algoritmilla hieman yli 2. Logaritmisella algoritmilla
erotus $T(2n) - T(n)$ on vakio. Esimerkki mittaa neljä algoritmia
samalla satunnaisella datalla:

```{.c tiedosto="esimerkit/02-kasvu.c" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/02-kasvu.odotettu"}
```

Suhdesarake on viimeisen ja toiseksi viimeisen sarakkeen suhde.
Lineaarihaku (pahin tapaus, etsitään puuttuvaa arvoa) tekee
täsmälleen $n$ vertailua. Binäärihaun vertailut kasvavat yhdellä joka
kaksinkertaistuksella, mikä on $\log_2 n$:n tuntomerkki.
Lomituslajittelun suhde 2,18 on lähellä teoreettista arvoa
$2 \cdot \log 8000 / \log 4000 \approx 2{,}17$, ja lisäyslajittelun 4,13
on lähellä neliöllisen 4:ää. Lisäyslajittelun luvut ovat noin $n^2/4$,
kuten keskimääräisen tapauksen analyysi ennustaa.

Log-log-asteikolla kasvuluokka näkyy suoran kulmakertoimena:
neliöllisen lisäyslajittelun suora on kaksi kertaa niin jyrkkä kuin
lineaarihaun, ja binäärihaun lähes vaakasuora.

![Vertailujen määrä syötteen koon funktiona (luvut yllä olevasta tulosteesta)](kuvat/kasvu.png){width=85%}

Kokeen ja analyysin yhtäpitävyys on vahvempi todiste kuin kumpikaan
yksin. Jos suhde olisi odotettua suurempi, toteutuksessa olisi
todennäköisesti piilevä silmukka, esimerkiksi `strlen` silmukan
ehdossa tai lisäys taulukon alkuun.

## Vakiokertoimet

Asymptoottinen analyysi kertoo, kumpi algoritmi voittaa *riittävän*
suurella syötteellä. Se ei kerro, missä raja kulkee. Lisäyslajittelu
tekee $n = 1000$:lla 260 000 vertailua ja lomituslajittelu 8700,
mutta kymmenen alkion taulukolla lisäyslajittelu on nopeampi: sen
sisin silmukka on yksinkertainen, se ei kutsu itseään eikä tarvitse
aputaulukkoa. Siksi käytännön lajittelijat (luku 4) siirtyvät
lisäyslajitteluun, kun osataulukko on pienempi kuin noin 16–32 alkiota.

Vakiokertoimiin vaikuttaa myös muisti. Peräkkäin luettava taulukko
on moninkertaisesti nopeampi kuin osoittimia seuraava lista, vaikka
molemmat ovat $\Theta(n)$ (taito *Tietorakenteet*). Analyysi valitsee
kasvuluokan, mittaus valitsee toteutuksen.

## Käytännössä

- **Laske kasvuluokka ennen koodaamista.** Syötteen enimmäiskoko ja
  kasvuluokkataulukko kertovat heti, riittääkö suora ratkaisu: jos
  $n = 10^5$, neliöllinen algoritmi on rajoilla ja kuutiollinen
  mahdoton.
- **Mittaa laskureilla, älä kellolla.** Laskuri on toistettava ja
  vertailukelpoinen analyysin kanssa. Kello mittaa myös konetta,
  kuormaa ja välimuistia.
- **Kaksinkertaista ja katso suhdetta.** Suhde $T(2n)/T(n)$ on nopein
  tapa tunnistaa kasvuluokka kokeellisesti ja löytää piilevä silmukka.
- **Kysy, kenen syöte.** Jos syöte voi olla vihamielinen, vain pahimman
  tapauksen takuu tai satunnaistus suojaa. Keskimääräinen tapaus
  olettaa jakauman, jota hyökkääjä ei noudata.
- **Muista pino.** Rekursion syvyys on tilavaativuutta. Syvyys $n$
  kaataa ohjelman jo muutaman sadan tuhannen alkion syötteellä, koska
  pino on tyypillisesti 8 MiB.

## Itsearviointi

- Osaat määritellä merkinnät $O$, $\Omega$ ja $\Theta$ ja perustella,
  miksi vakiokertoimet ja logaritmin kantaluku eivät vaikuta niihin.
- Osaat laskea sisäkkäisten silmukoiden työmäärän ja tunnistaa
  tavallisimpien rekursioyhtälöiden ratkaisut.
- Osaat selittää pahimman, keskimääräisen, satunnaistetun ja
  tasoitetun tapauksen erot ja kertoa, milloin kukin on oikea mittari.
- Osaat tunnistaa kasvuluokan mittaamalla operaatioiden määrän
  kaksinkertaistuvilla syötteillä.

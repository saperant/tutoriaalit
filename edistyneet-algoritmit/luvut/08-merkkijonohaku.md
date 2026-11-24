# Merkkijonohaku

Hahmon $P$ (pituus $m$) esiintymien etsiminen tekstistä $T$ (pituus
$n$) on tekstieditorien, `grep`-työkalun, virustorjunnan ja
DNA-analyysin perusoperaatio. Suora haku kokeilee jokaista
alkukohtaa. Satunnaisella tekstillä se on nopea, koska vertailu
epäonnistuu yleensä heti, mutta pahimmillaan se vie ajan $O(nm)$.
Tämän luvun algoritmit takaavat ajan $O(n + m)$. KMP ja Z-algoritmi
hyödyntävät hahmon rakennetta, ja Rabin–Karp vertaa hajautusarvoja.

## Suora haku ja sen pahin tapaus

```{.cpp tiedosto="esimerkit/08-kmp.cpp" osa="suora"}
```

Pahin syöte on teksti $a^n$ ja hahmo $a^{m-1}b$: jokainen alkukohta
vertaa $m$ merkkiä ennen epäonnistumista. Haku tekee hukkatyötä,
koska se unohtaa, mitä se juuri näki. Kun $m - 1$ merkkiä täsmäsi,
tiedetään tarkalleen, mitä tekstissä on, eikä niitä tarvitsisi lukea
uudelleen.

## Knuthin–Morrisin–Prattin algoritmi

KMP (Knuth, Morris ja Pratt 1977) laskee hahmosta *vikafunktion*.
$\text{vika}[j]$ on pisimmän sellaisen hahmon etuliitteen
$P[0..j]$ aidon etuliitteen pituus, joka on myös sen loppuliite. Kun
haku on täsmännyt $k$ merkkiä ja seuraava vertailu epäonnistuu, hahmon
$\text{vika}[k-1]$ ensimmäistä merkkiä täsmäävät edelleen. Haku jatkaa
siitä palaamatta tekstissä taaksepäin.

```{.cpp tiedosto="esimerkit/08-kmp.cpp" osa="vikafunktio"}
```

```{.cpp tiedosto="esimerkit/08-kmp.cpp" osa="vika"}
```

Vikafunktio lasketaan samalla algoritmilla kuin itse haku: hahmoa
haetaan itsestään. Aikaraja seuraa tasoitetusta argumentista (luku 5).
Täsmäävien merkkien määrä $k$ kasvaa enintään yhdellä tekstimerkkiä
kohden, ja jokainen epäonnistunut vertailu pienentää sitä. Kaikkiaan
vertailuja on siis enintään $2n$.

## Z-algoritmi

Z-funktio laskee jokaiselle kohdalle $i$ pisimmän sellaisen
merkkijonon pituuden $z[i]$, joka alkaa kohdasta $i$ ja on myös koko
merkkijonon etuliite. Algoritmi pitää yllä oikeimmalle ulottuvaa
löydettyä osumaa $[l, r)$. Sen sisällä $z[i]$ voidaan aloittaa jo
lasketusta arvosta $z[i - l]$, ja vain $r$:n ylittävä osa verrataan.
Haku laskee Z-funktion jonolle $P \cdot \# \cdot T$, missä $\#$ on
merkki, jota ei esiinny kummassakaan. Osuma on jokainen kohta, jossa
$z[i] = m$.

```{.cpp tiedosto="esimerkit/08-kmp.cpp" osa="z"}
```

## Vertailu ja pahin tapaus

Kolme toisistaan riippumatonta algoritmia ovat toistensa malleja.
Pieni aakkosto ($\{a\}$, $\{a, b\}$ tai $\{a, b, c\}$) tuottaa paljon
osittaisia osumia ja päällekkäisiä esiintymiä, joissa virheet
näkyvät. Testi ajaa 500 satunnaista tekstiä ja hahmoa, ja sen jälkeen
mitataan pahin tapaus:

```{.cpp tiedosto="esimerkit/08-kmp.cpp" osa="pahin"}
```

```{.tuloste tiedosto="esimerkit/08-kmp.odotettu"}
```

Pahimmassa tapauksessa suora haku tekee noin $nm \approx 10^8$
vertailua, KMP ja Z-algoritmi noin $2n$.

## Rabinin–Karpin algoritmi

Rabin–Karp (Karp ja Rabin 1987) laskee hahmosta ja jokaisesta
tekstin $m$ merkin ikkunasta *polynomihajautuksen*:
$h(s) = s_0 k^{m-1} + s_1 k^{m-2} + \cdots + s_{m-1} \pmod p$. Ikkunan
siirto päivittää arvon vakioajassa. Vanhimman merkin osuus vähennetään,
tulos kerrotaan $k$:lla ja uusi merkki lisätään. Kun arvot täsmäävät,
osuma varmistetaan vertaamalla merkkejä, koska eri merkkijonoilla voi
olla sama arvo.

```{.cpp tiedosto="esimerkit/08-rabinkarp.cpp" osa="rk"}
```

Modulina on Mersennen alkuluku $p = 2^{61} - 1$. Funktio `kerro()`
laskee tulon 128-bittisenä ja saa jakojäännöksen bittisiirroilla,
koska $2^{61} \equiv 1 \pmod p$. Funktio `summaa()` vähentää $p$:n
tarvittaessa. Kantaluku $k$ arvotaan. Kahden eri $m$-merkkisen
jonon erotus on enintään astetta $m - 1$ oleva polynomi muuttujan $k$
suhteen, ja sillä on modulo $p$ enintään $m - 1$ juurta. Satunnainen
$k$ osuu juureen todennäköisyydellä alle $m / p$. Tämä on
*universaalin hajautuksen* idea: takuu koskee jokaista syötettä,
koska satunnaisuus on algoritmissa eikä syötteessä.

Vertailutesti etsii esiintymät `std::string::find`-funktiolla ja
laskee lisäksi turhat ehdokkaat, eli hajautusarvon täsmäämiset ilman
osumaa. Niitä ei 300 tekstissä tullut yhtään.

## Ylivuotohajautuksen vaara

Moni toteutus laskee hajautuksen 64-bittisillä etumerkittömillä
luvuilla ja antaa ylivuodon hoitaa jakojäännöksen modulo $2^{64}$.
Tämä on nopeaa, mutta moduli ei ole alkuluku, eikä edellinen
juuriargumentti päde. *Thuen–Morsen jono* ($t_i$ = $i$:n ykkösbittien
määrän pariteetti) ja sen komplementti törmäävät millä tahansa
parittomalla kantaluvulla jo pituudella $2^{11}$. Parillinen kanta on
vielä huonompi, koska jokainen kertolasku siirtää vanhimmat merkit
sanan yläpään yli:

```{.cpp tiedosto="esimerkit/08-rabinkarp.cpp" osa="thue"}
```

Ohjelma vertaa 2048 merkin jonoja neljällä parittomalla kannalla,
joista viimeinen on arvottu:

```{.tuloste tiedosto="esimerkit/08-rabinkarp.odotettu"}
```

Jos hajautusarvoa käytetään ilman varmistusvertailua, esimerkiksi
tiedostojen tai osajonojen tunnistamiseen, tällainen törmäys antaa
väärän vastauksen. Hyökkääjä voi lisäksi rakentaa syötteen, joka
pakottaa jokaisen ikkunan ehdokkaaksi. Varmistusvertailun kanssa haku
on silloin $O(nm)$.

Rabin–Karp sopii erityisen hyvin moneen hahmoon kerralla. Kaikkien
samanmittaisten hahmojen hajautusarvot laitetaan hajautustauluun,
ja jokainen ikkuna tarkistetaan yhdellä haulla. Sama liukuva
hajautus on rsync-työkalun ja sisältöön perustuvan lohkojaon pohjana.

## Muut algoritmit

*Boyerin–Mooren* algoritmi vertaa hahmoa lopusta alkuun ja voi
hypätä epäonnistuessaan jopa $m$ merkkiä. Luonnollisella kielellä ja
pitkillä hahmoilla se lukee vain osan tekstistä, ja GNU grep perustuu
siihen. *Aho–Corasick* yleistää KMP:n moneen hahmoon: hahmoista
rakennetaan trie (luku 9) ja siihen vikalinkit, ja teksti luetaan
kerran kaikkia hahmoja vastaan. Virustorjunta ja tunkeutumisen
havaitseminen käyttävät sitä. Säännölliset lausekkeet ovat oma
aiheensa (taito *Kääntäjätekniikka*: automaatit).

| Algoritmi | Esikäsittely | Haku (pahin) | Erityistä |
|------------|----------|------------------|--------------------------------|
| suora | — | $O(nm)$ | nopea satunnaisella tekstillä |
| KMP | $O(m)$ | $O(n)$ | lukee tekstin kerran, sopii virtaan |
| Z-algoritmi | — | $O(n + m)$ | myös muut etuliitekyselyt |
| Rabin–Karp | $O(m)$ | $O(n)$ odotettu | monta hahmoa, liukuva hajautus |
| Boyer–Moore | $O(m + \sigma)$ | $O(n)$ muunnelmilla | hyppää, nopein pitkille hahmoille |
| Aho–Corasick | $O(\sum m_i)$ | $O(n + \text{osumat})$ | monta hahmoa yhdellä läpikäynnillä |

## Käytännössä

- Käytä kirjastoa, kun se riittää. `std::string_view::find` on
  yleensä suora haku, joka on optimoitu `memchr`-tyyppisillä
  vektorikäskyillä. `std::boyer_moore_searcher` (C++17) on
  pitkille hahmoille.
- Suora haku on pahimmassa tapauksessa neliöllinen. Jos syöte tulee
  ulkoa ja hahmo on pitkä, valitse algoritmi, jolla on lineaarinen
  takuu.
- Älä luota hajautusarvoon ilman vertailua, ellei virheen
  todennäköisyys ole laskettu ja hyväksytty. Arvo kanta satunnaisesti
  ja käytä alkulukumodulia.
- Vikafunktio ja Z-funktio ovat hyödyllisiä yksinäänkin: merkkijonon
  lyhin jakso on $m - \text{vika}[m-1]$, ja Z-funktio löytää kaikki
  kohdat, joissa merkkijono toistaa alkuaan.
- Testaa merkkijonoalgoritmit pienellä aakkostolla. Aakkoston
  $\{a, b\}$ satunnaiset jonot sisältävät paljon toistoa ja päällekkäisiä
  esiintymiä, kun taas $a$–$z$ tuottaa lähes pelkkiä ensimmäisen merkin
  epäonnistumisia.

## Itsearviointi

- Osaat laskea vikafunktion käsin ja selittää, miksi KMP ei koskaan
  palaa tekstissä taaksepäin.
- Osaat todistaa KMP:n vertailujen rajan $2n$ tasoitetulla
  argumentilla.
- Osaat toteuttaa Z-algoritmin ja käyttää sitä hakuun erottimen
  avulla.
- Osaat toteuttaa liukuvan polynomihajautuksen ja arvioida
  törmäystodennäköisyyden alkulukumodulilla ja satunnaisella kannalla.
- Osaat selittää, miksi hajautus modulo $2^{64}$ on haavoittuva, ja
  valita tehtävään sopivan hakualgoritmin.

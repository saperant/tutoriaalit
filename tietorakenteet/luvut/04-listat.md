# Linkitetyt listat

Linkitetty lista koostuu solmuista, joista kukin osoittaa seuraavaan.
Toisin kuin taulukossa, alkiot eivät ole muistissa peräkkäin, joten
indeksillä hakeminen vaatii listan läpikäynnin. Vastineeksi solmun voi
lisätä tai poistaa mistä kohdasta tahansa vakioajassa, kunhan kohta on
jo löydetty, eikä mikään muu solmu siirry muistissa. Jälkimmäinen
ominaisuus on usein tärkeämpi: osoitin solmuun pysyy voimassa, vaikka
listaa muutetaan.

| Operaatio | Taulukko | Yksöislinkitetty | Kaksoislinkitetty |
|-----------|----------|------------------|-------------------|
| $i$:s alkio | $O(1)$ | $O(i)$ | $O(i)$ |
| lisäys alkuun | $O(n)$ | $O(1)$ | $O(1)$ |
| lisäys loppuun | tasoitettu $O(1)$ | $O(1)$ häntäosoittimella | $O(1)$ |
| poisto, kun solmu tiedossa | $O(n)$ | $O(n)$ (edeltäjä haettava) | $O(1)$ |
| muisti alkiota kohti | alkio | alkio + osoitin + varauksen otsake | alkio + 2 osoitinta + otsake |

## Yksöislinkitetty lista

Esimerkki pitää tehtäviä prioriteettijärjestyksessä. Solmussa on data
ja osoitin seuraavaan:

```{.c tiedosto="esimerkit/04-lista.c" osa="solmu"}
```

Poisto on tavallisesti kirjoitettu näin: ensimmäinen solmu käsitellään
erikseen, koska sitä edeltää listan alkuosoitin eikä solmu.

```{.c tiedosto="esimerkit/04-lista.c" osa="erikoistapaus"}
```

Erikoistapauksen voi poistaa kokonaan. Kun silmukka kulkee
*linkkien* eikä solmujen yli, alun osoitin ja edellisen solmun
`seuraava`-kenttä ovat samanarvoisia: kumpikin on `Solmu *`-tyyppinen
muuttuja, jota muutetaan osoittimen `Solmu **p` kautta.

```{.c tiedosto="esimerkit/04-lista.c" osa="linkki"}
```

```{.tuloste tiedosto="esimerkit/04-lista.odotettu"}
```

Lisäysfunktio etsii ensimmäisen solmun, jonka prioriteetti on
*suurempi* kuin lisättävän, joten samanarvoiset pysyvät
saapumisjärjestyksessä (`varmuuskopio` ennen `päivitystä`). Tämä
vakaus on usein vaatimus ajastimissa ja tapahtumajonoissa. Tehtävät
tunnistetaan nimen osoittimella, ei merkkijonon sisällöllä, mikä riittää
tässä, koska nimet tulevat samasta taulukosta.

Lista pidetään järjestyksessä, joten pienimmän prioriteetin ottaminen
on $O(1)$, mutta lisäys on $O(n)$. Luvussa 9 sama tehtävä tehdään
keolla, jossa molemmat ovat $O(\log n)$.

## Kaksoislinkitetty lista ja tunnussolmu

Kaksoislinkitetyssä listassa solmulla on osoitin myös edeltäjäänsä.
Silloin solmun voi irrottaa tietämättä, missä listassa se on tai mikä
sitä edeltää. Hinta on toinen osoitin jokaisessa solmussa ja kaksi
päivitettävää linkkiä jokaisessa muutoksessa.

Rajatapaukset – tyhjä lista, ensimmäinen ja viimeinen solmu –
poistuvat *tunnussolmulla* (engl. sentinel): listassa on aina yksi
ylimääräinen solmu, joka ei sisällä dataa. Lista on rengas, jonka
tunnussolmun `seuraava` on ensimmäinen alkio ja `edellinen` viimeinen.
Tyhjässä listassa tunnussolmu osoittaa itseensä. Koska jokaisella
oikealla solmulla on aina edeltäjä ja seuraaja, irrotus ja lisäys ovat
kahden rivin operaatioita ilman ainuttakaan `if`-lausetta.

Esimerkkinä on LRU-välimuisti (engl. least recently used). Välimuistiin
mahtuu kolme sivua; kun se on täynnä, pisimpään käyttämättä ollut sivu
poistetaan. Lista pitää sivut käyttöjärjestyksessä, ja taulukko löytää
sivun solmun suoraan:

```{.c tiedosto="esimerkit/04-lru.c" osa="rakenne"}
```

Haku siirtää osuman listan alkuun. Hudin sattuessa ladataan uusi sivu
ja täydestä välimuistista irrotetaan listan viimeinen solmu, jota
käytetään uudelleen:

```{.c tiedosto="esimerkit/04-lru.c" osa="hae"}
```

```{.tuloste tiedosto="esimerkit/04-lru.odotettu"}
```

Kumpikaan rakenne ei yksin riittäisi. Lista ilman indeksiä vaatisi
haun $O(n)$-ajassa; indeksi ilman listaa ei tietäisi, mikä sivu on
vanhin. Yhdessä ne antavat kaikki operaatiot vakioajassa. Oikeassa
välimuistissa indeksi on hajautustaulu (luku 6), koska avaimia on
liikaa suoraan taulukkoon.

## Tunkeileva lista

Edellisissä esimerkeissä lista omistaa solmunsa ja data on solmun
sisällä. *Tunkeilevassa* listassa (engl. intrusive list) suunta on
päinvastainen: linkkikentät ovat osa datatietuetta, eikä listalla ole
omia solmuja lainkaan. Listaoperaatiot tuntevat vain linkkityypin:

```{.c tiedosto="esimerkit/04-tunkeileva.c" osa="linkki"}
```

Makro `SISALTAVA` (Linuxin ytimessä `container_of`) laskee
linkkikentän osoitteesta sen sisältävän tietueen osoitteen
vähentämällä kentän siirtymän `offsetof`-makrolla. Tietueessa voi olla
monta linkkiä, jolloin se voi olla monessa listassa yhtä aikaa:

```{.c tiedosto="esimerkit/04-tunkeileva.c" osa="tietue"}
```

Läpikäynti kulkee linkkien yli ja muuntaa kunkin linkin tietueeksi:

```{.c tiedosto="esimerkit/04-tunkeileva.c" osa="lapikaynti"}
```

```{.tuloste tiedosto="esimerkit/04-tunkeileva.odotettu"}
```

Tunkeilevalla listalla on kolme etua. Listaan lisääminen ei varaa
muistia, joten se ei voi epäonnistua – tärkeää käyttöjärjestelmän
ytimessä ja keskeytyskäsittelijöissä. Kun tietue tunnetaan, sen voi
irrottaa kaikista listoista vakioajassa ilman hakua. Ja data ja linkit
ovat samassa välimuistirivissä. Haittana on, että tietueen on
tiedettävä etukäteen, missä listoissa se voi olla, ja että
tyyppiturvallisuus jää ohjelmoijan vastuulle: `SISALTAVA` hyväksyy
väärän tyypin tai kentän ilman varoitusta.

## Listan invariantti

Kaksoislinkitetyn rengaslistan invariantti on, että jokaiselle
solmulle `s` pätee `s->seuraava->edellinen == s` ja
`s->edellinen->seuraava == s`, ja että tunnussolmusta lähtevä
läpikäynti palaa tunnussolmuun $n + 1$ askeleessa. Tarkistusfunktio
kulkee renkaan ympäri, laskee solmut ja vertaa tulosta tallennettuun
kokoon. Silmukan voi rajata esimerkiksi $n + 1$ askeleeseen, jotta
rikkinäinen rengas ei jumita testiä. Yksöislinkitetyn listan syklin
löytää Floydin algoritmilla: kaksi osoitinta, joista toinen etenee
kaksi askelta kerrallaan, kohtaavat vain, jos listassa on sykli.

## Käytännössä

- **Oletuksena taulukko.** Lista kannattaa valita vasta, kun tarvitaan
  pysyviä osoittimia alkioihin tai vakioaikaista poistoa keskeltä, kun
  alkio jo tunnetaan.
- **Osoitin osoittimeen** poistaa yksöislinkitetyn listan
  alkupään erikoistapauksen sekä lisäyksestä että poistosta.
- **Tunnussolmu** poistaa kaksoislinkitetyn listan rajatapaukset.
  Tyhjä lista on rengas, joka osoittaa itseensä.
- **Tunkeileva lista** sopii, kun samat tietueet ovat monessa
  listassa tai kun lisäys ei saa varata muistia.
- **Vapauta seuraava ensin talteen.** Listaa vapautettaessa
  `s->seuraava` on luettava ennen `free(s)`-kutsua; sanitoija havaitsee
  virheen, mutta vain jos se on päällä.

## Itsearviointi

- Osaat kirjoittaa yksöislinkitetyn listan lisäyksen ja poiston
  osoitin osoittimeen -tekniikalla ilman alkupään erikoistapausta.
- Osaat toteuttaa kaksoislinkitetyn rengaslistan tunnussolmulla ja
  irrottaa solmun vakioajassa.
- Osaat yhdistää listan ja indeksin niin, että LRU-välimuistin kaikki
  operaatiot ovat vakioaikaisia.
- Osaat selittää, miten `container_of`-tyyppinen makro löytää
  tietueen linkkikentän osoitteesta.

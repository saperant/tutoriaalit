# Atomiset operaatiot

`std::atomic<T>` tekee yksittäisestä muuttujasta jaettavan ilman
lukkoa: jokainen operaatio on jakamaton, ja muistijärjestys määrää, mitä
muuta se tekee näkyväksi. Tämä luku käy läpi operaatiot ja niiden hinnan,
rakentaa niistä spinlukon ja näyttää, miten tavallista dataa käsitellään
hetkellisesti atomisesti `std::atomic_ref`illä.

## Mitä voi tehdä atomiseksi

`std::atomic<T>` hyväksyy minkä tahansa triviaalisti kopioitavan tyypin.
Kokonaisluvut, osoittimet ja C++20:sta alkaen liukuluvut saavat lisäksi
aritmeettiset operaatiot. Kaikki atomiset tyypit eivät kuitenkaan ole
**lukottomia**: jos suoritin ei osaa käsitellä tyypin kokoista arvoa
yhdellä käskyllä, toteutus käyttää piilotettua lukkoa (libatomic):

```{.cpp tiedosto="esimerkit/05-atomiset.cpp" osa="lukottomuus"}
```

x86-64 käsittelee atomisesti enintään 8 tavua tavallisilla käskyillä ja
16 tavua käskyllä `cmpxchg16b`, jota GCC ei käytä oletuksena. Lukolla
toteutettu "atominen" muuttuja ei ole turvallinen signaalinkäsittelijässä
eikä prosessien välisessä jaetussa muistissa, ja se on hidas. Jos
lukottomuus on vaatimus, se tarkistetaan käännösaikana:
`static_assert(std::atomic<T>::is_always_lock_free)`.

## Operaatiot

| Operaatio | Merkitys |
|----------------------|---------------------------|
| `load`, `store` | Luku ja kirjoitus |
| `exchange(x)` | Kirjoittaa x:n ja palauttaa vanhan arvon |
| `fetch_add`, `fetch_sub`, `fetch_and`, `fetch_or`, `fetch_xor` | Päivitys, palauttaa vanhan arvon |
| `++`, `--`, `+=` jne. | Kuten `fetch_*`, mutta palauttavat uuden arvon |
| `compare_exchange_weak/strong(odotettu, uusi)` | Kirjoittaa uuden, jos arvo on odotettu; muuten päivittää `odotettu`n |
| `wait(vanha)`, `notify_one`, `notify_all` | C++20: odota, kunnes arvo muuttuu |

Kaikki muu rakennetaan **compare_exchange-silmukalla** (CAS): lue arvo,
laske uusi, yritä vaihtaa, ja yritä uudelleen, jos joku ehti väliin.
Atominen maksimi on tavallinen esimerkki:

```{.cpp tiedosto="esimerkit/05-atomiset.cpp" osa="maksimi"}
```

Epäonnistunut `compare_exchange` kirjoittaa muuttujan nykyisen arvon
parametriin `nyt`, joten silmukka ei lue sitä erikseen. `weak`-versio saa
epäonnistua aiheetta (*spurious failure*), mikä tekee siitä ARMin
LL/SC-käskyillä nopeamman. Silmukassa se ei haittaa. Yksittäinen
kertayritys, jonka epäonnistumisella on merkitys, käyttää `strong`-versiota.

```{.cpp tiedosto="esimerkit/05-atomiset.cpp" osa="operaatiot"}
```

```{.tuloste tiedosto="esimerkit/05-atomiset.odotettu"}
```

Laskuri käyttää `relaxed`-järjestystä, koska kukaan ei päättele sen
arvosta mitään muusta datasta. Lopullinen arvo luetaan säikeiden
`join`in jälkeen, joten se on taatusti täsmälleen 40 000. Liukulukujen
`fetch_add` on CAS-silmukka laitteistossa tai kirjastossa. Esimerkin summa
on tarkka, koska 0,5:n monikerrat ovat tarkasti esitettäviä; yleisessä
tapauksessa rinnakkainen liukulukusumma riippuu järjestyksestä.

## Atomisuuden hinta

Atominen luku–kirjoitus-operaatio (`fetch_add`, `exchange`, CAS) maksaa
jo kilpailemattomana enemmän kuin tavallinen kirjoitus, koska suoritin
tyhjentää kirjoituspuskurinsa ja varaa välimuistirivin yksinoikeudella.
Kilpailtuna hinta moninkertaistuu: rivi siirtyy ytimeltä toiselle
koherenssiprotokollan viesteillä (*cache line ping-pong*), ja jokainen
siirto kestää satoja sykliä, eri piirisirujen välillä enemmän. Siksi
yksi jaettu laskuri, jota kaikki säikeet kasvattavat tiiviissä
silmukassa, voi hidastaa ohjelmaa enemmän kuin säikeet nopeuttavat sitä.
Johdannon summaesimerkki välttää tämän laskemalla paikallisesti ja
kirjoittamalla kerran.

## Spinlukko

Spinlukko odottaa pyörimällä silmukassa eikä nukahda. Se on oikea valinta
vain, kun lukkoa pidetään hyvin lyhyen aikaa ja säikeitä on enintään yhtä
monta kuin ytimiä, esimerkiksi käyttöjärjestelmän ytimessä keskeytykset
estettyinä. Rakenne näyttää atomisten operaatioiden ja järjestysten
yhteistyön:

```{.cpp tiedosto="esimerkit/05-spinlukko.cpp" osa="spinlukko"}
```

`test_and_set` asettaa lipun ja palauttaa vanhan arvon. Lukon saanut säie
näki arvon `false`. Acquire lukitessa ja release vapauttaessa tekevät
lukosta oikean: kriittisen alueen kirjoitukset tapahtuvat ennen
vapautusta ja siten ennen seuraavan säikeen lukitusta. Sisempi silmukka
vain lukee lippua (*test and test-and-set*): jokainen `test_and_set` on
kirjoitus, joka siirtää välimuistirivin yksinoikeudella pyörivälle
ytimelle, kun taas lukijat voivat jakaa rivin.

Käyttäjätilan spinlukolla on vaarallinen heikkous: jos lukkoa pitävä säie
vuorontuu pois, muut pyörivät turhaan koko aikaviipaleensa ajan. Ytimessä
näin ei käy, koska lukon haltijaa ei voi keskeyttää. Käyttäjätilassa
ratkaisu on lakata pyörimästä ja pyytää ydintä herättämään, kun lukko
vapautuu. C++20:n `wait` ja `notify_one` tekevät sen (Linuxissa
futexilla, ks. taito *Käyttöjärjestelmät*):

```{.cpp tiedosto="esimerkit/05-spinlukko.cpp" osa="odottava"}
```

Tämä ei ole enää spinlukko vaan yksinkertainen nukkuva lukko: hinta on
järjestelmäkutsu jokaisessa vapautuksessa. `std::mutex` (glibc:n
toteutus) yhdistää molemmat: se pyörii lyhyesti, nukahtaa sitten
futexiin ja tekee herätyskutsun vain, jos joku odottaa. Se on lähes aina
parempi kuin kumpikaan oma lukko, ja oma spinlukko on perusteltu vain
mittausten perusteella.

```{.cpp tiedosto="esimerkit/05-spinlukko.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/05-spinlukko.odotettu"}
```

## `std::atomic_ref`: atominen hetken ajan

Usein data on tavallista ja vain osa ohjelmasta käsittelee sitä
rinnakkain. `std::atomic_ref` (C++20) tekee tavallisesta oliosta atomisen
niin kauan kuin viittaus on olemassa. Kaikkien samaan aikaan olion
käsittelevien on käytettävä `atomic_ref`iä; rinnakkaisen vaiheen jälkeen
oliota voi taas käyttää tavallisesti:

```{.cpp tiedosto="esimerkit/05-atomic-ref.cpp" osa="histogrammi"}
```

```{.tuloste tiedosto="esimerkit/05-atomic-ref.odotettu"}
```

Esimerkin ensimmäisessä versiossa lambda sieppasi kaiken viittauksena
(`[&, s]`), myös muuttujan `pala`, joka oli määritelty säiesäiliön
jälkeen. Se tuhoutui ennen kuin säikeet oli odotettu, ja Clangin
AddressSanitizer raportoi virheen `stack-use-after-scope`. GCC:llä sama
virhe ei näkynyt. Nimetyt sieppaukset olisivat estäneet sen.

Histogrammi kertoo myös hinnasta: 16 lokeroa vie 64 tavua eli yhden tai
kaksi välimuistiriviä, joten kaikki säikeet kilpailevat samoista riveistä.
Nopeampi ratkaisu on säiekohtainen histogrammi, joka lasketaan yhteen
lopuksi.

## Käytännössä

- **Atominen muuttuja on yksi arvo.** Kaksi atomista muuttujaa eivät
  muodosta atomista paria: niiden välinen invariantti tarvitsee lukon tai
  yhden atomisen arvon, johon molemmat on pakattu.
- **CAS-silmukka on yleistyökalu.** Lue, laske, vaihda, toista. Silmukan
  rungossa ei tehdä sivuvaikutuksia, koska se voidaan suorittaa monta
  kertaa.
- **Varmista lukottomuus käännösaikana**, jos sitä tarvitaan
  (`is_always_lock_free`). Muuten 16 tavun tai suuremmat rakenteet
  käyttävät piilolukkoa.
- **Vältä jaettua kuumaa muuttujaa.** Laske paikallisesti ja yhdistä
  lopuksi. Yksi jaettu laskuri skaalautuu huonommin kuin yksi säie.
- **`std::mutex` ennen omaa spinlukkoa.** Spinlukko on perusteltu
  vain, kun lukitus on mitattu pullonkaulaksi ja säikeitä ei ole enempää
  kuin ytimiä.

## Itsearviointi

- Osaat tarkistaa, onko atominen tyyppi lukoton, ja kertoa, mitä
  seuraa, jos se ei ole.
- Osaat kirjoittaa compare_exchange-silmukan ja valita `weak`- ja
  `strong`-version välillä.
- Osaat toteuttaa spinlukon `atomic_flag`illa, perustella sen
  muistijärjestykset ja kertoa, miten nukkuva lukko eroaa siitä.
- Osaat käyttää `std::atomic_ref`iä tavalliseen dataan ja kertoa, milloin
  sen käyttö on turvallista.

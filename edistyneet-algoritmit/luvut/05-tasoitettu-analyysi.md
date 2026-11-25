# Tasoitettu analyysi

Taito *Tietorakenteet* mittasi dynaamisen taulukon kopioiden määrän
eri kasvatuskertoimilla, ja *Algoritmit* määritteli tasoitetun ajan.
Tämä luku antaa menetelmät, joilla tasoitettu raja todistetaan, ja
tarkistaa todistuksen kirjanpidon ohjelmalla lisäys lisäykseltä.

Dynaamisen taulukon `push_back` on yleensä halpa, mutta joskus se
kopioi koko taulukon. Pahimman tapauksen analyysi antaa yhdelle
lisäykselle ajan $O(n)$, ja $n$ lisäykselle se antaisi
$O(n^2)$. Todellisuudessa $n$ lisäystä vie $O(n)$, koska kalliit
lisäykset ovat harvinaisia. *Tasoitettu analyysi* (engl. *amortized
analysis*) tekee tästä havainnosta täsmällisen. Se rajaa
*operaatiosarjan* kokonaishinnan eikä yksittäisen operaation hintaa.
Satunnaisuutta ei tarvita. Tasoitettu raja on takuu jokaiselle
sarjalle, toisin kuin odotusarvo.

Taito *Algoritmit* esitteli käsitteen dynaamisen taulukon
yhteydessä. Tässä luvussa käydään läpi kolme menetelmää todistaa
tasoitettu raja ja niiden sudenkuopat.

## Kolme menetelmää

**Kokonaismenetelmä** (engl. *aggregate method*) laskee koko sarjan
hinnan suoraan. Kun kapasiteetti kaksinkertaistuu, $n$ lisäyksen
kopioiden määrä on enintään $1 + 2 + 4 + \cdots + n/2 < n$. Kopioita on
siis keskimäärin alle yksi lisäystä kohden.

**Kirjanpitomenetelmä** (engl. *accounting method*) perii jokaiselta
operaatiolta kiinteän maksun, joka voi olla suurempi kuin operaation
todellinen hinta. Ylijäämä talletetaan rakenteeseen *krediitiksi*,
ja kalliit operaatiot maksetaan sillä. Dynaamisessa taulukossa
lisäys maksaa 3. Yksi kuluu lisäykseen itseensä, yksi alkion omaan
tulevaan kopiointiin ja yksi jonkin vanhemman alkion kopiointiin.
Vanhemmat alkiot ovat käyttäneet krediittinsä edellisessä
kasvatuksessa.

**Potentiaalimenetelmä** sitoo krediitin rakenteen tilaan. Valitaan
funktio $\Phi$, joka liittää jokaiseen tilaan ei-negatiivisen luvun.
Operaation *tasoitettu hinta* on

$$\hat c_i = c_i + \Phi(D_i) - \Phi(D_{i-1}).$$

Summa teleskooppautuu:
$\sum \hat c_i = \sum c_i + \Phi(D_n) - \Phi(D_0)$. Jos
$\Phi(D_n) \ge \Phi(D_0)$, tasoitetut hinnat ovat todellisten hintojen
yläraja. Halpa operaatio kasvattaa potentiaalia, ja kallis operaatio
käyttää sitä. Menetelmän taito on oikean $\Phi$:n löytäminen.

## Dynaaminen taulukko

Kustannusmalli laskee lisäyksen hinnaksi 1 ja kasvatuksen hinnaksi
kopioitavien alkioiden määrän:

```{.cpp tiedosto="esimerkit/05-taulukko.cpp" osa="malli"}
```

Kasvatuskertoimen valinnalla on suuri merkitys. Kerroin 2 antaa noin
yhden kopion lisäystä kohden. Kerroin 1,5 antaa noin kaksi, mutta
vapautunut muisti voidaan käyttää uudelleen (libstdc++ ja libc++
käyttävät kerrointa 2, MSVC kerrointa 1,5). Vakiolisäys sen sijaan
antaa neliöllisen kokonaishinnan, koska kopioiden määrä kasvaa
lineaarisesti lisäysten määrän mukana. Esimerkin tulosteen kolme
ensimmäistä riviä mittaavat tämän miljoonalla lisäyksellä (vakiolisäys
sadallatuhannella).

Potentiaalifunktio $\Phi = 2 \cdot \text{koko} - \text{kapasiteetti}$ on
nolla, kun taulukko on puoliksi täynnä, ja yhtä suuri kuin koko, kun
taulukko on täynnä. Halpa lisäys kasvattaa
sitä kahdella, joten tasoitettu hinta on $1 + 2 = 3$. Kasvatus maksaa
$\text{koko} + 1$ ja pienentää potentiaalia arvosta koko arvoon 2,
joten tasoitettu hinta on $(\text{koko} + 1) + 2 - \text{koko} = 3$.
Ohjelma tarkistaa tämän jokaiselle lisäykselle:

```{.cpp tiedosto="esimerkit/05-taulukko.cpp" osa="potentiaali"}
```

Alussa $\Phi = -1$, koska tyhjän taulukon kapasiteetti on 1. Arvo
on vakio, joten se ei muuta rajaa.

## Kutistaminen

Taulukko, josta poistetaan alkioita, kannattaa kutistaa, jotta muisti
vapautuu. Luonteva sääntö "puolita, kun puolet on vapaana" rikkoo
kuitenkin tasoitetun rajan. Täysi taulukko, johon lisätään ja josta
poistetaan vuorotellen yksi alkio, kasvaa ja kutistuu joka kerta:

```{.cpp tiedosto="esimerkit/05-taulukko.cpp" osa="kutistus"}
```

```{.tuloste tiedosto="esimerkit/05-taulukko.odotettu"}
```

Korjaus on *hystereesi*: puolitetaan vasta, kun taulukko on
neljäsosan täynnä. Kasvatuksen ja kutistuksen välissä on silloin
aina vähintään koko/2 halpaa operaatiota, jotka maksavat seuraavan
kalliin. Sama periaate koskee hajautustaulun uudelleenhajautusta ja
mitä tahansa rakennetta, joka muuttaa kokoaan kynnysarvon kohdalla.

## Binäärilaskuri

$k$-bittisen laskurin kasvatus vaihtaa lopun ykköset nolliksi ja
ensimmäisen nollan ykköseksi. Pahimmillaan se vaihtaa kaikki $k$
bittiä. Potentiaaliksi valitaan ykkösbittien määrä. Kasvatus, joka
nollaa $t$ ykköstä, maksaa $t + 1$ ja muuttaa potentiaalia
$-t + 1$:llä, joten tasoitettu hinta on täsmälleen 2:

```{.cpp tiedosto="esimerkit/05-laskuri.cpp" osa="laskuri"}
```

```{.cpp tiedosto="esimerkit/05-laskuri.cpp" osa="tasoitettu"}
```

Vähennysoperaatio rikkoo analyysin. Rajalla $2^{20} - 1 \leftrightarrow
2^{20}$ sekä vähennys että kasvatus vaihtavat 21 bittiä, eikä
potentiaali auta, koska vähennys kasvattaa ykkösten määrää yhtä
paljon kuin kasvatus sitä pienentää:

```{.cpp tiedosto="esimerkit/05-laskuri.cpp" osa="vuorottelu"}
```

```{.tuloste tiedosto="esimerkit/05-laskuri.odotettu"}
```

Tasoitettu raja koskee siis aina tiettyä operaatiojoukkoa. Uuden
operaation lisääminen rajapintaan voi kumota sen.

## Tasoitettu, odotettu ja pahin tapaus

| Raja | Mitä luvataan | Esimerkki |
|------|---------------|-----------|
| pahin tapaus | jokainen operaatio | punamustan puun lisäys $O(\log n)$ |
| tasoitettu | jokainen sarja, keskimäärin operaatiota kohden | `push_back` $O(1)$, splay-puu $O(\log n)$ |
| odotusarvo | keskiarvo algoritmin omien arvontojen yli | treap $O(\log n)$, pikavalinta $O(n)$ |
| keskimääräinen tapaus | keskiarvo oletetun syötejakauman yli | tavallinen hakupuu satunnaisella syötteellä |

Reaaliaikajärjestelmälle tasoitettu raja ei riitä. Yksittäinen
$O(n)$:n kasvatus voi rikkoa määräajan, vaikka keskiarvo on hyvä.
Silloin käytetään rakenteita, jotka jakavat kalliin työn vähitellen
monelle operaatiolle (engl. *deamortization*). Esimerkiksi taulukko
voi kopioida vanhasta tilasta uuteen kaksi alkiota jokaisen lisäyksen
yhteydessä.

## Käytännössä

- Varaa tila etukäteen (`reserve`), kun lopullinen koko tiedetään.
  Tasoitettu $O(1)$ on silti kopioita ja varauksia, ja ne näkyvät
  profiilissa.
- Tarkista, mikä on tasoitetun rajan operaatiojoukko. Jos rajapintaan
  tulee uusi operaatio, kuten vähennys, kutistus tai kopiointi,
  analyysi on tehtävä uudelleen.
- Käytä kynnyksissä hystereesiä aina, kun rakenne kasvaa ja kutistuu.
  Sama koskee välimuistien tyhjennystä ja säikeiden määrän säätöä.
- Reaaliaikaisissa ja viivekriittisissä palveluissa mittaa
  persentiilit, älä keskiarvoja. Tasoitettu raja kertoo keskiarvosta,
  mutta harvinaiset kalliit operaatiot näkyvät 99. persentiilissä.
- Potentiaalin valinta on usein "mikä tahansa, joka kasvaa halvoissa
  ja putoaa kalliissa operaatioissa". Hyvä ehdokas on kalliin työn
  määrä, joka odottaa tekemistä: täysien paikkojen, ykkösbittien tai
  pitkien polkujen määrä.

## Itsearviointi

- Osaat todistaa tasoitetun rajan kokonais-, kirjanpito- ja
  potentiaalimenetelmällä.
- Osaat laskea dynaamisen taulukon kopioiden määrän eri
  kasvatuskertoimilla ja selittää, miksi vakiolisäys on neliöllinen.
- Osaat valita potentiaalifunktion dynaamiselle taulukolle ja
  binäärilaskurille ja tarkistaa tasoitetun hinnan ohjelmallisesti.
- Osaat näyttää, miksi kutistus puolillaan rikkoo tasoitetun rajan ja
  miten hystereesi korjaa sen.
- Osaat erottaa tasoitetun, odotetun, keskimääräisen ja pahimman
  tapauksen rajan ja valita niistä sovellukseen sopivan.

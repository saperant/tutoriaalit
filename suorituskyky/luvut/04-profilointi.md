# Profilointi

Mittaus kertoo, kuinka kauan ohjelma kestää. Profiili kertoo, mihin
aika kuluu. Ilman profiilia optimoija korjaa sitä, mitä epäilee, ja
epäily osuu harvoin oikeaan. Tässä luvussa profiloidaan lokianalyysi
kolmella työkalulla, ja jokainen niistä näyttää eri puolen samasta
ohjelmasta.

## Kolme tapaa profiloida

| Tapa | Työkalu | Miten | Hinta ja rajoitukset |
|--------------|--------------------|------------------------------|------------------------------|
| Näytteistys | `perf`, gprofin ajat | Keskeytys esim. 1000 kertaa sekunnissa, ohjelmalaskurin arvo talteen | Pieni hidastus; tilastollinen, harvinaiset funktiot jäävät näkymättä |
| Instrumentointi | gprofin kutsumäärät (`-pg`), `-finstrument-functions` | Kääntäjä lisää laskurin funktioiden alkuun | Tarkat kutsumäärät; pienet funktiot hidastuvat suhteessa eniten |
| Simulointi | Valgrind: Callgrind, Cachegrind | Ohjelma ajetaan virtuaalikoneessa käsky kerrallaan | 20–100 kertaa hitaampi; deterministinen, mutta mittaa käskyjä, ei aikaa |

Näytteistävä profiloija mittaa sitä, mikä merkitsee eli aikaa, mutta
tulos vaihtelee ajosta toiseen. Simuloiva profiloija antaa joka kerta
samat luvut ja näkee jokaisen käskyn, mutta käskyjen määrä on eri asia
kuin aika: muistihuti maksaa satoja jaksoja, yksi käsky vain yhden.

## Esimerkkiohjelma

Ohjelma lukee verkkopalvelimen lokia ja laskee jokaisen asiakkaan
pyynnöt ja siirretyt tavut. Rajapinnalla on kolme toteutusta, jotka
kehitetään tämän luvun aikana:

```{.c tiedosto="esimerkit/04-lokit/loki.h"}
```

Ensimmäinen versio on kirjoitettu selkeästi: rivi jäsennetään
`sscanf`-funktiolla ja asiakas etsitään taulukosta.

```{.c tiedosto="esimerkit/04-lokit/hidas.c" osa="sscanf"}
```

```{.c tiedosto="esimerkit/04-lokit/hidas.c" osa="etsi"}
```

Lineaarinen haku tekee jokaiselle riville keskimäärin puolet niin
monta merkkijonovertailua kuin asiakkaita on. Kokenut lukija arvaa
heti, että se on pullonkaula. Profiloidaan ennen kuin korjataan.

## gprof

gprof on GNU:n vanha mutta kaikkialla saatavilla oleva profiloija.
Ohjelma käännetään lipulla `-pg`, jolloin kääntäjä lisää jokaisen
funktion alkuun kutsulaskurin ja ajonaikainen kirjasto ottaa
ohjelmalaskurista näytteen sadasti sekunnissa. Ajo kirjoittaa
tiedoston `gmon.out`, jonka `gprof` muuttaa raportiksi:

```{.makefile tiedosto="esimerkit/Makefile" osa="profiilit"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-gprof.txt"}
```

Ohjelman omista funktioista näytteitä sai vain lineaarinen haku, ja
arvaus näyttää osuneen. (Merkintään `_init` gprof kirjaa näytteet,
jotka osuvat kirjastokutsujen hyppytauluun.) Mutta raportti kattaa
vain muutaman sadasosasekunnin, vaikka ajo kesti noin 300
millisekuntia. Ero selittyy sillä, että
gprof näytteistää vain ohjelman omaa koodia. Aika, joka kuluu jaetussa
C-kirjastossa, kuten `sscanf`-, `strlen`- ja `strcmp`-funktioissa,
ei näy raportissa lainkaan. Kutsumäärät (`calls`) ovat sen sijaan
tarkkoja, koska ne tulevat instrumentoinnista.

## Callgrind

Callgrind ajaa ohjelman Valgrindin virtuaalikoneessa ja laskee jokaisen
funktion suorittamat käskyt (Ir, *instructions read*) sekä kutsut
funktioiden välillä. Se näkee myös kirjastot. Kumulatiivinen
(engl. inclusive) kustannus sisältää funktion itse suorittamat
käskyt ja kaikkien sen kutsumien funktioiden käskyt:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-callgrind.txt"}
```

```{.dot tiedosto="kaaviot/04-kutsupuu.dot" otsikko="Sama tuloste kutsupuuna: solmun luku on kumulatiivinen osuus käskyistä ja nuolen paksuus kutsun osuus. Yli kolmanneksen vievät funktiot on korostettu"}
```

Kuva on nyt toinen. Lineaarinen haku vie noin puolet käskyistä, mutta
`sscanf` vie lähes saman verran, ja sen sisällä lähes kaikki menee
`strlen`-funktioon. glibcin `sscanf` käsittelee merkkijonoa kuin
tiedostoa ja laskee aluksi sen pituuden, ja syöte on koko jäljellä
oleva loki eikä vain yksi rivi. Jokainen rivi käy siis läpi kaikki
seuraavat rivit: $n$ rivin loki maksaa $O(n^2)$ merkkiä. Tämä on
johdannossa mainittu latausruudun virhe.

Käskymäärä aliarvioi vielä `strlen`-funktion osuuden ajasta. Se
käyttää AVX2-käskyjä, jotka käsittelevät 32 tavua kerralla, joten
käskyjä on vähän, mutta jokainen tavu on luettava muistista. Callgrind
laskee käskyt, ei muistin odottamista. Sen vuoksi Callgrindin luvut
näyttävät, *missä* työtä tehdään, ja ajoitusmittaus näyttää, *paljonko*
se maksaa.

## Ensimmäinen korjaus

Jäsennettävä rivi kopioidaan omaan puskuriinsa, jolloin `sscanf`
laskee vain rivin pituuden:

```{.c tiedosto="esimerkit/04-lokit/hidas.c" osa="kopio"}
```

Callgrindin oma (engl. exclusive, self) kustannus kertoo, mitkä
funktiot suorittavat käskyt itse:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-puskuroitu.txt"}
```

`strlen` on kadonnut listalta, ja nyt pullonkaula on se, jota alun
perin epäiltiin: lineaarinen haku ja sen kutsuma `strcmp` vievät
kolme neljäsosaa käskyistä.

## Toinen korjaus

Asiakkaat tallennetaan hajautustauluun, jonka avain on IPv4-osoite
32-bittisenä lukuna. Merkkijonojen vertailu korvautuu kokonaislukujen
vertailulla, ja haku vie keskimäärin vakioajan. Samalla `sscanf`
korvataan pienellä jäsentimellä, joka lukee vain tarvittavat kentät:

```{.c tiedosto="esimerkit/04-lokit/nopea.c" osa="hajautus"}
```

```{.c tiedosto="esimerkit/04-lokit/nopea.c" osa="jasenna"}
```

Kaikki kolme toteutusta testataan samalla lokilla, ja tulosten on
oltava samat:

```{.c tiedosto="esimerkit/04-lokit/main.c" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/04-lokit.odotettu"}
```

Mittaus kirjoittajan koneella:

```{.tuloste tiedosto="esimerkit/tulokset/04-lokit.txt"}
```

Ensimmäinen korjaus oli yhden rivin kokoinen, toinen pienen
tietorakenteen kokoinen, ja yhdessä ne nopeuttivat ohjelmaa noin sata
kertaa. Kumpikaan ei ollut mikro-optimointi: molemmat poistivat
asymptoottisesti liikaa työtä. Profiloinnin tärkein tulos on usein
juuri tällainen löytö.

## perf

Linuxin `perf` näytteistää koko järjestelmää ytimen avulla: omaa
koodia, kirjastoja ja ydintä, ilman uudelleenkäännöstä. Se käyttää
suorittimen *suorituskykylaskureita* (engl. performance monitoring
counters), jotka laskevat laitteistotapahtumia: jaksoja, käskyjä,
välimuistihutia ja väärin ennustettuja haaroja. Laskurit eivät
yleensä ole käytettävissä konteissa ja virtuaalikoneissa, joten tämän
paketin esimerkit eivät aja perfiä; omalla Linux-koneella komennot
toimivat näin:

```text
perf stat ./bin/lokit --aja hidas 20000 3000
perf stat -e cycles,instructions,cache-misses,branch-misses ./ohjelma
perf record -g ./bin/lokit --aja hidas 20000 3000
perf report                      # interaktiivinen raportti
perf annotate etsi_lineaarisesti # käskykohtaiset näytteet
```

`perf stat` tulostaa laskurien arvot koko ajolta. Tärkeimmät rivit:

| Laskuri | Mitä kertoo | Mitä seuraavaksi |
|----------------------|------------------------------|------------------------------|
| `task-clock` | Prosessiaika ja käytettyjen ytimien määrä | Verrattava seinäkelloon |
| `cycles`, `instructions` | Jaksot ja käskyt; suhde on IPC (käskyä jaksossa) | IPC alle 1: odotetaan muistia tai haaroja |
| `cache-misses` | Viimeisen tason välimuistin hudit | Paljon: datan asettelu (luvut 5 ja 6) |
| `branch-misses` | Väärin ennustetut haarat | Yli prosentti haaroista: luku 7 |
| `page-faults` | Sivuvirheet | Paljon: muistinvaraus (luku 10) |

Nykyinen suoritin pystyy neljään tai useampaan käskyyn jaksossa. IPC
noin 3 tarkoittaa, että ydin on laskentarajoitteinen ja koodi
tehokasta; IPC alle 0,5 tarkoittaa, että ydin odottaa suurimman osan
ajasta. Intelin *top-down*-menetelmä (`perf stat --topdown`) jakaa
jaksot neljään luokkaan: käskyjen nouto, väärä spekulaatio,
taustapään odotus (muisti tai laskentayksiköt) ja hyödyllinen työ.

`perf record -g` tallentaa näytteiden lisäksi kutsupinot. Niistä
piirretään *liekkikuvaaja* (engl. flame graph, Brendan Gregg): jokainen
pino on pystysuora torni, jonka alimpana on `main`, ja jokaisen
funktion leveys on sen osuus näytteistä. Leveät tornit ovat kuumia
polkuja, ja tasaiset huiput ovat funktioita, jotka kuluttavat aikaa
itse. Callgrind-osion kutsupuu on sama tieto toisin päin piirrettynä:
liekkikuvaajassa `main` olisi koko leveyden levyinen pohja, sen päällä
`laske_hidas` ja sen päällä rinnakkain kaksi lähes yhtä leveää tornia,
joiden huipuilla ovat `strlen` ja `strcmp`. Kuvaaja tehdään
esimerkiksi komennolla `perf script` ja FlameGraph-skripteillä tai
suoraan työkaluilla kuten Hotspot ja Firefox Profiler.

Pinojen keräämiseen tarvitaan joko kehysosoitin (`-fno-omit-frame-pointer`)
tai DWARF-tiedot (`perf record --call-graph dwarf`). Monet jakelut
kääntävät nykyään kirjastonsakin kehysosoittimin juuri profiloinnin
takia.

## Kun ohjelma odottaa

Edellä kuvatut profiloijat näkevät ajan, jonka ohjelma viettää
suorittimella. Jos seinäkelloaika on paljon prosessiaikaa suurempi
(luku 2), ohjelma odottaa: levyä, verkkoa, lukkoa tai vuoroaan
suorittimelle. Näytteistävä profiili näyttää silloin tyhjää, koska
nukkuva säie ei tuota näytteitä.

Ensimmäinen työkalu on `strace`, joka näyttää ohjelman
järjestelmäkutsut. `strace -c` laskee ne ja niissä kuluneen ajan,
`strace -T` näyttää jokaisen kutsun keston. Makefile laskee luvun 10
kirjoitusesimerkin `write`-kutsut kahdella kirjoitustavalla:

```{.makefile tiedosto="esimerkit/Makefile" osa="strace"}
```

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-jarjestelmakutsut.txt"}
```

Sata tuhatta kutsua, joista jokainen käy ytimessä, on vastaus
kysymykseen "missä aika kuluu", vaikka mikään käyttäjätilan funktio ei
ole kuuma. Luku 10 korjaa tämän puskuroinnilla. Jäljitys hidastaa
ohjelmaa moninkertaisesti, joten `strace` kertoo kutsujen määrän ja
järjestyksen luotettavasti mutta kestot vain suuntaa-antavasti.

Muut työkalut samaan kysymykseen:

| Työkalu | Mitä näyttää |
|------------------|--------------------------------------------------|
| `strace -c`, `strace -T` | Järjestelmäkutsujen määrät ja kestot |
| `perf trace` | Sama pienemmällä hidastuksella |
| `perf sched timehist` | Kuinka kauan säie odotti vuoroaan suorittimelle |
| off-CPU-liekkikuvaaja | Kutsupinot painotettuina odotusajalla, ei suoritinajalla |
| `/proc/PID/status`, `pidstat -w` | Vapaaehtoiset ja pakotetut kontekstinvaihdot |

Paljon vapaaehtoisia kontekstinvaihtoja tarkoittaa, että ohjelma
nukahtaa itse (I/O, lukot); paljon pakotettuja, että se kilpailee
suorittimesta muiden kanssa.

## Käytännössä

- **Profiloi ennen kuin korjaat.** Esimerkin ilmeinen pullonkaula oli
  toinen kahdesta, ja suurempi löytyi vasta työkalulla, joka näkee
  kirjastot.
- **Käytä kahta työkalua.** Näytteistävä profiloija (perf) kertoo
  ajan, simuloiva (Callgrind) tarkat käskymäärät ja kutsupuun.
- **Lue sekä kumulatiivinen että oma kustannus.** Kumulatiivinen kertoo,
  minkä kutsupolun alla aika kuluu; oma kertoo, mikä funktio tekee
  työn.
- **Epäile kirjastofunktioita silmukassa.** `strlen`, `sscanf`,
  `realloc` ja vastaavat voivat kätkeä lineaarisen työn, jolloin
  silmukka muuttuu neliölliseksi.
- **Profiloi optimoitua koodia** debug-tiedoin (`-O2 -g`). Ilman
  optimointeja profiili näyttää eri pullonkaulat kuin tuotannossa.
- **Profiloi todellisella syötteellä.** Pieni testisyöte ei paljasta
  neliöllistä kasvua.
- **Jos suoritinprofiili on tyhjä, katso odotusta.** Vertaa
  seinäkelloa prosessiaikaan ja laske järjestelmäkutsut (`strace -c`).

## Itsearviointi

- Osaat selittää näytteistävän, instrumentoivan ja simuloivan
  profiloinnin erot ja valita työkalun tilanteeseen.
- Osaat profiloida ohjelman gprofilla ja Callgrindilla ja tulkita
  kumulatiivisen ja oman kustannuksen.
- Osaat selittää, miksi käskymäärä ei ole sama asia kuin aika.
- Osaat lukea `perf stat` -tulosteesta IPC:n ja hutien määrät ja
  päätellä niistä seuraavan askeleen.
- Osaat selittää, miten liekkikuvaaja luetaan.
- Osaat selvittää `strace`lla, mihin järjestelmäkutsuihin odottava
  ohjelma käyttää aikansa, ja nimetä työkalun vuorontajan viiveen
  tutkimiseen.

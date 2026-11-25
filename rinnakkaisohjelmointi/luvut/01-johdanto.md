# Johdanto {.runko-johdanto}

Yksittäisen suoritinytimen nopeus lakkasi kasvamasta 2000-luvun
puolivälissä. Kellotaajuutta ei enää voitu nostaa ilman, että teho ja
lämpö kasvoivat hallitsemattomasti (Dennardin skaalauksen loppu), joten
valmistajat alkoivat lisätä ytimiä. Herb Sutter kuvasi muutoksen vuonna
2005 otsikolla *The Free Lunch Is Over*: ohjelma ei enää nopeudu itsestään
uudella koneella, ellei se jaa työtään useille ytimille.

Tämä tutoriaali opettaa jakamaan työn turvallisesti ja tehokkaasti C++:lla.
Turvallisuus tulee ensin, sillä rinnakkaisohjelman virheet ovat
ohjelmointivirheistä hankalimpia. Ne ilmenevät satunnaisesti, eivät
välttämättä toistu debuggerissa ja voivat piillä vuosia, kunnes uusi kone,
kääntäjä tai kuorma paljastaa ne.

## Rinnakkaisuus ja samanaikaisuus

Kaksi käsitettä sekoitetaan usein:

- **Samanaikaisuus** (*concurrency*) on ohjelman rakenne: useita
  toimintoja on käynnissä yhtä aikaa ja niiden vaiheet lomittuvat.
  Yksiytiminenkin kone voi suorittaa samanaikaista ohjelmaa vuorottelemalla
  säikeitä.
- **Rinnakkaisuus** (*parallelism*) on suoritusta: laskentaa tehdään
  fyysisesti yhtä aikaa usealla ytimellä nopeuden vuoksi.

Palvelin, joka käsittelee tuhansia yhteyksiä, on ennen kaikkea
samanaikainen. Matriisitulo, joka jaetaan kahdeksalle ytimelle, on
rinnakkainen. Molemmissa tarvitaan samoja välineitä: säikeitä,
synkronointia ja muistimallin ymmärrystä. Rinnakkaisuus jaetaan lisäksi
**datarinnakkaisuuteen** (sama operaatio datan eri osille) ja
**tehtävärinnakkaisuuteen** (eri tehtävät rinnakkain).

## Esitiedot ja rajaus

Tutoriaali rakentuu kahden taidon päälle:

- *Käyttöjärjestelmät* opettaa, mitä säie on, miten ydin vuorontaa
  säikeitä ja miten POSIX-säikeet, mutex, ehtomuuttuja ja semafori
  toimivat. Sen luvuissa *Synkronointi* ja *Lukkiutuminen* käydään läpi
  tuottaja–kuluttaja-ongelma, lukijat ja kirjoittajat, Coffmanin ehdot ja
  lukkojärjestys C:llä. Niitä ei toisteta tässä.
- *Moderni C++* esittelee luvussa *Rinnakkaisuus* luokat `std::jthread`,
  `std::scoped_lock` ja `std::atomic`, funktion `std::async` sekä
  suljettavan työjonon. Tämä tutoriaali jatkaa siitä.

Välimuistit, koherenssiprotokolla MESI ja NUMA ovat taidossa
*Tietokonearkkitehtuuri*. Niihin viitataan, kun selitetään, miksi
atominen operaatio maksaa tai miksi väärä jakaminen hidastaa.

Tutoriaali käsittelee säikeitä, jotka jakavat muistin. Hajautetut
järjestelmät (prosessit, jotka viestivät verkon yli), GPU-laskenta ja
C++:n suorituskykyoptimointi ovat omia taitojaan. Korutiinit ja
asynkroninen I/O kuuluvat verkko-ohjelmointiin; tässä niihin viitataan
vain, kun ne ratkaisevat säikeiden ongelman.

## Luvut

Luku 1 on tämä johdanto ja luku 12 koostaa nyrkkisäännöt ja lähteet.

2. *Säikeet ja tehtävät*: argumentit, poikkeukset, pysäytys ja `std::async`.
3. *Säiepooli*: oma pooli tehtäväjonoineen ja sen sudenkuopat.
4. *Muistimalli*: tapahtumisjärjestys, muistijärjestykset ja litmus-testit.
5. *Atomiset operaatiot*: lukottomuus, `compare_exchange`, spinlukko,
   nukkuva lukko ja `std::atomic_ref`.
6. *Lukot*: monen lukon ottaminen, lukija–kirjoittaja-lukko ja raidoitus.
7. *Ehtomuuttujat ja muut odotusvälineet*: rajattu jono, este, semafori ja
   kertaalustus.
8. *Lukottomat tietorakenteet*: linearisoituvuus, SPSC-rengas,
   Treiberin pino, MPMC-jono ja ABA.
9. *Muistin takaisinotto*: vaaraosoittimet, epookit ja viittauslaskenta.
10. *Rinnakkaiset algoritmit ja työnjako*: suorituspolitiikat, reduktio,
   prefiksisumma, kuorman tasaus, OpenMP, Amdahl ja väärä jakaminen.
11. *ThreadSanitizer ja virheiden etsintä*: raporttien lukeminen,
    työkalun rajat ja stressitestaus.

## Työkalut

Esimerkit ovat C++23:a, ja ne käännetään GCC 14:llä ja Clang 20:llä
(libstdc++). Säikeiden käyttöön ei tarvita erillistä kirjastoa: glibc 2.34
yhdisti `libpthread`in C-kirjastoon, joten `-pthread` ei ole enää
pakollinen.

Testeissä jokainen esimerkki käännetään molemmilla kääntäjillä
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa ja ajetaan.
Esimerkit, joiden alussa on rivi `// TSAN`, käännetään ja ajetaan lisäksi
ThreadSanitizerilla (`-fsanitize=thread`), joka löytää datakilpailut.
Hakemiston `esimerkit/tsan/` ohjelmissa on tarkoituksellinen virhe, ja
niiden testi vaatii, että ThreadSanitizer raportoi sen. Hakemiston
`esimerkit/openmp/` ohjelma käännetään valitsimella `-fopenmp`.

Rinnakkaisen ohjelman tuloste ei saa riippua lomituksesta, jotta testi on
toistettava. Siksi esimerkit tulostavat vain lopputuloksia,
invarianttien tarkistuksia ja laskureita. Ajat ja muut koneesta riippuvat
mittaukset kirjoitetaan virhetulosteeseen, jota testi ei vertaa. Samaa
periaatetta kannattaa noudattaa omissa testeissä. Tekstissä näytetyt
mitatut tulokset (nopeutus, väärä jakaminen, litmus-testien
havaintomäärät) on ajettu erikseen kuormittamattomalla koneella
hakemiston `esimerkit/mittaus/` ohjelmilla.

Kehityskontissa (`.devcontainer/rinnakkaisohjelmointi`) ovat kääntäjät,
sanitoijat ja dokumenttityökalut.

## Ensimmäinen rinnakkainen ohjelma

Summan laskeminen jakautuu luontevasti osiin. Jokainen säie laskee oman
välinsä summan ja kirjoittaa sen omaan alkioonsa:

```{.cpp tiedosto="esimerkit/01-summa.cpp" osa="summa"}
```

```{.cpp tiedosto="esimerkit/01-summa.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/01-summa.odotettu"}
```

Ohjelmassa on kolme koko tutoriaalin läpi kulkevaa periaatetta:

- **Jaa olemalla jakamatta.** Säikeet lukevat yhteistä syötettä mutta
  kirjoittavat eri muistipaikkoihin, joten lukitusta ei tarvita.
  Paikallinen muuttuja `summa` pitää kuuman silmukan poissa jaetusta
  muistista.
- **Odotus luo järjestyksen.** Kun `jthread`-olioiden hajottimet ovat
  odottaneet säikeet loppuun, pääsäie näkee kaikki niiden kirjoitukset.
  Luku *Muistimalli* kertoo, miksi tämä on taattu.
- **Tulos ei riipu säikeiden määrästä.** Kokonaislukujen summa on sama
  millä tahansa jaolla. Liukuluvuilla näin ei ole, kuten luku
  *Rinnakkaiset algoritmit ja työnjako* näyttää.

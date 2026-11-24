# ThreadSanitizer ja virheiden etsintä

Rinnakkaisuusvirheet eivät toistu luotettavasti: väärä lomitus voi
osua kohdalle kerran miljoonassa ajossa, tai vain tietyllä suorittimella.
Siksi niitä ei löydetä pelkästään ajamalla testejä. Tämä luku esittelee
ThreadSanitizerin, joka löytää datakilpailut ajoituksesta riippumatta,
näyttää, miten sen raportteja luetaan, ja käy läpi, mitä se ei löydä ja
millä menetelmillä aukot täytetään.

## Miten ThreadSanitizer toimii

ThreadSanitizer (TSan, Serebryany ja Iskhodzhanov 2009) on kääntäjän ja
ajonaikaisen kirjaston yhdistelmä. Valitsimella `-fsanitize=thread`
kääntäjä lisää jokaisen muistiviittauksen eteen kutsun, joka kirjaa
viittauksen. Ajonaikainen kirjasto

- pitää jokaiselle säikeelle **vektorikelloa**, joka kertoo, mitkä muiden
  säikeiden tapahtumat se on "nähnyt". Lukot, atomiset operaatiot,
  säikeiden luonti ja `join` päivittävät kelloja muistimallin
  synkronointisääntöjen mukaan;
- pitää jokaisesta 8 tavun muistialueesta **varjomuistissa** muutaman
  viimeisimmän viittauksen (säie, kellonaika, luku vai kirjoitus);
- raportoi viittauksen, jos varjomuistissa on ristiriitainen viittaus
  toisesta säikeestä, jota nykyinen säie ei ole kellonsa mukaan nähnyt.

TSan tarkistaa siis tapahtumisjärjestyksen, ei ajoitusta. Kilpailu
löytyy, vaikka säikeet eivät olisi olleet käynnissä samaan aikaan, kunhan
molemmat viittaukset tapahtuvat ajon aikana eikä varjomuistin rajallinen
historia ole ehtinyt unohtaa ensimmäistä. Hinta on tyypillisesti 5–15
kertaa hitaampi suoritus ja 5–10 kertaa enemmän muistia. TSan ei toimi
yhdessä AddressSanitizerin kanssa, joten ne ajetaan erillisinä
käännöksinä, kuten tämän tutoriaalin testeissä.

Hyödyllisiä asetuksia ympäristömuuttujassa `TSAN_OPTIONS`:

| Asetus | Vaikutus |
|-----------------|--------------------------------|
| `halt_on_error=1` | Lopeta ensimmäiseen raporttiin (testeissä) |
| `second_deadlock_stack=1` | Lukkojärjestysraporttiin molempien lukkojen pinot |
| `history_size=7` | Pidempi historia: löytää kaukaisempia kilpailuja, vie muistia |
| `suppressions=tiedosto` | Ohita tunnetut raportit (esim. kolmannen osapuolen kirjasto) |
| `report_signal_unsafe=0` | Ei raportteja signaalinkäsittelijän kutsuista |

## Datakilpailun raportti

Kaksi säiettä kasvattaa tavallista laskuria:

```{.cpp tiedosto="esimerkit/tsan/kilpailu.cc" osa="kilpailu"}
```

Raportista ovat tässä olennaiset rivit; kolme pistettä korvaa osoitteet
ja muut ajosta riippuvat kohdat, ja standardikirjaston sisäiset pinot on
jätetty pois:

```{.tuloste tiedosto="esimerkit/tsan/kilpailu.raportti"}
```

Raportti luetaan näin:

1. **Otsikko** kertoo virheen lajin: `data race`.
2. **Nykyinen viittaus**: kuka, mitä (luku tai kirjoitus, koko) ja missä
   pinossa. Ylin kehys `#0` on lähdekoodin rivi.
3. **Edellinen viittaus** (`Previous`): ristiriitainen viittaus toisesta
   säikeestä, jota nykyinen ei ole nähnyt.
4. **Sijainti** (`Location`): globaali muuttuja nimeltä, pinon tai keon
   lohko varauspinoineen.
5. **Säikeet**: missä kukin säie luotiin. Tämä auttaa, kun samaa funktiota
   ajaa moni säie.

Se, kumpi säikeistä on "nykyinen" ja onko viittaus luku vai kirjoitus,
riippuu lomituksesta. Tarkistus tunnistaa sen ja hyväksyy molemmat.
Testi ajaa ohjelman myös Clangilla, mutta tarkistaa siitä vain otsikon,
koska Clangin TSan tarvitsee pinojen nimeämiseen ohjelman `llvm-symbolizer`,
jota kaikissa ympäristöissä ei ole.

## Väärä muistijärjestys

Luvun *Muistimalli* julkaisu toimii vain release/acquire-parilla. Kun
lippu on `relaxed`, data ja lippu eivät ole järjestyksessä:

```{.cpp tiedosto="esimerkit/tsan/julkaisu.cc" osa="julkaisu"}
```

```{.tuloste tiedosto="esimerkit/tsan/julkaisu.raportti"}
```

Raportti osoittaa *datan* kirjoituksen ja luvun, ei lippua, sillä lippu
on atominen eikä siihen voi kilpailla. Virhe on silti lipun
muistijärjestyksessä. Ohjelma tulostaa x86:lla aina oikean arvon, koska
suoritin ei järjestä kirjoituksia uudelleen; TSan löytää virheen silti,
koska se tarkistaa muistimallin eikä suoritinta.

## Lukkojärjestys

TSan seuraa myös, missä järjestyksessä lukkoja otetaan. Jos jossain
ohjelman kohdassa otetaan A ennen B:tä ja toisessa B ennen A:ta, ohjelma
voi lukkiutua, vaikka testiajossa ei lukkiutuisi:

```{.cpp tiedosto="esimerkit/tsan/lukkojarjestys.cc" osa="lukkojarjestys"}
```

```{.tuloste tiedosto="esimerkit/tsan/lukkojarjestys.raportti"}
```

Säikeet ajetaan peräkkäin, joten lukkiutuminen on tässä mahdotonta.
TSan raportoi silti syklin lukkojen järjestysgraafissa (M0 → M1 → M0),
koska jossain toisessa ajossa sama koodi lukkiutuisi. Tämä on
dynaamisen analyysin vahvuus: virhe löytyy ajosta, jossa se ei
ilmennyt.

## Mitä ThreadSanitizer ei löydä

TSan löytää datakilpailut, mutta kaikki rinnakkaisuusvirheet eivät ole
datakilpailuja. Tyypillisin aukko on **atomisuusrikko**: jokainen
operaatio on erikseen atominen, mutta tarkistus ja toiminta eivät ole
yhtenä operaationa. Seuraava esimerkki pakottaa pahimman lomituksen
esteellä:

```{.cpp tiedosto="esimerkit/11-tarkista-toimi.cpp" osa="virheellinen"}
```

```{.cpp tiedosto="esimerkit/11-tarkista-toimi.cpp" osa="oikea"}
```

```{.tuloste tiedosto="esimerkit/11-tarkista-toimi.odotettu"}
```

Molemmat versiot läpäisevät ThreadSanitizerin, koska kaikki jaettu data
on atomista. Saldo menee silti negatiiviseksi ensimmäisessä versiossa.
Korjaus yhdistää tarkistuksen ja vähennyksen yhdeksi CAS-operaatioksi.
Muita aukkoja:

- **Ajamaton koodi.** TSan näkee vain ajon aikana tapahtuneet viittaukset.
  Testien on käytävä läpi rinnakkaiset polut, mieluiten useammalla
  säikeellä kuin ytimiä on.
- **Liian heikko mutta kilpailuton järjestys.** `relaxed`-lippu ja
  atominen data eivät kilpaile, joten TSan ei raportoi, vaikka lukija voi
  ARMilla nähdä vanhan datan.
- **Lukkiutuminen ehtomuuttujaan tai kadonnut herätys.** Ohjelma jumittuu
  eikä kaadu. Testit tarvitsevat aikarajan.
- **Instrumentoimaton koodi.** Kirjastot, joita ei ole käännetty TSanilla,
  ja oma synkronointi assemblyllä tai `atomic_thread_fence`llä näyttävät
  TSanille kilpailuilta tai jäävät näkymättä. Rajapinnat
  `__tsan_acquire` ja `__tsan_release` kertovat sille omasta
  synkronoinnista. Tämän tutoriaalin esimerkissä `02-poikkeukset`
  Clangin TSan raportoi kuormitetussa konttiajossa kilpailun, kun
  poikkeusolio vapautettiin toisessa säikeessä kuin missä sen viestiä
  luettiin. Poikkeuksen viittauslaskenta on libstdc++:n jaetussa
  kirjastossa, jota ei ole instrumentoitu, joten TSan ei nähnyt
  synkronointia. Esimerkki järjestettiin niin, että säie odotetaan ennen
  poikkeuksen käsittelyä. Väärä hälytys on siis mahdollinen, mutta se
  selvitetään aina ennen kuin se ohitetaan.
- **Pitkä etäisyys.** Rajallinen historia unohtaa vanhat viittaukset.

## Stressitestaus

Atomisuusrikkojen ja logiikkavirheiden löytämiseen tarvitaan testejä,
jotka ajavat paljon erilaisia lomituksia ja tarkistavat invariantit.
Hyvä stressitesti käynnistää säikeet yhtä aikaa, toistaa lyhyen testin
monta kertaa ja sekoittaa lomitusta satunnaisilla viiveillä:

```{.cpp tiedosto="esimerkit/11-stressi.cpp" osa="hairio"}
```

```{.cpp tiedosto="esimerkit/11-stressi.cpp" osa="ajuri"}
```

```{.cpp tiedosto="esimerkit/11-stressi.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-stressi.odotettu"}
```

Lyhyt testi monta kertaa löytää enemmän kuin pitkä testi kerran, koska
säikeiden alku ja loppu ovat kohtia, joissa lomitukset vaihtelevat eniten.
Stressitestin kannattaa ajaa myös ThreadSanitizerilla: se hidastaa ja
sekoittaa ajoitusta, ja jokainen kierros on samalla kilpailutarkistus.

Muita menetelmiä:

- **Tallenna ja toista.** `rr` tallentaa ajon ja toistaa sen täsmälleen
  samana debuggerissa. Sen *chaos mode* sekoittaa vuorontamista
  löytääkseen harvinaisia lomituksia.
- **Mallintarkastus.** CDSChecker, GenMC ja Relacy käyvät läpi kaikki
  pienen testin muistimallin sallimat suoritukset, myös ne, joita x86 ei
  tuota. Ne sopivat lukottomien rakenteiden ydinoperaatioihin.
- **Staattinen analyysi.** Clangin `-Wthread-safety` tarkistaa
  lukkomerkintöjen avulla, että suojattua dataa käytetään vain lukon alla.
- **Muut dynaamiset työkalut.** Valgrindin Helgrind ja DRD löytävät
  kilpailuja ilman uudelleenkääntämistä, mutta ovat hitaampia.
- **Kielen takuut.** Rustin tyyppijärjestelmä (`Send`, `Sync` ja
  lainaussäännöt) estää datakilpailut käännösaikana; atomisuusrikot ja
  lukkiutumiset ovat sielläkin mahdollisia.

## Käytännössä

- **ThreadSanitizer CI:hin.** Kaikki rinnakkaista koodia sisältävät testit
  ajetaan TSanilla jokaisessa muutoksessa. Yksikin raportti on virhe,
  jota ei ohiteta ilman perustelua.
- **Pienennä löydetty virhe deterministiseksi testiksi.** Kun
  stressitesti tai tuotanto paljastaa virheen, lomitus pakotetaan
  esteillä tai salvoilla, kuten tämän luvun esimerkeissä. Silloin
  korjauksen voi todentaa ja virhe ei palaa.
- **Testaa invariantteja, älä lomituksia.** Testi tarkistaa säilymislait
  ja rakenteen eheyden, jotka eivät riipu ajoituksesta.
- **Aikarajat kaikkiin rinnakkaisiin testeihin.** Lukkiutuminen näkyy
  muuten jumittuneena CI-ajona.
- **Useita työkaluja.** TSan löytää kilpailut, ASan vapautetun muistin
  käytön, stressitestit atomisuusrikot ja mallintarkastimet
  muistijärjestysvirheet.

## Itsearviointi

- Osaat kertoa, miten ThreadSanitizer havaitsee datakilpailun
  vektorikelloilla ja varjomuistilla ja miksi tulos ei riipu ajoituksesta.
- Osaat lukea datakilpailu- ja lukkojärjestysraportin ja paikantaa virheen
  lähdekoodiin.
- Osaat nimetä virhetyyppejä, joita ThreadSanitizer ei löydä, ja
  menetelmän kullekin.
- Osaat kirjoittaa stressitestin ja pienentää löydetyn virheen
  deterministiseksi testiksi.

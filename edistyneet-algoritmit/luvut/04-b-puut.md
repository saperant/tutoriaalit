# B-puut ja lohkoittainen muisti

Binääripuun haku käy läpi noin $\log_2 n$ solmua. Jos solmut ovat
levyllä, jokainen niistä on oma lohkoluku. Miljardin avaimen puussa
se tarkoittaa 30 lukua, ja levyllä yksi luku voi kestää millisekunteja.
Keskusmuistissakin tilanne on samantapainen pienemmässä
mittakaavassa. Jokainen solmu on todennäköisesti eri välimuistirivillä,
ja välimuistin ohittava luku kestää satoja kellojaksoja. Vertailut
ovat halpoja verrattuna siihen, että solmu pitää hakea muistista.

*B-puu* (Bayer ja McCreight 1970) tekee solmusta lohkon kokoisen.
Yhdessä solmussa on satoja avaimia järjestyksessä, ja sen lapset
jakavat avainavaruuden avainten väleihin. Haku lukee solmun, etsii
siitä binäärihaulla oikean välin ja jatkaa lapseen. Vertailuja on yhä
noin $\log_2 n$, mutta luettuja lohkoja on vain $\log_B n$, missä $B$
on haarautumisaste.

## Rakenne

Cormenin ym. määritelmässä B-puulla on *minimiaste* $t \ge 2$:

- jokaisessa solmussa juurta lukuun ottamatta on $t - 1 \ldots 2t - 1$
  avainta ja juuressa $1 \ldots 2t - 1$ (ei-tyhjässä puussa),
- sisäsolmulla on yksi lapsi enemmän kuin avaimia, ja lapsen $i$
  avaimet ovat solmun avainten $i - 1$ ja $i$ välissä,
- kaikki lehdet ovat samalla syvyydellä.

Aste $t = 2$ antaa 2-3-4-puun, jonka binääriesitys on punamusta puu.
Korkeus on enintään $\log_t \frac{n+1}{2}$: miljardi avainta ja
$t = 500$ antavat korkeuden 4, ja ylimmät tasot pysyvät käytännössä
aina muistissa.

```{.cpp tiedosto="esimerkit/04-bpuu.cpp" osa="rakenne"}
```

## Lisäys halkaisemalla matkalla alas

Lisäys menee lehteen, kuten 2-3-puussa. Täyteen solmuun ei kuitenkaan
mahdu uutta avainta. Yksinkertainen ratkaisu on halkaista jokainen
täysi solmu jo matkalla alas, ennen kuin siihen laskeudutaan. Silloin
vanhemmassa on aina tilaa nousevalle avaimelle, eikä paluumatkaa
tarvita. Halkaisu siirtää täyden solmun $2t - 1$ avaimesta
keskimmäisen vanhempaan ja jakaa loput kahdeksi $t - 1$ avaimen
solmuksi:

```{.cpp tiedosto="esimerkit/04-bpuu.cpp" osa="halkaisu"}
```

```{.cpp tiedosto="esimerkit/04-bpuu.cpp" osa="lisays"}
```

Puu kasvaa korkeutta vain juuresta. Kun juuri on täysi, sen yläpuolelle
tehdään uusi juuri ja vanha halkaistaan. Lehdet pysyvät siksi aina
samalla syvyydellä.

Poisto toimii samalla periaatteella toiseen suuntaan. Ennen
laskeutumista lapseen varmistetaan, että siinä on vähintään $t$
avainta. Tarvittaessa avain lainataan sisarukselta tai lapsi
yhdistetään sisaruksen kanssa. Tapauksia on kolme, ja ne ovat
pitkiä mutta suoraviivaisia (Cormen ym., luku 18). Monet tietokannat
eivät yhdistä solmuja lainkaan. Ne merkitsevät avaimen poistetuksi ja
tiivistävät puun myöhemmin, koska vajaa solmu maksaa vain vähän tilaa.

## Testaus ja invariantit

Invarianttien tarkistus käy puun läpi ja tarkistaa jokaisen solmun
avainten määrän, järjestyksen ja lasten määrän sekä lehtien syvyyden.
Vertailutesti käyttää asteita 2, 3 ja 5, koska niillä halkaisuja tulee
paljon ja harvinaiset tilanteet, kuten juuren halkaisu, toistuvat
usein. Haun ja alarajan tulokset verrataan `std::set`-malliin jokaisen
operaation jälkeen.

Avainten rajat alipuiden välillä tarkistetaan epäsuorasti. Jos
sisäjärjestys on aidosti kasvava ja yhtä suuri kuin mallin sisältö,
jokainen avain on oikeassa välissä.

## Lohkoja ja vertailuja

Seuraava mittaus lisää satatuhatta avainta satunnaisessa
järjestyksessä eri asteisiin puihin ja hakee jokaisen kerran.
Laskurit erottavat luetut solmut (lohkot) vertailuista:

```{.tuloste tiedosto="esimerkit/04-bpuu.odotettu"}
```

Vertailujen määrä on kaikilla asteilla sama, noin $\log_2 n = 16{,}6$.
Binäärihaku solmun sisällä tekee saman työn kuin binääripuun
laskeutuminen. Luettujen solmujen määrä sen sijaan putoaa 12:sta
kahteen. Täyttöaste kertoo hinnan: satunnaisilla lisäyksillä solmut
ovat keskimäärin noin 70-prosenttisesti täynnä, koska halkaisun
jälkeen molemmat puolikkaat ovat vain puoliksi täysiä. Järjestyksessä
tulevilla avaimilla täyttöaste putoaa lähelle 50 prosenttia. Siksi
tietokannat tekevät oikeaan reunaan lisätessään epäsymmetrisen
halkaisun, joka jättää vasemman solmun täyteen.

## B+-puut ja välimuistitietoisuus

Tietokantojen ja tiedostojärjestelmien indeksit ovat lähes aina
*B+-puita*. Kaikki avaimet ja tietueet ovat lehdissä, ja sisäsolmut
sisältävät vain ohjausavaimia. Lehdet on lisäksi linkitetty
peräkkäin. Välikysely `BETWEEN a AND b` hakee $a$:n lehden ja kulkee
lehtiä pitkin. Sisäsolmuihin mahtuu enemmän avaimia, koska tietueet
eivät vie tilaa, joten puu on matalampi.

Sama ajatus toimii keskusmuistissa. Solmu, joka on yhden tai muutaman
välimuistirivin kokoinen (64–256 tavua, eli 16–64 kokonaislukua),
tekee hausta nopeamman kuin punamusta puu, vaikka vertailuja on yhtä
paljon. Abseilin `btree_map` ja Rustin `BTreeMap` ovat tällaisia.
*Välimuistista riippumattomat* (engl. *cache-oblivious*) rakenteet
menevät pidemmälle. Esimerkiksi van Emde Boasin asettelussa puu
tallennetaan rekursiivisesti alipuiksi niin, että se on tehokas millä
tahansa lohkokoolla tietämättä sitä. Välimuistin vaikutuksen
mittaaminen kuuluu taitoon *Suorituskyvyn analyysi ja optimointi*.

## Käytännössä

- Valitse aste lohkon koon mukaan: levyllä sivu (4–16 KiB), muistissa
  muutama välimuistirivi. Aste 2 on hyvä vain testaukseen.
- Haku solmun sisällä voi olla binäärihaku tai pienissä solmuissa
  lineaarinen haku, jonka prosessori vektoroi ja jonka haarat
  ennustetaan hyvin. Mittaa ennen kuin valitset.
- B-puun iteraattorit mitätöityvät halkaisussa, koska avaimet
  siirtyvät solmusta toiseen. `std::map` lupaa pysyvät iteraattorit ja
  viittaukset, mutta B-puupohjainen säiliö ei. Tämä on yleisin syy,
  miksi `btree_map` ei ole suora korvike.
- Tietokannan indeksin hidastuminen johtuu usein pirstoutumisesta ja
  alhaisesta täyttöasteesta. Juoksevat avaimet täyttävät oikean reunan
  tiiviisti, satunnaiset avaimet (esimerkiksi UUIDv4) jättävät puun
  puolityhjäksi.
- Testaa pienellä asteella ja suurella määrällä operaatioita.
  Juuren halkaisu ja lehtien syvyyden säilyminen ovat tapauksia,
  joihin suuri aste osuu harvoin.

## Itsearviointi

- Osaat määritellä B-puun minimiasteen avulla ja johtaa korkeuden
  rajan $\log_t \frac{n+1}{2}$.
- Osaat toteuttaa lisäyksen, joka halkaisee täydet solmut matkalla
  alas, ja selittää, miksi lehdet pysyvät samalla syvyydellä.
- Osaat erottaa B-puun haun lohkoluvut ja vertailut ja selittää,
  miksi vertailujen määrä ei riipu asteesta.
- Osaat kertoa, miten B+-puu eroaa B-puusta ja miksi tietokantojen
  indeksit ovat B+-puita.
- Osaat arvioida, milloin keskusmuistin B-puu on parempi kuin
  punamusta puu ja mitä sen käyttö maksaa iteraattorien pysyvyydessä.

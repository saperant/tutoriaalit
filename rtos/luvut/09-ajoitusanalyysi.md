# Ajoitusanalyysi

Testaus näyttää, että järjestelmä piti aikarajansa niissä tilanteissa,
jotka testattiin. Ajoitusanalyysi näyttää, että se pitää ne
*kaikissa* tilanteissa, kunhan oletukset pitävät. Analyysi on siksi
kovien reaaliaikajärjestelmien perusta, ja siihen liittyvät
standardit (IEC 61508, ISO 26262, DO-178C) vaativat sen tai sitä
vastaavan perustelun.

## Tehtävämalli

Klassinen analyysi olettaa yksinkertaisen mallin:

- tehtävät ovat jaksollisia: tehtävä *i* julkaisee työn jakson
  T~i~ välein
- määräaika on jakson loppu (D~i~ = T~i~)
- työn laskenta-aika on enintään C~i~ (WCET)
- tehtävät ovat riippumattomia: ne eivät odota toisiaan (ehtoa
  lievennetään alla)
- prioriteetit ovat kiinteät, ja vuorontaminen on etuoikeuttava
- ytimen kustannukset ovat nollia tai sisältyvät C~i~:hin.

Satunnaiset tehtävät (*sporadic*), joiden työt tulevat vähintään
T~i~:n välein, käyvät samaan malliin: ne analysoidaan kuin ne
julkaistaisiin aina mahdollisimman tiheään.

## Nopeusmonotoninen vuorontaminen

Liu ja Layland osoittivat vuonna 1973, että kun D = T, paras kiinteä
prioriteettijärjestys on *nopeusmonotoninen* (RMS, *rate-monotonic
scheduling*): mitä lyhyempi jakso, sitä korkeampi prioriteetti. Jos
jokin kiinteä järjestys pitää aikarajat, RMS pitää ne myös. Kun
määräajat ovat jaksoa lyhyemmät, sama pätee *määräaikamonotoniselle*
järjestykselle (DMS): lyhyin määräaika korkeimmalle.

Samassa työssä he johtivat käyttöasteelle rajan. Käyttöaste on
U = Σ C~i~ / T~i~, ja n tehtävän joukko pitää aikarajansa RMS:llä
varmasti, jos

$$U \le n\,(2^{1/n} - 1).$$

Raja on 1,000 yhdelle tehtävälle, 0,828 kahdelle, 0,780 kolmelle ja
lähestyy lukua ln 2 ≈ 0,693 tehtävien määrän kasvaessa. Raja on
*riittävä* ehto mutta ei *välttämätön*: moni joukko, jonka käyttöaste
on rajan yli, pitää silti aikarajansa. Jos jaksot ovat toistensa
monikertoja (*harmoninen* joukko), raja on 1,0.

## Vasteaika-analyysi

Tarkka testi on *vasteaika-analyysi* (Joseph ja Pandya 1986). Pahin
tilanne kiinteän prioriteetin järjestelmässä on *kriittinen hetki*,
jolloin tehtävä julkaistaan yhtä aikaa kaikkien tärkeämpien kanssa.
Tehtävän *i* pahin vasteaika R~i~ toteuttaa silloin yhtälön

$$R_i = C_i + B_i + \sum_{j \in hp(i)} \left\lceil \frac{R_i}{T_j} \right\rceil C_j,$$

missä hp(*i*) on tärkeämpien tehtävien joukko ja B~i~ pisin aika, jonka
vähemmän tärkeä tehtävä voi estää tehtävää *i* esimerkiksi pitämällä
mutexia (luku 8). Summa on tärkeämpien tehtävien häiriö: jokainen
tärkeämpi tehtävä *j* julkaisee välillä R~i~ enintään
$\lceil R_i / T_j \rceil$ työtä. Yhtälö ratkaistaan iteroimalla alkaen arvosta R~i~ = C~i~. Arvo
kasvaa joka kierroksella, kunnes se ei enää muutu (vasteaika löytyi)
tai se ylittää määräajan (joukko ei pidä aikarajoja).

```{.c tiedosto="esimerkit/14-rms/analyysi.c" osa="vasteaika"}
```

```{.c tiedosto="esimerkit/14-rms/analyysi.c" osa="kayttoaste"}
```

## Esimerkki: analyysi ja ajo

Tehtäväjoukossa on kolme tehtävää. Käyttöaste on 0,833, eli
Liu–Laylandin raja (0,780) ylittyy, eikä käyttöastetesti siksi kerro
mitään.

```{.c tiedosto="esimerkit/14-rms/joukko.h" osa="joukko"}
```

Kidessä jokainen tehtävä kuluttaa työssään C~i~ tikkiä ja odottaa
seuraavaa julkaisua `vTaskDelayUntil`illa. Kaikki julkaistaan
hetkellä 0, mikä on kriittinen hetki kaikille tehtäville. Tehtävä
kirjaa jokaisen työn vasteajan ja myöhästymiset.

```{.c tiedosto="esimerkit/14-rms/main.c" osa="tehtava"}
```

```{.c tiedosto="esimerkit/14-rms/main.c" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/testit/14-rms.odotettu"}
```

Vasteaika-analyysi löytää T3:lle vasteajan 10 ≤ 12, joten joukko pitää
aikarajansa, ja ajo vahvistaa sen: havaittu pahin vasteaika on sama
kuin analyysin. Aikajanalta näkyy, miksi: T3 saa ajaa vain niissä
väleissä, jotka T1 ja T2 jättävät, ja sen ensimmäinen työ valmistuu
hetkellä 10.

Muunnelmassa T3 laskee neljä tikkiä ja sen jakso on 10:

```{.tuloste tiedosto="esimerkit/testit/14-rms-ylikuorma.odotettu"}
```

Käyttöaste 0,983 on alle yhden, joten prosessorissa on periaatteessa
tilaa, mutta RMS ei pysty käyttämään sitä: T3:n vasteaika olisi 11 > 10.
Ajossa T3 myöhästyy kahdesti, ja pahin havaittu vasteaika on 12, siis
enemmän kuin analyysin 11. Analyysi pätee vain joukolle, joka pitää
aikarajansa: kun työ myöhästyy, seuraava työ alkaa sen perästä, ja
myöhästyminen voi kasautua. EDF (*earliest deadline first*) ajaisi
aina sen työn, jonka määräaika on lähimpänä, ja pitäisi tämänkin
joukon aikarajat, koska EDF:llä riittää U ≤ 1. Hinta on dynaaminen
prioriteetti, jota yleiset RTOSit eivät tue, ja ylikuormassa EDF
myöhästyttää helposti kaikkia tehtäviä, kun RMS myöhästyttää vain
vähiten tärkeitä.

## Laskenta-ajat ja kustannukset

Analyysi on yhtä hyvä kuin sen C~i~-arvot. WCET saadaan kahdella
tavalla:

- **Mittaamalla**: tehtävä ajetaan pahimmilla tunnetuilla syötteillä
  ja kylmällä välimuistilla, ja suurimpaan havaittuun aikaan lisätään
  marginaali (tyypillisesti 20–50 %). Halpaa mutta ei todistusta.
- **Staattisella analyysillä**: työkalu (esimerkiksi aiT tai OTAWA)
  laskee konekoodista ja prosessorin mallista ylärajan, joka on
  varmasti oikea mutta usein pessimistinen. Silmukoiden ylärajat on
  annettava työkalulle.

Ytimen omat kustannukset lisätään malliin: tikkikeskeytys vie
kaikilta tehtäviltä vähän aikaa jokaisella tikillä, ja jokainen
etuoikeutus maksaa kaksi kontekstinvaihtoa, jotka voidaan lisätä
tärkeämpien tehtävien C~j~:hin. Myös keskeytyskäsittelijät ovat
analyysissä tehtäviä, joiden prioriteetti on kaikkia tehtäviä
korkeampi. Jos julkaisu voi myöhästyä esimerkiksi tikin resoluution
vuoksi, yhtälöön lisätään julkaisun huojunta J~j~:
$\lceil (R_i + J_j) / T_j \rceil$.

## Käytännössä

- **Anna prioriteetit nopeus- tai määräaikamonotonisesti.** Se on
  optimaalinen kiinteä järjestys, ja analyysi olettaa sen.
- **Laske vasteajat, älä tyydy käyttöasteeseen.** Liu–Laylandin raja
  on helppo mutta pessimistinen; vasteaika-analyysi on tarkka ja vain
  vähän työläämpi.
- **Pidä analyysi koodin rinnalla.** Esimerkin tapaan tehtäväjoukko
  voi olla yhdessä otsakkeessa, josta sekä ohjelma että analyysi
  lukevat arvonsa. Analyysi ajetaan uudelleen, kun jokin muuttuu.
- **Mittaa laskenta-ajat jatkuvasti.** Ajoaikatilastot ja pahimpien
  vasteaikojen kirjaus tuotantolaitteessa paljastavat, jos oletukset
  eivät pidä.
- **Jätä varaa.** Käyttöaste 70 % jättää tilaa virheille, marginaaleille
  ja tuleville ominaisuuksille. Lähellä 100 %:a mikä tahansa muutos voi
  rikkoa aikarajat.

## Itsearviointi

- Osaat kuvata tehtävämallin oletukset ja antaa prioriteetit
  nopeus- tai määräaikamonotonisesti.
- Osaat laskea käyttöasteen ja Liu–Laylandin rajan ja kertoa, mitä
  testin tulos merkitsee ja mitä ei.
- Osaat laskea vasteajat iteroimalla, myös estoajan kanssa.
- Osaat selittää, miksi kriittinen hetki on pahin tilanne ja miksi
  analyysi ei päde enää, kun aikarajat ylittyvät.
- Osaat kertoa, miten WCET saadaan ja miten ytimen kustannukset
  otetaan huomioon.

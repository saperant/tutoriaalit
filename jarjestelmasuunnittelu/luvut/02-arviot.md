# Vaatimukset ja arviot

Suunnittelu alkaa kysymyksestä *kuinka paljon*. Sata pyyntöä sekunnissa
ja sata tuhatta pyyntöä sekunnissa ovat eri järjestelmiä: ensimmäinen
mahtuu yhdelle palvelimelle ja yhteen tietokantaan, jälkimmäinen
tarvitsee kuormantasauksen, välimuistin ja todennäköisesti osioinnin.
Arvion ei tarvitse olla tarkka. Sen tehtävä on kertoa mittaluokka ja
näyttää, mikä resurssi loppuu ensin.

## Toiminnalliset ja laadulliset vaatimukset

Toiminnalliset vaatimukset kertovat, mitä palvelu tekee: "käyttäjä
lataa kuvan", "käyttäjä näkee seuraamiensa kuvat". Laadulliset
vaatimukset (*non-functional requirements*) kertovat, kuinka hyvin:

- **Kuorma**: käyttäjiä, pyyntöjä, datan kasvu. Myös huippu, ei vain
  keskiarvo.
- **Latenssi**: tavoite persentiilinä, esim. 99 % katseluista alle
  200 ms:ssa. Keskiarvo ei kelpaa tavoitteeksi (luku 3).
- **Saatavuus**: kuinka suuri osa pyynnöistä saa onnistua, esim. 99,9 %
  kuukaudessa (luku 10).
- **Konsistenssi**: saako käyttäjä nähdä hetken vanhaa tietoa? Näkeekö
  hän oman muutoksensa heti (luku 7)?
- **Pysyvyys**: saako kuitattu kirjoitus kadota? Kuinka paljon dataa
  saa menettää katastrofissa (RPO) ja kuinka nopeasti on palauduttava
  (RTO)?

Laadulliset vaatimukset ratkaisevat arkkitehtuurin. Sama
toiminnallisuus voi olla yksi palvelin ja yksi tietokanta tai
kolmen konesalin replikoitu järjestelmä, riippuen siitä, mitä saa
kadota ja kuinka kauan saa olla poissa. Vaatimus kirjataan luvuksi,
koska "nopea" ja "aina saatavilla" eivät ole testattavia.

## Selkäpuolen laskut

Selkäpuolen lasku (*back-of-the-envelope estimate*) johtaa resurssit
muutamasta oletuksesta. Esimerkkinä kuvanjakopalvelu, jossa on kaksi
miljoonaa päivittäistä käyttäjää. Oletukset kirjoitetaan näkyviin:

```{.python tiedosto="esimerkit/luku02/arviot.py" osa="oletukset"}
```

Laskut ovat kertolaskuja ja yksikkömuunnoksia. Päivässä on 86 400
sekuntia, eli noin 10^5^; vuodessa noin 3 · 10^7^ sekuntia:

```{.python tiedosto="esimerkit/luku02/arviot.py" osa="laskut"}
```

```{.tuloste tiedosto="esimerkit/luku02/arviot.odotettu"}
```

Tulos kertoo enemmän kuin luvut erikseen:

- **Kirjoituksia on vähän, lukuja paljon.** 35 latausta sekunnissa
  huipussa on pieni kuorma, 2 800 katselua sekunnissa ei. Luku:kirjoitus
  80:1 tarkoittaa, että lukupolkua kannattaa optimoida: välimuisti,
  CDN ja lukureplikat.
- **Kuvat ja metatiedot erotetaan.** 2,4 petatavua kuvia ei mahdu
  tietokantaan, mutta 1,8 teratavua metatietoja mahtuu yhteen
  relaatiotietokantaan. Kuvat kuuluvat objektitallennukseen (esim. S3),
  ja tietokantaan tallennetaan vain viittaus.
- **Kaista ratkaisee kuvapalvelun kustannuksen.** 670 Mbit/s ulospäin
  huipussa on enemmän kuin yhden palvelimen verkkokortista kannattaa
  ottaa; esikatselut jaetaan sisällönjakeluverkosta (CDN).
- **Kuuma osa mahtuu muistiin.** Jos 80 % katseluista osuu 20 %:iin
  päivän kuvista, välimuisti tarvitsee satoja gigatavuja, ei
  teratavuja. Se on muutaman välimuistipalvelimen kokoluokka.

Huippukerroin on arvion herkin oletus. Kuluttajapalvelun kuorma
vaihtelee vuorokauden mukaan kertoimella 2–4, ja kampanjat, uutiset tai
urheilutapahtumat voivat nostaa sen hetkellisesti kymmenkertaiseksi.
Mitoitus tehdään huipulle, ja huippua suuremman kuorman varalle
tarvitaan suunnitelma: jonotus, rajoitus tai siisti heikentyminen
(luvut 8 ja 9).

## Mittaluokkia

Arvioissa tarvitaan muutamia lukuja ulkomuistista. Ne ovat
suuruusluokkia nykyisestä palvelinlaitteistosta, eivät tarkkoja arvoja:

| Toiminto | Aika | Huomio |
|----------|------|--------|
| muistiviittaus | 100 ns | välimuistiosuma 1–10 ns |
| 1 kt:n lähetys palvelinsalin sisällä | 1–10 µs | |
| SSD:n satunnaisluku | 20–100 µs | |
| kiertoviive saman konesalin sisällä | 0,1–0,5 ms | |
| Redis-haku verkon yli | 0,2–1 ms | kiertoviive hallitsee |
| indeksoitu tietokantahaku | 1–5 ms | yhteys valmiina |
| kiertoviive Helsinki–Frankfurt | 25–35 ms | |
| kiertoviive Eurooppa–Yhdysvaltain itärannikko | 80–100 ms | |
| kiertoviive Eurooppa–Australia | 250–300 ms | |

Kaksi seurausta toistuu suunnittelussa. Ensinnäkin verkon kiertoviive
on usein suurempi kuin itse työ, joten peräkkäisten kutsujen määrä
ratkaisee latenssin: kymmenen peräkkäistä tietokantahakua on 10–50 ms,
yksi kymmenen rivin haku 1–5 ms. Toiseksi valon nopeus rajaa
maantieteellisesti hajautetun järjestelmän: synkroninen replikointi
mantereiden välillä maksaa jokaisessa kirjoituksessa sata millisekuntia
(luku 7).

| Resurssi                         | Yhden palvelimen kokoluokka             |
|----------------------------------|-----------------------------------------|
| yksinkertaisia HTTP-pyyntöjä | 1 000–50 000 /s ytimiä ja kieltä kohden |
| PostgreSQL, indeksoituja lukuja | 10 000–100 000 /s |
| PostgreSQL, kirjoituksia | 1 000–20 000 /s levystä riippuen |
| Redis, yksinkertaisia komentoja | 100 000 /s ja enemmän |
| muistia | 64–1 024 Gt |
| verkkokortti | 10–100 Gbit/s |

Taulukon luvut vaihtelevat kertaluokalla laitteiston, kyselyjen ja
datan mukaan. Ne kertovat, milloin arvio on yhden koneen alueella ja
milloin selvästi sen ulkopuolella. Rajatapauksessa mitataan
(taito *Suorituskyvyn analyysi ja optimointi*).

## Käytännössä

- **Kirjoita oletukset koodiksi.** Laskentataulukko tai pieni ohjelma
  päivittää kaikki seuraukset, kun oletus muuttuu, ja näyttää, mihin
  oletukseen tulos on herkin.
- **Pyöristä rohkeasti.** Kaksi merkitsevää numeroa riittää; 86 400
  sekuntia on 10^5^. Tarkkuus ei paranna arviota, jonka oletukset ovat
  kertoimen kaksi päässä totuudesta.
- **Mitoita huipulle, laskuta keskiarvolla.** Kapasiteetti tarvitaan
  huipussa, kustannus syntyy keskimääräisestä käytöstä. Automaattinen
  skaalaus kaventaa eroa, mutta vain jos palvelu käynnistyy nopeasti.
- **Erota kuuma ja kylmä data.** Viimeisen viikon data ja viiden
  vuoden data kuuluvat usein eri tallennukseen.
- **Arvioi myös kasvu.** Mitoitus tehdään tyypillisesti 12–18 kuukauden
  päähän. Kymmenkertaisen kasvun kohdalla arkkitehtuuri muuttuu; sitä
  ei kannata rakentaa valmiiksi, mutta siihen kannattaa jättää tie
  (esim. osiointiavain, joka kelpaa myöhemmin).

## Itsearviointi

- Osaat erottaa toiminnalliset ja laadulliset vaatimukset ja kirjata
  laadulliset vaatimukset mitattaviksi luvuiksi.
- Osaat arvioida pyynnöt sekunnissa, tallennustarpeen, kaistan ja
  välimuistin koon muutamasta oletuksesta.
- Osaat päätellä arviosta arkkitehtuurin suunnan, esimerkiksi milloin
  data kuuluu objektitallennukseen ja milloin luku:kirjoitus-suhde
  puoltaa välimuistia.
- Osaat muistaa tärkeimpien viiveiden ja kapasiteettien kertaluokat ja
  käyttää niitä arviossa.

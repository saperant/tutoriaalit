# Lukitusaskel ja rollback

Tilannevedokset kasvavat entiteettien määrän mukana. Strategiapelissä,
jossa on tuhansia yksiköitä, tai taistelupelissä, jossa jokainen ruutu
ratkaisee, toimii toinen malli: koneet vaihtavat vain *syötteitä*, ja
jokainen simuloi koko pelin itse. Malli edellyttää täydellistä
determinismiä, joka rakennettiin taidossa *Peliohjelmointi*: kiinteä
askel, kokonaisluvut, oma satunnaislukugeneraattori ja kiinteä
käsittelyjärjestys.

Esimerkkien pelinä on pieni kaksintaistelu: hahmot liikkuvat ja
hyppäävät, ja toisen päälle laskeutunut saa pisteen.

```{.cpp tiedosto="esimerkit/yhteinen/kaksintaistelu.hpp" osa="peli"}
```

Tarkistussumma tiivistää koko tilan yhteen lukuun. Kun koneet vertaavat
summiaan, ne huomaavat heti, jos simulaatiot ovat eriytyneet (desync).

## Deterministinen lukitusaskel

Ruutu *f* voidaan laskea vasta, kun kaikkien pelaajien syötteet ruudulle
*f* ovat perillä. Jotta peli ei pysähtyisi joka ruudulla odottamaan,
syötteitä kerätään *syöteviiveen* verran etukäteen: painallus hetkellä
*T* koskee ruutua *T + viive*, ja syöte ehtii verkon yli ennen kuin
ruutu lasketaan.

```{.cpp tiedosto="esimerkit/09-lukitusaskel.cpp" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/09-lukitusaskel.odotettu"}
```

Jokainen ajo päätyy samaan summaan kuin viite, koska syötteet ovat
samat. Ero on tuntumassa: ilman syöteviivettä jokainen ruutu odottaa
vastustajan syötettä 40–55 ms, ja peli nykii. Kahden ruudun viive ei
riitä tälle yhteydelle. Neljän ruudun (64 ms) viiveellä mikään ruutu ei
myöhästy, mutta jokainen painallus näkyy omassa hahmossa 64 ms
myöhässä. Lukitusaskeleen syöteviive on siis aina vähintään
yhteyden yhden suunnan viive ja värinä.

## Rollback

*Rollback*-verkkokoodi (GGPO-periaate) poistaa odottamisen. Peli etenee
aikataulussa, ja puuttuva vastustajan syöte arvataan, tyypillisesti
toistamalla edellinen. Jokaisen ruudun tila tallennetaan. Kun oikea
syöte saapuu ja arvaus oli väärä, peli palaa ruutuun, jossa arvaus
tehtiin, ja simuloi ruudut nykyhetkeen oikeilla syötteillä:

```{.cpp tiedosto="esimerkit/09-rollback.cpp" osa="saapuminen"}
```

```{.cpp tiedosto="esimerkit/09-rollback.cpp" osa="ruutu"}
```

```{.tuloste tiedosto="esimerkit/09-rollback.odotettu"}
```

Lopputila on jälleen sama kuin viitteessä. Palautuksia tulee jokaisesta
vastustajan syötteen muutoksesta, jota ei ehditty saada ennen ruudun
laskemista. Ilman syöteviivettä palautus ulottuu enimmillään neljän
ruudun taakse, ja pelaaja voi nähdä vastustajan hypyn alkavan
kesken ilmalennon. Pieni syöteviive (2–3 ruutua) yhdistettynä
rollbackiin on taistelupelien vakiintunut kompromissi: palautukset
lyhenevät ja harvenevat, eikä oma ohjaus tunnu laahaavalta.

## Edellytykset ja rajat

- **Tilan tallennus ja palautus on oltava halpaa**, koska sitä tehdään
  joka ruutu. Pieni, kopioitava tila (ei osoittimia) on rollbackin
  edellytys.
- **Uudelleensimulointi kertautuu.** Neljän ruudun palautus tarkoittaa
  viittä simulointia yhden ruudun aikana; simulaation on oltava
  murto-osa ruudun ajasta.
- **Grafiikka ja ääni eivät palaa.** Ääni, joka soitettiin väärän
  arvauksen perusteella, on jo kuultu. Efektit käynnistetään
  vasta varmistuneista tapahtumista tai niin, että ne voi perua.
- **Eriytyminen on ohjelmointivirhe.** Vertaa tarkistussummia
  säännöllisesti ja tallenna syötteet, jotta virhe voidaan toistaa.

## Käytännössä

- **Lukitusaskel strategiapeleihin**, joissa on paljon yksiköitä ja
  viive on siedettävä. Syöteviive mitataan yhteydestä ja voi
  muuttua kesken pelin.
- **Rollback ja pieni syöteviive taistelupeleihin**, joissa reaktioaika
  ratkaisee ja tila on pieni.
- **Determinismi testataan jatkuvasti.** Aja sama tallenne kahdella
  kääntäjällä ja eri koneilla; summa kertoo, missä ruudussa ero syntyi.
- **Myöhään liittyvä pelaaja** tarvitsee koko tilan tai kaikki
  syötteet alusta; suunnittele liittyminen ja uudelleenliittyminen
  alusta asti.
- **Hinta:** yksi epädeterministinen rivi (järjestämätön kokoelma,
  liukuluku eri kääntäjäasetuksilla, alustamaton muisti) rikkoo koko
  mallin. Huijari näkee koko tilan, koska jokainen kone simuloi kaiken.

## Itsearviointi

- Osaat toteuttaa deterministisen lukitusaskeleen ja valita syöteviiveen
  yhteyden perusteella.
- Osaat toteuttaa rollbackin: arvauksen, tilan tallennuksen,
  palautuksen ja uudelleensimuloinnin.
- Osaat verrata lukitusaskelta, rollbackia ja tilannevedoksia pelin
  tyypin mukaan.
- Osaat tunnistaa eriytymisen tarkistussummilla ja luetella sen
  tavalliset syyt.

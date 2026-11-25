# Ohjelman suunnittelu

Aiemmat luvut opettivat rakennuspalikat. Ohjelmoinnin vaikein osa on
kuitenkin päättää, mitä palikoita tarvitaan ja miten ne liitetään
toisiinsa. Tämä luku kokoaa opitun yhdeksi ohjelmaksi ja näyttää
työtavan, jolla epämääräisestä tehtävästä tulee toimiva ja testattu
ohjelma.

## Tehtävä

Pankki antaa tiliotteen tekstitiedostona: jokaisella rivillä on päivä,
luokka ja summa. Halutaan kuukausittainen yhteenveto tuloista ja
menoista sekä tieto siitä, mihin rahaa kuluu eniten.

## 1. Ymmärrä ongelma esimerkeillä

Ennen koodia kirjoitetaan konkreettinen esimerkkisyöte ja käsin
laskettu haluttu tuloste. Samalla huomataan kysymykset, joihin
tehtävänanto ei vastaa:

- Mitä tehdään virheelliselle riville? *Ohitetaan ja kerrotaan
  rivinumero, ei kaadeta koko raporttia.*
- Ovatko `Ruoka` ja `ruoka` sama luokka? *Kyllä.*
- Miten tulot ja menot erotetaan? *Etumerkistä.*
- Sallitaanko kommentit ja tyhjät rivit? *Kyllä.*

```{.tuloste tiedosto="esimerkit/11-budjetti.syote"}
```

## 2. Pilko vaiheisiin

Ongelma jaetaan vaiheisiin ylhäältä alas, kunnes jokainen vaihe on
niin pieni, että sen toteutus on ilmeinen. Pseudokoodina:

```text
lue rivit
jokaiselle riville:
    ohita tyhjät ja kommentit
    jäsennä rivi tapahtumaksi, tai kirjaa virhe
laske tulot ja menot kuukausittain
laske menot luokittain ja valitse suurimmat
tulosta taulukko, suurimmat menot ja virheet
```

Vaiheista tulee funktioita, ja toisiinsa liittyvät funktiot kootaan
moduleiksi:

| Moduli | Vastuu |
|--------|--------|
| `tapahtuma.py` | tietomalli ja rivin jäsennys; ei tulosta mitään |
| `raportti.py` | koosteiden laskenta ja rahan muotoilu |
| `main.py` | syötteen luku, virheiden keruu ja tulostus |

```{.dot otsikko="Budjettiohjelman tietovirta. Teksti muuttuu tyypitetyksi dataksi heti alussa, ja laskenta käsittelee vain `Tapahtuma`-olioita. Virheilmoitukset kulkevat laskennan ohi."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.3;
  syote [label="tiliotteen\nrivit", shape=plain, style=""];
  tuloste [label="raportti", shape=plain, style=""];
  jasennys [label="tapahtuma.py\njäsennys"];
  laskenta [label="raportti.py\nkoosteet"];
  tulostus [label="main.py\ntulostus"];
  syote -> jasennys;
  jasennys -> laskenta [label="Tapahtuma-\noliot"];
  laskenta -> tulostus [label="summat"];
  tulostus -> tuloste;
  jasennys -> tulostus [label="virheilmoitukset", style=dashed];
}
```

## 3. Suunnittele data ensin

Kun data on mallinnettu hyvin, koodi seuraa siitä. Tapahtuma on
dataluokka, jonka kentät ovat oikeaa tyyppiä: päivä `date`, summa
sentteinä `int`. Jäsennyksen jälkeen ohjelman muu osa ei käsittele
tekstiä lainkaan, eikä sen tarvitse varautua virheelliseen muotoon.
Tämä on periaate *jäsennä, älä validoi* (*parse, don't validate*):
syöte muunnetaan reunalla tyypitetyksi dataksi tai hylätään.

```{.python tiedosto="esimerkit/11-budjetti/tapahtuma.py"}
```

Dataluokan `frozen=True` tekee tapahtumasta muuttumattoman: jäsennetty
tapahtuma ei voi muuttua vahingossa. `from None` piilottaa
virheilmoituksesta alkuperäisen englanninkielisen poikkeuksen, koska
uusi viesti kertoo saman asian käyttäjän kielellä.

## 4. Laskenta erillään syötteestä ja tulosteesta

```{.python tiedosto="esimerkit/11-budjetti/raportti.py"}
```

`setdefault(avain, oletus)` palauttaa avaimen arvon ja lisää
oletuksen, jos avainta ei vielä ole. `f"{t.paiva:%Y-%m}"` muotoilee
päivämäärästä kuukauden.

## 5. Pääohjelma kokoaa osat

```{.python tiedosto="esimerkit/11-budjetti/main.py"}
```

```{.tuloste tiedosto="esimerkit/11-budjetti.odotettu"}
```

Virheellinen päivämäärä 30.2. ohitettiin, ja käyttäjä tietää, minkä
rivin korjata. `lue_tapahtumat` saa rivit listana eikä lue niitä itse
syötteestä, joten sitä voi testata ilman tiedostoja.

## 6. Testaa osat

```{.python tiedosto="esimerkit/11-budjetti/test_budjetti.py"}
```

Testit kirjoitettiin vaihe kerrallaan toteutuksen rinnalla: ensin
summan jäsennys, sitten rivin jäsennys, koosteet ja lopuksi
virheellisten rivien käsittely.

Kun osa ei toimi odotetusti, virhe etsitään luvun *Virheet ja
poikkeukset* tavalla: pienin syöte, jolla virhe näkyy, kirjoitetaan
ensin testiksi ja korjataan sitten. Koska osat ovat pieniä ja erillään,
virheen paikka rajautuu yhteen funktioon.

## Kokeile itse

Näissä tehtävissä pohja on lähes tyhjä: suunnittelu on osa tehtävää.
Kirjoita ensin esimerkkisyöte ja haluttu tuloste, pilko ohjelma
funktioiksi ja testaa ne erikseen ennen kuin ajat tarkistimen.

1. **Sarjataulukko** (`11-1`). Ohjelma lukee ottelukohtaiset pisteet
   (`joukkue;pisteet`) ja tulostaa joukkueet pistesumman mukaan
   järjestettyinä.
2. **Tuntiraportti** (`11-2`). Ohjelma lukee työtuntikirjauksia
   (`päivä;tekijä;tunnit`), ohittaa kommentit, tulostaa tunnit
   tekijöittäin ja luettelee virheelliset rivit numeroineen.

## Käytännössä

- **Esimerkit ennen koodia.** Käsin laskettu syöte–tuloste-pari
  paljastaa epäselvät vaatimukset ja on samalla ensimmäinen testi.
- **Ylhäältä alas suunnittelu, alhaalta ylös toteutus.** Pilko ongelma
  vaiheisiin, toteuta ja testaa pienimmät osat ensin ja kokoa ne.
- **Erota syöte, laskenta ja tuloste** (*functional core, imperative
  shell*). Laskenta on puhtaita funktioita, jotka on helppo testata;
  syötteen luku ja tulostus ovat ohuessa pääohjelmassa.
- **Jäsennä reunalla.** Muunna teksti heti tyypitetyksi dataksi, niin
  sisempi koodi on yksinkertaista.
- **Pienet askeleet.** Aja ohjelma ja testit jokaisen pienen muutoksen
  jälkeen. Kun jokin hajoaa, syy on viimeisessä muutoksessa.
- **Ensin toimiva, sitten siisti.** Kun testit menevät läpi, siisti
  nimet ja rakenne. Testit varmistavat, että käytös säilyy.
- **Käytä versionhallintaa.** Gitillä jokaisen toimivan välivaiheen voi
  tallentaa ja palata siihen (taito *Versionhallinta (Git)*).

## Itsearviointi

- Osaat tarkentaa epämääräisen tehtävän konkreettisilla esimerkeillä
  ja kysymyksillä.
- Osaat pilkkoa ohjelman vaiheisiin, funktioihin ja moduleihin ja
  perustella vastuunjaon.
- Osaat mallintaa syötteen dataluokaksi ja jäsentää sen ohjelman
  reunalla.
- Osaat erottaa syötteen luvun, laskennan ja tulostuksen toisistaan
  niin, että laskennan voi testata ilman tiedostoja.

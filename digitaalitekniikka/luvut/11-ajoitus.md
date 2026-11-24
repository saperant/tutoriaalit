# Ajoitus ja kellotus

Synkroninen piiri toimii oikein, jos jokainen rekisterien välinen
logiikkapolku ehtii asettua kellojakson aikana. Tämä luku laskee,
kuinka nopea kello voi olla, ja näyttää, miten suunnittelija nopeuttaa
piiriä.

## Ajoitusyhtälöt

Tarkastellaan polkua kiikusta A logiikan läpi kiikkuun B. Reunalla A
päivittyy viiveellä $t_{cq}$, logiikka laskee ajan $t_{logiikka}$, ja
tuloksen on oltava B:n tulossa asetusajan $t_{su}$ ennen seuraavaa
reunaa:

$$T \geq t_{cq} + t_{logiikka,max} + t_{su}$$

Pisin tällainen polku on *kriittinen polku*, ja se määrää suurimman
kellotaajuuden $f_{max} = 1/T_{min}$.

Toinen ehto koskee lyhintä polkua. B näytteistää vanhan arvon samalla
reunalla, jolla A muuttuu. Uusi arvo ei saa ehtiä B:hen ennen kuin
pitoaika $t_h$ on kulunut:

$$t_{cq} + t_{logiikka,min} \geq t_h$$

Asetusehto riippuu kellojaksosta, pitoehto ei. Asetusrikkeen voi
korjata hidastamalla kelloa; pitorikettä ei voi, vaan piiriin on
lisättävä viivettä. Siksi pitorike on vakavampi: se rikkoo piirin
kaikilla taajuuksilla.

## Staattinen ajoitusanalyysi

Staattinen ajoitusanalyysi (static timing analysis, STA) laskee
jokaisen signaalin myöhäisimmän ja aikaisimman saapumisajan käymällä
piirin läpi kerran. Simulointia ei tarvita, joten analyysi kattaa
kaikki syötteet. Saapumisaika on suurin (tai pienin) tulojen
saapumisaika lisättynä portin viiveellä:

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="sta"}
```

Analysoitava piiri on 16-bittinen ripple-carry-summain kahden rekisterin
välissä:

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="summain"}
```

```{.python tiedosto="esimerkit/11-ajoitus.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/11-ajoitus.odotettu"}
```

Kriittinen polku alkaa bitistä 0, kulkee muistibittien ketjun läpi ja
päättyy muistibittiin 16, kuten luvussa 6 nähtiin. Lyhin polku on
yhden XOR-portin mittainen, ja pitomarginaali on positiivinen.

STA olettaa pahimman tapauksen, myös polkuja, joita mikään syöte ei
koskaan herätä (*false path*). Suunnittelija kertoo tällaiset polut
työkalulle rajoitteina, samoin polut, joilla on tarkoituksella useampi
jakso aikaa (*multicycle path*).

## Liukuhihnoitus

Kun kriittinen polku on liian pitkä, sen voi katkaista rekisterillä.
Esimerkissä summain jaetaan kahteen kahdeksan bitin vaiheeseen, joiden
välissä on rekisteri: alaosa lasketaan ensimmäisessä jaksossa, yläosa
ja sen muistibitti toisessa. Polku puolittuu ja kellotaajuus lähes
kaksinkertaistuu (704 → 1282 MHz).

Hinta on *latenssi*: yksittäinen summa valmistuu kahdessa jaksossa
yhden sijaan. *Läpäisy* sen sijaan kasvaa: uusi summa voi alkaa joka
jakso. Liukuhihnoitus kannattaa, kun laskentaa on paljon peräkkäin
(suoritin, signaalinkäsittely), ja vaihe-erojen lisärekisterit (yläosan
syötteet ja alaosan tulos viivästettyinä) kuuluvat toteutukseen.

| Toimenpide | Kriittinen polku | Latenssi | Pinta-ala |
|------------|------------------|----------|-----------|
| Nopeampi rakenne (lookahead) | lyhenee | ennallaan | kasvaa |
| Liukuhihnoitus | lyhenee | kasvaa | rekistereitä lisää |
| Rinnakkaistus | ennallaan | ennallaan | kasvaa paljon |
| Hitaampi kello | ennallaan | kasvaa ajassa | ennallaan |

## Kellon vino ja värinä

Todellisuudessa kello ei saavu kaikkiin kiikkuihin samaan aikaan. Ero
on *kellon vino* (clock skew), ja jakso jaksolta vaihteleva epätarkkuus
on *värinä* (jitter). Jos kello saapuu B:hen myöhemmin kuin A:han,
asetusehtoon jää enemmän aikaa mutta pitoehto tiukkenee. Siksi
kellopuu suunnitellaan erikseen niin, että vino on pieni, ja
ajoitusanalyysi ottaa sen huomioon.

## Käytännössä

- **Ajoitusraportti on piirin totuus.** Synteesin ja sijoittelun
  jälkeen STA-raportti kertoo, saavuttiko piiri tavoitetaajuuden.
  Simulaatio ei kerro sitä koskaan.
- **Pitorikkeet korjataan aina.** Asetusrikkeen voi joskus hyväksyä
  laskemalla taajuutta; pitorikettä ei. Työkalut lisäävät
  viivepuskureita automaattisesti, mutta suuri vino voi tehdä
  korjauksesta mahdotonta.
- **Rekisteröi lohkojen rajat.** Kun jokaisen lohkon lähdöt ja tulot
  ovat rekistereitä, kriittinen polku pysyy lohkon sisällä ja lohkot
  voi analysoida erikseen.
- **Liukuhihna vasta tarpeeseen.** Jokainen vaihe lisää latenssia ja
  ohjauslogiikkaa. Ensin katsotaan, löytyykö polulta turhaa
  logiikkaa, sitten nopeampi rakenne, vasta sitten uusi vaihe.

## Itsearviointi

- Osaat kirjoittaa asetus- ja pitoehdon ja laskea suurimman
  kellotaajuuden.
- Osaat selittää, miksi pitorike on vakavampi kuin asetusrike.
- Osaat kuvata staattisen ajoitusanalyysin periaatteen ja käsitteet
  false path ja multicycle path.
- Osaat arvioida, mitä liukuhihnoitus tekee kellotaajuudelle,
  latenssille ja läpäisylle.

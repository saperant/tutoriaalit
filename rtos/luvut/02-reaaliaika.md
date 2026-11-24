# Reaaliaikaisuus

Reaaliaikajärjestelmässä tulos on oikea vain, jos se on valmis
ajoissa. Moottorinohjain, joka laskee oikean virran mutta 2 ms liian
myöhään, on rikki. Reaaliaikaisuus ei siis tarkoita nopeutta vaan
aikarajojen pitämistä: hidas järjestelmä voi olla reaaliaikainen, jos
sen aikarajat ovat väljät ja se pitää ne aina.

## Käsitteet

Tehtävän *työ* (job) alkaa *julkaisusta* (release): hetkestä, jolloin
sen syöte on valmis, esimerkiksi ajastin laukeaa tai näyte saapuu.
Jaksollinen tehtävä julkaisee uuden työn jakson välein.

| Käsite | Merkitys |
|-----------|-------------------------------|
| määräaika (D, *deadline*) | hetki julkaisun jälkeen, johon mennessä työn on oltava valmis |
| vasteaika (R, *response time*) | julkaisusta valmistumiseen |
| latenssi | julkaisusta työn alkuun: aika, jonka työ odottaa vuoroaan |
| huojunta (*jitter*) | latenssin tai valmistumishetken vaihtelu työstä toiseen |
| laskenta-aika (C) | prosessoriaika, jonka työ tarvitsee ilman keskeytyksiä |
| WCET | pahin mahdollinen laskenta-aika (*worst-case execution time*) |

Aikarajat jaetaan sen mukaan, mitä myöhästyminen maksaa:

- **Kova** (*hard*): myöhästyminen on vika, usein vaarallinen.
  Turvatyynyn laukaisu, jarrujen ohjaus, sydämentahdistin.
- **Vakava** (*firm*): myöhästynyt tulos on arvoton, mutta harvoista
  myöhästymisistä ei seuraa vahinkoa. Videopuhelun ruutu, joka
  myöhästyy, jätetään näyttämättä.
- **Pehmeä** (*soft*): myöhästynytkin tulos on hyödyllinen, mutta laatu
  heikkenee. Käyttöliittymän päivitys, lokien kirjoitus.

Kovan järjestelmän suunnittelu nojaa *determinismiin*: jokaisen
toiminnon kesto on rajattu ja tunnettu. Siksi RTOSin ydin välttää
toimintoja, joiden kesto riippuu syötteestä. Kiden valmislistan haku
on yksi CLZ-käsky prioriteettien määrästä riippumatta, ja dynaaminen
muistinvaraus on poissa käytöstä tai vakioaikainen (luku 10).
Laitteistotasolla determinismiä heikentävät välimuistit, haarautumisen
ennustus ja väylän kilpailu, ja siksi kovien järjestelmien piirit ovat
usein yksinkertaisia ja niiden WCET mitataan pahimmassa tilanteessa.

## Tikki ja aika

Ytimen aika etenee *tikkeinä*. SysTick-ajastin keskeyttää prosessorin
`configTICK_RATE_HZ` kertaa sekunnissa, ja tikkikeskeytys herättää
tehtävät, joiden viive on täynnä. Taajuus on kompromissi: tiheä tikki
antaa tarkemman ajan mutta kuluttaa prosessoria ja estää syvän unen.
Tavallisia arvoja ovat 100–1000 Hz. Aika muunnetaan tikeiksi makrolla
`pdMS_TO_TICKS`, jottei koodi riipu taajuudesta.

```{.c tiedosto="esimerkit/kide/kide_asetukset.h" osa="asetukset"}
```

32-bittinen tikkilaskuri pyörähtää ympäri 1 kHz:n taajuudella 49,7
vuorokauden välein. Siksi aikoja ei vertailla suoraan (`a < b`) vaan
erotuksen avulla. Erotus `herays - nyt` on oikein myös ympäripyörähdyksen
jälkeen, kunhan tapahtumat ovat alle 2³¹ tikin päässä toisistaan. Kide
järjestää viivelistan avaimella `herays - nyt`:

```{.c tiedosto="esimerkit/kide/lista.c" osa="jarjestys"}
```

FreeRTOS ratkaisee saman kahdella viivelistalla, joista toinen sisältää
herätykset ympäripyörähdyksen jälkeen, ja listat vaihdetaan, kun
laskuri pyörähtää.

Tikin resoluutio rajaa viiveen tarkkuutta. `vTaskDelay(1)` odottaa
seuraavaan tikkiin, eli 0–1 tikkiä sen mukaan, missä kohdassa tikkiä
kutsu tehdään. Tarkkaan ajoitukseen (mikrosekunteja) käytetään
laitteistoajastinta ja keskeytystä, ei ytimen viiveitä.

## Jaksollinen tehtävä

Jaksollisen tehtävän voi kirjoittaa kahdella tavalla. `vTaskDelay`
laskee viiveen kutsuhetkestä, `vTaskDelayUntil` edellisestä
herätyshetkestä, jota se pitää yllä kutsujan muuttujassa.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="viive"}
```

Esimerkissä kaksi tehtävää yrittää toimia 10 tikin jaksolla. Niitä
tärkeämpi häiriötehtävä herää 7 tikin välein ja laskee 2 tikkiä, eli
se vie 29 % prosessorista.

```{.c tiedosto="esimerkit/02-jakso/main.c" osa="hairio"}
```

```{.c tiedosto="esimerkit/02-jakso/main.c" osa="viive"}
```

```{.c tiedosto="esimerkit/02-jakso/main.c" osa="tarkka"}
```

```{.tuloste tiedosto="esimerkit/testit/02-jakso.odotettu"}
```

`vTaskDelay`-tehtävän jakso on 10 tikkiä *plus* oma työ *plus* häiriön
aiheuttama odotus, joten se *ajelehtii*: seitsemän jaksoa vei 81
tikkiä. Virhe kasautuu, eikä tehtävä koskaan palaa aikatauluun.
`vTaskDelayUntil`-tehtävä myöhästyy kunkin jakson alusta 3–6 tikkiä,
koska tärkeämmät tehtävät ajavat ensin, mutta myöhästyminen ei
kasaudu: jokainen työ alkaa oman julkaisuhetkensä jälkeen. Latenssin
vaihtelu, 3 tikkiä, on tehtävän huojunta. Se ei johdu tehtävästä
itsestään vaan siitä, mitä tärkeämmät tehtävät sattuvat tekemään.

Jos tehtävä on niin myöhässä, että seuraavakin julkaisu on jo ohi,
`vTaskDelayUntil` palaa heti, ja tehtävä yrittää ottaa kiinni. Tämä on
yleensä oikein säätösilmukalle (näytteet otetaan oikeaan aikaan) mutta
väärin tehtävälle, joka ei voi ajaa kahta työtä peräkkäin. Silloin
tehtävän pitää itse havaita myöhästyminen ja hypätä jakson yli.

## Käytännössä

- **Käytä jaksollisiin tehtäviin `vTaskDelayUntil`ia.** `vTaskDelay`
  on oikea vain silloin, kun halutaan vähimmäistauko kahden asian
  välille, kuten "odota 5 ms ennen uudelleenyritystä".
- **Mittaa huojunta, älä arvaa sitä.** Kirjaa julkaisu- ja
  aloitushetket kuten esimerkissä tai nosta GPIO-nasta tehtävän alussa
  ja mittaa logiikka-analysaattorilla.
- **Älä nojaa tikkiin mikrosekuntiajoituksessa.** Tikin tarkkuus on
  ±1 tikki. Laitteistoajastin keskeytyksineen on tarkka ja
  deterministinen.
- **Vertaile aikoja erotuksena.** `(int32_t)(a - b) > 0` toimii
  ympäripyörähdyksen yli, `a > b` ei.
- **Luokittele aikarajat.** Kun tiedetään, mikä tehtävä on kova ja mikä
  pehmeä, tiedetään myös, mitkä saavat korkeimmat prioriteetit ja
  mihin analyysi keskitetään.

## Itsearviointi

- Osaat määritellä julkaisun, määräajan, vasteajan, latenssin ja
  huojunnan ja erottaa kovan, vakavan ja pehmeän aikarajan.
- Osaat selittää, miksi `vTaskDelay` ajelehtii ja `vTaskDelayUntil`
  ei.
- Osaat vertailla tikkiaikoja oikein laskurin pyörähtäessä ympäri.
- Osaat arvioida tikkitaajuuden vaikutuksen tarkkuuteen ja
  kuormitukseen.

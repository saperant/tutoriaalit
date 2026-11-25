# Jonot

Jono on RTOSin perusväline tehtävien väliseen viestintään. Se on
kiinteän kokoinen FIFO-puskuri, johon lähettäjä kopioi alkion ja josta
vastaanottaja kopioi sen. Kumpikin voi odottaa: lähettäjä tilaa ja
vastaanottaja dataa, enintään aikarajan verran. Jono yhdistää siis
datan välityksen ja synkronoinnin. Kun vastaanottaja odottaa tyhjässä
jonossa, se ei kuluta prosessoria, ja ydin herättää sen heti, kun
alkio tulee.

## Kopiointi

FreeRTOSin ja Kiden jono kopioi alkion arvon, ei osoitinta. Lähettäjä
voi käyttää muuttujaansa uudelleen heti kutsun jälkeen, eikä alkion
elinaikaa tarvitse miettiä. Kopio maksaa: 100 tavun alkio kopioidaan
kahdesti. Isoille alkioille välitetään osoitin, ja alkion omistus
siirtyy vastaanottajalle (luku 10).

```{.c tiedosto="esimerkit/kide/kide.h" osa="jono"}
```

Jonon tilan vaatima muisti (pituus × alkion koko) annetaan luotaessa.
Odottavat tehtävät ovat kahdessa listassa, `lahettajat` ja
`vastaanottajat`, jotka on järjestetty prioriteetin mukaan: kun jonoon
tulee tilaa tai dataa, tärkein odottaja herää ensin. Saman prioriteetin
odottajat palvellaan saapumisjärjestyksessä.

## Odottaminen ja herääminen

Jono ja kaikki muut ytimen oliot käyttävät samaa kahta funktiota.
`kide_odota` siirtää nykyisen tehtävän valmislistasta odotuslistaan ja,
jos aikaraja on annettu, myös viivelistaan. `kide_heraa` siirtää
odotuslistan ensimmäisen tehtävän takaisin valmislistaan ja kertoo,
onko se nykyistä tärkeämpi.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="odotus"}
```

Lähetys yrittää kriittisessä osiossa, ja jos jono on täynnä, jää
odottamaan. Herättyään se yrittää uudelleen, koska tila on voinut
täyttyä uudelleen: tärkeämpi tehtävä on voinut ehtiä lähettää ensin.
Herääminen voi johtua myös aikarajasta, jolloin jäljellä oleva aika on
nolla ja kutsu epäonnistuu. Vastaanotto on symmetrinen.

```{.c tiedosto="esimerkit/kide/jono.c" osa="laheta"}
```

```{.c tiedosto="esimerkit/kide/jono.c" osa="vastaanota"}
```

Aikaraja on tärkeä osa rajapintaa. `portMAX_DELAY` odottaa
ikuisesti, 0 ei lainkaan, ja muu arvo enintään niin monta tikkiä.
Ikuinen odotus on oikein tehtävälle, jonka ainoa työ on käsitellä
jonon viestejä. Kaikkialla muualla aikaraja kertoo, milloin jotain on
mennyt vikaan, ja antaa tehtävälle tilaisuuden toipua.

## Tuottaja ja kuluttaja

Esimerkissä tuottaja ottaa näytteen kahden tikin välein, mutta
kuluttajalta kuluu yhden käsittelyyn kolme tikkiä. Jonoon mahtuu kolme
näytettä. Tuottaja odottaa täyttä jonoa enintään tikin ja hylkää sen
jälkeen näytteen. Hylkääminen on usein oikea valinta: tuore näyte on
arvokkaampi kuin vanha, ja tuottajan pitää jatkaa omassa
aikataulussaan.

```{.c tiedosto="esimerkit/08-jono/main.c" osa="alkio"}
```

```{.c tiedosto="esimerkit/08-jono/main.c" osa="tuottaja"}
```

```{.c tiedosto="esimerkit/08-jono/main.c" osa="kuluttaja"}
```

```{.tuloste tiedosto="esimerkit/testit/08-jono.odotettu"}
```

Jono täyttyy hetkellä 12. Hetkellä 18 tuottaja odottaa täydessä
jonossa, kunnes kuluttaja ottaa näytteen 7, ja ehtii lähettää
näytteen 10. Näyte 11 jää ilman tilaa koko aikarajan ajan ja
hylätään. Koska tuottaja on tärkeämpi, se pääsee ajoon heti, kun tilaa
vapautuu. Siksi sen tuloste on kuluttajan tulosteen perässä samassa
tikissä. Jono ei korjaa kapasiteettiongelmaa: jos kuluttaja on
pysyvästi hitaampi, jono täyttyy, oli se kuinka pitkä tahansa. Jono
tasaa vain hetkellisiä ruuhkia, ja sen pituus mitoitetaan pahimman
ruuhkan mukaan.

## Keskeytyksestä jonoon

Sarjaportin vastaanotto on jonon tyyppitapaus. Keskeytyskäsittelijä
lukee tavut UART:sta ja lähettää ne jonoon `xQueueSendFromISR`illa.
Komentotehtävä kokoaa niistä rivejä ja suorittaa komennot. Jos jono on
täynnä, käsittelijä ei voi odottaa, joten tavu hukataan ja hukka
lasketaan. Taidon *Mikrokontrollerit ja bare-metal-ohjelmointi*
rengaspuskuri teki saman ilman ydintä, mutta pääsilmukka joutui nukkumaan ja tarkistamaan
puskuria itse.

```{.c tiedosto="esimerkit/09-uart/main.c" osa="isr"}
```

```{.c tiedosto="esimerkit/09-uart/main.c" osa="komento"}
```

Syöte tulee tiedostosta `syote.txt` QEMU:n sarjaportin kautta:

```{.tuloste tiedosto="esimerkit/testit/09-uart.odotettu"}
```

Tavu kerrallaan jonoon lähettäminen on yksinkertaista mutta kallista:
jokainen tavu on kriittinen osio, mahdollinen tehtävänvaihto ja kaksi
kopiota. Suurilla nopeuksilla (yli 100 kbit/s) käytetään DMA:ta ja
välitetään jonossa kokonaisia puskureita, tai FreeRTOSin *stream
buffer* -oliota, joka on tehty juuri yhden kirjoittajan ja yhden
lukijan tavuvirralle.

## Käytännössä

- **Mitoita jono pahimman ruuhkan mukaan** ja mittaa käyttö:
  `uxQueueMessagesWaiting` tai FreeRTOSin jonojen jäljitys kertovat,
  kuinka täynnä jono on ollut.
- **Päätä, mitä täysi jono tarkoittaa.** Odotetaanko, hylätäänkö uusin
  vai vanhin, vai onko täysi jono virhe, josta kerrotaan? Kirjoita
  päätös koodiin näkyviin.
- **Lähetä isoista alkioista osoitin** ja sovi omistuksesta: kuka
  vapauttaa muistin ja milloin (luku 10).
- **Käytä yhtä vastaanottajaa jonoa kohden.** Monta lähettäjää on
  tavallista, mutta monta vastaanottajaa tekee järjestyksestä vaikean
  ymmärtää. FreeRTOSin *queue set* antaa yhden tehtävän odottaa
  useaa jonoa.
- **Älä käsittele keskeytyksessä enempää kuin tavu kerrallaan**, jos
  sen voi välttää: lue laitteen FIFO tyhjäksi ja lähetä tavut yhdellä
  kertaa, tai käytä DMA:ta.

## Itsearviointi

- Osaat kertoa, miksi jono kopioi alkiot ja milloin osoittimen
  välittäminen on parempi.
- Osaat selittää, miten tehtävä odottaa jonossa ja miksi se yrittää
  herättyään uudelleen.
- Osaat valita aikarajan ja täyden jonon käsittelytavan tilanteen
  mukaan.
- Osaat välittää dataa keskeytyksestä tehtävälle jonolla ja tunnistaa,
  milloin tavu kerrallaan on liian raskasta.

# Ylikuorma ja vikojen leviäminen

Suuri järjestelmä ei yleensä kaadu siksi, että yksi osa hajoaa, vaan
siksi, että häiriö leviää. Hidas tietokanta tekee sovelluspalvelimista
hitaita, hitaat palvelimet keräävät pyyntöjä jonoihin, jonot kuluttavat
muistin ja säikeet, asiakkaat yrittävät uudelleen, ja uudelleenyritykset
moninkertaistavat kuorman juuri silloin, kun kapasiteettia on vähiten.
Aikarajat, uudelleenyritys, katkaisija ja laipio yksittäisen kutsun
tasolla ovat taidossa *Palveluarkkitehtuurit*. Tämä luku katsoo samoja
asioita koko järjestelmän tasolla: miten kuorma rajataan ja miten
estetään, että lyhyt häiriö muuttuu pysyväksi.

## Nopeusrajoitus

Nopeusrajoitus suojaa palvelua yksittäiseltä asiakkaalta, joka lähettää
liikaa: virheellinen skripti, kaavija, hyökkäys tai vain suuri asiakas.
Yleisin menetelmä on *token bucket*. Sankoon mahtuu tietty määrä merkkejä,
ja sinne valuu merkkejä tasaisella nopeudella. Pyyntö kuluttaa merkin,
ja tyhjästä sangosta pyyntö hylätään. Pitkän ajan nopeus on rajattu,
mutta lyhyt purske sallitaan. Sama algoritmi muotoilee liikennettä
linkillä; taidossa *Tietoliikennetekniikka* sen nimi on rahakkeen
ämpäri.

```{.python tiedosto="esimerkit/jarjestelma/rajoitin.py" osa="sanko"}
```

Kokeessa raja on 5 pyyntöä sekunnissa ja 10 pyynnön purske:

```{.python tiedosto="esimerkit/luku09/rajoitus.py" osa="paikallinen"}
```

Kun palvelimia on useita, jokaisen oma sanko antaa asiakkaalle
moninkertaisen rajan. Jaettu raja tarvitsee jaetun tilan. Redisissä
sanko päivitetään Lua-skriptillä, joka suoritetaan atomisesti, ja aika
otetaan Redisin kellosta, jotta palvelinten kellojen erot eivät vaikuta:

```{.python tiedosto="esimerkit/jarjestelma/rajoitin.py" osa="lua"}
```

```{.python tiedosto="esimerkit/luku09/rajoitus.py" osa="jaettu"}
```

```{.tuloste tiedosto="esimerkit/luku09/rajoitus.odotettu"}
```

Jaettu raja lisää jokaiseen pyyntöön Redis-kutsun. Jos se on liian
kallis tai Redis on poissa, tavallinen kompromissi on paikallinen raja,
joka on jaettu palvelinten määrällä, ja jaettu raja vain suurille
asiakkaille. Hylätty pyyntö saa vastauksen `429 Too Many Requests` ja
otsakkeen `Retry-After`, jotta asiakas tietää, milloin yrittää uudelleen.

## Uudelleenyritysmyrsky

Uudelleenyritys on hyödyllinen satunnaisille virheille ja tuhoisa
ylikuormalle. Simulaatiossa palvelu ehtii 100 pyyntöä sekunnissa ja
kuorma on 80. Kymmenen sekunnin ajan kapasiteetti putoaa puoleen
(tietokannan varmuuskopio, naapurin kuorma). Asiakkaat luopuvat
sekunnin jälkeen ja yrittävät uudelleen. Palvelin ei tiedä, että asiakas
on luopunut, joten se käsittelee jonossa odottavan pyynnön silti:

```{.python tiedosto="esimerkit/luku09/myrsky.py" osa="simulaatio"}
```

```{.tuloste tiedosto="esimerkit/luku09/myrsky.odotettu"}
```

![Tulosteen kolme riviä ajan funktiona. Häiriö kestää kymmenen
sekuntia; naiivilla uudelleenyrityksellä onnistuneiden vastausten määrä
putoaa nollaan eikä palaa, vaikka kapasiteetti on jälleen
täysi.](kuvat/myrsky.png){width=72%}

Naiiveilla uudelleenyrityksillä palvelu ei palaudu koskaan. Häiriö
loppuu 20 sekunnin kohdalla, mutta silloin jonossa on jo niin paljon
vanhoja pyyntöjä, että jokainen käsitelty pyyntö on jo hylätty, ja
jokainen hylätty pyyntö tuo uudelleenyrityksen jonoon. Kuorma on
moninkertainen alkuperäiseen nähden, ja kaikki työ menee hukkaan. Tila
on *metastabiili*: se pysyy, vaikka laukaisija on poissa, ja vaatii
toimenpiteen, kuten kuorman katkaisun tai palvelun uudelleenkäynnistyksen.

Kaksi korjausta:

- **Uudelleenyritysbudjetti** rajaa uudelleenyritykset osuuteen
  pyynnöistä (tässä 10 %) ja lisää eksponentiaalisen viiveen ja hajonnan.
  Kuorma ei kasva moninkertaiseksi, ja palvelu palautuu. Palautuminen
  kestää silti 20 sekuntia, koska jonossa on hylättyjä pyyntöjä, joita
  käsitellään turhaan.
- **Määräaika** (*deadline propagation*) kulkee pyynnön mukana, ja
  palvelin pudottaa vanhentuneet pyynnöt käsittelemättä. Hukkatyö
  poistuu, ja palvelu palautuu heti häiriön päätyttyä. gRPC välittää
  määräajan automaattisesti; HTTP:ssä se kulkee otsakkeessa.

Uudelleenyritykset kertautuvat myös kerroksittain: jos käyttöliittymä,
yhdyskäytävä ja kolme palvelukerrosta yrittävät kukin kolmesti, alin
palvelu saa pahimmillaan 3^5^ = 243 kutsua yhtä käyttäjän pyyntöä kohden.
Siksi uudelleenyritetään yhdessä kerroksessa, yleensä lähimpänä
käyttäjää tai lähimpänä vikaa, ei kaikissa.

## Kuorman pudotus ja siisti heikentyminen

Kun kuormaa on enemmän kuin kapasiteettia, osa pyynnöistä epäonnistuu
joka tapauksessa. Hallittu pudotus (*load shedding*) valitsee, mitkä:

- **Hylkää aikaisin.** Pyyntö, joka hylätään saapuessaan, maksaa vähän.
  Pyyntö, joka hylätään jonon jälkeen, on kuluttanut muistia ja aikaa.
  Rajaa samanaikaiset pyynnöt (luku 3: Littlen laki) ja hylkää ylimenevät.
- **Priorisoi.** Kassalle tuleva pyyntö on arvokkaampi kuin suositusten
  esihaku. Pudota ensin taustatyö ja vähemmän tärkeät pyynnöt.
- **Käytä LIFO:a ylikuormassa.** Vanhin jonossa oleva pyyntö on
  todennäköisimmin jo hylätty asiakkaan päässä; uusin ei ole.

Siisti heikentyminen (*graceful degradation*) tarkoittaa, että palvelu
toimii karsittuna, kun jokin sen osa on poissa: suosituksia ei näytetä,
haku palauttaa välimuistista vanhemman tuloksen, ja kuvat näytetään
pienempinä. Tämä on suunniteltava etukäteen. Jokaisesta riippuvuudesta
kysytään, onko se välttämätön vai vain hyödyllinen, ja hyödyllisen
riippuvuuden katko käsitellään paikallisesti eikä välitetä käyttäjälle
virheenä. Luvun 12 palvelu jatkaa ilman välimuistia, kun Redis on poissa.

## Laipiot

Laipio (*bulkhead*) erottaa resurssit, jotta yksi hidas riippuvuus ei vie
kaikkia. Jos kaikki pyynnöt jakavat 200 säiettä ja yksi riippuvuus
hidastuu niin, että sen kutsut kestävät 10 sekuntia, kaikki säikeet
odottavat lopulta sitä, ja muutkin toiminnot pysähtyvät. Kun
riippuvuudelle on oma 20 säikeen allas, vain sen toiminnot pysähtyvät.
Laipio mitoitetaan Littlen lailla: riippuvuuden kutsut sekunnissa kertaa
normaali kesto, ja sen päälle varaa. Sama ajatus toistuu suuremmassa
mittakaavassa: erilliset palvelinryhmät eri asiakkaille tai toiminnoille
(*cell-based architecture*) rajaavat vian vaikutuksen yhteen soluun.

## Käytännössä

- **Rajoita nopeutta reunalla.** Token bucket asiakasta kohden, `429` ja
  `Retry-After`; jaettu raja, kun palvelimia on monta.
- **Uudelleenyritä budjetilla, viiveellä ja hajonnalla.** Eksponentiaalinen
  viive ilman hajontaa synkronoi asiakkaat, ja ne yrittävät taas yhtä
  aikaa.
- **Välitä määräaika.** Palvelimen ei pidä tehdä työtä, jonka tulosta
  kukaan ei enää odota.
- **Uudelleenyritä yhdessä kerroksessa.** Kerrosten uudelleenyritykset
  kertautuvat.
- **Hylkää aikaisin ja priorisoi.** Rajaa samanaikaiset pyynnöt ja
  pudota vähiten tärkeä työ ensin.
- **Suunnittele heikentyminen.** Tiedä jokaisesta riippuvuudesta, mitä
  tapahtuu, kun se on poissa, ja testaa se.

## Itsearviointi

- Osaat toteuttaa token bucket -rajoittimen paikallisesti ja jaettuna
  Redisissä ja kertoa, miksi paikalliset rajat kertautuvat.
- Osaat selittää, miten uudelleenyritykset tekevät lyhyestä häiriöstä
  metastabiilin ylikuorman.
- Osaat estää uudelleenyritysmyrskyn budjetilla, viiveellä, hajonnalla ja
  määräajan välittämisellä.
- Osaat suunnitella kuorman pudotuksen, siistin heikentymisen ja laipiot.

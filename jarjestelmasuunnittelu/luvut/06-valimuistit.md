# Välimuistit

Välimuisti pitää usein luetun datan lähempänä ja nopeammassa muistissa
kuin sen varsinainen lähde. Se on järjestelmäsuunnittelun tehokkain
yksittäinen keino: kun luvut ovat moninkertaisia kirjoituksiin nähden
(luku 2), välimuisti voi poistaa suurimman osan tietokannan kuormasta ja
pudottaa latenssin millisekunneista alle millisekunnin. Hinta on
konsistenssi. Välimuistissa on kopio, ja kopio voi olla vanhentunut.

Välimuisteja on joka kerroksessa: selaimessa, CDN:ssä,
kuormantasaajassa, sovelluksen muistissa, erillisessä
välimuistipalvelussa kuten Redisissä tai Memcachedissa ja tietokannan
sisällä. Tämä luku käsittelee erillistä välimuistipalvelua, mutta samat
kysymykset koskevat kaikkia: mitä tallennetaan, kauanko ja miten kopio
pidetään ajan tasalla.

## Strategiat

| Strategia     | Toiminta                                                        | Hyvää ja huonoa                                       |
|---------------------|-----------------------------------------------------|-----------------------------------------------|
| cache-aside   | sovellus katsoo muistista ja hakee hudin kannasta; kirjoitus kantaan ja poisto muistista | yksinkertainen ja muistin katko ei kaada; ensimmäinen luku hidas, kilpatilanteet |
| read-through  | välimuisti hakee hudin kannasta itse                            | sovellus yksinkertaisempi; välimuisti tuntee kannan   |
| write-through | kirjoitus muistiin ja kantaan samalla kertaa                    | muisti aina tuore; jokainen kirjoitus hitaampi        |
| write-back    | kirjoitus muistiin, kantaan myöhemmin                           | nopeat kirjoitukset; data voi kadota                  |

Yleisin on *cache-aside* (*lazy loading*): sovellus katsoo ensin
välimuistista ja hakee puuttuvan kannasta.

```{.python tiedosto="esimerkit/jarjestelma/valimuisti.py" osa="rinnalla"}
```

Kokeessa 10 000 tuotteen suosio noudattaa Zipfin jakaumaa, kuten
verkkopalveluissa yleensä: muutama tuote saa suuren osan katseluista.

```{.python tiedosto="esimerkit/luku06/valimuisti.py" osa="osumat"}
```

```{.tuloste tiedosto="esimerkit/luku06/valimuisti.odotettu"}
```

Ensimmäisellä kierroksella välimuisti on kylmä, ja osumasuhde jää 56
prosenttiin. Toisella kierroksella suosituimmat tuotteet ovat jo
muistissa, ja 82 % pyynnöistä osuu. Kylmä välimuisti on todellinen
riski: kun välimuistiklusteri käynnistetään uudelleen tai avainten jako
muuttuu (luku 5), tietokanta saa hetkessä moninkertaisen kuorman.
Siksi välimuisti lämmitetään tai liikenne nostetaan vähitellen.

## TTL ja invalidointi

Vanhentunutta kopiota vastaan on kaksi keinoa. *Elinaika* (TTL) poistaa
arvon tietyn ajan kuluttua, jolloin vanhentunut arvo elää enintään TTL:n
verran. *Invalidointi* poistaa tai päivittää arvon, kun data muuttuu.
Käytännössä tarvitaan molemmat: invalidointi pitää muistin tuoreena, ja
TTL korjaa tilanteet, joissa invalidointi epäonnistui tai unohtui.

Cache-aside-mallissa on kilpatilanne, joka jättää vanhan arvon muistiin
invalidoinnista huolimatta. Pyyntö A toteaa hudin ja hakee arvon
kannasta, mutta haku on hidas. Sillä välin B päivittää kannan ja
poistaa arvon muistista. Kun A:n haku valmistuu, A tallentaa vanhan
arvonsa, ja se jää muistiin TTL:n ajaksi. Lomitus näytetään
vaiheittain, jotta tulos on joka ajolla sama:

```{.python tiedosto="esimerkit/luku06/valimuisti.py" osa="kilpa"}
```

Ilman suojaa muistiin jää vanha hinta 10.00, vaikka kannassa on 12.00.
*Vuokra* (*lease*) korjaa tämän. Huti saa lyhytaikaisen vuokran, ja
tallennus onnistuu vain, jos vuokra on yhä voimassa. Invalidointi
poistaa myös vuokran, joten invalidointia ennen haettu arvo hylätään.
Redisissä tarkistus ja tallennus tehdään Lua-skriptillä, joka
suoritetaan atomisesti:

```{.python tiedosto="esimerkit/jarjestelma/valimuisti.py" osa="vuokra"}
```

Malli on Facebookin Memcache-julkaisusta. Kevyempiä vaihtoehtoja ovat
lyhyt TTL (vanha arvo elää vain hetken), viivästetty toinen poisto
(*delayed double delete*) ja versionumero, joka tallennetaan arvon
mukana ja jota verrataan kirjoitettaessa.

## Välimuistiryntäys

Kun suosittu avain vanhenee, kaikki sitä samaan aikaan pyytävät toteavat
hudin ja kysyvät kannalta yhtä aikaa (*cache stampede*, *thundering
herd*). Jos haku on raskas, kanta ylikuormittuu juuri silloin, kun
välimuisti ei suojaa sitä. Sama vuokra estää ryntäyksen: vain vuokran
saanut hakee, ja muut odottavat hetken ja lukevat sitten muistista.

```{.python tiedosto="esimerkit/luku06/ryntays.py" osa="ryntays"}
```

```{.tuloste tiedosto="esimerkit/luku06/ryntays.odotettu"}
```

Muita keinoja ovat arvon uudistaminen taustalla ennen vanhenemista
(*refresh-ahead*), satunnainen hajonta TTL:ään, jotta avaimet eivät
vanhene yhtä aikaa, ja todennäköisyyteen perustuva ennenaikainen
uudistus, jossa jokainen lukija uudistaa arvon pienellä
todennäköisyydellä, joka kasvaa vanhenemisen lähestyessä.

## Kun muisti loppuu

Välimuistilla on rajattu koko, ja kun se täyttyy, jokin on poistettava.
Redis valitsee poistettavan politiikan mukaan. Kokeessa välimuistille
annetaan neljä megatavua, eli noin kolmannes datasta, ja kesken ajon
suosio siirtyy uusiin tuotteisiin:

```{.python tiedosto="esimerkit/luku06/hadotus.py" osa="politiikat"}
```

```{.tuloste tiedosto="esimerkit/luku06/hadotus.odotettu"}
```

`noeviction` hylkää uudet kirjoitukset, kun muisti on täynnä, joten
muistiin jäävät vanhat suositut tuotteet, eikä välimuisti seuraa
kysynnän muutosta. Häätävät politiikat mukautuvat. LRU ja satunnainen
häätö ovat tässä lähes yhtä hyviä, koska Zipf-jakaumassa suosituimmat
avaimet palaavat muistiin nopeasti joka tapauksessa. LRU on parempi,
kun käyttö on purskeista, ja LFU (`allkeys-lfu`), kun suosio on
pysyvää. Redisin LRU on likimääräinen: se vertaa satunnaista otosta
avaimia, joten tulos vaihtelee hieman ajosta toiseen.

`noeviction` on oikea valinta silloin, kun Redis ei ole välimuisti vaan
tallennus, esimerkiksi istuntojen tai jonojen säilytyspaikka. Silloin
häätö hävittäisi dataa hiljaa, ja virhe on parempi. Sama Redis ei
kannata olla molempia; välimuisti ja tallennus erotetaan omiksi
instansseikseen.

## Mitä välimuistiin ja missä

- **Valmiit vastaukset vai raakadata.** Valmis HTML- tai JSON-vastaus
  säästää eniten työtä, mutta sen invalidointi on vaikeampaa, koska se
  riippuu monesta rivistä. Rivitasoinen välimuisti on helppo
  invalidoida.
- **Paikallinen muisti vai jaettu palvelu.** Prosessin oma muisti on
  nopein (ei verkkoa), mutta jokaisella palvelimella on oma kopionsa,
  eikä invalidointi tavoita niitä kaikkia. Paikallinen välimuisti
  lyhyellä TTL:llä jaetun välimuistin edessä auttaa kuumiin avaimiin.
- **CDN** on välimuisti käyttäjän lähellä staattiselle ja julkiselle
  sisällölle: kuvat, skriptit, julkiset sivut. Se vähentää sekä
  latenssia että omaa kaistaa (luku 2). Invalidointi tehdään
  versioimalla osoitteet (`kuva.3f2a.jpg`) eikä poistopyynnöillä.
- **Negatiivinen välimuisti.** Myös "ei löydy" kannattaa tallentaa
  lyhyeksi ajaksi, jotta olemattomien avainten pyynnöt eivät kuormita
  kantaa (luku 12).

## Käytännössä

- **Aloita cache-asidella, TTL:llä ja invalidoinnilla.** Ne ovat
  yksinkertaisia, ja välimuistin kaatuminen ei kaada palvelua.
- **Aseta aina TTL.** Se rajaa vanhentuneen tiedon iän, vaikka
  invalidointi epäonnistuisi.
- **Suojaa kuumat avaimet ryntäykseltä.** Vuokra, taustauudistus tai
  TTL:n hajonta; ilman niitä yksi vanheneva avain voi kaataa kannan.
- **Varaudu kylmään välimuistiin.** Mitoita kanta tai rajoita kuormaa
  niin, että palvelu kestää välimuistin tyhjenemisen, tai lämmitä
  välimuisti ennen liikenteen ohjaamista.
- **Erota välimuisti ja tallennus.** Välimuisti saa häätää, tallennus ei.
- **Mittaa osumasuhde.** Se kertoo, tekeekö välimuisti työtään, ja sen
  äkillinen lasku on usein ensimmäinen merkki ongelmasta.

## Itsearviointi

- Osaat verrata cache-aside-, read-through-, write-through- ja
  write-back-strategioita ja valita niistä tilanteeseen sopivan.
- Osaat selittää, miten invalidoinnin ja hitaan haun lomittuminen jättää
  vanhan arvon välimuistiin, ja estää sen vuokralla.
- Osaat tunnistaa välimuistiryntäyksen ja estää sen.
- Osaat valita Redisin häätöpolitiikan sen mukaan, onko Redis
  välimuisti vai tallennus.

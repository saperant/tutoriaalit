# Vikasietoisuus ja aikakatkaisut

Verkko-ohjelman virheet eivät ole poikkeuksia vaan arkea: palvelin
käynnistyy uudelleen, yhteys katkeaa, kuorma kasvaa, reititin pudottaa
paketteja ja vastapuoli jumiutuu vastaamatta. Vikasietoinen ohjelma ei
estä näitä, vaan rajaa niiden vaikutuksen. Odotukselle asetetaan
aikaraja, epäonnistunut kutsu yritetään uudelleen hallitusti, toisto ei
tee vahinkoa, ja pysähtyminen tapahtuu siististi. Tämä luku käy nämä
läpi ohjelman näkökulmasta. *Hajautetut järjestelmät* jatkaa
konsensukseen ja replikointiin.

## Aikarajat

Jokainen odotus tarvitsee aikarajan. TCP:n omat rajat ovat pitkiä:
`connect` yrittää kuuden SYN-uudelleenlähetyksen ajan (Linuxissa noin
kaksi minuuttia), ja yhteys, jonka vastapuoli katoaa hiljaa, voi
pysyä auki tunteja tai ikuisesti, jos kumpikaan ei lähetä mitään.
Kolme kohtaa tarvitsee oman rajansa: yhteyden muodostus, vastauksen
odotus ja yhteyden elossaolo.

### Yhteyden muodostus

Estävälle `connect`-kutsulle ei voi antaa aikarajaa suoraan. Tavallinen
ratkaisu on yhdistää estämättömästi: `connect` palauttaa
`EINPROGRESS`, ja kirjoitettavuutta odotetaan `poll`-kutsulla
aikarajan verran. Tulos luetaan valitsimesta `SO_ERROR`, koska
kirjoitettavuus kertoo vain, että yritys päättyi, ei sitä, miten:

```{.c tiedosto="esimerkit/10-aikakatkaisut.c" osa="yhdista"}
```

Testissä palvelin kuuntelee jonolla, johon mahtuu yksi yhteys, eikä
hyväksy niitä. Toinen asiakas ei saa vastausta SYN-segmenttiinsä
(luku 2), ja aikaraja laukeaa:

```{.c tiedosto="esimerkit/10-aikakatkaisut.c" osa="jono"}
```

```{.c tiedosto="esimerkit/10-aikakatkaisut.c" osa="suljettu"}
```

Suljettu portti on eri tilanne: kohde vastaa RST-segmentillä, ja
`ECONNREFUSED` tulee heti. Aikaraja ja kieltäytyminen kertovat eri
asioita. Kieltäytyminen tarkoittaa, että kone on elossa mutta palvelu
ei, kun taas aikaraja voi tarkoittaa ylikuormaa, palomuuria tai
kadonnutta konetta.

### Vastauksen odotus

`SO_RCVTIMEO` ja `SO_SNDTIMEO` antavat estäville kutsuille aikarajan:
`recv` palauttaa `EAGAIN`, jos dataa ei tule ajoissa:

```{.c tiedosto="esimerkit/10-aikakatkaisut.c" osa="rcvtimeo"}
```

Raja koskee yksittäistä kutsua eikä koko viestiä. Hidas vastapuoli,
joka lähettää tavun juuri ennen rajan umpeutumista, pitää yhteyttä
auki loputtomiin. Koko operaatiolle tarvitaan siksi *määräaika*
(deadline): absoluuttinen hetki, jonka jälkeen luovutetaan, ja jonka
perusteella jokaisen odotuksen raja lasketaan uudelleen. Luvun 9
asiakas toimii näin. Tapahtumasilmukassa sama hoituu ajastimilla
(luku 8).

### Elossaolo

Kun yhteydellä ei kulje dataa, kumpikaan osapuoli ei huomaa, että
toinen on kadonnut esimerkiksi sähkökatkon tai NAT-taulun
tyhjentymisen vuoksi. TCP:n *keepalive* lähettää hiljaisella
yhteydellä koetussegmenttejä ja katkaisee yhteyden virheellä
`ETIMEDOUT`, jos niihin ei vastata. Linuxin oletus on kaksi tuntia
hiljaisuutta, joten arvot asetetaan itse:

```{.c tiedosto="esimerkit/10-aikakatkaisut.c" osa="keepalive"}
```

```{.tuloste tiedosto="esimerkit/10-aikakatkaisut.odotettu"}
```

Keepalive havaitsee vain hiljaisen yhteyden. Jos dataa on lähetetty
eikä sitä kuitata, TCP lähettää sitä uudelleen kasvavin välein noin 15
minuutin ajan (`tcp_retries2`). `TCP_USER_TIMEOUT` rajaa tämän ajan.
Monet sovellusprotokollat (HTTP/2:n PING, WebSocketin ping, gRPC:n
keepalive) tekevät saman sovellustasolla. Silloin koetus kulkee myös
välityspalvelinten läpi, ja se mittaa sovelluksen eikä vain ytimen
elossaoloa.

## Uudelleenyritys

Ohimenevä virhe kannattaa yrittää uudelleen, pysyvä ei. Yhteyden
katkeaminen, aikaraja ja ylikuorma (`ECONNREFUSED`, `ETIMEDOUT`,
`ECONNRESET`, HTTP 503, gRPC `UNAVAILABLE`) voivat korjaantua.
Virheellinen pyyntö tai puuttuvat oikeudet eivät korjaannu.

Uudelleenyritys on myös vaarallinen. Kun palvelu ylikuormittuu, sen
asiakkaat epäonnistuvat yhtä aikaa ja yrittävät uudelleen yhtä aikaa.
Kuorma moninkertaistuu juuri silloin, kun palvelu on heikoimmillaan.
Tätä kutsutaan nimellä *retry storm*. Siksi viive kasvaa
eksponentiaalisesti, ja siihen lisätään satunnaisuutta (jitter), jotta
samaan aikaan epäonnistuneet asiakkaat hajaantuvat. *Täysi
satunnaisuus* arpoo viiveen nollan ja eksponentiaalisen rajan väliltä:

```{.c tiedosto="esimerkit/10-uudelleenyritys.c" osa="viive"}
```

```{.c tiedosto="esimerkit/10-uudelleenyritys.c" osa="silmukka"}
```

Esimerkin aika on simuloitu: palvelu herää hetkellä 1 s, ja kello
siirtyy viiveiden verran. Toinen osa mittaa, kuinka moni tuhannesta
asiakkaasta osuu neljännellä yrityksellään samaan 50 millisekunnin
jaksoon:

```{.c tiedosto="esimerkit/10-uudelleenyritys.c" osa="lauma"}
```

```{.tuloste tiedosto="esimerkit/10-uudelleenyritys.odotettu"}
```

Ilman satunnaisuutta kaikki tuhat iskevät samalla hetkellä. Täysi
satunnaisuus levittää ne niin, että pahimmassakin jaksossa on vain
murto-osa. Muita tarpeellisia rajoja ovat yritysten enimmäismäärä,
koko operaation määräaika ja *uudelleenyritysbudjetti*: esimerkiksi
korkeintaan 10 % kutsuista saa olla toistoja. Jos palvelu on
pitkään rikki, *katkaisija* (circuit breaker) lopettaa kutsut kokonaan
hetkeksi ja päästää sitten läpi yksittäisiä koekutsuja. Silloin
toipuvaa palvelua ei kaadeta uudelleen.

## Idempotenssi

Kun vastaus jää tulematta, asiakas ei tiedä, suoritettiinko pyyntö
(luku 9). Uudelleenyritys on turvallinen vain, jos toisto ei muuta
lopputulosta eli operaatio on *idempotentti*. "Aseta saldoksi 10" on
idempotentti, "lisää saldoon 10" ei ole. Esimerkissä palvelin kirjaa
talletuksen, mutta vikaharjoitus hävittää vastauksen, ja asiakas
yrittää uudelleen:

```{.c tiedosto="esimerkit/10-idempotenssi.c" osa="asiakas"}
```

Ei-idempotentista operaatiosta tehdään idempotentti antamalla
pyynnölle yksilöllinen *idempotenssiavain*. Asiakas luo sen kerran ja
lähettää sen jokaisella yrityksellä. Palvelin muistaa käsitellyt
avaimet ja niiden vastaukset ja palauttaa toistolle saman vastauksen
kirjaamatta uudelleen:

```{.c tiedosto="esimerkit/10-idempotenssi.c" osa="palvelin"}
```

```{.c tiedosto="esimerkit/10-idempotenssi.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-idempotenssi.odotettu"}
```

Ilman tunnistetta asiakkaan talletus kirjattiin kahdesti. Tunnisteen
kanssa lopputulos on sama kuin ilman vikaa. Käytännössä avaimet
tallennetaan samaan tietokantatapahtumaan kuin itse muutos, jotta
kaatuminen niiden välissä ei riko takuuta. Avaimet pidetään muistissa
rajatun ajan, esimerkiksi vuorokauden. Maksurajapinnat (Stripen
`Idempotency-Key`-otsake) ja viestijonojen "täsmälleen kerran"
-käsittely perustuvat samaan: verkko voi toimittaa viestin *vähintään
kerran*, ja vastaanottajan toistojen tunnistus tekee siitä *vaikutukseltaan
kerran*.

## Siisti sammutus

Palvelin pysähtyy ennemmin tai myöhemmin: päivitys, siirto toiselle
koneelle tai kuormantasaajan skaalaus. Järjestelmänhallinta (systemd,
Kubernetes) lähettää ensin `SIGTERM`-signaalin ja odottaa hetken
(Kubernetesissa oletuksena 30 s) ennen `SIGKILL`-signaalia. Siisti
sammutus käyttää tämän ajan:

1. Lopeta uusien yhteyksien hyväksyminen (sulje kuunteleva soketti).
2. Vie kesken olevat pyynnöt loppuun.
3. Kerro asiakkaille, että yhteys päättyy: TCP:ssä `shutdown(SHUT_WR)`,
   HTTP/2:ssa `GOAWAY`, omissa protokollissa erillinen viesti.
4. Odota, että asiakkaat sulkevat, tai aikaraja.
5. Vapauta resurssit ja lopeta.

`SIGTERM` otetaan vastaan tapahtumasilmukassa `signalfd`-kuvaajana.
Signaali estetään tavallisena signaalina, jolloin se odottaa
kuvaajassa luettavaksi eikä keskeytä ohjelmaa satunnaisessa kohdassa:

```{.c tiedosto="esimerkit/10-sammutus.c" osa="palvelin"}
```

Testi lähettää signaalin, kun palvelin on aloittanut 300 millisekunnin
työn:

```{.c tiedosto="esimerkit/10-sammutus.c" osa="kulku"}
```

```{.tuloste tiedosto="esimerkit/10-sammutus.odotettu"}
```

Kesken ollut työ valmistui ja vastaus toimitettiin, yhteys päättyi
siististi, ja uusi yhteys hylättiin heti. Kuormantasaajan takana
palvelin ilmoittaa lisäksi ensin olevansa poistumassa (valmiusreitti
palauttaa virheen), jotta tasaaja ehtii ohjata uudet yhteydet muualle
ennen kuin kuuntelija suljetaan.

## Käytännössä

- **Aikaraja jokaiseen odotukseen:** yhteyden muodostus, jokainen
  vastaus ja koko operaation määräaika. Oletusarvot ovat minuutteja tai
  tunteja.
- **Keepalive pitkille yhteyksille:** TCP:n keepalive minuuteissa tai
  sovelluksen oma ping, sekä `TCP_USER_TIMEOUT` lähetetylle datalle.
- **Eksponentiaalinen viive ja täysi satunnaisuus:** sekä yritysten
  enimmäismäärä, budjetti ja katkaisija.
- **Yritä uudelleen vain ohimeneviä virheitä ja idempotentteja
  operaatioita:** tee muista idempotentteja avaimella.
- **Sammu siististi:** `SIGTERM` silmukkaan, kuuntelija kiinni,
  keskeneräiset loppuun ja aikaraja kaikelle.
- **Testaa viat:** vikojen injektointi (luku 11) on ainoa tapa nähdä,
  toimivatko nämä.

## Itsearviointi

- Osaat muodostaa yhteyden määräajassa estämättömällä `connect`-kutsulla
  ja erottaa aikarajan ja kieltäytymisen.
- Osaat asettaa vastaukselle aikarajan ja selittää eron yksittäisen
  kutsun aikarajan ja operaation määräajan välillä.
- Osaat säätää keepalive-asetukset ja `TCP_USER_TIMEOUT`-valitsimen.
- Osaat toteuttaa uudelleenyrityksen eksponentiaalisella viiveellä ja
  täydellä satunnaisuudella ja perustella, miksi satunnaisuus tarvitaan.
- Osaat tehdä ei-idempotentista operaatiosta turvallisesti toistettavan
  idempotenssiavaimella ja toteuttaa siistin sammutuksen.

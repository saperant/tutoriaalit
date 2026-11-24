# Tavuvirta ja viestien rajaus

TCP siirtää *tavuvirtaa*. Se takaa, että tavut saapuvat perille
kerran ja oikeassa järjestyksessä, mutta se ei tiedä mitään
sovelluksen viesteistä. Kaksi `send`-kutsua voi saapua yhtenä
`recv`-palana, ja yksi `send` voi saapua monena. Lähettäjän TCP
pilkkoo ja yhdistelee dataa segmenteiksi oman harkintansa mukaan
(Naglen algoritmi, MSS, ruuhkaikkuna), ja vastaanottaja palauttaa
kerralla sen, mitä puskurissa sattuu olemaan.

## Kaksi lähetystä, yksi vastaanotto

Esimerkin asiakas lähettää kaksi riviä kahdella kutsulla ja sulkee
yhteyden. Palvelin odottaa, että yhteyden loppu on saapunut
(`POLLRDHUP`), jolloin kaikki data on varmasti puskurissa, ja lukee
kerran:

```{.c tiedosto="esimerkit/03-osittainen.c" osa="lahettaja"}
```

```{.c tiedosto="esimerkit/03-osittainen.c" osa="yhdessa"}
```

Yksi `recv` sai molemmat rivit. Ohjelma, joka olettaa yhden
`recv`-kutsun vastaavan yhtä viestiä, toimii testissä, jossa
viestit lähetetään hitaasti yksi kerrallaan, ja hajoaa kuormassa, kun
viestit kasautuvat. Virhe on yleinen juuri siksi, että se ei näy
kehittäjän koneella.

## Osittaiset luvut ja kirjoitukset

Toinen puoli on päinvastainen: `recv(fd, puskuri, n, 0)` palauttaa
*enintään* n tavua, eli sen, mitä vastaanottopuskurissa sillä hetkellä
on. Esimerkki pienentää palvelimen vastaanottopuskurin 16 kibitavuun
ja vastaanottaa mebitavun:

```{.c tiedosto="esimerkit/03-osittainen.c" osa="vajaa"}
```

```{.tuloste tiedosto="esimerkit/03-osittainen.odotettu"}
```

Myös `send` voi kirjoittaa vähemmän kuin pyydettiin. Estävä soketti
odottaa yleensä, kunnes kaikki mahtuu lähetyspuskuriin, mutta signaali
voi keskeyttää kutsun kesken. Estämätön soketti (luku 7) palauttaa
heti sen, mikä mahtui. Kumpaankin suuntaan tarvitaan siksi silmukka.
Otsakkeen apufunktiot toistavat kutsua, kunnes kaikki on siirretty,
toistavat keskeytetyn kutsun (`EINTR`) ja erottavat siistin lopun
virheestä:

```{.c tiedosto="esimerkit/verkko.h" osa="kaikki"}
```

`lue_tasan` palauttaa nollan vain, jos yhteys sulkeutui *ennen*
ensimmäistä tavua eli viestien välissä. Jos yhteys sulkeutui kesken
viestin, kyse on virheestä (`EPROTO`): vastapuoli kaatui tai yhteys
katkesi. Tämä erottelu tarvitaan aina, kun viesteillä on rajat.

Lippu `MSG_WAITALL` pyytää `recv`-kutsua odottamaan koko määrää. Se
kuitenkin palaa vajaana signaalin, virheen tai yhteyden lopun
vuoksi, joten silmukkaa se ei korvaa.

## Viestien rajaus

Sovellus palauttaa viestirajat itse. Tapoja on kolme:

| Tapa | Esimerkkejä | Hyvää | Huonoa |
|------------------|----------------------------|-------------------------|------------------------|
| kiinteä koko | monet laitteiden protokollat | yksinkertainen | tuhlaa tai ei riitä |
| pituusetuliite | TLS-tietue, gRPC, PostgreSQL | nopea, binääri kelpaa | koko tiedettävä etukäteen |
| erotin | HTTP/1.1-otsakkeet, SMTP, Redis | luettava, virtaa | erotin ei saa esiintyä datassa |

### Pituusetuliite

Jokaisen viestin edellä on sen pituus kiinteän kokoisena
kokonaislukuna verkon tavujärjestyksessä. Lähettäjä kokoaa otsakkeen
ja datan yhdeksi kirjoitukseksi `writev`-kutsulla (scatter–gather).
Kaksi erillistä pientä kirjoitusta voisi lähteä kahtena segmenttinä,
ja Naglen algoritmin ja viivästetyn kuittauksen yhteisvaikutus voisi
viivästää jälkimmäistä kymmeniä millisekunteja:

```{.c tiedosto="esimerkit/03-pituus.c" osa="laheta"}
```

Vastaanottaja lukee ensin täsmälleen neljä tavua, sitten täsmälleen
niin monta kuin otsake kertoo. Pituus tarkistetaan ennen muistin
varaamista. Ilman rajaa yksi neljän tavun viesti voisi pakottaa
palvelimen varaamaan neljä gibitavua:

```{.c tiedosto="esimerkit/03-pituus.c" osa="vastaanota"}
```

```{.c tiedosto="esimerkit/03-pituus.c" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/03-pituus.odotettu"}
```

Nollan tavun viesti on kelvollinen ja eri asia kuin yhteyden loppu.
Siksi funktio palauttaa tilan ja pituuden erikseen eikä yhtenä
lukuna.

### Erotin

Tekstiprotokollissa viesti on rivi. Lukija puskuroi: yksi `recv` voi
tuoda puolikkaan rivin, ja silloin luetaan lisää. Toisaalta se voi
tuoda useita rivejä, ja silloin ylimääräiset säästetään seuraaville
kutsuille. Puskurin koko on samalla rivin enimmäispituus:

```{.c tiedosto="esimerkit/03-rivit.c" osa="lukija"}
```

Esimerkin asiakas lähettää komennot tarkoituksella hankalina
paloina ja kytkee Naglen algoritmin pois (`TCP_NODELAY`), jotta palat
lähtevät todennäköisesti erillisinä segmentteinä:

```{.c tiedosto="esimerkit/03-rivit.c" osa="asiakas"}
```

```{.tuloste tiedosto="esimerkit/03-rivit.odotettu"}
```

Tuloste on sama riippumatta siitä, miten palat saapuvat, ja juuri sitä
testi mittaa. Rivinvaihdoksi hyväksytään sekä CRLF (`\r\n`), jota
Internet-protokollat käyttävät, että pelkkä LF. Rivin pituusraja on
yhtä tärkeä kuin viestin kokoraja: ilman sitä asiakas voi lähettää
loputonta riviä, jota palvelin puskuroi, kunnes muisti loppuu.

Saman puskuroinnin tarjoaa myös stdio: `fdopen` tekee soketista
`FILE`-olion, ja `fgets` lukee siitä rivin. Se on kätevä estävien
sokettien rivipohjaisille protokollille, ja sitä käytetään luvuissa 6
ja 10. Se ei sovi estämättömille soketeille,
koska `fgets` ei kerro, oliko rivi kesken.

## Naglen algoritmi ja TCP_NODELAY

Naglen algoritmi pidättää pientä segmenttiä, kun edellinen on vielä
kuittaamatta, ja kokoaa pienet kirjoitukset yhteen. Algoritmi säästää
kaistaa, mutta pyyntö–vastaus-protokollassa se voi yhdessä
vastaanottajan viivästetyn kuittauksen kanssa lisätä vasteaikaan
kymmeniä millisekunteja. Interaktiiviset protokollat (SSH, pelit,
RPC) kytkevät sen yleensä pois `TCP_NODELAY`-valitsimella ja kokoavat
viestin itse yhdeksi kirjoitukseksi. `TCP_CORK` toimii päinvastoin:
se pidättää kaiken, kunnes korkki poistetaan, ja sopii esimerkiksi
otsakkeen ja tiedoston lähettämiseen yhdessä.

## Käytännössä

- **Älä oleta viestirajoja:** jokainen TCP-protokolla tarvitsee
  kehyksen. Yksi `recv` ei ole yksi viesti.
- **Lue ja kirjoita silmukassa:** `lue_tasan` ja `kirjoita_kaikki`
  (tai kirjaston vastaavat) eivät ole valinnaisia.
- **Rajoita koot:** viestin ja rivin enimmäiskoko tarkistetaan
  ennen varausta, ja ylitys katkaisee yhteyden.
- **Erota siisti loppu katkeamisesta:** nolla viestien välissä on
  normaalia; nolla kesken viestin on virhe.
- **Kokoa viesti yhdeksi kirjoitukseksi:** `writev` tai oma puskuri.
  `TCP_NODELAY` interaktiivisiin protokolliin.
- **Testaa pilkotulla syötteellä:** luvun 11 häiritsijä tai
  tavu kerrallaan lähettävä asiakas paljastaa rajavirheet heti.

## Itsearviointi

- Osaat selittää, miksi TCP:n vastaanottaja voi saada kaksi viestiä
  yhdellä `recv`-kutsulla tai yhden viestin monella.
- Osaat kirjoittaa funktiot, jotka lukevat ja kirjoittavat tarkan
  tavumäärän ja käsittelevät `EINTR`-keskeytyksen ja kesken jäävän
  yhteyden.
- Osaat toteuttaa pituusetuliitteisen kehyksen kokorajoineen ja
  rivipohjaisen kehyksen puskuroivalla lukijalla.
- Osaat kertoa, mitä Naglen algoritmi tekee ja milloin
  `TCP_NODELAY` kannattaa ottaa käyttöön.

# Testaus ja vianetsintä

Verkko-ohjelman virheet ilmenevät harvoin kehittäjän koneella. Siellä
viive on nolla, häviöitä ei ole, data tulee yhtenä palana ja
vastapuoli on aina paikalla. Testien on siksi luotava olosuhteet, joita
silmukkaosoite ei itse tuota: pilkottu data, katkenneet yhteydet,
hitaat ja kadonneet vastapuolet. Vianetsintä taas tarvitsee näkymän
siihen, mitä ydin ja verkko todella tekivät.

## Paikallinen asiakas–palvelin-testi

Tämän tutoriaalin esimerkit ovat kaikki saman mallin mukaisia
testejä. Malli kannattaa toistaa omissa projekteissa:

- **Prosessi tai säie kummallekin osapuolelle**, käynnistettynä
  testistä itsestään. Lapsiprosessi kuolee vanhempansa mukana
  (`PR_SET_PDEATHSIG`), eikä orpoja palvelimia jää.
- **Portti 0 ja `getsockname`:** testit voi ajaa rinnakkain samalla
  koneella, ja CI:n muut työt eivät häiritse.
- **Synkronointi tapahtumilla, ei nukkumalla:** odota yhteyttä,
  vastausta, tiedoston loppua tai prosessin päättymistä.
  `sleep(1)` on joko turhan pitkä tai joskus liian lyhyt.
- **Vahtikoira:** `alarm` tai testikehyksen aikaraja, jotta jumiutuva
  testi kaatuu eikä pysäytä koko ajoa.
- **Deterministinen tuloste:** ei aikoja, portteja eikä
  prosessinumeroita. Satunnaisuus kiinteällä siemenellä.

Protokollan logiikka kannattaa erottaa I/O:sta. Puhdas funktio
tavuista rakenteeseen (luvun 5 `pura`) ja tilakone, joka saa
tapahtumia ja tuottaa lähetettäviä tavuja, ovat testattavissa ilman
soketteja yksikkötesteinä ja sumealla testauksella. Sokettitestit
varmistavat sen jälkeen, että osat toimivat yhdessä.

## Vikojen injektointi

Kun vika ei tapahdu itsestään, se tuotetaan. Yksinkertainen ja
tehokas väline on *häiritsijä*: välityspalvelin asiakkaan ja palvelimen
välissä, joka välittää dataa mutta pilkkoo sen, viivästää sitä tai
katkaisee yhteyden. Sovellusta ei tarvitse muuttaa, vain osoite
vaihtuu. Esimerkin häiritsijä pilkkoo virran 1–8 tavun paloiksi ja
voi katkaista yhteyden, kun palvelimelta on välitetty tietty määrä
tavuja:

```{.c tiedosto="esimerkit/11-hairitsija.c" osa="valittaja"}
```

Asiakas lähettää pituusetuliitteisiä viestejä (luku 3) ja tarkistaa
jokaisen kaiun:

```{.c tiedosto="esimerkit/11-hairitsija.c" osa="asiakas"}
```

```{.tuloste tiedosto="esimerkit/11-hairitsija.odotettu"}
```

Pilkottu virta ei haitannut kehyskäsittelyä, ja katkaisu kesken
viestin tunnistettiin virheeksi (`EPROTO`) eikä siistiksi lopuksi.
Asiakas, joka olettaisi yhden `recv`-kutsun vastaavan yhtä viestiä,
olisi kaatunut jo ensimmäisessä tilassa.

Valmiita välineitä on useita:

| Väline | Mitä tekee | Taso |
|------------------|------------------------------------------|------------|
| `tc netem` | viive, värinä, häviö, monistus ja järjestyksen sekoitus | Linuxin jono |
| `iptables`/`nft` | pudottaa tai hylkää paketteja (`DROP`, `REJECT`) | palomuuri |
| Toxiproxy | TCP-välityspalvelin: viive, kaistaraja, katkaisu | sovellus |
| `strace -e inject` | järjestelmäkutsu palauttaa valitun virheen | prosessi |
| Chaos Mesh, Litmus | viat Kubernetes-ympäristöön | klusteri |

Esimerkiksi komento `tc qdisc add dev lo root netem delay 50ms loss
5%` hidastaa ja hävittää silmukkaosoitteen liikennettä koko koneelta.
Komento vaatii pääkäyttäjän oikeudet, ja siksi se ajetaan omassa
verkkonimiavaruudessaan (*Tietoverkot* ja *Virtualisointi*).
`strace -e inject=recvfrom:error=ECONNRESET:when=3` saa ohjelman
kolmannen `recvfrom`-kutsun epäonnistumaan, mikä testaa
virheenkäsittelyä ilman verkkoa lainkaan.

## Vianetsinnän työkalut

Kun ohjelma ei toimi, ensimmäinen kysymys on, missä vika on:
sovelluksessa, ytimessä vai verkossa. Työkalut kertovat eri kerrosten
tilan:

| Kysymys | Työkalu | Esimerkki |
|------------------------------------|------------------|--------------------------------|
| kuunteleeko kukaan? | `ss -tlnp` | portit ja prosessit |
| missä tilassa yhteydet ovat? | `ss -tanpi` | tila, jonot, RTT, ikkuna |
| mitä kutsuja ohjelma tekee? | `strace -f -e trace=network` | `connect`, `recv`, virheet |
| mitä verkossa kulkee? | `tcpdump -i lo port 8080` | SYN, RST, uudelleenlähetykset |
| toimiiko palvelu käsin? | `nc`, `socat`, `curl` | kirjoita protokollaa itse |
| onko nimi oikein? | `getent hosts`, `dig` | kuten ohjelma vs. DNS suoraan |

`ss` näyttää yhteyksien jonot. Kuuntelevan soketin `Recv-Q` on
kuuntelujonon pituus. Jos se on täynnä, palvelin ei ehdi hyväksyä
yhteyksiä (luku 2). Yhteyden `Send-Q`, joka vain kasvaa, tarkoittaa,
että vastapuoli ei lue, ja `Recv-Q`, joka kasvaa, että oma ohjelma ei
lue. Valitsin `-i` näyttää TCP:n sisäiset tiedot, kuten kiertoajan,
ruuhkaikkunan ja uudelleenlähetykset.

`strace` kertoo, mitä ohjelma pyysi ytimeltä ja mitä se sai. Monet
"verkko-ongelmat" ovat ohjelman omia: väärä osoiteperhe, `EAGAIN`,
jota ei käsitelty, tai `recv`, jonka palauttamaa pituutta ei luettu.
`getent hosts` selvittää nimen samalla tavalla kuin ohjelman
`getaddrinfo` (`/etc/hosts` ja `nsswitch.conf` mukaan lukien), kun
taas `dig` kysyy suoraan DNS:ltä. Jos tulokset eroavat, vika on
nimipalvelun asetuksissa eikä verkossa.

## Havainnoitavuus tuotannossa

Tuotannossa debuggeria ei voi kytkeä, joten ohjelma kertoo tilastaan
itse:

- **Mittarit:** avoimet yhteydet, pyynnöt ja virheet tyypeittäin,
  vasteajan jakauma (prosenttipisteet, ei keskiarvo), jonojen
  pituudet ja uudelleenyritykset.
- **Lokit:** yhteyden avaus ja sulkeminen syineen sekä pyynnön
  tunniste jokaisella rivillä. Silloin yhden pyynnön kulku löytyy.
- **Jäljitys:** hajautetussa järjestelmässä pyynnön tunniste ja
  ajoitukset välitetään palvelulta toiselle (W3C Trace Context,
  OpenTelemetry), ja koko ketju nähdään yhtenä jälkenä.

## Käytännössä

- **Testaa viat, ei vain onnistumista:** pilkottu data, katkaisu
  kesken viestin, hidas ja kadonnut vastapuoli ja jokaisen kutsun
  virhepaluu.
- **Häiritsijä testiympäristöön:** oma välityspalvelin, Toxiproxy tai
  netem omassa nimiavaruudessaan.
- **Protokollalogiikka erilleen I/O:sta:** puhtaat funktiot ja
  tilakoneet ovat testattavissa nopeasti ilman soketteja.
- **Ensin `ss` ja `strace`, sitten `tcpdump`:** useimmat viat näkyvät
  jo ohjelman ja ytimen rajalla.
- **Mittaa vasteajat jakaumana:** keskiarvo kätkee ne hitaat pyynnöt,
  joista käyttäjät valittavat.

## Itsearviointi

- Osaat kirjoittaa paikallisen asiakas–palvelin-testin, joka ei riipu
  porttinumeroista, ajoituksesta eikä ympäristöstä.
- Osaat rakentaa tai käyttää välityspalvelinta, joka pilkkoo ja
  katkaisee yhteyksiä, ja testata sillä kehyskäsittelyn.
- Osaat injektoida virheitä `strace`- ja `tc netem` -työkaluilla.
- Osaat selvittää `ss`-, `strace`- ja `tcpdump`-työkaluilla, onko vika
  sovelluksessa, ytimessä vai verkossa.

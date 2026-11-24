# Reititys ja NAT

Reititys vie paketin aliverkosta toiseen. Jokainen kone ja reititin
tekee saman päätöksen jokaiselle paketille: katsoo kohdeosoitteen,
etsii reititystaulusta parhaan reitin ja lähettää paketin joko suoraan
kohteelle (sama aliverkko) tai seuraavalle reitittimelle (*next hop*).
Kukaan ei tunne koko polkua; jokainen tietää vain seuraavan askeleen.

## Reititystaulu ja pisin etuliite

Reititystaulun rivillä on kohdeverkko, seuraava reititin tai liitäntä ja
metriikka. Jos useampi reitti sopii, valitaan se, jonka etuliite on
**pisin** (*longest prefix match*), koska se on tarkin. Tasatilanteessa
ratkaisee pienin metriikka. Oletusreitti `0.0.0.0/0` sopii kaikkeen ja
on siksi aina viimeinen vaihtoehto.

```{.python tiedosto="esimerkit/05-reitityshaku.py" osa="haku"}
```

```{.python tiedosto="esimerkit/05-reitityshaku.py" osa="taulu"}
```

```{.tuloste tiedosto="esimerkit/05-reitityshaku.odotettu"}
```

`10.20.2.9` sopii sekä reittiin `/16` että `/24`; `/24` voittaa.
Lineaarinen haku riittää esimerkiksi, mutta Internetin runkoreitittimen
taulussa on yli miljoona reittiä, ja haku tehdään etuliitepuulla
(*trie*) tai erikoispiirillä (TCAM) nanosekunneissa.

## Reititin laboratoriossa

Reititin on kone, jolla on liitäntä kahdessa verkossa ja joka välittää
paketteja niiden välillä. Linuxissa välitys kytketään päälle asetuksella
`net.ipv4.ip_forward`:

```{.bash tiedosto="esimerkit/05-reititin.sh" osa="verkko"}
```

```{.bash tiedosto="esimerkit/05-reititin.sh" osa="vaiheet"}
```

```{.tuloste tiedosto="esimerkit/05-reititin.odotettu"}
```

Kolme vaihetta kertovat, mitä reititykseen tarvitaan:

1. **Reitti.** Ilman reittiä A ei tiedä, minne paketti lähetetään, ja
   `ping` päättyy heti virheeseen *Network is unreachable*.
2. **Välitys.** Reitittimen on suostuttava välittämään paketteja.
   Ilman sitä paketti saapuu R:lle, joka hylkää sen, koska kohde ei ole
   sen oma osoite.
3. **Paluureitti.** B:n on tiedettävä, miten vastaus pääsee takaisin.
   Tässä B:n oletusreitti osoittaa R:ään. Unohtunut paluureitti on
   yleinen vika: kysely lähtee, vastaus ei palaa.

Vastauksen `ttl=63` kertoo, että paketti kulki yhden reitittimen läpi
(Linux lähettää arvolla 64). `ip route get` näyttää, minkä reitin ydin
valitsisi, ja on vianetsinnän tärkein komento. Reitit `proto kernel` ydin
lisäsi itse, kun liitännälle annettiin osoite.

## Staattinen ja dynaaminen reititys

Tässä reitit annettiin käsin (*staattinen reititys*). Pienissä verkoissa
ja palvelinten oletusreiteissä se riittää. Suuremmissa verkoissa
reitittimet kertovat toisilleen tuntemistaan verkoista
*reitityskäytännöillä*: OSPF organisaation sisällä ja BGP
organisaatioiden välillä. Ne käsitellään taidossa
*Verkkoinfrastruktuuri*.

## Osoitteenmuunnos (NAT)

Yksityisiä osoitteita ei reititetä Internetissä. Kotien ja yritysten
reititin muuttaa lähtevien pakettien lähdeosoitteen omaksi julkiseksi
osoitteekseen ja kirjaa muunnoksen *yhteystauluun* (*conntrack*).
Vastaus tulee reitittimen osoitteeseen, ja taulusta reititin tietää,
kenelle se kuuluu. Tätä kutsutaan nimillä NAT, NAPT, PAT tai
*masquerade*.

```{.bash tiedosto="esimerkit/05-nat.sh" osa="nat"}
```

```{.tuloste tiedosto="esimerkit/05-nat.odotettu"}
```

Ilman NAT:ia ping saapuu palvelimelle yksityisestä osoitteesta, johon
palvelimella ei ole reittiä, joten vastaus ei palaa. NAT:n jälkeen
palvelin näkee reitittimen osoitteen `203.0.113.5`, ja vastaus palaa.
Sääntö kirjoitettiin nftablesilla, Linuxin nykyisellä
pakettisuodattimella. Palomuurisäännöt käsitellään taidossa
*Verkkoinfrastruktuuri*.

NAT:n seuraukset ohjelmoijalle:

- **Ulkoa ei voi avata yhteyttä NAT:n takana olevaan koneeseen** ilman
  porttiohjausta. Siksi vertaisyhteydet (pelit, videopuhelut) tarvitsevat
  apukeinoja (STUN, TURN, ICE).
- **Palvelin näkee reitittimen osoitteen**, ei asiakkaan. Monta
  asiakasta voi näkyä samasta osoitteesta, joten IP-osoite ei yksilöi
  käyttäjää. Välityspalvelimen takana alkuperäinen osoite välitetään
  otsakkeessa (`X-Forwarded-For`, `Forwarded`), johon saa luottaa vain,
  jos sen asettaja on oma välityspalvelin.
- **Yhteystaulun merkinnät vanhenevat.** Pitkään hiljaa ollut
  TCP-yhteys katkeaa, kun merkintä poistuu. Pitkäikäiset yhteydet
  lähettävät *keepalive*-viestejä.

## Käytännössä

- **`ip route get OSOITE` ensin.** Se kertoo valitun reitin,
  liitännän ja lähdeosoitteen ilman yhtään pakettia.
- **Tarkista paluusuunta.** Kun kysely lähtee mutta vastaus ei palaa,
  vika on usein paluureitissä, NAT:ssa tai palomuurissa. Kaappaa
  liikenne vastaanottajan päässä.
- **Yksi oletusreitti.** Kaksi oletusreittiä eri liitännöissä (esim.
  WLAN ja kaapeli tai VPN) tuottaa satunnaisia ongelmia. Käytä
  metriikoita tai erillisiä reitityskäytäntöjä (`ip rule`).
- **Älä rakenna sovelluksen logiikkaa IP-osoitteen varaan.** NAT,
  välityspalvelimet ja mobiiliverkot vaihtavat ja jakavat osoitteita.

## Itsearviointi

- Osaat selittää pisimmän etuliitteen säännön ja ennustaa, minkä
  reitin reititystaulu valitsee annetulle osoitteelle.
- Osaat rakentaa reitittimen kahden aliverkon välille ja selittää,
  miksi reitti, välitys ja paluureitti tarvitaan.
- Osaat tulkita `ip route`- ja `ip route get` -komentojen tulosteet ja
  TTL-arvon.
- Osaat selittää NAT:n toiminnan ja sen vaikutukset sovelluksiin.

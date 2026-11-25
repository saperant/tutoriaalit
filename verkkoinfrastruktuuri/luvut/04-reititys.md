# Reitityksen suunnittelu

Reititin välittää IP-paketteja verkkojen välillä reititystaulunsa
perusteella. Taulun voi kirjoittaa käsin (staattinen reititys), tai
reitittimet voivat kertoa toisilleen tuntemansa verkot
reititysprotokollalla. Organisaation sisällä käytetään tyypillisesti
OSPF:ää, organisaatioiden ja operaattorien välillä BGP:tä. Tässä luvussa
rakennetaan kaikki kolme ja politiikkareititys, jolla liikenteen polku
valitaan muunkin kuin kohdeosoitteen perusteella.

## Staattinen reititys

Kaksi toimipistettä, joiden välillä on yksi yhteys:

```{.dot otsikko="Staattisen reitityksen laboratorio"}
graph {
  rankdir=LR; nodesep=0.4; ranksep=0.35;
  h1 [label="h1\n10.1.0.10/24"];
  r1 [label="r1\nlan 10.1.0.1/24\n172.16.12.1/30"];
  r2 [label="r2\n172.16.12.2/30\nlan 10.2.0.1/24"];
  h2 [label="h2\n10.2.0.10/24"];
  h1 -- r1; r1 -- r2; r2 -- h2;
}
```

```{.bash tiedosto="esimerkit/04-staattinen.sh" osa="reitit"}
```

Isännille riittää oletusreitti (`default`), joka osoittaa paikalliseen
yhdyskäytävään. Reitittimet tuntevat suoraan liitetyt verkkonsa, ja
toisen toimipisteen verkko kirjataan käsin. Lisäksi
`net.ipv4.ip_forward=1` kytkee välityksen päälle; ilman sitä Linux on
isäntä, joka hylkää muille osoitetut paketit.

Reititystaulusta valitaan aina **pisin vastaava etuliite** (*longest
prefix match*): `/24`-reitti voittaa `/16`-reitin, joka voittaa
oletusreitin. `ip route get` kertoo, minkä reitin ydin valitsee:

```{.bash tiedosto="esimerkit/04-staattinen.sh" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/04-staattinen.odotettu"}
```

Reitittimellä `r1` ei ole oletusreittiä, joten tuntematon kohde on
tavoittamaton. Paluureitti unohtuu helposti: yhteys toimii vain, jos
myös vastapuoli osaa reitittää vastauksen takaisin. Kun ping ei
kulje, tarkistetaan reitit molempiin suuntiin.

Staattinen reititys sopii pieniin verkkoihin ja reunoille, joissa on
yksi tie ulos. Se ei reagoi vikoihin: jos yhteys katkeaa, reitti jää
tauluun ja liikenne katoaa.

## OSPF: linkkitilareititys organisaation sisällä

OSPF:ssä (*Open Shortest Path First*) jokainen reititin kertoo
naapureilleen omat liitäntänsä ja niiden kustannukset. Tieto tulvitetaan
koko alueelle, jolloin jokaisella reitittimellä on sama kartta verkosta
(*link-state database*), josta se laskee lyhimmät polut Dijkstran
algoritmilla. Muutos yhdessä paikassa leviää sekunneissa, ja reitit
lasketaan uudelleen.

Kolme reititintä renkaassa, kullakin oma lähiverkkonsa. BIRD-reititysdemoni
ajaa OSPF:ää ja vie oppimansa reitit ytimen reititystauluun.

```{.dot otsikko="OSPF-laboratorion rengas. Kaikkien yhteyksien kustannus on sama, joten r1 käyttää suoraa yhteyttä r2:n lähiverkkoon. Kun yhteys r1–r2 katkaistaan, ainoa polku kulkee r3:n kautta."}
graph {
  nodesep=1.3; ranksep=0.8;
  r1 [label="r1\nlähiverkko 10.0.1.0/24"];
  r2 [label="r2\nlähiverkko 10.0.2.0/24"];
  r3 [label="r3\nlähiverkko 10.0.3.0/24"];
  r1 -- r2 [label="172.16.12.0/30\nkatkaistaan", style=dashed,
            color="#B04848", fontcolor="#B04848"];
  r1 -- r3 [label="172.16.13.0/30"];
  r2 -- r3 [label="172.16.23.0/30"];
  {rank=same; r2; r3}
}
```

```{.bash tiedosto="esimerkit/04-ospf.sh" osa="bird"}
```

Siirtoyhteydet ovat kahden reitittimen välisiä (`type ptp`), joten
OSPF:n ei tarvitse valita yhteydelle nimettyä reititintä (DR). Lähiverkot
ovat *stub*-liitäntöjä: niiden verkot mainostetaan, mutta niillä ei
lähetetä OSPF-viestejä, joten työasema ei voi esittäytyä reitittimeksi.
Ajastimet (`hello 1; dead 3`) ovat laboratoriota varten lyhyitä.
Oletuksena naapuri todetaan kuolleeksi 40 sekunnissa; tuotannossa nopea
vikojen havaitseminen tehdään BFD:llä.

Kun yhteys `r1`–`r2` katkeaa, `r1` laskee reitit uudelleen:

```{.bash tiedosto="esimerkit/04-ospf.sh" osa="katko"}
```

```{.tuloste tiedosto="esimerkit/04-ospf.odotettu"}
```

Suuret OSPF-verkot jaetaan **alueisiin**: runkoalue 0 ja sen ympärillä
muut alueet. Alueen rajalla reitit kootaan, joten yhden alueen muutokset
eivät käynnistä laskentaa koko verkossa. Hierarkkinen osoitesuunnitelma
tekee kokoamisesta helppoa.

## BGP: reititys organisaatioiden välillä

BGP (*Border Gateway Protocol*) on internetin reititysprotokolla. Siinä
ei lasketa lyhimpiä polkuja, vaan jokainen autonominen järjestelmä
(AS) päättää **politiikallaan**, mitä reittejä se hyväksyy ja mitä
se kertoo eteenpäin. Polun valintaan vaikuttavat AS-polun pituus,
paikallinen suosituimmuus ja muut attribuutit, joita säädetään
suodattimilla.

BGP on myös suurimpien internet-katkojen lähde: kun joku ilmoittaa
vahingossa verkkoja, joita hän ei omista, liikenne ohjautuu väärään
paikkaan (*route leak*, *hijack*). Siksi operaattori hyväksyy
asiakkaaltaan vain sovitut etuliitteet. Esimerkissä asiakas ilmoittaa
verkkonsa ja virheellisesti myös oletusreitin.

```{.dot otsikko="BGP-laboratorio: kaksi autonomista järjestelmää ja suodattimien paikat. Kumpikin pää suodattaa sekä lähettämänsä että vastaanottamansa ilmoitukset."}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.3;
  a [label="asiakas\nAS 65001\nvie vain omat verkot,\nei tuo mitään"];
  o [label="operaattori\nAS 65002\ntuo vain lohkon\n203.0.113.0/24"];
  a -> o [label="203.0.113.0/24: hyväksytään"];
  a -> o [label="0.0.0.0/0: hylätään", style=dashed, color="#B04848",
          fontcolor="#B04848"];
}
```

```{.bash tiedosto="esimerkit/04-bgp.sh" osa="asiakas"}
```

Operaattorin suodatin hyväksyy vain asiakkaalle osoitetun lohkon:

```{.bash tiedosto="esimerkit/04-bgp.sh" osa="operaattori"}
```

```{.tuloste tiedosto="esimerkit/04-bgp.odotettu"}
```

Asiakkaan puolella on toinen tärkeä suodatin: `import none` ja tarkasti
rajattu `export`. Asiakas, joka on yhteydessä kahteen operaattoriin, ei
saa koskaan välittää yhden operaattorin reittejä toiselle, koska silloin
siitä tulee kauttakulkuverkko näiden välillä.

Internetissä etuliitteiden alkuperä varmennetaan RPKI:llä: verkon haltija
allekirjoittaa, mikä AS saa ilmoittaa sen (ROA), ja reitittimet hylkäävät
ristiriitaiset ilmoitukset. Konesaleissa BGP:tä käytetään myös
sisäisesti, koska se skaalautuu ja sen politiikat ovat ilmaisuvoimaisia
(RFC 7938).

## Politiikkareititys

Tavallisesti reitti valitaan kohdeosoitteen perusteella. Joskus polku
pitää valita lähteen, palvelun tai merkinnän perusteella: vierasverkko
käyttää halvempaa yhteyttä, varmuuskopiot kulkevat omaa reittiään tai
palvelimen vastaus palaa samaa yhteyttä kuin pyyntö tuli. Linuxissa
tähän on useita reititystauluja ja säännöt, jotka valitsevat taulun:

```{.bash tiedosto="esimerkit/04-politiikka.sh" osa="politiikka"}
```

```{.bash tiedosto="esimerkit/04-politiikka.sh" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-politiikka.odotettu"}
```

Säännöt käydään läpi prioriteettijärjestyksessä, ja ensimmäinen osuva
taulu, josta reitti löytyy, ratkaisee. Säännön ehtona voi olla myös
tuloliitäntä tai palomuurin asettama merkki (`fwmark`), jolloin polku
voidaan valita esimerkiksi kohdeportin mukaan.

## Käytännössä

- **Staattinen reunalla, dynaaminen ytimessä.** Yhden yhteyden
  toimipisteessä staattinen oletusreitti on yksinkertaisin ja
  vikasiedoltaan riittävä. Kun polkuja on useita, dynaaminen reititys
  reagoi vikoihin ilman ihmistä.
- **Kokoa reitit rajoilla.** Hierarkkinen osoitteistus ja kootut
  reitit pitävät taulut pieninä ja rajaavat muutosten vaikutuksen.
- **Ei OSPF:ää käyttäjäverkkoihin.** Käyttäjäsegmentit ovat passiivisia
  (stub) liitäntöjä, ja naapuruudet todennetaan, jotta verkkoon ei voi
  liittää omaa reititintä.
- **BGP:ssä aina suodattimet molempiin suuntiin.** Hyväksy vain se, mitä
  odotat, ja ilmoita vain omasi. Käytä etuliitteiden enimmäismäärää
  (*max-prefix*) ja RPKI-validointia. Oletuksena salliva BGP-istunto on
  onnettomuus, joka odottaa tapahtumistaan.
- **Mittaa konvergenssi.** Testaa, kauanko yhteyden katkeamisesta
  kestää, että liikenne kulkee uutta reittiä. Se on vikasietoisuuden
  todellinen mitta.
- **`ip route get` ja paluureitti** ovat reititysvikojen ensimmäiset
  tarkistukset.

## Itsearviointi

- Osaat rakentaa staattisen reitityksen kahden verkon välille ja
  selittää pisimmän etuliitteen säännön ja paluureitin merkityksen.
- Osaat määrittää OSPF:n siirtoyhteyksille ja passiivisille lähiverkoille
  ja selittää, miten se laskee reitit uudelleen vian jälkeen.
- Osaat määrittää eBGP-istunnon suodattimineen ja selittää, miksi
  asiakkaan ja operaattorin pitää suodattaa molempiin suuntiin.
- Osaat ohjata liikennettä lähdeosoitteen perusteella omalla
  reititystaululla ja säännöllä.

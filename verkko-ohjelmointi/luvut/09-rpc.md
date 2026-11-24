# Etäproseduurikutsut (RPC)

Etäproseduurikutsu (remote procedure call) kätkee viestinvälityksen
funktiokutsun taakse: asiakas kutsuu `summa(40, 2)`, ja tulos lasketaan
toisessa prosessissa, kenties toisella mantereella. Ajatus on 1970-luvulta,
ja Birrell ja Nelson kuvasivat sen toteutuksen vuonna 1984. Sen jälkeen
sitä on toteutettu lukemattomia kertoja: Sun RPC (NFS), CORBA, DCOM,
Java RMI, XML-RPC ja SOAP, Thrift, JSON-RPC ja gRPC. *Palveluarkkitehtuurit*
käsittelee RPC:tä arkkitehtuurin osana. Tässä luvussa se rakennetaan
itse, jotta näkyy, mitä kirjastot tekevät ja missä abstraktio vuotaa.

## RPC:n osat

Jokainen RPC-järjestelmä koostuu samoista osista:

1. **Rajapinnan kuvaus:** metodit, argumentit ja paluuarvot, usein
   kieliriippumattomana skeemana (IDL).
2. **Sarjallistaminen:** argumenttien ja tulosten koodaus tavuiksi
   (luku 5).
3. **Kehystys ja kuljetus:** viestit TCP:n, HTTP/2:n tai UDP:n päällä
   (luku 3).
4. **Pyyntöjen yhdistäminen vastauksiin:** tunniste, jotta yhdellä
   yhteydellä voi olla monta kutsua kesken.
5. **Virheet ja määräajat:** etäkutsu voi epäonnistua tavoilla, joita
   paikallinen kutsu ei tunne.
6. **Tyngät (stub):** asiakkaan funktiot, jotka näyttävät paikallisilta,
   ja palvelimen runko, joka kutsuu toteutusta. Yleensä
   koodigeneraattori tuottaa ne skeemasta.

## Oma RPC

Esimerkin kehys on kiinteän kokoinen: pituus, pyyntötunniste,
metodin numero (vastauksessa tilakoodi) ja kaksi 32-bittistä
argumenttia. Koodaus tehdään tavuina kuten luvussa 5:

```{.cpp tiedosto="esimerkit/09-rpc.cpp" osa="protokolla"}
```

Palvelin lukee pyyntöjä ja suorittaa jokaisen omassa säikeessään.
Hidas kutsu ei siis viivytä nopeita, ja vastaukset lähtevät
valmistumisjärjestyksessä. Koska usea säie kirjoittaa samaan
sokettiin, kirjoitukset sarjallistetaan lukolla. Muuten kahden säikeen
kehykset voisivat lomittua tavutasolla:

```{.cpp tiedosto="esimerkit/09-rpc.cpp" osa="palvelin"}
```

Asiakas voi lähettää monta pyyntöä odottamatta vastauksia
(*putkitus*, pipelining). Vastaukset tunnistetaan tunnisteesta, ja
ne, joita ei vielä kysytty, talletetaan. Tulos on `std::expected`:
joko arvo tai virhe. Siitä näkyy tyypin tasolla, että etäkutsu voi
epäonnistua:

```{.cpp tiedosto="esimerkit/09-rpc.cpp" osa="asiakas"}
```

```{.cpp tiedosto="esimerkit/09-rpc.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-rpc.odotettu"}
```

Hidas kutsu lähetettiin ensimmäisenä, mutta sen vastaus saapui
viimeisenä. Tunnisteet yhdistivät vastaukset oikeisiin kutsuihin.
Viimeinen kutsu ylitti määräaikansa: asiakas lakkasi odottamasta 100
millisekunnin jälkeen, vaikka palvelin jatkoi työtä 500 millisekuntia.
Sen myöhästynyt vastaus olisi talletettu ja jätetty käyttämättä.
Asiakkaan pitäisi siivota tällaiset, ja oikeissa järjestelmissä
asiakas lähettää palvelimelle peruutuksen.

## Missä abstraktio vuotaa

Etäkutsu näyttää paikalliselta, mutta se ei ole sellainen. Waldo ym.
("A Note on Distributed Computing", 1994) ja Deutschin *hajautetun
laskennan harhaluulot* (verkko on luotettava, viive on nolla, kaista
on ääretön…) listaavat erot. Tärkeimmät ovat seuraavat:

- **Osittainen epäonnistuminen:** kun määräaika ylittyy, asiakas ei
  tiedä, suoritettiinko kutsu. Se ei ehkä saapunut, se suoritettiin ja
  vastaus katosi, tai se on yhä käynnissä. Uudelleenyritys on turvallinen
  vain idempotenteille operaatioille (luku 10).
- **Viive:** etäkutsu on tuhansista miljooniin kertoja hitaampi kuin
  paikallinen.
  Rajapinta, joka kutsuu `hae_nimi(id)` silmukassa tuhat kertaa, on
  suunniteltava uudelleen eräkutsuksi.
- **Muisti ei ole yhteinen:** osoittimia ja viittauksia ei voi
  välittää. Kaikki kopioidaan, ja suuret rakenteet maksavat.
- **Versiot elävät eri tahtiin:** asiakas ja palvelin päivitetään eri
  aikaan, joten skeeman on kestettävä laajennukset (luku 5).

Hyvä RPC-kirjasto tekee nämä näkyviksi eikä kätke niitä. gRPC:ssä
jokaisella kutsulla on määräaika, joka välitetään palvelimelle
(`grpc-timeout`-otsake), ja palvelin voi lopettaa työn, jota kukaan
ei enää odota. Määräaika siirtyy myös eteenpäin, kun palvelin kutsuu
toista palvelua.

## gRPC ja Protocol Buffers

gRPC on yleisin nykyinen RPC-kehys. Rajapinta kuvataan Protocol
Buffers -skeemana, ja `protoc` tuottaa siitä asiakkaan ja palvelimen
koodin kymmenille kielille:

```{.proto tiedosto="esimerkit/09-laskin.proto"}
```

Kenttien numerot (`= 1`, `= 2`) kulkevat viestissä: kenttä koodataan
avaimena, jossa ovat kentän numero ja sen tyyppi varint-muodossa,
ja sen jälkeen tulee arvo. Tyyppi `sint32` käyttää luvun 5
zigzag-koodausta. Tuntemattomat numerot ohitetaan, joten kenttiä voi
lisätä vapaasti, kunhan numeroita ei käytetä uudelleen. Kuljetuksena
on HTTP/2: jokainen kutsu on oma virtansa samalla yhteydellä, joten
putkitus ja rinnakkaiset kutsut ovat sisäänrakennettuja. Kutsuja on
neljää lajia: yksinkertainen, palvelimelta virtaava, asiakkaalta
virtaava ja kaksisuuntainen virta.

Virheet ovat määriteltyjä tilakoodeja (`INVALID_ARGUMENT`,
`DEADLINE_EXCEEDED`, `UNAVAILABLE`, `UNIMPLEMENTED` …). Asiakas voi
päättää koodin perusteella, kannattaako yrittää uudelleen: `UNAVAILABLE`
on ohimenevä, `INVALID_ARGUMENT` ei.

## JSON-RPC

JSON-RPC 2.0 on päinvastainen ääripää: muutaman sivun määrittely
ilman skeemaa ja kuljetusta. Viesti on JSON-olio, jossa ovat metodin
nimi, argumentit ja tunniste. Useamman kutsun voi lähettää eränä
taulukossa:

```{.json tiedosto="esimerkit/09-jsonrpc-pyynto.json"}
```

```{.json tiedosto="esimerkit/09-jsonrpc-vastaus.json"}
```

Erän vastaukset voivat tulla missä järjestyksessä tahansa, joten
ne yhdistetään tunnisteella kuten omassa RPC:ssä. Ilman tunnistetta
lähetetty pyyntö on *ilmoitus*, johon ei vastata. Virhekoodit
-32768…-32000 on varattu määrittelylle; -32602 tarkoittaa
virheellisiä parametreja. JSON-RPC:tä käyttävät
esimerkiksi Language Server Protocol ja Ethereumin solmut.

## REST ei ole RPC

HTTP-rajapinnat suunnitellaan usein *resursseina* eikä metodeina:
`GET /tilit/42`, `PUT /tilit/42`. HTTP:n metodien merkitys on
määritelty (GET ja PUT ovat idempotentteja, POST ei), ja välimuistit
ja välityspalvelimet ymmärtävät ne. RPC-tyylinen `POST /laskeSumma`
käyttää HTTP:tä pelkkänä kuljetuksena. Molemmat ovat perusteltuja:
resurssimalli sopii julkisiin rajapintoihin ja CRUD-tyyppiseen dataan,
RPC palvelujen välisiin kutsuihin, joissa tehokkuus ja tyypitetyt
skeemat ratkaisevat. Valinta kuuluu taitoon *Palveluarkkitehtuurit*.

## Käytännössä

- **Tunniste jokaiseen pyyntöön:** se mahdollistaa putkituksen,
  rinnakkaiset kutsut ja toistojen tunnistamisen (luku 10).
- **Määräaika jokaiseen kutsuun:** ilman määräaikaa yksi jumiutunut
  palvelin pysäyttää kaikki sitä kutsuvat. Välitä määräaika eteenpäin.
- **Virheet tyyppiin:** `std::expected`, `Result` tai tilakoodi.
  Etäkutsun epäonnistuminen ei ole poikkeuksellista.
- **Sarjallista kirjoitukset:** jos monta säiettä vastaa samaan
  yhteyteen, yksi kehys kirjoitetaan kerrallaan.
- **Suunnittele viiveelle:** eräkutsut ja virrat yksittäisten kutsujen
  silmukoiden sijaan.
- **Valmis kehys tuotantoon:** gRPC, Thrift tai JSON-RPC-kirjasto
  tuo skeemat, koodigeneraattorit, uudelleenyrityspolitiikat ja
  havainnoitavuuden.

## Itsearviointi

- Osaat luetella RPC-järjestelmän osat ja kertoa, mitä kukin tekee.
- Osaat toteuttaa yksinkertaisen RPC:n, jossa pyynnöt putkitetaan ja
  vastaukset yhdistetään tunnisteella ja jossa jokaisella kutsulla on
  määräaika.
- Osaat selittää, miksi etäkutsu ei ole paikallinen kutsu, ja mitä
  osittainen epäonnistuminen tarkoittaa uudelleenyrityksille.
- Osaat lukea Protocol Buffers -skeeman ja JSON-RPC-viestin ja kertoa,
  miten ne tukevat laajennuksia ja virheitä.

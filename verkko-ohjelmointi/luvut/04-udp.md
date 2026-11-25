# UDP ja luotettavuus

UDP on TCP:n vastakohta. Yhteyttä ei ole, eikä mitään taata: datagrammi
voi kadota, monistua tai ohittaa edellisen. UDP lupaa vain sen, että
saapunut datagrammi on ehjä (tarkistussumma) ja kokonainen. Kun
TCP:n palvelut eivät sovi sovellukselle, UDP antaa vapauden rakentaa
omat. Yksi myöhästynyt TCP-segmentti pysäyttää kaiken sen perässä
tulevan (head-of-line blocking), joten reaaliaikaiset sovellukset
valitsevat usein UDP:n. Sillä tehdään DNS, pelien tilapäivitykset,
äänen ja kuvan siirto (RTP) sekä QUIC ja sen päällä HTTP/3.

## Datagrammit

UDP-soketti sidotaan osoitteeseen kuten TCP:ssä, mutta `listen`- ja
`accept`-kutsuja ei ole. Jokainen `sendto` kertoo vastaanottajan, ja
jokainen `recvfrom` kertoo lähettäjän:

```{.c tiedosto="esimerkit/04-datagrammit.c" osa="soketti"}
```

```{.c tiedosto="esimerkit/04-datagrammit.c" osa="rajat"}
```

Viestirajat säilyvät: kolme lähetystä on kolme vastaanottoa, myös
nollan tavun datagrammi. Palvelin, joka vastaa usealle asiakkaalle
samalla soketilla, erottaa asiakkaat `recvfrom`-kutsun antamasta
osoitteesta. Osoitteeseen ei kuitenkaan voi luottaa todisteena
lähettäjästä, koska UDP:ssä lähdeosoitteen voi väärentää.
Tämä tekee UDP-palveluista heijastushyökkäysten välineitä: pieni
pyyntö väärennetyllä lähdeosoitteella tuottaa suuren vastauksen
uhrille.

## Koko ja katkaisu

Datagrammi luetaan kerralla. Jos puskuri on liian pieni, loppu
häviää. Lippu `MSG_TRUNC` saa Linuxin palauttamaan datagrammin
todellisen koon, jolloin katkaisu huomataan. IPv4:n UDP-datagrammin
hyötykuorma on enintään 65 507 tavua (65 535 miinus IP- ja
UDP-otsakkeet):

```{.c tiedosto="esimerkit/04-datagrammit.c" osa="katkaisu"}
```

Käytännön raja on paljon pienempi. Linkin MTU:ta (Ethernetissä
1500 tavua) suurempi datagrammi pilkotaan IP-tasolla, ja yhden palan
katoaminen hävittää koko datagrammin. IPv6:ssa reitittimet eivät
pilko lainkaan. Siksi UDP-protokollat pitävät datagrammit polun MTU:n
alla: DNS perinteisesti 512 tavussa ja nykyään 1232 tavussa, QUIC
1200 tavusta ylöspäin polun mukaan.

## Yhdistetty UDP-soketti

`connect` UDP-soketilla ei lähetä mitään verkkoon. Se vain kiinnittää
vastapuolen: `send` ja `recv` toimivat ilman osoitetta, muilta tulevat
datagrammit suodatetaan pois, ja – tärkeimpänä – ydin toimittaa
soketille ICMP-virheilmoitukset:

```{.c tiedosto="esimerkit/04-datagrammit.c" osa="suljettu"}
```

```{.tuloste tiedosto="esimerkit/04-datagrammit.odotettu"}
```

Suljettuun porttiin lähetetty datagrammi tuottaa ICMP-viestin "port
unreachable". Yhdistämätön soketti ei voi tietää, mihin lähetykseen
viesti liittyy, joten ydin jättää sen huomiotta. Yhdistetty soketti
saa sen seuraavan kutsun virheenä (`ECONNREFUSED`). Virhe on
asynkroninen: lähetys onnistui, ja virhe tulee myöhemmin jollekin
toiselle kutsulle. Verkossa ICMP-viestit myös usein suodatetaan, joten
niiden puuttuminen ei todista mitään.

## Luotettavuus itse

Kun UDP:n päälle tarvitaan luotettava siirto, sovellus toteuttaa
TCP:n keskeiset osat: järjestysnumerot, kuittaukset ja
uudelleenlähetyksen. Yksinkertaisin muoto on *pysähdy ja odota*
(stop-and-wait ARQ): lähetä paketti, odota sen kuittausta ja lähetä
uudelleen, jos kuittausta ei kuulu aikarajan sisällä.

```{.dot otsikko="Pysähdy ja odota -protokollan kaksi vikatapausta. Kadonnut paketti ja kadonnut kuittaus näyttävät lähettäjälle samalta: aikaraja umpeutuu, ja paketti lähetetään uudelleen. Jälkimmäisessä vastaanottaja saa paketin kahdesti, joten sen on tunnistettava kaksoiskappale numerosta ja kuitattava se silti."}
digraph {
  nodesep=1.4; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8"];
  t0 [shape=box, width=1.2, label="lähettäjä"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5 -> t0_6 -> t0_7 -> t0_8;
  t1 [shape=box, width=1.2, label="vastaanottaja"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5 -> t1_6 -> t1_7 -> t1_8;
  {rank=same; t0_0; t1_0;}
  {rank=same; t0_1; t1_1;}
  {rank=same; t0_2; t1_2;}
  {rank=same; t0_3; t1_3;}
  {rank=same; t0_4; t1_4;}
  {rank=same; t0_5; t1_5;}
  {rank=same; t0_6; t1_6;}
  {rank=same; t0_7; t1_7;}
  {rank=same; t0_8; t1_8;}
  edge [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false];
  t0_0 -> t1_1 [label="data 0"];
  t1_1 -> t0_2 [label="kuittaus 0"];
  t0_2 -> t1_3 [label="data 1 (katoaa)", color="#B04848", fontcolor="#B04848", style=dashed, arrowhead=tee];
  t0_3 -> t1_4 [label="aikaraja: data 1 uudelleen"];
  t1_4 -> t0_5 [label="kuittaus 1 (katoaa)", color="#B04848", fontcolor="#B04848", style=dashed, arrowhead=tee];
  t0_5 -> t1_6 [label="aikaraja: data 1 uudelleen"];
  t1_6 -> t0_7 [label="kaksoiskappale hylätään, kuittaus 1"];
  t0_7 -> t1_8 [label="data 2"];
}
```

Pakettimuoto koodataan tavuina eikä rakenteena (luku 5):

```{.c tiedosto="esimerkit/04-luotettava.c" osa="paketti"}
```

Häviöitä ei kannata odottaa oikealta verkolta, koska silmukkaosoite
ei hävitä mitään. Esimerkki simuloi häviöllisen kanavan: kiinteällä
siemenellä alustettu näennäissatunnaisgeneraattori pudottaa 25 %
lähetyksistä ja monistaa 10 %. Sama siemen tuottaa saman häviökuvion
joka ajossa, joten virhetilanteet toistuvat:

```{.c tiedosto="esimerkit/verkko.h" osa="satunnainen"}
```

```{.c tiedosto="esimerkit/04-luotettava.c" osa="kanava"}
```

Lähettäjä toistaa pakettia, kunnes saa sen numeroa vastaavan
kuittauksen. Vanhat ja monistuneet kuittaukset ohitetaan:

```{.c tiedosto="esimerkit/04-luotettava.c" osa="lahettaja"}
```

Vastaanottaja toimittaa sovellukselle vain odotetun numeron ja
kuittaa jokaisen jo saadun paketin uudelleen. Kuittaus voi kadota, ja
silloin lähettäjä toistaa paketin, jonka vastaanottaja on jo
toimittanut. Ilman uutta kuittausta lähettäjä jäisi toistamaan sitä
loputtomiin:

```{.c tiedosto="esimerkit/04-luotettava.c" osa="vastaanottaja"}
```

```{.tuloste tiedosto="esimerkit/04-luotettava.odotettu"}
```

Lopetus on protokollan vaikein kohta. Kun vastaanottaja kuittaa
LOPPU-paketin, se ei voi tietää, saapuiko kuittaus. Jos se lopettaisi
heti ja kuittaus katoaisi, lähettäjä yrittäisi turhaan, kunnes
luovuttaisi. Siksi vastaanottaja jää vielä hetkeksi kuuntelemaan ja
kuittaa toistot – sama syy, jonka vuoksi TCP:llä on tila `TIME_WAIT`.
Kahden kenraalin ongelma osoittaa, ettei äärellinen määrä viestejä voi
tehdä molemmista osapuolista varmoja; käytännössä riittää, että
epävarmuus rajataan ajalla.

Pysähdy ja odota -protokolla on hidas: kaistasta käytetään vain yksi
paketti kiertoaikaa kohden. TCP ja QUIC käyttävät *liukuvaa ikkunaa*,
jossa monta pakettia on matkalla yhtä aikaa, sekä valikoivia
kuittauksia, mitattuun kiertoaikaan perustuvaa aikarajaa ja
ruuhkanhallintaa. Menetelmien tehokkuuden vertailu on taidossa
*Tietoliikennetekniikka*. Ennen kuin toteutat omaa luotettavaa
protokollaa, mieti, riittäisikö TCP tai QUIC-kirjasto.

## Käytännössä

- **Valitse UDP perustellusti:** reaaliaikainen data, jossa myöhäinen
  on hyödytöntä, multicast, pienet kysely–vastaus-parit (DNS) tai
  oma protokolla QUIC-kirjaston kautta.
- **Pidä datagrammit pieninä:** alle 1200 tavua, niin IP-tason
  pilkkomista ei tarvita.
- **Tarkista koko:** `MSG_TRUNC` tai riittävän suuri puskuri; liian
  pieni puskuri katkaisee hiljaa.
- **Yhdistä soketti, kun vastapuoli on yksi:** saat ICMP-virheet ja
  vieraiden datagrammien suodatuksen.
- **Älä luota lähdeosoitteeseen:** se voidaan väärentää. Tunnistus
  kuuluu sovellusprotokollaan, ja vastaus ei saa olla pyyntöä paljon
  suurempi ennen tunnistusta.
- **Simuloi häviöt toistettavasti:** kiinteä siemen tekee
  virhetilanteista testattavia.

## Itsearviointi

- Osaat lähettää ja vastaanottaa UDP-datagrammeja ja kertoa, mitä
  UDP takaa ja mitä ei.
- Osaat havaita katkaistun datagrammin ja kertoa, miksi datagrammit
  pidetään polun MTU:n alla.
- Osaat selittää yhdistetyn UDP-soketin hyödyt ja sen, miksi
  `ECONNREFUSED` näkyy vasta seuraavassa kutsussa.
- Osaat toteuttaa pysähdy ja odota -protokollan järjestysnumeroilla,
  kuittauksilla ja uudelleenlähetyksellä ja testata sen simuloidulla
  häviöllä.

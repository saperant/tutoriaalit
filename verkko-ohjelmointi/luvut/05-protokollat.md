# Protokollan suunnittelu ja sarjallistaminen

Protokolla on sopimus kahden ohjelman välillä, ja usein ohjelmat ovat
eri versioita, eri kielillä kirjoitettuja ja eri tekijöiden
tekemiä. Hyvä protokolla on yksiselitteinen tavutasolla, kestää
virheellisen ja vihamielisen syötteen ja sallii laajennukset
rikkomatta vanhoja toteutuksia. Tämä luku käy läpi binääriprotokollan
rakennuspalikat: tavujärjestyksen, tyyppi–pituus–arvo-koodauksen,
vaihtuvanmittaiset kokonaisluvut ja purkajan testauksen.

## Tavujärjestys

Monitavuinen luku voidaan tallentaa merkitsevin tavu ensin
(*big-endian*, verkon tavujärjestys) tai vähiten merkitsevin ensin
(*little-endian*, x86-64 ja käytännössä ARM64). Protokolla määrää
järjestyksen. Internet-protokollat käyttävät big-endiania, monet
uudemmat binäärimuodot (Protocol Buffers, FlatBuffers) little-endiania.

```{.c tiedosto="esimerkit/05-tavujarjestys.c" osa="jarjestys"}
```

`htonl` kääntää tavut little-endian-koneessa eikä tee mitään
big-endian-koneessa. Selkeämpi ja aina siirrettävä tapa on koota luku
bitinsiirroilla. Se ei riipu koneesta eikä tarvitse kohdistettua
osoitinta:

```{.c tiedosto="esimerkit/tlv.h" osa="tavut"}
```

```{.tuloste tiedosto="esimerkit/05-tavujarjestys.odotettu"}
```

C-rakennetta ei lähetetä sellaisenaan. Kääntäjä lisää kenttien väliin
täytettä tasausta varten, ja täytteen määrä, kenttien tavujärjestys ja
jopa `int`-tyypin koko vaihtelevat alustoittain:

```{.c tiedosto="esimerkit/05-tavujarjestys.c" osa="rakenne"}
```

Viiden tavun kentistä tuli kahdeksan tavun rakenne. Täyte sisältää
lisäksi mitä sattuu – usein aiempaa pinon sisältöä –, joten rakenteen
lähettäminen voi vuotaa muistia verkkoon.

Yhtä yleinen virhe on lukea luku puskurin keskeltä
tyyppimuunnoksella. Osoite ei ole luvun tasauksen monikerta, mikä on
C:ssä määrittelemätöntä käytöstä. x86 sallii sen hitaasti, monet ARM-
ja RISC-V-ytimet antavat poikkeuksen, ja kääntäjä saa olettaa, ettei
sitä tapahdu. UBSan pysäyttää ohjelman:

```{.c tiedosto="esimerkit/05-kohdistus.kaatuu.c" osa="virhe"}
```

Oikea tapa on `memcpy` paikalliseen muuttujaan (kääntäjä optimoi sen
yhdeksi käskyksi) tai `lue_u32`.

## TLV-koodaus

*Tyyppi–pituus–arvo* (type–length–value) on laajennettavan
binääriprotokollan perusrakenne. Jokaisen kentän edellä ovat sen
tyyppi ja pituus. Purkaja, joka ei tunne tyyppiä, voi silti hypätä
kentän yli. Esimerkin mittausviestissä on versiotavu ja kolme kenttää:

```{.c tiedosto="esimerkit/tlv.h" osa="malli"}
```

```{.c tiedosto="esimerkit/tlv.h" osa="koodaa"}
```

Purkaja on koodauksen tärkeämpi puoli, koska se käsittelee
vieraalta tullutta dataa. Jokainen pituus tarkistetaan jäljellä
olevaa tavumäärää vastaan *ennen* lukemista, arvojen pituudet ja
sisällöt tarkistetaan tyypin mukaan, ja pakollisten kenttien
olemassaolo tarkistetaan lopuksi:

```{.c tiedosto="esimerkit/tlv.h" osa="pura"}
```

Vertailu `pituus > n - i` on kirjoitettu niin, ettei se voi
vuotaa yli. Luonteva muoto `i + pituus > n` voisi vuotaa, jos
pituus olisi suuri ja tyyppi kapeampi. Tässä se ei vuoda, koska
pituus on enintään 65 535, mutta tapa kannattaa opetella.

```{.c tiedosto="esimerkit/05-tlv.c" osa="kaytto"}
```

```{.c tiedosto="esimerkit/05-tlv.c" osa="uusi"}
```

```{.tuloste tiedosto="esimerkit/05-tlv.odotettu"}
```

## Versiointi ja yhteensopivuus

Protokolla elää pidempään kuin sen ensimmäinen toteutus. Kaksi
periaatetta pitää vanhat ja uudet toteutukset puheväleissä:

- **Taaksepäin yhteensopiva lisäys:** uusi kenttä on valinnainen, ja
  vanha purkaja ohittaa sen. Kenttien numeroita ei koskaan käytetä
  uudelleen eri merkityksessä, eikä vanhan kentän merkitystä
  muuteta.
- **Pääversio rikkovia muutoksia varten:** viestin alussa oleva
  versio kertoo, voiko purkaja ymmärtää viestin. Tuntematonta
  pääversiota ei yritetä arvata, vaan siitä ilmoitetaan virhe.
  Monet protokollat neuvottelevat version kättelyssä (TLS, HTTP/2:n
  ALPN), jolloin yhteys käyttää uusinta molempien tuntemaa versiota.

Robustness-periaate "ole tiukka siinä, mitä lähetät, ja salliva
siinä, mitä vastaanotat" (Postel) on nykyään kiistanalainen: sallivuus
tuottaa toteutuksia, jotka luottavat virheisiin, ja virheet
jähmettyvät standardiksi. RFC 9413 suosittaa sen sijaan tarkkaa
määrittelyä ja virheiden hylkäämistä. Tuntemattomien kenttien
ohittaminen on eri asia: se on määritelty laajennusmekanismi, ei
virheiden sietämistä.

## Vaihtuvanmittaiset kokonaisluvut

Kiinteän kokoinen luku tuhlaa tilaa, kun tyypilliset arvot ovat
pieniä. *Varint* (LEB128) käyttää jokaisesta tavusta seitsemän bittiä
ja kertoo ylimmällä bitillä, jatkuuko luku. Protocol Buffers, WebAssembly
ja DWARF käyttävät sitä. Negatiiviset luvut koodataan ensin
*zigzag*-muunnoksella, muuten -1 veisi kymmenen tavua:

```{.c tiedosto="esimerkit/05-varint.c" osa="varint"}
```

```{.tuloste tiedosto="esimerkit/05-varint.odotettu"}
```

Purkaja rajaa luvun kymmeneen tavuun. Ilman rajaa jatkuvien tavujen
jono saisi sen siirtämään bittejä 64 bitin ohi, mikä on
määrittelemätöntä käytöstä.

## Binääri vai teksti

Sama mittaus vei binäärinä 23 tavua ja tekstinä 45 tavua. Ero ei
yleensä ratkaise valintaa.

| Ominaisuus | Binääri | Teksti (rivit, JSON) |
|---------------------|-------------------------------|-------------------------------|
| koko ja jäsennys | pieni, nopea | suurempi, hitaampi |
| luettavuus | työkalu tarvitaan | `nc` ja silmät riittävät |
| tarkkuus | tyypit ja koot määrätty | luvut ja merkistö tulkinnanvaraisia |
| virheet | rajat tarkistettava itse | jäsentimet monimutkaisia |
| esimerkkejä | TLS, HTTP/2, gRPC, DNS | HTTP/1.1, SMTP, Redis, JSON-RPC |

Tekstiprotokolla ei ole automaattisesti turvallisempi. JSON:n
jäsentimet ovat olleet toistuvasti haavoittuvia, ja sallivat
tekstijäsentimet tulkitsevat saman viestin eri tavoin, mihin
esimerkiksi HTTP request smuggling perustuu. Tärkeintä on, että
muoto on yksiselitteinen ja purkaja tiukka.

## Purkaja vihamielistä syötettä vastaan

Verkosta tuleva data on hyökkääjän hallussa. Purkaja, joka luottaa
viestin omaan pituuskenttään, lukee puskurin ohi:

```{.c tiedosto="esimerkit/05-luottava.kaatuu.c" osa="virhe"}
```

AddressSanitizer pysäyttää ohjelman ilmoitukseen
`heap-buffer-overflow`. Ilman sanitoijaa ohjelma lukisi hiljaa muuta
muistia ja voisi lähettää sen takaisin vastauksessa. Heartbleed
(OpenSSL, 2014) oli juuri tällainen virhe.

### Sumea testaus

Esimerkkejä ei voi keksiä tarpeeksi. *Sumea testaus* (fuzzing)
syöttää purkajalle valtavan määrän rikottuja viestejä ja tarkkailee,
kaatuuko se. Yksinkertaisin muoto ottaa kelvollisen viestin ja rikkoo
sen satunnaisesti:

```{.c tiedosto="esimerkit/05-sumea.c" osa="mutaatio"}
```

Jokainen syöte kopioidaan omaan, tarkan kokoiseen varaukseensa.
Silloin AddressSanitizer huomaa yhdenkin tavun ylilukemisen. Lisäksi
tarkistetaan *invariantti*: jos purkaja hyväksyy viestin, sama sisältö
koodattuna ja purettuna on ennallaan.

```{.c tiedosto="esimerkit/05-sumea.c" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/05-sumea.odotettu"}
```

Sata tuhatta viestiä purettiin alle sekunnissa sanitoijien kanssa, ja
jokainen hylkäys tuli hallitusti oikeasta syystä. Oikeat
sumeat testaajat ovat paljon tehokkaampia: libFuzzer (`clang
-fsanitize=fuzzer`) ja AFL++ mittaavat koodikattavuutta ja kehittävät
syötteitä, jotka vievät uusiin haaroihin. Purkaja kannattaa kirjoittaa
niin, että se on puhdas funktio tavuista rakenteeseen, kuten `pura`.
Silloin sumean testaajan kytkeminen siihen on muutaman rivin työ.

## Valmiit sarjallistamismuodot

Omaa koodausta ei aina tarvitse kirjoittaa. Valmiit muodot tuovat
skeeman, koodigeneraattorin ja versiointisäännöt:

- **Protocol Buffers:** skeema `.proto`-tiedostossa, varint- ja
  TLV-tyyppinen koodaus kenttänumeroin. Käytetään gRPC:ssä (luku 9).
- **FlatBuffers ja Cap'n Proto:** luettavissa suoraan puskurista
  ilman purkuvaihetta (zero-copy), sopii suurille rakenteille.
- **CBOR ja MessagePack:** binäärinen JSON, skeema valinnainen.
- **ASN.1 (DER, PER):** varmenteet, LDAP ja mobiiliverkot. Monimutkainen,
  ja sen purkajissa on ollut paljon haavoittuvuuksia.

## Käytännössä

- **Määrittele tavutasolla:** jokaisen kentän koko, tavujärjestys,
  etumerkki ja merkistö kirjoitetaan auki.
- **Älä lähetä rakenteita:** koodaa kentät tavuina bitinsiirroilla
  tai `memcpy`-kutsulla.
- **Versio ja laajennettavuus alusta asti:** versiotavu ja
  ohitettavat tuntemattomat kentät maksavat vähän ja säästävät
  myöhemmin paljon.
- **Tiukka purkaja:** jokainen pituus rajoja vastaan, jokainen arvo
  tyyppiään vastaan, ja virhe hylkää koko viestin.
- **Purkaja puhtaaksi funktioksi:** helppo testata yksikkötestein ja
  sumealla testauksella sanitoijien kanssa.

## Itsearviointi

- Osaat koodata ja purkaa kokonaislukuja verkon tavujärjestyksessä
  ilman kohdistusvirheitä ja selittää, miksi C-rakennetta ei lähetetä
  sellaisenaan.
- Osaat suunnitella TLV-muotoisen viestin, jota voi laajentaa
  rikkomatta vanhoja purkajia.
- Osaat koodata ja purkaa varint- ja zigzag-muotoja.
- Osaat kirjoittaa purkajan, joka kestää vihamielisen syötteen, ja
  testata sen sumealla testauksella ja sanitoijilla.

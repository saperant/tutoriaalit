# TLM-2.0:n perusteet

Signaalitason väylämalli simuloi jokaisen kellojakson, osoitelinjan ja
kättelysignaalin. Kun prosessori lukee sanan muistista, väylällä vaihtuu
kymmeniä signaaleja ja simulaattori ajaa kymmeniä prosessiherätyksiä.
*Transaktiotason* mallissa sama luku on yksi funktiokutsu, jolle
annetaan komento, osoite ja puskuri. Ero simulointinopeudessa on
kertaluokkia, ja juuri se tekee virtuaaliprototyypeistä käyttökelpoisia.

TLM-2.0 standardoi, miltä tämä funktiokutsu näyttää. Standardin ansiosta
eri toimittajien ja tiimien mallit voi kytkeä toisiinsa: prosessorimalli
yhdeltä, väylämalli toiselta ja oma oheislaite kolmannelta.

## Käsitteet

| Käsite | Merkitys |
|--------|----------|
| aloittaja (*initiator*) | lähettää transaktioita, esim. prosessori tai DMA |
| kohde (*target*) | vastaa transaktioihin, esim. muisti tai oheislaite |
| välittäjä (*interconnect*) | kulkee välissä, esim. väylä tai silta |
| socket | aloittajan tai kohteen liitäntä; sisältää portin ja exportin |
| eteenpäin (*forward path*) | kutsut aloittajalta kohteelle |
| taaksepäin (*backward path*) | kutsut kohteelta aloittajalle |
| *generic payload* | standardoitu transaktio-olio |
| *base protocol* | säännöt, joita generic payload ja vaiheet noudattavat |

```{.dot otsikko="Aloittaja, välittäjä ja kohde socketeineen. Yhtenäinen nuoli on eteenpäin kulkeva polku, jota pitkin b_transport-kutsu etenee ja palaa; katkoviiva on taaksepäin kulkeva polku, jota kohde käyttää AT-tyylin vaiheisiin ja DMI:n mitätöintiin."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.7;
  node [shape=box, height=0.4];
  a [label="aloittaja\n(prosessori)"];
  v [label="välittäjä\n(väylä)"];
  k [label="kohde\n(muisti)"];
  a -> v [label="b_transport(payload, viive)"];
  v -> k [label="osoite muunnettu,\nviive + väylän viive"];
  k -> v [style=dashed, constraint=false];
  v -> a [style=dashed, constraint=false];
}
```

Kutsu on tavallinen C++-funktiokutsu, joka kulkee ketjun läpi ja palaa
samaa reittiä. Jokainen lohko lisää viiveargumenttiin oman osuutensa, ja
vasta aloittaja päättää, milloin kertynyt viive odotetaan. Rajapinnat
ovat:

| Rajapinta | Suunta | Tarkoitus |
|------------------------------------|------------|------------------------------------|
| `b_transport` | eteenpäin | estävä siirto, LT-tyyli (tämä luku) |
| `nb_transport_fw`, `nb_transport_bw` | molemmat | estämätön siirto vaiheittain, AT-tyyli (luku 10) |
| `get_direct_mem_ptr` | eteenpäin | suora muistiosoitin, DMI (luku 9) |
| `invalidate_direct_mem_ptr` | taaksepäin | DMI-osoittimen mitätöinti |
| `transport_dbg` | eteenpäin | debug-luku ja -kirjoitus ilman aikaa (luku 8) |

## Generic payload

Transaktio on olio `tlm::tlm_generic_payload`. Aloittaja täyttää sen,
kohde lukee ja kirjoittaa sen kenttiä ja asettaa vastauksen tilan.

| Kenttä | Asettaa | Merkitys |
|----------------------|------------------------|----------------------------------------------|
| komento | aloittaja | `TLM_READ_COMMAND`, `TLM_WRITE_COMMAND` tai `TLM_IGNORE_COMMAND` |
| osoite | aloittaja (väylä muuttaa) | ensimmäisen tavun osoite |
| dataosoitin ja pituus | aloittaja | puskuri, josta kirjoitetaan tai johon luetaan |
| tavumaski | aloittaja | valinnainen: mitkä tavut siirretään |
| suoratoistoleveys | aloittaja | toistuvan osoitteen siirto (FIFO-rekisteri) |
| DMI-vihje | kohde | suora pääsy olisi mahdollinen |
| vastauksen tila | aloittaja alustaa, kohde asettaa | `TLM_OK_RESPONSE` tai virhe |
| laajennukset | kuka tahansa | omat lisätiedot, esim. suojaus tai prioriteetti |

Data on tavupuskuri, ja sen tavujärjestys on isäntäkoneen järjestys:
x86-64:llä ja ARM:lla pieni. Malli, joka simuloi isoa tavujärjestystä
käyttävää laitetta, kääntää tavut itse. Generic payload ei omista
puskuria; aloittaja vastaa siitä, että puskuri on olemassa niin kauan
kuin transaktio on kesken.

## Aloittaja

Aloittajan socket `simple_initiator_socket` on apuluokka (*convenience
socket*) kirjastosta `tlm_utils`. Aloittaja luo payloadin, täyttää sen ja
kutsuu socketin kautta kohteen `b_transport`-funktiota:

```{.cpp tiedosto="esimerkit/09-tlm-muisti/main.cpp" osa="aloittaja"}
```

Vastauksen tila alustetaan arvoon `TLM_INCOMPLETE_RESPONSE`; base
protocol vaatii sen, ja jos kohde jättää tilan asettamatta, aloittaja
huomaa sen. Tavumaski on tässä valinnainen parametri, jotta virheen voi
näyttää.

`b_transport`in toinen argumentti on *ajan annotointi*: viive, jonka
kohde lisää kertoakseen, kauanko siirto kesti. Kohde ei odota itse, vaan
kertoo viiveen aloittajalle, joka odottaa sen `wait(viive)`-kutsulla.
Tämä on tärkein yksittäinen ero signaalitason malliin: aika ei kulu
siellä, missä työ tehdään, vaan siellä, missä aloittaja päättää
synkronoida. Luku 9 käyttää tätä hyväksi ja synkronoi vain harvoin.

## Kohde

Muistimalli on hakemistossa `mallit`, koska myöhemmät luvut käyttävät
sitä. Socketille rekisteröidään toteutukset, jotka socket kutsuu:

```{.cpp tiedosto="esimerkit/mallit/muisti.hpp" osa="muisti"}
```

Kohde tarkistaa ensin, pystyykö se palvelemaan pyynnön, ja kertoo muussa
tapauksessa syyn vastauksen tilassa:

```{.cpp tiedosto="esimerkit/mallit/muisti.hpp" osa="tarkistus"}
```

```{.cpp tiedosto="esimerkit/mallit/muisti.hpp" osa="b_transport"}
```

Lukuviive on 20 ns ja kirjoitusviive 30 ns. Viive lisätään annotointiin
(`+=`), ei sijoiteta: aloittajalla voi jo olla kertynyttä paikallista
aikaa, ja väylä on voinut lisätä omansa. `set_dmi_allowed(true)` on vihje,
jota käsitellään luvussa 9.

## Ajo

```{.cpp tiedosto="esimerkit/09-tlm-muisti/main.cpp" osa="testi"}
```

Pääohjelma luo 4 kt:n muistin (lukuviive 20 ns, kirjoitusviive 30 ns) ja
kytkee aloittajan socketin suoraan muistin sockettiin:
`aloittaja.socket.bind(muisti.socket)`.

```{.tuloste tiedosto="esimerkit/09-tlm-muisti/odotettu"}
```

Jokainen transaktio näkyy simulaatioajassa, joka kulkee kohteen
ilmoittamien viiveiden mukaan: kolme kirjoitusta à 30 ns ja kolme lukua
à 20 ns. Osoite 0x1000 on muistin ulkopuolella, ja kohde vastaa
osoitevirheellä; aloittaja päättää, mitä virheelle tehdään. Tavumaskia
tämä muisti ei tue, ja se vastaa sen mukaisella virheellä.
`TLM_INCOMPLETE_RESPONSE` ei saa koskaan jäädä voimaan: se tarkoittaisi,
ettei kukaan käsitellyt pyyntöä.

## Vastauksen tilat

| Tila | Tarkoitus |
|------|-----------|
| `TLM_OK_RESPONSE` | onnistui |
| `TLM_INCOMPLETE_RESPONSE` | ei käsitelty (aloittajan alkuarvo) |
| `TLM_ADDRESS_ERROR_RESPONSE` | osoite ei kuulu kohteelle |
| `TLM_COMMAND_ERROR_RESPONSE` | komento ei ole sallittu, esim. kirjoitus vain luettavaan |
| `TLM_BURST_ERROR_RESPONSE` | pituus tai suoratoistoleveys ei ole tuettu |
| `TLM_BYTE_ENABLE_ERROR_RESPONSE` | tavumaskia ei tueta |
| `TLM_GENERIC_ERROR_RESPONSE` | muu virhe |

Oikean väylän virhevastaukset, kuten AXI:n `SLVERR` ja `DECERR`,
vastaavat näitä tiloja, ja prosessorimalli voi muuttaa ne
poikkeukseksi (*bus fault*) samoin kuin oikea prosessori.

## Käytännössä

- **Kohde ei odota `b_transport`issa.** Viive annotoidaan, ja kohde
  palaa heti. Silloin kohdetta voi kutsua myös ajallisesti irrotetusta
  aloittajasta ja debug-kutsusta. `wait()` kohteessa on sallittu, mutta
  vain jos kohteen on pakko synkronoida, ja se hidastaa mallia.
- **Tarkista kaikki kentät.** Base protocol vaatii, että kohde joko
  tukee kentän tai vastaa virheellä. Hiljaa ohitettu tavumaski tai
  liian pitkä pituus muuttuu ohjelmistotestissä selittämättömäksi
  muistin sotkemiseksi.
- **Payloadin elinikä.** LT-tyylissä payload voi olla aloittajan pinossa,
  koska `b_transport` palaa vasta, kun siirto on valmis. Pitkäikäisiä
  transaktioita varten on muistinhallinta (luku 10).
- **Laajennukset harkiten.** Generic payloadin laajennuksilla
  (`tlm_extension`) voi välittää esimerkiksi suojaustason tai
  välimuistiattribuutit. Jokainen laajennus heikentää yhteensopivuutta
  muiden mallien kanssa, joten valmiiden kenttien käyttö on parempi aina
  kun mahdollista.

## Itsearviointi

- Osaat täyttää generic payloadin luku- ja kirjoitustransaktiota varten
  ja kutsua `b_transport`ia aloittajan socketin kautta.
- Osaat toteuttaa kohteen, joka tarkistaa pyynnön, siirtää datan,
  annotoi viiveen ja asettaa vastauksen tilan.
- Osaat selittää ajan annotoinnin: kuka lisää viiveen ja kuka odottaa
  sen.
- Osaat valita oikean virhetilan osoite-, komento- ja tavumaskivirheelle.

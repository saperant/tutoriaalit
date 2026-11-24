# AT-mallinnus: vaiheet ja liukuhihna

LT-tyylissä transaktiolla on kaksi ajanhetkeä: alku ja loppu. Oikea
väylä on monimutkaisempi. AXI-väylällä aloittaja voi lähettää uuden
pyynnön ennen kuin edellinen on valmis, kohde voi hyväksyä pyynnön
nopeasti mutta vastata hitaasti, ja vastaukset voivat palata eri
järjestyksessä. Väylän suorituskyky riippuu juuri tästä
*liukuhihnoituksesta* (*pipelining*). *Likimäärin ajoitettu*
(*approximately timed*, AT) tyyli mallintaa sen jakamalla transaktion
vaiheisiin, jotka ilmoitetaan estämättömillä kutsuilla
`nb_transport_fw` ja `nb_transport_bw`.

## Neljä vaihetta

TLM-2.0:n base protocol määrittelee neljä ajoituspistettä:

| Vaihe | Suunta | Merkitys |
|--------------|--------------------|--------------------------------------------------|
| `BEGIN_REQ` | aloittaja → kohde | pyyntö alkaa |
| `END_REQ` | kohde → aloittaja | kohde hyväksyi pyynnön; aloittaja saa lähettää seuraavan |
| `BEGIN_RESP` | kohde → aloittaja | vastaus alkaa |
| `END_RESP` | aloittaja → kohde | aloittaja hyväksyi vastauksen; kohde saa lähettää seuraavan |

Kaksi *poissulkemissääntöä* tekevät vaiheista väylän kaltaisen: samaan
suuntaan voi olla kesken vain yksi pyyntö (`BEGIN_REQ` ennen edellisen
`END_REQ`:ia on kielletty) ja yksi vastaus. Pyyntöjä voi kuitenkin olla
*käsittelyssä* monta yhtä aikaa: kohde hyväksyy pyynnön ja jatkaa sen
käsittelyä samalla, kun aloittaja lähettää seuraavan.

Estämättömän kutsun paluuarvo kertoo, miten vastaanottaja käsitteli
vaiheen:

| Paluuarvo | Merkitys |
|------------------|--------------------------------------------------------------|
| `TLM_ACCEPTED` | vastaanotettu; seuraava vaihe tulee myöhemmin vastakkaiseen suuntaan |
| `TLM_UPDATED` | vastaanottaja siirsi vaiheen eteenpäin samassa kutsussa (vaihe- ja viiveargumentti muuttuivat) |
| `TLM_COMPLETED` | koko transaktio valmis heti; jäljellä olevat vaiheet ohitetaan |

Tämän luvun esimerkki käyttää vain `TLM_ACCEPTED`-paluuarvoa: jokainen
vaihe lähetetään omana kutsunaan. Muut paluuarvot ovat optimointeja,
jotka säästävät kutsuja, ja vastaanottajan on silti ymmärrettävä ne.

## Muistinhallinta

AT-transaktio elää usean kutsun yli, joten payload ei voi olla
aloittajan pinossa. Generic payload tukee viitelaskentaa:
`acquire()` kasvattaa laskuria, `release()` pienentää sitä, ja kun laskuri
menee nollaan, payload palautetaan muistinhallinnalle (`tlm_mm_interface`):

```{.cpp tiedosto="esimerkit/13-at/muistinhallinta.hpp" osa="mm"}
```

Pooli kierrättää payloadit, joten tuhansien transaktioiden mallissa
muistia varataan vain kerran.

## Kohde

Kohde hyväksyy pyynnön 10 ns:ssa ja vastaa 50 ns pyynnön alun jälkeen.
Se käyttää *PEQ*:ta (*payload event queue*), joka ajastaa vaiheen
käsittelyn oikealle hetkelle: estämätön kutsu palaa heti, ja PEQ kutsuu
takaisinkutsufunktiota, kun vaiheen aika koittaa.

```{.cpp tiedosto="esimerkit/13-at/main.cpp" osa="kohde"}
```

PEQ:n avulla kohde ajastaa myös oman sisäisen tapahtumansa: vaihe
`VALMIS` (tässä vapaana oleva `UNINITIALIZED_PHASE`) tarkoittaa, että
käsittely on valmis ja vastaus voidaan lähettää. Jos edellinen vastaus
odottaa vielä kuittausta, valmis transaktio jonotetaan.

## Aloittaja

AT-aloittaja lähettää uuden pyynnön heti, kun edellinen on hyväksytty:

```{.cpp tiedosto="esimerkit/13-at/main.cpp" osa="at"}
```

Vertailuksi toinen aloittaja tekee saman työn `b_transport`illa kuten
luvun 7 aloittaja: neljä kirjoitusta peräkkäin, ja jokaisen jälkeen
`wait(viive)`. Se kytketään toiseen samanlaiseen kohteeseen. Kohteeseen ei tarvitse tehdä mitään LT-aloittajaa varten:
`simple_target_socket` muuntaa `b_transport`-kutsun automaattisesti
vaiheiksi, jos kohde on rekisteröinyt vain `nb_transport_fw`:n, ja
päinvastoin. Muunnos on kätevä, mutta se lisää säikeen ja
kontekstinvaihtoja, joten se on kytkentäapu eikä nopea polku.

```{.cpp tiedosto="esimerkit/13-at/main.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/13-at/odotettu"}
```

Tuloste on vastaanottajan näkökulmasta: jokainen rivi on hetki, jolloin
vastaanottaja käsitteli vaiheen. Pyynnöt menevät liukuhihnaan 10 ns:n
välein, ja vastaukset palaavat samassa tahdissa 50 ns:n viiveellä.
Neljä kirjoitusta valmistuu 80 ns:ssa. LT-aloittaja odottaa jokaisen
vastauksen ennen seuraavaa pyyntöä, joten sama työ vie 4 × 50 = 200 ns.
Ero on sama, joka erottaa liukuhihnoitetun väylän yksinkertaisesta,
ja juuri tämän eron mittaamiseen AT-malleja tarvitaan.

## Milloin AT

| Kysymys | Tyyli |
|------------------------------------------------------------|----------|
| toimiiko ajuri, käynnistyykö käyttöjärjestelmä | LT |
| riittääkö väylän kaistanleveys, mikä on viive kuormassa | AT |
| montako pyyntöä kohteen on pystyttävä ottamaan vastaan | AT |
| mitkä ovat arbitroinnin ja prioriteettien vaikutukset | AT |
| onko mallin kokonaisnopeus tärkein | LT |

AT-malli on hitaampi kuin LT, koska jokainen vaihe on oma tapahtumansa
ja ajallinen irrottaminen ei ole mahdollista. Siksi käytännön
järjestelmämalleissa sekoitetaan tyylejä: prosessori ja suurin osa
oheislaitteista ovat LT-malleja, ja tutkittava osajärjestelmä, kuten
muistiohjain tai väylä, on AT-malli. Kohteet, jotka tukevat molempia
liitäntöjä, ovat tähän tarkoitukseen arvokkaimpia.

## Käytännössä

- **PEQ vaiheiden ajoitukseen.** Estämätön kutsu ei saa odottaa, joten
  vaihe, jolla on viive, ajastetaan PEQ:hun. `peq_with_cb_and_phase`
  kutsuu takaisinkutsua oikealla hetkellä ja oikeassa järjestyksessä.
- **Poissulkemissäännöt näkyviin.** Aloittaja odottaa `END_REQ`:ia
  ennen seuraavaa pyyntöä, ja kohde odottaa `END_RESP`:iä ennen
  seuraavaa vastausta. Väärin toteutettu sääntö on yleisin AT-mallin
  virhe, ja se näkyy liian hyvänä suorituskykynä.
- **Muistinhallinta pakollinen.** AT-transaktio tarvitsee
  muistinhallinnan, ja jokainen osapuoli, joka tallentaa payloadin
  osoittimen, kutsuu `acquire()` ja myöhemmin `release()`.
- **Tarkista protokolla.** Accellera julkaisee *TLM base protocol
  checker* -mallin, joka kytketään aloittajan ja kohteen väliin ja
  raportoi sääntörikkomukset. Se kannattaa pitää mukana jokaisessa
  AT-mallin testissä.
- **AT ei ole syklitarkka.** Vaiheet antavat väylän ajoituksen
  likimäärin: purskeiden sisäiset jaksot ja kättelyn yksityiskohdat
  puuttuvat. Jos niitä tarvitaan, malli on syklitarkka tai RTL.

## Itsearviointi

- Osaat nimetä base protocolin neljä vaihetta ja poissulkemissäännöt.
- Osaat kirjoittaa AT-kohteen, joka hyväksyy pyynnöt, käsittelee niitä
  rinnakkain ja lähettää vastaukset yksi kerrallaan PEQ:n avulla.
- Osaat toteuttaa muistinhallinnan ja käyttää `acquire()`- ja
  `release()`-kutsuja oikein.
- Osaat perustella, milloin AT-tyyli on tarpeen ja milloin LT riittää.

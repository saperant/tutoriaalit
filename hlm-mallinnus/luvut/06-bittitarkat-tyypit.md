# Bittitarkat tietotyypit

C++:n kokonaisluvut ovat 8, 16, 32 tai 64 bittiä, mutta laitteiston
rekisteri voi olla 4, 12 tai 35 bittiä. Algoritmin liukulukumalli kertoo,
toimiiko algoritmi, mutta ei sitä, toimiiko se 16-bittisellä
datapolulla. *Bittitarkka* (*bit-accurate*) malli laskee täsmälleen
samat bitit kuin tuleva laitteisto, ja siksi sitä voi käyttää RTL:n
referenssinä (luku 12). Tämä luku päättää signaalitason osuuden:
tyypit kuuluvat SystemC:n ytimeen kuten kanavatkin, mutta niitä
käytetään seuraavan kerran vasta, kun malli luvussa 12 asetetaan RTL:n
rinnalle. Luvun 5 lopussa esitelty socket jatkuu luvussa 7. SystemC:n
tietotyypit ovat nimiavaruudessa `sc_dt`.

| Tyyppi | Leveys | Arvot | Käyttö |
|------------------------------|--------------|----------------------|------------------------------|
| `sc_int<W>`, `sc_uint<W>` | 1–64 | kokonaisluku | laskurit, osoitteet, datapolut |
| `sc_bigint<W>`, `sc_biguint<W>` | mielivaltainen | kokonaisluku | leveät summaimet, kryptografia |
| `sc_bv<W>` | mielivaltainen | 0, 1 | bittikentät, maskit |
| `sc_lv<W>` | mielivaltainen | 0, 1, X, Z | kolmitilaväylät, alustamaton tila |
| `sc_fixed<W, I, Q, O>` | mielivaltainen | kiinteän pilkun luku | DSP-datapolut |
| `sc_ufixed<W, I, Q, O>` | mielivaltainen | etumerkitön kiinteän pilkun luku | kertoimet, vahvistukset |

`sc_int` ja `sc_uint` on toteutettu 64-bittisellä kokonaisluvulla, joten
ne ovat nopeita. `sc_bigint` ja kiinteän pilkun tyypit ovat moninkertaisesti
hitaampia, koska ne laskevat mielivaltaisella tarkkuudella. Mallissa
käytetään nopeinta tyyppiä, joka on vielä bittitarkka.

## Kokonaisluvut ja bittikentät

```{.cpp tiedosto="esimerkit/07-tyypit/main.cpp" osa="kokonaisluvut"}
```

`sc_uint<4>` kiertää 15:stä nollaan ja `sc_int<8>` 127:stä −128:aan,
kuten laitteistossa. `range(11, 8)` poimii bittikentän ja `[2]` yhden
bitin; molemmat ovat myös sijoitettavissa. Pilkkuoperaattori liittää
arvot yhteen (*concatenation*), kuten Verilogin `{a, b}`: sulkeet ovat
pakolliset, koska muuten C++ tulkitsee pilkun tavallisesti.

Tärkein sudenkuoppa on viimeisenä. Lausekkeen `a + b` välitulos
lasketaan 64-bittisenä, ja leveys määräytyy vasta sijoituksessa:
9-bittinen tulos säilyttää summan 300, 8-bittinen katkaisee sen 44:ään.
Verilogissa sama sääntö on monimutkaisempi, ja ero on yleinen syy
mallin ja RTL:n eroihin.

## Bittivektorit ja neliarvoinen logiikka

```{.cpp tiedosto="esimerkit/07-tyypit/main.cpp" osa="bittivektorit"}
```

`sc_bv` on pelkkiä bittejä, ja bittioperaatiot ja pienennykset
(`or_reduce`, `and_reduce`, `xor_reduce`) toimivat kuten RTL:ssä.
`sc_lv`:n bitit ovat `sc_logic`-arvoja: 0, 1, X (tuntematon) ja Z
(korkeaimpedanssinen). `is_01()` kertoo, onko vektorissa vain
määriteltyjä bittejä, mikä on hyvä tarkistus ennen muunnosta
kokonaisluvuksi.

Usean ajurin väylän arvo *ratkaistaan* bitti kerrallaan: Z väistyy,
samat arvot säilyvät ja eri arvot antavat X:n. Esimerkki tekee
ratkaisun itse; `sc_signal_resolved` tekee saman signaalina.
Pelkkä bittioperaatio ei ole ratkaisu: `01ZZ | ZZ10` antaa `X11X`, koska
`Z | 1` on määritelmän mukaan X, ei 1.

```{.tuloste tiedosto="esimerkit/07-tyypit/odotettu"}
```

## Kiinteä pilkku

Taito *Lukujen esitys ja kiinteän pilkun aritmetiikka* käsittelee Q-muodot, kvantisoinnin
ja ylivuodon; tässä ne kirjoitetaan SystemC:n tyypeillä. `sc_fixed<W, I,
Q, O>` on W-bittinen etumerkillinen luku, jossa I bittiä on
kokonaisosaa (etumerkki mukaan lukien). Q1.15 on siis
`sc_fixed<16, 1>`. Kaksi viimeistä parametria valitsevat, mitä tapahtuu,
kun arvo ei mahdu:

| Tila | Parametri | Toiminta |
|------|-----------|----------|
| kvantisointi | `SC_TRN` (oletus) | katkaisu kohti miinus ääretöntä |
| kvantisointi | `SC_RND` | pyöristys, puolikas kohti plus ääretöntä |
| kvantisointi | `SC_RND_CONV` | pyöristys, puolikas parilliseen |
| ylivuoto | `SC_WRAP` (oletus) | kierto kuten kokonaisluvuissa |
| ylivuoto | `SC_SAT` | saturaatio suurimpaan tai pienimpään |

Kiinteän pilkun tyypit tulevat mukaan vain, jos makro `SC_INCLUDE_FX` on
määritelty ennen ensimmäistä `<systemc>`-otsaketta. Siksi se asetetaan
yleensä käännösvalitsimella `-DSC_INCLUDE_FX`; muuten virheilmoitus
kertoo vain, ettei `sc_fixed` ole tyyppi.

```{.cpp tiedosto="esimerkit/07-tyypit/main.cpp" osa="kiintopiste"}
```

Q1.7:n pienin askel on 2^−7^ = 0,0078125. Tulosteen kiinteän pilkun osa
näyttää eron: 0,3 osuu askelten 38 ja 39 väliin lähemmäs alempaa, joten
molemmat tilat antavat saman tuloksen, mutta −0,3 katkaistaan kohti
miinus ääretöntä eli itseisarvoltaan suuremmaksi. Samoin 0,99 katkeaa
alaspäin mutta pyöristyy suurimpaan arvoon.
1,5 ei mahdu välille [−1, 1): kierto antaa −0,5 ja saturaatio suurimman
arvon 0,9921875. −2,0 kiertää nollaan. Kertolaskun tarkka tulos vaatii
W1 + W2 bittiä ja I1 + I2 kokonaisbittiä, tässä `sc_fixed<16, 2>`.

## Bittitarkka FIR-suodin

Kahdeksan kertoimen FIR-suodin on tyypillinen DSP-lohko, jonka
toteuttaja haluaa tehdä mahdollisimman kapeilla väleillä. Malli
kirjoitetaan niin, että välitulosten tyypit ovat parametreja:

```{.cpp tiedosto="esimerkit/08-fir/fir.hpp" osa="tyypit"}
```

```{.cpp tiedosto="esimerkit/08-fir/fir.hpp" osa="suodin"}
```

Tarkka tulo kahdesta Q1.15-luvusta on Q2.30 eli 32 bittiä. Kahdeksan
tulon summa voi kasvaa enintään kertoimien itseisarvojen summan
verran, tässä 1,28-kertaiseksi, joten kokonaisosaan tarvitaan lisää
*vartijabittejä* (*guard bits*): kolme bittiä riittää kahdeksalle
tulolle (log₂ 8 = 3) kertoimista riippumatta. Ulostulo pyöristetään ja
saturoidaan takaisin Q1.15:een.

Viitteeksi tehdään sama suodin liukuluvuilla (`fir::Viite`) mutta samoilla
kvantisoiduilla kertoimilla, jolloin ero johtuu vain välitulosten
leveyksistä.

Vertailu ajaa jokaisen toteutusvaihtoehdon kahdella signaalilla:
kahden sinin summalla ja *pahimman tapauksen herätteellä*, jonka
etumerkit on valittu niin, että kaikki tulot ovat samanmerkkisiä ja
välisummat kasvavat suurimmiksi:

```{.cpp tiedosto="esimerkit/08-fir/main.cpp" osa="vertailu"}
```

```{.cpp tiedosto="esimerkit/08-fir/main.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/08-fir/odotettu"}
```

Tarkoilla välituloksilla virhe on enintään puoli LSB:tä, mikä on
ulostulon pyöristyksen teoreettinen alaraja. Tulojen katkaisu 18 bittiin
säästää kertojien ja summaimen leveyttä mutta kasvattaa suurimman virheen
lähes seitsenkertaiseksi ja heikentää signaali–kohinasuhdetta 16 dB;
pyöristys samaan leveyteen puolittaa haitan. Summain ilman vartijabittejä
toimii täydellisesti sinisignaalilla mutta kiertää pahimmassa
tapauksessa: virhe on kymmeniätuhansia LSB:itä, eli ulostulo vaihtaa
merkkiään. Juuri tällainen virhe jää huomaamatta, jos testataan vain
tavallisella signaalilla.

## Käytännössä

- **Algoritmi, sitten bittitarkka malli.** Ensin liukulukumalli, joka
  todentaa algoritmin, sitten bittitarkka malli, joka todentaa
  leveydet. Sama koodi tyyppiparametreilla tekee molemmat ja estää
  mallien erkanemisen.
- **Pahin tapaus mitoittaa.** Bittileveydet perustellaan analyysillä
  (vartijabitit, kertoimien itseisarvojen summa) ja todennetaan pahimman
  tapauksen herätteellä. Satunnainen tai tyypillinen signaali löytää
  kvantisointikohinan mutta harvoin ylivuodon.
- **Pyöristystila on määrittely.** Katkaisu, pyöristys ja saturaatio
  ovat toteutuksen ominaisuuksia, jotka kirjataan määrittelyyn
  bittileveyksien kanssa. RTL:n on tehtävä täsmälleen sama, tai malli
  ei ole referenssi.
- **Nopeus.** `sc_fixed` laskee mielivaltaisella tarkkuudella ja on
  hidas. Suurissa simuloinneissa käytetään `sc_fixed_fast`-tyyppiä
  (enintään 53 bitin tarkkuus, toteutettu liukuluvulla) tai lasketaan
  kokonaisluvuilla ja siirroilla, kuten luvun 12 RTL tekee. Myös
  HLS-työkalujen omat tyypit, kuten `ac_fixed` ja `ap_fixed`, ovat
  nopeampia ja syntetisoituvia.

## Itsearviointi

- Osaat valita `sc_int`-, `sc_bigint`-, `sc_bv`-, `sc_lv`- ja
  `sc_fixed`-tyypin välillä tarpeen mukaan.
- Osaat poimia ja kirjoittaa bittikenttiä ja liittää arvoja yhteen, ja
  tiedät, missä vaiheessa lausekkeen tulos katkaistaan.
- Osaat määritellä Q-muodon `sc_fixed`-tyyppinä ja valita kvantisointi-
  ja ylivuototilan.
- Osaat mitoittaa summaimen vartijabitit ja todentaa mitoituksen
  bittitarkalla mallilla ja pahimman tapauksen herätteellä.

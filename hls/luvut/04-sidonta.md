# Sidonta ja ohjaus

Ajoituksen jälkeen jokaisella operaatiolla on jakso, mutta piiriä ei
vielä ole. *Sidonta* (*binding*) päättää, mikä laitteistoyksikkö laskee
kunkin operaation ja mikä rekisteri säilyttää kunkin välituloksen.
*Ohjauksen tuottaminen* tekee tilakoneen, joka kertoo datapolulle,
millä jaksolla ollaan. Tulos on *FSMD* (*finite state machine with
datapath*): sama tilakoneen ja datapolun jako, jonka taito
*RTL-suunnittelu* opetti kirjoittamaan käsin.

## Yksiköiden jakaminen

Kaksi operaatiota voi käyttää samaa yksikköä, jos ne ovat eri jaksoilla.
Jakaminen säästää yksiköitä mutta lisää jokaisen yksikön eteen
multiplekserin, joka valitsee jakson mukaan oikeat operandit.
Kannattavuus riippuu yksikön koosta:

| Yksikkö | Koko (32 bittiä) | Jaetaanko |
|------------------------|------------------------------|------------------------|
| kertoja | 3–4 DSP-lohkoa tai yli 1 000 LUTia | yleensä |
| yhteen- tai vähennyslasku | noin 32 LUTia ja kantoketju | harvoin, mux on yhtä suuri |
| vertailu | noin 11–32 LUTia | ei |
| bittioperaatio, siirto vakiolla | johdotusta tai muutama LUT | ei koskaan |
| muistiportti | rajallinen määrä | aina, portteja ei voi lisätä |

minihls jakaa kertojat aina, kun se on mahdollista, ja jättää muut
yksiköt jakamatta. Kertolaskut käydään läpi jaksojärjestyksessä, ja
kukin sidotaan ensimmäiseen kertojaan, joka on sillä jaksolla vapaa:

```{.python tiedosto="esimerkit/minihls/sidonta.py" osa="yksikot"}
```

Eri alueet suoritetaan peräkkäin, joten saman kertojan voivat jakaa
myös eri silmukat. Liukuhihnoitetussa silmukassa (luku 6) jakso
lasketaan modulo aloitusväli, koska samalla jaksolla on käynnissä
useita kierroksia.

## Resurssien rajoittaminen

Ilman rajoja listaajoitus sijoittaa operaatiot niin aikaisin kuin
riippuvuudet sallivat, ja yksiköitä tulee niin monta kuin samalle
jaksolle osuu. Pragma `allocation` rajoittaa yksiköiden määrää:

```{.cpp tiedosto="esimerkit/04-jakaminen/diffeq_1.cpp" osa="pragma"}
```

Ajoitus noudattaa rajaa, ja kuusi kertolaskua jaetaan kuudelle
jaksolle. Yosys kertoo tuotetun RTL:n rakenteen karkealla tasolla
(`proc; opt; wreduce`), ennen kuin se on muutettu minkään piirin
soluiksi:

```{.tuloste tiedosto="esimerkit/04-jakaminen/odotettu"}
```

Kertojia on yksi kolmen sijaan, mutta kierros vie kuusi jaksoa ja
multiplekserien ja kiikkujen bitit kasvoivat. Kertojan eteen tuli
kuuden syötteen multiplekseri molemmille operandeille:

```{.verilog tiedosto="esimerkit/04-jakaminen/diffeq_1.v" osa="kertoja"}
```

Lisäksi välitulosten on odotettava kertojaa rekistereissä (`t6_v0`,
`t7_v0` jne.), joten kiikkuja tarvitaan enemmän. Jakaminen kannatti,
koska kaksi 32-bittistä kertojaa on paljon suurempi kuin noin 70 bittiä
lisää multipleksereitä ja 33 kiikkua. Pienillä yksiköillä tulos olisi
päinvastainen.

## Rekisterit

Arvo tarvitsee rekisterin, jos sitä käytetään myöhemmällä jaksolla kuin
sillä, jolla se valmistuu. Arvon *elinaika* ulottuu valmistumisesta
viimeiseen käyttöön. minihls antaa jokaiselle tällaiselle arvolle oman
rekisterin kullekin liukuhihnan vaiheelle, jonka yli arvo elää:

```{.python tiedosto="esimerkit/minihls/sidonta.py" osa="rekisterit"}
```

Liukuhihnattomassa silmukassa vaiheita on yksi, joten jokainen
myöhemmin tarvittava arvo saa yhden rekisterin (`t6_v0`). Oikeat
työkalut jakavat rekisterejäkin: arvot, joiden elinajat eivät
leikkaa, voivat käyttää samaa rekisteriä. Klassinen menetelmä on
*left-edge*-algoritmi, joka lajittelee elinajat alkujakson mukaan ja
täyttää rekisterit ahneesti, tai elinaikojen leikkausgraafin
värittäminen, kuten ohjelmistokääntäjän rekisterinvarauksessa.
Muuttujat, jotka elävät alueesta toiseen tai silmukan kierroksesta
seuraavaan, saavat aina oman rekisterin (`m_s`).

## Tuotettu Verilog

Luvun 1 pistetulosta tuotettu Verilog on kokonaisuudessaan noin sata
riviä. Moduulin portit noudattavat Vitis HLS:n nimeämistä, joka
esitellään luvussa 9:

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="portit"}
```

Tilakoneessa on tila jokaiselle alueelle sekä lepo- ja lopetustila.
Silmukan alueella on laskuri `l2_n` kierroksille ja `l2_ks` jaksolle
kierroksen sisällä. *Aktiivisuussignaali* `l2_j1` on tosi, kun ollaan
silmukan jaksolla 1; datapolun rekisterit ja muistiportit ohjataan
näillä signaaleilla:

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="tilakone"}
```

Datapolun operaatiot ovat jatkuvia johtoja, jotka laskevat koko ajan.
Laskun tuloksella on merkitystä vain sillä jaksolla, jolle operaatio on
ajoitettu, ja vain silloin tulos kirjoitetaan rekisteriin:

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="datapolku"}
```

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="kytkennat"}
```

Kierroksen laskuri on samalla osoite: `t2` on silmukkamuuttuja `i`, ja
muistit lukevat sen osoittaman alkion jaksolla 0. Synkroninen muisti
antaa datan seuraavalla jaksolla (`a_q0`), jolloin kertolasku ja
yhteenlasku ketjutetaan ja summa kirjoitetaan rekisteriin `m_s`.

Tilakone siirtyy alueesta toiseen. Silmukan tilassa kierros päättyy
jaksolla 1, ja viimeisen kierroksen jälkeen siirrytään palauttamaan
tulos:

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="ohjaus"}
```

Rekisterit päivittyvät aktiivisuussignaalien mukaan:

```{.verilog tiedosto="esimerkit/01-mac/mac.v" osa="paivitykset"}
```

Jokainen rivi vastaa raportin ajoitusta: `m_s` alustetaan lohkossa 1,
päivitetään silmukan jaksolla 1 ja luetaan lohkossa 3 paluuarvoksi.
Tuotettu koodi on tarkoituksella luettavaa. Oikeiden työkalujen RTL on
paljon pidempää, ja sen nimet ovat työkalun omia (`ap_CS_fsm_state3`,
`mul_ln12_fu_142_p2`), joten raportin ja RTL:n yhdistäminen vaatii
työkalun omia ristiviitteitä.

## Tilakoneen koodaus

minihls numeroi tilat binäärisesti. Vitis HLS käyttää oletuksena
*one-hot*-koodausta, jossa jokaisella tilalla on oma kiikkunsa: tilan
tunnistaminen on silloin yksi bitti, mikä nopeuttaa datapolun
ohjausta, mutta kiikkuja tarvitaan yhtä monta kuin tiloja. Suurissa
ytimissä tiloja on satoja, ja koodauksen valinta näkyy sekä pinta-alassa
että ajoituksessa.

## Käytännössä

- **Rajoita suuria yksiköitä, älä pieniä.** `allocation` kannattaa
  kertojille, jakajille ja liukulukuyksiköille, harvoin summaimille.
- **Jakaminen lisää latenssia ja multipleksereitä.** Mittaa molemmat;
  raportin pinta-ala-arvio on karkea, Yosysin tai toteutuksen luvut
  tarkempia.
- **Multiplekseri on kriittisellä polulla.** Jaetun yksikön eteen tuleva
  monisyötteinen multiplekseri lisää viivettä, jota HLS-raportti ei
  aina arvioi oikein.
- **Lue tuotettua RTL:ää.** Kun raportti yllättää, RTL:stä näkee, mihin
  rekisterit ja multiplekserit tulivat.

## Itsearviointi

- Osaat selittää, milloin kaksi operaatiota voi jakaa yksikön ja mitä
  jakaminen maksaa.
- Osaat rajoittaa kertojien määrää `allocation`-pragmalla ja arvioida
  vaikutuksen latenssiin ja resursseihin.
- Osaat määrittää arvon elinajan ajoituksesta ja kertoa, milloin arvo
  tarvitsee rekisterin.
- Osaat lukea tuotetusta Verilogista tilakoneen, aktiivisuussignaalit ja
  datapolun ja yhdistää ne raportin ajoitukseen.

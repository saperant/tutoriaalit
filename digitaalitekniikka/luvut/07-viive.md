# Viive ja hasardit

Totuustaulu kertoo, mihin piiri asettuu. Se ei kerro, mitä piiri tekee
matkalla. Kun tulo muuttuu, muutos etenee porttien läpi eri polkuja
pitkin eri nopeudella, ja lähtö voi käydä väärässä arvossa ennen kuin
asettuu oikeaan. Tässä luvussa rakennetaan simulaattori, joka näyttää
tämän.

## Tapahtumapohjainen simulointi

Laitteistosimulaattorit (myös SystemVerilog- ja VHDL-simulaattorit)
ovat tapahtumapohjaisia. Simulaattori pitää jonoa tulevista
tapahtumista "signaali s saa arvon v hetkellä t". Kun signaali
muuttuu, jokaisen sitä lukevan portin lähtö lasketaan uudelleen, ja
uusi arvo ajastetaan portin viiveen päähän. Signaaleja, jotka eivät
muutu, ei lasketa ollenkaan, mikä tekee menetelmästä tehokkaan.

```{.python tiedosto="esimerkit/porttisim.py" osa="portit"}
```

```{.python tiedosto="esimerkit/porttisim.py" osa="piiri"}
```

Simulaattori käyttää *kuljetusviivettä*: jokainen muutos etenee, myös
lyhyt piikki. Todellinen portti ei välitä hyvin lyhyitä pulsseja
(*inertiaalinen viive*), ja SystemVerilogin `#`-viive käyttäytyy
oletuksena niin. Opetuksessa kuljetusviive on parempi, koska se
näyttää jokaisen välitilan.

Aaltomuoto tulostetaan tekstinä, yksi merkki aikayksikköä kohden:

```{.python tiedosto="esimerkit/porttisim.py" osa="aaltomuoto"}
```

Johdannon invertteriketju (luku 1) on tämän simulaattorin ensimmäinen
esimerkki, ja luvun 6 summaimien viiveet mitattiin sillä.

## Hasardi

Kahden syötteen multiplekseri $y = a\bar{s} + bs$ on oikein
totuustaulun mukaan. Kun $a = b = 1$, lähdön pitäisi olla 1 riippumatta
valinnasta $s$. Mutta $\bar{s}$ tulee invertterin kautta, joten kun $s$
putoaa nollaan, termi $bs$ sammuu ennen kuin $a\bar{s}$ syttyy:

```{.python tiedosto="esimerkit/07-hasardi.py" osa="mux"}
```

```{.python tiedosto="esimerkit/07-hasardi.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/07-hasardi.odotettu"}
```

Lähtöön syntyy kahden aikayksikön nollapiikki (*glitch*). Alla oleva
kuva näyttää saman aaltomuotona: invertterin viiveen ajan kumpikin
tulotermi on nolla. Alin rivi on konsensustermillä korjattu lähtö.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/07-hasardi.json" otsikko="Staattinen 1-hasardi multiplekserissä (yksi ruutu on yksi aikayksikkö)"}
```

Tämä on *staattinen 1-hasardi*: lähdön pitäisi pysyä ykkösenä, mutta se käy
nollassa. Hasardi korjataan lisäämällä konsensustermi $ab$, joka on
looginen seuraus kahdesta muusta (luku 4) mutta pitää lähdön ylhäällä
siirtymän ajan. Turha termi Boolen algebran kannalta on tarpeellinen
ajan kannalta.

Hasardeja on muitakin. *Staattinen 0-hasardi* on ykköspiikki
lähdössä, jonka pitäisi pysyä nollana. *Dynaaminen hasardi* syntyy,
kun lähdön pitäisi vaihtua kerran mutta se vaihtuu kolmesti.
Summaimen summabitit käyvät läpi monta väärää arvoa, kun muistibitti
etenee: luvun 6 mittaus laski hetken, jolloin viimeinen niistä
loppui.

## Miksi hasardit eivät yleensä haittaa

Synkronisessa suunnittelussa (luku 9) kombinaatiologiikan lähtö luetaan
vain kellon reunalla, ja kellojakso valitaan niin pitkäksi, että
kaikki piikit ovat ohi ennen reunaa. Hasardit eivät silloin näy.
Siksi nykyaikainen suunnittelu ei poista niitä logiikasta, vaan
huolehtii ajoituksesta (luku 11).

Hasardit haittaavat kolmessa tilanteessa:

- kun kombinaatiologiikan lähtöä käytetään **kellona** tai
  **asynkronisena nollauksena**: piikki näyttää ylimääräiseltä
  kellonreunalta tai nollaukselta
- kun lähtö menee **piirin ulkopuolelle** ilman rekisteriä,
  esimerkiksi toisen laitteen kellotuloon tai keskeytyslinjaan
- **tehonkulutuksessa**: jokainen piikki varaa ja purkaa kapasitanssia
  (luku 3).

## Kombinatorinen silmukka

Jos kombinaatiologiikan lähtö kytketään takaisin sen tuloon, piirillä
voi olla muistia (salpa, luku 8) tai se voi värähdellä. Pariton
määrä inverttereitä renkaana ei voi asettua:

```{.python tiedosto="esimerkit/07-rengas.kaatuu.py" osa="rengas"}
```

```{.tuloste tiedosto="esimerkit/07-rengas.virhe"}
```

Tällainen *rengasoskillaattori* on hyödyllinen mittalaite: sen taajuus
kertoo porttiviiveen, ja piirivalmistajat käyttävät sitä prosessin
laadun mittaamiseen. Tahattomana se on virhe. Lint-työkalut ja
synteesi varoittavat kombinatorisista silmukoista, ja Verilator
kieltäytyy simuloimasta niitä tehokkaasti (varoitus `UNOPTFLAT`).

## Käytännössä

- **Älä käytä kombinaatiologiikan lähtöä kellona.** Kellotettu
  signaali tulee kiikusta tai kellogeneraattorista. Jos kelloa pitää
  hallita, käytetään valmistajan kellonportitussolua, joka on
  suunniteltu hasardittomaksi.
- **Rekisteröi ulospäin lähtevät signaalit.** Piirin ulkopuolelle
  menevä signaali otetaan kiikusta, jolloin siinä ei ole piikkejä.
- **Kuljetus- vai inertiaalinen viive.** Kun simulaattori näyttää
  piikin, kysy, onko se fyysinen vai simulointimallin tuote.
  Porttitason simulointi ajoitustiedoilla (SDF) on tarkempi kuin
  RTL-simulointi, jossa viiveitä ei ole lainkaan.
- **Silmukka on virhe, ellei se ole tarkoituksellinen.** Ainoat
  tarkoitukselliset kombinatoriset silmukat ovat salpoja ja
  oskillaattoreita, ja niitä ei kirjoiteta tavalliseen RTL-koodiin.

## Itsearviointi

- Osaat selittää tapahtumapohjaisen simuloinnin periaatteen ja kuljetus-
  ja inertiaalisen viiveen eron.
- Osaat tunnistaa staattisen 1-hasardin kahden polun piiristä ja
  korjata sen konsensustermillä.
- Osaat kertoa, miksi hasardit eivät haittaa synkronisessa
  suunnittelussa ja milloin ne haittaavat.
- Osaat selittää, mitä kombinatorinen silmukka tekee ja miksi pariton
  invertterirengas värähtelee.

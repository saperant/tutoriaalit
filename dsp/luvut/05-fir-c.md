# FIR-suodin C:llä

Suunniteltu suodin on taulukko lukuja. Tässä luvussa siitä tehdään C:llä
suodin, joka käsittelee signaalia lohko kerrallaan, säilyttää tilansa
lohkojen välillä eikä varaa muistia. Lopuksi C-toteutus käännetään
jaetuksi kirjastoksi ja sitä verrataan SciPyyn Pythonista.

## Kertoimet Pythonista C:hen

Kertoimet tuotetaan suunnitteluskriptillä C-otsakkeeksi. Generoitu
tiedosto on versionhallinnassa, ja testi varmistaa, että se vastaa
generaattorin nykyistä tulostetta. Näin kukaan ei muokkaa kertoimia
käsin, eikä vanhentunut otsake jää huomaamatta.

```{.python tiedosto="esimerkit/05-kertoimet.py" osa="generoi"}
```

```{.c tiedosto="esimerkit/05-fir/kertoimet.h"}
```

Kaksitoista merkitsevää numeroa riittää. Pyöristysvirhe on noin
$10^{-12}$ eli 240 dB signaalin alapuolella, mikä on kaukana kaikista
käytännön vaatimuksista. Pienempi tarkkuus myös suojaa koneiden
välisiltä eroilta: SciPyn sini- ja Bessel-funktioiden viimeinen bitti
voi vaihdella prosessorin mukaan, ja täysi 17 numeron tarkkuus tekisi
otsakkeesta koneriippuvaisen.

## Tila ja rengaspuskuri

FIR-suodin tarvitsee $N - 1$ edellistä syötettä. Kun signaali tulee
lohkoina, näiden näytteiden on säilyttävä lohkosta toiseen. Tila
kuuluu suodinolioon, ei funktion paikallisiin muuttujiin, ja muisti
tulee kutsujalta. Reaaliaikakoodi ei varaa muistia ajon aikana, ja
kutsuja voi sijoittaa puskurin staattiseen muistiin, pinoon tai
nopeaan sisäiseen RAM-muistiin.

```{.c tiedosto="esimerkit/05-fir/fir.h" osa="rakenne"}
```

Viivelinja on **rengaspuskuri**: uusi näyte kirjoitetaan vanhimman
paikalle, ja indeksi kiertää. Tavallisessa renkaassa jokainen
indeksointi tarvitsee jakojäännöksen tai ehtolauseen. Tässä käytetään
**kaksoiskirjoitusta**: puskurissa on $2N$ paikkaa, ja jokainen näyte
kirjoitetaan kahteen kohtaan. Silloin viimeiset $N$ näytettä ovat aina
peräkkäin muistissa, ja sisäsilmukka on tavallinen pistetulo, jonka
kääntäjä osaa vektoroida.

```{.c tiedosto="esimerkit/05-fir/fir.c" osa="tyonna"}
```

```{.c tiedosto="esimerkit/05-fir/fir.c" osa="kasittele"}
```

Hinta on kaksinkertainen muisti viivelinjalle ja yksi ylimääräinen
kirjoitus näytettä kohti. Vaihtoehtoja ovat kahden potenssin pituinen
rengas, jonka indeksi lasketaan bittimaskilla, ja DSP-prosessorien
**kiertävä osoitus**, jossa laitteisto hoitaa kierron ilmaiseksi.

## Symmetria puolittaa kertolaskut

Lineaarivaiheisessa suotimessa $h[k] = h[N-1-k]$, joten saman kertoimen
kertomat näytteet voi laskea ensin yhteen:

$$y[n] = \sum_{k=0}^{N/2-1} h[k]\,\bigl(x[n-k] + x[n-N+1+k]\bigr)
\;\bigl(+\, h[\tfrac{N-1}{2}]\,x[n-\tfrac{N-1}{2}]\bigr).$$

Kertolaskujen määrä puolittuu, yhteenlaskujen ei. Tämä hyödyttää
laitteita, joissa kertolasku on kallis, kuten FPGA:ita ja pieniä
mikrokontrollereita.

```{.c tiedosto="esimerkit/05-fir/fir.c" osa="symm"}
```

## Käyttö ja testaus C:ssä

Pääohjelma suodattaa testisignaalin kerralla ja sitten vaihtelevan
kokoisina lohkoina, myös yhden näytteen lohkoina. Lohkoittaisen
tuloksen on oltava **bitilleen** sama, koska laskujärjestys on sama.
Pienikin ero paljastaisi tilan käsittelyn virheen.

```{.c tiedosto="esimerkit/05-fir/main.c" osa="kaytto"}
```

```{.c tiedosto="esimerkit/05-fir/main.c" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/05-fir.odotettu"}
```

300 Hz kulkee läpi, 3 kHz vaimenee 85 dB, ja symmetrinen muoto antaa
saman tuloksen pyöristysvirheen tarkkuudella. Sen tulos ei ole bitilleen
sama, koska yhteenlaskujen järjestys muuttui.

Yleisin rengaspuskurin virhe on unohtunut kierto. Indeksi
`paikka + k` kulkee puskurin ohi, ja ohjelma lukee viereistä muistia.
Ilman tarkistuksia tulos on hiljaa väärä. Sanitoijilla käännettynä
virhe pysähtyy heti:

```{.c tiedosto="esimerkit/05-rengas.kaatuu.c" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/05-rengas.virhe"}
```

## Vertailu SciPyyn ctypesilla

C-toteutusta verrataan referenssiin samalla datalla. Tutoriaalin
C-lähteet käännetään jaetuksi kirjastoksi, joka ladataan Pythoniin
`ctypes`-modulilla. Kytkentä vaatii, että Python tuntee C-rakenteiden
kentät ja funktioiden tyypit. Taito *Python ja C/C++ yhteen* esittelee
muut tavat (CFFI, pybind11); tässä ctypes riittää, koska tarkoitus on
testata, ei julkaista kirjastoa.

```{.python tiedosto="esimerkit/vertailu/kirjasto.py" osa="kaanna"}
```

```{.python tiedosto="esimerkit/vertailu/kirjasto.py" osa="tyypit"}
```

Tyyppien esittely ei ole muodollisuus. Ilman sitä ctypes muuntaa
argumentit omien sääntöjensä mukaan, olettaa paluuarvon `int`-tyypiksi
ja välittää kaiken, mitä sille annetaan. Jos argumenttien järjestys
on väärä, ohjelma kaatuu tai korruptoi muistia ilman virheilmoitusta.
Rakenne määritellään samoin kentin kuin C:ssä:

```{.python tiedosto="esimerkit/vertailu/kirjasto.py" osa="rakenne"}
```

```{.python tiedosto="esimerkit/vertailu/kirjasto.py" osa="fir"}
```

Kääreolio pitää NumPy-taulukot elossa niin kauan kuin C-rakenne
viittaa niihin. Jos taulukko vapautuisi, C-koodi lukisi vapautettua
muistia. Vertailun virhe normitetaan signaalin tasoon (luku 2):

```{.python tiedosto="esimerkit/vertailu/mallit.py" osa="vertaa"}
```

Vertailuohjelma ajaa kaikki tutoriaalin C-toteutukset ja tulostaa vain
toleranssin ja tuloksen. Varsinainen ero voi vaihdella kääntäjän ja
prosessorin mukaan, joten se näytetään vain virhetilanteessa.

```{.python tiedosto="esimerkit/vertailu/main.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/vertailu.odotettu"}
```

Myöhemmät luvut lisäävät taulukkoon omat rivinsä. Sama vertailu ajetaan
pytestillä parametrisoituna: FIR-suotimen kaikki pituudet 1–255 ja
lohkokoot 1–3000 käydään läpi, ja virheelliset parametrit on hylättävä.

```{.python tiedosto="esimerkit/vertailu/test_vertailu.py" osa="fixture"}
```

```{.python tiedosto="esimerkit/vertailu/test_vertailu.py" osa="fir"}
```

Kirjasto käännetään kerran koko testiajoa varten (`scope="session"`).
Esimerkkihakemiston Makefile ajaa testit ja saman vertailun myös
Clangilla käännetyllä kirjastolla sekä tarkistaa generoidun otsakkeen:

```{.make tiedosto="esimerkit/Makefile" osa="kohteet"}
```

## Käytännössä

- **Generoi kertoimet skriptillä** ja tarkista testissä, että
  versionhallinnan otsake vastaa generaattoria.
- **Pidä tila oliossa ja muisti kutsujalla.** Reaaliaikakoodi ei kutsu
  `malloc`-funktiota, ja sama suodin toimii mikrokontrollerissa ja
  PC:ssä.
- **Testaa lohkoittain ja kerralla**, myös yhden näytteen ja yhden
  pitkän lohkon kokoisina. Tulosten on oltava bitilleen samat.
- **Käännä C-testit sanitoijilla.** Rengaspuskurin indeksivirhe
  tuottaa muuten uskottavan näköistä roskaa.
- **Esittele ctypesille kaikki tyypit** (`argtypes`, `restype`) ja pidä
  NumPy-taulukot elossa niin kauan kuin C viittaa niihin.

## Itsearviointi

- Osaat toteuttaa FIR-suotimen, jonka tila säilyy lohkojen välillä ja
  jonka muisti tulee kutsujalta.
- Osaat selittää kaksoiskirjoitetun rengaspuskurin ja sen hyödyn
  sisäsilmukalle.
- Osaat puolittaa symmetrisen suotimen kertolaskut ja kertoa, miksi
  tulos ei ole bitilleen sama.
- Osaat kääntää C-koodin jaetuksi kirjastoksi, kutsua sitä ctypesilla
  ja verrata tulosta SciPyyn toleranssilla.

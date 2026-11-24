# Tapeout, valmistus ja kotelointi

Tapeout on hetki, jolloin piirikuvio lähetetään valmistajalle. Nimi on
peräisin ajasta, jolloin kuvio toimitettiin magneettinauhalla; nykyään
se on GDSII- tai OASIS-tiedosto, jossa on jokainen suorakulmio
jokaisella kerroksella. Valmistaja tekee kuviosta maskit, yhden
jokaiselle kerrokselle, ja valottaa ne piikiekolle kerros kerrallaan.

## Kiekko ja saanto

Kiekolle mahtuu sitä enemmän piirejä, mitä pienempi piiri on, ja
valmistusvirhe osuu suureen piiriin todennäköisemmin. Saanto (yield)
arvioidaan virhetiheydestä: Poissonin malli olettaa virheet tasaisesti
jakautuneiksi, Murphyn malli huomioi niiden kasautumisen.

```{.python tiedosto="esimerkit/11-saanto.py" osa="malli"}
```

```{.python tiedosto="esimerkit/11-saanto.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/11-saanto.odotettu"}
```

Kun piirin koko nelinkertaistuu 100 mm²:stä 400 mm²:iin, toimivan
piirin hinta lähes kymmenkertaistuu. Siksi suuret suorittimet jaetaan
nykyään pienempiin osapiireihin (chiplet), jotka yhdistetään kotelossa,
ja suuriin muisteihin lisätään vararivejä, joilla viallinen rivi
korvataan testissä.

Valmistuksen jälkeen jokainen piiri testataan kiekolla (wafer sort)
testeripiikeillä luvun 6 vektoreilla. Toimivat piirit sahataan,
koteloidaan ja testataan uudelleen lopputestissä, usein useassa
lämpötilassa. Testin tulokset palautetaan valmistajalle saannon
parantamiseksi.

## Kotelointi

Kotelo liittää piirin piirilevyyn, suojaa sitä ja johtaa lämmön pois.
Kaksi päätapaa:

- **Lankabondaus**: piirin reunan nastoista (pad) vedetään ohuet
  kulta- tai kuparilangat kotelon jalkoihin. Halpa ja joustava, mutta
  nastat ovat vain reunoilla, ja jokaisella langalla on muutaman
  nanohenryn induktanssi.
- **Flip-chip**: piiri käännetään ylösalaisin ja liitetään juotos-
  kuulilla (bump), joita voi olla koko pinnalla. Induktanssi on
  kymmenesosa ja nastoja voi olla tuhansia.

Induktanssi näkyy, kun monta lähtöä vaihtaa tilaa yhtä aikaa: maajohdin
pomppaa (ground bounce), ja hiljaisetkin lähdöt näyttävät hetken
väärää arvoa.

```{.python tiedosto="esimerkit/11-kotelo.py" osa="maapomppu"}
```

## IO-rengas ja ESD

IO-solut ovat suuria: niissä on lähtöajurit, tulojen tasonsiirtimet ja
suojaus sähköstaattista purkausta (ESD) vastaan. Ihmiskehon varaus voi
olla kilovoltteja, ja suojadiodit ja puristimet ohjaavat purkauksen
syöttöjohtimiin ennen kuin se rikkoo transistorin. IO-renkaan nastat
voivat määrätä piirin koon:

```{.python tiedosto="esimerkit/11-kotelo.py" osa="nastat"}
```

```{.python tiedosto="esimerkit/11-kotelo.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/11-kotelo.odotettu"}
```

Nastarajoitteisessa (pad-limited) piirissä ydin on pienempi kuin nastat
vaativat, ja tyhjä tila on hukkaa: piiriin voi lisätä logiikkaa
ilmaiseksi tai siirtyä flip-chipiin, jossa nastat eivät vaadi reunaa.

## Käytännössä

- **Maadoita runsaasti.** Jokaista samanaikaisesti kytkeytyvää
  lähtöryhmää kohden varataan omat syöttö- ja maanastat. Valmistaja
  antaa suhdeluvut (simultaneously switching outputs, SSO).
- **Kotelo valitaan aikaisin.** Kotelo määrää nastojen määrän ja
  järjestyksen, lämmönpoiston ja usein piirin koon.
- **Ensimmäinen piiri ei ole tuote.** Ensimmäiset näytteet (first
  silicon) ajetaan laboratoriossa läpi kaikkien kulmien; virheet
  korjataan metallimaskien ECO:lla (luku 10).
- **MPW prototyypeille.** Monikäyttökiekko jakaa maskikustannuksen,
  mutta näytteitä saa vain kymmeniä ja aikataulu on valmistajan.

## Itsearviointi

- Osaat kuvata tapeoutin, maskien ja kiekkotestin roolin.
- Osaat arvioida saannon ja toimivan piirin hinnan piirin koon
  funktiona.
- Osaat vertailla lankabondausta ja flip-chipiä ja laskea maapompun
  suuruusluokan.
- Osaat selittää, mitä nastarajoitteinen piiri tarkoittaa ja mihin
  ESD-suojausta tarvitaan.

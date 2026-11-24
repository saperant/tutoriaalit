# Mittaa ensin

Ennen kuin riviäkään kirjoitetaan C++:lla, mitataan, missä aika
kuluu. Ohjelman hitaus keskittyy lähes aina pieneen osaan koodia, ja
arvaus siitä, mikä osa se on, menee usein väärin. Mittaus kertoo myös,
millainen pullonkaula on: osa ratkeaa NumPylla ilman yhtään riviä
natiivikoodia, osa ei.

## Kaksi silmukkaa

Esimerkissä anturin mittaussarjasta lasketaan liukuva keskiarvo ja
eksponentiaalinen suodatin. Molemmat ovat yksinkertaisia
Python-silmukoita:

```{.python tiedosto="esimerkit/02-pullonkaula/main.py" osa="silmukat"}
```

Silmukat näyttävät samanlaisilta, mutta ne ovat rakenteeltaan
erilaisia. Liukuvan keskiarvon jokainen tulos riippuu vain syötteestä,
joten sen voi laskea koko taulukolle kerralla. Suodattimen jokainen
tulos riippuu edellisestä tuloksesta, joten lasku on luonnostaan
peräkkäinen.

## Profiloija näyttää pullonkaulan

`cProfile` mittaa jokaisen funktion kutsukerrat ja ajan. Komentoriviltä
se ajetaan muodossa `python3 -m cProfile -s tottime ohjelma.py`, ja
tulosteen kärjessä ovat funktiot, joissa kuluu eniten omaa aikaa.
Esimerkki käyttää samaa profiloijaa ohjelmasta käsin ja poimii
tuloksesta pahimman funktion:

```{.python tiedosto="esimerkit/02-pullonkaula/main.py" osa="profilointi"}
```

*Oma aika* (`tottime`) on funktiossa itsessään kulunut aika ilman sen
kutsumia funktioita. *Kumulatiivinen aika* (`cumtime`) sisältää
kutsutut funktiot. Pullonkaula löytyy omasta ajasta, ja kumulatiivinen
aika näyttää, mitä polkua pitkin siihen päädytään.

`cProfile` lisää jokaiseen funktiokutsuun oman kustannuksensa, joten se
liioittelee pienten, usein kutsuttujen funktioiden osuutta.
Näytteenottava profiloija, kuten `py-spy` tai Linuxin `perf` (Python
3.12:sta alkaen `python3 -X perf`), keskeyttää ohjelman satunnaisin
väliajoin eikä muuta sen ajoitusta. Se näkee myös natiivikoodin
sisään, mikä on hyödyllistä, kun osa ohjelmasta on jo C++:aa.

## Vektorointi ratkaisee toisen

Liukuva keskiarvo saadaan kertymäsummasta: ikkunan summa on kahden
kertymän erotus. Koko lasku on muutama NumPy-operaatio, jotka
silmukoivat C:ssä:

```{.python tiedosto="esimerkit/02-pullonkaula/main.py" osa="vektoroitu"}
```

Tulokset verrataan ennen ajoituksia, ja ajoista otetaan paras
viidestä, koska muut ohjelmat ja välimuistit hidastavat yksittäisiä
ajoja satunnaisesti:

```{.python tiedosto="esimerkit/02-pullonkaula/main.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/02-pullonkaula/main.odotettu"}
```

Testattu raja on väljä, viisinkertainen. Todellinen ero on tyypillisesti
kymmeniä kertoja, mutta tarkka luku riippuu koneesta, eikä
testi saa kaatua hitaalla CI-koneella. Tutoriaalin kaikki ajoitukset
on kirjoitettu samalla periaatteella: tulosteessa on vain väite, joka
pitää paikkansa kaikilla koneilla, ja tarkat suhdeluvut tulostetaan
virhetulosteeseen.

Eksponentiaalista suodatinta ei voi kirjoittaa samalla tavalla.
Jokainen `y` tarvitsee edellisen, eikä NumPylla ole operaatiota, joka
laskisi juuri tämän rekursion. Tämä on tyypillinen paikka natiivikoodille.

## Vaihtoehdot ennen C++:aa

Kun profiloija on osoittanut silmukan, jota ei voi vektoroida, on
monta tapaa nopeuttaa sitä. Ne ovat eri hintaisia:

- **Parempi algoritmi tai tietorakenne.** Lineaarinen haku
  sanakirjaksi, toistuva lasku välimuistiin. Ilmaista ja usein
  tehokkainta.
- **NumPy, SciPy ja vakiokirjasto.** Esimerkiksi `scipy.signal.lfilter`
  laskee juuri eksponentiaalisen suodattimen kaltaiset rekursiot
  C:ssä. Valmis kirjasto on testattu ja nopea.
- **Numba** kääntää Python-funktion konekielelle ajon aikana, kun
  siihen lisätään koriste `@numba.njit`. Se sopii NumPy-taulukoita
  käsitteleviin silmukoihin, mutta tukee vain osaa Pythonista.
- **Cython** on Pythonin laajennus, jossa muuttujille annetaan
  C-tyypit. Se käännetään C:ksi ja edelleen laajennusmoduuliksi. Se
  sopii, kun nopeutettava koodi on alun perin Pythonia.
- **Oma C- tai C++-laajennus** pybind11:llä tai nanobindilla. Se on
  oikea valinta, kun logiikka on jo C++:aa, kun tarvitaan C++-kirjastoja
  tai säikeitä, tai kun samaa koodia käytetään myös muualta kuin
  Pythonista.

Tämä tutoriaali käsittelee viimeistä vaihtoehtoa ja sen esiastetta:
olemassa olevan C-kirjaston käyttöä suoraan `ctypes`illä.

## Käytännössä

- **Profiloi oikealla syötteellä.** Pieni testisyöte näyttää eri
  pullonkaulan kuin tuotannon data: käynnistys ja tuonnit hallitsevat
  pieniä ajoja.
- **Oma aika ensin.** Lajittele `tottime`n mukaan ja katso kärkeä.
  Kumulatiivinen aika kertoo, mistä kärkeen tullaan.
- **Vertaa tulokset ennen ajoja.** Nopea väärä tulos on arvoton, ja
  optimointi on yleinen virheiden lähde.
- **Paras usean ajon ajasta**, ei keskiarvo. Häiriöt vain hidastavat,
  joten minimi on lähimpänä koodin todellista nopeutta.
  `timeit`-moduuli tekee saman valmiiksi.
- **Vektoroi ennen kuin käännät.** NumPy-ratkaisu on lyhyempi,
  siirrettävä ja ilman käännösvaihetta. C++ kannattaa vasta, kun
  lasku on peräkkäistä tai vaatii natiivikirjastoa.
- **Sudenkuoppa:** muunnokset rajalla. `data.tolist()` ja
  `np.array(lista)` kopioivat koko datan. Jos putki vaihtaa muotoa
  vaiheiden välillä, muunnos voi olla kalliimpi kuin itse lasku.

## Itsearviointi

- Osaat profiloida ohjelman `cProfile`lla ja tulkita oman ja
  kumulatiivisen ajan eron.
- Osaat erottaa vektoroitavan laskun peräkkäisestä ja kirjoittaa
  vektoroitavan NumPylla.
- Osaat ajoittaa kaksi toteutusta luotettavasti: tulosten vertailu,
  paras usean ajon ajasta ja koneesta riippumaton raja.
- Osaat valita NumPyn, Numban, Cythonin ja oman C++-laajennuksen
  välillä tilanteen mukaan.

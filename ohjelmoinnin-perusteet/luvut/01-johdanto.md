# Johdanto {.runko-johdanto}

Ohjelma on tarkka kuvaus siitä, miten tietokone muuttaa syötteen
halutuksi tulokseksi. Ohjelmointi on vähemmän koodin kirjoittamista kuin
ongelman jäsentämistä: mitä tietoa on, mitä siitä halutaan, missä
vaiheissa ja mitkä tilanteet voivat mennä pieleen. Koodi on tämän
ajattelun lopputulos.

Tämä tutoriaali opettaa ohjelmoinnin perusteet lukijalle, joka ei ole
ohjelmoinut aiemmin. Kieli on Python, mutta käsitteet (arvot, tyypit,
ohjausrakenteet, funktiot, tietorakenteet, virheet, luokat, modulit ja
testit) ovat samat kaikissa yleisissä ohjelmointikielissä.

## Mitä tutoriaali opettaa

Tavoite on oikea ohjelmointitaito, ei syntaksin luettelo. Siksi:

- Jokainen esimerkki ratkaisee pienen, tunnistettavan tehtävän: kuitin
  laskenta, syötteen tarkistus, sanatilasto, pankkiviitteen tarkiste,
  budjettiraportti.
- Esimerkit on kirjoitettu niin kuin ammattilainen ne kirjoittaisi:
  kuvaavat nimet, pienet funktiot, syötteen tarkistus ja testit.
- Jokaisen luvun lopussa *Käytännössä* kertoo, miten ammattilaiset
  luvun asioita käyttävät ja miksi, ja *Itsearviointi* luettelee, mitä
  luvun jälkeen pitäisi osata.
- Yleiset virheet näytetään testattuina esimerkkeinä: koodi, jonka
  tarkistustyökalu hylkää, tai ohjelma, joka kaatuu.
- Sisältölukujen lopussa on *Kokeile itse* -tehtäviä, joiden ratkaisun
  voi tarkistaa automaattisesti (ks. *Tehtävät*).

Tutoriaali ei käy läpi Pythonin kaikkia piirteitä. Kun perusteet ovat
hallussa, taitopuussa seuraavat taito *Python* (idiomaattinen ja
ammattimainen Python), *Tietorakenteet*, *Algoritmit*, *Versionhallinta (Git)*
ja *Komentorivi ja Linux*.

## Miksi Python

Python on yleisin ensimmäinen ohjelmointikieli yliopistoissa ja
ammattikorkeakouluissa, ja sitä käytetään laajasti datan käsittelyssä,
tekoälyssä, automaatiossa, verkkopalveluissa ja testauksessa. Sen
syntaksi on tiivis: ohjelman rakenne näkyy sisennyksestä, eikä
aloittelijan tarvitse heti ymmärtää muistinhallintaa tai kääntämistä.

Pythonin heikkouksia ovat hitaus suoritinta kuormittavissa tehtävissä ja
se, että tyyppivirheet huomataan oletuksena vasta ohjelmaa ajettaessa.
Jälkimmäistä paikataan tässä tutoriaalissa alusta asti
tarkistustyökaluilla (ks. *Työkalut*).

## Ympäristö

Esimerkit vaativat Python 3.12:n tai uudemman. Helpoin tapa saada
valmis ympäristö on tutoriaalin kehityskontti: avaa repositorio
Visual Studio Codessa *Dev Containers* -laajennuksella tai GitHub
Codespacesissa ja valitse *Ohjelmoinnin perusteet*. Kontissa on Python,
pytest, ruff ja mypy valmiina.

Omalle koneelle Pythonin saa osoitteesta python.org tai Linuxissa
paketinhallinnasta. Asennuksen voi tarkistaa terminaalissa:

```text
$ python3 --version
Python 3.12.3
```

Ohjelmointiin tarvitaan kaksi työkalua:

- **Editori** tiedostojen kirjoittamiseen. Visual Studio Code
  Python-laajennuksella näyttää virheet jo kirjoitettaessa.
- **Terminaali** ohjelmien ajamiseen. Ohjelma `kuitti.py` ajetaan
  komennolla `python3 kuitti.py`.

Komento `python3` ilman tiedostonimeä avaa vuorovaikutteisen tulkin
(REPL), johon voi kirjoittaa lausekkeita ja nähdä tuloksen heti. Se
sopii kokeiluihin; varsinaiset ohjelmat kirjoitetaan tiedostoihin.

## Ensimmäinen ohjelma

Kolme ystävää jakaa ravintolalaskun tasan ja lisää kymmenen prosentin
tipin. Ohjelma laskee kunkin osuuden:

```{.python tiedosto="esimerkit/01-ateria.py"}
```

```{.tuloste tiedosto="esimerkit/01-ateria.odotettu"}
```

Ohjelma suoritetaan ylhäältä alas rivi kerrallaan:

1. Ensimmäinen rivi on *dokumentaatiomerkkijono*, joka kertoo, mitä
   tiedosto tekee.
2. Rivit `lasku = 86.40` jne. antavat arvoille nimet eli luovat
   *muuttujat*.
3. Seuraavat rivit laskevat uusia arvoja aiemmista.
4. `print` tulostaa tuloksen. Merkkijonon edessä oleva `f` sallii
   lausekkeet aaltosulkeissa, ja `:.2f` pyöristää kahteen desimaaliin.

Jo näin lyhyessä ohjelmassa on kaksi hyvän koodin tapaa. Nimet kertovat,
mitä arvot tarkoittavat: `tippi_prosentti` on selvempi kuin `t` tai `x`.
Lähtötiedot ovat ohjelman alussa omina muuttujinaan, joten laskun tai
henkilömäärän muuttaminen ei vaadi kaavojen muokkaamista.

## Työkalut

Python-tulkki huomaa monet virheet vasta, kun virheellinen rivi
suoritetaan. Ammattilaiset tarkistavat koodin ennen ajamista kahdella
työkalulla, joita tämäkin tutoriaali käyttää:

- **ruff** on *lintteri*: se etsii koodista virheitä ja epäilyttäviä
  rakenteita, kuten käyttämättömiä muuttujia ja nimiä, joita ei ole
  määritelty.
- **mypy** on *tyyppitarkistin*: se varmistaa, että arvoja käytetään
  niiden tyypin mukaisesti, esimerkiksi ettei tekstiä yritetä laskea
  yhteen luvun kanssa.

Kun koodissa ei ole huomautettavaa, työkalut kertovat sen lyhyesti:

```text
$ ruff check kuitti.py
All checks passed!
$ mypy kuitti.py
Success: no issues found in 1 source file
$ python3 kuitti.py
```

Testauskehys **pytest** esitellään luvussa *Testaus*.

Kehityskontissa työkalut ovat valmiina. Omalle koneelle ne asennetaan
projektin omaan *virtuaaliympäristöön*, jotta ne eivät sekoitu muiden
projektien paketteihin:

```text
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install ruff mypy pytest
```

Windowsissa aktivointikomento on `.venv\Scripts\activate`.
Virtuaaliympäristöihin ja `pip`-työkaluun palataan luvussa *Modulit ja
standardikirjasto*.

## Esimerkkien testaus

Kaikki tämän tutoriaalin koodi on peräisin hakemiston `esimerkit`
tiedostoista. Jokainen tiedosto tarkistetaan ruffilla ja mypyllä,
ajetaan tyhjässä väliaikaisessa hakemistossa ja sen tulostetta verrataan
tiedostoon, josta myös tekstissä näkyvät tulosteet on poimittu.

Osa esimerkeistä näyttää koodia, jonka tarkistus hylkää. Ne testataan
kahdesti: ensin varmistetaan, että tarkistus epäonnistuu, ja sitten,
että se onnistuu, kun virheellinen rivi on poistettu. Muutama esimerkki
näyttää ajonaikaisen virheen, ja sen testi varmistaa, että ohjelma
todella kaatuu odotetulla tavalla. Hakemistoesimerkkien pytest-testit
ajetaan hakemiston `esimerkit` Makefilellä (`make`).

## Tehtävät

Lukujen 2–11 lopussa on *Kokeile itse* -tehtäviä helpoimmasta
vaativimpaan. Jokaisella tehtävällä on tunnus (luku ja järjestysnumero,
esimerkiksi `03-1`), pohjatiedosto, jonka alussa on tarkka tehtävänanto,
ja testitapaukset. Tehtävät tehdään hakemistossa `esimerkit`:

```text
$ python3 tarkista.py --aloita 03-1
Pohja kopioitu: .../esimerkit/tehtavat/omat/03-1.py
$ python3 tarkista.py 03-1
03-1 Lämpötilan luokitus: tapaus 1/5 ei mene läpi.
  syöte:    -5
  odotettu: pakkasta
  saatu:    ?
```

Valitsin `--aloita` kopioi pohjan hakemistoon `tehtavat/omat`, jossa
sitä muokataan. Tarkistin ajaa ratkaisun testitapauksilla ja näyttää
ensimmäisen, joka ei mene läpi: syötteen tai funktiokutsun, odotetun
tuloksen ja saadun tuloksen. Kun ratkaisu on valmis, tuloste on
`03-1 Lämpötilan luokitus: 5/5 tapausta oikein.` Ilman argumentteja
tarkistin kertoo käyttönsä:

```{.tuloste tiedosto="esimerkit/tarkista.odotettu"}
```

Malliratkaisut ovat hakemistossa `tehtavat/ratkaisut`. Niihin kannattaa
katsoa vasta, kun oma ratkaisu menee läpi: tehtävän hyöty on omassa
ajattelussa, ja malliratkaisu on vain yksi oikeista tavoista.
Tutoriaalin testit ajavat malliratkaisut samoilla testitapauksilla ja
varmistavat, ettei muokkaamaton pohja kelpaa ratkaisuksi.

## Miten tätä tutoriaalia kannattaa lukea

Ohjelmointia oppii vain ohjelmoimalla. Kirjoita esimerkit itse
mieluummin kuin kopioit ne, aja ne ja muuta niitä: mitä tapahtuu, jos
syöte on tyhjä, negatiivinen tai tekstiä? Tee luvun tehtävät ennen
seuraavaan lukuun siirtymistä. Virheilmoitukset ovat tietoa, eivät
epäonnistumisia. Luvut on tarkoitettu luettaviksi
järjestyksessä, koska jokainen rakentuu edellisten varaan.

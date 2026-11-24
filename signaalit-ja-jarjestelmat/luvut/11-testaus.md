# Signaalinkäsittelykoodin testaus

Signaalinkäsittelyn virheet ovat hiljaisia. Väärin normitettu suodin,
unohtunut tila tai sekoittunut taajuusyksikkö tuottaa uskottavan näköisen
käyrän, eikä ohjelma kaadu. Siksi tällainen koodi testataan
järjestelmällisesti. Tässä luvussa kootaan aiempien lukujen tekniikat
pieneksi kirjastoksi ja sen pytest-testeiksi. Pytestin perusteet ja
fixturet käytiin läpi taidossa *Python työkaluohjelmointiin*; tässä
keskitytään siihen, mitä signaalinkäsittelyssä testataan ja millä
toleransseilla.

## Kirjasto

Kirjastossa on kolme suodinta: liukuva keskiarvo, tilallinen
eksponentiaalinen keskiarvo ja lovisuotimen suunnittelufunktio. Kaikki
tarkistavat parametrinsa, koska väärä parametri tuottaisi muuten
hiljaa väärän suotimen.

```{.python tiedosto="esimerkit/11-suotimet/suotimet.py" osa="keskiarvo"}
```

```{.python tiedosto="esimerkit/11-suotimet/suotimet.py" osa="ema"}
```

```{.python tiedosto="esimerkit/11-suotimet/suotimet.py" osa="lovi"}
```

Pääohjelma käyttää kirjastoa: se poistaa 50 Hz:n hurinan ja tasoittaa
tuloksen lohkoittain.

```{.python tiedosto="esimerkit/11-suotimet/main.py"}
```

```{.tuloste tiedosto="esimerkit/11-suotimet.odotettu"}
```

## Mitä testataan

Signaalinkäsittelykoodille on neljä hyödyllistä testityyppiä.

| Testityyppi | Mitä se löytää | Esimerkki |
|-------------|----------------|-----------|
| ominaisuus | tilan vuotaminen, epälineaarisuus, indeksivirheet | lineaarisuus, aikainvarianssi |
| referenssi | väärät kertoimet, normitus, reunaehdot | oma toteutus vs. `lfilter` |
| vaatimus | suunnitteluvirheet | vaimennus loven kohdalla, stabiilisuus |
| rajatapaus | puuttuva validointi | tyhjä syöte, virheellinen taajuus |

**Ominaisuustestit** ovat luvun 4 tekniikka. Satunnaiset syötteet
tuotetaan fixturen generaattorilla, jolla on kiinteä siemen, joten
epäonnistunut testi toistuu samanlaisena. Parametrisointi ajaa samat
testit kaikille järjestelmille.

```{.python tiedosto="esimerkit/11-suotimet/test_suotimet.py" osa="fixture"}
```

```{.python tiedosto="esimerkit/11-suotimet/test_suotimet.py" osa="ominaisuudet"}
```

**Referenssitestit** vertaavat kirjaston tulosta luotettavaan
toteutukseen. Lohkoittainen käsittely testataan useilla lohkopituuksilla,
myös pituudella 1, koska tilan käsittelyn virheet näkyvät lohkojen
rajoilla (luku 5).

```{.python tiedosto="esimerkit/11-suotimet/test_suotimet.py" osa="referenssi"}
```

**Vaatimustestit** kirjoittavat suotimen määrittelyn auki: vahvistus
tasajännitteellä, vaimennus loven kohdalla, vahvistus muualla ja navat
yksikköympyrän sisällä. Parametrisointi kokeilee useita näytetaajuuksia,
mikä paljastaa hertsien ja normitettujen taajuuksien sekoittumisen.
**Rajatapaustestit** varmistavat, että virheellinen parametri hylätään.

```{.python tiedosto="esimerkit/11-suotimet/test_suotimet.py" osa="lovi"}
```

Testit ajetaan esimerkkihakemistosta komennolla `make` tai suoraan:
`python3 -m pytest -q`. Parametrisoinnin ansiosta 19 testitapausta
syntyy alle sadasta rivistä.

## Toleranssit

Liukuluvut eivät ole tarkkoja, joten testit vertaavat toleranssilla.
Toleranssin valinta on suunnittelupäätös.

- **Absoluuttinen toleranssi** (`atol`) sopii, kun odotettu arvo voi
  olla nolla, kuten suotimen ulostulo hiljaisella hetkellä.
  Suhteellinen toleranssi on silloin hyödytön, koska nollan ympärillä
  jokainen virhe on suhteellisesti ääretön.
- **Suhteellinen toleranssi** (`rtol`) sopii suureille, joiden
  suuruusluokka vaihtelee, kuten energialle ja vahvistukselle.
- **Toleranssi kertoo vaatimuksen.** Kun kaksi toteutusta laskee saman
  asian samalla tavalla, ero on pyöristysvirheen luokkaa ($10^{-12}$).
  Kun vaatimus on suunnittelusta ("vahvistus noin yksi"), toleranssi on
  löysempi ja perustellaan kommentissa.

`numpy.testing.assert_allclose` kertoo epäonnistuessaan, montako
alkiota poikkeaa ja kuinka paljon. Se on paljon hyödyllisempi kuin
`assert np.allclose(...)`, joka kertoo vain epätoden totuusarvon. Alla
lohkoittainen suodatus unohtaa tilan, ja vertailu referenssiin
paljastaa sen:

```{.python tiedosto="esimerkit/11-toleranssi.kaatuu.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/11-toleranssi.virhe"}
```

Ensimmäinen lohko on oikein, ja kolme muuta ovat väärin. Virheiden
osuus, 75 prosenttia, kertoo suoraan, että ongelma on lohkojen
rajoilla.

## Kultaiset tiedostot ja deterministisyys

Tämän tutoriaalin jokainen esimerkki on myös testi: testaaja ajaa sen
ja vertaa tulostetta tallennettuun *kultaiseen* tiedostoon. Jotta se
toimii, tulosteen on oltava sama joka koneella. Tutoriaalin esimerkit
noudattavat muutamaa sääntöä.

- Satunnaisuus tuotetaan aina kiinteällä siemenellä
  (`numpy.random.default_rng(siemen)`), ei globaalilla tilalla.
- Tulostetaan pyöristetty arvo tai totuusarvo (`numpy.allclose`), ei
  koko liukulukua. Pyöristys poistaa viimeisten bittien erot, joita eri
  prosessorit ja kirjastoversiot tuottavat.
- Pyöristetty $-0{,}0$ muutetaan nollaksi lisäämällä $0{,}0$, koska
  `f"{-0.0:.2f}"` tulostaa miinusmerkin.
- Ajoaikoja ei tulosteta. Tehokkuutta verrataan laskemalla operaatioita,
  kuten luvussa 9.

## Käytännössä

- **Testaa ominaisuuksia, ei vain esimerkkejä.** Lineaarisuus,
  aikainvarianssi ja lohkoittaisen käsittelyn yhtäpitävyys löytävät
  virheitä, joita yksittäinen odotettu arvo ei löydä.
- **Pidä referenssitoteutus yksinkertaisena.** Silmukkaversio on hidas
  mutta luettava, ja se on hyvä totuus nopealle toteutukselle.
- **Kirjoita suotimen vaatimukset testeiksi.** Päästö- ja estokaistan
  rajat sekä stabiilisuus ovat tarkistettavia lukuja.
- **Käytä `assert_allclose`-funktiota** ja valitse `atol` tai `rtol`
  sen mukaan, voiko odotettu arvo olla nolla.
- **Kiinnitä siemen ja pyöristä tulosteet**, jotta testit ovat
  toistettavia koneesta ja kirjastoversiosta riippumatta.

## Itsearviointi

- Osaat kirjoittaa pytest-testit, jotka tarkistavat suotimen
  lineaarisuuden ja aikainvarianssin satunnaisilla syötteillä kiinteällä
  siemenellä.
- Osaat testata lohkoittaisen käsittelyn referenssiä vastaan usealla
  lohkopituudella.
- Osaat kirjoittaa suotimen taajuusvaatimukset ja stabiilisuuden
  testeiksi ja parametrisoida ne.
- Osaat valita absoluuttisen ja suhteellisen toleranssin ja tehdä
  tulosteista deterministisiä.

# Funktiot

Funktio on nimetty koodin osa, joka saa syötteenä *parametreja* ja
palauttaa *paluuarvon*. Funktiot ovat ohjelmoinnin tärkein työkalu
monimutkaisuuden hallintaan: iso ongelma jaetaan pieniin osiin, joista
jokainen on helppo ymmärtää, testata ja käyttää uudelleen.

## Määrittely ja kutsu

```{.python tiedosto="esimerkit/04-kuitti.py"}
```

```{.tuloste tiedosto="esimerkit/04-kuitti.odotettu"}
```

Funktion osat:

- `def rivin_hinta(maara: int, a_hinta_snt: int) -> int:` määrittelee
  funktion nimen ja parametrit. Merkinnät `: int` ja `-> int` ovat
  *tyyppivihjeitä*: parametrit ja paluuarvo ovat kokonaislukuja.
  Python ei käytä niitä ajon aikana, mutta mypy tarkistaa niiden
  avulla, että funktiota kutsutaan oikein.
- Ensimmäinen rivi `"""..."""` on dokumentaatiomerkkijono. Se kertoo,
  *mitä* funktio tekee, ei *miten*.
- `return` lopettaa funktion ja palauttaa arvon kutsujalle. Funktio
  ilman `return`-lausetta palauttaa `None`.

Kutsu `rivin_hinta(2, 189)` sijoittaa argumentit parametreihin
järjestyksessä, suorittaa rungon ja korvautuu paluuarvolla.

Pääohjelma on nyt lyhyt ja luettava: se kertoo *mitä* tehdään, ja
funktiot kertovat *miten*. Jos ALV-laskenta muuttuu, muutos tehdään
yhteen paikkaan.

## Paluuarvo vai tulostus

Funktio, joka palauttaa tuloksen, on hyödyllisempi kuin funktio, joka
tulostaa sen. Palautettua arvoa voi käyttää laskennassa, tallentaa,
näyttää eri muodoissa ja testata. Tulostettu arvo on vain tekstiä
ruudulla.

```{.python tiedosto="esimerkit/04-salasana.py"}
```

```{.tuloste tiedosto="esimerkit/04-salasana.odotettu"}
```

`salasanan_ongelmat` ei päätä, miten ongelmat esitetään: sama funktio
sopisi verkkolomakkeeseen ja komentoriviohjelmaan. Paluuarvona on lista
ongelmista, joten tyhjä lista tarkoittaa hyväksyttyä salasanaa ja
kutsuja voi kertoa käyttäjälle kaikki puutteet kerralla.
`any(merkki.isdigit() for merkki in salasana)` on tosi, jos jokin
merkeistä on numero (rakenne `... for ... in ...` esitellään luvussa
*Kokoelmat*), ja `", ".join(ongelmat)` yhdistää listan merkkijonot
pilkuin erotelluksi tekstiksi.

## Oletusarvot ja nimetyt argumentit

Parametrilla voi olla oletusarvo (`min_pituus: int = 12`), jolloin
argumentin voi jättää kutsusta pois. Argumentin voi antaa myös nimellä:
`salasanan_ongelmat("Kissa123", min_pituus=8)`. Nimetty argumentti tekee
kutsusta itsedokumentoivan: pelkkä `8` ei kertoisi lukijalle mitään.

## Näkyvyys: paikalliset ja globaalit nimet

Funktion sisällä sijoitetut nimet ovat *paikallisia*: ne ovat olemassa
vain funktion suorituksen ajan, eivätkä ne näy funktion ulkopuolelle.
Tämä on hyvä asia, koska funktion sisäiset nimet eivät voi sotkea
muuta ohjelmaa. Seurauksena funktio ei kuitenkaan voi muuttaa
ulkopuolista muuttujaa sijoituksella:

```{.python tiedosto="esimerkit/04-kavijat.ei-kaanny.py"}
```

Funktiossa `kirjaa_kavija_vaarin` sijoitus tekee nimestä `kavijoita`
paikallisen, joten oikean puolen `kavijoita` viittaa paikalliseen
muuttujaan, jolla ei vielä ole arvoa. Ohjelma kaatuisi virheeseen
`UnboundLocalError`, mutta ruff huomaa sen jo ennen ajoa:

```text
F823 Local variable `kavijoita` referenced before assignment
```

Oikea ratkaisu on `kirjaa_kavija`: arvo tuodaan funktioon parametrina
ja uusi arvo palautetaan. Avainsanalla `global` funktio voisi muuttaa
globaalia muuttujaa, mutta sitä ei käytetä, koska silloin funktion
toiminta riippuu piilotetusta tilasta, jota on vaikea seurata ja
testata.

## Käytännössä

- **Yksi funktio, yksi tehtävä.** Jos funktion tehtävän kuvaamiseen
  tarvitaan sana "ja", se kannattaa todennäköisesti jakaa kahdeksi.
  Hyvä funktio mahtuu ruudulle, tyypillisesti alle 20 riviä.
- **Nimeä funktio teon mukaan** (`laske_tarkiste`, `tulosta_rivi`) tai
  tuloksen mukaan (`rivin_hinta`, `salasanan_ongelmat`).
- **Palauta, älä tulosta.** Erota laskenta ja esittäminen: laskevat
  funktiot palauttavat arvon, ja vain ohjelman reunalla oleva koodi
  lukee syötteen ja tulostaa.
- **Puhtaat funktiot ensin.** Funktio, jonka tulos riippuu vain
  parametreista eikä se muuta mitään muuta, on helppo ymmärtää ja
  testata. Vältä globaaleja muuttujia; vakiot (`ALV_PROSENTTI`) ovat
  sallittuja, koska ne eivät muutu.
- **Tyyppivihjeet ja dokumentaatiomerkkijono jokaiseen funktioon.**
  Ne ovat funktion käyttöohje, jonka myös mypy ymmärtää.
- **DRY (*don't repeat yourself*).** Kun sama laskenta toistuu, siitä
  tehdään funktio. Kopioitu koodi korjataan helposti vain yhdestä
  kohdasta.

## Itsearviointi

- Osaat määritellä funktion parametreineen, tyyppivihjeineen,
  dokumentaatiomerkkijonoineen ja paluuarvoineen.
- Osaat pilkkoa ohjelman pieniksi funktioiksi ja perustella jaon.
- Osaat selittää, miksi palauttava funktio on parempi kuin tulostava.
- Osaat käyttää oletusarvoja ja nimettyjä argumentteja.
- Osaat selittää paikallisen ja globaalin nimen eron ja välttää
  globaalia tilaa.

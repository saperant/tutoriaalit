# Testaus

Ohjelman kokeileminen käsin kertoo, että se toimi sillä kertaa, sillä
syötteellä. *Automaattinen testi* on koodia, joka ajaa ohjelman osaa
tunnetuilla syötteillä ja tarkistaa tuloksen. Testit ajetaan jokaisen
muutoksen jälkeen sekunneissa, joten ne kertovat heti, jos muutos
rikkoi jotain aiemmin toiminutta. Ammattimaisessa ohjelmistokehityksessä
testit ovat yhtä tärkeä osa koodia kuin itse ohjelma.

## Testattava tehtävä: pankkiviite

Suomalaisen pankkiviitteen viimeinen numero on *tarkiste*, joka
lasketaan muista numeroista. Pankki hylkää viitteen, jonka tarkiste ei
täsmää, joten näppäilyvirhe huomataan heti. Laskusääntö on
dokumentaatiomerkkijonossa:

```{.python tiedosto="esimerkit/10-viite/viite.py"}
```

`enumerate(reversed(perusosa))` käy numerot läpi oikealta alkaen
järjestysnumeroineen, ja `PAINOT[i % 3]` kiertää painoja 7, 3, 1.
Viimeinen `% 10` hoitaa tapauksen, jossa erotus on 10.

## Testit pytestillä

pytest-kehyksessä testi on funktio, jonka nimi alkaa sanalla `test_`, ja
se tarkistaa tuloksen `assert`-lauseella. Testit kirjoitetaan omaan
tiedostoonsa, jonka nimi alkaa samoin:

```{.python tiedosto="esimerkit/10-viite/test_viite.py"}
```

Testit ajetaan hakemistossa komennolla `pytest`:

```text
$ pytest -q
.............                                            [100%]
13 passed in 0.02s
```

Jokainen piste on läpäisty testi. Jos `assert`-lauseen ehto on epätosi,
pytest näyttää epäonnistuneen testin nimen ja vertailun molemmat
puolet, esimerkiksi:

```text
>       assert muodosta_viite("123456") == "1234561"
E       AssertionError: assert '1234567' == '1234561'
```

Testitiedoston rakenteet:

- `@pytest.mark.parametrize` ajaa saman testin monella syötteellä.
  Jokainen syöte näkyy raportissa omana testinään.
- `with pytest.raises(ValueError):` tarkistaa, että lohko nostaa
  poikkeuksen. Myös virhetilanteet ovat määriteltyä käytöstä, jota
  testataan.
- Kommentti `# 1*7 + 0*3 + 3*1 = 10` kertoo, miksi odotettu tulos on
  oikea. Testi on samalla esimerkki laskusäännöstä.

Pääohjelma käyttää samaa modulia:

```{.python tiedosto="esimerkit/10-viite/main.py"}
```

```{.tuloste tiedosto="esimerkit/10-viite.odotettu"}
```

## Mitä testataan

Kaikkia syötteitä ei voi testata, joten testitapaukset valitaan
järjestelmällisesti:

- **Tunnettu oikea tulos** riippumattomasta lähteestä. Viite 1234561
  on yleisesti käytetty esimerkkiviite.
- **Rajatapaukset:** lyhin ja pisin sallittu, yksi yli ja yksi alle,
  tyhjä syöte, nolla. Viitteessä 3 ja 19 numeron perusosat ovat
  sallittuja, 2 ja 20 eivät.
- **Erikoistapaukset**, joissa laskusääntö haarautuu: tarkiste 0, kun
  summa on tasakymmeniä.
- **Virheelliset syötteet:** kirjaimet, väärä tarkiste, välilyönnit.
- **Jokainen löydetty virhe** saa testin, joka toistaa sen ennen
  korjausta. Sama virhe ei palaa huomaamatta.

## Testit ensin

Testin voi kirjoittaa ennen toteutusta. Silloin testi on tarkka
määrittely sille, mitä funktion pitää tehdä, ja kirjoittaja joutuu
miettimään rajatapaukset ennen koodia. Työtapa (*test-driven
development*, TDD) etenee lyhyin kierroksin:

1. Kirjoita testi yhdelle uudelle toiminnolle. Aja se: testin pitää
   epäonnistua, koska toimintoa ei vielä ole.
2. Kirjoita yksinkertaisin koodi, joka läpäisee testin.
3. Siisti koodi (*refaktoroi*). Testit varmistavat, ettei siistiminen
   rikkonut mitään.

Täyttä TDD:tä ei tarvitse noudattaa aina, mutta testit ensin
-ajattelu kannattaa: jos funktiolle ei osaa kirjoittaa testiä, sen
tehtävä ei ole vielä selvä.

## Kokeile itse

Lukujen tehtävien tarkistin `tarkista.py` on tämän luvun sovellus: se
ajaa ratkaisun tunnetuilla syötteillä ja vertaa tulosta odotettuun.
Vertailu ei ole pelkkä `==`, koska testin pitää hyväksyä kaikki oikeat
vastaukset ja vain ne:

```{.python tiedosto="esimerkit/tarkista.py" osa="sama"}
```

Liukulukuja verrataan pienellä toleranssilla (luku *Arvot, tyypit ja
muuttujat*), ja tyypin on täsmättävä: `True == 1` on Pythonissa tosi,
mutta totuusarvoa odottava testi ei saa hyväksyä lukua 1.
`isinstance(arvo, tyyppi)` kertoo, onko arvo annettua tyyppiä.

Tämän luvun tehtävissä kirjoitetaan testejä, ei toteutusta. Tarkistin
ajaa testisi ensin oikeaa toteutusta vasten, jolloin kaikkien testien
pitää mennä läpi. Sitten se vaihtaa tilalle virheellisiä toteutuksia
yksi kerrallaan: hyvä testijoukko jää kiinni jokaiseen. Jos jokin
virhe pääsee läpi, tarkistin kertoo, mitä testeistä puuttuu.

1. **Testit karkausvuodelle** (`10-1`). Kirjoita funktiolle
   `on_karkausvuosi` testit, jotka kattavat säännön jokaisen haaran.
2. **Testit kellonajan jäsennykselle** (`10-2`). Kirjoita funktiolle
   `minuutteina` testit: tunnettu tulos, rajatapaukset ja virheelliset
   syötteet (`pytest.raises`).

## Käytännössä

- **Testaa funktioita, älä tulosteita.** Laskevat funktiot, jotka
  palauttavat arvon (luku *Funktiot*), on helppo testata. Siksi
  esimerkin `main` on ohut, ja logiikka on modulissa `viite`.
- **Testin nimi kertoo, mitä vaaditaan.**
  `test_tarkiste_nolla_kun_summa_tasakymmenia` dokumentoi säännön;
  `test_3` ei kerro mitään.
- **Yksi asia testiä kohden** ja rakenne *järjestä–toimi–tarkista*
  (*arrange–act–assert*): alkuarvot, kutsu ja tarkistus.
- **Testien on oltava nopeita ja toistettavia.** Ei riippuvuutta
  kellonajasta, satunnaisuudesta, verkosta tai testien
  suoritusjärjestyksestä.
- **Aja testit jokaisen muutoksen jälkeen** ja ennen kuin jaat koodin
  muille. Versionhallinnan ja jatkuvan integraation (CI) yhteydessä
  palvelin ajaa ne automaattisesti (taito *Käännösjärjestelmät,
  testaus ja CI*).

## Itsearviointi

- Osaat kirjoittaa pytest-testin ja ajaa sen.
- Osaat testata saman funktion usealla syötteellä parametrisoinnilla
  ja tarkistaa, että virheellinen syöte nostaa poikkeuksen.
- Osaat valita testitapaukset järjestelmällisesti: tunnetut
  tulokset, rajatapaukset ja virheelliset syötteet.
- Osaat kuvata testit ensin -työtavan ja sen hyödyt.
- Osaat arvioida testijoukon kattavuutta kysymällä, mikä virheellinen
  toteutus pääsisi testeistä läpi.

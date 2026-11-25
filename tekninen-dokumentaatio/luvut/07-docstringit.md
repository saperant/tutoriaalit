# Rajapintadokumentaatio koodista

Viite on dokumentaation osa, jonka pitää olla täsmälleen oikein, ja
juuri siksi se kirjoitetaan koodiin. Kuvaus funktion vieressä näkyy
muokkaimessa, kulkee katselmoinnin läpi koodin kanssa ja päätyy
generoituun viitteeseen ilman kopiointia.

## Mitä kuvaukseen kuuluu

Funktion kuvaus on sopimus kutsujan kanssa. Kutsuja ei lue toteutusta,
joten kuvauksen pitää kertoa kaikki, mitä hän tarvitsee:

- mitä funktio tekee, yhdellä virkkeellä
- parametrit: merkitys, yksikkö ja sallitut arvot
- paluuarvo, myös erikoistapaukset (tyhjä syöte, ei tulosta)
- virheet: mitä poikkeuksia tai virhekoodeja ja milloin
- sivuvaikutukset, säieturvallisuus ja omistajuus, jos niitä on
- esimerkki

Esimerkkikirjaston jäsennysfunktio:

```{.python tiedosto="esimerkit/saa/lukema.py" osa="jasenna"}
```

Kuvaus ei toista sitä, minkä koodi jo sanoo. Tyyppi on allekirjoituksen
tyyppivihjeissä, joten sitä ei kirjoiteta uudelleen; työkalu näyttää
sen viitteessä. Kuvaus kertoo sen, mitä tyyppi ei kerro: että aika
vaatii aikavyöhykkeen ja että kosteus saa puuttua.

## Miksi, ei mitä

Kommentti, joka kertoo saman kuin koodi (”kasvattaa laskuria
yhdellä”), on kohinaa. Hyödyllinen kommentti kertoo sen, mitä koodista
ei voi lukea: miksi ratkaisu on tämä eikä ilmeisempi.

```{.python tiedosto="esimerkit/saa/tilasto.py" osa="keskiarvo"}
```

Toinen kappale perustelee, miksi vajaita ikkunoita ei lasketa. Ilman
sitä seuraava kehittäjä ”korjaa” puutteen, ja kuvaajiin palaa häiriö,
jonka takia ratkaisu alun perin tehtiin. Pidempi perustelu kuuluu
selitykseen (luku 2) tai päätöslokiin (luku 10), ja kuvaus viittaa
sinne.

Julkisen rajapinnan kuvaus ja toteutuksen kommentti ovat eri asioita.
Kuvaus on kutsujalle ja kertoo sopimuksen. Kommentti on ylläpitäjälle
ja kertoo, miksi toteutus on tällainen. Yksityinen apufunktio ei
tarvitse viitesivua.

## Docstringien tyylit

Pythonissa kuvaus on *docstring*, funktion ensimmäinen merkkijono.
Sen rakenteelle on kolme yleistä tyyliä:

| Tyyli | Osiot | Tunnistaa | Käyttö |
|--------------|----------------------------|-------------------|--------------------|
| Google | `Args:`, `Returns:`, `Raises:` | sisennetyt osiot | yleiskäyttö, tiivis |
| NumPy | `Parameters`, `Returns`, alleviivattu | alleviivatut otsikot | tieteellinen laskenta |
| Sphinx (reST) | `:param x:`, `:returns:` | kenttäluettelo | vanhempi Sphinx-koodi |

Tämä tutoriaali käyttää Googlen tyyliä. Tyylillä on vähemmän väliä
kuin johdonmukaisuudella: työkalu, joka tarkistaa tai generoi, pitää
asettaa samalle tyylille kuin koodi. Esimerkeissä tarkistin on ruff,
jonka säännöstö `D` vaatii docstringin jokaiselta julkiselta nimeltä ja
tarkistaa sen muodon.

Luokan kentät kuvataan osiossa `Attributes`:

```{.python tiedosto="esimerkit/saa/lukema.py" osa="lukema"}
```

## Esimerkit docstringissä

Docstringin `>>>`-rivit ovat tulkin istunto. Moduuli `doctest` ajaa
ne ja vertaa tulostetta seuraaviin riveihin; pytest tekee saman
valitsimella `--doctest-modules`. Funktion `jasenna_rivi` esimerkki
näyttää sekä onnistuneen kutsun että virheen, ja molemmat ajetaan
jokaisessa testiajossa.

Docstringin esimerkki on dokumentaatiota, ei testisarja. Yksi tai kaksi
tyypillistä tapausta riittää; reunatapaukset kuuluvat yksikkötesteihin,
joissa niitä ei tarvitse muotoilla luettavaksi.

## Kattavuus ja ajautuminen

Kaksi asiaa menee docstringeissä vikaan: kuvaus puuttuu, tai se kuvaa
funktiota sellaisena kuin se ennen oli. Jälkimmäinen on yleisempi ja
pahempi. Tässä parametri on nimetty uudelleen ja toinen lisätty, mutta
kuvaus on ennallaan:

```{.python tiedosto="esimerkit/naytteet/ajautunut.py"}
```

Tyyppitarkistin ei huomaa mitään, koska koodi on oikein. Esimerkkien
tarkistin lukee lähdekoodin syntaksipuun ja vertaa `Args:`-osion
nimiä funktion parametreihin:

```{.python tiedosto="esimerkit/tyokalut/kattavuus.py" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/naytteet/ajautunut.odotettu"}
```

Kirjasto itse läpäisee tarkistuksen:

```{.tuloste tiedosto="esimerkit/saa.kattavuus.odotettu"}
```

Valmiita työkaluja samaan ovat interrogate (kattavuus) ja pydoclint
(parametrien vastaavuus). Kattavuusluku on
huono tavoite sellaisenaan: sen saa sataan kirjoittamalla jokaiseen
funktioon sen nimen uudelleen. Hyödyllinen se on vahtina, joka estää
dokumentoimattoman julkisen funktion pääsyn päähaaraan.

## Käytännössä

- **Kirjoita kuvaus ennen toteutusta.** Jos funktion tehtävää ei saa
  sanottua yhdellä virkkeellä, funktio tekee liikaa.
- **Kuvaa sopimus, älä toteutusta.** ”Käy listan läpi silmukassa” on
  toteutus; ”palauttaa tyhjän listan, jos arvoja on liian vähän” on
  sopimus.
- **Yksiköt nimiin tai kuvaukseen.** `lampotila_c` ei tarvitse
  selitystä; `aikakatkaisu` tarvitsee.
- **Virheet ovat osa rajapintaa.** Kutsujan pitää tietää, mihin
  varautua, lukematta toteutusta.
- **Julkinen rajapinta on pieni.** Jokainen julkinen nimi pitää
  dokumentoida ja pitää vakaana. Alaviiva nimen alussa on halvin
  dokumentaatio.
- **Päivitä kuvaus samassa muutoksessa.** Katselmoija lukee erotuksesta
  myös kommenttien rivit.

## Itsearviointi

- Osaat kirjoittaa funktiolle kuvauksen, joka kertoo parametrit,
  paluuarvon, virheet ja esimerkin.
- Osaat erottaa kommentin, joka toistaa koodin, kommentista, joka
  perustelee ratkaisun.
- Osaat ajaa docstringien esimerkit testeinä.
- Osaat selittää, miten kuvaus ajautuu koodista ja miten ajautuminen
  havaitaan koneellisesti.

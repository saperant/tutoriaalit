# Resurssit ja muisti

Pelin *resursseja* (assets) ovat tekstuurit, äänet, mallit, tasot ja
pelin arvot (vihollisten kestot, aseiden vahingot). Ne ladataan
levyltä, jaetaan monen käyttäjän kesken ja vapautetaan, kun taso
vaihtuu. Samalla pelin aikainen muistinhallinta on suunniteltava niin,
että ruudun aikana ei varata eikä vapauteta muistia hallitsemattomasti.

## Kahvat osoittimien sijaan

Jos sprite pitää osoitinta tekstuuriin ja tekstuuri vapautetaan tason
vaihtuessa, osoitin jää roikkumaan. *Kahva* (handle) on indeksi ja
sukupolvi, ja jokainen käyttö tarkistaa, onko resurssi yhä sama.

```{.cpp tiedosto="esimerkit/10-kahvat.cpp" osa="kahva"}
```

```{.cpp tiedosto="esimerkit/10-kahvat.cpp" osa="vanheneminen"}
```

```{.tuloste tiedosto="esimerkit/10-kahvat.odotettu"}
```

Uusi tekstuuri sai saman paikan, mutta vanha kahva ei osoita siihen.
Kahvoilla on muitakin etuja: ne ovat pieniä, ne voi tallentaa ja
sarjallistaa, ja varasto voi siirtää resursseja muistissa
(defragmentointi, suoratoisto) rikkomatta viittauksia.

## Objektipooli

Ammuksia, partikkeleita ja ääniä syntyy ja katoaa jatkuvasti. Jos
jokainen varataan keosta, varauksia on satoja sekunnissa, keko
pirstoutuu ja yksittäinen varaus voi kestää arvaamattoman kauan.
*Objektipooli* varaa kiinteän määrän olioita kerran ja kierrättää niitä
vapaiden listan avulla.

```{.cpp tiedosto="esimerkit/10-pooli.cpp" osa="pooli"}
```

```{.cpp tiedosto="esimerkit/10-pooli.cpp" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/10-pooli.odotettu"}
```

Esimerkki laskee varaukset korvaamalla globaalin `operator new`n.
Sama tekniikka sopii kehitysversioon: varaus pelisilmukassa kirjataan
ja korjataan. Täyden poolin käsittely on pelisuunnittelun päätös:
uusi ammus voi jäädä syntymättä, tai vanhin ammus poistetaan.

## Välimuisti ja kuumalataus

Resurssivälimuisti lataa saman tiedoston vain kerran ja jakaa sen
käyttäjille. *Kuumalataus* (hot reload) lataa muuttuneen tiedoston
uudelleen pelin ollessa käynnissä, jolloin suunnittelija näkee
muutoksen heti ilman pelin uudelleenkäynnistystä.

```{.cpp tiedosto="esimerkit/10-valimuisti.cpp" osa="valimuisti"}
```

```{.tuloste tiedosto="esimerkit/10-valimuisti.odotettu"}
```

Muutos päivitetään paikallaan, joten olemassa olevat viittaukset näkevät
uuden arvon. Tiedostojärjestelmän aikaleiman tarkkuus voi olla sekunti,
joten tuotantotyökalut seuraavat muutoksia käyttöjärjestelmän
ilmoituksilla (inotify, ReadDirectoryChangesW) tai sisällön
tiivisteellä.

## Tallennus

Pelitilanteen tallennus on resurssien lataamisen peilikuva: pelin tila
kirjoitetaan tiedostoksi ja luetaan myöhemmin takaisin, mahdollisesti
pelin uudemmalla versiolla. Tallennetaan vain se, mitä ei voi johtaa
muusta: taso, pisteet ja pelaajan paikka, ei ladattuja kuvia eikä
osoittimia.

```{.cpp tiedosto="esimerkit/10-tallennus.cpp" osa="tila"}
```

```{.cpp tiedosto="esimerkit/10-tallennus.cpp" osa="tavut"}
```

Tiedoston alussa on otsake: tunniste, versio, sisällön pituus ja
tarkistussumma.

```{.cpp tiedosto="esimerkit/10-tallennus.cpp" osa="tallenna"}
```

Lataus tarkistaa otsakkeen ennen kuin se uskoo yhtäkään kenttää, ja
palauttaa joko tilanteen tai syyn hylkäykseen. Versio kertoo, mitkä
kentät tiedostossa on: vanhasta tiedostosta puuttuva kenttä saa
oletusarvon.

```{.cpp tiedosto="esimerkit/10-tallennus.cpp" osa="lataa"}
```

```{.tuloste tiedosto="esimerkit/10-tallennus.odotettu"}
```

Yhden bitin muutos ja kesken jäänyt kirjoitus havaitaan, vanha versio
latautuu ja tulevaisuuden versio hylätään siististi. Tarkistussumma
suojaa vahingoilta, ei muokkaukselta: pelaaja voi laskea summan
uudelleen. Verkkopelissä tärkeä tila pidetään siksi palvelimella.

## Käytännössä

- **Tallenna turvallisesti:** kirjoita ensin väliaikaiseen tiedostoon
  ja nimeä se vasta lopuksi oikeaksi. Jos peli kaatuu tai virta katkeaa
  kesken kirjoituksen, edellinen tallennus säilyy.
- **Kahvat** (generational handles) resurssi- ja entiteettiviittauksiin;
  `std::shared_ptr` vain, kun omistajuus todella jaetaan.
- **Objektipooli** usein syntyville ja katoaville olioille. Varaa
  pelisilmukan ulkopuolella: tason latauksessa, ei ruudun aikana.
- **Areena tai pinovaraaja** ruudun väliaikaisille tiedoille: kaikki
  vapautetaan kerralla ruudun lopussa.
- **Data tiedostoihin.** Pelin arvot (kestot, nopeudet, pudotustaulukot)
  kuuluvat tiedostoihin, joita suunnittelija muokkaa, ja kuumalataus
  tekee iteroinnista nopeaa.
- **Resurssien käsittelyputki:** julkaisuversiossa resurssit esikäsitellään
  (pakkaus, atlakset, mipmapit) ja paketoidaan, jotta lataus on nopeaa.

## Itsearviointi

- Osaat toteuttaa kahvavaraston, joka havaitsee vapautettuun resurssiin
  viittaavan kahvan.
- Osaat toteuttaa objektipoolin ja perustella, miksi pelisilmukassa
  vältetään keon varauksia.
- Osaat toteuttaa resurssivälimuistin ja kuumalatauksen niin, että
  olemassa olevat viittaukset pysyvät voimassa.
- Osaat suunnitella tallennustiedoston, jossa on versio ja
  tarkistussumma, ja ladata vanhan version tiedoston.

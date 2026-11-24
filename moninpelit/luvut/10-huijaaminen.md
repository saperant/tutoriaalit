# Auktoriteetti ja huijaamisen esto

Asiakasohjelma on pelaajan koneella, ja pelaaja voi muuttaa sitä:
lukea muistia, muokata paketteja, ajaa nopeammin tai korvata sen
kokonaan omalla. Huijaamisen esto alkaa arkkitehtuurista, ei
huijauksentunnistusohjelmista: palvelin ei usko mitään, minkä se voi
itse laskea, eikä kerro mitään, mitä pelaaja ei saa tietää.

## Aikeet, ei lopputuloksia

Kun asiakas lähettää sijaintinsa, palvelin joutuu joko uskomaan sen tai
arvaamaan, onko se mahdollinen. Kun asiakas lähettää syötteen ("liiku
oikealle"), palvelin laskee sijainnin itse eikä mahdottomia sijainteja
synny. Syötteetkin on silti tarkistettava: suuntavektorin pituus,
syötteiden määrä aikayksikössä ja toimintojen ehdot (onko aseessa
ammuksia, onko kyky latautunut).

```{.cpp tiedosto="esimerkit/10-validointi.cpp" osa="tarkistus"}
```

```{.cpp tiedosto="esimerkit/10-validointi.cpp" osa="palvelin"}
```

```{.tuloste tiedosto="esimerkit/10-validointi.odotettu"}
```

Jos asiakas päättää sijainnistaan, teleporttaaja on maalissa
ensimmäisellä tikillä ja nopeushuijari kulkee kolminkertaisesti.
Palvelimen päättäessä kaikki liikkuvat korkeintaan sallittua
nopeutta. Syötebudjetti (merkkiämpäri) sallii pienen purskeen verkon
värinän takia mutta ei jatkuvaa ylitystä, ja hylätyt syötteet
kirjataan: ne ovat todiste, jota huijauksen tunnistus voi käyttää.

## Tiedon rajaaminen

Seinän läpi näkevä huijaus (wallhack) ja tutkahuijaus näyttävät
tietoa, jonka asiakas on saanut mutta jota peli ei piirrä. Ainoa varma
torjunta on jättää tieto lähettämättä. Palvelin laskee jokaiselle
pelaajalle, mitkä vastustajat ovat näkyvissä tai kuuluvissa, ja
lähettää vain ne:

```{.cpp tiedosto="esimerkit/10-nakyvyys.cpp" osa="nakyvyys"}
```

```{.cpp tiedosto="esimerkit/10-nakyvyys.cpp" osa="suodatus"}
```

```{.tuloste tiedosto="esimerkit/10-nakyvyys.odotettu"}
```

Pelaaja *P* saa tiedon kolmesta vastustajasta kuudesta. Kolme muuta
(kysymysmerkit) eivät koskaan kulje verkossa, joten mikään asiakkaan
muokkaus ei paljasta niitä. Käytännössä näkyvyys lasketaan
hieman väljemmin (konservatiivisesti), jotta vastustaja ei ilmesty
tyhjästä kulman takaa viiveen takia: palvelin lähettää vastustajan
juuri ennen kuin tämä tulee näkyviin.

## Muut huijaukset ja torjunta

- **Tähtäysapu** (aimbot) käyttää samaa tietoa kuin pelaaja, joten sitä
  ei voi estää arkkitehtuurilla. Se tunnistetaan tilastoista
  (epäinhimillinen reaktioaika, tähtäyksen tarkkuus) ja palvelimen
  näkemästä syötteestä.
- **Pakettien manipulointi**: kaikki asiakkaan viestit ovat
  epäluotettavaa syötettä. Tarkista rajat, tyypit ja tila (vrt. taito
  *Tietoturvan perusteet*).
- **Viiveen väärentäminen**: huijari viivästää omia pakettejaan
  hyötyäkseen kompensoinnista. Kelauksen yläraja (luku *Viiveen
  kompensointi*) rajaa hyödyn.
- **Asiakkaan eheys**: huijauksentunnistusohjelmat (anti-cheat)
  tarkistavat muistin ja prosessit. Ne nostavat huijaamisen kynnystä
  mutta ovat kilpajuoksua, eivät korvaa palvelimen auktoriteettia.
- **Taloudelliset huijaukset** (tavaroiden monistus, kaupan
  kilpailutilanteet) torjutaan palvelimen transaktioilla, kuten
  taustapalveluissa.

## Käytännössä

- **Älä luota asiakkaaseen missään, millä on väliä.** Sijainnit, osumat,
  vahinko, tavarat ja pisteet lasketaan palvelimella.
- **Lähetä vain tarpeellinen.** Kiinnostusalue on sekä kaistan säästö
  että huijaamisen esto.
- **Kirjaa epäilyttävä toiminta** (hylätyt syötteet, rajojen ylitykset)
  ja käsittele se taustalla tilastollisesti. Välitön porttikielto
  opettaa huijarille, mikä paljastui.
- **Tasapainota tuntuman kanssa.** Liian tiukka tarkistus hylkää
  rehellisen pelaajan syötteitä huonolla yhteydellä.
- **Hinta:** palvelimen auktoriteetti vaatii palvelimen, joka simuloi
  kaiken; näkyvyyden laskenta maksaa laskentaa pelaajaa kohti.

## Itsearviointi

- Osaat perustella, miksi asiakas lähettää syötteitä eikä sijainteja,
  ja toteuttaa syötteiden tarkistuksen ja määrän rajoituksen.
- Osaat toteuttaa näkyvyyteen perustuvan tiedon rajaamisen.
- Osaat luetella yleiset huijaukset ja niiden torjunnan rajat.

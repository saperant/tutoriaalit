# Tekstimuotojen jäsentäminen

Työkalujen syötteet ovat useimmiten tekstiä: simulaattorien ja
synteesityökalujen lokeja, raportteja, taulukoita ja asetustiedostoja.
Jäsentämisen tavoite on muuttaa teksti mahdollisimman aikaisin
tyypitetyiksi olioiksi. Muu ohjelma käsittelee olioita eikä
merkkijonoja, joten muodon muutos rikkoo vain jäsentimen.

## Säännölliset lausekkeet

UVM-testipenkin lokirivissä on taso, lähdetiedosto ja rivi, aika
yksikköineen, komponentin polku, viestin tunniste ja teksti:

```{.text tiedosto="esimerkit/04-loki.syote"}
```

Pitkä lauseke kirjoitetaan `re.VERBOSE`-tilassa: välilyönnit ja
kommentit ohitetaan, joten osat voi kommentoida riveittäin.
*Nimetyt ryhmät* (`(?P<nimi>...)`) tekevät tuloksesta luettavan:
`m["aika"]` eikä `m.group(4)`:

```{.python tiedosto="esimerkit/04-loki.py" osa="lauseke"}
```

Lauseke käännetään kerran moduulin tasolla. Jäsennin muuntaa
osumasta olion ja aikayksikön nanosekunneiksi:

```{.python tiedosto="esimerkit/04-loki.py" osa="jasenna"}
```

```{.tuloste tiedosto="esimerkit/04-loki.odotettu"}
```

Jäsennin laskee myös tunnistamattomat rivit. Kun lokin muoto muuttuu
(uusi simulaattoriversio), luku kasvaa ja muutos huomataan, eikä
jäsennin hiljaa ohita kaikkea.

Säännöllisten lausekkeiden sudenkuopat:

- **`match` vai `search` vai `fullmatch`.** `match` sitoo alkuun,
  `fullmatch` koko merkkijonoon, `search` etsii mistä tahansa.
  Validoinnissa käytetään `fullmatch`ia, muuten `"100MHzX"` kelpaa.
- **Ahne `.*`** nielaisee niin paljon kuin voi. Rajaa merkkiluokalla
  (`[^\]]+`) tai laiskalla `.*?`.
- **Katastrofinen paluuhaku.** Sisäkkäiset toistot (`(a+)+`) voivat
  viedä eksponentiaalisen ajan, kun osumaa ei löydy. Pidä lausekkeet
  yksiselitteisinä.
- **Raakamerkkijono** `r"..."` aina, muuten `\d` ja `\b` tulkitaan
  Pythonin merkkijonon koodinvaihtomerkkeinä.

## Tilakone monirivisille lohkoille

Ajoitusanalyysin raportissa yksi polku on usean rivin lohko. Kentät
ovat eri riveillä, ja niiden välissä on rivejä, joista ei tarvita
mitään:

```{.text tiedosto="esimerkit/04-ajoitus.syote"}
```

Yksi lauseke ei sovi tähän. Jäsennin käy rivit läpi kerran ja muistaa
tilan: polkujen välissä vai polun sisällä. Jokainen polku tuotetaan
generaattorista heti, kun sen viimeinen kenttä (`slack`) on luettu,
joten muisti ei kasva raportin koon mukana:

```{.python tiedosto="esimerkit/04-ajoitus.py" osa="tilakone"}
```

```{.dot otsikko="Jäsentimen tilat ja siirtymät. Rivi luokitellaan säännöllisillä lausekkeilla, ja tila päättää, mitä rivillä tehdään. Katkoviiva on virhe: polku jäi kesken."}
digraph {
  rankdir=LR; nodesep=0.45; ranksep=0.85;
  alku [shape=point, width=0.08];
  valissa [label="VALISSA\npolkujen välissä"];
  polussa [label="POLUSSA\npolun sisällä"];
  valmis [label="valmis", shape=plain, style=""];
  virhe [label="ValueError", shape=plain, style=""];
  alku -> valissa;
  valissa -> polussa [label="Startpoint"];
  polussa -> valissa [label="slack:\ntuota Polku"];
  valissa -> valissa [label="muu rivi"];
  polussa -> polussa [label="muu kenttä:\ntallenna"];
  valissa -> valmis [label="syöte loppui"];
  polussa -> virhe [label="Startpoint tai\nsyöte loppui", style=dashed];
}
```

Rikkinäinen raportti, kuten kesken loppuva tiedosto tai polku ilman
slack-riviä, nostaa virheen rivinumeroineen. Hiljaisesti ohitettu
puolikas polku voisi kätkeä juuri pahimman ajoitusrikkeen.

```{.tuloste tiedosto="esimerkit/04-ajoitus.odotettu"}
```

WNS (*worst negative slack*) on pahin marginaali ja TNS (*total
negative slack*) rikkovien polkujen marginaalien summa. Taito
*FPGA-toteutus* käsittelee niiden merkityksen.

## CSV: rekisterikartta C-otsakkeeksi

Rekisterikartta on usein taulukko, jota laitteistosuunnittelija
ylläpitää. Ohjelmisto tarvitsee siitä vakiot, ja generoitu otsake
pysyy samana kuin kartta:

```{.text tiedosto="esimerkit/04-rekisterikartta.syote"}
```

`csv.DictReader` käsittelee lainausmerkit ja erottimet oikein, mitä
`split(",")` ei tee. Generaattori tarkistaa koko kartan ennen kuin
kirjoittaa mitään: osoitteiden kohdistus, päällekkäiset osoitteet ja
bitit, bittialueet ja pääsytyypit:

```{.python tiedosto="esimerkit/04-rekisterikartta.py" osa="luku"}
```

```{.python tiedosto="esimerkit/04-rekisterikartta.py" osa="otsake"}
```

Kaikki virheet kerätään ja raportoidaan kerralla. Käyttäjä korjaa ne
yhdellä kierroksella eikä yksi kerrallaan.

```{.tuloste tiedosto="esimerkit/04-rekisterikartta.odotettu"}
```

## TOML, INI ja JSON

Asetustiedostot luetaan tyypitetyiksi olioiksi ohjelman reunalla.
TOML on uusien työkalujen suositeltu muoto, koska siinä on tyypit
(luku, merkkijono, lista, taulukko) ja se on yksiselitteinen:

```{.toml tiedosto="esimerkit/04-asetukset.toml"}
```

Vanhoissa työkaluissa käytetään usein INI-muotoa, jossa kaikki arvot
ovat merkkijonoja:

```{.ini tiedosto="esimerkit/04-vanha.ini"}
```

Molemmat muunnetaan samoiksi tietoluokiksi, jotka tarkistavat
itsensä luonnissa (`__post_init__`):

```{.python tiedosto="esimerkit/04-asetukset.py" osa="mallit"}
```

`tomllib` on vakiokirjastossa (Python 3.11+) ja lukee tiedoston
binääritilassa. Se vain lukee. Kirjoittamiseen tarvitaan kolmannen
osapuolen `tomli-w`:

```{.python tiedosto="esimerkit/04-asetukset.py" osa="toml"}
```

INI-tiedoston arvot muunnetaan itse. `getint` tekee sen ja kertoo
virheellisestä arvosta:

```{.python tiedosto="esimerkit/04-asetukset.py" osa="ini"}
```

```{.tuloste tiedosto="esimerkit/04-asetukset.odotettu"}
```

JSON on koneiden välinen muoto. `ensure_ascii=False` säilyttää
ääkköset luettavina, ja `sort_keys=True` tekee tulosteesta
deterministisen, kun avainten järjestys ei ole merkityksellinen.
Tulosvirroille sopii *JSON Lines*: yksi JSON-objekti riviä kohden,
jolloin tiedostoon voi lisätä rivejä ja sen voi lukea rivi kerrallaan.
Luvun *Testaus* raporttityökalu lukee tällaista tiedostoa.

## Käytännössä

- **Jäsennä reunalla tyypitetyiksi olioiksi** (*parse, don't
  validate*). Sanakirja, jonka avaimia luetaan ympäri ohjelmaa, levittää
  muodon tuntemuksen kaikkialle.
- **Ole tiukka syötteessä, laske tuntemattomat.** Ohitetut rivit
  lasketaan ja raportoidaan. Hiljaa ohitettu muodon muutos on pahin
  virhe, koska raportti näyttää puhtaalta.
- **Valmis jäsennin ennen omaa.** `csv`, `json`, `tomllib`,
  `configparser`, `xml.etree` ja `email` käsittelevät lainaukset ja
  erikoistapaukset, joita oma `split` ei tunne.
- **Generoidun tiedoston alussa varoitus** ("älä muokkaa käsin") ja
  mieluiten lähde. Generointi kuuluu käännösjärjestelmään, jotta
  otsake ei vanhene.
- **Tiedostot tekstitilassa aina `encoding="utf-8"`.** Oletus riippuu
  lokaalista, ja sama skripti toimii eri tavalla eri koneilla.
  Lokeissa voi olla rikkinäisiä tavuja: `errors="replace"` estää
  kaatumisen.

## Itsearviointi

- Osaat kirjoittaa kommentoidun säännöllisen lausekkeen nimetyillä
  ryhmillä ja valita `match`in, `search`in ja `fullmatch`in välillä.
- Osaat jäsentää monirivisiä lohkoja tilakoneella, joka huomaa
  keskeneräisen lohkon.
- Osaat lukea CSV:n `DictReader`illa ja tarkistaa koko syötteen ennen
  tulosteen kirjoittamista.
- Osaat lukea TOML- ja INI-asetukset tietoluokiksi, jotka tarkistavat
  itsensä.

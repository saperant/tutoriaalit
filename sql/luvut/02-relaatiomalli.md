# Relaatiomalli ja normalisointi

Relaatiomallissa tieto on tauluissa. Taulun rivi kuvaa yhtä asiaa,
kuten asiakasta tai tilausta, ja sarake yhtä sen ominaisuutta. Taulu on
rivien *joukko*: riveillä ei ole järjestystä, ja kaksi täysin samaa
riviä on mallin kannalta virhe. Siksi jokaisella taululla on
*pääavain*, joka yksilöi rivin.

Taulujen väliset yhteydet ilmaistaan *viiteavaimilla*: tilausrivillä
on tilauksen tunniste, ei kopiota tilauksen tiedoista. Yhteyksiä on
kolmea lajia:

- **1–1**: harvinainen; usein merkki siitä, että kaksi taulua voisi
  yhdistää, tai tapa erottaa harvoin käytetyt sarakkeet.
- **1–N**: asiakkaalla on monta tilausta. Viiteavain on N-puolella
  (`tilaus.asiakas_id`).
- **N–M**: tuotteella on monta tunnistetta ja tunnisteella monta
  tuotetta. Yhteys toteutetaan *välitaululla*.

## Miksi normalisoidaan

Taulukkolaskentaan tottunut kehittäjä tallentaisi tilaukset helposti
yhteen tauluun:

```{.sql tiedosto="esimerkit/02-normalisoimaton.sql" osa="taulu"}
```

Rakenne johtaa *anomalioihin*. Esimerkki muuttaa yhden rivin
`UPDATE`-lauseella; muutoslauseet käsitellään luvussa 10:

```{.sql tiedosto="esimerkit/02-normalisoimaton.sql" osa="anomalia"}
```

```{.tuloste tiedosto="esimerkit/02-normalisoimaton.odotettu"}
```

- **Päivitysanomalia**: sama tieto on monessa rivissä, ja päivitys,
  joka ei osu kaikkiin, jättää kannan ristiriitaiseksi. Nyt Ainolla on
  kaksi sähköpostiosoitetta.
- **Lisäysanomalia**: asiakasta ei voi tallentaa ennen ensimmäistä
  tilausta.
- **Poistoanomalia**: viimeisen tilauksen poisto hävittää asiakkaan.
- **Moniarvoinen sarake**: `LIKE '%Kahvi%'` osuu myös kahvimyllyyn, eikä
  tuotteilla voi olla määriä, hintoja tai viiteavaimia.

*Normalisointi* poistaa toisteen jakamalla tiedot tauluihin niin, että
jokainen tosiasia tallennetaan yhteen paikkaan. Normaalimuodot ovat
tämän periaatteen porrastus:

1. **1NF**: jokainen sarake sisältää yhden arvon, ei listaa.
2. **2NF**: jokainen sarake riippuu *koko* pääavaimesta. Tilausrivin
   avain on (tilaus, tuote); tuotteen nimi riippuu vain tuotteesta,
   joten se kuuluu tuotetauluun.
3. **3NF**: sarake ei riipu toisesta avaimettomasta sarakkeesta.
   Asiakkaan sähköposti riippuu asiakkaasta, ei tilauksesta.

Muistisääntö: sarake riippuu avaimesta, koko avaimesta eikä mistään
muusta kuin avaimesta. Käytännössä 3NF riittää; korkeammat
normaalimuodot koskevat harvinaisia moniarvoisia riippuvuuksia.

## Verkkokaupan skeema

Tutoriaalin tietomalli on normalisoitu verkkokauppa:

```{.sql tiedosto="esimerkit/02-skeema.sql" osa="skeema"}
```

Taulut ja niiden yhteydet kuvana (*ER-kaavio*). Alleviivatut
sarakkeet muodostavat pääavaimen, ja haarautuva pää on yhteyden
N-puoli:

```{.dot otsikko="Verkkokaupan taulut. Asiakkaalla on monta tilausta ja tilauksella monta riviä; tilausrivi yhdistää tilauksen ja tuotteen."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=1.1;
  node [shape=plain, style=""];
  edge [arrowhead=crow, arrowtail=tee, dir=both];
  asiakas [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#F3E5DC"><b>asiakas</b></td></tr>
    <tr><td align="left" port="id"><u>id</u></td></tr>
    <tr><td align="left">nimi</td></tr>
    <tr><td align="left">kaupunki</td></tr></table>>];
  tilaus [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#F3E5DC"><b>tilaus</b></td></tr>
    <tr><td align="left" port="id"><u>id</u></td></tr>
    <tr><td align="left" port="asiakas_id">asiakas_id</td></tr>
    <tr><td align="left">paiva</td></tr></table>>];
  tilausrivi [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#F3E5DC"><b>tilausrivi</b></td></tr>
    <tr><td align="left" port="tilaus_id"><u>tilaus_id</u></td></tr>
    <tr><td align="left" port="tuote_id"><u>tuote_id</u></td></tr>
    <tr><td align="left">maara</td></tr></table>>];
  tuote [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td bgcolor="#F3E5DC"><b>tuote</b></td></tr>
    <tr><td align="left" port="id"><u>id</u></td></tr>
    <tr><td align="left">nimi</td></tr>
    <tr><td align="left">kategoria</td></tr>
    <tr><td align="left">hinta_snt</td></tr></table>>];
  asiakas:id:e -> tilaus:asiakas_id:w;
  tilaus:id:e -> tilausrivi:tilaus_id:w;
  tuote:id:e -> tilausrivi:tuote_id:w;
}
```

Ratkaisut ja niiden perustelut:

- **`INTEGER PRIMARY KEY`** on SQLitessä rivin sisäisen tunnisteen
  (*rowid*) alias: arvo annetaan automaattisesti, ja haku sillä on
  nopein mahdollinen. PostgreSQL:ssä vastaava on
  `id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY`.
- **Sijaisavaimet** (`id`) yksilöivät rivit, vaikka luonnollinen avain,
  kuten tuotteen nimi, muuttuisi. Luonnollinen avain pidetään silti
  yksikäsitteisenä rajoitteella `UNIQUE`.
- **Rahasummat ovat kokonaislukuja senteissä** (`hinta_snt`).
  Liukuluku ei esitä lukua 0,1 tarkasti, ja pyöristysvirheet kertyvät
  summiin. PostgreSQL:ssä voi käyttää myös tyyppiä `numeric(12,2)`.
- **Päivämäärät ovat ISO 8601 -tekstiä** (`2026-10-15`), koska
  SQLitessä ei ole päivämäärätyyppiä. Rajoite
  `CHECK (paiva = date(paiva))` hylkää kelvottomat arvot (luku 9).
- **Tilausrivin pääavain on yhdistelmä** `(tilaus_id, tuote_id)`: sama
  tuote voi olla tilauksessa vain kerran, ja määrä on omassa
  sarakkeessaan.
- **`NOT NULL` on oletus**; vain asiakkaan kaupunki saa puuttua.

Data lisätään tavallisilla `INSERT`-lauseilla:

```{.sql tiedosto="esimerkit/02-skeema.sql" osa="data"}
```

```{.sql tiedosto="esimerkit/02-skeema.sql" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/02-skeema.odotettu"}
```

Malli on tarkoituksella yksinkertaistettu. Tuotantojärjestelmässä
tilausrivi tallentaa myös yksikköhinnan tilaushetkellä: tuotteen hinta
muuttuu, mutta vanhan tilauksen summa ei saa muuttua. Tämä ei ole
toistoa vaan eri tosiasia, *hinta tilaushetkellä*. Normalisointi koskee
samaa tosiasiaa, ei samannäköisiä arvoja.

## Monesta moneen

Tuotteiden tunnisteet tarvitsevat välitaulun, jonka pääavain on
viiteavainten pari:

```{.sql tiedosto="esimerkit/02-monesta-moneen.sql" osa="valitaulu"}
```

```{.sql tiedosto="esimerkit/02-monesta-moneen.sql" osa="kysely"}
```

```{.tuloste tiedosto="esimerkit/02-monesta-moneen.odotettu"}
```

Välitaululle voi lisätä yhteyden omia tietoja, kuten tunnisteen
lisäysajan. Liitokset käsitellään tarkemmin luvussa 5.

## Käytännössä

- **Normalisoi ensin, denormalisoi mitattuun tarpeeseen.**
  Normalisoitu malli on helppo pitää oikeana. Raportointia varten tehty
  toisto (yhteenvetotaulu, välimuisti) on perusteltua vasta, kun kysely
  on mitattu liian hitaaksi, ja silloin toiston ylläpito automatisoidaan
  (triggeri, materialisoitu näkymä, ajastettu päivitys).
- **Nimeämiskäytäntö** on yhtenäinen ja ennustettava: taulut
  yksikössä, sarakkeet `snake_case`-muodossa, viiteavaimet
  `<taulu>_id`. Yksikkö sarakkeen nimessä (`hinta_snt`, `kesto_ms`)
  estää yksikkövirheitä.
- **Sijaisavain ja yksikäsitteinen luonnollinen avain.** Pelkkä
  sijaisavain sallii saman tuotteen kahdesti; pelkkä luonnollinen avain
  tekee muutoksista kalliita, koska viittaukset on päivitettävä.
- **Rahat kokonaislukuina tai `numeric`-tyyppinä**, ei liukulukuina.
  Aikaleimat tallennetaan UTC-aikana ja muunnetaan paikalliseen aikaan
  vasta näytettäessä.
- **Sudenkuoppa: lista sarakkeessa** (pilkuilla erotetut tunnisteet,
  `tuote1`, `tuote2`, `tuote3`). Kyselyt, eheys ja indeksit hajoavat.
  Oikea ratkaisu on oma taulu.
- **Sudenkuoppa: EAV-malli** (*entity–attribute–value*), jossa kaikki
  tiedot ovat yhdessä taulussa muodossa (olio, attribuutti, arvo). Malli
  näyttää joustavalta mutta menettää tyypit, rajoitteet ja luettavat
  kyselyt. Aidosti vaihtelevat ominaisuudet sopivat paremmin
  JSON-sarakkeeseen kuin EAV-tauluun.

## Itsearviointi

- Osaat selittää pääavaimen, viiteavaimen ja välitaulun tehtävät.
- Osaat tunnistaa päivitys-, lisäys- ja poistoanomalian ja korjata ne
  normalisoimalla taulun kolmanteen normaalimuotoon.
- Osaat perustella, miksi rahasummat tallennetaan kokonaislukuina ja
  miksi tilausrivi tallentaa hinnan tilaushetkellä.
- Osaat valita sijaisavaimen ja luonnollisen avaimen välillä ja pitää
  luonnollisen avaimen yksikäsitteisenä.

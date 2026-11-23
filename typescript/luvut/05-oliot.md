# Oliotyypit ja luokat {.runko-omat-tyypit}

TypeScriptissä datan muoto kuvataan oliotyypeillä. Luokkia tarvitaan
harvemmin kuin Javassa tai C#:ssa, koska tavallinen olio kelpaa mihin
tahansa tyyppiin, jonka rakenne täsmää.

## interface ja type

```{.typescript tiedosto="esimerkit/05-oliotyypit.ts"}
```

```{.tuloste tiedosto="esimerkit/05-oliotyypit.odotettu"}
```

`interface` ja `type`-alias ovat oliotyypeille lähes vaihdettavissa.
Erot:

| | `interface` | `type` |
|-|-------------|--------|
| Oliotyypit | kyllä | kyllä |
| Unionit, monikot, primitiivit, kuvatut tyypit | ei | kyllä |
| Laajennus | `extends` (ristiriidat virheitä) | leikkaus `&` |
| Avoin täydennettäväksi (*declaration merging*) | kyllä | ei |

Nyrkkisääntö: `type` kaikkeen, `interface` kun tyyppiä on tarkoitus
laajentaa tai toteuttaa luokassa. Tärkeämpää kuin valinta on
johdonmukaisuus projektin sisällä.

- **Valinnainen kenttä** `sahkoposti?: string` voi puuttua kokonaan.
  `?? "oletus"` käsittelee puuttumisen.
- **`readonly`** estää sijoituksen kääntäjän tasolla, ei ajossa.
  `Object.freeze` estää muutoksen myös ajossa, ja `Readonly<T>`
  kuvaa jäädytetyn olion.
- **Indeksiallekirjoitus** `{ [tuote: string]: number }` kuvaa olion,
  jonka avaimet ovat dataa. Usein `Map` on parempi (luku 8).

## Ylimääräisten kenttien tarkistus

Rakenteellisessa tyypityksessä ylimääräiset kentät ovat sallittuja.
Poikkeus: kun *tuore olioliteraali* annetaan suoraan tyypitettyyn
paikkaan, tuntemattomat kentät ovat virheitä. Tarkistus löytää
kirjoitusvirheet valinnaisten kenttien nimissä:

```{.typescript tiedosto="esimerkit/05-ylimaaraiset.ei-kaanny.ts"}
```

```
05-ylimaaraiset.ei-kaanny.ts(8,34): error TS2561: Object literal may
  only specify known properties, but 'tumme' does not exist in type
  'Asetukset'. Did you mean to write 'tumma'?
```

```{.tuloste tiedosto="esimerkit/05-ylimaaraiset.odotettu"}
```

Sama kirjoitusvirhe muuttujan kautta menee läpi, ja tumma tila jää
hiljaa pois. Valinnaiset kentät ovat siksi riski: mitä vähemmän
pakollisia kenttiä, sitä useampi väärä olio kelpaa. Suosi pakollisia
kenttiä ja erillisiä tyyppejä eri tilanteisiin (luku 6).

## Luokat

Luokat ovat JavaScriptin luokkia tyyppimerkinnöin. TypeScript lisää
näkyvyysmääreet (`private`, `protected`, `public`), `readonly`-kentät,
`abstract`-luokat ja `implements`-tarkistuksen.

```{.typescript tiedosto="esimerkit/05-luokat.ts"}
```

```{.tuloste tiedosto="esimerkit/05-luokat.odotettu"}
```

- **`#saldo` vai `private saldo`?** `#`-kenttä on JavaScriptin aito
  yksityinen kenttä, johon ei pääse käsiksi ajossakaan. `private` on vain
  kääntäjän tarkistus. Uudessa koodissa käytä `#`-kenttiä; `private`
  sopii konstruktorille ja metodeille, joita halutaan rajata vain
  käännösaikana.
- **Tehdasmetodi** `static avaa` validoi syötteen ennen olion luomista.
  Yksityinen konstruktori pakottaa käyttämään sitä.
- **`implements` on vapaaehtoinen.** Se tarkistaa, että luokka täyttää
  rajapinnan, mutta mikä tahansa samanmuotoinen olio kelpaa myös
  (`vale`).

Parametriominaisuudet (`constructor(readonly nimi: string)`) eivät ole
poistettavaa syntaksia, koska ne tuottavat sijoituslauseet ajoon:

```{.typescript tiedosto="esimerkit/05-parametrit.ei-kaanny.ts"}
```

```
05-parametrit.ei-kaanny.ts(3,15): error TS1294: This syntax is not
  allowed when 'erasableSyntaxOnly' is enabled.
```

```{.tuloste tiedosto="esimerkit/05-parametrit.odotettu"}
```

## Käytännössä

- **Data tyyppeinä, käyttäytyminen funktioina.** Tavallinen olio ja
  sitä käsittelevät funktiot riittävät useimmiten. Luokka kannattaa, kun
  olio suojaa invarianttia (tili, välimuisti, yhteys) tai kun kirjasto
  odottaa luokkaa.
- **Invariantti yksityiseen tilaan.** `#`-kentät ja tehdasmetodi
  takaavat, ettei virheellistä oliota voi luoda. Muista, että
  rakenteellinen tyyppi `Tili` ei takaa mitään: kelvollisuuden takaa
  vain luokka itse tai brändätty tyyppi.
- **`readonly` oletuksena.** Muuttumattomat oliot ja kopiointi
  (`{ ...t, hinta }`) ovat TypeScript-koodin valtavirtaa; ne tekevät
  muutoksista näkyviä ja helpottavat Reactin kaltaisia kehyksiä.
- **Vältä laajoja valinnaisten kenttien tyyppejä.** Jos kenttä on
  olemassa vain tietyssä tilassa, käytä erotettua unionia.
- **Ei periytymishierarkioita.** Rakenteellinen tyypitys ja koostaminen
  tekevät syvät hierarkiat tarpeettomiksi; abstrakti kantaluokka
  tarvitaan harvoin.

## Itsearviointi

- Osaat valita `interface`n ja `type`-aliaksen välillä ja kuvata
  valinnaiset, `readonly`- ja indeksoidut kentät.
- Osaat selittää ylimääräisten kenttien tarkistuksen ja milloin se ei
  suojaa.
- Osaat kirjoittaa luokan, joka suojaa invarianttinsa `#`-kentillä ja
  tehdasmetodilla, ilman parametriominaisuuksia.
- Osaat perustella, milloin luokka on parempi kuin tyyppi ja funktiot.

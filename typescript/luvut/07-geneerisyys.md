# Geneerisyys ja tyyppien muuntaminen {.runko-omat-tyypit}

Geneerinen funktio tai tyyppi toimii monille tyypeille ja säilyttää
silti tyyppitiedon. TypeScriptissä geneerisyyttä käytetään myös
tyyppitasolla: tyypeistä johdetaan uusia tyyppejä apuvälinetyypeillä,
kuvatuilla tyypeillä ja ehdollisilla tyypeillä.

## Geneeriset funktiot ja luokat

```{.typescript tiedosto="esimerkit/07-geneeriset.ts"}
```

```{.tuloste tiedosto="esimerkit/07-geneeriset.odotettu"}
```

- **Tyyppiparametri päätellään** argumenteista: `ensimmainen(tuotteet)`
  palauttaa tuotteen tyypin, ei `unknown`ia. Tyhjästä taulukosta
  päätellään `never`.
- **Rajoite** `T extends { id: string }` sallii kaikki tyypit, joilla
  on `id`-kenttä, ja palauttaa silti koko `T`:n. Vertaa: parametrityyppi
  `{ id: string }[]` hukkaisi muut kentät.
- **`K extends keyof T`** sitoo avaimen tyypin kenttiin. `poimi(x,
  "nimi")` hyväksyy vain olemassa olevat kentät, ja paluutyyppi
  `Pick<T, K>` sisältää täsmälleen ne.
- **Oletustyyppiparametri** `V = string` toimii kuten oletusparametri.
- **Ei-null-väite** `tuotteet[1]!` kertoo kääntäjälle, että indeksi on
  olemassa. Se on oikeutettu vain, kun data on samassa kohdassa
  näkyvillä.

Geneerisyys poistetaan ajossa kuten muutkin tyypit: funktion sisällä ei
voi kysyä, mikä `T` on. Jos käyttäytyminen riippuu tyypistä, tarvitaan
ajonaikainen arvo, kuten jäsennin tai erotin.

## Apuvälinetyypit

Standardikirjaston apuvälinetyypit johtavat uusia tyyppejä yhdestä
mallista. Kun malli muuttuu, johdetut tyypit seuraavat mukana.

```{.typescript tiedosto="esimerkit/07-apuvalineet.ts"}
```

```{.tuloste tiedosto="esimerkit/07-apuvalineet.odotettu"}
```

| Tyyppi | Tulos |
|--------|-------|
| `Partial<T>`, `Required<T>` | Kaikki kentät valinnaisia tai pakollisia |
| `Readonly<T>` | Kentät `readonly` (vain yksi taso) |
| `Pick<T, K>`, `Omit<T, K>` | Valitut kentät tai kaikki paitsi valitut |
| `Record<K, V>` | Olio, jonka avaimet `K` ja arvot `V` |
| `Exclude<U, X>`, `Extract<U, X>` | Unionin jäsenet pois tai mukaan |
| `NonNullable<T>` | `null` ja `undefined` pois |
| `ReturnType<F>`, `Parameters<F>` | Funktion paluu- ja parametrityypit |
| `Awaited<T>` | Lupauksen arvon tyyppi |

`T["id"]` on *indeksoitu tyyppi*: kentän `id` tyyppi. `typeof hae`
on arvon `hae` tyyppi. Nämä kaksi yhdistämällä tyypit voi johtaa
koodista sen sijaan, että ne kirjoitettaisiin uudelleen.

## Kuvatut ja ehdolliset tyypit

Apuvälinetyypit on toteutettu kuvatuilla ja ehdollisilla tyypeillä.
Omia tarvitaan harvoin, mutta niitä on hyvä osata lukea:

```{.typescript tiedosto="esimerkit/07-kuvatut.ts"}
```

```{.tuloste tiedosto="esimerkit/07-kuvatut.odotettu"}
```

- **Kuvattu tyyppi** `{ [K in keyof T]: … }` käy läpi tyypin kentät.
  `Lomake<Asiakas>` muuttuu automaattisesti, kun `Asiakas` muuttuu.
- **`as`-uudelleennimeäminen** ja mallimerkkijonotyypit tuottavat uudet
  avaimet: `nimi` → `muutaNimi`.
- **Ehdollinen tyyppi** `T extends U ? X : Y` valitsee tyypin, ja
  `infer` nimeää osan vastaavuudesta. Ehdollinen tyyppi jakautuu
  unionin jäsenille.

Tyyppitason ohjelmointi on houkuttelevaa mutta kallista: monimutkainen
tyyppi hidastaa tarkistusta, ja sen virheilmoituksia on vaikea lukea.
Käytä sitä kirjastojen rajapinnoissa, joissa se säästää käyttäjiltä
paljon toistoa, ei sovelluskoodissa.

## Käytännössä

- **Yksi lähde, johdetut tyypit.** Kirjoita tietomalli kerran ja johda
  muut tyypit siitä (`Omit`, `Partial`, `Pick`). Rinnakkain ylläpidetyt
  lähes samanlaiset tyypit erkanevat ajan myötä.
- **Rajoite ennen `any`ä.** Jos funktio käyttää argumentista vain yhtä
  kenttää, kirjoita rajoite (`T extends { id: string }`) eikä
  `any`-tyyppiä.
- **Tyyppiparametri vain, jos se yhdistää jotain.** Parametri, joka
  esiintyy vain kerran (esim. vain paluutyypissä), on piilotettu
  `as`-pakotus. Se on merkki huonosta allekirjoituksesta.
- **Kopioi, älä muuta.** `{ ...t, ...m }` tuottaa uuden olion, ja
  `Readonly<T>` parametrissa dokumentoi, ettei funktio muuta
  argumenttiaan.
- **Tyyppitaso kohtuudella.** Kuvattu tai ehdollinen tyyppi kannattaa,
  kun se poistaa toistoa monesta paikasta. Jos tyyppiä ei ymmärrä
  vilkaisulla, se kannattaa kirjoittaa auki.

## Itsearviointi

- Osaat kirjoittaa geneerisen funktion rajoitteineen niin, että
  paluutyyppi säilyttää argumentin tarkan tyypin.
- Osaat käyttää `keyof`ia, indeksoituja tyyppejä ja `typeof`ia tyyppien
  johtamiseen.
- Osaat valita sopivan apuvälinetyypin (`Partial`, `Omit`, `Pick`,
  `Record`, `ReturnType`, `Awaited`).
- Osaat lukea kuvattuja ja ehdollisia tyyppejä ja arvioida, milloin
  niitä kannattaa kirjoittaa itse.

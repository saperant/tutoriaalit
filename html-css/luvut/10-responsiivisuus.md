# Responsiivisuus

Responsiivinen sivu toimii 320 pikselin puhelimesta laajakuvanäyttöön
saman HTML:n ja CSS:n avulla. Nykyinen lähestymistapa yhdistää kolme
keinoa: luontaisesti joustavat asettelut (luvut 8 ja 9), sujuvat arvot
(`clamp()`) ja kyselyt, jotka reagoivat näkymään, konttiin tai
käyttäjän asetuksiin.

## Mobile first

Perustyylit kirjoitetaan kapealle näkymälle, ja leveämmille lisätään
sääntöjä `min-width`-kyselyillä, kuten luvun 9 sivupohjassa
(`@media (min-width: 48rem) { ... }`). Perusteet:

- Kapea asettelu on yksinkertaisempi (yksi sarake), joten se on hyvä
  lähtökohta, ja laajennukset ovat lisäyksiä eivätkä kumoamisia.
- Puhelin ei lataa ja laske turhaan monimutkaista työpöytäasettelua.
- Rajapisteet `rem`-yksiköissä toimivat myös, kun käyttäjä suurentaa
  tekstiä: 48rem on 768 px oletusfontilla mutta 960 px 20 pikselin
  fontilla, jolloin sivu siirtyy ajoissa kapeaan asetteluun.

Rajapisteet valitaan sisällön mukaan, kohdasta, jossa asettelu alkaa
näyttää huonolta, eikä suosittujen laitteiden leveyksistä.
Tavallisesti kaksi tai kolme rajapistettä riittää.

## Sujuvat arvot

`clamp(minimi, ihanne, maksimi)` muuttaa arvoa näkymän koon mukaan
rajojen sisällä:

```{.css tiedosto="esimerkit/10-fluidi.html" osa="fluidi"}
```

```{.tuloste tiedosto="esimerkit/10-fluidi.odotettu"}
```

Otsikko on 360 pikselin näkymässä 25 px (24 + 0,025 × 360 = 25),
1024 pikselissä 41,6 px ja leveämmässä enintään 48 px. Ihannearvossa
on `rem`-osa, jotta käyttäjän fonttikoko vaikuttaa siihen; pelkkä `vw`
estäisi tekstin suurentamisen. Leipätekstin rivin pituus rajataan
`max-inline-size: 65ch` -säännöllä, ja palsta keskitetään
`margin-inline: auto` -säännöllä: 1024 pikselissä palsta on 694 px
leveä.

## Konttikyselyt

Mediakysely reagoi näkymän leveyteen, mutta komponentti ei tiedä,
missä se on: sama kortti voi olla leveässä pääpalstassa ja kapeassa
sivupalkissa. Konttikysely (*container query*) reagoi lähimmän
kontin kokoon:

```{.css tiedosto="esimerkit/10-kontti/kortti.css" osa="kysely"}
```

```{.html tiedosto="esimerkit/10-kontti/index.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/10-kontti.odotettu"}
```

Sama kortti on pääpalstassa (yli 400 px) vaakasuuntainen, ja kuva on
160 pikselin sarakkeessa, mutta sivupalkissa (250 px) pystysuuntainen,
jolloin kuva on koko palstan levyinen. Konttikyselyt tekevät
komponenteista uudelleenkäytettäviä: komponentin tyylit eivät oleta
mitään sivun asettelusta. Yksiköt `cqi` ja `cqb` ovat prosentteja
kontin koosta, vastaavasti kuin `vw` näkymästä.

## Käyttäjän asetukset

Mediakyselyt kertovat myös käyttäjän järjestelmäasetuksista:

| Kysely | Asetus |
|--------|--------|
| `prefers-reduced-motion: reduce` | vähennä animaatioita (huimaus, migreeni) |
| `prefers-color-scheme: dark` | tumma teema (luku 11) |
| `prefers-contrast: more` | suurempi kontrasti |
| `forced-colors: active` | Windowsin pakotetut värit |
| `hover: hover`, `pointer: coarse` | hiiri vai kosketus |

```{.css tiedosto="esimerkit/10-liike.html" osa="liike"}
```

```{.tuloste tiedosto="esimerkit/10-liike.odotettu"}
```

Testausselain on asetettu vähentämään liikettä, joten siirtymä on
poistettu. Pelkkä ulkoasun hienous ei ole syy ohittaa asetusta;
merkitystä kantavat siirtymät korvataan vähentyneessä tilassa
lyhyellä häivytyksellä.

## Käytännössä

- **Luontainen ensin, kysely tarvittaessa.** `auto-fit`, `flex-wrap`,
  `clamp()` ja `min()` hoitavat suurimman osan responsiivisuudesta
  ilman rajapisteitä. Mediakyselyitä tarvitaan rakenteellisiin
  muutoksiin, konttikyselyitä komponenttien muotoon.
- **Testaa todellisilla leveyksillä ja zoomilla.** Kehittäjätyökalujen
  laitetila on nopea, mutta 200 %:n zoomaus työpöydällä ja oikea
  puhelin paljastavat eri ongelmia. Vaakavieritys 320 pikselin
  leveydellä on WCAG-virhe.
- **Kosketuskohteet vähintään 24 × 24 pikseliä** (WCAG 2.2 AA),
  mieluummin 44 × 44. Pienet linkit tiheässä luettelossa ovat
  kosketusnäytöllä vaikeita.
- **Älä piilota sisältöä kapeassa näkymässä.** Jos tieto on tarpeeton
  puhelimessa, se on usein tarpeeton muuallakin.

## Itsearviointi

- Osaat kirjoittaa tyylit mobile first -periaatteella ja valita
  rajapisteet `rem`-yksiköissä sisällön mukaan.
- Osaat tehdä sujuvan fonttikoon `clamp()`-funktiolla niin, että
  tekstin suurentaminen toimii.
- Osaat tehdä komponentin, joka muuttaa asetteluaan konttikyselyllä.
- Osaat kunnioittaa käyttäjän liike-, väri- ja kontrastiasetuksia.

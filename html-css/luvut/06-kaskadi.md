# Kaskadi, periytyminen ja spesifisyys

CSS-sääntö koostuu valitsimesta ja esittelyistä:
`.ilmoitus p { color: navy; }`. Valitsin poimii elementit, ja
esittelyt antavat niiden ominaisuuksille arvot. Kun usea sääntö
asettaa saman ominaisuuden samalle elementille, *kaskadi* päättää
voittajan. Useimmat "CSS ei toimi" -tilanteet ovat kaskadin
väärinymmärryksiä.

Tyylit liitetään sivuun ulkoisella tyylitiedostolla
(`<link rel="stylesheet">`), joka on oletus: selain tallentaa sen
välimuistiin ja sama tiedosto palvelee kaikkia sivuja. `<style>`-
elementti sopii sivukohtaisiin ja kriittisiin tyyleihin (luku 15).
`style`-attribuuttia vältetään, koska se ohittaa lähes kaiken muun ja
estää tiukan sisällön turvallisuuskäytännön (CSP).

## Valitsimet

Valitsin kertoo, mihin elementteihin sääntö osuu. Perusosia on neljä:
elementin tyyppi (`p`), luokka (`.kortti`), tunniste (`#haku`) ja
attribuutti (`[type="email"]`). Peräkkäin kirjoitettuina ne
tarkentavat toisiaan: `input.pakollinen[type="email"]` vaatii kaikki
kolme. Pilkku erottaa vaihtoehdot: `h1, h2` osuu kumpaankin.

**Kombinaattori** kahden valitsimen välissä kuvaa elementtien
suhteen dokumentin puussa:

| Kombinaattori | Esimerkki | Osuu |
|--------------------------|-----------|-----------------------------------------|
| välilyönti (jälkeläinen) | `nav a` | linkit missä tahansa `nav`-elementin sisällä |
| `>` (lapsi) | `ul > li` | vain luettelon suorat lapset |
| `+` (seuraava sisarus) | `h2 + p` | kappale heti otsikon jälkeen |
| `~` (myöhemmät sisarukset) | `h2 ~ p` | kaikki otsikkoa seuraavat sisaruskappaleet |

**Pseudoluokka** (yksi kaksoispiste) valitsee elementin tilan tai
aseman perusteella, ja **pseudoelementti** (kaksi kaksoispistettä)
valitsee elementin osan tai luo sellaisen:

| Valitsin | Osuu |
|--------------------------------------|----------------------------------------|
| `:hover`, `:focus-visible`, `:active` | osoitin päällä, näppäimistöfokus, painettuna |
| `:checked`, `:disabled`, `:user-invalid` | lomake-elementin tila (luku 4) |
| `:first-child`, `:last-child`, `:nth-child(odd)` | asema sisarusten joukossa |
| `:not(.piilotettu)` | elementit, joihin argumentti ei osu |
| `:is(h1, h2, h3)` | mikä tahansa argumenteista; lyhentää luetteloita |
| `::before`, `::after` | luotu sisältö elementin alkuun tai loppuun |
| `::placeholder`, `::marker`, `::selection` | kentän vihjeteksti, luettelomerkki, valittu teksti |

```{.css tiedosto="esimerkit/06-valitsimet.html" osa="valitsimet"}
```

```{.html tiedosto="esimerkit/06-valitsimet.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/06-valitsimet.odotettu"}
```

![Valitsimien tulos: ensimmäinen kappale on suurempi, joka toinen
kurssi on korostettu ja ulkoinen linkki on saanut
nuolen.](kuvat/06-valitsimet-480.png){width=55%}

- `h1 + p` osuu vain ensimmäiseen kappaleeseen (20 px), koska toinen
  ei ole heti otsikon jälkeen.
- `.kurssit > li` antaa reunaviivan kolmelle kurssille mutta ei
  sisäkkäiselle kohdalle "Lomakkeet" (`0px`). Jälkeläisvalitsin
  `.kurssit li` olisi osunut siihenkin.
- `:nth-child(odd)` värittää ensimmäisen ja kolmannen kohdan.
  Argumentti voi olla myös kaava: `3n` on joka kolmas ja `n + 2`
  kaikki toisesta alkaen.
- `a[href^="https://"]` osuu linkkeihin, joiden osoite *alkaa*
  merkkijonolla `https://`. Vastaavasti `$=` vertaa loppua ja `*=`
  mitä tahansa kohtaa.
- `::after` lisää nuolen linkin perään. Saavutettavuuspuussa linkin
  nimi on "MDN ↗": luotu sisältö luetaan ääneen. `content`-arvoon ei
  siksi laiteta tietoa, jonka pitää olla HTML:ssä, eikä koristetta,
  jonka lukeminen häiritsee.

Selain lukee valitsimen oikealta vasemmalle: `nav a` tutkii ensin
jokaisen linkin ja sitten sen esivanhemmat. Käytännössä tällä ei
ole merkitystä suorituskyvylle, mutta se selittää, miksi valitsimen
viimeinen osa on se, johon tyylit tulevat. Vanhemman valitseminen
lapsen perusteella onnistuu `:has()`-valitsimella (luku 15).

## Kaskadin järjestys

Selain vertaa kilpailevia esittelyjä tässä järjestyksessä; ensimmäinen
ero ratkaisee:

1. **Alkuperä ja tärkeys**: selaimen oletustyylit < sivun tyylit <
   sivun `!important` < selaimen `!important`. (Käyttäjän omat tyylit
   ovat välissä.)
2. **Konteksti**: verkkokomponentin kapseloidut tyylit (Shadow DOM,
   komponentin oma, muusta sivusta eristetty dokumenttipuu) häviävät
   sivun tyyleille.
3. **Tyyliattribuutti** `style="..."` voittaa tyylitiedostot.
4. **Kerros** (`@layer`): myöhemmin esitelty kerros voittaa, ja
   kerroksiin kuulumattomat tyylit voittavat kaikki kerrokset.
   Kerrokset esitellään tämän luvun lopussa.
5. **Spesifisyys**: tarkempi valitsin voittaa.
6. **Järjestys**: viimeisenä esitelty voittaa.

## Spesifisyys

Spesifisyys on kolmikko *(id, luokka, tyyppi)*, jota verrataan
vasemmalta oikealle:

| Valitsimen osa | Lisää |
|----------------|-------|
| `#tunniste` | (1,0,0) |
| `.luokka`, `[attribuutti]`, `:hover` | (0,1,0) |
| `p`, `::before` | (0,0,1) |
| `*`, `:where(...)` | ei mitään |
| `:is(...)`, `:not(...)`, `:has(...)` | argumenttinsa tarkimman verran |

Yksikään määrä luokkia ei voita yhtä tunnistetta: (0,99,0) < (1,0,0).

```{.css tiedosto="esimerkit/06-spesifisyys.html" osa="saannot"}
```

```{.html tiedosto="esimerkit/06-spesifisyys.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/06-spesifisyys.odotettu"}
```

![Kappaleet a–d selaimessa.](kuvat/06-spesifisyys-1024.png){width=28%}

- **a**: `.ilmoitus p` (0,1,1) voittaa pelkän `p`-säännön (0,0,1).
- **b**: `p.tarkea` ja `.ilmoitus p` ovat yhtä tarkkoja; myöhempi voittaa.
- **c**: tunniste voittaa kaikki luokkavalitsimet.
- **d**: `:where()` ei tuo spesifisyyttä, joten
  `:where(#tiedote, .ilmoitus) .pieni` on vain (0,1,0) ja häviää
  `.ilmoitus p` -säännölle. Väri on siksi navy eikä harmaa.
  Fonttikoon asettaa ainoa sitä koskeva sääntö.

`:where()` on hyödyllinen kirjastojen ja nollaustyylien
kirjoittajille: niiden oletukset on helppo ohittaa. Tunnisteita ei
käytetä tyylittelyyn lainkaan, koska niiden spesifisyys pakottaa
ohitukset yhä tarkemmiksi.

## Periytyminen

Osa ominaisuuksista periytyy lapsille, osa ei. Tekstiin liittyvät
periytyvät (`color`, `font-*`, `line-height`, `text-align`,
`visibility`), laatikkoon liittyvät eivät (`border`, `margin`,
`padding`, `background`, `width`).

```{.css tiedosto="esimerkit/06-periytyminen.html" osa="saannot"}
```

```{.html tiedosto="esimerkit/06-periytyminen.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/06-periytyminen.odotettu"}
```

- Kappale perii värin ja koon kortilta, mutta ei reunaa.
- **Lomake-elementit eivät peri fonttia.** Selaimen oletustyyli antaa
  painikkeelle oman fontin ja värin (13,33 px). Siksi lähes jokainen
  nollaustyyli sisältää säännön `button, input, select, textarea
  { font: inherit; }`.
- Avainsanat ohjaavat periytymistä: `inherit` (vanhemman arvo),
  `initial` (ominaisuuden määrittelyn alkuarvo, värille musta),
  `unset` (periytyvälle `inherit`, muille `initial`) ja `revert`
  (selaimen oletustyyli).

## Kaskadikerrokset

`@layer` jakaa tyylit nimettyihin kerroksiin, joiden järjestys
ratkaisee ennen spesifisyyttä. Näin kirjaston tai perustyylien tarkka
valitsin ei voi voittaa myöhemmän kerroksen yksinkertaista luokkaa:

```{.css tiedosto="esimerkit/06-kerrokset/tyyli.css" osa="kerrokset"}
```

```{.html tiedosto="esimerkit/06-kerrokset/index.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/06-kerrokset.odotettu"}
```

Perustyylin valitsin (1,2,1) on paljon tarkempi kuin `.painike`
(0,1,0), mutta komponenttikerros on myöhempi, joten painikkeen väri
on valkoinen. Apuluokka voittaa vastaavasti komponentin. Tavallinen
kerrosjärjestys on *nollaus, perusta, komponentit, apuluokat*;
kolmannen osapuolen tyylit tuodaan omaan kerrokseensa:
`@import url(kirjasto.css) layer(kirjasto);`.

`!important` kääntää kerrosten järjestyksen: tärkeäksi merkitty
esittely aikaisemmassa kerroksessa voittaa myöhemmän kerroksen
tärkeän esittelyn. Se on tarkoitettu nollauksille, jotka eivät saa
väistyä, kuten `prefers-reduced-motion`-sääntö.

## Käytännössä

- **Matala ja tasainen spesifisyys.** Yksi luokka per valitsin on
  hyvä oletus. Kun kaikki säännöt ovat yhtä tarkkoja, järjestys ja
  kerrokset ratkaisevat, ja niitä on helppo ennustaa.
- **Nimeämiskäytäntö pitää spesifisyyden kurissa.** BEM
  (`.kortti__otsikko--korostettu`) välttää sisäkkäiset valitsimet.
  Utility-first-kehykset (Tailwind) käyttävät pelkkiä yhden ominaisuuden
  luokkia. CSS-modulit ja Vue/Svelte-komponenttien rajatut tyylit
  tuottavat yksilölliset luokkanimet automaattisesti. Kaikki ratkaisevat
  saman ongelman: globaalin nimiavaruuden.
- **`!important` on hälytysmerkki.** Se kertoo, että spesifisyys on
  karannut käsistä. Poikkeuksia ovat apuluokat ja saavutettavuuden
  nollaukset.
- **Kehittäjätyökalut kertovat syyn.** *Computed*-näkymä näyttää
  lasketun arvon ja säännön, josta se tuli; yliviivatut esittelyt
  *Styles*-näkymässä hävisivät kaskadissa.

## Itsearviointi

- Osaat kertoa kaskadin vaiheet ja ennustaa, mikä kilpailevista
  säännöistä voittaa.
- Osaat laskea valitsimen spesifisyyden ja käyttää `:where()`- ja
  `:is()`-valitsimia tarkoituksella.
- Osaat kertoa, mitkä ominaisuudet periytyvät, ja korjata lomake-
  elementtien fontin periytymisen.
- Osaat jäsentää tyylit kaskadikerroksiin ja selittää, miksi kerros
  voittaa spesifisyyden.

# Mukautetut ominaisuudet ja teemat

Mukautetut ominaisuudet (*custom properties*, puhekielessä
CSS-muuttujat) ovat `--`-alkuisia ominaisuuksia, joiden arvon
`var()` lukee. Toisin kuin esikääntäjien (Sass) muuttujat, ne ovat
voimassa ajossa: ne periytyvät, niitä voi muuttaa kyselyissä ja
valitsimissa, ja JavaScript voi lukea ja asettaa niitä.

## Arvot, varavarat ja periytyminen

```{.css tiedosto="esimerkit/11-muuttujat.html" osa="muuttujat"}
```

```{.html tiedosto="esimerkit/11-muuttujat.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/11-muuttujat.odotettu"}
```

- **Komponentin sisäinen muuttuja.** `--merkin-vari` määritellään
  komponentissa, ja muunnelma (`.varoitus`) vaihtaa vain sen. Kaikki
  siitä riippuvat ominaisuudet (teksti, reuna, tausta) seuraavat.
- **Varavara** `var(--merkin-reuna, currentcolor)` käytetään, kun
  muuttujaa ei ole asetettu. Reunan väri on siksi tekstin väri.
- **`color-mix()`** sekoittaa värejä; vaalea tausta syntyy samasta
  perusväristä. Selain ilmoittaa sekoituksen tuloksen `color()`-muodossa.
- **Virheellinen arvo ei kaadu näkyvästi.** Muuttujan arvoa ei
  tarkisteta sitä määriteltäessä. Kun `color: var(--merkin-vari)` saa
  arvon `12px`, esittely on *virheellinen laskentahetkellä*, ja
  ominaisuus saa periytyvän arvonsa (mustan) eikä edellistä toimivaa
  arvoa. `@property`-säännöllä muuttujalle voi määritellä tyypin, jolloin
  virheellinen arvo hylätään ja käytetään alkuarvoa.

## Suunnittelutokenit

Suunnittelujärjestelmän päätökset, kuten värit, välit, fonttikoot ja
pyöristykset, tallennetaan *suunnittelutokeneiksi* (*design tokens*).
Tavallinen jako on kaksitasoinen:

```{.css tiedosto="esimerkit/11-teemat/tokenit.css" osa="primitiivit"}
```

```{.css tiedosto="esimerkit/11-teemat/tokenit.css" osa="semanttiset"}
```

Komponentit käyttävät vain semanttisia tokeneita:

```{.css tiedosto="esimerkit/11-teemat/komponentit.css" osa="komponentit"}
```

```{.html tiedosto="esimerkit/11-teemat/index.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/11-teemat.odotettu"}
```

![Sama komponentti vaaleassa ja tummassa teemassa.](kuvat/11-teemat-1024.png){width=80%}

- **Primitiivit** nimeävät paletin (`--sininen-700`), eivätkä kerro
  käyttötarkoitusta. Niitä ei käytetä komponenteissa suoraan.
- **Semanttiset tokenit** nimeävät tarkoituksen (`--pinta`,
  `--teksti`, `--korostus`). Teeman vaihto muuttaa vain niiden
  kytkennän primitiiveihin.
- **Tumma teema** kytketään käyttäjän järjestelmäasetukseen
  (`prefers-color-scheme: dark`), ja `data-teema`-attribuutti antaa
  käyttäjän ohittaa valinnan sivustolla. Testausselain käyttää vaaleaa
  teemaa, joten raportissa tumma teema näkyy vain
  `data-teema="tumma"`-osiossa.
- **`color-scheme`** kertoo selaimelle teeman, jolloin vierityspalkit,
  lomake-elementit ja oletusvärit vaihtuvat samalla.
- Tummassa teemassa korostusväri on vaaleampi, koska sama sininen
  tummalla pinnalla ei täyttäisi kontrastivaatimusta. Teema ei ole
  pelkkä värien kääntö: jokainen pari tarkistetaan erikseen.

Tokeneita ylläpidetään usein työkalulla (esimerkiksi Style Dictionary)
yhtenä lähteenä, josta tuotetaan CSS, mobiilisovellusten resurssit ja
suunnitteluohjelman kirjasto. W3C:n Design Tokens -yhteisöryhmä on
määritellyt niille JSON-muodon.

## Käytännössä

- **Kaksi tasoa tokeneita.** Primitiivit ja semanttiset tokenit. Kolmas
  taso, komponenttikohtaiset tokenit (`--painike-tausta`), kannattaa
  vasta, kun komponentteja teemoitetaan erikseen.
- **Muuttuja muunnelmille, ei uusia sääntöjä.** Komponentin muunnelma
  vaihtaa yhden tai kaksi muuttujaa sen sijaan, että toistaisi
  ominaisuudet. Tämä pitää spesifisyyden matalana ja muunnelmat
  yhdenmukaisina.
- **Teeman valinta talteen ennen ensimmäistä piirtoa.** Jos käyttäjä
  valitsee teeman sivustolla, valinta asetetaan `<html>`-elementin
  attribuutiksi palvelimella tai pienellä `<head>`-skriptillä. Muuten
  sivu välähtää väärässä teemassa (*flash of incorrect theme*).
- **Nimeä tarkoitus, älä arvoa.** `--korostus` kestää brändin
  värimuutoksen, `--sininen` ei.

## Itsearviointi

- Osaat käyttää mukautettuja ominaisuuksia komponentin muunnelmiin
  ja varavaroja puuttuvien arvojen varalle.
- Osaat selittää, mitä virheelliselle muuttujan arvolle tapahtuu, ja
  käyttää `@property`-sääntöä tyypin määrittelyyn.
- Osaat jäsentää suunnittelutokenit primitiiveihin ja semanttisiin
  tokeneihin.
- Osaat toteuttaa vaalean ja tumman teeman, joka seuraa käyttäjän
  asetusta ja jonka voi ohittaa.

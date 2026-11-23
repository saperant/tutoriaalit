# Laatikkomalli ja normaali virtaus

Jokainen elementti on suorakulmainen laatikko: sisältö, sen ympärillä
täyte (`padding`), reunus (`border`) ja uloimpana marginaali
(`margin`). Ilman asettelusääntöjä laatikot asettuvat *normaaliin
virtaukseen*: lohkotason elementit (`<p>`, `<div>`, `<h1>`) allekkain
koko leveydeltä ja tekstitason elementit (`<a>`, `<strong>`) rivin
sisään tekstin tavoin.

## box-sizing

```{.css tiedosto="esimerkit/07-laatikko.html" osa="laatikot"}
```

```{.html tiedosto="esimerkit/07-laatikko.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/07-laatikko.odotettu"}
```

Oletuksena (`content-box`) leveys koskee vain sisältöä, ja täyte ja
reunus lisätään siihen: 200 + 2 × 20 + 2 × 5 = 250 pikseliä.
`border-box` laskee täytteen ja reunan mukaan annettuun leveyteen,
mikä vastaa sitä, miten mitoista yleensä ajatellaan. Siksi lähes
jokainen projekti aloittaa säännöllä
`*, *::before, *::after { box-sizing: border-box; }`.

## Marginaalien yhdistyminen

Peräkkäisten lohkojen pystymarginaalit yhdistyvät (*margin
collapsing*): väliin jää suurempi marginaaleista, ei niiden summa.
Raportissa ylempi päättyy kohtaan 204 ja alempi alkaa kohdasta 228,
joten väli on 24 eikä 40 pikseliä. Sama tapahtuu vanhemman ja
ensimmäisen lapsen marginaalille, mikä selittää "ylimääräisen" välin
otsikon yläpuolella. Flex- ja grid-asettelussa marginaalit eivät
yhdisty. Siksi välit kannattaa tehdä asettelun `gap`-ominaisuudella
(luvut 8 ja 9) tai yhdensuuntaisilla marginaaleilla, esimerkiksi vain
`margin-block-end`.

## Loogiset ominaisuudet

Fyysiset ominaisuudet (`left`, `right`, `top`, `bottom`, `width`)
viittaavat ruudun suuntiin. Loogiset ominaisuudet viittaavat
tekstin suuntaan: *inline* on rivin suunta ja *block* rivien
etenemissuunta.

| Fyysinen | Looginen (vaakasuuntainen kirjoitus) |
|----------|---------------------------------------|
| `width`, `height` | `inline-size`, `block-size` |
| `margin-left` | `margin-inline-start` (vasen, oikealta vasemmalle oikea) |
| `padding-top`, `padding-bottom` | `padding-block` |
| `border-left` | `border-inline-start` |
| `left` | `inset-inline-start` |
| `text-align: left` | `text-align: start` |

```{.css tiedosto="esimerkit/07-loogiset.html" osa="loogiset"}
```

```{.html tiedosto="esimerkit/07-loogiset.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/07-loogiset.odotettu"}
```

Sama CSS toimii arabiankielisessä tekstissä peilattuna: merkki siirtyy
laatikon oikeaan reunaan (`x=296`), ja reunaviiva on oikealla. Loogiset
ominaisuudet ovat uusien tyylien oletus, vaikka sivusto olisi vain
suomeksi, koska ne eivät maksa mitään ja kansainvälistäminen ei vaadi
tyylien uudelleenkirjoitusta.

## Yksiköt

| Yksikkö | Suhteessa | Käyttö |
|---------|-----------|--------|
| `rem` | juuren fonttikokoon (oletus 16 px) | fonttikoot, välit, rajapisteet |
| `em` | elementin omaan fonttikokoon | komponentin sisäiset välit |
| `px` | CSS-pikseli | reunat, varjot, pienet yksityiskohdat |
| `%` | sisältävään laatikkoon | leveydet |
| `ch` | merkin "0" leveyteen | tekstipalstan leveys (`65ch`) |
| `vw`, `vh`, `dvh` | näkymän kokoon | koko näkymän osiot |
| `fr` | grid-ruudukon vapaaseen tilaan | sarakkeet (luku 9) |

Fonttikoot ja rajapisteet `rem`-yksiköissä noudattavat käyttäjän
selaimeen asettamaa fonttikokoa; pikseleinä ne ohittaisivat sen.
`dvh` ottaa huomioon mobiiliselaimen piiloutuvan osoitepalkin, jonka
kanssa `100vh` on liian korkea.

## display ja ylivuoto

- `display: block` ja `inline` vaihtavat laatikon tyypin, `inline-block`
  on rivin sisällä mutta ottaa mitat, `none` poistaa elementin
  asettelusta ja saavutettavuuspuusta.
- `display: flex` ja `grid` tekevät elementistä asettelukontin
  lapsilleen (luvut 8 ja 9).
- `overflow: auto` lisää vierityspalkin vain tarvittaessa; `hidden`
  leikkaa sisällön, mikä voi piilottaa fokuksen ja tekstiä
  suurennettaessa.
- Pitkä katkeamaton merkkijono (URL, tunniste) venyttää laatikkoa;
  `overflow-wrap: anywhere` sallii katkaisun mistä tahansa.

## Käytännössä

- **Nollaus alussa.** `box-sizing: border-box`, `margin: 0` otsikoille
  ja kappaleille sekä `font: inherit` lomake-elementeille ovat
  tavallinen kevyt nollaus (*modern CSS reset*). Raskaita nollauksia,
  jotka poistavat kaiken, ei enää tarvita.
- **Älä anna korkeuksia tekstisisällölle.** Kiinteä `height` leikkaa
  tai ylivuotaa, kun tekstiä suurennetaan tai käännös on pidempi.
  Käytä `min-block-size`-ominaisuutta, jos minimikorkeus tarvitaan.
- **Leveydet maksimeina.** `max-inline-size` antaa laatikon kutistua
  kapeassa näkymässä; kiinteä `width` aiheuttaa vaakavierityksen.
- **Välit vanhemmalta.** Asettelukontin `gap` tai *pino*-malli
  (`.pino > * + * { margin-block-start: 1rem; }`) pitää välit yhdessä
  paikassa sen sijaan, että jokainen komponentti tuo omat marginaalinsa.

## Itsearviointi

- Osaat laskea laatikon koon `content-box`- ja `border-box`-malleissa.
- Osaat selittää marginaalien yhdistymisen ja välttää sen yllätykset.
- Osaat käyttää loogisia ominaisuuksia ja kertoa, miksi ne ovat
  fyysisiä parempi oletus.
- Osaat valita yksikön käyttötarkoituksen mukaan niin, että sivu
  noudattaa käyttäjän fonttikokoa.

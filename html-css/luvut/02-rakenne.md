# Dokumentin rakenne ja semantiikka

HTML-elementti kertoo, *mitä* sisältö on, ei miltä se näyttää.
Ulkoasu tulee CSS:stä, joten elementti valitaan merkityksen mukaan:
otsikko on `<h2>`, koska se on otsikko, ei siksi, että sen teksti on
isompaa. Tätä kutsutaan **semanttiseksi HTML:ksi**.

## Div-sivu ja semanttinen sivu

Uutissivun alku kahdella tavalla. Ensin pelkillä `<div>`-elementeillä,
kuten sivuja usein rakennetaan:

```{.html tiedosto="esimerkit/02-div-sivu.html" osa="runko"}
```

```{.tuloste tiedosto="esimerkit/02-div-sivu.odotettu"}
```

Sitten semanttisilla elementeillä:

```{.html tiedosto="esimerkit/02-semanttinen.html" osa="runko"}
```

```{.tuloste tiedosto="esimerkit/02-semanttinen.odotettu"}
```

![Div-sivu selaimessa ilman omia tyylejä: pelkkää
tekstiä.](kuvat/02-div-sivu-1024.png){width=30%}

![Semanttinen sivu ilman omia tyylejä: otsikko ja luettelo saavat
selaimen oletusulkoasun.](kuvat/02-semanttinen-1024.png){width=62%}

Sopivalla CSS:llä sivut näyttävät samalta, ja molemmat ovat
validaattorin mielestä kelvollisia. Saavutettavuuspuu paljastaa eron.
Div-sivulla otsikko, ingressi ja alatunniste ovat yhtä tekstimassaa:
ruudunlukija ei voi hypätä otsikosta toiseen eikä navigaatioon, eikä
se tiedä, missä pääsisältö alkaa. Semanttisella sivulla jokaisella
osalla on rooli.

## Maamerkit ja osiot

| Elementti | Rooli | Käyttö |
|-----------|-------|--------|
| `<header>` | `banner` | sivuston yläosa: logo, haku, päävalikko |
| `<nav>` | `navigation` | navigaatiolinkkien ryhmä |
| `<main>` | `main` | sivun pääsisältö, yksi sivua kohden |
| `<aside>` | `complementary` | sisältöön liittyvä sivuhuomio |
| `<footer>` | `contentinfo` | sivuston alaosa: yhteystiedot, oikeudet |
| `<search>` | `search` | hakulomake |
| `<section>` | `region` (nimettynä) | temaattinen osio, jolla on otsikko |
| `<article>` | `article` | itsenäinen kokonaisuus: uutinen, kommentti |

`<header>` ja `<footer>` ovat maamerkkejä vain, kun ne ovat suoraan
`<body>`-elementin alla; `<article>`-elementin sisällä ne ovat sen
oma ylä- ja alaosa. Jos sivulla on useita samanlaisia maamerkkejä,
kuten kaksi `<nav>`-elementtiä, ne nimetään `aria-label`-attribuutilla,
jotta ruudunlukijan käyttäjä erottaa ne toisistaan.

`<div>` ja `<span>` ovat edelleen oikeita valintoja, kun tarvitaan
ryhmä vain ulkoasua varten. Niillä ei ole merkitystä, eikä niitä
tarvitse välttää; niitä ei vain käytetä sellaisen sisällön tilalla,
jolla on oma elementtinsä.

## Otsikkohierarkia

Otsikot muodostavat sivun sisällysluettelon. Ruudunlukijan käyttäjistä
suurin osa etsii sisältöä hyppimällä otsikosta toiseen. Siksi tasot
eivät saa hypätä: `<h2>`-otsikon alla on `<h3>`, ei `<h4>`.

```{.html tiedosto="esimerkit/02-otsikot.ei-kaanny.html"}
```

```text
10:8  error  Heading level can only increase by one, expected <h2>
             but got <h3>  heading-level
```

Virheellinen rivi on valittu ulkoasun takia: `<h3>` oli sopivan
kokoinen. Korjattuna (rivi `@virhe` poistettuna) otsikkopuu on ehjä:

```{.tuloste tiedosto="esimerkit/02-otsikot.odotettu"}
```

Säännöt:

- Sivulla on yksi `<h1>`, joka kertoo, mistä sivu kertoo. Yleensä
  se on sama kuin `<title>`-elementin ensimmäinen osa.
- Otsikko kuvaa sitä seuraavaa sisältöä. Otsikkoa ei käytetä
  korostukseen eikä korostusta otsikkona.
- Koko valitaan CSS:llä. Jos otsikon pitää näyttää pienemmältä kuin
  sen taso, sille annetaan luokka.

## Tekstin semantiikka

Resepti näyttää tekstitason elementit:

```{.html tiedosto="esimerkit/02-resepti.html" osa="resepti"}
```

```{.tuloste tiedosto="esimerkit/02-resepti.odotettu"}
```

- `<ul>` on luettelo, jonka järjestyksellä ei ole väliä, `<ol>`
  järjestetty luettelo (vaiheet) ja `<dl>` nimi–arvo-pareja (termit ja
  määritelmät, tekniset tiedot). Ruudunlukija kertoo luettelon koon,
  jolloin käyttäjä tietää, mitä on tulossa.
- `<time datetime="2026-11-02">` antaa koneluettavan arvon
  ihmisluettavalle päivämäärälle; `PT10M` on ISO 8601 -kesto.
- `<strong>` merkitsee tärkeää ja `<em>` painotusta, joka muuttaa
  lauseen merkitystä. `<b>` ja `<i>` ovat tyylillisiä poikkeamia
  ilman lisämerkitystä, esimerkiksi vieraskielinen termi.
- `<abbr title="...">` avaa lyhenteen, mutta `title`-attribuutti ei
  näy kosketusnäytöillä eikä näppäimistökäyttäjille. Tärkeä lyhenne
  kannattaa avata tekstissä ensimmäisellä kerralla.

## Linkit ja navigaatio

```{.html tiedosto="esimerkit/02-navigaatio.html" osa="navigaatio"}
```

```{.tuloste tiedosto="esimerkit/02-navigaatio.odotettu"}
```

- **Ohituslinkki** (*skip link*) on sivun ensimmäinen kohdistettava
  elementti. Näppäimistön käyttäjä ohittaa sillä toistuvan valikon.
  Se piilotetaan näkyvistä kunnes se saa fokuksen (luku 5).
- `aria-current="page"` kertoo, mikä valikon linkki osoittaa nykyiselle
  sivulle. Samaa attribuuttia kannattaa käyttää myös tyylittelyssä
  (`[aria-current="page"]`), jolloin visuaalinen ja ohjelmallinen tila
  eivät voi erota.
- **Murupolku** (*breadcrumb*) on järjestetty luettelo nimetyn
  `<nav>`-elementin sisällä.
- **Linkin teksti kertoo kohteen.** "Vertaile kahvinkeittimiä" on
  ymmärrettävä myös ruudunlukijan linkkiluettelossa, jossa ympäröivä
  teksti ei näy. "Klikkaa tästä" ei ole.
- Linkki vie jonnekin (`<a href>`), painike tekee jotain
  (`<button>`). Jos elementti ei vaihda sivua tai osoitetta, se on
  painike.

## Käytännössä

- **Rakenne ensin, ulkoasu sitten.** Kirjoita sivu ensin pelkkänä
  semanttisena HTML:nä ja tarkista, että se on järkevä ilman CSS:ää.
  Selaimen lukutila, hakukoneet ja ruudunlukijat näkevät sivun
  juuri näin.
- **Elementti merkityksen mukaan.** Kun valitset elementtiä, kysy
  "mikä tämä on?" eikä "miltä tämä näyttää?". MDN:n elementtiluettelo
  kertoo jokaisen elementin roolin.
- **Saavutettavuuspuu on testattava rajapinta.** Kehittäjätyökalujen
  saavutettavuusnäkymä tai tämän tutoriaalin raportti näyttää sivun
  sellaisena kuin avustavat teknologiat sen saavat. Rakenteelliset
  muutokset kannattaa tarkistaa siitä.
- **Validaattori jatkuvaan integraatioon.** html-validate tai W3C:n
  validaattori ajetaan samoin kuin kääntäjän varoitukset. Se ei löydä
  div-sivun kaltaisia merkitysvirheitä, joten katselmointi tarvitaan
  silti.
- **Komponenttikirjastot noudattavat samoja sääntöjä.** Reactin,
  Vuen tai Sveltin komponentti tuottaa lopulta HTML:ää. Komponentin
  juurielementti valitaan samoin perustein kuin käsin kirjoitetussa
  sivussa.

## Itsearviointi

- Osaat rakentaa sivun maamerkkielementeistä ja selittää, mitä ne
  antavat ruudunlukijan käyttäjälle.
- Osaat laatia ehjän otsikkohierarkian ja erottaa otsikon tason sen
  ulkoasusta.
- Osaat valita oikean luetteloelementin ja tekstitason elementin
  sisällön merkityksen mukaan.
- Osaat tehdä ohituslinkin, nimetyt navigaatiot ja kuvaavat linkkitekstit
  ja erottaa linkin painikkeesta.

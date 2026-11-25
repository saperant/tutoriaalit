# Flexbox

Flexbox asettelee lapsensa yhteen suuntaan, riville tai sarakkeeseen,
ja jakaa vapaan tilan niiden kesken. Se sopii komponenttien sisäiseen
asetteluun: palkit, painikeryhmät, kortin sisältö ja kuvan ja tekstin
rinnastus. Kaksiulotteiset asettelut kuuluvat gridille (luku 10).

## Akselit

`display: flex` tekee elementistä flex-kontin. Pääakseli kulkee
`flex-direction`-suuntaan (oletus `row`, rivin suunta) ja poikkiakseli
sitä vastaan.

| Ominaisuus | Akseli | Tehtävä |
|------------|--------|---------|
| `justify-content` | pää | vapaan tilan jako: `start`, `space-between`, `center` |
| `align-items` | poikki | kohdistus: `stretch` (oletus), `center`, `baseline` |
| `flex-wrap` | | rivitys, kun tila loppuu |
| `gap` | molemmat | välit kohteiden väliin, ei reunoille |
| `align-self` | poikki | yksittäisen kohteen kohdistus |

![Tavallisimmat arvot rivisuuntaisessa kontissa. Katkoviiva on
kontti. Kaavio on HTML-sivu
(`esimerkit/09-akselit.html`).](kuvat/09-akselit-720.png){width=95%}

Kaavion rivit eroavat toisistaan vain yhdellä esittelyllä:

```{.css tiedosto="esimerkit/09-akselit.html" osa="arvot"}
```

Kun `flex-direction` on `column`, akselit vaihtavat paikkaa:
`justify-content` vaikuttaa pystysuunnassa ja `align-items`
vaakasuunnassa.

## Yläpalkki

Logo, valikko ja kirjautumislinkki, joka työntyy oikeaan reunaan:

```{.css tiedosto="esimerkit/09-ylapalkki.html" osa="palkki"}
```

```{.html tiedosto="esimerkit/09-ylapalkki.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-ylapalkki.odotettu"}
```

![Yläpalkki 1024 pikselin levyisenä.](kuvat/09-ylapalkki-1024.png){width=100%}

![Sama palkki 360 pikselin levyisenä rivittyy.](kuvat/09-ylapalkki-360.png){width=40%}

- `margin-inline-start: auto` syö kaiken vapaan tilan kohteen
  edestä ja työntää sen loppuun. Se on yksinkertaisin tapa erottaa
  ryhmät palkissa.
- `flex-wrap: wrap` rivittää kohteet kapeassa näkymässä. Ilman sitä ne
  kutistuisivat ja ylivuotaisivat. Kapeassa näkymässä valikko siirtyy
  omalle rivilleen ja kirjautumislinkki kolmannelle, mutta oikeaan
  reunaan (`x=278`).
- `gap: 8px 24px` antaa eri välin riveille ja sarakkeille.
- Valikko on itsekin flex-kontti. Sisäkkäiset flex-kontit ovat
  tavallisia: kukin taso hoitaa oman suuntansa.

## Kohteiden koko

Kohteen koko lasketaan kolmesta arvosta: `flex-grow` (osuus vapaasta
tilasta), `flex-shrink` (osuus puutteesta) ja `flex-basis`
(lähtökoko). Lyhenne `flex` asettaa kaikki kolme:

```{.css tiedosto="esimerkit/09-joustavuus.html" osa="jousto"}
```

```{.html tiedosto="esimerkit/09-joustavuus.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-joustavuus.odotettu"}
```

![Ylärivillä `flex: 1`, `flex: 2` ja `flex: none`, alarivillä kaksi
`flex: auto` -kohdetta.](kuvat/09-joustavuus-1024.png){width=80%}

- `flex: 1` tarkoittaa `1 1 0%`: lähtökoko on nolla, joten koko tila
  (600 − 120 = 480) jaetaan kertoimien suhteessa: A saa 160 ja B 320.
  Tämä tekee yhtä leveät sarakkeet sisällöstä riippumatta.
- `flex: none` (`0 0 auto`) pitää kohteen omassa koossaan.
- `flex: auto` (`1 1 auto`) lähtee sisällön koosta ja jakaa vasta
  ylimääräisen tilan: pidempi teksti saa leveämmän laatikon.

## Ylivuodon sudenkuoppa

Flex-kohteen minimileveys on oletuksena sen sisällön minimi
(`min-inline-size: auto`). Pitkä katkeamaton sana tai URL ei siksi
anna kohteen kutistua, vaan se työntää kontin yli:

```{.css tiedosto="esimerkit/09-ylivuoto.html" osa="ylivuoto"}
```

```{.html tiedosto="esimerkit/09-ylivuoto.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-ylivuoto.odotettu"}
```

![Katkoviiva on 400 pikselin kontti. Ylhäällä teksti ylivuotaa,
alhaalla korjattu versio.](kuvat/09-ylivuoto-1024.png){width=75%}

Kontti on 400 pikseliä, mutta ensimmäinen tekstilaatikko on 518
pikseliä leveä ja ylivuotaa. `min-inline-size: 0` sallii kutistumisen,
ja `overflow-wrap: anywhere` katkaisee sanan. Sama koskee grid-
kohteita, joissa korjaus on sarakkeen koko `minmax(0, 1fr)`.

## Käytännössä

- **Media-objekti.** Kuva tai ikoni ja sen viereinen teksti:
  `display: flex; gap; align-items: start`, kuvalle `flex: none` ja
  tekstille `flex: 1; min-inline-size: 0`. Malli toistuu kommenteissa,
  ilmoituksissa ja listoissa.
- **`gap` marginaalien sijaan.** Se ei lisää väliä reunoille eikä
  vaadi `:last-child`-poikkeuksia.
- **Rivitys ja `flex-basis` mediakyselyjen sijaan.** `flex: 1 1 15rem;
  flex-wrap: wrap` asettaa kohteet rinnakkain, kun niille on tilaa, ja
  allekkain, kun ei ole. Asettelu sopeutuu kontin kokoon ilman
  rajapisteitä.
- **Älä muuta järjestystä `order`-ominaisuudella.** Näkyvä järjestys
  ja fokuksen järjestys eriytyvät. Muuta mieluummin HTML:n järjestystä.

## Itsearviointi

- Osaat tehdä palkin, jossa ryhmät jakautuvat reunoille ja rivittyvät
  kapeassa näkymässä.
- Osaat ennustaa kohteiden leveydet `flex`-lyhenteen arvoista.
- Osaat tunnistaa ja korjata `min-inline-size: auto` -ylivuodon.
- Osaat valita flexboxin ja gridin välillä asettelun ulottuvuuksien
  mukaan.

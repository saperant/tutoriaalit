# Siirtymät ja animaatiot

Liike kertoo, mitä käyttöliittymässä tapahtui: painike reagoi,
paneeli aukesi, sisältöä ladataan. Hyvä liike on lyhyt ja
huomaamaton, ja sivu toimii täysin ilman sitä. CSS:ssä on kaksi
välinettä: **siirtymä** (`transition`) kahden tilan välillä ja
**animaatio** (`animation`), jonka vaiheet kuvataan avainkehyksinä.

## Siirtymä

Kun ominaisuuden arvo muuttuu, esimerkiksi osoittimen tullessa
painikkeen päälle, muutos tapahtuu oletuksena heti. `transition`
kertoo, että muutos tehdään vähitellen:

```{.css tiedosto="esimerkit/14-siirtyma.html" osa="siirtyma"}
```

```{.html tiedosto="esimerkit/14-siirtyma.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/14-siirtyma.odotettu"}
```

![Painike lepotilassa ja aktiivisena. Siirtymä on näiden kahden
tilan välinen liike.](kuvat/14-siirtyma-480.png){width=55%}

Siirtymä määritellään **lepotilan** säännössä, ei `:hover`-säännössä,
jolloin se pätee kumpaankin suuntaan. Lyhenteen osat ovat:

| Osa | Esimerkissä | Merkitys |
|-----------------------------|--------------------|--------------------------------|
| `transition-property` | `background-color` | mitä ominaisuutta siirtymä koskee |
| `transition-duration` | `150ms` | kesto |
| `transition-timing-function` | `ease-out` | nopeuden muutos keston aikana |
| `transition-delay` | (ei annettu) | viive ennen alkua |

- **Luettele ominaisuudet.** `transition: all` animoi kaiken, mikä
  sattuu muuttumaan, myös asiat, joita ei tarkoitettu (esimerkiksi
  teeman vaihtuessa), ja teettää selaimella turhaa työtä.
- **Tila ei ole vain `:hover`.** Sama ulkoasu annetaan
  näppäimistöfokukselle (`:focus-visible`), koska kosketusnäytöllä ja
  näppäimistöllä osoitinta ei ole. Luokka (`.aktiivinen`) tai
  attribuutti (`[aria-expanded="true"]`) käynnistää siirtymän samoin,
  kun JavaScript vaihtaa sen.
- **Kaikki arvot eivät siirry.** Siirtymä toimii arvoille, joiden
  väliltä voi laskea välivaiheita: värit, pituudet, `opacity` ja
  `transform`. Avainsanojen välillä (`display: none` → `block`,
  `height: auto`) ei perinteisesti ole välivaiheita, joten ne
  vaihtuvat kerralla.

Raportin viimeinen rivi poikkeaa tyylitiedoston alusta, koska
testausselain pyytää vähennettyä liikettä: siirtymästä on jäänyt
pois `transform`, ja aktiivinen painike ei nouse (`transform=none`).
Tähän palataan alempana.

## Kesto ja ajoitusfunktio

Käyttöliittymän siirtymät ovat lyhyitä. Pieni tilanmuutos (väri,
korostus) kestää 100–200 millisekuntia ja suurempi liike (paneeli,
valikko) 200–400. Yli puolen sekunnin siirtymä tuntuu hitaalta, kun
sen näkee kymmenennen kerran.

Ajoitusfunktio kertoo, miten muutos etenee keston aikana:

![Ajoitusfunktioiden avainsanat. Vaaka-akselilla on kulunut aika ja
pystyakselilla muutoksen edistymä; vertailuna tasainen
eteneminen.](kuvat/14-ajoitusfunktiot.png){width=100%}

- `ease-out` alkaa nopeasti ja hidastuu. Se sopii näkyviin tulevalle
  ja käyttäjän toimeen reagoivalle sisällölle, koska vaste tuntuu
  välittömältä.
- `ease-in` kiihtyy loppua kohti ja sopii poistuvalle sisällölle.
- `linear` sopii jatkuvaan liikkeeseen, kuten pyörivään latausmerkkiin,
  ja värin tai läpinäkyvyyden muutokseen.
- `ease` on oletus, ja `cubic-bezier(x1, y1, x2, y2)` määrittelee
  oman käyrän. Kehittäjätyökaluissa käyrää voi muokata kokeilemalla.

## Mitä kannattaa animoida

Selain piirtää sivun vaiheittain: asettelu (koot ja paikat),
maalaus (pikselit) ja koostaminen (valmiiden kerrosten yhdistäminen).
Animoitava ominaisuus ratkaisee, mistä vaiheesta jokainen kehys
alkaa:

| Ominaisuus | Työ joka kehyksellä | Sujuvuus |
|----------------------------------|----------------------|-------------------|
| `transform`, `opacity` | vain koostaminen | hyvä |
| `color`, `background-color`, `box-shadow` | maalaus | yleensä riittävä |
| `width`, `height`, `margin`, `top` | asettelu ja maalaus | nykii helposti |

Liike tehdään siksi `transform`-ominaisuudella: `translate()` siirtää,
`scale()` skaalaa ja `rotate()` kiertää elementtiä muuttamatta
asettelua. Muu sisältö ei liiku, vaikka elementti näyttää siirtyvän.
Esimerkin painike nousee `translateY(-2px)`-muunnoksella, ei
marginaalia muuttamalla. Huomaa, että `transform` ja alle yhden
`opacity` muodostavat pinoutumiskontekstin (luku 11).

## Avainkehykset

Siirtymällä on kaksi tilaa ja se tarvitsee muutoksen käynnistyäkseen.
`@keyframes` kuvaa animaation, jossa on useita vaiheita, joka voi
toistua ja joka alkaa heti, kun elementti on sivulla:

```{.css tiedosto="esimerkit/14-avainkehykset.html" osa="avainkehykset"}
```

```{.html tiedosto="esimerkit/14-avainkehykset.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/14-avainkehykset.odotettu"}
```

- `@keyframes` nimeää animaation ja sen vaiheet prosentteina
  (`from` on 0 % ja `to` 100 %). Puuttuva alku tai loppu on elementin
  oma tyyli, joten `pyori` tarvitsee vain loppuarvon.
- `animation` liittää animaation elementtiin: nimi, kesto,
  ajoitusfunktio ja toistojen määrä (`infinite` toistaa loputtomasti).
  Muita osia ovat `animation-delay`, `animation-direction: alternate`
  (edestakaisin) ja `animation-fill-mode: forwards` (loppuarvot jäävät
  voimaan).
- Latausmerkki on koriste (`aria-hidden="true"`). Tieto välittyy
  tekstinä `role="status"`-elementissä, jonka sisällön muutokset
  ruudunlukija lukee ääneen.

Raportissa animaation nimi on `sykki`, ei `pyori`: vähennetyn liikkeen
tilassa pyöriminen on vaihdettu rauhalliseen läpinäkyvyyden
vaihteluun.

## Vähennetty liike

Osalle käyttäjistä liike ruudulla aiheuttaa huimausta, pahoinvointia
tai migreenin, ja keskittymistä se häiritsee monella muullakin.
Käyttöjärjestelmän asetus "vähennä liikettä" välittyy sivulle
mediakyselynä `prefers-reduced-motion: reduce` (luku 12). Asetus ei
tarkoita, että kaikki animaatiot poistetaan, vaan että *liike*
poistetaan:

| Tavallinen | Vähennetty |
|------------------------------------|------------------------------|
| liukuminen, zoomaus, pyöriminen | häivytys tai välitön vaihto |
| värin ja läpinäkyvyyden siirtymät | säilyvät |
| automaattisesti toistuva liike | pysäytetään tai korvataan |
| parallaksi, vierityksen kaappaus | poistetaan |

Kummassakin esimerkissä tyylit on kirjoitettu tämän mukaan.
Painikkeen värisiirtymä säilyy, mutta nousu poistuu, ja latausmerkki
sykkii pyörimisen sijaan. Koska testausselain pyytää aina vähennettyä
liikettä, raportit näyttävät juuri nämä muunnelmat. Samalla testi
varmistaa, että vähennetty tila on olemassa.

Lisäksi WCAG edellyttää, että yli viisi sekuntia kestävän, itsestään
alkavan liikkeen voi pysäyttää, ja kieltää yli kolme kertaa
sekunnissa välkkyvän sisällön.

## Käytännössä

- **Liike on lisä, ei edellytys.** Sisällön on oltava näkyvissä ja
  toiminnon käytettävissä, vaikka animaatio ei koskaan käynnistyisi.
  Älä piilota sisältöä lähtötilaan, josta vain animaatio tuo sen
  esiin.
- **Animoi `transform` ja `opacity`.** Kokojen ja paikkojen animointi
  teettää asettelun joka kehyksellä.
- **Lyhyt kesto, `ease-out`.** 150–300 millisekuntia riittää lähes
  kaikkeen.
- **Kirjoita vähennetyn liikkeen tyylit samalla kertaa.** Jälkikäteen
  ne jäävät tekemättä. Kehittäjätyökalujen *Rendering*-välilehdeltä
  asetuksen voi kytkeä päälle kokeilua varten.
- **Älä animoi kaikkea.** Usein toistuva toiminto (rivin valinta,
  välilehden vaihto) on parempi ilman viivettä. Liike kuuluu
  harvinaisiin, suuriin muutoksiin, joissa se auttaa hahmottamaan,
  mistä sisältö tuli.
- **Monimutkainen liike kuuluu JavaScriptille.** Käyttäjän eleeseen
  sidotut tai toisistaan riippuvat animaatiot tehdään Web Animations
  API:lla. CSS riittää tilanvaihdoksiin ja latausmerkkeihin.

## Itsearviointi

- Osaat lisätä painikkeeseen tai linkkiin siirtymän ja selittää
  `transition`-lyhenteen osat.
- Osaat valita keston ja ajoitusfunktion käyttötarkoituksen mukaan.
- Osaat kertoa, miksi liike tehdään `transform`-ominaisuudella eikä
  kokoa tai paikkaa muuttamalla.
- Osaat kirjoittaa toistuvan animaation `@keyframes`-säännöllä.
- Osaat toteuttaa vähennetyn liikkeen muunnelman ja selittää, mitä
  asetus käyttäjälle merkitsee.

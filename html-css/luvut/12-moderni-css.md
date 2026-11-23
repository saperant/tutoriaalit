# Moderni CSS ja ylläpidettävyys

Viime vuosina CSS:ään on tullut ominaisuuksia, joihin ennen tarvittiin
esikääntäjää tai JavaScriptiä: sisäkkäiset säännöt, vanhemman valitsin
`:has()`, kaskadikerrokset ja konttikyselyt. Tämä luku esittelee kaksi
ensimmäistä ja kokoaa ylläpidettävän CSS:n ja suorituskyvyn käytännöt.

## :has()

`:has()` valitsee elementin sen sisällön perusteella. Se on ensimmäinen
tapa tyylitellä vanhempaa lapsen tilan mukaan:

```{.css tiedosto="esimerkit/12-has.html" osa="has"}
```

```{.html tiedosto="esimerkit/12-has.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/12-has.odotettu"}
```

Kuvallinen kortti on kaksisarakkeinen (teksti alkaa kohdasta `x=112`),
kuvaton yksisarakkeinen. Valitun vaihtoehdon nimiö on lihavoitu ilman
skriptiä. Muita tavallisia käyttöjä:

- `form:has(:user-invalid) .laheta` tyylittelee lähetyspainikkeen,
  kun lomakkeessa on virhe.
- `.kentta:has(input:focus-visible)` korostaa koko kenttäryhmän.
- `body:has(dialog[open])` estää taustan vierityksen.

`:has()` on tehokas, mutta laaja käyttö (`body:has(...)`) pakottaa
selaimen tarkistamaan tyylit uudelleen jokaisessa muutoksessa. Valitsin
kannattaa rajata komponenttiin.

## Sisäkkäiset säännöt

CSS tukee sisäkkäisiä sääntöjä ilman esikääntäjää:

```{.css tiedosto="esimerkit/12-sisakkain.html" osa="sisakkain"}
```

```{.html tiedosto="esimerkit/12-sisakkain.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/12-sisakkain.odotettu"}
```

`&` viittaa ympäröivään valitsimeen; `& h2` on `.ilmoitus h2` ja
`&.virhe` on `.ilmoitus.virhe`. Mediakyselyn voi kirjoittaa säännön
sisään, jolloin komponentin kaikki tyylit ovat yhdessä paikassa.
Testinäkymä on 1024 px eli yli 60rem, joten täyte on 24 px. Sisäkkäisyys
lisää spesifisyyttä samoin kuin kirjoitettu valitsin, joten yli kahden
tason syvyyttä vältetään, kuten Sassissa.

## Ylläpidettävä CSS

- **Komponentti on rajattu kokonaisuus.** Jokaisella komponentilla on
  oma juuriluokkansa ja tiedostonsa, eikä komponentti oleta mitään
  sijainnistaan sivulla. Ulkoiset marginaalit ja leveydet antaa
  käyttävä asettelu, ei komponentti itse.
- **Nimeämiskäytäntö.** *BEM* (*Block Element Modifier*):
  `.kortti`, `.kortti__otsikko`, `.kortti--korostettu`. Yksi luokka per
  valitsin ja nimestä näkee rakenteen. *Utility-first* (Tailwind):
  luokat ovat yksittäisiä ominaisuuksia (`p-4 flex gap-2`) suoraan
  HTML:ssä, jolloin CSS ei kasva sivuston mukana, mutta HTML pitenee.
  *Rajatut tyylit* (CSS-modulit, Vue- ja Svelte-komponentit) tekevät
  luokkanimistä yksilöllisiä automaattisesti. Valinta riippuu tiimistä
  ja kehyksestä; tärkeintä on käyttää yhtä tapaa johdonmukaisesti.
- **Kerrokset** (luku 6) järjestävät nollauksen, perustyylit,
  komponentit ja apuluokat niin, että järjestys ei riipu tiedostojen
  latausjärjestyksestä.
- **Tokenit** (luku 11) pitävät arvot yhdessä paikassa. Taikaluku
  `margin: 13px` on CSS:n vastine kovakoodatulle vakiolle.
- **Progressiivinen parantaminen `@supports`-säännöllä.** Uusi
  ominaisuus kirjoitetaan toimivan perusratkaisun päälle:
  `@supports (container-type: inline-size) { ... }` lisää
  konttikyselyt vain selaimille, jotka tukevat niitä. Usein mitään ei
  tarvita, koska selain ohittaa tuntemattoman esittelyn ja käyttää
  edellistä.
- **Tarkistin.** Stylelint löytää virheelliset ominaisuudet, toistot ja
  käytäntöjen rikkomukset, ja Prettier yhtenäistää muotoilun.

## Suorituskyky

CSS estää sivun piirtämisen, kunnes se on ladattu ja jäsennetty
(*render-blocking*). Tavalliset keinot:

- **Kriittinen CSS.** Ensimmäiseen näkymään tarvittavat tyylit
  upotetaan `<style>`-elementtiin `<head>`-osaan, ja loput ladataan
  tavallisesti. Tämä kannattaa vain, kun mittaus osoittaa tyylien
  latauksen hidastavan ensimmäistä piirtoa.
- **Ei `@import`-ketjuja.** `@import` tyylitiedostossa lataa tiedostot
  peräkkäin. Kokoa tiedostot rakennusvaiheessa tai käytä useita
  `<link>`-elementtejä.
- **Fontit.** Itse isännöidyt WOFF2-fontit, vain tarvittavat leikkaukset,
  `font-display: swap` ja kriittisen fontin esilataus
  (`<link rel="preload">`). Järjestelmäfontit (`system-ui`) eivät
  maksa mitään.
- **Kuvien mitat** estävät asettelun siirtymät (luku 3), ja
  `aspect-ratio` tekee saman CSS:llä upotuksille.
- **`content-visibility: auto`** lykkää näkymän ulkopuolisten osien
  asettelun ja piirron pitkillä sivuilla.
- **Animoi `transform`- ja `opacity`-ominaisuuksia.** Ne lasketaan
  ilman uutta asettelua; `width`, `top` tai `margin` laukaisevat
  asettelun jokaisella ruudulla.
- **Valitsimien tehokkuudesta ei tarvitse huolehtia.** Selaimet
  sovittavat valitsimet nopeasti; mittaa ennen kuin optimoit.

Core Web Vitals -mittarit (LCP, INP, CLS) mittaavat käyttäjän kokemaa
nopeutta, ja Lighthouse sekä selaimen *Performance*-näkymä kertovat,
mikä niitä hidastaa. Suorituskyvyn analyysi yleisellä tasolla kuuluu
taitoon *Web-sovellukset*.

## Käytännössä

- **Selaintuki ratkaistaan Baseline-tasolla.** Määrittele projektille
  tukitaso (esimerkiksi "Baseline laajasti saatavilla"), ja käytä
  sen kattamia ominaisuuksia ilman paikkauksia. Työkalut kuten
  Browserslist ja Stylelintin tukisäännöt valvovat sitä.
- **Vähemmän CSS:ää on parempi CSS.** Luontaiset asettelut, perityt
  arvot ja tokenit vähentävät sääntöjen määrää. Jokainen poikkeussääntö
  on ylläpitokohde.
- **Poista käyttämätön.** Kun komponentti poistetaan, sen tyylitiedosto
  poistetaan samalla. Tämä on helppoa, kun tyylit ovat komponentin
  vieressä eivätkä yhteisessä tiedostossa.

## Itsearviointi

- Osaat tyylitellä elementin sen sisällön tai lapsen tilan perusteella
  `:has()`-valitsimella ja rajata sen käytön.
- Osaat kirjoittaa sisäkkäisiä sääntöjä ja kertoa, miten ne vaikuttavat
  spesifisyyteen.
- Osaat perustella nimeämiskäytännön valinnan (BEM, utility-first,
  rajatut tyylit) ja jäsentää tyylit komponenteittain.
- Osaat nimetä CSS:n suorituskyvyn tärkeimmät tekijät: estävä lataus,
  fontit, asettelun siirtymät ja animaatiot.

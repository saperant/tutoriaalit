---
title: HTML ja CSS
subtitle: Pikaopas · semanttinen HTML, saavutettavuus ja moderni CSS
---

# Sivupohja

```{.html tiedosto="esimerkit/pikaopas.html" osa="pohja"}
```

```{.html tiedosto="esimerkit/pikaopas.html" osa="runko"}
```

`<html lang="fi">` ja `<!doctype html>` aina. Title muodossa
*sivu – sivusto*; virhesivulla alkuun "Virhe:".

# Elementit

| Tarve | Elementti |
|-------|-----------|
| maamerkit | `header` `nav` `main` `aside` `footer` `search` |
| itsenäinen kokonaisuus | `article`; nimetty osio `section` + otsikko |
| luettelot | `ul` järjestämätön, `ol` vaiheet, `dl` nimi–arvo |
| aika, lyhenne | `<time datetime>`, `<abbr title>` |
| kuva + teksti | `figure` + `figcaption` |
| vie jonnekin / tekee jotain | `<a href>` / `<button type>` |
| laajennettava | `details` + `summary`, modaali `<dialog>` |
| taulukko | `caption`, `th scope` (`col`, `row`), `thead`, `tbody` |

# Saavutettavuus

| Asia | Sääntö |
|------|--------|
| `alt` | tieto tai toiminto; koriste `alt=""` |
| nimi | näkyvä teksti > `aria-labelledby` > `aria-label` |
| piilotus | vain ruudulta: `clip-path`-luokka; kaikilta: `hidden` |
| ARIA | natiivi ensin; `aria-current`, `-describedby`, `-invalid`, `-hidden` |
| fokus | `:focus-visible`, ei positiivista `tabindex`iä |
| kontrasti | teksti 4,5:1, iso teksti ja reunat 3:1 |
| kohteet | vähintään 24 × 24 px |
| lomake | `label`, `fieldset`+`legend`, `autocomplete`, virhe tekstinä |

# Kaskadi

Järjestys: alkuperä ja `!important` → `style` → `@layer` (myöhempi
voittaa, kerrokseton voittaa kerrokset) → spesifisyys → järjestys.

| Valitsin | Spesifisyys |
|----------|-------------|
| `#id` | 1,0,0 |
| `.luokka` `[attr]` `:hover` | 0,1,0 |
| `p` `::before` | 0,0,1 |
| `:where()` `*` | 0 |
| `:is()` `:not()` `:has()` | tarkin argumentti |

Periytyy: `color`, `font`, `line-height`, `text-*`. Ei periydy:
`margin`, `padding`, `border`, `background`, `width`. Lomake-elementit:
`font: inherit`. Avainsanat `inherit` `initial` `unset` `revert`.

```{.css tiedosto="esimerkit/pikaopas.html" osa="nollaus"}
```

# Asettelu

| Tarve | Ratkaisu |
|-------|----------|
| koko leveys, keskitetty palsta | `max-inline-size` + `margin-inline: auto` |
| luettava rivi | `max-inline-size: 65ch` |
| palkki, ryhmät reunoille | flex + `margin-inline-start: auto` |
| yhtä leveät sarakkeet | flex `flex: 1` tai grid `1fr` |
| kuva + teksti | flex; kuva `flex: none`, teksti `min-inline-size: 0` |
| korttiruudukko | `repeat(auto-fit, minmax(min(100%, 15rem), 1fr))` |
| sivun runko | `grid-template-areas` + mediakysely |
| linjatut kortit | `grid-template-rows: subgrid` |
| keskitys | `display: grid; place-items: center` |
| komponentin muoto | `container-type: inline-size` + `@container` |
| sujuva koko | `clamp(1.5rem, 1rem + 2.5vw, 3rem)` |

```{.css tiedosto="esimerkit/pikaopas.html" osa="asettelu"}
```

# Laatikko ja yksiköt

- `box-sizing: border-box`; pystymarginaalit yhdistyvät normaalissa
  virtauksessa, eivät flexissä eikä gridissä.
- Loogiset: `inline-size`, `block-size`, `margin-inline`,
  `padding-block`, `inset-inline-start`, `text-align: start`.
- `rem` fonteille, väleille ja rajapisteille; `px` reunoille; `ch`
  palstalle; `dvh` koko näkymälle; `fr` gridiin.

# Teemat ja kyselyt

- Primitiivit (`--sininen-700`) → semanttiset (`--pinta`, `--teksti`,
  `--korostus`) → komponentit.
- `var(--x, varavara)`; virheellinen arvo → periytyvä/alkuarvo;
  `@property` tyypitykseen.
- `@media (prefers-color-scheme: dark)`, `[data-teema]`-ohitus,
  `color-scheme: light dark`.
- `prefers-reduced-motion`, `prefers-contrast`, `forced-colors`,
  `hover`, `pointer`.
- `:has()`, sisäkkäiset säännöt `&`, `@supports`, `color-mix()`.

# Sudenkuopat

- `placeholder` ei ole nimiö; `outline: none` ilman korvaajaa.
- `display: none` piilottaa myös ruudunlukijalta.
- `order` ja grid-sijoittelu eivät muuta fokusjärjestystä.
- Flex- ja grid-kohteen `min-inline-size: auto` → ylivuoto.
- `100vh` mobiilissa liian korkea → `100dvh`.
- `type="number"` postinumerolle → `inputmode="numeric"`.
- Kiinteä `height` tekstille; `px`-fontit ohittavat käyttäjän koon.

# Työkalut

| Tarkoitus | Työkalu |
|-----------|---------|
| HTML | `html-validate sivu.html`, validator.w3.org/nu |
| saavutettavuus | axe, Lighthouse, NVDA/VoiceOver, näppäimistö |
| CSS | Stylelint, Prettier |
| tuki | MDN Baseline, caniuse.com |
| tutkiminen | kehittäjätyökalut: Computed, Accessibility, grid/flex-peitot |

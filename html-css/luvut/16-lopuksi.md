# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

HTML:

1. Elementti merkityksen mukaan; `<div>` ja `<span>` vain ryhmittelyyn.
2. Maamerkit (`header`, `nav`, `main`, `footer`), yksi `<h1>` ja ehjä
   otsikkohierarkia.
3. Linkki vie, painike tekee. Linkin teksti kertoo kohteen.
4. Jokaisella kuvalla `alt`, koristeilla tyhjä; jokaisella kuvalla
   `width` ja `height`.
5. Jokaisella kentällä `<label>`, sopiva `type` ja `autocomplete`.
   Virheet tekstinä kentän vieressä ja yhteenvetona.
6. Natiivi elementti ennen ARIA:a.
7. Validaattori jatkuvassa integraatiossa.

CSS:

8. `box-sizing: border-box`, kevyt nollaus ja `font: inherit`
   lomake-elementeille.
9. Matala, tasainen spesifisyys: yksi luokka per valitsin, ei
   tunnisteita, kerrokset järjestämään.
10. Loogiset ominaisuudet ja `rem`-yksiköt oletuksena.
11. Rivikorkeus paljaana lukuna, tekstipalsta enintään noin 65 merkkiä,
    fonttikoot `rem`-yksiköissä.
12. Grid runkoon, flexbox komponentteihin, `gap` väleihin.
13. Asemointi vain osille, joiden kuuluu olla muun sisällön päällä.
    Kun `z-index` ei toimi, etsi pinoutumiskonteksti; dialogit
    `<dialog>`-elementillä.
14. Luontaiset asettelut ensin (`auto-fit`, `flex-wrap`, `clamp()`),
    mediakyselyt mobile first, konttikyselyt komponentteihin.
15. Arvot tokeneista; semanttiset tokenit teemoille.
16. Liike lyhyenä ja `transform`- ja `opacity`-ominaisuuksilla;
    vähennetyn liikkeen muunnelma kirjoitetaan samalla kertaa.
17. Näkyvä fokus, kontrasti vähintään 4,5:1, käyttäjän asetukset
    (`prefers-reduced-motion`, `prefers-color-scheme`) kunnioitettuina.

Testaus:

18. Saavutettavuuspuu, näppäimistö, 200 %:n zoomaus ja 320 pikselin
    leveys jokaiselle uudelle näkymälle.

## Mihin tästä

- *Web-sovellukset*: DOM, tapahtumat, lomakkeiden käsittely
  JavaScriptillä, saavutettavat dynaamiset komponentit ja suorituskyky.
- *Web-sovelluskehykset ja niiden periaatteet*: sama sovellus
  Reactilla, Vuella, Angularilla ja Sveltellä sekä kehysten yhteiset
  periaatteet.
- *JavaScript*: kieli itse.
- *Tietoturvan perusteet*: XSS, sisällön turvallisuuskäytäntö (CSP) ja
  lomakkeiden suojaus.

## Lähteet ja jatkolukeminen

- **MDN Web Docs** (<https://developer.mozilla.org>) on kattavin
  HTML- ja CSS-hakuteos: jokaisen elementin ja ominaisuuden kuvaus,
  selaintuki ja Baseline-tila. Sisältö on lisensoitu CC BY-SA 2.5
  -lisenssillä.
- **HTML Living Standard** (<https://html.spec.whatwg.org>), WHATWG.
  Erityisesti luvut elementeistä ja lomakkeista. Lisenssi CC BY 4.0.
- **CSS-määrittelyt** (<https://www.w3.org/Style/CSS/>) ja CSS-työryhmän
  vuosittainen *CSS Snapshot*.
- **WCAG 2.2** (<https://www.w3.org/TR/WCAG22/>) sekä sen selitykset
  *Understanding WCAG 2.2* ja *Techniques*. Suomenkieliset
  ohjeet ja lainsäädäntö: <https://www.saavutettavuusvaatimukset.fi>.
- **ARIA Authoring Practices Guide** (<https://www.w3.org/WAI/ARIA/apg/>)
  saavutettavien komponenttien mallit näppäimistökäyttöineen.
- **web.dev** (<https://web.dev/learn>): Googlen kurssit *Learn HTML*,
  *Learn CSS*, *Learn Accessibility* ja *Learn Forms*. Lisenssi
  CC BY 4.0.
- **GOV.UK Design System** (<https://design-system.service.gov.uk>):
  tutkittuja lomake- ja virheilmoitusmalleja. Avoin lisenssi (Open
  Government Licence / MIT).
- **Kirjat**: Heydon Pickering ja Andy Bell, *Every Layout*
  (luontaiset asettelut); Heydon Pickering, *Inclusive Components*;
  Adam Silver, *Form Design Patterns*; Rachel Andrew, *The New CSS
  Layout*.
- **WebAIM** (<https://webaim.org>): saavutettavuusartikkelit,
  kontrastilaskuri ja vuosittainen *WebAIM Million* -tutkimus.

### Työkalut

- **html-validate** (<https://html-validate.org>) ja W3C:n Nu-
  validaattori HTML:n tarkistukseen.
- **axe DevTools** ja **Lighthouse** automaattisiin
  saavutettavuustarkistuksiin; **Accessibility Insights** ohjattuun
  käsin testaukseen.
- **Stylelint** (<https://stylelint.io>) CSS:n tarkistukseen ja
  **Prettier** muotoiluun.
- **caniuse.com** ja MDN:n Baseline-merkinnät selaintukeen.
- **Playwright** (<https://playwright.dev>) selaintesteihin ja
  saavutettavuuspuun tilannekuviin, kuten tämän tutoriaalin esimerkeissä.

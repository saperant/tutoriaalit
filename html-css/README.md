# HTML ja CSS

Tiivis suomenkielinen tutoriaali verkkosivujen rakenteesta ja
ulkoasusta: semanttinen HTML, saavutettavuus ja moderni CSS-asettelu.
Valmiit dokumentit: [html-css.pdf](html-css.pdf) ja pikaopas
[html-css-pikaopas.pdf](html-css-pikaopas.pdf).

## Sisältö

1. Johdanto – historia ja standardit, työkalut, esimerkkien testaus
2. Dokumentin rakenne ja semantiikka – maamerkit, otsikot, linkit
3. Kuvat, grafiikka ja taulukot – `alt`, `srcset`, SVG, taulukko-otsikot
4. Lomakkeet – nimiöt, kenttätyypit, selaimen tarkistus, virheet
5. Saavutettavuus – WCAG 2.2, rooli–nimi–tila, fokus, kontrasti
6. Kaskadi, periytyminen ja spesifisyys – `:where()`, `@layer`
7. Laatikkomalli ja normaali virtaus – `box-sizing`, loogiset
   ominaisuudet, yksiköt
8. Flexbox – palkki, `flex`-lyhenne, ylivuodon sudenkuoppa
9. Grid – `auto-fit`, nimetyt alueet, `subgrid`
10. Responsiivisuus – mobile first, `clamp()`, konttikyselyt,
    käyttäjän asetukset
11. Mukautetut ominaisuudet ja teemat – suunnittelutokenit, tumma teema
12. Moderni CSS ja ylläpidettävyys – `:has()`, sisäkkäisyys,
    nimeämiskäytännöt, suorituskyky
13. Lopuksi – nyrkkisäännöt, lähteet

## Esimerkit ja testaus

Esimerkit ovat hakemistossa `esimerkit/`: yksittäiset `.html`-sivut ja
hakemistot, joissa on `index.html` ja tyylitiedostot. Jokainen esimerkki
tarkistetaan html-validatella (`../yhteiset/htmlvalidate.json`) ja
avataan Chromiumissa (`../yhteiset/selain.cjs`), joka tulostaa
saavutettavuuspuun ja pyydetyt mitat ja lasketut tyylit. Tulostetta
verrataan `.odotettu`-tiedostoon.

```text
make testaa   # html-validate ja Chromium-raportit
make pdf      # rakentaa html-css.pdf:n ja html-css-pikaopas.pdf:n
make kuvat    # päivittää kuvakaappaukset hakemistoon kuvat/
              # (Playwright ja ImageMagick)
```

Yksittäisen sivun voi avata suoraan selaimessa tai tarkistaa käsin:
`node ../yhteiset/selain.cjs esimerkit/09-asettelu/index.html`.
Kehityskontti: `.devcontainer/html-css`.

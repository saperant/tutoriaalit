# Grid

Grid asettelee lapsensa kahteen suuntaan yhtä aikaa: sarakkeisiin ja
riveihin. Se sopii sivun runkoon, korttiruudukoihin ja kaikkeen, missä
kohteiden pitää olla linjassa sekä vaaka- että pystysuunnassa. Nyrkkisääntö:
flexbox, kun sisältö määrää koon; grid, kun asettelu määrää.

## Sarakkeet ja fr-yksikkö

```{.css tiedosto="esimerkit/09-kortit.html" osa="ruudukko"}
```

```{.html tiedosto="esimerkit/09-kortit.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-kortit.odotettu"}
```

- `fr` on osuus vapaasta tilasta, kun kiinteät sarakkeet ja `gap` on
  vähennetty.
- `minmax(240px, 1fr)` tarkoittaa: vähintään 240 pikseliä, muuten tasan
  jaettu osuus. `min(100%, 240px)` estää ylivuodon, kun kontti on
  kapeampi kuin 240 pikseliä.
- `repeat(auto-fit, ...)` tekee niin monta saraketta kuin mahtuu:
  360 pikselissä yksi, 700 pikselissä kaksi ja 1024 pikselissä kolme.
  Responsiivinen ruudukko ilman yhtään mediakyselyä.
- `auto-fit` venyttää kohteet täyttämään rivin, kun kohteita on vähän;
  `auto-fill` jättää tyhjät sarakkeet paikoilleen.

## Nimetyt alueet

Sivun runko on luontevinta kuvata nimetyillä alueilla. Kapea
asettelu on oletus, ja leveä lisätään mediakyselyllä (*mobile first*,
luku 10):

```{.css tiedosto="esimerkit/09-asettelu/tyyli.css" osa="alueet"}
```

```{.html tiedosto="esimerkit/09-asettelu/index.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-asettelu.odotettu"}
```

![Sivupohja 1024 pikselin levyisenä.](kuvat/09-asettelu-1024.png){width=70%}
![Sama sivupohja 360 pikselin levyisenä.](kuvat/09-asettelu-360.png){width=25%}

Kuvakaappaukset: vasemmalla 1024 pikselin ja oikealla 360 pikselin
näkymä.

- `grid-template-areas` piirtää asettelun merkkijonoina; sama nimi
  vierekkäisissä soluissa yhdistää ne alueeksi.
- Rivit `auto 1fr auto` pitävät ylä- ja alaosan sisältönsä korkuisina
  ja venyttävät pääsisällön, jolloin alaosa pysyy näkymän pohjalla
  lyhyelläkin sivulla (`min-block-size: 100vh`).
- `minmax(0, 1fr)` pääpalstan sarakkeena estää pitkän sisällön
  levittämästä saraketta (luvun 8 sudenkuoppa gridissä).
- HTML:n järjestys pysyy loogisena (otsikko, sisältö, sivupalkki,
  alaosa). Grid muuttaa vain sijoittelua, joten näppäimistön ja
  ruudunlukijan järjestys säilyy.

## Alikehys

Korttiruudukossa korttien sisällöt eivät oletuksena ole linjassa:
pitkä kuvaus työntää yhden kortin painikkeen alemmas kuin muiden.
`subgrid` antaa kortin käyttää isäntäruudukon rivejä, jolloin samat
osat asettuvat samalle riville kaikissa korteissa:

```{.css tiedosto="esimerkit/09-alikehys.html" osa="alikehys"}
```

```{.html tiedosto="esimerkit/09-alikehys.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/09-alikehys.odotettu"}
```

Alikehyksellä kaikkien korttien linkit ovat samalla korkeudella
(`y=231`). Ilman sitä (kortit `ilman`, sama HTML ilman alikehystä)
linkit ovat eri korkeuksilla sen mukaan, kuinka pitkä kuvaus on.

## Sijoittelu ja kohdistus

- `grid-column: 1 / -1` venyttää kohteen kaikkien sarakkeiden yli;
  `span 2` kahden.
- `justify-items` ja `align-items` kohdistavat kohteet soluissaan,
  `place-items: center` molemmat kerralla. Elementin keskittäminen
  vaaka- ja pystysuunnassa on gridillä kaksi riviä:
  `display: grid; place-items: center`.
- Rivit syntyvät automaattisesti, kun kohteita on enemmän kuin
  määriteltyjä soluja; niiden koon antaa `grid-auto-rows`.

## Käytännössä

- **Grid runkoon, flexbox komponentteihin.** Sivun pääalueet,
  lomakkeiden nimiö–kenttä-ruudukot ja korttilistat ovat gridiä;
  palkit ja painikeryhmät flexboxia. Valinta ei ole ehdoton, mutta
  tämä jako tuottaa yksinkertaisimman CSS:n.
- **Luontainen asettelu** (*intrinsic layout*). `auto-fit` ja
  `minmax()` sopeuttavat ruudukon tilaan ilman rajapisteitä. Jos
  asettelu tarvitsee mediakyselyn vain sarakemäärän vaihtamiseen,
  `auto-fit` on yleensä parempi.
- **Gap kaikkialle.** Sama `gap` gridissä ja flexboxissa antaa
  yhtenäisen rytmin, kun arvo tulee suunnittelujärjestelmän tilatokenista
  (luku 11).
- **Kehittäjätyökalujen grid-peittokuva** näyttää rivit, sarakkeet ja
  alueiden nimet suoraan sivun päällä. Se on nopein tapa ymmärtää,
  miksi kohde on väärässä paikassa.

## Itsearviointi

- Osaat tehdä responsiivisen korttiruudukon `repeat(auto-fit,
  minmax())`-mallilla ilman mediakyselyjä.
- Osaat kuvata sivun rungon nimetyillä alueilla ja muuttaa sen
  rajapisteessä.
- Osaat linjata korttien sisällöt alikehyksellä.
- Osaat perustella, milloin käytät gridiä ja milloin flexboxia.

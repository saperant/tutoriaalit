# Asemointi ja pinoaminen

Flexbox ja grid asettelevat elementit vierekkäin ja allekkain niin,
etteivät ne peitä toisiaan. Joskus elementin kuuluu olla toisen
*päällä* tai pysyä paikallaan vierityksen aikana: merkki kortin
kulmassa, pudotusvalikko, tarttuva yläpalkki tai dialogi. Niihin
käytetään `position`-ominaisuutta. Samalla on päätettävä, mikä
päällekkäisistä elementeistä näkyy päällimmäisenä.

## position

| Arvo | Paikka virrassa | Sijainti lasketaan |
|--------------------|----------------|------------------------------------------|
| `static` (oletus) | on | normaali virtaus; siirtymät eivät vaikuta |
| `relative` | on | omasta paikasta; tila jää varatuksi |
| `absolute` | ei | lähimmästä asemoidusta esivanhemmasta |
| `fixed` | ei | näkymästä; ei liiku vieritettäessä |
| `sticky` | on | omasta paikasta, kunnes tarttuu vierityskontin reunaan |

Sijainti annetaan `inset`-ominaisuuksilla. Loogiset nimet
(`inset-block-start`, `inset-inline-end`) noudattavat kirjoitussuuntaa
kuten luvun 7 marginaalit; fyysiset vastineet ovat `top`, `right`,
`bottom` ja `left`. Lyhenne `inset: 0` venyttää elementin koko
sisältävän lohkon kokoiseksi.

Asemoitu elementti, jonka arvo on `absolute` tai `fixed`, poistuu
virrasta: muut elementit asettuvat kuin sitä ei olisi. Siksi
asemointi ei ole sivun asettelun väline. Sarakkeet, palkit ja
keskittäminen tehdään flexboxilla ja gridillä, ja asemointia käytetään
vain, kun elementin kuuluu olla muun sisällön päällä.

## Absoluuttinen asemointi ja sisältävä lohko

Absoluuttisesti asemoidun elementin sijainti lasketaan sen
**sisältävästä lohkosta** (*containing block*). Se on lähin
esivanhempi, jonka `position` on muu kuin `static`. Jos sellaista ei
ole, sijainti lasketaan sivun alusta:

```{.css tiedosto="esimerkit/11-merkki.html" osa="merkki"}
```

```{.html tiedosto="esimerkit/11-merkki.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/11-merkki.odotettu"}
```

![Vasemmalla merkki on kortin kulmassa. Oikealla vanhempaa ei ole
asemoitu, ja merkki karkaa sivun kulmaan.](kuvat/11-merkki-640.png){width=80%}

Kortin A merkki on kahdeksan pikseliä kortin ylä- ja loppureunasta.
Kortin B merkki käyttää samoja tyylejä, mutta koska kortilta puuttuu
`position: relative`, merkki on sivun oikeassa yläkulmassa (`y=8`).
`position: relative` ilman siirtymiä ei liikuta korttia mihinkään;
sen ainoa tehtävä tässä on tehdä kortista lastensa sisältävä lohko.

Kaksi muuta asiaa on hyvä tietää:

- Absoluuttisesti asemoitu elementti ei vie tilaa, joten sen alle
  jäävälle sisällölle on varattava tila itse (esimerkiksi täytteellä).
- Kun vastakkaiset reunat on molemmat annettu (`inset-inline: 0`),
  elementti venyy niiden väliin. Näin tehdään peite, joka kattaa koko
  vanhempansa: `position: absolute; inset: 0`.

## Tarttuva asemointi

`position: sticky` käyttäytyy kuin tavallinen elementti, kunnes se
vieritettäessä saavuttaa annetun etäisyyden vierityskontin reunasta.
Sen jälkeen se pysyy paikallaan niin kauan kuin sen vanhempi on
näkyvissä:

```{.css tiedosto="esimerkit/11-tarttuva.html" osa="tarttuva"}
```

```{.html tiedosto="esimerkit/11-tarttuva.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/11-tarttuva.odotettu"}
```

![Luetteloa on vieritetty 100 pikseliä: otsikko A on tarttunut
yläreunaan.](kuvat/11-tarttuva-400.png){width=45%}

Testi vierittää luetteloa 100 pikseliä. Rivi "Aalto" on vierinyt
kontin yläpuolelle (`y=-13`), mutta otsikko A on yhä kontin
yläreunassa (`y=55`). Kun ryhmä A loppuu, otsikko H työntää sen pois
ja tarttuu vuorostaan. Tavallisimmat käytöt ovat sivun yläpalkki,
taulukon otsikkorivi (`thead th`) ja pitkän sivun sisällysluettelo.

Jos `sticky` ei tartu, syy on yleensä jokin näistä:

- Etäisyys puuttuu. Ilman `inset-block-start`-arvoa elementillä ei
  ole reunaa, johon tarttua.
- Jollakin esivanhemmalla on `overflow: hidden` tai `auto`. Elementti
  tarttuu *lähimpään* vierityskonttiin, ja jos se ei vieri, mitään ei
  tapahdu.
- Vanhempi on yhtä korkea kuin elementti itse, joten liikkumavaraa ei
  ole.

Vierivä alue, jossa ei ole kohdistettavia elementtejä, tarvitsee
`tabindex="0"`-attribuutin ja nimen, jotta sitä voi vierittää
näppäimistöllä (luku 5).

`position: fixed` kiinnittää elementin näkymään. Se sopii harvoin
tarvittaviin, koko sivun yläpuolella oleviin osiin, kuten
ilmoituksiin. Kiinteä palkki peittää pysyvästi osan näytöstä, mikä
tuntuu erityisesti puhelimessa ja suurennetussa näkymässä, ja se voi
peittää näppäimistöllä kohdistetun elementin. `sticky` on yleensä
parempi valinta, ja ankkurilinkkien kohdille varataan palkin verran
tilaa ominaisuudella `scroll-margin-block-start`.

## Pinoutumisjärjestys ja z-index

Kun elementit ovat päällekkäin, selain piirtää ne järjestyksessä:
ensin asemoimattomat, sitten asemoidut dokumenttijärjestyksessä.
Myöhempi elementti peittää aiemman. `z-index` muuttaa järjestystä:
suurempi luku on päällimmäisenä. Se vaikuttaa vain asemoituihin
elementteihin sekä flex- ja grid-kohteisiin.

Luvut eivät kuitenkaan ole koko sivun yhteisiä. Tietyt elementit
muodostavat **pinoutumiskontekstin** (*stacking context*): niiden
jälkeläisten `z-index`-arvoja verrataan vain keskenään, ja koko
konteksti sijoittuu ympäristöönsä yhtenä kerroksena. Tämä on
tavallisin syy siihen, että "z-index ei toimi":

```{.css tiedosto="esimerkit/11-pinot.html" osa="pinot"}
```

```{.html tiedosto="esimerkit/11-pinot.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/11-pinot.odotettu"}
```

![Vasemmalla valikko jää ilmoituksen alle arvostaan 9999 huolimatta.
Oikealla kortti ei muodosta omaa
kontekstiaan.](kuvat/11-pinot-720.png){width=95%}

Vasemmalla kortti (`z-index: 1`) muodostaa pinoutumiskontekstin.
Valikon 9999 pätee vain kortin sisällä; ulospäin koko kortti
valikkoineen on kerroksessa 1 ja jää ilmoituksen (2) alle. Arvon
kasvattaminen ei auta. Oikealla kortin `z-index` on `auto`, jolloin
se ei muodosta kontekstia ja valikon arvoa verrataan suoraan
ilmoituksen arvoon. Toinen korjaus olisi nostaa koko kortti
ilmoituksen yläpuolelle (`z-index: 3`).

Pinoutumiskontekstin muodostavat muun muassa:

- asemoitu elementti, jonka `z-index` on muu kuin `auto`
- `position: fixed` ja `sticky`
- `opacity` alle 1, `transform`, `filter` ja `will-change`
- `isolation: isolate` sekä konttikyselyn kontti (`container-type`)

Luettelon kolmas kohta yllättää: häivytys tai siirtymäanimaatio
(luku 14) muuttaa pinoutumista, vaikka `z-index`-arvoihin ei kosketa.
`transform` tekee elementistä lisäksi `fixed`-jälkeläistensä
sisältävän lohkon, jolloin "kiinteä" elementti vierii vanhempansa
mukana.

`isolation: isolate` muodostaa kontekstin tarkoituksella ilman
sivuvaikutuksia. Komponentin juuressa se pitää komponentin sisäiset
`z-index`-arvot (1, 2, 3) komponentin sisällä, eivätkä ne kilpaile
muun sivun kanssa.

## Ylin kerros: dialogi

Modaalinen dialogi, eli ikkuna, joka on suljettava ennen kuin muuta
sivua voi käyttää, on perinteisesti tehty `position: fixed`
-elementillä ja suurella `z-index`-arvolla. `<dialog>`-elementti
tekee saman ilman kumpaakaan:

```{.html tiedosto="esimerkit/11-dialogi.html" osa="rakenne"}
```

```{.css tiedosto="esimerkit/11-dialogi.html" osa="tyyli"}
```

```{.html tiedosto="esimerkit/11-dialogi.html" osa="skripti"}
```

```{.tuloste tiedosto="esimerkit/11-dialogi.odotettu"}
```

![Avattu dialogi ja sen taustaverho peittävät yläpalkin, jonka
`z-index` on 9999.](kuvat/11-dialogi-560.png){width=60%}

- `showModal()` nostaa dialogin **ylimpään kerrokseen** (*top
  layer*), joka on kaikkien pinoutumiskontekstien yläpuolella.
  Raportin mukaan yläpalkin kohdalla päällimmäisenä on dialogi
  (tarkemmin sen taustaverho `::backdrop`), vaikka palkin `z-index`
  on 9999.
- Selain siirtää fokuksen dialogiin (raportissa painikkeeseen
  "Peru"), pitää sen siellä, sulkee dialogin Esc-näppäimellä ja
  palauttaa fokuksen avanneeseen painikkeeseen. Muu sivu ei ole
  käytettävissä dialogin ollessa auki.
- `<form method="dialog">` sulkee dialogin ilman JavaScriptiä, ja
  painikkeen `value` jää dialogin `returnValue`-ominaisuuteen.
- Dialogi tarvitsee nimen (`aria-labelledby`). Se näkyy
  saavutettavuuspuussa dialogin nimenä.

Avaamiseen tarvitaan yksi rivi JavaScriptiä. Ilman sitäkin onnistuvat
kevyemmät ponnahdusosat: attribuutti `popover` tekee elementistä
ylimpään kerrokseen avautuvan valikon tai vihjeen, jonka painike avaa
attribuutilla `popovertarget` ja joka sulkeutuu napsautuksesta
muualle. Itse tehtyä modaalia tai pudotusvalikkoa ei näiden jälkeen
juuri tarvita.

## float

`float: left` ja `right` siirtävät elementin rivin reunaan ja antavat
tekstin kiertää sen. Ennen flexboxia ja gridiä kellutuksilla tehtiin
koko sivun asettelu, ja vanhassa koodissa niitä näkee yhä
(`clearfix`-luokkineen). Nykyään kellutuksella on yksi käyttö:
tekstin sisään upotettu kuva, jonka ympäri leipäteksti rivittyy.
Loogiset arvot ovat `inline-start` ja `inline-end`.

## Käytännössä

- **Asettelu ensin ilman asemointia.** Jos `position: absolute`
  -elementtejä on paljon, asettelu on todennäköisesti tehtävissä
  gridillä: myös grid-kohteet voi asettaa päällekkäin samaan soluun.
- **Pieni `z-index`-asteikko.** Sovi sivuston kerrokset (esimerkiksi
  sisältö, tarttuva palkki, ilmoitukset) ja anna niille nimet
  mukautettuina ominaisuuksina (luku 13). Arvot 9999 ja 99999
  kertovat, että pinoutumiskonteksti on jäänyt selvittämättä.
- **Etsi konteksti, älä kasvata lukua.** Kun elementti jää väärän
  alle, käy esivanhemmat läpi ja etsi, mikä niistä muodostaa
  pinoutumiskontekstin. Kehittäjätyökalujen kerrosnäkymä (*Layers*)
  auttaa.
- **Dialogit ja valikot ylimpään kerrokseen.** `<dialog>` ja
  `popover` ohittavat koko `z-index`-kilpailun ja hoitavat fokuksen.
- **Asemoitu sisältö ei saa peittää fokusta.** Tarttuvan palkin alle
  jäävä kohdistettu linkki on WCAG 2.2:n virhe (*Focus Not Obscured*).

## Itsearviointi

- Osaat valita `position`-arvon ja kertoa, mistä elementin sijainti
  kussakin lasketaan.
- Osaat asemoida elementin vanhempansa kulmaan ja selittää, miksi
  vanhempi tarvitsee `position: relative` -määrityksen.
- Osaat tehdä tarttuvan otsikon ja selvittää, miksi `sticky` ei
  tartu.
- Osaat selittää pinoutumiskontekstin ja korjata tilanteen, jossa
  suuri `z-index` ei nosta elementtiä päällimmäiseksi.
- Osaat tehdä modaalisen dialogin `<dialog>`-elementillä.

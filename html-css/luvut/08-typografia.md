# Teksti ja typografia

Suurin osa verkkosivusta on tekstiä, ja luettavuus ratkeaa muutamalla
valinnalla: fontti, koko, rivikorkeus ja rivin pituus. Tässä luvussa
käydään ne läpi. Yksiköt (`rem`, `em`, `ch`) esiteltiin luvussa 7.

## Fontti ja fonttipino

`font-family` on luettelo fontteja tärkeysjärjestyksessä. Selain
käyttää ensimmäistä, joka laitteesta löytyy, ja jokaiselle merkille
erikseen: jos fontista puuttuu merkki, se haetaan seuraavasta.
Luettelon viimeisenä on aina **yleinen perhe**, joka löytyy
kaikkialta:

| Yleinen perhe | Merkitys |
|---------------|----------|
| `serif` | päätteellinen (kirjatyyli) |
| `sans-serif` | päätteetön |
| `monospace` | tasalevyinen (koodi) |
| `system-ui` | käyttöjärjestelmän käyttöliittymäfontti |

Nopein ja varmin valinta on järjestelmän oma fontti:
`font-family: system-ui, sans-serif`. Se ei lataa mitään, ja teksti
näyttää laitteessa kotoisalta. Koodille vastaava pino on
`ui-monospace, "Cascadia Code", Menlo, Consolas, monospace`.
Välilyöntejä sisältävät nimet kirjoitetaan lainausmerkkeihin.

Fontti, koko ja rivikorkeus periytyvät, joten ne asetetaan kerran
`body`-elementille. Lomake-elementit eivät oletuksena peri fonttia;
`font: inherit` korjaa sen (luku 7).

## Koko: rem ja em

Tekstin peruskoko on käyttäjän selaimeen asettama, oletuksena 16
pikseliä. Sivu ei muuta sitä (`html { font-size: 10px; }` ohittaisi
käyttäjän valinnan), vaan ilmaisee muut koot suhteessa siihen.
`rem` on suhteessa juuren kokoon ja `em` vanhemman kokoon, mikä
kertautuu sisäkkäin:

```{.css tiedosto="esimerkit/08-koko.html" osa="koko"}
```

```{.html tiedosto="esimerkit/08-koko.html" osa="rakenne"}
```

```{.tuloste tiedosto="esimerkit/08-koko.odotettu"}
```

Sisäkkäinen `em`-luettelo on jo 25 pikseliä (16 · 1,25 · 1,25), mutta
`rem`-luettelo pysyy 20 pikselissä. Fonttikoot annetaan siksi
`rem`-yksiköissä. `em` sopii mittoihin, joiden kuuluu seurata
elementin omaa tekstikokoa, kuten painikkeen täyte tai otsikon
alamarginaali.

Kokoja tarvitaan vähän. Tavallinen asteikko on leipäteksti (1rem),
pieni teksti (0,875rem) ja kolme tai neljä otsikkokokoa, joiden
suhde on noin 1,2–1,25. Leipätekstiä ei pienennetä alle 16 pikselin.

## Rivikorkeus

`line-height` on rivin korkeus, ja ylimääräinen tila jakautuu rivin
ylä- ja alapuolelle. Arvo annetaan **paljaana lukuna**, ei pituutena.
Raportin loppuosa näyttää syyn:

```{.css tiedosto="esimerkit/08-koko.html" osa="rivi"}
```

```{.html tiedosto="esimerkit/08-koko.html" osa="otsikot"}
```

Luku periytyy kertoimena, ja jokainen elementti laskee rivikorkeutensa
omasta fonttikoostaan: 32 pikselin otsikko saa 48 pikselin rivin.
Pituus (`24px`, `1.5em`) lasketaan kerran ja periytyy valmiina
arvona, jolloin sama otsikko saa 24 pikselin rivin. Se on kirjaimia
matalampi, ja kahdelle riville jakautuva otsikko menisi päällekkäin.

Leipätekstille sopii 1,5–1,6 (WCAG edellyttää, että sivu toimii
vähintään arvolla 1,5) ja otsikoille 1,1–1,3, koska suuressa tekstissä
sama kerroin näyttää harvalta.

## Rivin pituus ja ladonta

Sama teksti selaimen oletustyyleillä ja ladottuna:

```{.css tiedosto="esimerkit/08-artikkeli.html" osa="typografia"}
```

```{.tuloste tiedosto="esimerkit/08-artikkeli.odotettu"}
```

![Ylhäällä oletustyylit: rivi on koko ikkunan levyinen. Alhaalla sama
teksti 65 merkin palstana.](kuvat/08-artikkeli-1024.png){width=85%}

- **Rivin pituus** on 45–75 merkkiä. `max-inline-size: 65ch` rajaa
  palstan noin 65 merkkiin fontista ja koosta riippumatta (raportissa
  710 px, josta 48 px on täytettä). Kapeassa näkymässä palsta
  kutistuu, koska arvo on maksimi.
- **Rivikorkeus** on otsikossa 1,2, ingressissä 1,4 ja leipätekstissä
  1,6. Lasketut arvot näkyvät raportissa pikseleinä.
- **`text-wrap: balance`** jakaa otsikon rivit tasapituisiksi, jolloin
  viimeiselle riville ei jää yksinäistä sanaa. Leipätekstille vastaava
  on `text-wrap: pretty`. Molemmat ovat parannuksia: selain, joka ei
  tue niitä, rivittää tavalliseen tapaan.
- **Tasaus** on vasen liehu (`text-align: start`, oletus). Molempien
  reunojen tasaus (`justify`) tekee kapeaan palstaan epätasaiset
  sanavälit, ja keskitetty teksti sopii vain lyhyisiin otsikoihin.
- **`font-variant-numeric: tabular-nums`** tekee numeroista
  tasalevyisiä, jolloin taulukon luvut asettuvat allekkain.
- **Kappaleväli** tehdään marginaalilla, ei tyhjillä riveillä tai
  `<br>`-elementeillä.

Esimerkissä fonttipinon ensimmäisenä on DejaVu Sans, jotta raportin
mitat ovat samat kaikilla koneilla. Omassa sivustossa pino alkaisi
`system-ui`-fontilla tai sivuston omalla fontilla.

Suomen pitkät yhdyssanat eivät aina mahdu kapealle riville.
`hyphens: auto` tavuttaa tekstin `lang`-attribuutin kielen säännöillä,
jos selaimessa on kielen tavutussanasto; siksi `lang="fi"` kuuluu
jokaiselle sivulle (luku 2). `overflow-wrap: anywhere` (luku 7) on
varakeino katkeamattomille merkkijonoille.

## Paino, kursiivi ja korostus

`font-weight` on luku 100–900 (`normal` on 400 ja `bold` 700) ja
`font-style: italic` kursiivi. Korostuksen *merkitys* kuuluu
HTML:ään: `<strong>` on tärkeä ja `<em>` painotettu, ja CSS päättää,
miltä ne näyttävät. Jos fontista puuttuu pyydetty paino, selain
lihavoi tai kallistaa kirjaimet keinotekoisesti, mikä näyttää
suttuiselta. Ladattavasta fontista tarvitaan siis jokainen käytetty
paino.

Muita hyödyllisiä ominaisuuksia:

| Ominaisuus | Käyttö |
|-----------------------------|------------------------------------------|
| `letter-spacing` | hieman väljempi versaaliteksti (`0.05em`) |
| `text-transform: uppercase` | versaalit ulkoasuna; HTML:ssä teksti on tavallista |
| `text-decoration` | alleviivaus; `text-underline-offset` siirtää viivaa |
| `white-space: nowrap` | estää rivityksen (lyhyt nimiö, luku ja yksikkö) |
| `text-overflow: ellipsis` | katkaisee yksirivisen tekstin kolmella pisteellä |

Katkaistu teksti (`ellipsis`) piilottaa sisältöä. Sitä käytetään
vain, kun koko teksti on saatavilla muualta, esimerkiksi luettelon
rivin takaa aukeavalta sivulta.

## Web-fontit

Oman fontin käyttö tarkoittaa, että selain lataa fonttitiedoston.
`@font-face` antaa fontille nimen ja kertoo, mistä se haetaan:

```{.css tiedosto="esimerkit/08-fontti.html" osa="fontti"}
```

```{.tuloste tiedosto="esimerkit/08-fontti.odotettu"}
```

`src` on luettelo lähteitä, joista käytetään ensimmäinen kelpaava.
`local()` etsii koneelle asennettua fonttia ja `url()` lataa
tiedoston. Testikoneessa DejaVu Sans on asennettu, joten tiedostoa
ei haeta ja raportin viimeinen rivi kertoo fontin olevan käytössä.
Sivustolla `local()` jätetään yleensä pois, jotta kaikki kävijät
saavat saman version fontista.

- **WOFF2** on pakattu fonttimuoto, jota kaikki nykyselaimet tukevat.
  Muita muotoja ei tarvita.
- **`font-display: swap`** näyttää tekstin heti varafontilla ja
  vaihtaa fontin, kun se on ladattu. Oletuskäytös piilottaa tekstin
  latauksen ajaksi, jolloin hitaalla yhteydellä sivu on hetken tyhjä.
- **Muuttuva fontti** (*variable font*) sisältää kaikki painot yhdessä
  tiedostossa, joten usean painon käyttö ei moninkertaista latauksia.
- **Fontti omalta palvelimelta.** Kolmannen osapuolen fonttipalvelu
  on ylimääräinen yhteys ja välittää kävijän IP-osoitteen palvelun
  tarjoajalle.
- Fontin vaihtuminen voi siirtää sisältöä, jos varafontin mitat
  poikkeavat. Siirtymä pienenee, kun varafontti valitaan
  samanlevyiseksi; tarvittaessa `@font-face`-säännön `size-adjust`
  sovittaa varafontin mitat.

Jokainen fontti on latausta ja ylläpitoa. Yksi fonttiperhe, enintään
kaksi, riittää lähes aina, ja järjestelmäfontti on täysin kelvollinen
valinta.

## Käytännössä

- **Aseta perusta kerran.** `body { font: 1rem/1.5 system-ui,
  sans-serif; }` ja otsikoille oma rivikorkeus. Loput periytyy.
- **Rajaa palsta, älä tekstiä.** `max-inline-size: 65ch` kuuluu
  tekstisisällön kontille, jolloin kuvat ja taulukot voivat olla
  leveämpiä.
- **Tarkista suurennettuna.** Selaimen tekstin suurennus 200 %:iin ei
  saa leikata tekstiä eikä tuoda vaakavieritystä. Kiinteät korkeudet
  ja pikselikoot paljastuvat tässä.
- **Kontrasti kuuluu typografiaan.** Ohut, vaaleanharmaa teksti on
  vaikealukuista, vaikka kontrastisuhde täyttyisi niukasti (luku 5).
- **Älä välitä tietoa pelkällä tyylillä.** Lihavointi tai väri ei
  näy ruudunlukijalle; käytä merkitykseen `<strong>`- ja
  `<em>`-elementtejä.

## Itsearviointi

- Osaat kirjoittaa fonttipinon ja selittää, miksi se päättyy yleiseen
  perheeseen.
- Osaat valita `rem`- ja `em`-yksikön välillä ja ennustaa
  sisäkkäisten `em`-kokojen tuloksen.
- Osaat selittää, miksi rivikorkeus annetaan paljaana lukuna.
- Osaat latoa luettavan tekstipalstan: rivin pituus, rivikorkeus ja
  otsikoiden rivitys.
- Osaat ottaa web-fontin käyttöön niin, että teksti näkyy latauksen
  aikana.

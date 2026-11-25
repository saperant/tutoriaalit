# Fysiikka ja törmäysvaste

Edellinen luku kertoi, koskettavatko kappaleet ja kuinka paljon ne ovat
sisäkkäin. Tämä luku kertoo, miten kappaleet liikkuvat ja mitä
kosketuksen jälkeen tehdään: ensin liike (integrointi ja hyppy), sitten
*törmäysvaste* kolmella tasolla. Hahmo pysäytetään seinään, pallot
kimpoavat toisistaan ja pino pysyy pystyssä.

Pelifysiikan tavoite ei ole todellisuus vaan uskottava, vakaa ja
hallittava liike. Kappaleen tila on paikka ja nopeus, ja voimat
muuttavat nopeutta. Tila päivitetään luvun *Pelisilmukka* kiinteällä
aika-askeleella *integraattorilla*, ja integraattorin valinta
ratkaisee, pysyykö simulaatio vakaana.

## Integraattorit

Jousi on hyvä testi: energian pitäisi säilyä, ja kappaleen pitäisi
heilua samaa rataa loputtomiin.

```{.cpp tiedosto="esimerkit/08-integraattorit.cpp" osa="integraattorit"}
```

```{.tuloste tiedosto="esimerkit/08-integraattorit.odotettu"}
```

![Sama jousi kolmella integraattorilla. Vasemmalla paikka kolmen
ensimmäisen sekunnin aikana, oikealla energian suhde alkuenergiaan
logaritmisella asteikolla. Eksplisiittisen Eulerin energia kasvaa
jokaisella askeleella samalla kertoimella, kaksi muuta pysyvät tarkan
ratkaisun päällä.](kuvat/energia.png){width=95%}

- **Eksplisiittinen Euler** päivittää paikan vanhalla nopeudella.
  Jokainen askel lisää energiaa, ja jousi räjähtää: kymmenessä
  sekunnissa energia on kasvanut satojatuhansia kertoja.
- **Semi-implisiittinen Euler** päivittää ensin nopeuden ja sitten
  paikan uudella nopeudella. Laskentaa on yhtä paljon, mutta energia
  heilahtelee eikä karkaa. Se on pelien oletusintegraattori, myös
  Box2D:ssä.
- **Nopeus-Verlet** laskee kiihtyvyyden kahdesti ja on tarkempi.
  Paikkapohjainen Verlet (ilman eksplisiittistä nopeutta) sopii
  köysille, kankaille ja ragdolleille, koska rajoitteet voi toteuttaa
  siirtämällä pisteitä.

Integraattorin vakaus riippuu askeleen pituudesta suhteessa
järjestelmän jäykkyyteen. Jäykkä jousi tarvitsee lyhyemmän askeleen
tai alaskeleita (substepping). Kiinteä aika-askel on siksi myös
fysiikan edellytys: muuttuvalla askeleella yksi hidas ruutu voi viedä
vakaan simulaation epävakaalle alueelle. Menetelmien virheen
kertaluvut ja vakausalueet käsittelee taito *Numeeriset menetelmät*,
ja jousen kaltaisten järjestelmien tarkat ratkaisut taito
*Differentiaaliyhtälöt ja Laplace-muunnos*.

## Hyppy suunnitellaan, ei kokeilla

Pelisuunnittelija ajattelee korkeutta ja aikaa, ei painovoimaa.
Kun hyppy nousee korkeudelle *h* ajassa *t*, liikeyhtälöistä saadaan
painovoima ja alkunopeus suoraan.

```{.cpp tiedosto="esimerkit/08-hyppy.cpp" osa="parametrit"}
```

Hyvä tasohyppely ei noudata fysiikkaa: lyhyt painallus tuottaa matalan
hypyn, ja putoaminen on nousua nopeampaa, jolloin hyppy tuntuu
hallitulta eikä leijuvalta.

```{.cpp tiedosto="esimerkit/08-hyppy.cpp" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/08-hyppy.odotettu"}
```

![Kolme hyppyä samoilla parametreilla. Lyhyt painallus katkaisee
nousun, ja raskas pudotus lyhentää ilma-aikaa muuttamatta
huippua.](kuvat/hyppy.png){width=70%}

Simuloitu huippu jää neljä prosenttia lasketusta, koska
semi-implisiittinen Euler vähentää painovoiman nopeudesta ennen
ensimmäistä siirtoa. Ero on sama kaikilla koneilla, koska askel on
kiinteä; tarvittaessa alkunopeutta korjataan puolen askeleen verran.

## Hahmo ja ruutukartta

Yksinkertaisin vaste on *kinemaattinen*: hahmoa siirretään, ja jos se
päätyy kiinteän ruudun sisään, se työnnetään takaisin ruudun reunaan ja
nopeus siihen suuntaan nollataan. Hahmo on akselien suuntainen laatikko
ja maailma ruutukartta, joten tarkistettavat ruudut saadaan suoraan
laatikon reunoista.

```{.cpp tiedosto="esimerkit/08-hahmo.cpp" osa="hahmo"}
```

Liike ratkaistaan *akseli kerrallaan*. Jos hahmo siirrettäisiin
molempiin suuntiin yhtä aikaa ja työnnettäisiin ulos lyhintä tietä,
lattiaa pitkin juokseva hahmo voisi tarttua ruutujen saumoihin, koska
sauman kohdalla lyhin tie ulos on välillä sivulle. Kun vaakaliike
ratkaistaan ensin ja pystyliike sen jälkeen, tulosuunta tiedetään:
vaakaliikkeen osuma on seinä ja pystyliikkeen osuma lattia tai katto.

```{.cpp tiedosto="esimerkit/08-hahmo.cpp" osa="akselit"}
```

Tieto `maassa` syntyy sivutuotteena: hahmo on maassa, jos alaspäin
suuntautunut liike osui johonkin. Hyppy sallitaan vain silloin.

```{.cpp tiedosto="esimerkit/08-hahmo.cpp" osa="askel"}
```

Esimerkin tallennettu syöte juoksee oikealle ja painaa hyppyä kolmesti.

```{.tuloste tiedosto="esimerkit/08-hahmo.odotettu"}
```

![Hahmon keskipisteen rata ruutu ruudulta. Ensimmäinen hyppy osuu
tasanteen kylkeen, liukuu sitä pitkin ylös ja laskeutuu tasanteelle.
Toinen hyppy osuu ylemmän tasanteen kylkeen ja putoaa. Laatikot
näyttävät hahmon koon.](kuvat/hahmo.png){width=95%}

Hahmo ei tunneloidu, koska se liikkuu askeleessa enintään noin 0,3 metriä
ja ruutu on metrin levyinen. Nopeammalle kappaleelle liike jaetaan
osiin tai käytetään luvun *Törmäykset* pyyhkäisytestiä.

## Impulssivaste

Kun kaksi liikkuvaa kappaletta törmää, kumpikaan ei ole seinä.
Molempien nopeutta muutetaan törmäysnormaalin suunnassa yhtä suurella
ja vastakkaisella *impulssilla*, jolloin liikemäärä säilyy.
*Kimmokerroin* e kertoo, kuinka suuri osa lähestymisnopeudesta palaa
erkanemisnopeudeksi: 1 on täysin kimmoisa, 0 jättää kappaleet
liikkumaan yhdessä.

```{.cpp tiedosto="esimerkit/08-impulssi.cpp" osa="kappale"}
```

Kappaleeseen tallennetaan *käänteismassa*. Silloin liikkumaton kappale
on käänteismassa 0 eikä erikoistapaus: seinä ei siirry eikä sen nopeus
muutu, koska kaikki siirrot ja impulssit kerrotaan nollalla.

```{.cpp tiedosto="esimerkit/08-impulssi.cpp" osa="vaste"}
```

Vasteessa on kaksi vaihetta samassa järjestyksessä kuin edellisen luvun
neuvossa. Ensin limitys puretaan siirtämällä kappaleita erilleen,
kevyempää enemmän. Sitten lasketaan impulssi
j = −(1 + e) · v~n~ / (1/m~a~ + 1/m~b~), missä v~n~ on suhteellinen
nopeus normaalin suunnassa. Jos kappaleet jo erkanevat, impulssia ei
anneta; muuten ne liimautuisivat yhteen.

```{.tuloste tiedosto="esimerkit/08-impulssi.odotettu"}
```

Liikemäärä on sama ennen ja jälkeen jokaisella kimmokertoimella, mutta
liike-energiaa jää sitä vähemmän, mitä pienempi e on. Vinossa osumassa
seinään muuttuu vain normaalin suuntainen nopeus; seinän suuntainen
säilyy, ellei kitkaa mallinneta erikseen.

## Lepäävät kosketukset

Lattialla makaava kappale törmää lattiaan joka askeleella, koska
painovoima antaa sille joka askeleella uutta nopeutta alaspäin. Tästä
seuraa kaksi tuttua vikaa: pallo, joka ei koskaan lakkaa pomppimasta,
ja pino, joka vajoaa itsensä läpi.

```{.cpp tiedosto="esimerkit/08-kosketus.cpp" osa="kynnys"}
```

Pinossa jokainen kosketus riippuu naapureistaan. Kun alin kosketus
pysäyttää alimman laatikon, toiseksi alin törmää siihen, ja korjaus
etenee ylöspäin yhden kosketuksen kierroksessa. Fysiikkamoottorit
ratkaisevat kosketukset siksi *iteroimalla*: sama kierros toistetaan
useita kertoja askeleessa.

```{.cpp tiedosto="esimerkit/08-kosketus.cpp" osa="pino"}
```

```{.tuloste tiedosto="esimerkit/08-kosketus.odotettu"}
```

Yhdellä kierroksella neljän metrin pino on vajonnut kahdessa
sekunnissa lähes kaksi metriä, kuudellatoista kolme senttimetriä.
Sijainnin korjaus poistaa jo syntynyttä limitystä vähän kerrallaan ja
auttaa eniten, kun kierroksia on vähän. Kierrosten määrä on suora
kauppa tarkkuuden ja laskenta-ajan välillä, ja korkeat pinot ovat
kaikille iteroiville ratkaisijoille vaikeita.

## Käytännössä

- **Semi-implisiittinen Euler ja kiinteä askel** ovat pelifysiikan
  oletus. Älä integroi muuttuvalla `dt`:llä.
- **Parametrit suunnittelijan kielellä:** hypyn korkeus, aika
  huippuun, kiihtymisaika huippunopeuteen. Fysiikan vakiot lasketaan
  niistä.
- **Kitka ja vaimennus** kertoimena askelessa (`v *= 0.98`) riippuu
  askeleen pituudesta; kiinteällä askeleella se on toistettava.
- **Vasteen taso tarpeen mukaan.** Tasohyppelyn hahmo ja ruutukartta
  tarvitsevat vain pysäytyksen akseli kerrallaan. Impulssit tarvitaan,
  kun kappaleet työntävät toisiaan.
- **Valmis fysiikkamoottori** (Box2D, Jolt, PhysX, Bullet) kannattaa,
  kun tarvitaan pinoja, niveliä, kitkaa ja pyöriviä jäykkiä kappaleita:
  ne ovat tämän luvun kosketusten ratkaisua monin verroin laajempana.
  Hahmon ohjaus tehdään silti usein itse (*kinemaattinen hahmo*),
  koska fysiikalla ohjattu hahmo tuntuu liukkaalta.
- **Lepotila** (sleeping): paikallaan pysyvät kappaleet jätetään pois
  simulaatiosta, kunnes jokin osuu niihin. Se säästää laskentaa ja
  poistaa värinän.
- **Hinta:** tarkempi integraattori tai alaskeleet maksavat laskentaa
  jokaisella askeleella. Valitse tarkkuus sen mukaan, mitä pelaaja
  huomaa.

## Itsearviointi

- Osaat selittää, miksi eksplisiittinen Euler lisää energiaa ja miksi
  semi-implisiittinen Euler ei.
- Osaat valita integraattorin (semi-implisiittinen Euler, Verlet)
  tilanteen mukaan.
- Osaat laskea hypyn painovoiman ja alkunopeuden halutusta korkeudesta ja
  ajasta ja toteuttaa vaihtelevan hypyn korkeuden.
- Osaat toteuttaa hahmon törmäyksen ruutukarttaan akseli kerrallaan ja
  päätellä siitä, onko hahmo maassa.
- Osaat laskea kahden kappaleen törmäysimpulssin käänteismassoilla ja
  kimmokertoimella ja tarkistaa, että liikemäärä säilyy.
- Osaat selittää, miksi lepäävät kosketukset tarvitsevat lepokynnyksen,
  iteroinnin ja sijainnin korjauksen.

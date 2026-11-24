# Fysiikka

Pelifysiikan tavoite ei ole todellisuus vaan uskottava, vakaa ja
hallittava liike. Kappaleen tila on paikka ja nopeus, ja voimat
muuttavat nopeutta. Kiinteällä aika-askeleella tila päivitetään
*integraattorilla*, ja integraattorin valinta ratkaisee, pysyykö
simulaatio vakaana.

## Integraattorit

Jousi on hyvä testi: energian pitäisi säilyä, ja kappaleen pitäisi
heilua samaa rataa loputtomiin.

```{.cpp tiedosto="esimerkit/08-integraattorit.cpp" osa="integraattorit"}
```

```{.tuloste tiedosto="esimerkit/08-integraattorit.odotettu"}
```

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
tai alaskeleita (substepping).

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

Simuloitu huippu jää neljä prosenttia lasketusta, koska
semi-implisiittinen Euler vähentää painovoiman nopeudesta ennen
ensimmäistä siirtoa. Ero on sama kaikilla koneilla, koska askel on
kiinteä; tarvittaessa alkunopeutta korjataan puolen askeleen verran.

## Käytännössä

- **Semi-implisiittinen Euler ja kiinteä askel** ovat pelifysiikan
  oletus. Älä integroi muuttuvalla `dt`:llä.
- **Parametrit suunnittelijan kielellä:** hypyn korkeus, aika
  huippuun, kiihtymisaika huippunopeuteen. Fysiikan vakiot lasketaan
  niistä.
- **Kitka ja vaimennus** kertoimena askelessa (`v *= 0.98`) riippuu
  askeleen pituudesta; kiinteällä askeleella se on toistettava.
- **Valmis fysiikkamoottori** (Box2D, Jolt, PhysX, Bullet) kannattaa,
  kun tarvitaan pinoja, niveliä ja jäykkiä kappaleita. Hahmon ohjaus
  tehdään silti usein itse (*kinemaattinen hahmo*), koska fysiikalla
  ohjattu hahmo tuntuu liukkaalta.
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

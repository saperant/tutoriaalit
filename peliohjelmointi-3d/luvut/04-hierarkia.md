# Muunnoshierarkia

Maailman kappaleet eivät ole toisistaan riippumattomia: kontti roikkuu
koukussa, koukku vaunussa ja vaunu nosturin puomissa. Taito
*Peliohjelmointi* esitteli näkymäpuun ja sen läpikäynnin matriiseilla.
Tässä luvussa hierarkia tehdään niin kuin se pelissä tarvitaan:
paikallinen muunnos osina, maailmamatriisi välimuistina, uudelleenlaskenta
vain muuttuneille haaroille ja vanhemman vaihto kesken pelin.

## Paikallinen ja maailma

Jokaisella solmulla on *paikallinen muunnos* vanhempansa
koordinaatistossa. Se on pelin tilaa: sitä muutetaan, animoidaan ja
tallennetaan. *Maailmamatriisi* on johdettua tietoa, joka saadaan
kertomalla vanhemman maailmamatriisi omalla paikallisella matriisilla.

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="puu"}
```

Kaksi ratkaisua pitävät päivityksen halpana. Solmut ovat taulukossa
niin, että vanhempi on aina ennen lasta, jolloin yksi läpikäynti alusta
loppuun riittää eikä rekursiota tarvita. Lisäksi jokaisella solmulla on
*likaisuuslippu*: matriisi lasketaan uudelleen vain, jos solmun oma
muunnos tai jokin sen esivanhemmista on muuttunut. Useimmat maailman
kappaleet eivät liiku useimmilla ruuduilla.

```{.dot otsikko="Nosturin näkymäpuu. Kontti on aluksi maailman lapsi ja kiinnitetään myöhemmin koukkuun."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.25;
  node [width=0, height=0, margin="0.1,0.06"];
  maailma -> alusta -> torni -> puomi -> vaunu -> koukku;
  maailma -> kontti;
  koukku -> kontti [style=dashed, label="kiinnitys", constraint=false];
}
```

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="nosturi"}
```

```{.tuloste tiedosto="esimerkit/04-hierarkia.odotettu" rivit="1-2"}
```

## Vanhemman vaihto

Kun koukku tarttuu konttiin, kontista tulee koukun lapsi. Kontin ei
kuitenkaan pidä hypätä mihinkään: sen maailmamuunnoksen on pysyttävä
samana, vaikka vanhempi vaihtuu. Uusi paikallinen muunnos ratkaistaan
yhtälöstä *uusi vanhempi × paikallinen = nykyinen maailma*:

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="kiinnita"}
```

Käänteismatriisi tarvitaan vain tässä, ja koska muunnos on affiini,
se lasketaan kääntämällä 3 × 3 -osa ja viemällä siirto sen läpi:

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="affiini"}
```

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="nosto"}
```

```{.tuloste tiedosto="esimerkit/04-hierarkia.odotettu" rivit="3-4"}
```

Kiinnityksen jälkeen kontti nousee koukun mukana, ja uudelleen
lasketaan vain kaksi solmua: koukku ja kontti.

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="kaanto"}
```

```{.tuloste tiedosto="esimerkit/04-hierarkia.odotettu" rivit="5-8"}
```

Tornin kääntö muuttaa yhden solmun paikallista muunnosta, mutta
maailmamatriisi vaihtuu viidellä: tornilla ja kaikilla sen
jälkeläisillä. Alusta ei muutu. Kun mikään ei muutu, ei lasketa
mitään.

![Nosturi ennen tornin kääntöä ja sen jälkeen. Kontin paikallinen
muunnos koukun suhteen on molemmissa kuvissa
sama.](kuvat/nosturi.png){width=90%}

Irrotus on sama operaatio toiseen suuntaan: vanhemmaksi tulee maailma,
ja kontti jää siihen, missä se irrotushetkellä oli.

```{.cpp tiedosto="esimerkit/04-hierarkia.cpp" osa="irrotus"}
```

```{.tuloste tiedosto="esimerkit/04-hierarkia.odotettu" rivit="9-10"}
```

## Matriisista takaisin osiksi

Vanhemman vaihto tuottaa uuden paikallisen muunnoksen matriisina, mutta
solmu tallentaa sen osina. Matriisi puretaan: siirto on viimeinen
sarake, skaalat ovat kolmen ensimmäisen sarakkeen pituudet, ja kun
sarakkeet jaetaan pituuksillaan, jäljelle jää kiertomatriisi.

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="hajota"}
```

Kiertomatriisi muutetaan kvaternioksi sen lävistäjän avulla. Neljästä
vaihtoehtoisesta kaavasta valitaan se, jossa jakaja on suurin:

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="matriisista"}
```

## Epäyhtenäinen skaala

Purku onnistuu vain, jos matriisi todella on siirto, kierto ja skaala.
Hierarkiassa näin ei aina ole. Jos vanhempaa on venytetty yhteen
suuntaan ja lasta kierretty, lapsen maailmamatriisissa on *leikkaus*
(*shear*): sen akselit eivät ole enää kohtisuorassa.

```{.cpp tiedosto="esimerkit/04-skaala.cpp" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/04-skaala.odotettu"}
```

Yhtenäisellä skaalalla akselit pysyvät suorassa kulmassa ja purku
palauttaa matriisin täsmälleen. Kun vanhemman skaala on (3, 1, 1),
45 astetta kierretyn lapsen akselien välinen kulma on 143 astetta, eikä
mikään sijainnin, kierron ja skaalan yhdistelmä tuota samaa matriisia.

Seuraukset ovat käytännöllisiä. Vinoon venytetyn vanhemman lapsena
pallo ei ole pallo eikä törmäyskapseli kapseli, ja vanhemman vaihto
muuttaa kappaleen muotoa. Pelimoottorit ratkaisevat tämän eri tavoin:
osa kieltää epäyhtenäisen skaalan fysiikkakappaleilta, osa pudottaa
leikkauksen pois hiljaa.

## Hierarkia ja kiinteä askel

Piirto interpoloi kappaleiden paikat kahden kiinteän askeleen välillä
(taito *Peliohjelmointi*). Kolmessa ulottuvuudessa interpoloidaan
paikallisia muunnoksia funktiolla `sekoita`: sijainti ja skaala
lineaarisesti, kierto slerpillä. Maailmamatriisit lasketaan
interpoloiduista paikallisista muunnoksista, ei toisin päin.

## Käytännössä

- **Paikallinen muunnos on tila, maailmamatriisi välimuisti.** Vain
  paikallista muutetaan; maailma lasketaan siitä.
- **Taulukko, vanhemmat ennen lapsia.** Yksi läpikäynti, muisti
  luetaan järjestyksessä, ei rekursiota.
- **Maailmamatriisi on ajan tasalla vasta päivityksen jälkeen.**
  Tavallinen virhe on lukea lapsen maailmapaikka samalla askeleella,
  jolla vanhempaa siirrettiin, ennen kuin hierarkia on päivitetty.
- **Kiinnitä säilyttäen maailmamuunnos.** Ase käteen, matkustaja
  ajoneuvoon ja esine hyllylle ovat kaikki vanhemman vaihtoja.
- **Vältä epäyhtenäistä skaalaa solmuissa, joilla on lapsia.** Skaalaa
  mieluummin lehtisolmua tai itse verkkoa.
- **Syvä hierarkia ei ole itseisarvo.** Suurin osa maailman kappaleista
  on juuren lapsia. Hierarkiaa käytetään, kun kappaleet todella
  liikkuvat yhdessä.

## Itsearviointi

- Osaat laskea solmun maailmamatriisin paikallisista muunnoksista ja
  selittää, miksi taulukko vanhemmat ennen lapsia riittää yhteen
  läpikäyntiin.
- Osaat toteuttaa likaisuuslipun ja kertoa, mitkä solmut lasketaan
  uudelleen, kun yhden solmun muunnos muuttuu.
- Osaat vaihtaa solmun vanhemman niin, että sen paikka maailmassa
  säilyy, ja purkaa matriisin sijainniksi, kierroksi ja skaalaksi.
- Osaat selittää, miksi epäyhtenäinen skaala vanhemmassa tuottaa
  leikkauksen ja mitä siitä seuraa.

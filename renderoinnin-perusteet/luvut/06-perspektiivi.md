# Perspektiivi

Edellisen luvun lopussa kärjet ovat ruudulla. Rasteroija antaa
jokaiselle pikselille barysentriset painot, ja kärkien arvot
interpoloidaan niillä. Perspektiivissä tämä menee kuitenkin pieleen:
painot ovat lineaarisia **ruudulla**, mutta kärkien arvot (väri,
tekstuurikoordinaatti, normaali) ovat lineaarisia **maailmassa**.
Kaukainen puoli kolmiosta on ruudulla kutistunut, joten ruudun
puoliväli ei ole maailman puoliväli.

## Virhe näkyviin

Seuraava esimerkki piirtää shakkilautalattian kahtena suurena
kolmiona. Varjostimet ovat ensimmäistä kertaa funktioita:
verteksivarjostin muuntaa kärjen ja välittää sen
tekstuurikoordinaatin (`uv`), ja fragmenttivarjostin päättää pikselin
värin interpoloidusta `uv`:stä. Putken rakenne käydään läpi luvussa
*Grafiikkaputki*; tässä riittää, että asetus `perspektiivikorjaus`
valitsee interpolointitavan.

```{.cpp tiedosto="esimerkit/06-perspektiivi.cpp" osa="varjostimet"}
```

```{.cpp tiedosto="esimerkit/06-perspektiivi.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-perspektiivi.odotettu"}
```

![Vasemmalla ruudulla lineaarinen (affiininen) interpolointi,
oikealla perspektiivikorjattu. Lattia on kaksi kolmiota.](kuvat/06-perspektiivi.png){width=85%}

Affiinisesti interpoloitu lattia on vääristynyt: ruudut eivät pienene
kaukana, ja kolmioiden yhteinen lävistäjä näkyy taitteena, koska
kumpikin kolmio vääristyy eri tavalla. Ensimmäisen PlayStationin
pelit näyttivät tältä, koska sen laitteisto osasi vain affiinisen
interpoloinnin. Vaikutusta lievennettiin jakamalla lattiat pieniksi
kolmioiksi.

## Mistä korjaus tulee

Perspektiivijaon jälkeen ruudun koordinaatit ovat muotoa $x/w$ ja
$y/w$. Maailmassa lineaarisesti muuttuva suure $v$ ei ole lineaarinen
ruudulla, mutta suureet $v/w$ ja $1/w$ ovat. Sen voi todeta
kirjoittamalla kolmion tason yhtälön kamerakoordinaateissa ja
jakamalla sen syvyydellä: tason pisteillä $1/w$ on ruudun
koordinaattien lineaarinen funktio, ja sama pätee mihin tahansa
suureeseen, joka on maailmassa lineaarinen ja jaettu $w$:llä.

Oikea arvo saadaan siis interpoloimalla ruudulla kaksi lineaarista
suuretta ja jakamalla ne:

$$v = \frac{\lambda_0 v_0 / w_0 + \lambda_1 v_1 / w_1 + \lambda_2 v_2 / w_2}
           {\lambda_0 / w_0 + \lambda_1 / w_1 + \lambda_2 / w_2}.$$

Käytännössä painot korjataan kerran pikseliä kohden, ja kaikki arvot
interpoloidaan korjatuilla painoilla:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="interpolointi"}
```

Jako $1/w$ lasketaan kärjelle valmiiksi perspektiivijaon yhteydessä,
joten pikselissä tarvitaan kolme kertolaskua ja yksi jakolasku
riippumatta siitä, montako arvoa interpoloidaan:

```{.cpp tiedosto="esimerkit/yhteinen/putki.hpp" osa="ruutu"}
```

## Syvyys on poikkeus

Syvyyttä $z/w$ ei korjata. Se on jo valmiiksi jaettu $w$:llä, joten
se on lineaarinen ruudulla, ja rasteroija interpoloi sen
korjaamattomilla painoilla. Tämä on syvyyspuskurin perusta: arvo on
halpa interpoloida ja sitä voi verrata suoraan. Hintana on, että se
ei ole lineaarinen etäisyyden suhteen (luku *Syvyys ja näkyvyys*).

Näytönohjaimissa perspektiivikorjaus on oletus kaikille vaihteleville
arvoille. GLSL:ssä sen voi kytkeä pois määreellä `noperspective`,
mikä on hyödyllistä ruudun koordinaateissa määritellyille suureille,
kuten rautalankaviivan etäisyydelle reunasta. Määre `flat` puolestaan
ottaa arvon yhdestä kärjestä (provoking vertex) interpoloimatta.

## Mitä kamera tekee kuvalle

Perspektiivin parametrit vaikuttavat kuvaan muutenkin kuin
vääristyminä:

- **Näkökenttä.** Laaja näkökenttä (pieni `f`) venyttää kuvan reunoja,
  koska tasoprojektio levittää reunojen kulmat suuremmalle alalle.
  Pelit käyttävät tyypillisesti 60–90 asteen pystynäkökenttää.
- **Kuvasuhde.** Projektiomatriisin $x$-skaalaus jaetaan kuvasuhteella,
  joten pystynäkökenttä pysyy samana ja vaakanäkökenttä kasvaa
  leveällä ruudulla.
- **Lähi- ja kaukotaso** rajaavat piirrettävän syvyysalueen. Niiden
  suhde ratkaisee syvyyspuskurin tarkkuuden, ja lähitaso on myös
  leikkaustaso (luku *Leikkaus*).
- **Ortografinen projektio** jättää perspektiivin pois: $w$ pysyy
  ykkösenä, eikä korjausta tarvita. Sitä käytetään CAD-ohjelmissa,
  karttanäkymissä ja varjokartoissa suunnatulle valolle.

## Käytännössä

- **Interpoloi perspektiivikorjatusti** kaikki maailmassa
  määritellyt arvot. Affiininen interpolointi kelpaa vain ruudun
  suuntaisille kolmioille ja 2D-grafiikkaan.
- **Laske $1/w$ kerran kärkeä kohden** ja korjaa painot kerran
  pikseliä kohden; sen jälkeen interpolointi on yhtä halpaa kuin
  ilman korjausta.
- **Syvyys interpoloidaan korjaamatta**, koska $z/w$ on jo lineaarinen
  ruudulla.
- **Jos tekstuuri näyttää taittuvan kolmioiden rajalla**, epäile
  interpolointia: korjaus puuttuu tai $w$ on hukattu matkalla.

## Itsearviointi

- Osaat selittää, miksi ruudulla lineaarinen interpolointi on väärin
  perspektiivissä.
- Osaat johtaa perspektiivikorjatun interpoloinnin kaavan siitä, että
  $v/w$ ja $1/w$ ovat lineaarisia ruudulla.
- Osaat kertoa, miksi syvyyttä ei tarvitse korjata.
- Osaat kuvata näkökentän, kuvasuhteen ja ortografisen projektion
  vaikutuksen kuvaan.

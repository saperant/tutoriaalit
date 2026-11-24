# Johdanto {.runko-johdanto}

Lineaarialgebra on matematiikkaa, jota ohjelmoija käyttää useammin kuin
huomaa. Kolmiulotteinen peli kääntää ja siirtää kappaleita matriiseilla,
kuvankäsittely vaihtaa värikoordinaatteja, anturin kalibrointi sovittaa
suoran kohinaiseen dataan, hakukone laskee sivujen tärkeyden
ominaisvektorina ja neuroverkko on pohjimmiltaan joukko matriisituloja.
Kaikissa näissä on sama rakenne: suureet kootaan vektoreiksi ja
riippuvuudet matriiseiksi, ja laskenta on vektorien ja matriisien
operaatioita.

Tämä tutoriaali opettaa lineaarialgebran insinöörin ja ohjelmoijan
näkökulmasta kolmella tavalla yhtä aikaa:

- **Geometria.** Vektori on nuoli ja matriisi on kuvaus, joka kääntää,
  venyttää tai litistää tasoa tai avaruutta. Kun tietää, mitä
  laskutoimitus tekee geometrisesti, kaavoja ei tarvitse muistaa
  ulkoa.
- **Laskut koodina.** Jokainen menetelmä toteutetaan ensin itse
  puhtaalla Pythonilla, jotta näkee, mitä silmukat tekevät ja mitä ne
  maksavat. Sen jälkeen sama lasketaan NumPylla, ja tuloksia verrataan
  toleranssilla.
- **Numeerinen luotettavuus.** Liukuluvuilla laskettu tulos ei ole
  tarkka. Tutoriaali näyttää, milloin pyöristysvirhe on harmiton ja
  milloin se tuhoaa tuloksen, ja mitä sille voi tehdä.

## Kenelle ja mitä tarvitaan

Lukija osaa ohjelmoida Pythonilla (taito *Ohjelmoinnin perusteet*).
Koulumatematiikka riittää: funktiot, yhtälöt ja trigonometrian
perusteet. Todistuksia ei tarvita; perustelut ovat geometrisia ja
kokeellisia.

| Luku | Kysymys |
|------|---------|
| Vektorit | Miten suunnat ja siirtymät lasketaan? |
| Matriisit ja kuvaukset | Mitä matriisi tekee pisteille? |
| Yhtälöryhmät | Miten monta yhtälöä ratkaistaan yhtä aikaa? |
| LU-hajotelma | Miten samaa matriisia käytetään toistuvasti tehokkaasti? |
| Determinantti ja käänteismatriisi | Miten kuvaus kumotaan ja paljonko se venyttää? |
| Aliavaruudet ja kanta | Missä koordinaatistossa asiat ovat yksinkertaisia? |
| Ortogonaalisuus | Miksi kohtisuorat kannat ovat numeerisesti parhaita? |
| Pienimmän neliösumman sovitus | Miten malli sovitetaan kohinaiseen dataan? |
| Ominaisarvot | Mihin suuntiin kuvaus vain venyttää? |
| Homogeeniset koordinaatit | Miten grafiikka siirtää ja projisoi matriiseilla? |
| Numeeriset näkökohdat | Milloin tulokseen voi luottaa? |

## Ensimmäinen esimerkki: ostoskori

Ostoskorin hinta on tuttu laskutoimitus, ja se on jo lineaarialgebraa.
Hinnat ja määrät ovat vektoreita, ja korin hinta on niiden pistetulo:
vastinalkioiden tulojen summa.

```{.python tiedosto="esimerkit/01-ostoskori.py" osa="puhdas"}
```

Kun koreja on monta, ne kootaan matriisiksi, jonka jokainen rivi on
yksi kori. Matriisin ja vektorin tulo laskee kaikkien rivien
pistetulot hintavektorin kanssa kerralla. NumPyssa operaattori `@`
tarkoittaa matriisituloa:

```{.python tiedosto="esimerkit/01-ostoskori.py" osa="matriisi"}
```

Hintojen muuttaminen tuotekohtaisella kertoimella on sekin
matriisitulo: lävistäjämatriisi kertoo jokaisen koordinaatin omalla
luvullaan.

```{.python tiedosto="esimerkit/01-ostoskori.py" osa="alennus"}
```

```{.tuloste tiedosto="esimerkit/01-ostoskori.odotettu"}
```

Tässä on koko tutoriaalin kaava pienessä mittakaavassa: data vektoreina,
operaatio matriisina, laskenta ensin itse ja sitten kirjastolla.

## Merkinnät

Vektorit kirjoitetaan pienillä lihavoimattomilla kirjaimilla
($u$, $v$, $x$) ja matriisit isoilla ($A$, $B$). Vektori on
oletuksena **sarakevektori**, ja matriisi kertoo sen vasemmalta:
$y = Ax$. Vektorin alkiot ovat $x_1, \dots, x_n$, ja matriisin alkio
rivillä $i$ ja sarakkeessa $j$ on $a_{ij}$. Matematiikassa indeksit
alkavat ykkösestä, Pythonissa nollasta; koodissa `a[i][j]` on siis
$a_{i+1,j+1}$.

Esimerkeissä vektori on puhtaassa Pythonissa lista (`list[float]`) ja
matriisi rivien lista (`list[list[float]]`). NumPyn vastine on
`ndarray`, jonka tyyppi on `float64` ellei toisin mainita.

## Työkalut

Esimerkit toimivat Python 3.12:lla ja NumPy 2:lla. Tyypit tarkistetaan
`mypy --strict` -tilassa ja koodin tyyli `ruff`illa. Kehityskontissa
(`.devcontainer/lineaarialgebra`) kaikki on valmiina. Jokainen esimerkki
ajetaan testeissä, ja sen tulostetta verrataan tallennettuun
tulosteeseen. Siksi tulosteet on pyöristetty niin, että ne ovat samat
kaikilla koneilla: NumPyn laskentakirjastot voivat tuottaa viimeisiin
desimaaleihin eroja suorittimen mukaan.

## Mitä tutoriaali ei kata

Tutoriaali ei käsittele abstrakteja vektoriavaruuksia, kompleksisia
matriiseja eikä singulaariarvohajotelman teoriaa; SVD mainitaan
työkaluna. Fourier-muunnos ja kompleksiset vektorit ovat taidon
*Signaalimatematiikka* aihe, ja suurten harvojen matriisien iteratiiviset
menetelmät jäävät numeeristen menetelmien kirjallisuuteen.

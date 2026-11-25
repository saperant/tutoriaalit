# Säteenheitto

Moni pelin kysymys on muotoa "mitä tästä pisteestä näkyy tähän
suuntaan": mihin luoti osuu, mitä pelaaja osoittaa hiirellä, onko
vihollisen ja pelaajan välissä seinä, kuinka kaukana maa on jalkojen
alla. Vastaus on *säteenheitto* (*raycast*): puolisuora, jolle etsitään
lähin osuma maailman muotoihin. Tässä luvussa tehdään säteen testit
edellisen luvun muodoille ja kaksi tavallista käyttöä.

## Säde

Säteellä on alkupiste ja yksikön pituinen suunta. Piste säteellä
määräytyy yhdestä luvusta $t \ge 0$, joka on samalla etäisyys alusta.
Osumasta palautetaan tämä etäisyys ja pinnan normaali.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="sade"}
```

## Säde ja pallo

Kun säteen piste sijoitetaan pallon yhtälöön, saadaan toisen asteen
yhtälö etäisyydelle. Diskriminantti kertoo, osuuko säde, ja pienempi
juuri on kohta, jossa säde tulee palloon.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="sade-pallo"}
```

## Säde ja laatikko

Akselien suuntainen laatikko on kolmen *laatan* leikkaus: jokainen
laatta on kahden yhdensuuntaisen tason väli. Säde on laatikossa sillä
välillä, jolla se on kaikissa kolmessa laatassa yhtä aikaa. Jos
myöhäisin sisääntulo on myöhemmin kuin aikaisin ulostulo, säde menee
ohi.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="sade-laatikko"}
```

Testi on halpa, ja siksi se on seuraavan luvun hierarkian perusta:
ennen kuin sädettä verrataan tuhanteen kolmioon, sitä verrataan
laatikkoon, joka sisältää ne kaikki.

## Säde ja kolmio

Kolmion piste voidaan kirjoittaa kärjen ja kahden reunavektorin avulla
barysentrisillä koordinaateilla $u$ ja $v$ (taito *Renderöinnin
perusteet*). Kun se asetetaan yhtä suureksi säteen pisteen kanssa,
saadaan kolmen yhtälön ryhmä tuntemattomille $t$, $u$ ja $v$. Möllerin
ja Trumboren menetelmä ratkaisee ryhmän ristitulojen avulla ja hylkää
säteen heti, kun jokin ehdoista $u \ge 0$, $v \ge 0$, $u + v \le 1$
ei täyty.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="sade-kolmio"}
```

## Valinta hiirellä

Kun pelaaja napsauttaa ruutua, peli tarvitsee säteen, joka lähtee
kamerasta ja kulkee napsautetun pikselin läpi. Projektion voi kääntää
käänteismatriisilla, mutta suunnan saa suoremmin kameran akseleista:
pikselin paikka ruudulla kertoo, kuinka paljon katselusuuntaan lisätään
kameran oikeaa ja ylöspäin osoittavaa akselia.

```{.cpp tiedosto="esimerkit/06-sateet.cpp" osa="kamera"}
```

Lähin osuma löytyy testaamalla säde jokaista kohdetta vastaan ja
pitämällä pienin etäisyys:

```{.cpp tiedosto="esimerkit/06-sateet.cpp" osa="maailma"}
```

```{.cpp tiedosto="esimerkit/06-sateet.cpp" osa="valinta"}
```

```{.tuloste tiedosto="esimerkit/06-sateet.odotettu" rivit="1-6"}
```

![Viiden pikselin säteet. Osumakohdat on merkitty keltaisella ja
pinnan normaalit punaisella; viides säde menee
taivaalle.](kuvat/sateet.png){width=70%}

Sama funktio vastaa muihinkin kysymyksiin. *Näkölinja* on säde
vihollisen silmistä pelaajaan: jos lähin osuma on lähempänä kuin
pelaaja, välissä on este. Välittömästi osuva ase (*hitscan*) on säde
piipusta tähtäyssuuntaan. Jalkojen alla oleva maa löytyy säteellä
suoraan alas, ja sitä käytetään luvussa *Hahmon liike*.

## Pyyhkäisy

Nopea kappale voi yhden askeleen aikana hypätä ohuen esteen yli.
Ilmiö, *tunneloituminen*, on tuttu taidosta *Peliohjelmointi*, ja
ratkaisu on sama: verrataan koko liikkeen jälkeä eikä vain
loppupaikkaa. Pallon liike on helppo palauttaa säteeksi. Pallo, jonka
säde on $r$, osuu laatikkoon täsmälleen silloin, kun sen keskipiste
osuu laatikkoon, jota on kasvatettu $r$:n verran joka suuntaan. Liikkuva
pallo on siis säde kasvatettua laatikkoa vastaan.

```{.cpp tiedosto="esimerkit/06-sateet.cpp" osa="pyyhkaisy"}
```

```{.tuloste tiedosto="esimerkit/06-sateet.odotettu" rivit="8-13"}
```

Paikkatesti ei huomaa seinää yhdelläkään askeleella, koska ammus on
ennen seinää askeleen alussa ja sen takana askeleen lopussa. Pyyhkäisy
kertoo, että neljännellä askeleella ammus osuu seinään 0,35 metrin
päässä. Kasvatettu laatikko on kulmistaan hieman liian suuri, sillä
oikea muoto olisi pyöristetty, mutta virhe on turvallisella puolella.

## Käytännössä

- **Säde on pelin yleistyökalu.** Aseet, valinta, näkölinja, maan
  haku, kameran törmäys ja tekoälyn aistit ovat kaikki säteitä.
- **Normalisoi suunta.** Silloin $t$ on etäisyys metreinä, ja
  enimmäismatkan rajaus on yksi vertailu.
- **Rajaa matka ja kohteet.** Säteelle annetaan enimmäispituus ja
  kerrosmaski (taito *Peliohjelmointi*): näkölinjaa ei kiinnosta
  ruohonkorsi eikä pelaajan oma kapseli.
- **Varo alkua pinnalla.** Säde, joka lähtee täsmälleen pinnalta,
  voi osua samaan pintaan etäisyydellä nolla. Alkupistettä siirretään
  hieman normaalin suuntaan.
- **Nopeille kappaleille pyyhkäisy.** Ammus on säde tai pyyhkäisty
  pallo, ei pieni pallo, jonka paikkaa verrataan askelittain.

## Itsearviointi

- Osaat laskea säteen osuman palloon, akselien suuntaiseen laatikkoon
  ja kolmioon ja selittää laattamenetelmän idean.
- Osaat muodostaa säteen kamerasta ruudun pikselin läpi ja valita sillä
  lähimmän kohteen.
- Osaat nimetä ainakin neljä pelin toimintoa, jotka toteutetaan
  säteenheitolla.
- Osaat selittää, miksi liikkuvan pallon osuma laatikkoon voidaan
  laskea säteenä kasvatettua laatikkoa vastaan.

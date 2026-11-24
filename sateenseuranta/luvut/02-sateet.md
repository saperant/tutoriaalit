# Säteet ja kamera

Säteenseurantarenderöijän ydin on kolme riviä: muodosta säde, etsi
lähin osuma, laske osumakohdan väri. Tässä luvussa rakennetaan kaksi
ensimmäistä niin, että kolmannelle jää vain varjostus, jonka
myöhemmät luvut tekevät fysikaalisesti oikein.

## Säde

Säde on puolisuora $\mathbf{r}(t) = \mathbf{o} + t\,\mathbf{d}$, kun
$t > 0$. Lähtöpiste $\mathbf{o}$ on kamera tai pinta, suunta
$\mathbf{d}$ on yksikkövektori. Yksikkösuunnan ansiosta parametri $t$
on suoraan etäisyys, mikä yksinkertaistaa leikkauksia ja valon
vaimenemisen laskemista.

```{.cpp tiedosto="esimerkit/yhteinen/sade.hpp" osa="sade"}
```

Vektorit ovat samat kuin renderöinnin perusteissa, mutta
homogeenisia koordinaatteja ja matriiseja ei tarvita: säteenseuranta
toimii suoraan maailman koordinaateissa. Vektorikirjastoon lisätään
peiliheijastus, jota tarvitaan luvusta *Whitted-säteenseuranta*
alkaen:

```{.cpp tiedosto="esimerkit/yhteinen/vektori.hpp" osa="heijastus"}
```

## Neulanreikäkamera

Neulanreikäkamerassa kaikki säteet lähtevät samasta pisteestä,
silmästä, ja kulkevat kuvatason pisteiden kautta. Kuvataso on
etäisyydellä $f$ katsesuunnassa, ja sen korkeus on 2 yksikköä:
silloin $f = 1/\tan(\theta/2)$, missä $\theta$ on pystysuuntainen
näkökenttä, aivan kuten perspektiivimatriisissa. Kameran kanta
lasketaan katsesuunnasta ja ylösvektorista ristitulolla:

```{.cpp tiedosto="esimerkit/yhteinen/kamera.hpp" osa="kamera"}
```

Pikselikoordinaatit kulkevat ruudun mukaan: $x$ oikealle ja $y$
alaspäin, ja pikselin $(x, y)$ keskipiste on
$(x + 0{,}5,\ y + 0{,}5)$. Kuvasuhde kerrotaan vaakakoordinaattiin,
jotta pikselit ovat neliöitä. Säteenseurannassa ei ole lähi- eikä
kaukotasoa: jokainen säde kulkee niin pitkälle kuin tarvitsee, eikä
syvyyden tarkkuutta tarvitse jakaa kahden tason välille.

Kameran kanta on oikeakätinen, kuten renderöinnin perusteiden
katsematriisissa. Kun kamera katsoo positiivisen $z$-akselin
suuntaan ja ylös on $+y$, oikealle osoittaa $-x$. Tämä on
tavallinen hämmennyksen lähde: kohtaus näyttää peilikuvalta, jos
kannan kätisyys vaihtuu jossain vaiheessa. Esimerkkien kohtaukset on
rakennettu tämän mukaan.

Neulanreikäkameran kaikki kohdat ovat tarkkoja. Oikean kameran
linssillä on aukko, joten vain yksi etäisyys on terävä. Syväterävyys
saadaan valitsemalla säteen lähtöpiste satunnaisesti aukon alueelta
ja suunta niin, että säde kulkee tarkennustason saman pisteen kautta.
Tekniikka on sama kuin seuraavassa osiossa: yksi integraali lisää,
joka lasketaan satunnaisilla näytteillä.

## Ensimmäinen kuva

Ensimmäinen renderöijä etsii lähimmän osuman kolmesta pallosta ja
lattiasta ja varjostaa sen Lambertin mallilla ilman varjoja.
Lähin osuma löytyy pitämällä yllä tähänastista pienintä $t$:tä ja
antamalla se seuraavalle testille ylärajaksi, jolloin kauempana
olevat osumat hylätään heti:

```{.cpp tiedosto="esimerkit/02-kamera.cpp" osa="sade"}
```

Leikkausfunktiot `leikkaa_pallo` ja `leikkaa_taso` käydään läpi
seuraavassa luvussa. Tässä riittää tietää, että ne palauttavat lähimmän
osuman väliltä $(t_\text{min}, t_\text{max})$ tai äärettömän.

## Pikselin väri on integraali

Pikseli ei ole piste vaan pieni neliö, ja sen väri on neliön läpi
näkyvän valon keskiarvo:

$$I = \int_0^1 \int_0^1 L\big(\mathbf{r}(x + u, y + v)\big)\,du\,dv.$$

Yksi säde keskipisteen kautta arvioi integraalia yhdellä pisteellä.
Kappaleen reunalla arvio on joko kappale tai tausta, ja reuna
porrastuu. Renderöinnin perusteissa porrastusta vähennettiin
ylinäytteistyksellä kiinteässä kuviossa. Säteenseurannassa
luontevampaa on valita näytteet satunnaisesti pikselin alueelta,
*värinä* (jitter):

```{.cpp tiedosto="esimerkit/02-kamera.cpp" osa="jitter"}
```

Pikselin satunnaislukugeneraattori alustetaan pikselin indeksillä.
Jos koko kuva käyttäisi yhtä generaattoria, jokaisen pikselin
näytteet riippuisivat siitä, montako lukua aiemmat pikselit
käyttivät, ja yhden pikselin muutos siirtäisi koko loppukuvan
satunnaislukuja. PCG32:n jonoparametri antaa jokaiselle pikselille
oman, toisista riippumattoman virran:

```{.cpp tiedosto="esimerkit/yhteinen/satunnainen.hpp" osa="pcg"}
```

Pääohjelma renderöi saman kohtauksen yhdellä ja 16 näytteellä:

```{.cpp tiedosto="esimerkit/02-kamera.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/02-kamera.odotettu"}
```

![Primäärisäteet ja Lambertin varjostus 16 värinänäytteellä
pikselissä. Kaukainen ruudukko on edelleen sumea: yksi pikseli kattaa
siellä useita ruutuja.](kuvat/02-kamera.png){width=70%}

Keskiarvo muuttuu vähän (0,2818 → 0,2825), koska reunojen
porrastus on suunnilleen symmetristä: yhtä monta pikseliä pyöristyy
kappaleeseen kuin taustaan. Ero näkyy RMSE:ssä ja reunoilla. Kaukana
olevassa shakkiruudukossa yksi pikseli kattaa useita ruutuja, ja
yksi näyte valitsee niistä satunnaisesti yhden. Tuloksena on
moiré-kuvio. Kuudellatoista näytteellä pikseli saa ruutujen keskiarvon.
Rasteroinnissa sama ongelma ratkaistiin tekstuurin mipmapeilla;
säteenseurannassa se ratkeaa samalla mekanismilla kuin reunat.

## Kuvat ja tarkistussummat

Kuvapuskuri on liukulukuinen (`Kehys`), koska pikselin arvo on
radianssin keskiarvo eikä sillä ole ylärajaa: valolähteen radianssi
on kymmeniä kertoja näytön valkoista suurempi. Tallennettaessa arvot
koodataan sRGB-tavuiksi samoin kuin renderöinnin perusteissa:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="kehys"}
```

Tarkistussumma lasketaan tallennettavista tavuista. Pienet
liukulukuerot, jotka eivät muuta yhtään tavua, eivät muuta
tarkistussummaa, mutta yksikin näkyvä muutos muuttaa sen:

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="tallennus"}
```

```{.cpp tiedosto="esimerkit/yhteinen/kuva.hpp" osa="raportti"}
```

## Käytännössä

- **Säteen suunta yksikkövektoriksi** heti, kun säde muodostetaan.
  Moni kaava (pallon leikkaus, etäisyys, valon vaimeneminen) olettaa
  sen, ja normalisointi myöhemmin unohtuu helposti.
- **Jokaiselle pikselille oma satunnaislukuvirta.** Tulos ei riipu
  laskentajärjestyksestä tai säikeiden määrästä, ja yksittäisen
  pikselin voi laskea uudelleen virheenjäljitystä varten.
- **Yksi satunnaisluku lausetta kohden.** Argumenttien
  laskentajärjestys ei ole määrätty, ja ero näkyy vasta, kun koodi
  käännetään toisella kääntäjällä.
- **Liukulukupuskuri, koodaus vasta lopuksi.** Keskiarvot, suodatus
  ja sävykuvaus tehdään radianssilla, ei tavuilla.
- **Pidä kanta selvänä.** Kirjoita ylös, mihin suuntaan kamera katsoo
  ja kumpi akseli on oikealla. Peilikuvaksi kääntynyt kohtaus on
  tavallinen virhe, jota testit eivät huomaa.

## Itsearviointi

- Osaat muodostaa neulanreikäkameran säteen pikselikoordinaateista
  ja selittää, miten näkökenttä ja kuvasuhde vaikuttavat siihen.
- Osaat selittää, miksi pikselin väri on integraali ja miten
  satunnaiset näytteet pikselin alueelta vähentävät porrastusta.
- Osaat perustella, miksi jokaisella pikselillä on oma
  satunnaislukuvirta ja miksi satunnaislukuja ei kutsuta saman
  funktion argumenteissa.
- Osaat kuvata, miten syväterävyys lisätään neulanreikäkameraan.

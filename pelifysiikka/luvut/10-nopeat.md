# Nopeat kappaleet

Simulaatio katsoo maailmaa kuudenkymmenen ruudun sekuntivauhdilla.
Kappale, joka ehtii kahden katselukerran välissä esteen toiselle
puolelle, ei törmää siihen koskaan. Ilmiö on *tunneloituminen*, ja se
on tuttu taidosta *Peliohjelmointi*. Tässä luvussa mitataan, milloin
se tapahtuu, ja korjataan se laskemalla törmäyksen ajankohta.

## Milloin diskreetti testi pettää

*Diskreetti* törmäystunnistus tarkistaa kappaleiden paikat askeleen
lopussa. Esimerkki ampuu kymmenen senttimetrin säteisen pallon
kymmenen senttimetriä paksuun seinään eri nopeuksilla:

```{.cpp tiedosto="esimerkit/10-nopea.cpp" osa="koe"}
```

```{.cpp tiedosto="esimerkit/10-nopea.cpp" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/10-nopea.odotettu" rivit="1-5"}
```

Nopeudella 40 m/s pallo kulkee askeleessa 67 senttimetriä ja hyppää
seinän yli näkemättä sitä. Kiinnostavampi on rivi 12 m/s. Pallo kulkee
askeleessa 20 senttimetriä, eli vähemmän kuin pallon ja seinän
yhteinen paksuus, ja se havaitaan seinän sisältä. Silti se päätyy
väärälle puolelle: sen keskipiste on ehtinyt seinän puolivälin ohi, ja
luvun 4 testi työntää sisäkkäiset kappaleet ulos lyhintä tietä.
Turvallinen matka askeleessa on siis noin puolet ohuimman esteen
paksuudesta.

![Pallon paikka askelittain nopeudella 40 m/s. Diskreetti testi ei
näe seinää lainkaan. Jatkuva tunnistus pysäyttää pallon seinän
pintaan, ja seuraavalla askeleella se
kimpoaa.](kuvat/nopea.png){width=75%}

## Osuma-aika

*Jatkuva törmäystunnistus* (*continuous collision detection*, CCD) ei
kysy, koskettavatko kappaleet askeleen lopussa, vaan milloin ne
askeleen aikana ensimmäisen kerran koskettavat. Vastaus on *osuma-aika*
(*time of impact*) nollan ja yhden väliltä.

Pallolle liikkumatonta laatikkoa vastaan osuma-aika on säteenheitto.
Laatikkoa paisutetaan pallon säteen verran, jolloin pallosta tulee
piste ja sen liikkeestä jana, ja janan ja laatikon leikkaus lasketaan
laatoilla kuten taidossa *3D-peliohjelmointi*:

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="pyyhkaisy"}
```

```{.cpp tiedosto="esimerkit/10-nopea.cpp" osa="aika"}
```

```{.tuloste tiedosto="esimerkit/10-nopea.odotettu" alkaen="osuma-aika"}
```

Paisutettu laatikko on kulmistaan liian suuri: oikea muoto olisi
pyöristetty. Virhe on varovaiseen suuntaan, sillä pallo voi pysähtyä
hieman ennen kulmaa, mutta se ei mene läpi.

Simulaatioaskel käyttää osuma-aikaa yksinkertaisimmalla mahdollisella
tavalla. Nopeaksi merkitty pallo siirtyy askeleessa vain ensimmäiseen
osumaansa asti. Seuraavalla askeleella se on kosketuksessa, ja
tavallinen ratkaisija hoitaa kimpoamisen. Loppuosa askeleesta jää
pallolta käyttämättä, mikä näkyy kuvassa yhden askeleen pysähdyksenä.

Yksi yksityiskohta on välttämätön: jo kosketuksessa oleva pallo on
jätettävä pyyhkäisyn ulkopuolelle. Muuten seinästä poispäin kimpoava
pallo saisi joka askeleella osuma-ajan nolla ja jäisi seinään kiinni.

## Yleinen tapaus

Kahden pyörivän kappaleen osuma-ajalle ei ole suljettua kaavaa.
Moottorit käyttävät *varovaista etenemistä* (*conservative
advancement*): lasketaan kappaleiden etäisyys ja yläraja sille, kuinka
nopeasti ne voivat lähestyä toisiaan pyöriminen mukaan lukien.
Etäisyys jaettuna nopeudella on aika, jonka kappaleita voi varmasti
siirtää ilman osumaa. Siirretään sen verran ja toistetaan, kunnes
etäisyys on lähes nolla. Etäisyys saadaan luvun 4 GJK-algoritmilla.

Kevyempi vaihtoehto on luvun 7 ennakoiva kosketus. Kun laaja vaihe
käyttää ympäryksiä, jotka on venytetty kappaleen askeleen aikaisen
liikkeen verran, lähestyvät kappaleet saavat kosketusrivin jo ennen
osumaa, ja rivi sallii lähestymisen vain raon verran. Menetelmä ei
tarvitse osuma-aikaa lainkaan. Sen haittapuoli on haamukosketus:
kappale voi pysähtyä esteeseen, jonka ohi se olisi oikeasti lentänyt.

## Käytännössä

- **CCD vain niille, jotka sitä tarvitsevat.** Jatkuva tunnistus on
  kallis, joten se kytketään kappalekohtaisesti: luodit, heitetyt
  esineet, pelaaja. Laatikkopino ei tarvitse sitä.
- **Ammus on usein säde.** Hyvin nopeaa ammusta ei kannata simuloida
  kappaleena: säteenheitto piipusta antaa osumakohdan heti.
- **Nopeuskatto.** Moottorit rajaavat kappaleiden suurimman nopeuden.
  Katto ja ohuimman seinän paksuus yhdessä kertovat, tarvitaanko
  jatkuvaa tunnistusta.
- **Seinät paksuiksi.** Halvin korjaus tehdään tasosuunnittelussa:
  ohut seinä korvataan törmäysmuodolla, joka jatkuu näkyvän pinnan
  taakse.
- **Pyöriminen on vaikein.** Nopeasti pyörivä pitkä kappale voi lyödä
  esteen läpi, vaikka sen massakeskipiste liikkuu hitaasti. Useimmat
  moottorit käsittelevät jatkuvassa tunnistuksessa vain siirtymän ja
  rajaavat kulmanopeutta.
- **Aliaskeleet** pienentävät askeleessa kuljettua matkaa ja siirtävät
  tunneloitumisen rajaa samassa suhteessa.

## Itsearviointi

- Osaat arvioida, millä nopeudella kappale voi tunneloitua annetun
  paksuisen esteen läpi.
- Osaat selittää, miksi kappale voi päätyä esteen väärälle puolelle,
  vaikka se havaitaan esteen sisältä.
- Osaat laskea pallon osuma-ajan tasoa tai laatikkoa vastaan.
- Osaat kuvata varovaisen etenemisen ja ennakoivan kosketuksen erot.

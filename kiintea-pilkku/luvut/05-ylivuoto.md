# Saturaatio ja kierto

Kun tulos ei mahdu muotoonsa, laitteisto tekee jompaakumpaa. *Kierto*
(*wrap-around*) pitää alimmat bitit ja pudottaa ylimmät, jolloin suuri
positiivinen luku muuttuu suureksi negatiiviseksi. *Saturaatio*
(*clamping*) leikkaa tuloksen lähimpään esitettävään arvoon. Kierto on
ilmainen, saturaatio vaatii vertailun ja multiplekserin. Kumpikaan ei
ole aina oikein.

## Virhe ylivuodossa

Saturaation virhe on pieni ja paikallinen: tulos on niin lähellä oikeaa
kuin muoto sallii. Kierron virhe on lähes koko arvoalueen suuruinen:

```{.c tiedosto="esimerkit/05-saturaatio.c" osa="summaimet"}
```

```{.c tiedosto="esimerkit/05-saturaatio.c" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/05-saturaatio.odotettu"}
```

Audiossa kierto kuuluu kovana napsahduksena, kuvassa väärän värisenä
pikselinä ja säätöjärjestelmässä täyteen vastakkaiseen suuntaan
kääntyvänä toimilaitteena. Saturaatio kuulostaa leikkaantumiselta, mikä
on häiritsevää mutta ei vaarallista. Siksi signaalin tie ulos
järjestelmästä, kuten DA-muuntimelle, ohjaimelle tai näytölle,
saturoidaan aina.

## Kierto välituloksissa on sallittua

Kahden komplementin aritmetiikka on modulaarista: summa modulo $2^n$ on
oikein riippumatta siitä, kiersivätkö välitulokset. Jos lopputulos
tiedetään mahtuvan alueelle, välitulosten ylivuodosta ei tarvitse
välittää. Tämä on *Jacksonin sääntö*, ja se tekee pitkistä summista
halpoja:

```{.python tiedosto="esimerkit/05-valitulos.py" osa="summat"}
```

```{.tuloste tiedosto="esimerkit/05-valitulos.odotettu"}
```

Välitulos 0,9 + 0,7 = 1,6 ei mahdu Q1.15:een. Kierto antaa välitulokseksi
−0,4, mutta lopputulos on oikein. Saturaatio leikkaa välituloksen 1,0:aan,
ja virhe jää pysyväksi: lopputulos on 0,2 eikä 0,8. Saturaatiota ei siis
pidä tehdä jokaisen yhteenlaskun jälkeen, vaan vain kerran, kun tulos
lähtee datapolulta.

Sääntö pätee summille ja FIR-suodattimille, joiden lopputulos on
rajattu. Se ei päde, jos välitulos kerrotaan tai sitä vertaillaan, ja
se ei päde IIR-suodattimen takaisinkytkennässä, jossa kiertänyt arvo
palaa seuraavan kierroksen syötteeksi. Siellä kierto voi tuottaa
*ylivuotovärähtelyn*, jossa suodatin heiluu täyttä amplitudia ilman
syötettä. IIR-tilamuuttujat saturoidaan tai mitoitetaan niin leveiksi,
ettei ylivuotoa voi syntyä.

## Saturaation hinta laitteistossa

Saturoiva summain tarvitsee ylivuodon tunnistuksen ja multiplekserin.
Ylivuoto tunnistetaan joko yhden ylimääräisen bitin avulla (summa
lasketaan $n+1$ bittiin, ja ylimmät kaksi bittiä eroavat) tai
etumerkeistä: kahden saman merkkisen luvun summa, jonka etumerkki
poikkeaa, on vuotanut yli. Logiikka on pientä, mutta se on kriittisellä
polulla summaimen perässä, joten nopeissa datapoluissa saturaatio
siirretään usein omaan liukuhihnavaiheeseensa.

## Käytännössä

- **Saturoi ulostulot, kierrä välitulokset.** Datapolun sisällä
  käytetään kiertäviä summaimia ja riittävästi vartijabittejä, ja
  saturaatio tehdään kerran, kun tulos kavennetaan rajapinnan
  leveyteen.
- **Saturoi takaisinkytkennät.** IIR-suodattimien ja integraattorien
  tila joko saturoidaan tai mitoitetaan niin, ettei ylivuoto ole
  mahdollinen. Kiertävä integraattori on sallittu vain erityisrakenteissa,
  kuten CIC-suodattimessa, jossa modulaarisuus on osa suunnittelua.
- **Testaa ylivuoto tarkoituksella.** Testipenkkiin kuuluu signaali,
  joka ylittää alueen, sekä tarkistus, että tulos saturoituu eikä kierrä.
- **Laske saturaatiotapahtumat.** Laitteistoon kannattaa lisätä laskuri
  tai tilalippu, joka kertoo, kuinka usein saturaatio laukesi. Usein
  toistuva saturaatio tarkoittaa väärin mitoitettua vahvistusta.

## Itsearviointi

- Osaat toteuttaa kiertävän ja saturoivan summan ja kertoa niiden
  virheen suuruuden ylivuodossa.
- Osaat selittää, miksi välitulosten kierto on sallittua, kun
  lopputulos mahtuu alueelle, ja milloin se ei ole.
- Osaat valita, mihin kohtiin datapolkua saturaatio sijoitetaan.
- Osaat kertoa, miten ylivuoto tunnistetaan laitteistossa.

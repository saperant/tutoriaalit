# Johdanto {.runko-johdanto}

Digitaalinen järjestelmä on aina analogisen maailman ympäröimä. Anturi
antaa millivoltteja kohinan seassa, AD-muunnin haluaa nollasta
referenssijännitteeseen ulottuvan puhtaan signaalin, ja kaiutin,
moottori tai venttiili tarvitsee virtaa, jota mikrokontrollerin pinni ei
pysty antamaan. Niiden väliin tarvitaan analogiaelektroniikkaa:
vahvistimia, suodattimia, muuntimia ja huolellista piirisuunnittelua,
joka pitää kohinan ja häiriöt kurissa. Tämä tutoriaali käsittelee nämä
rakennuspalikat insinöörin näkökulmasta:

- transistorivahvistimet: toimintapiste, piensignaalimalli ja
  toimintapisteen herkkyys
- operaatiovahvistinkytkennät ja todellisen vahvistimen rajat
- aktiiviset suodattimet: mitoitus, siirtofunktio ja komponenttien
  toleranssit
- takaisinkytkentä ja stabiilisuus: vaihevara ja kapasitiivinen kuorma
- AD- ja DA-muuntimet: kvantisointi, SAR- ja sigma-delta-periaate,
  R-2R-tikapuu sekä näytteenotto ja pito
- kohina ja signaalin eheys: terminen kohina, kohinabudjetti ja
  heijastukset siirtolinjassa.

```{.dot otsikko="Tyypillinen mittausketju. Tutoriaalin luvut käsittelevät ketjun analogisen osan; luvun numero on suluissa."}
digraph {
  rankdir=LR;
  anturi [label="anturi"];
  vahvistin [label="vahvistin\n(2, 3)"];
  suodin [label="antialiasointi-\nsuodin (4)"];
  ad [label="AD-muunnin\n(6)"];
  ohjelma [label="ohjelmisto", style="rounded,dashed"];
  anturi -> vahvistin -> suodin -> ad -> ohjelma;
  kohina [label="kohina ja\nhäiriöt (7)", shape=plaintext, style=""];
  kohina -> vahvistin [style=dashed, arrowhead=open];
}
```

## Kaksi riippumatonta laskua

Tutoriaali jatkaa taidon *Elektroniikan perusteet ja SPICE* tapaa:
jokainen piiri lasketaan käsin Pythonilla ja simuloidaan avoimella
ngspice-simulaattorilla, ja esimerkkiohjelma vertaa tuloksia. Kun ne
täsmäävät, sekä ymmärrys että simulointi ovat kunnossa. Kun ne eroavat,
ero on opettavainen: tämän tutoriaalin esimerkeissä se paljasti muun
muassa, että transistorin vahvistus toimintapisteessä on puolet mallin
huippuarvosta, että nousunopeus voi peittää epävakauden ja että
-3 dB:n rajataajuus riippuu komponenttitoleransseista enemmän kuin
suodattimen kulmataajuus.

Analogiapiirien käsilasku on aina mallin varassa. Transistori on
piensignaalimalli, operaatiovahvistin ihanteellinen tai yksinapainen, ja
suodatin toisen kertaluvun siirtofunktio. SPICE laskee saman piirin
tarkemmalla mallilla ilman näitä yksinkertaistuksia, joten vertailu
kertoo, kuinka hyvin malli kuvaa piiriä. Taidon *Differentiaaliyhtälöt
ja Laplace-muunnos* siirtofunktiot, navat ja askelvasteet ovat tämän
tutoriaalin päätyökalu.

## Ensimmäinen piiri: invertoiva vahvistin

Operaatiovahvistin on erovahvistin, jonka vahvistus on hyvin suuri
(tyypillisesti 10^5^ ... 10^6^). Takaisinkytkettynä sen ominaisuudet
määräytyvät lähes kokonaan ulkoisista vastuksista. Invertoivassa
vahvistimessa tulojännite syötetään vastuksen R1 kautta invertoivaan
tuloon, ja R2 kytkee lähdön takaisin samaan solmuun:

![Invertoiva vahvistin. Vahvistus on $-R_2/R_1$.](kuvat/invertoiva.png){width=50%}

Ihanteellisella vahvistimella vahvistus on $-R_2/R_1 = -10$. Äärellinen
avoimen silmukan vahvistus $A_{ol}$ pienentää sitä hieman: suljetun
silmukan vahvistus on ihanteellinen kerrottuna tekijällä
$1/(1 + 1/(A_{ol}\beta))$, missä $\beta = R_1/(R_1 + R_2)$ on
takaisinkytkentäkerroin.

```{.python tiedosto="esimerkit/01-vahvistin.py" osa="kasin"}
```

Netlistissä operaatiovahvistin on aliohjelma `OPAMP`, joka on
kirjastossa `operaatiovahvistimet.lib`. Sen rakenne käydään läpi
luvussa 3; tässä riittää, että aliohjelman parametrit ovat
avoimen silmukan vahvistus `AOL` ja vahvistus-kaistanleveystulo `GBW`.

```{.spice tiedosto="esimerkit/01-vahvistin.cir"}
```

```{.python tiedosto="esimerkit/01-vahvistin.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/01-vahvistin.odotettu"}
```

Invertoivan tulon jännite on vain 10 µV, vaikka lähtö on −1 V. Tämä on
*virtuaalimaa*: takaisinkytkentä pitää tulojen eron niin pienenä, että
ihanteellisessa mallissa sitä voi pitää nollana. Virtuaalimaa on
operaatiovahvistinkytkentöjen analyysin tärkein työkalu: kun tulojen
ero on nolla ja tuloihin ei kulje virtaa, piirin voi ratkaista pelkillä
Kirchhoffin laeilla.

## Apumoduuli ja mallikirjastot

Esimerkit käyttävät samaa apumoduulia `spice.py` kuin taito
*Elektroniikan perusteet ja SPICE*: funktio `simuloi` ajaa ngspicen
eräajona ja palauttaa `meas`- ja `print`-tulokset sekä
`wrdata`-tiedostot NumPy-taulukkoina, ja `vertaa` tulostaa simuloidun ja
lasketun arvon rinnakkain:

```{.python tiedosto="esimerkit/spice.py" osa="vertaa"}
```

```{.tuloste tiedosto="esimerkit/spice.odotettu"}
```

Mallikirjastoja on kaksi. `transistorit.lib` on sama kuin perustaidossa:
pienitehoisen NPN-transistorin malli (2N3904:n kaltainen) ja
MOSFET-mallit. `operaatiovahvistimet.lib` sisältää tämän tutoriaalin
operaatiovahvistimen makromallin. Mallien parametrit ovat tyypillisiä
arvoja eivätkä minkään valmistajan takuuarvoja; oikeassa suunnittelussa
käytetään valmistajan julkaisemia malleja ja datalehden raja-arvoja.

## Kenelle ja mitä tarvitaan

Tutoriaali olettaa taidon *Elektroniikan perusteet ja SPICE* hallinnan:
Kirchhoffin lait, impedanssin, Bode-kuvaajan, diodit, transistorin
kytkimenä ja SPICEn perusanalyysit (`op`, `dc`, `ac`, `tran`, `meas`).
Siirtofunktioiden ja stabiilisuuden osalta se nojaa taitoon
*Differentiaaliyhtälöt ja Laplace-muunnos*. AD-muunnoksen yhteydessä
viitataan taitoihin *Signaalit ja järjestelmät* ja *Digitaalinen
signaalinkäsittely*.

Kehityskontissa (`.devcontainer/analogiaelektroniikka`) ovat valmiina
ngspice, NumPy, SciPy, SymPy, Matplotlib ja schemdraw. Esimerkit ajetaan
esimerkkihakemistossa (`python3 01-vahvistin.py`), ja paketin juuressa
`make testaa` ajaa kaikki tarkistukset.

## Tutoriaalin rakenne

Luku 2 käsittelee bipolaaritransistorin vahvistimena: toimintapisteen,
piensignaalimallin ja sen, miksi emitterivastus tekee piiristä
toistettavan. Luku 3 siirtyy operaatiovahvistimiin ja niiden todellisiin
rajoihin. Luku 4 rakentaa niistä aktiivisia suodattimia, ja luku 5
selvittää, milloin takaisinkytketty piiri alkaa värähdellä. Luku 6
käsittelee AD- ja DA-muuntimet, ja luku 7 kohinan ja signaalin eheyden.
Luku 8 kokoaa nyrkkisäännöt ja lähteet.

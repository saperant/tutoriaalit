# Johdanto {.runko-johdanto}

Ohjelmoija kohtaa elektroniikan viimeistään silloin, kun koodi alkaa
ohjata jotain fyysistä: LEDiä, relettä, moottoria tai anturia. Silloin
kysymykset muuttuvat. Ei riitä, että pinni asetetaan tilaan 1; pitää
tietää, kuinka paljon virtaa pinni kestää, miksi I2C-väylä toimii
pöydällä mutta ei pitkällä kaapelilla ja miksi transistori kuumenee,
vaikka sen piti olla "täysin auki". Tämä tutoriaali antaa vastaukset
niihin perusasioihin, joita näihin kysymyksiin tarvitaan:

- jännite, virta, resistanssi ja teho sekä komponenttien arvot ja
  toleranssit
- piirianalyysi: Kirchhoffin lait, solmujännitemenetelmä,
  Theveninin vastine ja superpositio
- kondensaattori ja kela: aikavakio, varaus ja purkautuminen,
  RC-viiveet digitaalisissa signaaleissa
- vaihtovirta: tehollisarvo, impedanssi kompleksilukuna, taajuusvaste
  ja resonanssi
- diodit ja transistorit kytkiminä: tasasuuntaus, LEDit,
  vapaakäyntidiodi ja CMOS-invertteri
- piirisimulaattori SPICE ja sen avoin toteutus **ngspice**.

Jokainen piiri lasketaan kahdella tavalla: käsin kaavoilla, Pythonin
avulla, ja simuloimalla ngspicellä. Esimerkkiohjelma vertaa tuloksia
ja ilmoittaa, jos ne eroavat. Kahdesta riippumattomasta laskusta
syntyvä sama tulos on vahva todiste siitä, että sekä ymmärrys että
simulointi ovat kunnossa. Kun tulokset eroavat, ero kertoo jotain
tärkeää: joko kaavan oletus ei päde (esimerkiksi kuormitus jäi
huomiotta) tai simulointimalli on erilainen kuin luultiin.

## Ensimmäinen piiri: jännitteenjakaja

Jännitteenjakaja on kahden vastuksen sarjakytkentä, jonka keskipisteestä
otetaan pienempi jännite. Se on elektroniikan yleisin yksittäinen
rakenne: sillä skaalataan anturin jännite AD-muuntimen alueelle,
asetetaan vertailujännite ja jaetaan akun jännite mitattavaksi.

![Jännitteenjakaja: 12 V:n lähde ja vastukset 10 kohm ja 4,7 kohm.
Lähtö otetaan vastusten välistä.](kuvat/jakaja.png){width=38%}

Sama virta kulkee molempien vastusten läpi, joten virta on syöttöjännite
jaettuna vastusten summalla, ja lähtöjännite on virta kertaa alempi
vastus:

$$
I = \frac{U}{R_1 + R_2}, \qquad
U_\text{ulos} = I R_2 = U \frac{R_2}{R_1 + R_2}.
$$

Pythonilla lasku on kolme riviä:

```{.python tiedosto="esimerkit/01-jakaja.py" osa="kasin"}
```

Sama piiri ngspicelle kuvataan *netlistinä*. Jokainen rivi on yksi
komponentti: nimi (ensimmäinen kirjain kertoo lajin: V on
jännitelähde, R vastus), kytkentäsolmut ja arvo. Solmu `0` on maa,
josta kaikki jännitteet mitataan. Tähdellä alkavat rivit ovat
kommentteja, ja `.control`-lohko kertoo, mitä simulaattori tekee:
`op` laskee tasajännitteisen toimintapisteen ja `print` tulostaa
pyydetyt suureet.

```{.spice tiedosto="esimerkit/01-jakaja.cir"}
```

Esimerkkien yhteinen apumoduuli `spice.py` ajaa ngspicen eräajona ja
poimii sen tulosteesta nimetyt arvot. Vertailu tulostaa simuloidun ja
lasketun arvon rinnakkain:

```{.python tiedosto="esimerkit/01-jakaja.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/01-jakaja.odotettu"}
```

Lähteen virta on SPICEssä negatiivinen. Simulaattori mittaa virran
jännitelähteen läpi sen plusnavasta miinusnapaan, ja syöttävässä
lähteessä virta kulkee päinvastoin. Etumerkkikäytäntö on yleinen
hämmennyksen lähde; luvussa 8 palataan siihen.

## Apumoduuli spice.py

Kaikki esimerkit käyttävät samaa pientä moduulia. Sen ydin on funktio
`simuloi`, joka kirjoittaa netlistin väliaikaiseen hakemistoon, ajaa
`ngspice -b` (batch eli eräajo ilman käyttöliittymää) ja kerää
tulokset:

```{.python tiedosto="esimerkit/spice.py" osa="simuloi"}
```

Moduuli palauttaa kahdenlaisia tuloksia. `arvot` sisältää rivit
muotoa `nimi = arvo`, joita syntyy `meas`- ja `print`-komennoista.
`data` sisältää `wrdata`-komennolla tiedostoon kirjoitetut sarakkeet,
esimerkiksi transienttisimuloinnin koko aaltomuodon, jota käsitellään
NumPylla ja piirretään Matplotlibilla. Tämä työnjako on käytännön
työssäkin hyvä: simulaattori laskee piirin, ja Python tekee analyysin,
vertailut ja raportit, jotka voi ajaa uudelleen aina, kun piiri muuttuu.

Arvot muotoillaan kolmella merkitsevällä numerolla ja SI-etuliitteellä
(`k` = 10^3^, `m` = 10^-3^, `u` = mikro, 10^-6^, `n` = 10^-9^, `p` =
10^-12^). Samat etuliitteet kelpaavat netlistissä: `4.7k`, `100n`,
`1Meg`. SPICE ei erota isoja ja pieniä kirjaimia, joten `M` tarkoittaa
milliä; megaohmi kirjoitetaan `Meg`. Tämä on yksi tavallisimmista
SPICE-virheistä.

## Kenelle ja mitä tarvitaan

Tutoriaali on tarkoitettu ohjelmoijalle tai insinööriopiskelijalle,
joka hallitsee lukion matematiikan: yhtälöt, eksponentti- ja
logaritmifunktiot sekä trigonometrian. Taito *Matematiikan perusteet
ohjelmallisesti* kattaa ne ja esittelee työkalut (SymPy, NumPy,
Matplotlib), joita tässä käytetään. Kompleksiluvut esitellään luvussa 5
siinä laajuudessa kuin impedanssi vaatii; taito *Kompleksiluvut ja
Fourier-analyysi* syventää niitä.

Kehityskontissa on valmiina ngspice ja Pythonin kirjastot. Omalle
koneelle ngspice asennetaan pakettienhallinnalla (`apt install ngspice`,
`brew install ngspice`) tai Windowsille ngspicen verkkosivuilta.
Esimerkit ajetaan esimerkkihakemistossa komennolla `python3
01-jakaja.py`; kaikki tarkistukset ajaa paketin juuressa `make testaa`.

## Turvallisuudesta

Kaikki tutoriaalin piirit toimivat pienillä jännitteillä, enintään
muutamissa kymmenissä voltissa, ja ne simuloidaan. Kun piirejä
rakennetaan oikeasti, kannattaa pysyä samalla alueella: verkkojännite
(230 V) ja suuret energiat (akut, suuret kondensaattorit) vaativat
koulutuksen ja asianmukaiset välineet. Sähköturvallisuuslaki rajaa
myös, kuka saa tehdä sähköasennuksia. Luvun 6 tasasuuntaaja olettaa
valmiin, turvallisen muuntajan, jonka toisiojännite on 12 V.

## Tutoriaalin rakenne

Luku 2 käsittelee perussuureet ja komponenttien arvot, luku 3
piirianalyysin menetelmät ja luku 4 kondensaattorin ja kelan
ajassa. Luku 5 siirtyy vaihtovirtaan ja taajuustasoon. Luvut 6 ja 7
esittelevät puolijohteet: diodit ja transistorit kytkiminä, mukaan
lukien CMOS-invertteri, joka on kaiken digitaalilogiikan
rakennuspalikka. Luku 8 kokoaa SPICEn käytön syvemmin:
aliohjelmat, parametrit, silmukat, Monte Carlo -analyysi ja
simuloinnin rajat. Jatkotaito *Analogiaelektroniikka* rakentuu
tämän päälle: operaatiovahvistimet, aktiiviset suodattimet, AD- ja
DA-muuntimet sekä kohina.

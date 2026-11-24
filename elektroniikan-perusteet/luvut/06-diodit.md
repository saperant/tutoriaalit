# Diodit

Diodi päästää virran kulkemaan vain yhteen suuntaan: anodilta
katodille. Se on yksinkertaisin puolijohdekomponentti ja ensimmäinen
epälineaarinen komponentti tässä tutoriaalissa: Ohmin laki ja
superpositio eivät päde sille. Diodeja käytetään tasasuuntaukseen,
suojaukseen, valon tuottamiseen ja jännitteen vakauttamiseen.

## Ominaiskäyrä ja Shockleyn yhtälö

Ihanteellisen diodin virran ja jännitteen riippuvuutta kuvaa
Shockleyn yhtälö:

$$
I = I_S \left(e^{U / (n U_T)} - 1\right),
$$

missä $I_S$ on estosuuntainen kyllästysvirta (nanoampeereja tai
paljon vähemmän), $n$ on ideaalisuuskerroin (1...2) ja $U_T = kT/q
\approx 25{,}9$ mV huoneenlämmössä. Virta kasvaa eksponentiaalisesti:
jokainen $n U_T \ln 10 \approx 100$ mV:n lisäys kymmenkertaistaa virran.
Siksi diodilla näyttää olevan "kynnysjännite": alle 0,5 V:n virta on
merkityksetön, ja 0,6...0,7 V:ssa piidiodi johtaa jo kymmeniä
milliampeereja. Suurilla virroilla sarjaresistanssi $R_S$ alkaa näkyä.

SPICE-malli on Shockleyn yhtälö lisättynä sarjaresistanssilla,
kapasitansseilla ja läpilyönnillä. Paketin mallit ovat tiedostossa
`diodit.lib`, joka otetaan käyttöön `.include`-rivillä:

```{.spice tiedosto="esimerkit/diodit.lib"}
```

Mallin parametrit voi määrittää mittauksista. DC-pyyhkäisy tuottaa
ominaiskäyrän, ja kun $e^{U/(nU_T)} \gg 1$, logaritmi virrasta on
suora, jonka kulmakertoimesta saadaan $n$ ja leikkauspisteestä $I_S$:

```{.spice tiedosto="esimerkit/06-ominaiskayra.cir"}
```

```{.python tiedosto="esimerkit/06-ominaiskayra.py" osa="sovitus"}
```

```{.python tiedosto="esimerkit/06-ominaiskayra.py" osa="kynnys"}
```

```{.tuloste tiedosto="esimerkit/06-ominaiskayra.odotettu"}
```

Tässä "simuloitu" sarake on simulaation datasta sovitettu arvo, ja
"laskettu" mallin parametri. Sovitus palauttaa mallin parametrit, mikä
todistaa menetelmän; oikealle diodille sama sovitus tehdään
mittausdatasta.

![Diodin ominaiskäyrä lineaarisella ja logaritmisella virta-asteikolla.
Logaritmisella asteikolla Shockleyn alue on suora, ja suurilla
virroilla sarjaresistanssi taivuttaa sitä.](kuvat/diodi.png){width=85%}

## LED ja etuvastus

LED on diodi, jonka puolijohdemateriaali säteilee valoa. Kynnysjännite
riippuu väristä: punainen noin 1,8...2,1 V, vihreä ja sininen
2,8...3,3 V. LED tarvitsee aina virtaa rajoittavan etuvastuksen, koska
eksponentiaalisen ominaiskäyrän takia pieni jännitteen muutos muuttaa
virtaa paljon:

$$
R = \frac{U_\text{syöttö} - U_F}{I_\text{LED}} .
$$

```{.python tiedosto="esimerkit/06-led.py" osa="mitoitus"}
```

```{.spice tiedosto="esimerkit/06-led.cir"}
```

```{.python tiedosto="esimerkit/06-led.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-led.odotettu"}
```

Laskettu arvo 132 ohm pyöristetään ylöspäin seuraavaan E12-arvoon,
jolloin virta jää hieman tavoitteen alle eikä ylitä LEDin tai
mikrokontrollerin pinnin rajaa. Mikrokontrollerin lähtöpinnillä on
myös oma sisäresistanssinsa (tyypillisesti kymmeniä ohmeja), joka
pienentää virtaa entisestään; datalehti kertoo lähtöjännitteen
virran funktiona.

## Tasasuuntaus

Tasasuuntaaja muuttaa vaihtojännitteen tasajännitteeksi.
Diodisillassa (Graetzin kytkentä) kaksi diodia johtaa kummallakin
puolijaksolla, joten molemmat puolijaksot saadaan käyttöön ja lähtö on
aina samanmerkkinen. Suodatuskondensaattori latautuu huippuarvoon ja
syöttää kuormaa huippujen välissä. Jännite laskee kondensaattorin
purkautuessa, ja tätä vaihtelua kutsutaan *rippeliksi*.

```{.spice tiedosto="esimerkit/06-tasasuuntaaja.cir"}
```

Karkea arvio olettaa, että kondensaattori syöttää kuormavirtaa koko
puolijakson ajan: $\Delta U = I / (2 f C)$. Tarkempi arvio laskee
eksponentiaalisen purkautumisen ja hetken, jolloin tasasuunnattu
siniaalto nousee taas kondensaattorin jännitteen yli:

```{.python tiedosto="esimerkit/06-tasasuuntaaja.py" osa="arvio"}
```

```{.python tiedosto="esimerkit/06-tasasuuntaaja.py" osa="tarkempi"}
```

```{.tuloste tiedosto="esimerkit/06-tasasuuntaaja.odotettu"}
```

![Diodisillan lähtö (vihreä) ja tasasuunnattu toisiojännite (harmaa).
Kondensaattori latautuu huippujen kohdalla ja purkautuu kuormaan
niiden välissä.](kuvat/tasasuuntaaja.png){width=80%}

Simuloitu rippeli on hieman tarkempaakin arviota pienempi. Syy on
diodien jännite: kondensaattoria ladataan lyhyinä, suurina
virtapiikkeinä, ja suurella virralla diodin ja käämin jännitehäviö on
suurempi kuin arvion 0,85 V. Huippujännite jää siksi pienemmäksi, ja
pienempi jännite tarkoittaa pienempää kuormavirtaa. Virtapiikit ovat
käytännössä tärkeä asia: diodien, muuntajan ja kondensaattorin on
kestettävä ne. Netlistin `Rkaami` on toisiokäämin resistanssi. Se on
fysikaalisesti oikein, ja ilman sitä simulaattori ei löydä ratkaisua,
koska ideaalinen jännitelähde ja johtava diodi muodostaisivat
äärettömän virran (luku 8).

## Zener-diodi

Zener-diodi on suunniteltu toimimaan estosuunnassa läpilyöntialueella,
jossa jännite pysyy lähes vakiona virrasta riippumatta. Sarjavastuksen
kanssa se muodostaa yksinkertaisen jännitteensäätimen:

```{.spice tiedosto="esimerkit/06-zener.cir"}
```

```{.python tiedosto="esimerkit/06-zener.py" osa="zener"}
```

```{.tuloste tiedosto="esimerkit/06-zener.odotettu"}
```

Lähtö muuttuu vain 55 mV, kun syöttö muuttuu 3 V. Zenerin ylimääräinen
virta muuttuu lämmöksi, joten säädin on tehoton; nykyään zeneriä
käytetään lähinnä vertailujännitteenä ja ylijännitesuojana, ja
käyttöjännitteet tehdään lineaarisilla tai hakkurisäätimillä.

## Suojadiodit

Lähes jokaisen integroidun piirin tulossa on diodit käyttöjännitteeseen
ja maahan. Ne johtavat, jos tulojännite ylittää käyttöjännitteen tai
alittaa maan yli 0,3...0,5 V, ja suojaavat piiriä staattiselta
sähköltä. Ne kestävät kuitenkin vain muutaman milliampeerin. Jos
tuloon voi tulla suurempi jännite (pitkä kaapeli, 5 V:n signaali 3,3 V:n
piiriin), sarjavastus rajoittaa virran suojadiodien kestämäksi.
Erillisiä TVS-diodeja käytetään liittimissä, joihin voi kohdistua
sähköstaattinen purkaus.

## Käytännössä

- Diodin "kynnysjännite" on likiarvo. Pienillä virroilla piidiodi
  johtaa 0,5 V:ssa, suurilla 0,8...1 V:ssa. Schottky-diodilla jännite
  on noin puolet pienempi, mikä säästää tehoa tasasuuntaajissa ja
  suojauksissa.
- LED tarvitsee aina virranrajoituksen. Laske etuvastus ja pyöristä
  ylöspäin; käytä useille LEDeille omia vastuksia, koska rinnan
  kytketyt LEDit eivät jaa virtaa tasan.
- Tasasuuntaajan kondensaattorin rippelivirta lämmittää sitä.
  Elektrolyyttikondensaattorin rippelivirran kesto ja jännitteen
  marginaali (vähintään 1,5-kertainen) kannattaa tarkistaa.
- Diodin estosuuntainen jännitekesto (BV) on mitoitettava suurimman
  estojännitteen mukaan marginaalilla.
- Kun käytät valmistajan SPICE-mallia, tarkista, mitkä ilmiöt se
  mallintaa. Yksinkertainen diodimalli ei kuvaa lämpenemistä eikä
  kaikkia kytkentäilmiöitä.

## Itsearviointi

- Osaat selittää diodin ominaiskäyrän Shockleyn yhtälön avulla ja
  kertoa, miksi kynnysjännite on vain likiarvo.
- Osaat sovittaa diodimallin parametrit mitatusta tai simuloidusta
  ominaiskäyrästä.
- Osaat mitoittaa LEDin etuvastuksen ja tarkistaa sen simuloimalla.
- Osaat arvioida tasasuuntaajan lähtöjännitteen ja rippelin sekä
  selittää, miksi simulointi poikkeaa arviosta.
- Osaat selittää zener- ja suojadiodien toiminnan ja käyttötarkoitukset.

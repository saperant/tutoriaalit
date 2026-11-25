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
\approx 25{,}9$ mV huoneenlämmössä ($k$ on Boltzmannin vakio, $T$
lämpötila kelvineinä ja $q$ alkeisvaraus). Virta kasvaa
eksponentiaalisesti: jokainen $n U_T \ln 10$:n lisäys kymmenkertaistaa
virran. Lisäys on 60 mV, kun $n = 1$, ja 120 mV, kun $n = 2$; tämän
luvun diodimallilla ($n \approx 1{,}75$) se on noin 100 mV.
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

![LED ja etuvastus mikrokontrollerin 3,3 V:n lähdössä. Vastuksen yli jää
syötön ja LEDin kynnysjännitteen erotus.](kuvat/led.png){width=34%}

```{.python tiedosto="esimerkit/06-led.py" osa="mitoitus"}
```

```{.spice tiedosto="esimerkit/06-led.cir"}
```

```{.python tiedosto="esimerkit/06-led.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-led.odotettu"}
```

Laskettu arvo 132 Ω pyöristetään ylöspäin seuraavaan E12-arvoon,
jolloin virta jää hieman tavoitteen alle eikä ylitä LEDin tai
mikrokontrollerin pinnin rajaa. Mikrokontrollerin lähtöpinnillä on
myös oma sisäresistanssinsa (tyypillisesti kymmeniä ohmeja), joka
pienentää virtaa entisestään; datalehti kertoo lähtöjännitteen
virran funktiona.

## Tasasuuntaus

Tasasuuntaaja muuttaa vaihtojännitteen tasajännitteeksi.
Diodisillassa (Graetzin kytkentä) on neljä diodia, joista kaksi johtaa
kummallakin puolijaksolla. Kun muuntajan toision solmu `a` on
positiivinen, virta kulkee diodin D1 kautta kuormaan ja palaa diodin D4
kautta solmuun `b`. Toisella puolijaksolla johtavat D2 ja D3. Kuorman
läpi virta kulkee kummallakin kerralla samaan suuntaan, joten molemmat
puolijaksot saadaan käyttöön ja lähtö on aina samanmerkkinen.

![Diodisillan virran reitti (vihreä) kummallakin puolijaksolla. Harmaat
diodit ovat estosuunnassa. Suodatuskondensaattori, joka on netlistissä
kuorman rinnalla, on jätetty kuvasta pois.](kuvat/diodisilta.png){width=100%}

Suodatuskondensaattori latautuu huippuarvoon ja syöttää kuormaa
huippujen välissä. Jännite laskee kondensaattorin purkautuessa, ja tätä
vaihtelua kutsutaan *rippeliksi*.

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

![Zener-säädin. Zener-diodi on estosuunnassa: katodi on lähdössä.
Sarjavastus Rs ottaa vastaan syötön ja lähdön
erotuksen.](kuvat/zener.png){width=52%}

```{.spice tiedosto="esimerkit/06-zener.cir"}
```

```{.python tiedosto="esimerkit/06-zener.py" osa="zener"}
```

```{.tuloste tiedosto="esimerkit/06-zener.odotettu"}
```

Lähtö muuttuu vain 55 mV, kun syöttö muuttuu 3 V. Sarjavastuksen läpi
kulkee kuitenkin koko ajan sama virta: se osa, jota kuorma ei ota,
kulkee zenerin läpi ja muuttuu lämmöksi. Säädin on siksi tehoton, ja
nykyään zeneriä käytetään lähinnä vertailujännitteenä ja
ylijännitesuojana.

## Lineaarisäädin

Käyttöjännitteet tehdään valmiilla säädinpiireillä. *Lineaarisäädin*
on kolminapainen piiri: tulo, lähtö ja maa. Sen sisällä on
vertailujännite, sarjatransistori ja takaisinkytkentä, joka säätää
transistoria niin, että lähtö pysyy asetetussa jännitteessä. Tässä
säädintä käsitellään mustana laatikkona; sisäinen silmukka ja sen
stabiilisuus kuuluvat jatkotaitoon *Analogiaelektroniikka*. Käyttäjän
kannalta säätimellä on kolme ominaisuutta:

- **Pudotusjännite** (*dropout*). Tulon on oltava lähtöä suurempi
  vähintään pudotusjännitteen verran. Perinteisellä säätimellä se on
  noin 2 V, *LDO*-säätimellä (*low dropout*) 0,1...0,5 V.
- **Häviöteho.** Kuormavirta kulkee säätimen läpi tulosta lähtöön,
  joten säätimessä kuluu teho $(U_\text{sisään} - U_\text{ulos})\,I$,
  ja hyötysuhde on enintään $U_\text{ulos} / U_\text{sisään}$.
- **Kondensaattorit.** Säädin tarvitsee tuloonsa ja lähtöönsä
  kondensaattorin pysyäkseen vakaana ja jaksaakseen nopeat
  kuormanmuutokset. Arvot ja sallitut tyypit kerrotaan datalehdessä.

![Lineaarisäädin kytkettynä. Netlistin mallissa kondensaattoreita ei
ole, koska se laskee vain tasajännitteet.](kuvat/saadin.png){width=62%}

Netlistin aliohjelma `LINSAADIN` kuvaa nämä ominaisuudet
käyttäytymislähteellä (`B`), jonka jännite lasketaan lausekkeesta.
Aliohjelmat ja parametrit käydään läpi luvussa 8; tässä riittää, että
rivi `X1` kytkee säätimen piiriin. Samassa netlistissä on vertailuksi
zener-säädin samalle tehtävälle:

```{.spice tiedosto="esimerkit/06-saadin.cir"}
```

```{.python tiedosto="esimerkit/06-saadin.py" osa="haviot"}
```

```{.python tiedosto="esimerkit/06-saadin.py" osa="vertailu"}
```

```{.python tiedosto="esimerkit/06-saadin.py" osa="pudotus"}
```

```{.tuloste tiedosto="esimerkit/06-saadin.odotettu"}
```

Lineaarisäätimen lähtö pysyy 5,00 V:ssa koko alueella, ja sen häviö
kasvaa kuormavirran mukana: ilman kuormaa se kuluttaa vain lepovirtansa.
Zener-säädin ottaa syötöstä lähes saman tehon kuormasta riippumatta ja
menettää säädön, kun kuorma vaatii enemmän virtaa kuin sarjavastus
päästää läpi (tässä noin 46 mA). Viimeinen rivi näyttää
pudotusjännitteen: kun syöttö laskee alle 5,3 V:n, lähtö seuraa
syöttöä 0,3 V sen alapuolella.

Lineaarisäätimen hyötysuhde on tässä 42 %, koska 12 V:sta pudotetaan
5 V:iin. Kun jännite-ero tai virta on suuri, käytetään *hakkurisäädintä*,
joka katkoo virtaa transistorilla ja tasoittaa sen kelalla ja
kondensaattorilla (luvun 7 pulssinleveysmodulaatio); sen hyötysuhde on
tyypillisesti 85...95 %, mutta lähdössä on kytkentätaajuista rippeliä.
Mikrokontrollerikortin tavallinen ratkaisu on hakkuri suurelle
jännite-erolle ja sen perässä LDO herkille analogiaosille.

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
- Laske lineaarisäätimen häviö $(U_\text{sisään} - U_\text{ulos})\,I$
  suurimmalla kuormalla ja tarkista pudotusjännite pienimmällä
  syöttöjännitteellä. Käytä datalehden määräämiä kondensaattoreita.
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
- Osaat laskea lineaarisäätimen häviön ja hyötysuhteen, tarkistaa
  pudotusjännitteen ja kertoa, milloin tilalle valitaan hakkurisäädin.

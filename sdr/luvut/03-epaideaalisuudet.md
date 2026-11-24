# Radion epäideaalisuudet

Laskennallisesti IQ-näyte on kompleksiluku. Fyysisesti se on kahden
analogisen haaran tulos, ja haarat eivät ole täsmälleen samanlaiset.
Edullisissa SDR-laitteissa epäideaalisuudet ovat suuria, ja ne
korjataan ohjelmistolla. Neljä tavallisinta ovat tasakomponentti,
IQ-epätasapaino, vahvistuksen vaihtelu ja kiteen taajuusvirhe.

## Tasakomponentti

Suoramuunnosvastaanottimessa paikallisoskillaattorin signaali vuotaa
sekoittimen tuloon ja sekoittuu itsensä kanssa nollataajuudelle.
Lisäksi haarojen vahvistimien siirtymäjännitteet näkyvät
tasakomponenttina. Spektrissä tämä on piikki tasan keskitaajuudella,
RTL-SDR:n tunnetuin ominaisuus.

```{.python tiedosto="esimerkit/03-dc.py" osa="piikki"}
```

**DC-esto** on derivaattori ja napa yksikköympyrän lähellä. Se on
kapea lovi nollataajuudella. Kertoimella $a = 0{,}999$ lovi on noin
145 Hz leveä 912 kS/s:lla, eikä 30 kHz:n signaali vaimene
lainkaan:

```{.python tiedosto="esimerkit/03-dc.py" osa="esto"}
```

Jos tasakomponentti pysyy vakiona koko tallenteen ajan, myös
keskiarvon vähentäminen toimii. Vahvistuksen ja virityksen muutokset
kuitenkin muuttavat sitä, joten jatkuvassa virrassa käytetään
DC-estoa.

```{.python tiedosto="esimerkit/03-dc.py" osa="keskiarvo"}
```

```{.tuloste tiedosto="esimerkit/03-dc.odotettu"}
```

DC-esto poistaa myös nollataajuudella olevan *hyötysignaalin* osan.
Siksi kokeneet käyttäjät virittävät radion hieman ohi halutusta
taajuudesta (*offset tuning*), esimerkiksi 250 kHz, ja siirtävät
signaalin kohdalleen digitaalisesti (luku 4). Tasakomponentti jää
silloin kaistalle, jota ei käytetä.

## IQ-epätasapaino

Jos Q-haaran vahvistus on $1 + \varepsilon$ ja oskillaattorien
vaihe-ero $90° + \varphi$, taajuudella $+f$ olevasta signaalista
vuotaa peilikuva taajuudelle $-f$. **Peilivaimennus** (*image
rejection ratio*, IRR) on

$$\text{IRR} = \frac{1 + 2g\cos\varphi + g^2}{1 - 2g\cos\varphi + g^2},
\qquad g = 1 + \varepsilon .$$

```{.python tiedosto="esimerkit/03-iq.py" osa="malli"}
```

Epätasapaino korjataan **sokeasti** signaalin tilastoista. Kun kaistalla
on paljon toisistaan riippumattomia signaaleja, signaali on
ympyräsymmetrinen: I:llä ja Q:lla on sama teho, eivätkä ne korreloi.
Epätasapaino rikkoo molemmat ehdot, ja Gram–Schmidt-ortogonalisointi
palauttaa ne: Q:sta poistetaan sen I:n suuntainen osa, ja tehot
tasataan.

```{.python tiedosto="esimerkit/03-iq.py" osa="korjaus"}
```

```{.python tiedosto="esimerkit/03-iq.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/03-iq.odotettu"}
```

Mitattu peilivaimennus osuu kaavaan. Korjauksen jälkeen peilikuvan
kohdalla on enää kohinaa, joten 84 dB on mittauksen lattia eikä
korjauksen raja. Korjaus edellyttää kuitenkin, että ympyräsymmetrisyys
pätee. Yksittäinen voimakas kantoaalto ei ole ympyräsymmetrinen, ja
silloin tilastot pitää kerätä pitkältä ajalta tai laitteen
kalibrointisignaalista. Esimerkissä laajakaistainen kohina edustaa
kaistan "muuta liikennettä".

## Vahvistuksen säätö

Luvun 2 perusteella vahvistuksen pitää riittää heikoille signaaleille
ylikuormittamatta vahvoja. RTL-SDR:n virittimessä on portaittain
säädettävä RF- ja IF-vahvistus, ja automaattinen tila säätää sitä
laitteessa. Ohjelmistossa käytetään lisäksi digitaalista **AGC:tä**
(*automatic gain control*), joka tasaa signaalin tason ilmaisimelle.
Esimerkiksi QAM-ilmaisimen päätösrajat ja FSK-ilmaisimen kynnys
oletetaan tietylle tasolle.

```{.python tiedosto="esimerkit/03-agc.py" osa="tulo"}
```

AGC seuraa tehon verhokäyrää desibeleinä. Vahvistus pienenee nopeasti
(isku, *attack*), kun signaali voimistuu, ja kasvaa hitaasti
(palautus, *decay*), kun se heikkenee. Epäsymmetria estää
ylikuormituksen ja vahvistuksen pumppauksen lyhyiden taukojen
aikana.

```{.python tiedosto="esimerkit/03-agc.py" osa="agc"}
```

```{.python tiedosto="esimerkit/03-agc.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/03-agc.odotettu"}
```

Hetkellä 100 ms signaali voimistuu 30 dB, ja lähtö käy hetken 12 dB
täyden skaalan yli ennen kuin isku ehtii reagoida. Viiden millisekunnin
kuluttua taso on tavoitteessa. Palautus 50 ms:n aikavakiolla on
hidas: kun signaali heikkenee 200 ms:n kohdalla, taso on 80 ms
myöhemminkin vielä 3 dB tavoitteen alapuolella. Pakettiradioissa AGC lukitaan tämän vuoksi
alkuosan ajaksi, ja vahvistus pidetään vakiona koko paketin ajan.

## Kiteen taajuusvirhe

Edullisen RTL-SDR:n 28,8 MHz:n kiteen tarkkuus on kymmeniä
miljoonasosia (ppm), ja lämpötila muuttaa sitä. Virhe skaalaa sekä
paikallisoskillaattorin että näytetaajuuden. Viritystaajuudella
100 MHz 37 ppm tarkoittaa 3,7 kHz:n siirtoa, 1 090 MHz:llä jo 40 kHz:n
siirtoa. Virhe mitataan tunnetusta signaalista, kuten FM-aseman
kantoaallosta, GSM-tukiaseman taajuuskorjauskanavasta tai omasta
kalibrointilähetteestä.

```{.python tiedosto="esimerkit/03-ppm.py" osa="arvio"}
```

Taajuuden arviointi FFT:n huipusta rajoittuu binnin leveyteen.
Nollatäyttö tihentää binnejä, ja paraabelisovitus kolmen binnin
logaritmeihin antaa huipun murto-osan tarkkuudella.

```{.python tiedosto="esimerkit/03-ppm.py" osa="mittaus"}
```

```{.python tiedosto="esimerkit/03-ppm.py" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/03-ppm.odotettu"}
```

Korjaus annetaan laitteelle (`rtl_sdr -p 37`) tai tehdään
digitaalisella sekoituksella. Ppm-virhe ei korjaa näytetaajuuden
virhettä, mutta se on yleensä merkityksetön: 37 ppm:n virhe
näytetaajuudessa muuttaa 1187,5 bit/s:n bittinopeutta 0,04 bit/s.
Pitkissä tallenteissa ja tarkoissa ajoituksissa sekin pitää
huomioida. Kalliimmissa laitteissa on lämpötilakompensoitu kide
(TCXO, noin 1 ppm), ja ammattilaitteet lukitaan GPS-vertailuun.

## Käytännössä

- **Viritä ohi.** Viritä 100–250 kHz halutun signaalin viereen ja
  sekoita se digitaalisesti kohdalleen. Tasakomponentti ja
  matalien taajuuksien 1/f-kohina jäävät pois kaistalta.
- **Käytä DC-estoa virrassa, keskiarvoa tallenteessa.** DC-esto on
  kevyt (kaksi kertolaskua näytettä kohti) ja seuraa muutoksia.
- **Kalibroi IQ-epätasapaino kerran ja seuraa sitä.** Epätasapaino
  riippuu taajuudesta ja vahvistuksesta, mutta muuttuu hitaasti.
  Sokea korjaus toimii hyvin laajakaistaisessa liikenteessä.
- **Mittaa kiteen virhe lämpimänä.** Virhe muuttuu ensimmäisten
  minuuttien aikana, kun laite lämpenee. Tallenna se laitteen
  asetuksiin.
- **Älä luota automaattiseen vahvistukseen mittauksissa.**
  Tehomittauksessa vahvistuksen on oltava kiinteä ja tunnettu.
  AGC tasaa tason ilmaisimelle, ja se on oikea paikka sille.

## Itsearviointi

- Osaat selittää, mistä suoramuunnosvastaanottimen tasakomponentti
  syntyy, ja poistaa sen DC-estolla tai virittämällä ohi.
- Osaat mallintaa IQ-epätasapainon, laskea peilivaimennuksen ja
  korjata epätasapainon sokeasti tilastoista.
- Osaat toteuttaa AGC:n, jossa on erilliset isku- ja
  palautusaikavakiot, ja perustella niiden valinnan.
- Osaat mitata kiteen taajuusvirheen tunnetusta signaalista ja
  arvioida sen vaikutuksen eri taajuuksilla.

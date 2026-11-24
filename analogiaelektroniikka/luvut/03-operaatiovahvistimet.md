# Operaatiovahvistimet

Operaatiovahvistin on integroitu erovahvistin, jossa on kymmeniä
transistoreja: erovahvistin tuloasteena, suuren vahvistuksen välivaihe
ja seuraajatyyppinen lähtöaste. Sen avoimen silmukan vahvistus on hyvin
suuri mutta huonosti määritelty ja taajuudesta riippuva. Juuri siksi
sitä ei koskaan käytetä ilman takaisinkytkentää: ulkoiset vastukset
määräävät vahvistuksen, ja vahvistimen suuri sisäinen vahvistus
huolehtii siitä, että tulos on tarkka. Luvun 2 periaate, ominaisuudet
passiivisista komponenteista, toteutuu tässä melkein täydellisesti.

## Ihanteellinen malli ja kaksi sääntöä

Ihanteellisen operaatiovahvistimen analyysiin riittää kaksi sääntöä,
kun piirissä on negatiivinen takaisinkytkentä:

1. Tuloihin ei kulje virtaa.
2. Lähtö asettuu niin, että tulojen välinen jännite on nolla.

Toinen sääntö on luvun 1 virtuaalimaa. Sääntöjen avulla tavalliset
kytkennät ratkeavat parilla rivillä:

| Kytkentä | Siirtoyhtälö | Tuloimpedanssi |
|----------|--------------|----------------|
| invertoiva | $u_o = -\frac{R_2}{R_1} u_i$ | $R_1$ |
| ei-invertoiva | $u_o = \left(1 + \frac{R_2}{R_1}\right) u_i$ | hyvin suuri |
| seuraaja | $u_o = u_i$ | hyvin suuri |
| summaaja | $u_o = -R_f \sum_k u_k / R_k$ | $R_k$ kullekin tulolle |
| integraattori | $u_o = -\frac{1}{RC}\int u_i\,dt$ | $R$ |
| erovahvistin | $u_o = \frac{R_2}{R_1}(u_+ - u_-)$ | $R_1$ / $R_1 + R_2$ |

Invertoivan kytkennän summaaja on sama piiri usealla tulovastuksella:
virtuaalimaa erottaa tulot toisistaan, ja kunkin tulon virta summautuu
takaisinkytkentävastukseen. Näin sekoitetaan audiosignaaleja tai
lisätään anturisignaaliin siirtojännite.

## Makromalli

SPICE-simulointia varten operaatiovahvistin kuvataan *makromallilla*,
joka jäljittelee liittimissä näkyvää käyttäytymistä mutta ei sisäistä
rakennetta. Tämän tutoriaalin malli on tarkoituksella yksinkertainen,
jotta jokainen sen ominaisuus näkyy ja on laskettavissa:

```{.spice tiedosto="esimerkit/operaatiovahvistimet.lib"}
```

Tulojen erojännite ohjaa virtalähdettä `B1`, jonka virta on
$g_m u_d$ pienillä jännitteillä mutta rajoittuu arvoon $I_{max}$
(funktio tanh). Virta latautuu RC-kuormaan: resistanssi antaa
tasavahvistuksen $A_{ol} = g_m R_A$, ja kapasitanssi tekee vahvistuksesta
yksinapaisen. Napa on taajuudella $GBW/A_{ol}$, tässä 10 Hz, ja sen
yläpuolella vahvistus putoaa 20 dB dekadilla niin, että se on 1
taajuudella $GBW$. Virran rajoitus tekee *nousunopeuden*:
kondensaattorin jännite voi muuttua enintään nopeudella
$I_{max}/C_A = SR$. Lähtöjännite leikataan syöttöjännitteiden sisään, ja
lähdössä on resistanssi. Valmistajien mallit ovat paljon tarkempia, mutta
rakennuspalikat ovat samat.

## Vahvistus ja kaistanleveys

Yksinapaisella vahvistimella vahvistuksen ja kaistanleveyden tulo on
vakio. Ei-invertoivan vahvistimen, jonka vahvistus on
$G = 1 + R_2/R_1$, kaistanleveys on $GBW/G$: kymmenkertainen vahvistus
maksaa kymmenesosan kaistasta.

```{.spice tiedosto="esimerkit/03-kaistanleveys.cir"}
```

```{.python tiedosto="esimerkit/03-kaistanleveys.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/03-kaistanleveys.odotettu"}
```

Ensimmäinen vertailu ilman kuormitustermiä erosi 5 %. Syy oli
lähtöresistanssi: 50 ohmin lähtö ja 1 kohmin takaisinkytkentäverkko
muodostavat jännitteenjakajan, joka pienentää silmukkavahvistusta
samassa suhteessa. Kun termi otetaan mukaan, malli ja simulointi
täsmäävät. Sama ilmiö on todellisissa piireissä: pieni
takaisinkytkentäresistanssi kuormittaa lähtöä ja syö kaistaa.

## Integraattori

Kun invertoivan vahvistimen takaisinkytkentävastus korvataan
kondensaattorilla, saadaan integraattori. Virtuaalimaan ansiosta tulovirta
on $u_i/R$, ja se latautuu kondensaattoriin, joten lähtö muuttuu
nopeudella $-u_i/(RC)$. Kanttiaallosta tulee kolmioaalto.

```{.spice tiedosto="esimerkit/03-integraattori.cir"}
```

```{.python tiedosto="esimerkit/03-integraattori.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/03-integraattori.odotettu"}
```

Puhdas integraattori integroi myös tulon pienen tasakomponentin ja
vahvistimen offsetin, ja lähtö ajautuu syöttöjännitteeseen. Rinnakkainen
1 Mohmin vastus rajoittaa tasavahvistuksen sataan, ja piiri integroi
vain taajuuksilla, jotka ovat selvästi yli $1/(2\pi R_f C) = 16$ Hz.
Simulointi ajetaan 60 ms, jotta tämän aikavakion alkuvaihe on ohi.
Integraattoreita käytetään aktiivisissa suodattimissa, PID-säätimissä ja
sigma-delta-muuntimissa (luku 6).

## Instrumentointivahvistin

Monet anturit, kuten venymäliuskasilta, antavat pienen *erojännitteen*
suuren *yhteismuotoisen* jännitteen päällä: 10 mV:n ero 2,5 V:n
tasossa. Vahvistimen on vahvistettava eroa ja jätettävä yhteinen taso
huomiotta. Yhteismuotoisen jännitteen vaimennus (*CMRR*,
common-mode rejection ratio) on erovahvistuksen ja yhteismuotoisen
vahvistuksen suhde desibeleinä.

Kolmen operaatiovahvistimen instrumentointivahvistimessa kaksi
ei-invertoivaa vahvistinta puskuroi tulot ja vahvistaa erojännitteen
yhden vastuksen $R_g$ avulla ($G = 1 + 2R/R_g$), ja erovahvistin
poistaa yhteisen tason. Erovahvistimen CMRR riippuu sen neljän vastuksen
sovituksesta: jos yksi poikkeaa suhteellisesti $\varepsilon$,
yhteismuotoinen vahvistus on $\varepsilon/(2 + \varepsilon)$.

```{.spice tiedosto="esimerkit/03-instrumentointi.cir"}
```

```{.python tiedosto="esimerkit/03-instrumentointi.py" osa="kasin"}
```

```{.python tiedosto="esimerkit/03-instrumentointi.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/03-instrumentointi.odotettu"}
```

0,1 %:n vastus riittää 92 dB:n vaimennukseen, kun tuloasteiden vahvistus
on 21: vahvistus ennen erovahvistinta parantaa CMRR:ää samalla
kertoimella. Siksi instrumentointivahvistimissa vahvistus tehdään
tuloasteissa, ja siksi integroiduissa instrumentointivahvistimissa
(INA-sarjat) vastukset on trimmattu laserilla. Erillisistä
komponenteista rakennettuna sovitettu vastusverkko on tavallista halvempi
kuin neljä tarkkuusvastusta.

## Tasonsiirto AD-muuntimelle

Tavallinen käytännön tehtävä: anturi antaa ±1 V, mutta mikrokontrollerin
AD-muunnin mittaa vain 0 ... 3,3 V, ja käytössä on yksi 3,3 V:n syöttö.
Signaali on vahvistettava ja siirrettävä alueen keskelle niin, että
reunoille jää hieman tilaa. Ei-invertoiva summaaja tekee molemmat:
tulo ja referenssijännite summautuvat yhtä suurten vastusten kautta
plus-tuloon, ja vahvistus $1 + R_4/R_3$ skaalaa summan.

```{.python tiedosto="esimerkit/03-tasonsiirto.py" osa="mitoitus"}
```

```{.spice tiedosto="esimerkit/03-tasonsiirto.cir"}
```

```{.tuloste tiedosto="esimerkit/03-tasonsiirto.odotettu"}
```

Lähtöalue 0,15 ... 3,15 V jättää 150 mV marginaalin kumpaankin reunaan,
koska rail-to-rail-lähtökään ei pääse aivan syöttöjännitteisiin.
Referenssijännite 1,1 V tehdään käytännössä jakajalla
referenssipiiristä ja puskuroidaan, tai valitaan vastukset niin, että
referenssiksi käy suoraan AD-muuntimen oma referenssijännite. Silloin
mittaus on ratiometrinen (luku 6).

## Todellisen vahvistimen rajat

Ihanteellinen malli unohtaa neljä asiaa, jotka ratkaisevat käytännössä:

- *Lähdön jännitealue.* Perinteisen vahvistimen lähtö ei pääse lähemmäs
  kuin 1 ... 2 V syöttöjännitteistä. *Rail-to-rail*-lähtö pääsee
  kymmenien millivolttien päähän. Pienillä syöttöjännitteillä (3,3 V,
  5 V) ero on ratkaiseva.
- *Nousunopeus (slew rate).* Lähtö voi muuttua enintään nopeudella
  $SR$, tyypillisesti 0,5 ... 20 V/µs. Suurella amplitudilla tämä rajoittaa
  kaistaa enemmän kuin $GBW$: siniaalto pysyy siistinä vain, kun
  $2\pi f \hat{U} < SR$.
- *Offsetjännite.* Tuloasteen transistorit eivät ole täsmälleen samanlaisia,
  ja vahvistin käyttäytyy kuin tulojen väliin olisi kytketty pieni
  jännitelähde, tyypillisesti 0,1 ... 5 mV. Se vahvistuu ei-invertoivalla
  vahvistuksella $1 + R_2/R_1$ riippumatta siitä, onko kytkentä
  invertoiva.
- *Tulojännitealue ja biasvirrat.* Tulojen on oltava sallitulla
  alueella, ja tuloihin kulkee pieni virta, joka suurten vastusten yli
  muuttuu offsetiksi.

```{.spice tiedosto="esimerkit/03-rajat.cir"}
```

```{.python tiedosto="esimerkit/03-rajat.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/03-rajat.odotettu"}
```

Perinteinen vahvistin ±5 V:n syötöllä antaa −3,5 V, vaikka piiri
pyytää −6 V:ia: lähtö leikkautuu, ja signaalin huiput litistyvät.
Rail-to-rail-vahvistin pääsee −4,95 V:iin. 8 V:n askel vie 12,8 µs
10 %:sta 90 %:iin, kun $GBW$ yksinään antaisi alle mikrosekunnin.
2 mV:n offset näkyy lähdössä 202 mV:na. Jokaisen rajan voi laskea
datalehden luvuista ennen kuin piiri rakennetaan, ja jokainen niistä on
joskus syy siihen, että toimiva piiri ei toimi.

## Käytännössä

- Analysoi kytkentä ensin ihanteellisella mallilla (virtuaalimaa, ei
  tulovirtaa), sitten tarkista rajat: lähdön alue, nousunopeus,
  kaistanleveys ja offset.
- Valitse vahvistin syöttöjännitteen mukaan. 3,3 ja 5 V:n
  järjestelmissä tarvitaan rail-to-rail-lähtö ja usein myös -tulo.
- Älä käytä operaatiovahvistinta vertailijana. Se on suunniteltu
  lineaariseen käyttöön, ja kyllästyksestä toipuminen on hidasta.
  Vertailijapiireissä on nopea, logiikkatasoinen lähtö.
- Pidä takaisinkytkentävastukset kohtuullisina, 1 ... 100 kohm. Pienet
  kuormittavat lähtöä, suuret lisäävät kohinaa ja biasvirtojen
  aiheuttamaa offsetia.
- Kytke jokaisen vahvistimen syöttönastoihin 100 nF:n
  ohituskondensaattori mahdollisimman lähelle (luku 7).

## Itsearviointi

- Osaat analysoida invertoivan, ei-invertoivan, summaavan ja
  integroivan kytkennän virtuaalimaan avulla.
- Osaat laskea suljetun silmukan kaistanleveyden vahvistus-
  kaistanleveystulosta ja ottaa lähdön kuormituksen huomioon.
- Osaat selittää instrumentointivahvistimen rakenteen ja laskea
  vastusten epäsovituksen vaikutuksen CMRR:ään.
- Osaat arvioida lähdön jännitealueen, nousunopeuden ja offsetin
  vaikutuksen ja tunnistaa ne simuloinnissa.
- Osaat lukea operaatiovahvistimen makromallin ja selittää, mikä sen osa
  tuottaa minkäkin ominaisuuden.

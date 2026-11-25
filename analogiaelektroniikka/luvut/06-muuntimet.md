# AD- ja DA-muuntimet

AD-muunnin (ADC) on raja, jossa analoginen signaali muuttuu luvuiksi, ja
DA-muunnin (DAC) tekee saman toiseen suuntaan. Muunnin tekee kaksi
asiaa: *näytteistää* signaalin ajassa ja *kvantisoi* sen arvoalueella.
Näytteistyksen seuraukset, Nyquistin taajuus ja laskostuminen,
käsitellään taidossa *Signaalit ja järjestelmät* ja luvun 4
antialiasointisuodattimessa. Tämä luku keskittyy kvantisointiin,
muunninarkkitehtuureihin ja niihin analogisiin yksityiskohtiin, jotka
ratkaisevat, saavuttaako muunnin paperilla luvatun tarkkuuden.
DA-muunnin käsitellään ensin, koska tavallisimpien AD-muuntimien
sisällä on DA-muunnin.

## Kvantisointi ja SNR

N-bittinen muunnin jakaa alueensa $2^N$ portaaseen. Yksi porras on
*LSB* (least significant bit): referenssijännite jaettuna $2^N$:llä.
Kvantisointivirhe on enintään puoli LSB:tä.

![Kolmibittisen muuntimen porrasfunktio ja kvantisointivirhe. Virhe
pysyy ±½ LSB:n sisällä, kunnes tulo ylittää ylimmän
portaan.](kuvat/kvantisointi.png){width=66%}

Kun signaali on monimutkainen, virhe käyttäytyy kuin tasajakautunut
kohina, jonka tehollisarvo on $\mathrm{LSB}/\sqrt{12}$. Täyden alueen
siniaallon ja tämän kohinan suhde on

$$
\mathrm{SNR} = 6{,}02\,N + 1{,}76\ \mathrm{dB}.
$$

Jokainen bitti lisää kuusi desibeliä. Sama kaava kuvaa myös
laskennan sananpituutta; sen näkökulman käsittelee taito *Lukujen
esitys ja kiinteän pilkun aritmetiikka*. Kaavan voi todentaa
simuloimalla ihanteellisen muuntimen ja laskemalla kohinan spektristä.
Signaalin jaksojen määrä valitaan alkuluvuksi, jolloin näytteistys on
*koherentti*: jokainen näyte osuu eri vaiheeseen, ja kvantisointivirhe
leviää spektriin tasaisesti eikä keskity harmonisiksi.

```{.python tiedosto="esimerkit/06-kvantisointi.py" osa="muunnin"}
```

```{.python tiedosto="esimerkit/06-kvantisointi.py" osa="snr"}
```

```{.tuloste tiedosto="esimerkit/06-kvantisointi.odotettu"}
```

Oikea muunnin jää aina tämän alle: sen kohinaan lisätään vahvistimien
ja referenssin kohina, kellon värinä (*jitter*) ja epälineaarisuus.
Datalehti ilmoittaa todellisen suorituskyvyn *efektiivisenä bittimääränä*
$\mathrm{ENOB} = (\mathrm{SINAD} - 1{,}76)/6{,}02$. 16-bittisen
muuntimen ENOB on tyypillisesti 13 ... 14,5 bittiä.

## R-2R-tikapuu-DA-muunnin

DA-muunnin muuttaa koodin jännitteeksi. R-2R-tikapuussa jokainen bitti
kytkee 2R-vastuksen referenssiin tai maahan, ja tikapuu jakaa
virrat niin, että kunkin bitin paino on puolet edellisestä. Rakenteessa
on vain kahta vastusarvoa, mikä tekee sovituksesta helpon.

![Nelibittinen R-2R-tikapuu. Jokainen bittitulo on joko
referenssijännitteessä (1) tai maassa (0). Solmut `n0`–`n3` vastaavat
netlistin solmuja.](kuvat/r2r.png){width=80%}

Esimerkki simuloi kaikki 16 koodia yhdellä ajolla:

```{.python tiedosto="esimerkit/06-r2r.py" osa="netlist"}
```

Muuntimen virheet kuvataan kahdella luvulla. *Integraalinen
epälineaarisuus* (INL) on poikkeama ihanteellisesta suorasta ja
*differentiaalinen epälineaarisuus* (DNL) kahden peräkkäisen koodin
välin poikkeama yhdestä LSB:stä. Jos DNL on alle −1 LSB, muunnin ei ole
*monotoninen*: suurempi koodi antaa pienemmän jännitteen, mikä on
säätösilmukassa vakava vika.

```{.python tiedosto="esimerkit/06-r2r.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-r2r.odotettu"}
```

![Simuloidun muuntimen virheet, kun ylimmän bitin vastus on 5 % liian
suuri. INL on poikkeama päätepisteiden kautta kulkevasta suorasta; DNL
näyttää yhden liian lyhyen askeleen koodien 7 ja 8
välissä.](kuvat/r2r-virheet.png){width=92%}

Pahin kohta on keskellä, koodien 7 (0111) ja 8 (1000) välissä, jossa
kaikki bitit vaihtuvat ja ylimmän bitin virhe näkyy kokonaan. Neljällä
bitillä 1 %:n virhe on merkityksetön, mutta virhe skaalautuu
bittimäärän mukana: 16-bittisessä muuntimessa sama vastusvirhe olisi
satoja LSB:itä. Siksi tarkat DA-muuntimet käyttävät laserilla
trimmattuja vastuksia, segmentoituja rakenteita (ylimmät bitit
termometrikoodattuina) tai tämän luvun lopussa esiteltävää
sigma-delta-tekniikkaa.

## PWM ja RC-suodin DA-muuntimena

Mikrokontrollerin yleisin "DA-muunnin" ei ole vastusverkko vaan
ajastimen PWM-lähtö ja RC-alipäästösuodin. Pulssisuhde määrää
keskiarvon (taito *Elektroniikan perusteet ja SPICE*), ja suodin poistaa
kytkentätaajuuden. Suotimen aikavakio on kompromissi: suuri aikavakio
pienentää *rippeliä*, joka jää lähtöön, mutta hidastaa asettumista
uuteen arvoon.

```{.python tiedosto="esimerkit/06-pwm-da.py" osa="kompromissi"}
```

```{.spice tiedosto="esimerkit/06-pwm-da.cir"}
```

```{.tuloste tiedosto="esimerkit/06-pwm-da.odotettu"}
```

1 ms:n aikavakiolla rippeliä on 2,4 LSB, eli kahdeksasta bitistä
alimmat hukkuvat siihen. Kymmenkertainen aikavakio pudottaa
rippelin neljäsosaan LSB:stä, mutta asettuminen vie 62 ms. Korkeampi
PWM-taajuus tai toisen kertaluvun suodin (luku 4) parantaa molempia.
PWM-muunnin sopii hitaisiin ohjauksiin, kuten säätöarvoihin ja
kirkkauksiin; signaalien tuottamiseen käytetään oikeaa DA-muunninta.

## Peräkkäisapproksimaatiomuunnin (SAR)

SAR-muunnin on mikrokontrollerien yleisin AD-muunnin. Se tekee
binäärihaun: sisäinen DA-muunnin tuottaa koejännitteen, vertailija
(luku 5) kertoo, onko tulo suurempi, ja ohjauslogiikka päättää bitti
kerrallaan ylimmästä alkaen.

```{.dot otsikko="SAR-muuntimen rakenne. Näytteenotto ja pito jäädyttää tulon N vertailun ajaksi."}
digraph {
  rankdir=LR;
  tulo [shape=plaintext, style="", label="tulo"];
  sh [label="näytteenotto\nja pito"];
  vert [label="vertailija"];
  sar [label="SAR-logiikka\n(N bittiä)"];
  dac [label="DA-muunnin"];
  koodi [shape=plaintext, style="", label="koodi"];
  tulo -> sh -> vert -> sar -> koodi;
  sar -> dac;
  dac -> vert;
}
```

```{.python tiedosto="esimerkit/06-sar.py" osa="sar"}
```

```{.tuloste tiedosto="esimerkit/06-sar.odotettu"}
```

![Sama haku kuvana: DA-muuntimen koejännite lähestyy tuloa (katkoviiva)
puolittuvin askelin. Kun koejännite ylittää tulon, bitti poistetaan ja
seuraava koe tehdään alempaa.](kuvat/sar-haku.png){width=80%}

N-bittinen muunnos vie N vertailua, joten SAR-muunnin on kohtuullisen
nopea (tyypillisesti 100 kS/s ... 10 MS/s) ja energiatehokas. Tulon on
pysyttävä paikallaan koko haun ajan; siksi edessä on näytteenotto ja
pito. SAR-muuntimen tarkkuus riippuu sisäisen DA-muuntimen tarkkuudesta:
sen INL ja DNL siirtyvät suoraan AD-muunnokseen. Integroidussa
muuntimessa DA-muunnin on yleensä vastusten sijaan kytkettyjen
kondensaattoreiden verkko, jonka kondensaattorit toimivat samalla
näytteenottokondensaattorina.

## Näytteenotto ja pito

Näytteenottovaiheessa kytkin yhdistää tulon pitokondensaattoriin, ja
kondensaattori latautuu kytkimen resistanssin kautta. Kytkimen
avautuessa jännitteen on oltava puolen LSB:n päässä lopullisesta
arvosta. RC-latautuminen lähestyy loppuarvoa eksponentiaalisesti, joten
tarvittava aika kasvaa lineaarisesti bittimäärän mukana:
$t = RC \ln 2^{N+1}$.

![Näytteenotto- ja pitopiiri. Kytkin S1 (johtavana 100 Ω) lataa
pitokondensaattorin Ch, ja puskuri lukee sen jännitettä
kuormittamatta.](kuvat/naytteenotto.png){width=66%}

```{.spice tiedosto="esimerkit/06-naytteenotto.cir"}
```

```{.python tiedosto="esimerkit/06-naytteenotto.py" osa="asettuminen"}
```

```{.tuloste tiedosto="esimerkit/06-naytteenotto.odotettu"}
```

![Simuloidun pitokondensaattorin virhe loppuarvosta logaritmisella
asteikolla. Virhe pienenee eksponentiaalisesti, joten jokainen lisäbitti
maksaa saman ajan, 0,69 aikavakiota. Pystyviivat ovat hetket, joina
virhe alittaa puoli LSB:tä 8, 12 ja 16 bitillä.](kuvat/asettuminen.png){width=80%}

12 bittiä vaatii yhdeksän aikavakiota, 16 bittiä yli 11. Tämä selittää,
miksi mikrokontrollerin ADC:n eteen tarvitaan pienen lähtöimpedanssin
ohjain tai RC-suodin, jonka kondensaattori on paljon suurempi kuin
näytteenottokondensaattori: korkeaimpedanssinen lähde, kuten suuren
vastuksen jännitteenjakaja, ei ehdi ladata kondensaattoria, ja tulos jää
liian pieneksi. Datalehti antaa näytteenottoajan ja suurimman sallitun
lähdeimpedanssin.

## Sigma-delta-muunnin

Sigma-delta-muunnin kääntää asetelman: yksibittinen vertailija, mutta
näytetaajuus moninkertainen tarvittavaan nähden (ylinäytteistys, *OSR*).
Integraattori summaa tulon ja lähdön erotuksen, ja takaisinkytkentä pitää
yksibittisen lähdön keskiarvon tulon tasossa. Kvantisointikohinaa on
valtavasti, mutta takaisinkytkentä *muokkaa* sen: kohina työntyy
korkeille taajuuksille, joista digitaalinen desimointisuodin sen
poistaa.

```{.python tiedosto="esimerkit/06-sigmadelta.py" osa="modulaattori"}
```

```{.python tiedosto="esimerkit/06-sigmadelta.py" osa="kaista"}
```

```{.tuloste tiedosto="esimerkit/06-sigmadelta.odotettu"}
```

![Ensimmäisen kertaluvun sigma-delta-modulaattorin spektri.
Kvantisointikohina kasvaa taajuuden mukana 20 dB dekadilla; pystyviivat
ovat kaistan reunat ylinäytteistyksillä 16 ja 128.](kuvat/sigmadelta.png){width=80%}

Jokainen ylinäytteistyksen kaksinkertaistus parantaa SNR:ää noin 9 dB:llä
eli puolitoista bittiä: 3 dB tavallisesta ylinäytteistyksestä ja 6 dB
kohinanmuokkauksesta. Ensimmäisen kertaluvun modulaattori tuottaa
helposti jaksollisia kuvioita, jotka näkyvät kaistalla piikkeinä;
esimerkin vertailijan tuloon lisätty pieni satunnaiskohina (*dither*)
hajottaa ne. Kaupalliset sigma-delta-muuntimet ovat kolmannen ... viidennen
kertaluvun, ja niiden OSR on 64 ... 256. Niillä päästään audiossa ja
mittaustekniikassa 20 ... 24 bittiin, ja analoginen antialiasointisuodin
voi olla yksinkertainen, koska näytetaajuus on niin korkea.

## Referenssi

Muunnin mittaa aina suhteessa referenssijännitteeseen: koodi on
$2^N u_{in}/U_{ref}$. Referenssin virhe ja kohina siirtyvät suoraan
tulokseen. Käyttöjännite on huono referenssi, koska siinä on
kytkentähäiriöitä ja se vaihtelee kuorman mukana. Erillinen
referenssipiiri (esimerkiksi 2,5 V, 0,1 %, 10 ppm/K) tai
ratiometrinen mittaus auttaa. *Ratiometrisessä* mittauksessa anturi, kuten
potentiometri tai venymäliuskasilta, syötetään samasta jännitteestä kuin
muuntimen referenssi, jolloin syöttöjännitteen vaihtelu kumoutuu.

## Käytännössä

- Mitoita ADC:n ohjauspiiri näytteenoton mukaan: lähdeimpedanssi ja
  RC-suodin datalehden suositusten mukaan. Suuren vastuksen jakaja
  suoraan ADC-tuloon antaa väärän tuloksen.
- Arvioi todellinen tarkkuus ENOB:n, referenssin tarkkuuden ja
  vahvistimen kohinan perusteella, ei bittimäärästä.
- Käytä ratiometristä mittausta resistiivisille antureille aina, kun
  mahdollista.
- Valitse SAR nopeaan ja yleiskäyttöiseen mittaukseen, sigma-delta
  hitaaseen ja tarkkaan (punnitus, lämpötila, audio).
- Tarkista DA-muuntimen monotonisuus ja DNL, kun muunnin on säätösilmukan
  osa.
- Mitoita PWM-lähdön suodin rippelin ja asettumisajan mukaan: rippeli
  alle puolen LSB:n siitä tarkkuudesta, jota oikeasti tarvitset.

## Itsearviointi

- Osaat laskea LSB:n, kvantisointikohinan ja ihanteellisen SNR:n ja
  todentaa kaavan simuloimalla.
- Osaat selittää SAR-muuntimen binäärihaun ja näytteenotto- ja
  pitopiirin asettumisvaatimuksen.
- Osaat selittää sigma-delta-muuntimen kohinanmuokkauksen ja laskea
  ylinäytteistyksen vaikutuksen.
- Osaat selittää R-2R-tikapuun toiminnan sekä INL:n, DNL:n ja
  monotonisuuden.
- Osaat mitoittaa PWM-lähdön RC-suotimen rippelin ja asettumisajan
  kompromissina.
- Osaat perustella referenssin valinnan ja ratiometrisen mittauksen.

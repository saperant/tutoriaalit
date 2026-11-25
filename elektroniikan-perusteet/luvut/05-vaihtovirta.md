# Vaihtovirta, impedanssi ja taajuusvaste

Luvun 4 piirejä tarkasteltiin ajan funktiona. Kun herätteenä on
siniaalto, sama piiri on paljon helpompi kuvata *taajuuden* funktiona:
siniaallon kulkiessa lineaarisen piirin läpi tulos on samantaajuinen
siniaalto, jonka amplitudi ja vaihe ovat muuttuneet. Tämä luku
esittelee tehollisarvon, kompleksisen impedanssin ja taajuusvasteen,
ja SPICEn AC-analyysin, joka laskee ne.

## Sinimuotoiset suureet ja tehollisarvo

Sinimuotoinen jännite on

$$
u(t) = \hat{U} \sin(2\pi f t + \varphi),
$$

missä $\hat{U}$ on huippuarvo, $f$ taajuus ja $\varphi$ vaihekulma.
Kulmataajuus $\omega = 2\pi f$ yksinkertaistaa kaavoja.

Vaihtojännitteen "suuruus" ilmoitetaan yleensä *tehollisarvona*
(RMS, *root mean square*): se tasajännite, joka tuottaisi vastukseen
saman keskimääräisen tehon. Siniaallolle $U_\text{rms} = \hat{U} /
\sqrt{2}$, joten 230 V:n verkkojännitteen huippuarvo on noin 325 V.
Muille aaltomuodoille suhde on eri, ja sen voi laskea numeerisesti
suoraan määritelmästä:

```{.python tiedosto="esimerkit/05-tehollisarvo.py" osa="rms"}
```

```{.tuloste tiedosto="esimerkit/05-tehollisarvo.odotettu"}
```

Halpa yleismittari mittaa usein keskiarvon ja kertoo sen siniaallolle
pätevällä kertoimella. Kantti- tai kolmioaallolla tulos on silloin
väärä; "true RMS" -mittari laskee tehollisarvon oikeasti.

## Impedanssi kompleksilukuna

Siniaallolla kondensaattorin virta on $i = C\,\mathrm{d}u/\mathrm{d}t$,
eli derivaatta muuttaa sinin kosiniksi: virta on 90° jännitettä
edellä, ja sen suuruus kasvaa taajuuden mukana. Kelalla tilanne on
päinvastainen. Nämä amplitudin ja vaiheen muutokset käsitellään
kätevimmin kompleksiluvuilla. Kompleksiluku $z = a + jb$ (sähkötekniikassa
imaginaariyksikkö on $j$, koska $i$ on virta) voidaan esittää myös
napamuodossa $|z| e^{j\varphi}$: itseisarvo on amplitudi ja argumentti
vaihekulma. Jokaisella komponentilla on *impedanssi* $Z$, kompleksinen
resistanssi:

| Komponentti | Impedanssi | Pienillä taajuuksilla | Suurilla taajuuksilla |
|-------------|------------|------------------------|------------------------|
| vastus | $R$ | $R$ | $R$ |
| kondensaattori | $1/(j\omega C)$ | avoin piiri | oikosulku |
| kela | $j\omega L$ | oikosulku | avoin piiri |

Kun impedanssit on määritelty, kaikki luvun 3 menetelmät toimivat
sellaisenaan: jännitteenjako, solmujännitemenetelmä ja Thevenin.
Laskut vain tehdään kompleksiluvuilla, ja Pythonissa ne ovat
sisäänrakennettuja (`1j`, `abs`, `cmath.phase`). Taito
*Kompleksiluvut ja Fourier-analyysi* käsittelee osoittimet ja
kompleksiluvut perusteellisemmin.

## RC-alipäästösuodin

RC-alipäästö on jännitteenjakaja, jonka alaosa on kondensaattori.
Pienillä taajuuksilla kondensaattori on lähes avoin piiri ja koko
jännite pääsee läpi; suurilla taajuuksilla se oikosulkee lähdön.

![Luvun kolme piiriä vasemmalta oikealle: RC-alipäästö, moottorin
käämiä kuvaava RL-kuorma ja sarja-RLC-piiri. Solmunimet ovat samat kuin
netlisteissä.](kuvat/ac-piirit.png){width=100%}

Siirtofunktio on jakosuhde:

$$
H(f) = \frac{Z_C}{R + Z_C} = \frac{1}{1 + j 2\pi f R C} .
$$

Rajataajuudella $f_c = 1 / (2\pi R C)$ reaali- ja imaginaariosat ovat
yhtä suuret: vahvistus on $1/\sqrt{2}$ eli −3 dB, ja vaihe −45°.
Sen yläpuolella vahvistus putoaa 20 dB dekadia kohti.

```{.python tiedosto="esimerkit/05-alipaasto.py" osa="kompleksi"}
```

SPICEn AC-analyysi laskee piirin piensignaalivasteen taajuuden
funktiona. Lähteelle annetaan `AC 1` eli yksikköamplitudi, jolloin
solmun jännite on suoraan siirtofunktio. `ac dec 50 10 1Meg` laskee
50 pistettä dekadia kohti välillä 10 Hz...1 MHz. Funktiot `vdb()` ja
`vp()` antavat vahvistuksen desibeleinä ja vaiheen (asteina, kun
`set units=degrees`).

```{.spice tiedosto="esimerkit/05-alipaasto.cir"}
```

```{.tuloste tiedosto="esimerkit/05-alipaasto.odotettu"}
```

![RC-alipäästön Bode-kuvaaja ngspicen AC-analyysistä: vahvistus
desibeleinä ja vaihe logaritmisella taajuusakselilla. Pisteviiva on
rajataajuus 1,59 kHz.](kuvat/bode.png){width=80%}

Bode-kuvaajassa taajuus on logaritmisella asteikolla ja vahvistus
desibeleinä, jolloin RC-suotimen vaste on kaksi suoraa: tasainen
rajataajuuteen asti, sitten −20 dB/dekadi. Taito *Signaalit ja
järjestelmät* käsittelee taajuusvasteen ja suodattimet digitaalisesti;
sama ajattelu pätee molempiin.

## Teho vaihtovirtapiirissä

Kun kuormassa on kelaa tai kondensaattoria, virta ja jännite ovat eri
vaiheessa, eikä tehollisarvojen tulo $U_\text{eff} I_\text{eff}$ ole
kuorman todellinen teho. Se on *näennäisteho* $S$ (voltiampeeri, VA).
Kuormaan siirtyvä keskimääräinen teho, *pätöteho*, on

$$
P = U_\text{eff} I_\text{eff} \cos\varphi ,
$$

missä $\varphi$ on virran ja jännitteen vaihe-ero ja $\cos\varphi$
*tehokerroin*. Loput, *loisteho* $Q = S \sin\varphi$, heiluu kuorman
ja verkon välillä jakson aikana tekemättä työtä, mutta kuormittaa
johtimia ja muuntajia. Esimerkissä moottorin käämiä mallinnetaan
vastuksella ja kelalla. Piiri vain simuloidaan; verkkojännitteellä
työskentely vaatii sähköalan pätevyyden.

```{.spice tiedosto="esimerkit/05-loisteho.cir"}
```

```{.python tiedosto="esimerkit/05-loisteho.py" osa="teho"}
```

```{.tuloste tiedosto="esimerkit/05-loisteho.odotettu"}
```

![Saman simulaation aaltomuodot kahden jakson ajalta. Virta on 37°
jännitettä jäljessä. Hetkellinen teho on negatiivinen (varjostus)
niinä hetkinä, joina jännite ja virta ovat erimerkkiset: silloin kela
palauttaa energiaa verkkoon. Katkoviiva on tehon keskiarvo eli
pätöteho.](kuvat/teho-aallot.png){width=80%}

SPICE laskee hetkellisen tehon $p(t) = u(t)\,i(t)$ ja sen keskiarvon
(`meas ... AVG`) ajan yli, eikä tiedä mitään osoittimista. Tulos on
silti sama kuin kompleksiluvuilla laskettu, mikä näyttää, että
osoitinlaskenta on vain tehokas tapa laskea sinimuotoisten suureiden
keskiarvoja. Mittaus aloitetaan 100 ms:n kohdalta, koska kelan virran
alkutransientti vaimenee aikavakiolla $L/R$.

## Resonanssi

Kela ja kondensaattori yhdessä muodostavat resonanssipiirin. Kelan
impedanssi kasvaa taajuuden mukana ja kondensaattorin pienenee; ne
kumoavat toisensa resonanssitaajuudella

$$
f_0 = \frac{1}{2\pi \sqrt{LC}} .
$$

Sarja-RLC-piirissä impedanssi on resonanssissa pienimmillään, pelkkä
$R$, ja virta suurimmillaan. Resonanssin terävyyttä kuvaa
hyvyysluku $Q = \sqrt{L/C} / R$, ja −3 dB:n kaistanleveys on
$f_0 / Q$.

```{.spice tiedosto="esimerkit/05-resonanssi.cir"}
```

```{.python tiedosto="esimerkit/05-resonanssi.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/05-resonanssi.odotettu"}
```

![Vastuksen jännite taajuuden funktiona kolmella vastuksen arvolla.
Resonanssitaajuus pysyy samana, mutta pieni vastus (suuri Q) tekee
piikistä kapean. Esimerkin piiri on keskimmäinen
käyrä.](kuvat/resonanssi.png){width=80%}

Resonanssi tunnistetaan simuloinnista vaiheesta: vastuksen jännite on
samassa vaiheessa lähteen kanssa juuri resonanssissa (`vp(ulos)=0`).
Resonanssipiirit valitsevat radiokanavan, tuottavat kellosignaalin
kidevärähtelijässä ja suodattavat hakkuriteholähteen lähtöä. Ne myös
aiheuttavat ongelmia: jokainen johdin on pieni kela ja jokainen
liitos pieni kondensaattori, ja niiden ei-toivottu resonanssi näkyy
signaalin ylilyöntinä ja värähtelynä.

## Käytännössä

- Tarkista aina, onko jännite ilmoitettu huippu-, huipusta huippuun- vai
  tehollisarvona. Ero on siniaallolla $\sqrt{2}$ ja $2\sqrt{2}$.
- Laske impedanssit päässä ääritapauksina: pienillä taajuuksilla
  kondensaattori on katkos ja kela oikosulku, suurilla päinvastoin.
  Se kertoo suodattimen tyypin hetkessä.
- AC-analyysi on lineaarinen: se ei näe säröä, leikkautumista eikä
  komponenttien rajoja. Suurilla signaaleilla käytä
  transienttianalyysiä.
- Desibeli on suhde: $20 \log_{10}$ jännitteille, $10 \log_{10}$
  tehoille. −3 dB on puolet tehosta ja $1/\sqrt{2}$ jännitteestä.
- Suodattimen rajataajuus valitaan niin, että hyötysignaali on
  selvästi päästökaistalla ja häiriö estokaistalla. Yhden RC-asteen
  20 dB/dekadi on loiva; jyrkemmät suodattimet ovat jatkotaidon
  *Analogiaelektroniikka* aihe.

## Itsearviointi

- Osaat laskea siniaallon ja muiden aaltomuotojen tehollisarvon.
- Osaat laskea vastuksen, kondensaattorin ja kelan impedanssin ja
  käyttää niitä jännitteenjaossa kompleksiluvuilla.
- Osaat laskea RC-suotimen rajataajuuden, vahvistuksen ja vaiheen sekä
  lukea Bode-kuvaajaa.
- Osaat laskea pätö-, lois- ja näennäistehon sekä tehokertoimen.
- Osaat laskea sarjaresonanssipiirin resonanssitaajuuden, hyvyysluvun
  ja kaistanleveyden.
- Osaat ajaa ngspicen AC-analyysin ja mitata siitä rajataajuuden.

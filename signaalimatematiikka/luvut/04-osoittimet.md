# Sinimuotoiset signaalit ja osoittimet

Sinimuotoinen signaali on signaalinkäsittelyn perusrakennuspalikka.
Verkkojännite, puhdas ääni, radiolähettimen kantoaalto ja värähtelevä
jousi ovat kaikki muotoa

$$x(t) = A\cos(2\pi f t + \varphi),$$

missä $A > 0$ on **amplitudi**, $f$ **taajuus** hertseinä ja $\varphi$
**vaihe** radiaaneina. Signaalin **jakso** on $T = 1/f$ ja
**kulmataajuus** $\omega = 2\pi f$. Sini on sama aalto eri vaiheessa:
$\sin\theta = \cos(\theta - \pi/2)$, joten erillistä sinimuotoa ei
tarvita.

Tässä luvussa sinimuotoinen signaali esitetään **osoittimena**
(englanniksi *phasor*), yhtenä kompleksilukuna, joka pitää sisällään
amplitudin ja vaiheen. Osoittimilla saman taajuuden signaalien summat
lasketaan kompleksilukujen yhteenlaskuna, ja interferenssi ja huojunta
saavat yksinkertaisen selityksen.

## Pyörivä nuoli ja sen varjo

Eulerin kaavan mukaan $\cos\theta = \operatorname{Re} e^{i\theta}$. Siksi

$$A\cos(2\pi f t + \varphi) = \operatorname{Re}\big(A e^{i\varphi} e^{2\pi i f t}\big)
= \operatorname{Re}\big(X e^{2\pi i f t}\big), \qquad X = A e^{i\varphi}.$$

Kompleksiluku $X$ on signaalin **osoitin**. Sen itseisarvo on amplitudi
ja kulma vaihe. Tekijä $e^{2\pi i f t}$ on yksikköympyrää taajuudella $f$
vastapäivään kiertävä nuoli. Signaali on siis nuolen $X e^{2\pi i f t}$
varjo reaaliakselilla: nuoli pyörii, ja sen kärjen vaakakoordinaatti
piirtää kosinikäyrän. Osoitin on nuolen asento hetkellä $t = 0$.

Vaihe kertoo, kuinka paljon aalto on edellä tai jäljessä
vertailukosinista. Vaihe $\varphi$ vastaa aikasiirtoa $\varphi/(2\pi f)$:
aalto $\cos(2\pi f t + \varphi)$ saavuttaa huippunsa hetkellä
$t = -\varphi/(2\pi f)$, eli positiivinen vaihe tarkoittaa, että aalto
on edellä.

```{.python tiedosto="esimerkit/04-osoitin.py" osa="signaali"}
```

Kun taajuus tiedetään, kaikki saman taajuuden signaalit ovat
osoittimia. Osoittimen esitys pätee vain yhdelle taajuudelle; eri
taajuuksisia signaaleja ei voi yhdistää yhdeksi osoittimeksi. Tähän
palataan huojunnan yhteydessä.

## Saman taajuuden signaalien summa

Kun kaksi tai useampi saman taajuuden sinimuotoista signaalia lasketaan
yhteen, tulos on samaa taajuutta oleva sinimuotoinen signaali, jonka
osoitin on osoittimien summa:

$$\operatorname{Re}(X_1 e^{2\pi i f t}) + \operatorname{Re}(X_2 e^{2\pi i f t})
= \operatorname{Re}\big((X_1 + X_2) e^{2\pi i f t}\big).$$

Laskettavaksi jää kompleksilukujen summa. Ilman osoittimia sama tulos
vaatisi summakaavojen käyttöä ja termien järjestelyä. Esimerkki laskee
yhteen kosinin, sinin ja kolmannen aallon vaiheella $2.5$. Sini
$1.5\sin(2\pi f t)$ on osoitin $1.5e^{-i\pi/2} = -1.5i$.

```{.python tiedosto="esimerkit/04-osoitin.py" osa="summa"}
```

```{.tuloste tiedosto="esimerkit/04-osoitin.odotettu"}
```

![Esimerkin osoitin $X = 2\angle 60°$ kompleksitasossa, sen reaaliosa
ajan funktiona ja kolmen osoittimen summa nuoliketjuna. Summan
laskeminen on vektorien yhteenlaskua.](kuvat/osoitin.png){width=100%}

Summasignaalin huippuarvo näytteistä on hieman pienempi kuin osoittimen
itseisarvo, koska näytteet eivät osu täsmälleen huipun kohdalle.
Osoitin antaa tarkan amplitudin.

Sähkötekniikassa sama menetelmä tunnetaan **vaihtovirtalaskuna**:
jännitteet ja virrat ovat osoittimia, ja kondensaattori ja kela ovat
kompleksisia impedansseja. Yhtälön $u = L\,di/dt$ derivaatta muuttuu
kertolaskuksi $2\pi i f$:llä, koska
$\frac{d}{dt}e^{2\pi i f t} = 2\pi i f\, e^{2\pi i f t}$. Tämä on
kompleksisen eksponentin toinen suuri etu: **derivointi on
kertolasku**, joten lineaariset differentiaaliyhtälöt muuttuvat
osoittimille algebrallisiksi yhtälöiksi.

## Osoittimen mittaaminen näytteistä

Mitatusta signaalista osoitin saadaan **korrelaatiolla**: signaali
kerrotaan nuolella, joka pyörii vastakkaiseen suuntaan, ja tulos
keskiarvoistetaan. Jos $x(t) = \operatorname{Re}(X e^{2\pi i f t})
= \frac12\big(X e^{2\pi i f t} + \bar X e^{-2\pi i f t}\big)$, niin

$$x(t) e^{-2\pi i f t} = \tfrac12 X + \tfrac12 \bar X e^{-4\pi i f t}.$$

Ensimmäinen termi on vakio, ja jälkimmäinen pyörii kaksinkertaisella
taajuudella. Kokonaisten jaksojen yli laskettu keskiarvo kumoaa
pyörivän termin, joten $X = 2 \cdot \text{keskiarvo}\big(x(t)e^{-2\pi i f t}\big)$.
Samalla kumoutuvat muut taajuudet, kunhan nekin tekevät mittausaikana
kokonaisen määrän jaksoja.

```{.python tiedosto="esimerkit/04-mittaus.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/04-mittaus.odotettu"}
```

Mittaus löytää 250 ja 750 hertsin komponentit oikeilla amplitudeilla
ja vaiheilla (1 radiaani on 57.30 astetta ja $-0.4$ radiaania
$-22.92$ astetta) eikä löydä mitään 500 hertsistä. Tämä
korrelaatiomittaus on Fourier-analyysin ydin: luvussa 6 sama kaava
antaa Fourier-sarjan kertoimet ja luvussa 9 DFT:n. Lukitusvahvistin
(*lock-in amplifier*) ja radiovastaanottimen I/Q-ilmaisin tekevät
saman analogisesti.

## Interferenssi

Kun kaksi samantaajuista aaltoa kohtaa, niiden summan amplitudi riippuu
vaihe-erosta. Kahden yksikköamplitudisen aallon summan osoitin on
$1 + e^{i\delta}$, ja sen itseisarvo on

$$|1 + e^{i\delta}| = |e^{i\delta/2}|\,|e^{-i\delta/2} + e^{i\delta/2}|
= 2\,|\cos(\delta/2)|.$$

Samassa vaiheessa ($\delta = 0$) aallot vahvistavat toisiaan, ja
amplitudi kaksinkertaistuu; vastakkaisessa vaiheessa ($\delta = \pi$)
ne kumoavat toisensa. Esimerkki tulostaa myös summan tehon desibeleinä
suhteessa täyteen vahvistukseen. **Desibeli** (dB) on tehosuhteen
logaritmi, $10\log_{10}(P/P_0)$; amplitudisuhteelle kerroin on 20,
koska teho on verrannollinen amplitudin neliöön.

```{.python tiedosto="esimerkit/04-interferenssi.py" osa="interferenssi"}
```

Tietoliikennetekniikassa interferenssi on **monitie-etenemisen**
ongelma: suoraan ja heijastuneena saapuvat signaalit summautuvat, ja
jos niiden kulkuaikaero vastaa puolta jaksoa, signaali häipyy. Koska
vaihe-ero on $2\pi f\Delta t$, häipyminen riippuu taajuudesta. OFDM
jakaa siksi datan monelle kapealle alikantoaallolle, joista vain osa
häipyy kerrallaan. Melua vaimentavat kuulokkeet hyödyntävät samaa
ilmiötä tarkoituksella: ne tuottavat melun vastavaiheisena.

## Huojunta: eri taajuudet

Eri taajuisten aaltojen summa ei ole sinimuotoinen, mutta lähellä
toisiaan olevilla taajuuksilla se näyttää sinimuotoiselta aallolta,
jonka amplitudi vaihtelee hitaasti. Summakaavasta saadaan

$$\cos(2\pi f_1 t) + \cos(2\pi f_2 t)
= 2\cos\big(\pi (f_2 - f_1) t\big)\cos\big(2\pi \tfrac{f_1 + f_2}{2} t\big).$$

Osoitinkuvassa kaksi nuolta pyörii hieman eri nopeuksilla. Kun ne
osoittavat samaan suuntaan, summa on suuri, ja kun vastakkaisiin, pieni.
Suunnat vaihtuvat taajuuserolla $|f_2 - f_1|$, joten voimakkuus
vaihtelee sillä taajuudella. Tämä on **huojunta**, jonka kuulee, kun
kaksi lähes samaan säveleen viritettyä kieltä soi yhtä aikaa.
Soittimen virittäjä hyödyntää sitä: huojunta hidastuu ja katoaa, kun
taajuudet ovat samat.

```{.python tiedosto="esimerkit/04-interferenssi.py" osa="huojunta"}
```

```{.tuloste tiedosto="esimerkit/04-interferenssi.odotettu"}
```

![Esimerkin summa-aalto 0,6 sekunnin ajalta. Nopea värähtely (442 Hz)
näkyy täyttönä, ja sen amplitudi seuraa hidasta
verhokäyrää.](kuvat/huojunta.png){width=95%}

Huojunnan voi myös kuunnella. Seuraava ohjelma kirjoittaa saman
summan kolmen sekunnin äänitiedostoksi standardikirjaston
`wave`-moduulilla. Äänessä kuuluu yksi sävel, jonka voimakkuus
sykkii neljä kertaa sekunnissa.

```{.python tiedosto="esimerkit/04-aani.py" osa="wav"}
```

```{.tuloste tiedosto="esimerkit/04-aani.odotettu"}
```

Verhokäyrän $2|\cos(\pi \Delta f\, t)|$ jakso on $1/\Delta f$, koska
itseisarvo kaksinkertaistaa kosinin toistumisnopeuden. Kaavan
oikea puoli on **amplitudimoduloitu** aalto: hidas signaali kertoo
nopeaa kantoaaltoa. Luvussa 7 sama tulo nähdään taajuustasossa
modulaatio-ominaisuutena, joka siirtää spektriä.

## Käytännössä

- **Esitä saman taajuuden signaalit osoittimina.** Summat, vaihe-erot
  ja derivaatat ovat silloin kompleksilukujen yhteen- ja kertolaskuja.
- **Muista, että osoitin kuuluu yhdelle taajuudelle.** Eri taajuuksien
  summaa ei voi tiivistää yhteen osoittimeen; käsittele jokainen
  taajuus erikseen.
- **Mittaa osoitin korrelaatiolla kokonaisten jaksojen yli.** Kerro
  näytteet luvulla $e^{-2\pi i f t}$, ota keskiarvo ja kerro kahdella.
  Jos mittausaika ei ole jaksojen monikerta, tulos vääristyy (DFT:n
  vuotaminen, taito *Signaalit ja järjestelmät*).
- **Laske amplitudisuhteet desibeleinä kertoimella 20 ja tehosuhteet
  kertoimella 10.** Puolikas amplitudi on noin $-6$ dB ja puolikas teho
  noin $-3$ dB.

## Itsearviointi

- Osaat kirjoittaa signaalin $A\cos(2\pi ft + \varphi)$ osoittimena ja
  selittää, mitä osoittimen itseisarvo ja kulma tarkoittavat.
- Osaat laskea saman taajuuden sinimuotoisten signaalien summan
  osoittimilla ja tarkistaa sen numeerisesti.
- Osaat mitata osoittimen näytteistä korrelaatiolla ja perustella,
  miksi muut taajuudet kumoutuvat kokonaisten jaksojen yli.
- Osaat selittää interferenssin ja huojunnan osoitinkuvan avulla.

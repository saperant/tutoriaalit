# Kondensaattori ja kela

Vastus reagoi muutokseen heti. Kondensaattori ja kela varastoivat
energiaa, ja siksi niiden piireissä jännitteet ja virrat muuttuvat
ajassa. Tässä luvussa tarkastellaan niitä ajan funktiona: miten
kondensaattori latautuu, miksi digitaalinen signaali ei nouse
hetkessä ja mitä tapahtuu, kun kelan virta katkaistaan.

## Kondensaattori

Kondensaattori on kaksi johdetta, joiden välissä on eriste. Kun sen yli
on jännite $U$, se varastoi varauksen $Q = C U$, missä $C$ on
kapasitanssi (faradi, F). Käytännön arvot ovat pikofaradeista
millifaradeihin. Virta on varauksen muutosnopeus, joten

$$
i = C \frac{\mathrm{d}u}{\mathrm{d}t} .
$$

Tästä seuraa kondensaattorin tärkein ominaisuus: sen jännite ei voi
muuttua hyppäyksellisesti, koska se vaatisi äärettömän virran.
Kondensaattori vastustaa jännitteen muutosta, ja siksi sitä käytetään
käyttöjännitteen suodatukseen jokaisen piirin vieressä
(*ohituskondensaattori*, tyypillisesti 100 nF). Tasajännitteellä
latautunut kondensaattori ei päästä virtaa läpi: se on avoin piiri.
Energia on

$$
E = \tfrac12 C U^2 .
$$

Kondensaattorityyppi valitaan käyttötarkoituksen mukaan:

|Tyyppi|Tyypilliset arvot|Ominaisuudet|Käyttö|
|--------------------|----------------|----------------------------|------------------------|
| keraaminen (C0G) | 1 pF...10 nF | vakaa, tarkka, ei napaisuutta | ajoitus, suodattimet, värähtelijät |
| keraaminen (X7R) | 1 nF...10 µF | kapasitanssi pienenee jännitteen kasvaessa | ohituskondensaattorit |
| elektrolyytti | 1 µF...10 mF | napainen, suuri arvo, rajallinen ikä | teholähteiden suodatus |
| kalvo | 1 nF...10 µF | vakaa, kestää suuria jännitteitä | audio, verkkosuodattimet |

X7R-tyyppisen keraamisen kondensaattorin kapasitanssi voi pudota
nimellisjännitteellä alle puoleen: 10 µF:n osa 5 V:n jännitteellä on
käytännössä muutama mikrofaradi. Alumiinielektrolyyttikondensaattori on
napainen, ja väärin päin kytkettynä se voi rikkoutua rajusti.

## RC-piirin lataus

Kun jännitelähde $U$ kytketään vastuksen $R$ kautta tyhjään
kondensaattoriin, alussa koko jännite on vastuksen yli ja virta on
$U/R$. Kondensaattorin jännitteen kasvaessa vastuksen yli jää vähemmän,
ja lataus hidastuu.

![Luvun kaksi peruspiiriä: RC-piiri (vasemmalla) ja RL-piiri. Harmaat
solmunimet `sisaan`, `c` ja `l` ovat samat kuin
netlisteissä.](kuvat/rc-rl-piirit.png){width=72%}

Ratkaisu on eksponenttifunktio, jonka aikavakio on $\tau = RC$ (taito
*Differentiaaliyhtälöt ja Laplace-muunnos* johtaa sen piirin
differentiaaliyhtälöstä):

$$
u_C(t) = U \left(1 - e^{-t/\tau}\right).
$$

Yhden aikavakion jälkeen jännite on 63 % lopullisesta, kolmen jälkeen
95 % ja viiden jälkeen yli 99 %. Purkautuminen on peilikuva:
$u_C(t) = U_0 e^{-t/\tau}$.

```{.python tiedosto="esimerkit/04-rc.py" osa="kasin"}
```

SPICEn transienttianalyysi (`tran`) laskee piirin ajan funktiona.
`tran 5u 6m` tarkoittaa tulostusväliä 5 µs ja kestoa 6 ms; `uic`
(*use initial conditions*) käyttää kondensaattorin alkujännitettä
`IC=0` toimintapisteen laskemisen sijaan. Lähde on pulssi
`PULSE(alku loppu viive nousu lasku leveys jakso)`.
`meas`-komennot poimivat tuloksesta yksittäisiä arvoja: hetken, jolloin
jännite ohittaa tason (`WHEN`), tai arvon tiettynä hetkenä (`FIND ...
AT`).

```{.spice tiedosto="esimerkit/04-rc.cir"}
```

```{.tuloste tiedosto="esimerkit/04-rc.odotettu"}
```

![RC-piirin lataus: SPICEn tulos ja analyyttinen ratkaisu ovat
päällekkäin. Pystyviivat ovat yhden, kahden ja kolmen aikavakion
kohdalla.](kuvat/rc-lataus.png){width=80%}

## Kela

Kela on johdinkäämi, jonka magneettikenttä varastoi energiaa. Sen
induktanssi $L$ (henry, H) kertoo, kuinka suuren jännitteen virran
muutos aiheuttaa:

$$
u = L \frac{\mathrm{d}i}{\mathrm{d}t}, \qquad E = \tfrac12 L I^2 .
$$

Kela on kondensaattorin pari: sen *virta* ei voi muuttua
hyppäyksellisesti. Tasavirralla kela on oikosulku (vain käämilangan
resistanssi jää). RL-piirissä (edellisen kuvan oikea puoli) virta
kasvaa samalla eksponenttifunktiolla kuin RC-piirin jännite, ja
aikavakio on $\tau = L/R$:

```{.spice tiedosto="esimerkit/04-rl.cir"}
```

```{.python tiedosto="esimerkit/04-rl.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/04-rl.odotettu"}
```

Keloja on hakkuriteholähteissä, suodattimissa, releissä, moottoreissa
ja kaiuttimissa. Luvussa 7 nähdään, mitä tapahtuu, kun kelan virta
katkaistaan äkillisesti: koska virta ei voi muuttua hetkessä, kela
nostaa jännitettään niin paljon kuin tarvitaan virran ylläpitämiseksi.

## RC-viive digitaalisissa signaaleissa

Jokaisessa johtimessa ja tulossa on kapasitanssia, ja jokaisessa
lähdössä on resistanssia. Siksi digitaalinen signaali on todellisuudessa
RC-latautumista, ja sen nousuaika rajoittaa nopeutta. Selvin esimerkki
on I2C-väylä: avokollektorilähdöt vain vetävät linjaa alas, ja
vetovastus $R_p$ lataa väylän kapasitanssin $C_b$ takaisin ylös.

![I2C-väylän datalinja. Jokaisen laitteen lähtö on transistori, joka
voi vain vetää linjan maahan. Kun se päästää irti, vetovastus Rp lataa
johtimien ja tulojen yhteisen kapasitanssin Cb. Netlistissä transistoria
ei ole: simulointi alkaa hetkestä, jolloin linja
vapautuu.](kuvat/vetovastus.png){width=50%}

Väylän spesifikaatio mittaa nousuajan 30 %:sta 70 %:iin
käyttöjännitteestä:

```{.python tiedosto="esimerkit/04-nousuaika.py" osa="kasin"}
```

```{.spice tiedosto="esimerkit/04-nousuaika.cir"}
```

Netlistissä on kaksi uutta asiaa: `.param` määrittelee nimetyn arvon,
jota käytetään aaltosulkeissa (`{Rp}`), ja `.control`-lohkon `let`
laskee uuden vektorin mittauksista. Nousuajan raja määrää, kuinka
suuri vetovastus saa olla:

```{.python tiedosto="esimerkit/04-nousuaika.py" osa="mitoitus"}
```

```{.tuloste tiedosto="esimerkit/04-nousuaika.odotettu"}
```

![Simuloitu nousureuna kahdella vetovastuksella, kun väylän
kapasitanssi on 200 pF. Pisteet ovat 30 %:n ja 70 %:n tasojen
ohitushetket. Sallittu nousuaika on 1000 ns nopeudella 100 kbit/s ja
300 ns nopeudella 400 kbit/s.](kuvat/nousuaika.png){width=80%}

4,7 kΩ:n vetovastus toimii siis 100 kbit/s:n väylällä mutta ei
400 kbit/s:n nopeudella, kun väylän kapasitanssi on 200 pF; 1,5 kΩ:n
vastuksella nousuaika on 254 ns ja nopeampikin väylä toimii.
Pienempi vastus nopeuttaa nousua, mutta lähtötransistorin on silloin
kyettävä vetämään suurempi virta alas (I2C:ssä enintään 3 mA, mikä
rajaa vastuksen 3,3 V:n väylällä noin yhteen kilo-ohmiin). Taito
*Oheislaiteväylät* käsittelee väylän protokollan; tämä on sen
sähköinen pohja.

## Kosketinvärähtelyn poisto

Mekaaninen kosketin ei sulkeudu siististi: se pomppii millisekuntien
ajan, ja mikrokontrolleri näkee yhden painalluksen monena. Väre
voidaan poistaa ohjelmallisesti (luetaan tila uudelleen esimerkiksi
10 ms:n kuluttua) tai laitteistolla RC-suotimella ja Schmitt-liipaisimella.
Schmitt-liipaisimen tulossa on kaksi kynnystä: lähtö vaihtuu ylös
vasta ylemmän ja alas vasta alemman kynnyksen kohdalla. Tämä
*hystereesi* estää hitaasti muuttuvaa tai kohisevaa signaalia
värähtelemästä kynnyksen ympärillä.

![Painike, RC-suodin ja Schmitt-tulo. Netlistissä painike ja sen
vetovastus on korvattu jännitelähteellä `Vraaka`, jonka aaltomuoto
jäljittelee pomppivaa kosketinta.](kuvat/kosketin.png){width=62%}

```{.spice tiedosto="esimerkit/04-varahtely.cir"}
```

PWL-lähde (*piecewise linear*) kuvaa mielivaltaisen aaltomuodon
aika-arvo-pareina. Python lukee raa'an ja suodatetun aaltomuodon ja
laskee, kuinka monta tilamuutosta tavallinen ja Schmitt-tulo näkisi:

```{.python tiedosto="esimerkit/04-varahtely.py" osa="schmitt"}
```

```{.python tiedosto="esimerkit/04-varahtely.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/04-varahtely.odotettu"}
```

![Värähtelevä kosketin (harmaa) ja kaksi RC-suodinta. Katkoviivat ovat
Schmitt-liipaisimen kynnykset 1,0 V ja 2,3 V, pisteviiva tavallisen
tulon kynnys 1,65 V.](kuvat/varahtely.png){width=80%}

Pieni aikavakio (0,22 ms) ei yksin riitä: suodatettu jännite käy
kynnyksen molemmin puolin. Schmitt-tulo korjaa tämän. Suuri aikavakio
(1 ms) suodattaa pomppimisen yksinäänkin, mutta hidastaa reagointia ja
tuottaa hitaasti laskevan reunan, jollaista tavallinen CMOS-tulo ei
siedä (luku 7). Siksi hyvä ratkaisu on molemmat: kohtuullinen RC ja
Schmitt-tulo, joka monessa mikrokontrollerissa on valittavissa.
Ohjelmoitavassa logiikassa sama tehdään digitaalisesti näytteistämällä
tuloa ja vaatimalla, että se pysyy samana riittävän pitkään; sen
näyttävät taidot *RTL-suunnittelu SystemVerilogilla* ja
*FPGA-toteutus*.

## Käytännössä

- Aikavakio $\tau = RC$ tai $L/R$ on tärkein luku: 63 % yhdessä,
  99 % viidessä aikavakiossa. Sen arvioiminen päässä on hyödyllisempää
  kuin mikään kaava.
- Jokainen digitaalinen piiri tarvitsee ohituskondensaattorin (tyypillisesti
  100 nF) mahdollisimman lähelle käyttöjännitenastaa. Se syöttää
  kytkentävirtojen piikit, joita johdotus ei ehdi tuoda.
- Vetovastuksen arvo on kompromissi: suuri vastus säästää virtaa mutta
  hidastaa nousua ja altistaa häiriöille. Laske nousuaika väylän
  kapasitanssista.
- Hitaita reunoja ei saa syöttää tavalliseen logiikkatuloon. Käytä
  Schmitt-tuloa aina, kun signaali on suodatettu, tulee pitkältä
  johdolta tai mekaaniselta kytkimeltä.
- SPICEssä `IC=` ja `uic` antavat hallitut alkuarvot. Ilman niitä
  simulaattori laskee ensin tasajännitteisen toimintapisteen, jossa
  kondensaattorit ovat jo latautuneet.

## Itsearviointi

- Osaat selittää, miksi kondensaattorin jännite ja kelan virta eivät
  voi muuttua hyppäyksellisesti.
- Osaat laskea RC- ja RL-piirin aikavakion sekä jännitteen tai virran
  annettuna hetkenä.
- Osaat laskea signaalin nousuajan vetovastuksesta ja kapasitanssista ja
  mitoittaa vetovastuksen.
- Osaat selittää hystereesin merkityksen ja suunnitella yksinkertaisen
  värähtelyn poiston.
- Osaat ajaa transienttianalyysin ja käyttää `meas`-komentoja
  ajanhetkien ja arvojen mittaamiseen.

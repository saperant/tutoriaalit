# Kohina ja signaalin eheys

Kaikki edelliset luvut olettivat, että piirin ainoat signaalit ovat ne,
jotka sinne syötetään. Todellisuudessa jokainen vastus tuottaa kohinaa,
jokainen vahvistin lisää omansa, ja johtimet, maadoitus ja viereiset
digitaalisignaalit tuovat häiriöitä. Luvussa on kaksi osaa. Alkuosa
käsittelee kohinaa, joka syntyy komponenteissa itsessään ja asettaa
mittauksen tarkkuudelle perustavan rajan, jota ei voi ohittaa
vahvistamalla. Loppuosa käsittelee häiriöitä, jotka syntyvät
johtimissa: heijastuksia, maadoitusta ja käyttöjännitteen notkahduksia.

## Terminen kohina

Johteen elektronien lämpöliike tuottaa jännitekohinan, jonka
tehotiheys on tasainen kaikilla taajuuksilla (*valkoinen kohina*). Sen
tiheys on

$$
e_n = \sqrt{4 k T R}\ \ \mathrm{V}/\sqrt{\mathrm{Hz}},
$$

missä $k$ on Boltzmannin vakio ja $T$ absoluuttinen lämpötila. 1 kΩ:n
vastus tuottaa huoneenlämmössä noin 4 nV/√Hz. Kohinan tehollisarvo
kaistalla $B$ on $e_n\sqrt{B}$, joten kohinaa on sitä enemmän, mitä
leveämpi kaista on.

RC-alipäästö rajaa kaistan, ja sen *ekvivalentti kohinakaista* on
$\frac{\pi}{2} f_c = 1/(4RC)$. Kokonaiskohina on silloin
$\sqrt{4kTR / (4RC)} = \sqrt{kT/C}$: vastus supistuu pois. Suurempi
vastus tuottaa enemmän kohinaa, mutta kaventaa kaistaa samassa
suhteessa. Tämä *kT/C-kohina* on näytteenotto- ja pitopiirien
perustava raja: 1 pF:n kondensaattorissa se on 64 µV, mikä on
16-bittisessä 1 V:n muuntimessa jo neljä LSB:tä.

SPICEn `noise`-analyysi laskee jokaisen vastuksen ja puolijohteen
kohinan ja niiden yhteisvaikutuksen haluttuun solmuun:

```{.spice tiedosto="esimerkit/07-terminen.cir"}
```

```{.python tiedosto="esimerkit/07-terminen.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/07-terminen.odotettu"}
```

Simulointi vahvistaa molemmat: tiheys on $\sqrt{4kTR}$, ja kokonaiskohina
on sama 1 kΩ:n ja 100 kΩ:n vastuksella. Ngspicen oletuslämpötila on
27 °C, joten laskussa on käytetty 300,15 K.

## Kohinabudjetti

Vahvistimen kohina kuvataan datalehdessä tulon ekvivalenttisena
jännitekohinana $e_n$ (nV/√Hz) ja virtakohinana $i_n$ (pA/√Hz).
Virtakohina muuttuu jännitteeksi lähteen resistanssissa. Riippumattomat
kohinalähteet summautuvat neliöllisesti, joten suurin lähde
määrää kokonaisuuden:

```{.python tiedosto="esimerkit/07-kohinabudjetti.py" osa="budjetti"}
```

```{.tuloste tiedosto="esimerkit/07-kohinabudjetti.odotettu"}
```

Esimerkissä kolme lähdettä ovat samaa suuruusluokkaa. Jos lähteen
resistanssi olisi 100 Ω, vahvistimen jännitekohina hallitsisi, ja
kannattaisi valita pienikohinainen bipolaarivahvistin. Jos se olisi
1 MΩ, virtakohina hallitsisi, ja oikea valinta olisi FET-tuloinen
vahvistin, jonka virtakohina on femtoampeereja. Budjetti kertoo, mihin
kannattaa käyttää rahaa: kohinattomampi vahvistin ei auta, jos anturin oma
terminen kohina on suurin lähde. Silloin auttaa vain kapeampi kaista,
eli suodatus tai keskiarvoistus.

Matalilla taajuuksilla valkoisen kohinan päälle tulee
*1/f-kohina* (välkekohina), jonka tiheys kasvaa taajuuden laskiessa.
Datalehti antaa *kulmataajuuden*, jonka alapuolella 1/f-kohina hallitsee,
tyypillisesti 10 Hz ... 1 kHz. Tasajännitettä tai hitaita signaaleja
mittaavissa piireissä käytetään *chopper*- tai *auto-zero*-vahvistimia,
jotka siirtävät signaalin 1/f-alueen yläpuolelle.

![Vasemmalla vahvistimen kohinatiheyden tyypillinen muoto: valkoinen
taso (tässä 10 nV/√Hz) ja sen alapuolella kulmataajuudesta (100 Hz)
alkava 1/f-kohina. Käyrä on periaatekuva, ei simulaation tulos.
Oikealla esimerkin budjetti: kolme lähdettä summautuvat neliöllisesti,
joten summa on selvästi pienempi kuin osien
yhteenlaskettu arvo.](kuvat/kohina.png){width=92%}

## Heijastukset siirtolinjassa

Mittausketjun toisessa päässä on digitaalipiiri, ja sen nopeat reunat
ovat analoginen ilmiö: jännite ja virta etenevät johtimessa aaltona.
Sama johdotus, jossa väylän signaali heijastuu ja soi, kytkee häiriön
viereiseen anturijohtimeen ja AD-muuntimen referenssiin. Siksi luvun
loppuosa siirtyy komponenttien kohinasta johtimiin.

Kun signaalin nousuaika on lyhyt verrattuna aikaan, jossa se kulkee
johtimen päästä päähän, johdin ei ole enää pelkkä yhteys vaan
*siirtolinja*, jolla on ominaisimpedanssi $Z_0$ (piirilevyllä ja
koaksiaalikaapelissa tyypillisesti 50 Ω). Jos linjan pää ei ole
päätetty ominaisimpedanssilla, osa aallosta heijastuu takaisin
heijastuskertoimella

$$
\Gamma = \frac{Z - Z_0}{Z + Z_0}.
$$

Avoin pää heijastaa koko aallon samanmerkkisenä ($\Gamma = 1$),
oikosulku vastakkaismerkkisenä ($\Gamma = -1$), ja oikein päätetty linja
ei heijasta lainkaan. Heijastunut aalto heijastuu uudelleen lähteestä,
jos lähteen resistanssi poikkeaa $Z_0$:sta. Kuorman jännitteen voi
laskea askel kerrallaan:

![Päättämisen kaksi tapaa. Ylhäällä lähteen resistanssi on sovitettu
linjaan ja pää on auki; alhaalla linjan päässä on ominaisimpedanssin
suuruinen vastus.](kuvat/paatokset.png){width=74%}

```{.python tiedosto="esimerkit/07-heijastus.py" osa="heijastus"}
```

Ngspicen ideaalinen siirtolinja `T` saa parametreikseen ominaisimpedanssin
ja viiveen:

```{.spice tiedosto="esimerkit/07-heijastus.cir"}
```

```{.tuloste tiedosto="esimerkit/07-heijastus.odotettu"}
```

![Kuorman jännite 50 Ω:n linjan päässä. Sovitettu lähde (50 Ω)
antaa puhtaan askeleen avoimeen päähän; 10 Ω:n lähde ja avoin pää
soivat; päätetty linja on puhdas mutta jännite jää jaon mukaiseksi.](kuvat/heijastus.png){width=80%}

Kolme tapausta näyttävät päättämisen kaksi tapaa. *Sarjapäätös*
(lähteen resistanssi $Z_0$) antaa avoimeen päähän puhtaan askeleen,
koska pään heijastus kulkee takaisin ja vaimenee sovitetussa lähteessä.
Tätä käytetään pisteestä pisteeseen kulkevissa signaaleissa, kuten
kellolinjoissa ja SPI-väylässä. *Rinnakkaispäätös* (kuorma $Z_0$) ei
heijasta lainkaan, mutta kuluttaa tehoa ja jakaa jännitteen; sitä
käytetään esimerkiksi CAN- ja RS-485-väylien päissä ja nopeissa
differentiaalipareissa. Taidon *Oheislaiteväylät* CAN-väylän 120 Ω:n
päätevastukset ovat juuri tätä.

Nyrkkisääntö: johdinta on pidettävä siirtolinjana, kun sen viive on
yli kuudesosa signaalin nousuajasta. Piirilevyllä signaali kulkee noin
15 cm nanosekunnissa, joten 1 ns:n nousuajalla jo 3 cm:n johdin on
siirtolinja. Nykyaikaisten mikrokontrollerien nopeat GPIO-lähdöt
ylittävät tämän helposti, ja *nousunopeuden rajoitus* (slew rate
-asetus) on usein helpoin keino vähentää soimista ja häiriöpäästöjä.

## Maadoitus, ohituskondensaattorit ja häiriöt

Monet analogiapiirien ongelmat eivät näy piirikaaviossa, koska ne
syntyvät johtimista:

- *Maan jännitehäviöt.* Maajohtimessa on resistanssia ja induktanssia.
  Jos tehopiirin virta kulkee samaa maajohdinta pitkin kuin anturin
  signaali, häviö summautuu signaaliin. Ratkaisu on yhtenäinen maataso
  piirilevyllä ja virtojen kulkureittien suunnittelu: suuret virrat eivät
  saa kulkea herkkien piirien alta.
- *Ohituskondensaattorit.* Piirin käyttöjännitenasta virran on päästävä
  lyhyttä reittiä takaisin maahan. 100 nF:n kondensaattori jokaisen piirin
  käyttöjännitenastassa, mahdollisimman lähellä, antaa nopeille
  virtapiikeille paikallisen varaston. Ilman sitä syöttöjännitteeseen
  syntyy piikkejä, ja vahvistimet voivat värähdellä.
- *Kytkeytyminen.* Kapasitiivinen kytkeytyminen siirtää nopeita
  jännitemuutoksia viereisiin johtimiin, induktiivinen kytkeytyminen
  virtasilmukoista toisiin. Herkät signaalit pidetään erillään nopeista,
  silmukat pieninä ja differentiaaliset signaalit vierekkäin.
- *Suodatus ja suojaus.* Tulojen RC-suodin poistaa radiotaajuisia
  häiriöitä, jotka vahvistimen epälineaarisuus muuten tasasuuntaisi
  signaalin taajuudelle.

Ohituskondensaattorin vaikutuksen voi simuloida. Logiikkapiiri ottaa
100 mA:n virtapiikin 2 ns:n nousuajalla, ja syöttö tulee 20 nH:n
johtimen kautta, mikä vastaa parin senttimetrin johdinta ilman
maatasoa:

```{.spice tiedosto="esimerkit/07-ohitus.cir"}
```

```{.python tiedosto="esimerkit/07-ohitus.py" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/07-ohitus.odotettu"}
```

![Piirin käyttöjännite virtapiikin aikana. Ilman ohitusta jännite
notkahtaa voltin virran noustessa ja ylittää käyttöjännitteen virran
katketessa, koska johtimen induktanssi vastustaa virran muutosta
kumpaankin suuntaan.](kuvat/ohitus.png){width=80%}

Ilman ohitusta käyttöjännite notkahtaa voltin, mikä riittää kaatamaan
3,3 V:n logiikan. Ohituskondensaattorin kanssa notkahdus on 50 mV, ja
sen määrää nyt kondensaattorin oma induktanssi (ESL). Siksi
ohituskondensaattori sijoitetaan aivan piirin viereen ja kytketään
lyhyillä johtimilla suoraan maatasoon: jokainen millimetri lisää
induktanssia. Suuremmat virrat ja nopeammat reunat vaativat useita
rinnakkaisia kondensaattoreita, joiden yhteinen ESL on pienempi.

Nämä ovat sähkömagneettisen yhteensopivuuden (EMC) perusasioita.
SPICE-simulointi ei tavoita niitä, ellei johtimia mallinneta; siksi
piirilevyn suunnittelusäännöt ja valmistajien sovellusohjeet ovat
analogiasuunnittelijan tärkeimpiä lähteitä.

## Käytännössä

- Laske kohinabudjetti ennen vahvistimen valintaa: lähteen
  terminen kohina, vahvistimen $e_n$ ja $i_n$ lähteen resistanssissa ja
  kaistanleveys. Rajaa kaista suodattimella heti alussa.
- Simuloi kohina SPICEn `noise`-analyysillä, kun piirissä on useita
  lähteitä. Valmistajien vahvistinmallit sisältävät kohinan; tämän
  tutoriaalin makromalli ei.
- Päätä nopeat signaalit: sarjapäätös pisteestä pisteeseen,
  rinnakkaispäätös väylissä. Käytä mikrokontrollerin hitainta riittävää
  lähtönopeutta.
- Suunnittele maadoitus ja ohituskondensaattorit ennen johdotusta.
  Ne korjataan jälkikäteen kalliisti.
- Mittaa prototyypistä kohina oskilloskoopilla ja spektrianalysaattorilla
  ja vertaa budjettiin. Ero kertoo kytkeytyvästä häiriöstä.

## Itsearviointi

- Osaat laskea vastuksen termisen kohinan ja RC-piirin kT/C-kohinan ja
  todentaa ne SPICEn kohina-analyysillä.
- Osaat laatia vahvistimen kohinabudjetin ja valita vahvistintyypin
  lähteen resistanssin perusteella.
- Osaat laskea heijastuskertoimen ja kuorman jännitteen siirtolinjassa
  ja valita sarja- tai rinnakkaispäätöksen.
- Osaat arvioida, milloin johdin on käsiteltävä siirtolinjana.
- Osaat selittää maadoituksen, ohituskondensaattoreiden ja
  kytkeytymisen merkityksen ja niiden tavalliset ratkaisut.

# Transistorit kytkiminä

Transistori on elektroninen venttiili: pieni ohjausvirta tai -jännite
säätää suurta virtaa. Vahvistimissa virtaa säädetään portaattomasti
(jatkotaito *Analogiaelektroniikka*); tässä luvussa transistori on
kytkin, joka joko johtaa täysin tai ei johda lainkaan. Näin
mikrokontrollerin pinni, joka antaa muutaman milliampeerin, ohjaa
releitä, moottoreita ja LED-nauhoja. Luku etenee kytkimen
mitoituksesta sen lämpenemiseen ja induktiivisen kuorman
jännitepiikkiin. Lopuksi kaksi transistoria muodostaa CMOS-invertterin,
kaiken digitaalilogiikan perusrakenteen, ja sen siirtokäyrästä luetaan
logiikkatasot.

## Bipolaaritransistori

NPN-bipolaaritransistorissa (BJT) on kolme liitäntää: kanta (B),
kollektori (C) ja emitteri (E). Kun kanta–emitteriliitos johtaa
(noin 0,6...0,7 V), kollektorivirta on kantavirran $h_{FE}$-kertainen;
$h_{FE}$ (tai $\beta$) on tyypillisesti 100...300 mutta vaihtelee
yksilöittäin ja lämpötilan mukaan.

Kytkimenä transistori ajetaan *kyllästykseen*: kantavirtaa syötetään
selvästi enemmän kuin kuorman virta vaatisi. Silloin kollektorivirtaa
rajoittaa kuorma eikä transistori, ja kollektori–emitterijännite on
pieni, noin 0,1...0,3 V. Mitoituksessa käytetään *pakotettua
vahvistusta*, joka on selvästi pienin taattu $h_{FE}$, tyypillisesti
10...20:

```{.python tiedosto="esimerkit/07-bjt.py" osa="mitoitus"}
```

![NPN-transistori kytkimenä: mikrokontrollerin 3,3 V:n lähtö ohjaa
12 V:n kuormaa kantavastuksen kautta.](kuvat/bjt-kytkin.png){width=40%}

Transistorimallit ovat tiedostossa `transistorit.lib`. Netlistissä
transistorin rivi on `Qnimi kollektori kanta emitteri malli`:

```{.spice tiedosto="esimerkit/07-bjt.cir"}
```

```{.python tiedosto="esimerkit/07-bjt.py" osa="teho"}
```

```{.tuloste tiedosto="esimerkit/07-bjt.odotettu"}
```

Kantavastukseksi valittiin seuraava *pienempi* E12-arvo, jolloin
kantavirta on hieman suurempi ja kyllästys varmistuu. Transistorissa
kuluu vain noin 21 mW, koska jännite sen yli on pieni. Jos kantavirta
olisi liian pieni, transistori jäisi aktiiviselle alueelle, jännite
sen yli nousisi voltteihin ja häviö satoihin milliwatteihin.

## MOSFET

MOSFET-transistoria ohjataan jännitteellä: hila (G) on eristetty
kanavasta, eikä sen läpi kulje tasavirtaa. Kun hila–lähdejännite
$U_{GS}$ ylittää kynnysjännitteen $U_{GS(th)}$, nielun (D) ja lähteen
(S) välille syntyy johtava kanava.

![N-kanavainen MOSFET alapuolen kytkimenä: kuorma on käyttöjännitteen
ja nielun välissä, ja lähde on maassa.](kuvat/mosfet-kytkin.png){width=34%}

MOSFETilla on kaksi johtavaa toiminta-aluetta. Kun nielu–lähdejännite
$U_{DS}$ on pieni, kanava käyttäytyy kuin vastus, jonka arvoa
hilajännite säätää: tämä on **vastusalue** (myös *triodialue* tai
*lineaarinen alue*). Kun $U_{DS}$ kasvaa yli ylijännitteen
$U_{GS} - U_{GS(th)}$, virta lakkaa kasvamasta ja riippuu enää
hilajännitteestä: tämä on **kyllästysalue**. Yksinkertaisimmassa
mallissa (Shichman–Hodges, SPICEn taso 1) virta on vastusalueella

$$
I_D = K \left( (U_{GS} - U_{GS(th)})\, U_{DS} - \tfrac12 U_{DS}^2 \right),
\qquad U_{DS} < U_{GS} - U_{GS(th)},
$$

ja kyllästysalueella $I_D = \tfrac12 K (U_{GS} - U_{GS(th)})^2$.
Kytkimenä MOSFETin halutaan olevan vastusalueella: pienellä
$U_{DS}$:llä se on vastus $R_{DS(on)} \approx 1 / (K (U_{GS} -
U_{GS(th)}))$, joka pienenee, kun hilajännite kasvaa.

Nimissä on ansa. MOSFETin kyllästysalue on se alue, jossa transistori
*rajoittaa* virtaa ja jännite sen yli on suuri. Bipolaaritransistorin
kyllästys tarkoittaa päinvastaista: transistori johtaa täysin ja
jännite sen yli on pieni. Kytkimeksi halutaan siis kyllästynyt
bipolaaritransistori mutta vastusalueella oleva MOSFET.

```{.spice tiedosto="esimerkit/07-mosfet.cir"}
```

Python laskee toimintapisteen samasta mallista puolitushaulla:
kuorman ja transistorin virtojen on oltava samat.

```{.python tiedosto="esimerkit/07-mosfet.py" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/07-mosfet.odotettu"}
```

![Transistorin ominaiskäyrät kolmella hilajännitteellä ja kuorman
kuormasuora. Toimintapiste on käyrän ja suoran leikkauspiste. 2 V:n
hilajännitteellä se on kyllästysalueella keskellä suoraa, ja
varjostettu ala $U_{DS} I_D$ on transistorin häviöteho. Suuremmilla
hilajännitteillä piste on vastusalueella aivan vasemmassa
yläkulmassa.](kuvat/mosfet-kayrat.png){width=80%}

Tulos näyttää, miksi hilajännitteellä on väliä. 2 V:n hilajännitteellä
transistori on kyllästysalueella, rajoittaa virran 0,85 A:iin ja
kuluttaa lähes 6 W. 3,3 V:lla häviö on 0,24 W ja 5 V:lla puolet siitä.
Siksi mikrokontrollerin suoraan ohjaamaksi MOSFETiksi valitaan
*logiikkatason* MOSFET, jonka $R_{DS(on)}$ on taattu jo 2,5 tai
4,5 V:n hilajännitteellä. Datalehden kynnysjännite $U_{GS(th)}$
(esimerkiksi 1...2 V) tarkoittaa vain sitä, että virta alkaa kulkea;
täysin johtava transistori on vasta paljon suuremmalla jännitteellä.

| Ominaisuus | BJT | MOSFET |
|------------------|------------------------------|----------------------------------|
| ohjaus | kantavirta | hilajännite |
| johtavana | $U_{CE(sat)}$ 0,1...0,3 V | $R_{DS(on)}$ milliohmeista ohmeihin |
| täysin johtavan tilan nimi | kyllästys | vastusalue (triodialue) |
| virtaa rajoittavan tilan nimi | aktiivinen alue | kyllästysalue |
| suurilla virroilla | häviö $\approx U_{CE} I$ | häviö $I^2 R_{DS(on)}$ |
| ohjauksen kulutus | jatkuva kantavirta | vain hilan latausvirta |

## Häviöteho ja lämpö

Häviöteho muuttuu transistorin liitoksessa lämmöksi, joka johtuu
kotelon kautta ympäristöön. Lämmön kulkua kuvaa *lämpöresistanssi*
$R_\theta$ (K/W), ja lasku on samaa muotoa kuin Ohmin laki: teho
vastaa virtaa ja lämpötilaero jännitettä. Liitoksen lämpötila on

$$
T_j = T_a + P\,R_{\theta JA} ,
$$

missä $T_a$ on ympäristön lämpötila ja $R_{\theta JA}$ lämpöresistanssi
liitoksesta ympäristöön (*junction to ambient*). Datalehti antaa sen
kotelolle ja suurimman sallitun liitoslämpötilan, piillä tyypillisesti
150 °C. Lasketaan edellisen esimerkin häviöt kahdessa kotelossa:

```{.python tiedosto="esimerkit/07-lampo.py" osa="lampo"}
```

```{.tuloste tiedosto="esimerkit/07-lampo.odotettu"}
```

Pieni SOT-23-pintaliitoskotelo kestää noin 0,4 W, joten se riittää
vain, kun hilajännite on vähintään 3,3 V. 2 V:n hilajännitteellä
transistori tuhoutuisi kummassakin kotelossa; 5,87 W vaatisi
jäähdytyslevyn, jonka kanssa lämpöresistanssi on alle 18,7 K/W.
Ympäristön lämpötilaksi on valittu 40 °C, koska laitekotelon sisällä
on lämpimämpää kuin huoneessa. Sama lasku tehdään jokaiselle
komponentille, jossa kuluu yli kymmeniä milliwatteja: vastuksille,
säätimille (luvun 6 lineaarisäädin) ja diodeille.

## Yläpuolen kytkin

Tähän asti kytkin on ollut kuorman ja maan välissä (*alapuolen
kytkin*). Joskus kuorman toisen pään on oltava maassa, esimerkiksi
kun kuorma on kiinni laitteen rungossa tai kun katkaistaan anturin
käyttöjännite. Silloin kytkin on käyttöjännitteen ja kuorman välissä
(*yläpuolen kytkin*), ja N-kanavainen MOSFET ei toimi sellaisenaan:
sen lähde on nyt kuorman päällä, ja kun kuorman jännite nousee,
$U_{GS}$ pienenee. Lähde jää ylijännitteen ja kynnysjännitteen verran
hilan alapuolelle, ja transistori jää kyllästysalueelle.

Ratkaisu on P-kanavainen MOSFET, jonka lähde kytketään
käyttöjännitteeseen. Se johtaa, kun hila vedetään *alas* lähteeseen
nähden. Hilan on kuitenkin noustava käyttöjännitteeseen asti, jotta
transistori sulkeutuu, eikä 3,3 V:n pinni yllä 12 V:iin. Siksi väliin
tarvitaan tasonsiirto: pieni NPN-transistori vetää hilan maahan, ja
vetovastus nostaa sen käyttöjännitteeseen.

![Yläpuolen kytkin kahdella tavalla. Vasemmalla N-kanava, jonka lähde
seuraa hilaa; oikealla P-kanava ja ohjaintransistori
Q1.](kuvat/ylapuoli.png){width=88%}

```{.spice tiedosto="esimerkit/07-ylapuoli.cir"}
```

```{.python tiedosto="esimerkit/07-ylapuoli.py" osa="seuraaja"}
```

```{.tuloste tiedosto="esimerkit/07-ylapuoli.odotettu"}
```

N-kanavalla kuorma saa 1,5 V ja transistori kuluttaa 2,6 W. P-kanava
antaa kuormalle käytännössä koko 12 V:n. Suurilla virroilla
N-kanavaista MOSFETia käytetään silti myös yläpuolella, koska sen
$R_{DS(on)}$ on pienempi; silloin erillinen hilaohjainpiiri tuottaa
hilalle käyttöjännitettä suuremman jännitteen. Moottorien H-silloissa
ja hakkureissa on juuri tällainen rakenne.

## Induktiivinen kuorma ja vapaakäyntidiodi

Releen käämi, moottori ja solenoidi ovat keloja. Luvusta 4 tiedetään,
että kelan virta ei voi muuttua hetkessä. Kun transistori katkaisee
virran, kela nostaa jännitettään niin paljon kuin tarvitaan virran
ylläpitämiseksi, ja energia $\tfrac12 L I^2$ purkautuu jonnekin.
Ilman reittiä se purkautuu käämin omaan pieneen kapasitanssiin ja
tuottaa kilovolttien piikin, joka tuhoaa transistorin.
*Vapaakäyntidiodi* rinnan käämin kanssa antaa virralle reitin: virta
kiertää käämin ja diodin kautta ja vaimenee aikavakiolla $L / R$.

![Releen käämi (induktanssi ja langan resistanssi), kytkin ja
vapaakäyntidiodi D1. Diodin katodi on käyttöjännitteessä, joten se ei
johda, kun kytkin on kiinni. Netlistissä on lisäksi käämin oma
kapasitanssi 100 pF käämin rinnalla.](kuvat/vapaakaynti-kaavio.png){width=42%}

```{.spice tiedosto="esimerkit/07-vapaakaynti.cir"}
```

```{.python tiedosto="esimerkit/07-vapaakaynti.py" osa="ilman"}
```

```{.python tiedosto="esimerkit/07-vapaakaynti.py" osa="kanssa"}
```

```{.tuloste tiedosto="esimerkit/07-vapaakaynti.odotettu"}
```

![Simuloidut aaltomuodot katkaisun jälkeen. Ilman diodia (vasen sarake,
aika mikrosekunteina) nielun jännite käy 3,8 kilovoltissa, kun käämin
virta purkautuu sen omaan kapasitanssiin. Diodin kanssa (oikea sarake,
aika millisekunteina) jännite nousee vain hieman yli 12 V:n, ja virta
vaimenee rauhallisesti.](kuvat/vapaakaynti.png){width=92%}

Energiaperiaate ennustaa piikin tarkasti: $\tfrac12 L I^2 = \tfrac12 C
U^2$. Todellinen transistori ei kestäisi kilovoltteja, vaan se lyö läpi
jo kymmenissä tai sadoissa volteissa ja voi tuhoutua. Diodin kanssa
nielun jännite nousee vain käyttöjännitteen ja diodin kynnysjännitteen
summaan. Virta vaimenee hieman aikavakiota
nopeammin, koska diodin jännite lisää jarrutusta. Hinta on se, että
rele päästää hitaammin. Jos se haittaa, diodin kanssa sarjaan
lisätään zener-diodi, joka nopeuttaa vaimenemista mutta sallii
suuremman jännitteen.

## Pulssinleveysmodulaatio

Kytkimenä toimiva transistori voi myös säätää tehoa. Kun kytkin
avataan ja suljetaan nopeasti, kuorman keskimääräinen jännite on
käyttöjännite kertaa *pulssisuhde* (*duty cycle*), eli se osuus
jaksosta, jonka kytkin johtaa. Tämä on pulssinleveysmodulaatio (PWM).
Mikrokontrollerin ajastin tuottaa PWM-signaalin laitteistolla, ja
samalla periaatteella säädetään LEDin kirkkautta, moottorin nopeutta
ja hakkuriteholähteen lähtöjännitettä. PWM-signaalin tuottamisen
logiikalla näyttää taito *RTL-suunnittelu SystemVerilogilla*.

```{.ajoituskaavio otsikko="PWM: sama jakso, pulssisuhteet 25 % ja 75 %. Kuorman keskimääräinen jännite on käyttöjännite kertaa pulssisuhde."}
{"signal": [
  {"name": "25 %", "wave": "hlllhlllhlllhlll"},
  {"name": "75 %", "wave": "hhhlhhhlhhhlhhhl"}
], "config": {"hscale": 0.8}}
```

PWM on tehokasta, koska transistori joko johtaa täysin (pieni
jännite) tai ei johda (ei virtaa), ja häviö on pieni molemmissa
tiloissa. Häviötä syntyy kuitenkin *kytkettäessä*: siirtymän aikana
sekä jännite että virta ovat suuria. Kytkentähäviö on likimain

$$
P_\text{kytkentä} \approx \tfrac12 U I (t_\text{nousu} + t_\text{lasku})
f_\text{PWM} ,
$$

joten se kasvaa kytkentätaajuuden mukana. Siksi hilaa ohjataan
nopeasti ja taajuus valitaan kompromissina: moottoreille tyypillisesti
yli 20 kHz (kuuloalueen yläpuolella), LEDeille vähintään satoja
hertsejä, jotta välkettä ei näe. Induktiivinen kuorma, kuten moottori,
tasoittaa virtaa luonnostaan, ja edellisen osion vapaakäyntidiodi
kantaa virran sen osan jaksosta, jonka kytkin ei johda.

## CMOS-invertteri

CMOS-logiikka rakentuu toisiaan täydentävistä transistoreista:
P-kanavainen MOSFET kytkee lähdön käyttöjännitteeseen ja N-kanavainen
maahan. Kun tulo on 0, P johtaa ja N ei, ja lähtö on 1. Kun tulo on 1,
tilanne kääntyy. Lepotilassa toinen transistori on aina pois päältä,
joten portti ei kuluta virtaa: se kuluttaa tehoa vain vaihtaessaan
tilaa, kun kuormakapasitanssi ladataan. Taito *Digitaalitekniikka*
käsittelee portit loogisina ja näyttää, miten samoista transistoreista
kootaan NAND-portti, kolmitilalähtö ja avoin nielu; tässä nähdään
yhden portin sähköinen puoli.

![CMOS-invertteri. Kummankin transistorin hila on tulossa ja nielu
lähdössä; kuormakapasitanssi kuvaa seuraavan portin tuloa ja
johdotusta.](kuvat/cmos-invertteri.png){width=46%}

```{.spice tiedosto="esimerkit/07-cmos.cir"}
```

Invertterin *siirtokäyrä* näyttää lähtöjännitteen tulojännitteen
funktiona. Kytkentäkynnys $U_M$ on kohta, jossa lähtö on yhtä suuri
kuin tulo. Siinä molemmat transistorit ovat kyllästysalueella ja
niiden virrat ovat yhtä suuret, mistä saadaan kaava:

```{.python tiedosto="esimerkit/07-cmos.py" osa="kynnys"}
```

```{.tuloste tiedosto="esimerkit/07-cmos.odotettu"}
```

![CMOS-invertterin siirtokäyrä kahdella P-transistorin leveydellä.
Kapeampi P-transistori siirtää kytkentäkynnystä alaspäin.](kuvat/cmos.png){width=55%}

Elektronien liikkuvuus on noin 2,5-kertainen aukkoihin nähden, joten
P-transistori tehdään vastaavasti leveämmäksi, jotta kynnys on
puolivälissä ja nousu- ja laskuviiveet ($t_{pLH}$, $t_{pHL}$) yhtä
suuret. Kapealla P-transistorilla nouseva lähtö on kaksi kertaa
hitaampi. Viive syntyy kuormakapasitanssin latauksesta transistorin
virralla, eli se on luvun 4 RC-ilmiö. Siksi portin viive kasvaa
kuorman mukana (taito *ASIC-toteutus* laskee samasta ilmiöstä
kokonaisen piirin ajoituksen), ja siksi siirtokäyrän keskiosa on
vaarallinen:
hitaasti muuttuvalla tulolla molemmat transistorit johtavat yhtä aikaa,
läpi kulkee virta, ja lähtö voi värähdellä. Tämä on syy luvun 4
Schmitt-tuloihin.

## Logiikkatasot ja kohinamarginaalit

Siirtokäyrästä näkee, mitä "nolla" ja "ykkönen" tarkoittavat
jännitteinä. Käyrän päissä portti *vaimentaa* tulon häiriöitä: tulon
pieni muutos ei näy lähdössä. Keskellä se *vahvistaa* niitä. Rajoiksi
on sovittu pisteet, joissa käyrän kulmakerroin on −1:

- $U_{IL}$: suurin tulojännite, joka tulkitaan varmasti nollaksi
- $U_{IH}$: pienin tulojännite, joka tulkitaan varmasti ykköseksi
- $U_{OH}$ ja $U_{OL}$: lähdön jännitteet ykkösenä ja nollana.

Kahden portin välissä johtimeen kytkeytyy häiriöitä. Portti sietää
niitä *kohinamarginaalin* verran: alhaalla $U_{IL} - U_{OL}$ ja
ylhäällä $U_{OH} - U_{IH}$. Esimerkki lukee rajat samasta simuloidusta
siirtokäyrästä:

```{.python tiedosto="esimerkit/07-tasot.py" osa="tasot"}
```

```{.python tiedosto="esimerkit/07-tasot.py" osa="marginaalit"}
```

![Siirtokäyrä, logiikkatasot ja kohinamarginaalit (varjostetut
alueet). Tasojen välinen alue on kielletty: siellä lähdön tila ei ole
määritelty.](kuvat/kohinamarginaalit.png){width=58%}

Valmistaja takaa tasot datalehdessä koko lämpötila-alueella ja
kuormitettuna, joten taatut arvot ovat varovaisempia kuin yhden portin
simuloidut. Taulukossa ovat tavallisimmat logiikkaperheet:

| Perhe | $U_{OH}$ väh. | $U_{OL}$ enint. | $U_{IH}$ väh. | $U_{IL}$ enint. |
|-------|------|------|------|------|
| 3,3 V CMOS | 2,4 V | 0,4 V | 2,0 V | 0,8 V |
| 5 V CMOS (74HC, 4,5 V:n syötöllä) | 4,4 V | 0,1 V | 3,15 V | 1,35 V |
| 5 V, TTL-tasoiset tulot (74HCT) | 4,4 V | 0,1 V | 2,0 V | 0,8 V |

Kun kaksi piiriä kytketään yhteen, ajavan piirin lähtötasojen on
mahduttava vastaanottavan piirin tulotasojen sisään. Tavallisin
kysymys on, kelpaako 3,3 V:n mikrokontrollerin lähtö 5 V:n piirin
tuloon:

```{.python tiedosto="esimerkit/07-tasot.py" osa="yhteensopivuus"}
```

```{.tuloste tiedosto="esimerkit/07-tasot.odotettu"}
```

3,3 V:n lähtö ei riitä 5 V:n CMOS-tulolle, joka vaatii ykköseksi
vähintään 3,15 V, mutta TTL-tasoiselle tulolle se kelpaa. Siksi
5 V:n ja 3,3 V:n järjestelmien väliin valitaan HCT-tyyppinen piiri tai
erillinen tasonmuunnin. Toiseen suuntaan tasot riittävät, mutta 5 V:n
lähtö ylittää 3,3 V:n piirin käyttöjännitteen: ellei tulo ole
*5 V:n sietoinen*, luvun 6 suojadiodit alkavat johtaa, ja väliin
tarvitaan jännitteenjako tai sarjavastus.

## Käytännössä

- Mitoita BJT-kytkimen kantavirta pakotetulla vahvistuksella 10...20.
  Liian pieni kantavirta jättää transistorin puoliksi johtavaksi, ja
  se kuumenee.
- Valitse mikrokontrollerin suoraan ohjaama MOSFET datalehden
  $R_{DS(on)}$-arvosta *sillä hilajännitteellä*, joka on käytössä. Älä
  luota kynnysjännitteeseen.
- Laita aina vapaakäyntidiodi induktiivisen kuorman rinnalle
  (katodi käyttöjännitteeseen). Moottoreissa ja H-silloissa MOSFETien
  omat sisäiset diodit hoitavat saman tehtävän.
- MOSFETin hila on kondensaattori. Nopea kytkentä vaatii hilaohjaimen,
  joka lataa sen suurella virralla; hitaassa kytkennässä transistori
  viettää pitkään kyllästysalueella, jossa sekä jännite että virta ovat
  suuria, ja kuumenee. Sarjavastus
  (10...100 Ω) mikrokontrollerin pinnin ja hilan välissä rajoittaa
  latausvirran piikkiä.
- Laske häviöstä liitoslämpötila $T_j = T_a + P R_{\theta JA}$ ja
  jätä marginaalia: lämpöresistanssi riippuu piirilevyn kuparista, ja
  kuuma puolijohde vanhenee nopeammin.
- Tarkista logiikkatasot datalehdistä aina, kun kytket yhteen eri
  käyttöjännitteillä toimivia piirejä.
- Varmista, että hila ei jää kellumaan käynnistyksen aikana:
  alasvetovastus (esimerkiksi 100 kΩ) hilalta maahan pitää
  transistorin pois päältä, kun mikrokontrollerin pinni on vielä
  tulotilassa.

## Itsearviointi

- Osaat mitoittaa bipolaaritransistorikytkimen kantavastuksen ja
  tarkistaa kyllästyksen simuloimalla.
- Osaat laskea MOSFETin jännite- ja tehohäviön ja selittää, miksi
  hilajännite ratkaisee.
- Osaat nimetä MOSFETin toiminta-alueet ja kertoa, miten ne eroavat
  bipolaaritransistorin kyllästyksestä.
- Osaat laskea liitoslämpötilan häviötehosta ja lämpöresistanssista.
- Osaat selittää, miksi yläpuolen kytkimeksi valitaan P-kanavainen
  MOSFET tai erillinen hilaohjain.
- Osaat selittää pulssinleveysmodulaation ja arvioida kytkentähäviön.
- Osaat selittää induktiivisen kuorman jännitepiikin energiaperiaatteella
  ja suojata kytkimen vapaakäyntidiodilla.
- Osaat selittää CMOS-invertterin toiminnan, laskea sen
  kytkentäkynnyksen ja kertoa, mistä viive syntyy.
- Osaat lukea siirtokäyrästä logiikkatasot ja kohinamarginaalit ja
  tarkistaa kahden logiikkaperheen yhteensopivuuden.
- Osaat käyttää transistorimalleja netlistissä ja lukea niiden
  sisäisiä suureita.

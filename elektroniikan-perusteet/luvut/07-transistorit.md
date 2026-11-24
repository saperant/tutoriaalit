# Transistorit kytkiminä

Transistori on elektroninen venttiili: pieni ohjausvirta tai -jännite
säätää suurta virtaa. Vahvistimissa transistoria käytetään sen
lineaarisella alueella (jatkotaito *Analogiaelektroniikka*); tässä
luvussa transistori on kytkin, joka on joko täysin auki tai täysin
kiinni. Näin mikrokontrollerin pinni, joka antaa muutaman
milliampeerin, ohjaa releitä, moottoreita ja LED-nauhoja.
Luvun lopussa kaksi transistoria muodostaa CMOS-invertterin, kaiken
digitaalilogiikan perusrakenteen.

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
$U_{GS}$ ylittää kynnysjännitteen $U_T$, nielun (D) ja lähteen (S)
välille syntyy johtava kanava. Kytkimenä MOSFET toimii lineaarisella
alueella, jossa se käyttäytyy kuin pieni vastus $R_{DS(on)}$.
Yksinkertaisimmassa mallissa (Shichman–Hodges, SPICEn taso 1) virta on

$$
I_D = K \left( (U_{GS} - U_T) U_{DS} - \tfrac12 U_{DS}^2 \right)
\quad \text{(lineaarinen alue, } U_{DS} < U_{GS} - U_T\text{)},
$$

ja kyllästysalueella $I_D = \tfrac12 K (U_{GS} - U_T)^2$. Pienellä
$U_{DS}$:llä vastus on noin $1 / (K (U_{GS} - U_T))$, joten se pienenee,
kun hilajännite kasvaa.

```{.spice tiedosto="esimerkit/07-mosfet.cir"}
```

Python laskee toimintapisteen samasta mallista puolitushaulla:
kuorman ja transistorin virtojen on oltava samat.

```{.python tiedosto="esimerkit/07-mosfet.py" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/07-mosfet.odotettu"}
```

Tulos näyttää, miksi hilajännitteellä on väliä. 2 V:n hilajännitteellä
transistori on kyllästysalueella, rajoittaa virtaa ja kuluttaa lähes
6 W: se tuhoutuisi ilman jäähdytystä. 3,3 V:lla häviö on 0,24 W ja
5 V:lla puolet siitä. Siksi mikrokontrollerin suoraan ohjaamaksi
MOSFETiksi valitaan *logiikkatason* MOSFET, jonka $R_{DS(on)}$ on
taattu jo 2,5 tai 4,5 V:n hilajännitteellä. Datalehden
"kynnysjännite" (esimerkiksi 1...2 V) tarkoittaa vain sitä, että virta
alkaa kulkea; täysin auki transistori on vasta paljon suuremmalla
jännitteellä.

| Ominaisuus | BJT | MOSFET |
|------------------|------------------------------|----------------------------------|
| ohjaus | kantavirta | hilajännite |
| johtavana | $U_{CE(sat)}$ 0,1...0,3 V | $R_{DS(on)}$ milliohmeista ohmeihin |
| suurilla virroilla | häviö $\approx U_{CE} I$ | häviö $I^2 R_{DS(on)}$ |
| ohjauksen kulutus | jatkuva kantavirta | vain hilan latausvirta |

## Pulssinleveysmodulaatio

Kytkimenä toimiva transistori voi myös säätää tehoa. Kun kytkin
avataan ja suljetaan nopeasti, kuorman keskimääräinen jännite on
käyttöjännite kertaa *pulssisuhde* (*duty cycle*), eli se osuus
jaksosta, jonka kytkin johtaa. Tämä on pulssinleveysmodulaatio (PWM).
Mikrokontrollerin ajastin tuottaa PWM-signaalin laitteistolla, ja
samalla periaatteella säädetään LEDin kirkkautta, moottorin nopeutta
ja hakkuriteholähteen lähtöjännitettä.

```{.ajoituskaavio otsikko="PWM: sama jakso, pulssisuhteet 25 % ja 75 %. Kuorman keskimääräinen jännite on käyttöjännite kertaa pulssisuhde."}
{"signal": [
  {"name": "25 %", "wave": "hlllhlllhlllhlll"},
  {"name": "75 %", "wave": "hhhlhhhlhhhlhhhl"}
], "config": {"hscale": 0.8}}
```

PWM on tehokasta, koska transistori on aina joko täysin auki (pieni
jännite) tai kiinni (pieni virta), ja häviö on pieni molemmissa
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
tasoittaa virtaa luonnostaan, ja vapaakäyntidiodi kantaa virran
kytkimen ollessa kiinni.

## Induktiivinen kuorma ja vapaakäyntidiodi

Releen käämi, moottori ja solenoidi ovat keloja. Luvusta 4 tiedetään,
että kelan virta ei voi muuttua hetkessä. Kun transistori katkaisee
virran, kela nostaa jännitettään niin paljon kuin tarvitaan virran
ylläpitämiseksi, ja energia $\tfrac12 L I^2$ purkautuu jonnekin.
Ilman reittiä se purkautuu käämin omaan pieneen kapasitanssiin ja
tuottaa kilovolttien piikin, joka tuhoaa transistorin.
*Vapaakäyntidiodi* rinnan käämin kanssa antaa virralle reitin: virta
kiertää käämin ja diodin kautta ja vaimenee aikavakiolla $L / R$.

```{.spice tiedosto="esimerkit/07-vapaakaynti.cir"}
```

```{.python tiedosto="esimerkit/07-vapaakaynti.py" osa="ilman"}
```

```{.python tiedosto="esimerkit/07-vapaakaynti.py" osa="kanssa"}
```

```{.tuloste tiedosto="esimerkit/07-vapaakaynti.odotettu"}
```

Energiaperiaate ennustaa piikin tarkasti: $\tfrac12 L I^2 = \tfrac12 C
U^2$. Diodin kanssa nielun jännite nousee vain käyttöjännitteen ja
diodin kynnysjännitteen summaan. Virta vaimenee hieman aikavakiota
nopeammin, koska diodin jännite lisää jarrutusta. Hinta on se, että
rele päästää hitaammin. Jos se haittaa, diodin kanssa sarjaan
lisätään zener-diodi, joka nopeuttaa vaimenemista mutta sallii
suuremman jännitteen.

## CMOS-invertteri

CMOS-logiikka rakentuu toisiaan täydentävistä transistoreista:
P-kanavainen MOSFET kytkee lähdön käyttöjännitteeseen ja N-kanavainen
maahan. Kun tulo on 0, P johtaa ja N ei, ja lähtö on 1. Kun tulo on 1,
tilanne kääntyy. Lepotilassa toinen transistori on aina pois päältä,
joten portti ei kuluta virtaa: se kuluttaa tehoa vain vaihtaessaan
tilaa, kun kuormakapasitanssi ladataan. Taito *Digitaalitekniikka*
käsittelee portit loogisina; tässä nähdään niiden sähköinen puoli.

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
kuorman mukana, ja siksi siirtokäyrän keskiosa on vaarallinen:
hitaasti muuttuvalla tulolla molemmat transistorit johtavat yhtä aikaa,
läpi kulkee virta, ja lähtö voi värähdellä. Tämä on syy luvun 4
Schmitt-tuloihin.

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
  viettää pitkään lineaarialueella ja kuumenee. Sarjavastus
  (10...100 ohm) mikrokontrollerin pinnin ja hilan välissä rajoittaa
  latausvirran piikkiä.
- Varmista, että hila ei jää kellumaan käynnistyksen aikana:
  alasvetovastus (esimerkiksi 100 kohm) hilalta maahan pitää
  transistorin pois päältä, kun mikrokontrollerin pinni on vielä
  tulotilassa.

## Itsearviointi

- Osaat mitoittaa bipolaaritransistorikytkimen kantavastuksen ja
  tarkistaa kyllästyksen simuloimalla.
- Osaat laskea MOSFETin jännite- ja tehohäviön ja selittää, miksi
  hilajännite ratkaisee.
- Osaat selittää pulssinleveysmodulaation ja arvioida kytkentähäviön.
- Osaat selittää induktiivisen kuorman jännitepiikin energiaperiaatteella
  ja suojata kytkimen vapaakäyntidiodilla.
- Osaat selittää CMOS-invertterin toiminnan, laskea sen
  kytkentäkynnyksen ja kertoa, mistä viive syntyy.
- Osaat käyttää transistorimalleja netlistissä ja lukea niiden
  sisäisiä suureita.

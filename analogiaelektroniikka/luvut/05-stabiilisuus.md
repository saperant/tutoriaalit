# Takaisinkytkentä ja stabiilisuus

Negatiivinen takaisinkytkentä tekee vahvistimesta tarkan, lineaarisen
ja riippumattoman aktiivisten komponenttien vaihtelusta. Sillä on
hintansa: jos takaisinkytketty signaali viivästyy niin paljon, että se
palaa vahvistimen tuloon samassa vaiheessa kuin alkuperäinen,
negatiivinen takaisinkytkentä muuttuu positiiviseksi, ja piiri alkaa
värähdellä. Tämä luku selvittää, miten stabiilisuus mitataan ja miksi
tavallinen syy epävakauteen on niinkin arkinen asia kuin kaapelin tai
kondensaattorin kapasitanssi lähdössä. Luvun lopussa positiivinen
takaisinkytkentä otetaan tarkoituksella käyttöön: vertailijassa se
tuottaa hystereesin.

## Silmukkavahvistus

Takaisinkytketyssä vahvistimessa signaali kiertää silmukan: vahvistimen
avoimen silmukan vahvistus $A(s)$ ja takaisinkytkentäverkon kerroin
$\beta$. Silmukkavahvistus on $T(s) = A(s)\beta$, ja suljetun silmukan
vahvistus on

$$
H(s) = \frac{A(s)}{1 + A(s)\beta} = \frac{1}{\beta}\cdot\frac{T(s)}{1 + T(s)}.
$$

```{.dot otsikko="Takaisinkytketty vahvistin lohkokaaviona. Silmukkavahvistus on A kertaa beta."}
digraph {
  rankdir=LR;
  tulo [shape=plaintext, style="", label="tulo"];
  summa [shape=circle, label="+\n−", width=0.5, fixedsize=true];
  A [label="A(s)\nvahvistin"];
  lahto [shape=plaintext, style="", label="lähtö"];
  beta [label="β\ntakaisinkytkentä"];
  tulo -> summa -> A -> lahto;
  A -> beta [constraint=false];
  beta -> summa;
}
```

Kun $|T| \gg 1$, $H \approx 1/\beta$: vahvistus riippuu vain
takaisinkytkennästä. Vaara on kohdassa, jossa $T(s) = -1$: nimittäjä on
nolla, ja piiri vahvistaa ilman tuloa eli värähtelee. Bode-kuvaajasta
asian voi lukea kahdella luvulla. *Vaihevara* on se, kuinka paljon
silmukkavahvistuksen vaihe on yli −180°:n taajuudella, jolla $|T| = 1$
(*ylitystaajuus*). *Vahvistusvara* on se, kuinka paljon $|T|$ on alle
1:n taajuudella, jolla vaihe on −180°. Hyvä suunnittelu tavoittelee
vähintään 45 ... 60 asteen vaihevaraa.

## Silmukkavahvistuksen mittaaminen

Silmukkavahvistuksen voi mitata simulaattorissa katkaisemalla silmukan
vain vaihtosignaalilta. Suuri kela takaisinkytkentäpolussa välittää
tasajännitteen, joten toimintapiste säilyy oikeana, mutta katkaisee
vaihtosignaalin. Suuri kondensaattori syöttää testisignaalin
invertoivaan tuloon. Silloin $T = -u_{ulos}/u_{tulo-}$.

![Luvun kaksi kytkentää. Vasemmalla silmukkavahvistuksen mittaus: kela
Lkatko sulkee silmukan tasajännitteelle, ja kondensaattori Ckatko tuo
testisignaalin lähteestä Vt. Oikealla osion *Kompensointi*
eristysvastus: takaisinkytkentä otetaan vahvistimen lähdöstä `o2`, ja
kuorma on vastuksen takana.](kuvat/silmukka.png){width=96%}

```{.spice tiedosto="esimerkit/05-silmukka.cir"}
```

Vahvistinmallissa on nyt toinen napa 30 MHz:ssä, kuten oikeissa
vahvistimissa, joissa sisäiset asteet tuovat lisää viivettä. Kuorma
kondensaattori $C_L$ muodostaa vahvistimen lähtöresistanssin kanssa
kolmannen navan taajuudelle $1/(2\pi R_{ulos} C_L)$. Python laskee saman
silmukkavahvistuksen napojen tulona ja hakee ylitystaajuuden:

```{.python tiedosto="esimerkit/05-silmukka.py" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/05-silmukka.odotettu"}
```

![Seuraajan silmukkavahvistus ja sen vaihe kolmella kuormalla.
Kuorman napa siirtää ylitystaajuutta alas ja vaihetta kohti −180°:ta.](kuvat/vaihevara.png){width=78%}

Ilman kuormaa vaihevara on 72°. Jo 1 nF:n kuorma, joka vastaa noin
kymmentä metriä koaksiaalikaapelia, pudottaa sen 22 asteeseen, ja
4,7 nF kymmeneen asteeseen. Vahvistin ei vielä värähtele, mutta se on
lähellä.

## Askelvaste kertoo saman

Pieni vaihevara näkyy aikatasossa ylityksenä ja soimisena.
Suljetun silmukan askelvasteen voi laskea suoraan siirtofunktiosta
$H = T/(1 + T)$:

```{.python tiedosto="esimerkit/05-askel.py" osa="malli"}
```

```{.spice tiedosto="esimerkit/05-askel.cir"}
```

```{.tuloste tiedosto="esimerkit/05-askel.odotettu"}
```

![Seuraajan askelvaste 1 nF:n kuormalla. Suoraan kytkettynä vaste
ylittää 54 % ja soi; eristysvastus vaimentaa soimisen.](kuvat/askel-kuorma.png){width=78%}

Ensimmäinen versio tästä esimerkistä käytti 100 mV:n askelta ja
oletusnousunopeutta. Simuloitu ylitys oli vain 19 %, kun malli ennusti
54 %. Syy: vahvistin oli nousunopeuden rajoittama, jolloin se ei ole
lineaarinen eikä siirtofunktio päde. Nousunopeus *peitti* epävakauden.
Pienellä askeleella sama piiri soi selvästi. Tästä on käytännön opetus:
stabiilisuus tarkistetaan pienellä signaalilla, koska suuri signaali voi
näyttää siistiltä juuri siksi, että vahvistin on kyllästynyt.

## Kompensointi

Kapasitiivisen kuorman ongelmaan on kolme tavallista ratkaisua:

- *Eristysvastus.* 20 ... 100 Ω:n vastus vahvistimen lähdön ja
  kuorman välissä, takaisinkytkentä vahvistimen lähdöstä. Vastus tuo
  silmukkaan nollan, joka kumoaa kuorman navan vaikutuksen. Haittana
  vastuksen yli syntyy jännitehäviö kuormavirralla, ja tarkkuus
  kärsii raskaalla resistiivisellä kuormalla.
- *Kaksoissilmukka.* Tasajännitteen takaisinkytkentä otetaan kuorman
  puolelta (tarkkuus), suurtaajuinen pienen kondensaattorin kautta
  vahvistimen lähdöltä (stabiilisuus).
- *Kuormalle sopiva vahvistin.* Osa vahvistimista on suunniteltu
  ohjaamaan rajattomia kapasitiivisia kuormia, ja datalehti kertoo
  sallitun kuorman. Myös suurempi vahvistus auttaa: pienempi $\beta$
  laskee ylitystaajuutta, ja kuorman napa jää sen yläpuolelle.

Sama analyysi koskee kaikkia takaisinkytkettyjä järjestelmiä:
jännitteensäätimiä, vaihelukittuja silmukoita ja ohjelmallisia
säätimiä. Lineaarisäädin on vahvistin, joka vertaa lähtöään
referenssiin ja ohjaa sarjatransistoria, ja sen kuorma on aina
kondensaattori. Siksi säätimen datalehti määrää lähtökondensaattorin
arvon ja sarjaresistanssin rajat: ne ovat juuri tämän luvun
vaihevaraehto valmiiksi laskettuna. Taidossa *Differentiaaliyhtälöt ja Laplace-muunnos* Routhin
ehto kertoi, onko järjestelmä stabiili; vaihevara kertoo, *kuinka*
stabiili, ja juuri se ratkaisee, soiko piiri.

## Positiivinen takaisinkytkentä: vertailija ja hystereesi

*Vertailija* (*comparator*) on vahvistin ilman negatiivista
takaisinkytkentää: sen lähtö on ylhäällä, kun plus-tulo on miinus-tuloa
suurempi, ja muuten alhaalla. Se muuttaa analogisen jännitteen
yhdeksi bitiksi, ja luvun 6 AD-muuntimet rakentuvat sen varaan.
Vertailijapiiri on tehty tähän: sen lähtö on logiikkatasoinen ja toipuu
ääriasennosta nanosekunneissa, toisin kuin operaatiovahvistimen.

Pelkällä vertailijalla on sama ongelma kuin taidon *Elektroniikan
perusteet ja SPICE* kosketinvärähtelyssä: kun tulo on lähellä kynnystä,
pienikin kohina heiluttaa lähtöä edestakaisin. Ratkaisu on
*hystereesi*, ja se tehdään positiivisella takaisinkytkennällä. Vastus
R2 tuo osan lähdöstä plus-tuloon, jolloin kynnys siirtyy aina poispäin
siitä suunnasta, josta tulo sen juuri ylitti.

![Vertailija, jonka kynnys riippuu lähdön tilasta (invertoiva
Schmitt-liipaisin). Plus-tulon jännite on referenssin ja lähdön
painotettu keskiarvo.](kuvat/vertailija-kaavio.png){width=52%}

Kynnykset saadaan solmun `p` jännitteenjaosta lähdön kummassakin
tilassa:

```{.python tiedosto="esimerkit/05-vertailija.py" osa="kynnykset"}
```

Netlistin vertailija on aliohjelma, jonka lähtö lasketaan tulojen
erotuksesta jyrkällä tanh-funktiolla. Tuloon syötetään hidas
kolmioaalto, ja mittaukset poimivat tulojännitteen niillä hetkillä,
joina lähtö vaihtuu:

```{.spice tiedosto="esimerkit/05-vertailija.cir"}
```

Toinen koe näyttää, mitä hystereesi tekee kohinalle. Tulo nousee
hitaasti kynnyksen ohi, ja sen päällä on ±60 mV kohinaa. Sama netlist
ajetaan kahdesti: takaisinkytkentävastuksella 1 GΩ (käytännössä ei
hystereesiä) ja 100 kΩ.

```{.python tiedosto="esimerkit/05-vertailija.py" osa="kohina"}
```

```{.tuloste tiedosto="esimerkit/05-vertailija.odotettu"}
```

![Vasemmalla simuloitu siirtokäyrä: lähtö vaihtuu alas tulon noustessa
1,8 V:n yli ja ylös vasta sen laskiessa 1,5 V:n alle. Oikealla kohiseva
tulo ja vertailijan lähtö (lähdöt on piirretty tulon yläpuolelle
pienennettyinä). Ilman hystereesiä lähtö vaihtuu 21 kertaa, 0,3 V:n
hystereesillä kerran.](kuvat/vertailija.png){width=96%}

Hystereesin leveys mitoitetaan kohinan mukaan: sen on oltava suurempi
kuin tulon kohinan huipusta huippuun -arvo, mutta ei suurempi kuin
on pakko, koska se siirtää vaihtohetkeä. Negatiivinen takaisinkytkentä
pitää vahvistimen lineaarisena, positiivinen tekee siitä kaksitilaisen:
sama silmukkavahvistus, vastakkainen etumerkki. Kun stabiilin
vahvistimen vaihevara loppuu, se muuttuu vahingossa juuri tällaiseksi
piiriksi.

## Käytännössä

- Tarkista stabiilisuus simuloimalla silmukkavahvistus tai askelvaste
  *pienellä* signaalilla ja todellisella kuormalla, mukaan lukien
  kaapelit ja ADC-tulojen kapasitanssi.
- Tavoittele 45 ... 60 asteen vaihevaraa. Alle 30 asteen vara näkyy
  selvänä soimisena, ja lämpötila tai komponenttien vaihtelu voi kaataa
  piirin värähtelyyn.
- Lue datalehdestä, kuinka suurta kapasitiivista kuormaa vahvistin
  sietää ja millä vahvistuksella. Seuraajakytkentä (vahvistus 1) on
  herkin.
- Ohjaa pitkiä kaapeleita ja AD-muuntimen näytteenottokondensaattoria
  eristysvastuksen kautta. ADC-tuloon tarvitaan yleensä RC-suodin
  joka tapauksessa (luku 6).
- Lisää vertailijaan hystereesi aina, kun tulo muuttuu hitaasti tai
  siinä on kohinaa. Monessa vertailijapiirissä ja mikrokontrollerin
  sisäisessä vertailijassa se on valmiina muutaman millivoltin
  suuruisena.
- Kun piiri värähtelee oikeasti mutta ei simulaattorissa, etsi
  kuorma- ja hajakapasitanssi, jota netlistissä ei ole.

## Itsearviointi

- Osaat selittää silmukkavahvistuksen, ylitystaajuuden, vaihevaran ja
  vahvistusvaran ja lukea ne Bode-kuvaajasta.
- Osaat mitata silmukkavahvistuksen simulaattorissa katkaisemalla silmukan
  vaihtosignaalilta.
- Osaat laskea kapasitiivisen kuorman tuottaman navan ja sen vaikutuksen
  vaihevaraan.
- Osaat yhdistää vaihevaran askelvasteen ylitykseen ja selittää, miksi
  stabiilisuus tarkistetaan pienellä signaalilla.
- Osaat valita kompensointikeinon kapasitiivisen kuorman ohjaamiseen.
- Osaat mitoittaa vertailijan hystereesin vastuksilla ja perustella sen
  leveyden tulon kohinasta.

# Takaisinkytkentä ja stabiilisuus

Negatiivinen takaisinkytkentä tekee vahvistimesta tarkan, lineaarisen
ja riippumattoman aktiivisten komponenttien vaihtelusta. Sillä on
hintansa: jos takaisinkytketty signaali viivästyy niin paljon, että se
palaa vahvistimen tuloon samassa vaiheessa kuin alkuperäinen,
negatiivinen takaisinkytkentä muuttuu positiiviseksi, ja piiri alkaa
värähdellä. Tämä luku selvittää, miten stabiilisuus mitataan ja miksi
tavallinen syy epävakauteen on niinkin arkinen asia kuin kaapelin tai
kondensaattorin kapasitanssi lähdössä.

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

- *Eristysvastus.* 20 ... 100 ohmin vastus vahvistimen lähdön ja
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
jännitteenvakaajia, vaihelukittuja silmukoita ja ohjelmallisia
säätimiä. Taidossa *Differentiaaliyhtälöt ja Laplace-muunnos* Routhin
ehto kertoi, onko järjestelmä stabiili; vaihevara kertoo, *kuinka*
stabiili, ja juuri se ratkaisee, soiko piiri.

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

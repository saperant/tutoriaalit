# IIR-rakenteet laitteistossa

IIR-suodin saa saman vaimennuksen murto-osalla FIR-suotimen kertojista,
koska se käyttää omia aiempia ulostulojaan. Laitteistossa
takaisinkytkentä on sekä vahvuus että ongelma: se on silmukka, jonka
on valmistuttava yhdessä näytejaksossa, ja virhe, joka pääsee
silmukkaan, kiertää siinä. Tässä luvussa toteutetaan toisen asteen
lohko, kytketään kaksi lohkoa kaskadiksi ja katsotaan, mitä
saturaatio ja pyöristys silmukassa tekevät.

## Toisen asteen lohko

Taito *Digitaalinen signaalinkäsittely* perusteli, miksi IIR-suotimet
toteutetaan toisen asteen lohkoina (SOS) ja miksi kiinteän pilkun
toteutukseen sopii suora muoto I (DF1). DF1 laskee kaikki viisi tuloa
yhteen leveään kertymään ja kaventaa vasta lopuksi. Sen tila on
pelkkiä näytteitä (kaksi sisääntuloa ja kaksi ulostuloa), joten tila
ei voi vuotaa yli, ja ainoa kavennus on ulostulossa.

```{.dot otsikko="Toisen asteen lohko suorassa muodossa I. Viisi tuloa summataan yhteen leveään kertymään, ja ainoa kavennus on ulostulossa. Takaisinkytkentä (punainen) kulkee kavennuksen kautta, joten kavennuksen virhe kiertää silmukassa."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.45;
  node [shape=box, height=0.3];
  x [label="x[n]", shape=plaintext];
  x1 [label="x[n−1]"]; x2 [label="x[n−2]"];
  y1 [label="y[n−1]"]; y2 [label="y[n−2]"];
  summa [label="Σ\n35 b.", shape=circle];
  kav [label="kavenna"];
  y [label="y[n]", shape=plaintext];
  x -> x1 -> x2;
  x -> summa [label="b0"];
  x1 -> summa [label="b1"];
  x2 -> summa [label="b2"];
  summa -> kav -> y;
  kav -> y1 [color="#B04848", constraint=false];
  y1 -> y2 [color="#B04848"];
  y1 -> summa [label="−a1", color="#B04848", fontcolor="#B04848"];
  y2 -> summa [label="−a2", color="#B04848", fontcolor="#B04848"];
}
```

Esimerkin suodin on neljännen asteen Butterworth-alipäästö
(`signal.butter(4, 0.1)`, rajataajuus 5 % näytetaajuudesta) kahtena
lohkona. Kertoimet ovat muotoa Q2.14, koska $|a_1|$ on lähes 2:

```{.python tiedosto="esimerkit/malli/kertoimet.py" osa="sos"}
```

SciPy sijoittaa koko vahvistuksen ensimmäiseen lohkoon, jolloin
ensimmäisen lohkon $b$-kertoimet olisivat pieniä (0,0004) ja toisen
lohkon $b_1 = 2$ ei mahtuisi muotoon Q2.14. Vahvistus jaetaan siksi
uudelleen niin, että kummankin lohkon tasavirtavahvistus on 1:

```{.python tiedosto="esimerkit/analyysit/suunnittelu.py" osa="sos"}
```

Tällöin kummankin lohkon ulostulo pysyy samalla tasolla kuin
sisääntulo, eikä kaskadin keskellä tarvita erillistä skaalausta.

Lohko on DF1-yhtälö RTL:nä:

```{.systemverilog tiedosto="esimerkit/rtl/biquad.sv" osa="biquad"}
```

Viisi tuloa johdetaan ensin omiin täysleveisiin johtoihinsa. Ilman
tätä välivaihetta lausekkeen `b0 * s_data` leveys määräytyisi
SystemVerilogin leveyssääntöjen mukaan, ja on helppo kirjoittaa
lauseke, jossa tulo katkeaa 16 bittiin ennen yhteenlaskua. Erilliset
johdot tekevät leveydet näkyviksi myös lukijalle.

Malli on sama yhtälö näyte kerrallaan:

```{.python tiedosto="esimerkit/malli/suotimet.py" osa="biquad"}
```

## Silmukkaa ei voi liukuhihnoittaa

FIR-suotimeen voi lisätä rekistereitä mihin tahansa: latenssi kasvaa,
mutta tulos ei muutu. IIR-lohkossa $y[n]$ tarvitsee arvon $y[n-1]$,
joka valmistui edellisellä jaksolla. Polku `y1` → kertoja → summain →
`kavenna` → `y1` on yhden jakson mittainen silmukka. Jos siihen
lisätään rekisteri, $y[n]$ käyttääkin arvoa $y[n-2]$, ja suodin on
toinen.

Silmukan viive rajoittaa siis suoraan näytetaajuutta. Luvun 10
synteesissä lohkon suurin kellotaajuus on noin 13 MHz, kun saman
piirin FIR-suotimet toimivat 23–36 MHz:llä. Keinoja on kolme:

- **Lyhyempi silmukka.** Silmukkaan kuuluvat vain takaisinkytkennän
  tulot $a_1 y[n-1]$ ja $a_2 y[n-2]$. Etenevät tulot $b_k x$
  voidaan laskea ja summata rekistereihin etukäteen, jolloin silmukassa
  on kaksi kertojaa ja kolme summainta viiden sijasta. Synteesi ei
  tee tätä itse, koska RTL määrää laskujärjestyksen.
- **Ennakointi** (*look-ahead*). Yhtälöön sijoitetaan
  $y[n-1]$:n lauseke, jolloin $y[n]$ riippuu arvosta $y[n-2]$ ja
  silmukkaan saa yhden rekisterin lisää. Hintana on lisää kertojia ja
  napa-nollakumoutumia, jotka ovat kiinteässä pilkussa herkkiä.
- **Lomitus** (*C-slow*). Jos samaa suodinta ajetaan $C$
  riippumattomalle kanavalle, silmukkaan voi lisätä $C - 1$
  rekisteriä ja kanavat kiertävät vuorotellen. Jokainen kanava näkee
  oman edellisen arvonsa, ja kellotaajuus kasvaa lähes $C$-kertaiseksi.

Monikanavaisessa radiossa tai äänikäsittelyssä lomitus on tavallisin
ratkaisu. Yksikanavaisessa suotimessa näytetaajuus on usein niin
paljon kellotaajuutta pienempi, että silmukalla on aikaa useita
kellojaksoja: silloin kertojan voi myös jakaa kuten luvussa 8.

## Kaskadi

Kaksi lohkoa kytketään virtaliitännällä peräkkäin. Toisen lohkon
`s_ready` on ensimmäisen `m_ready`, joten vastapaine kulkee ketjun
läpi taaksepäin:

```{.systemverilog tiedosto="esimerkit/rtl/sos.sv" osa="sos"}
```

Lohkojen järjestys ja skaalaus päätetään suunnittelussa. Tässä
pienemmän hyvyysluvun lohko on ensin, jolloin kapean resonanssin lohko
saa jo valmiiksi suodatetun signaalin. Kaskadi tarvitsee kymmenen
kertojaa, mikä on enemmän kuin UP5K-piirin kahdeksan DSP-lohkoa.
Luvussa 10 syntetisoidaan siksi yksi lohko.

## Ylivuoto silmukassa

Butterworth-suotimen askelvaste ylittää lopullisen tason noin 11 %.
Täyden asteikon askel vie siis ulostulon yli alueen, ja saturaatio
ratkaisee, mitä tapahtuu. Istutettu vika `BUGI_KIERTO` poistaa
saturaation `kavenna`-moduulista:

```text
make -C esimerkit cocotb-sos-kierto
```

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-sos-kierto.odotettu"}
```

![Testin askel mallilla laskettuna: vasemmalla oikea, saturoiva
kavennus, oikealla sama suodin ilman saturaatiota. Yksi kiertänyt arvo
näytteessä 14 riittää: sen jälkeen ulostulo ei palaa oikeaan arvoon,
vaikka sisääntulo pysyy vakiona.](kuvat/iir-askel.png){width=100%}

Näytteessä 14 oikea tulos on suurin arvo 32767, mutta kiertävä
toteutus antaa −31674: ylivuoto käänsi etumerkin. FIR-suotimessa
virhe jäisi yhteen näytteeseen. IIR-lohkossa väärä arvo menee
takaisinkytkentään, ja seuraavat ulostulot lasketaan sen varassa: 130
näytettä 144:stä on väärin. Pahimmillaan kiertävä takaisinkytkentä
jää värähtelemään täydellä amplitudilla (*overflow oscillation*),
vaikka sisääntulo olisi nolla.

Huomaa, että satunnainen testi meni läpi myös viallisella
toteutuksella. Tasajakautunut kohina ei saa suodinta ylivuotoon,
koska suodin vaimentaa sen. Saturaatio testataan vain sisääntulolla,
joka on suunniteltu viemään ulostulo rajalle (luku 9).

## Kuollut alue

Takaisinkytkentä pyöristää joka näytteellä. Kun sisääntulo on vakio,
ulostulo ei välttämättä asetu oikeaan arvoon, vaan jää kohtaan, jossa
pyöristys kumoaa jäljellä olevan eron. Mallin testi mittaa ilmiön:

```{.python tiedosto="esimerkit/testit/test_malli.py" osa="kuollut"}
```

Ensimmäisen lohkon napojen summa $1 + a_1 + a_2$ on vain 0,076, joten
puolen LSB:n pyöristysvirhe vahvistuu takaisinkytkennässä noin
13-kertaiseksi: askel 10000 asettuu arvoon 10005. Mitä lähempänä navat
ovat pistettä $z = 1$, eli mitä kapeampi suodin, sitä leveämpi
*kuollut alue* (*deadband*). Samasta syystä syntyvät rajasyklit, jotka
taito *Digitaalinen signaalinkäsittely* näytti.

![Ensimmäisen lohkon askelvaste tasolle 10000. Koko mittakaavassa vaste
näyttää asettuvan oikein; suurennos näyttää, että se jää pysyvästi
viisi LSB:tä tavoitteen yläpuolelle.](kuvat/iir-kuollut.png){width=100%}

Korjauksia on kaksi. Kertymään voi tallentaa pyöristyksessä
pudotetut bitit ja lisätä ne seuraavaan näytteeseen (*error
feedback*, virheen takaisinkytkentä), jolloin virhe ei kasaannu.
Yksinkertaisempi keino on pitää takaisinkytkennässä muutama
murtobitti enemmän kuin ulostulossa ja pyöristää vasta ulostuloon.
Molemmat maksavat summaimen tai rekisteribittejä, ja molemmat
näkyvät bittitarkassa mallissa ennen kuin RTL:ää on kirjoitettu.

## Käytännössä

- Toteuta IIR-suodin toisen asteen lohkoina DF1-muodossa: yksi leveä
  kertymä ja yksi kavennus lohkoa kohden.
- Jaa vahvistus lohkoille niin, että jokaisen lohkon ulostulo pysyy
  sisääntulon tasolla. Tarkista kertoimien muoto: $|a_1| < 2$
  vaatii kaksi kokonaisbittiä.
- Saturoi takaisinkytkentään menevä arvo aina. Kiertävä ylivuoto
  IIR-silmukassa on katastrofi, ei yhden näytteen virhe.
- Arvioi silmukan viive ennen kuin valitset rakenteen. Jos
  kellotaajuus ei riitä, lyhennä silmukkaa, lomita kanavia tai
  käytä näytejakson ylimääräiset kellojaksot kertojan jakamiseen.
- Mittaa kuollut alue mallilla ja lisää tarvittaessa murtobittejä
  takaisinkytkentään.

## Itsearviointi

- Osaat toteuttaa toisen asteen DF1-lohkon RTL:nä ja selittää, miksi
  muoto sopii kiinteälle pilkulle.
- Osaat perustella, miksi IIR-silmukkaa ei voi liukuhihnoittaa
  lisäämällä rekisteriä, ja nimetä kolme keinoa kasvattaa
  näytetaajuutta.
- Osaat jakaa SOS-kaskadin vahvistuksen lohkoille ja valita
  kertoimien Q-muodon.
- Osaat selittää, miksi kiertävä ylivuoto on IIR-suotimessa paljon
  vaarallisempi kuin FIR-suotimessa, ja testata saturaation.
- Osaat laskea kuolleen alueen rajan ja keinot pienentää sitä.

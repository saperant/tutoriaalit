# Monitaajuusrakenteet

Nopea A/D-muunnin tuottaa näytteitä paljon tiheämmin kuin kiinnostava
kaista vaatii. Ohjelmistoradion muunnin näytteistää satoja
megahertsejä, mutta yksi kanava on muutaman sadan kilohertsin
levyinen. Näytetaajuutta pienennetään *desimoimalla*: suodatetaan
alipäästöllä ja säilytetään joka $R$:s näyte. Laitteistossa
desimointi on enemmän kuin suodin ja valitsin, koska suodinta ei
tarvitse laskea niille näytteille, jotka heitetään pois. Tässä
luvussa toteutetaan kaksi tapaa hyödyntää tätä: kertojaton
CIC-suodin ja polyfaasisuodin.

## CIC-desimaattori

CIC-suodin (*cascaded integrator-comb*, Hogenauer 1981) on $N$
integraattoria sisääntulon näytetaajuudella, desimointi $R$:llä ja $N$
kampaa ulostulon näytetaajuudella. Integraattori on $w[n] = w[n-1] +
x[n]$ ja kampa $c[m] = v[m] - v[m-M]$, jossa $M$ on kamman viive
(tässä 1). Yhdessä ne ovat $N$ kertaa toistettu liukuva summa $RM$
näytteen yli:

$$H(z) = \left( \frac{1 - z^{-RM}}{1 - z^{-1}} \right)^N
= \left( \sum_{k=0}^{RM-1} z^{-k} \right)^N.$$

Alla oleva kuva näyttää kolmiasteisen CIC-desimaattorin: integraattorit
toimivat sisääntulon taajuudella, ja kammat toimivat desimoinnin
jälkeen $R$ kertaa hitaammin.

```{.dot otsikko="Kolmiasteinen CIC-desimaattori"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.3;
  node [width=0.5, height=0.35];
  x [label="x[n]", shape=plaintext, style=""];
  y [label="y[m]", shape=plaintext, style=""];
  i1 [label="∫"]; i2 [label="∫"]; i3 [label="∫"];
  r [label="↓R", shape=circle];
  c1 [label="1 − z⁻ᴹ"]; c2 [label="1 − z⁻ᴹ"]; c3 [label="1 − z⁻ᴹ"];
  x -> i1 -> i2 -> i3 -> r -> c1 -> c2 -> c3 -> y;
  subgraph cluster_nopea { label="sisääntulon taajuus"; fontsize=9;
    style="rounded,dashed"; color="#9aa7ab"; i1; i2; i3; }
  subgraph cluster_hidas { label="ulostulon taajuus"; fontsize=9;
    style="rounded,dashed"; color="#9aa7ab"; c1; c2; c3; }
}
```

Rakenteessa ei ole yhtään kertojaa eikä kerrointa, ja sen voi
toteuttaa millä tahansa desimointisuhteella samalla määrällä
summaimia. Siksi CIC on desimointiketjun ensimmäinen vaihe
lähes jokaisessa digitaalisessa radiossa.

```{.systemverilog tiedosto="esimerkit/rtl/cic.sv" osa="cic"}
```

Integraattorit ovat rekistereitä, joten jokainen niistä lisää
edellisen asteen *edellisen* jakson arvon. Kammat lasketaan vasta,
kun desimoitava näyte on valmis. Ne ovat tässä yhdistelmälogiikkaa,
kolme vähennyslaskua peräkkäin. Koska kammat päivittyvät vain joka
kahdeksannella jaksolla, ne voisi myös laskea yhdellä vähentäjällä
kolmessa jaksossa. Malli seuraa samaa rakennetta:

```{.python tiedosto="esimerkit/malli/suotimet.py" osa="cic"}
```

## Bittikasvu ja kiertävä laskenta

CIC-suotimen vahvistus tasavirralla on $(RM)^N$. Esimerkissä
$8^3 = 512$, joten ulostulo on yhdeksän bittiä sisääntuloa leveämpi.
Hogenauerin sääntö antaa sisäisen leveyden

$$B = B_{\mathrm{in}} + N \log_2(RM).$$

```{.python tiedosto="esimerkit/analyysit/cic.py" osa="hogenauer"}
```

```{.tuloste tiedosto="esimerkit/odotetut/cic.odotettu"}
```

Sääntö koskee vain ulostuloa. Integraattoreiden arvot kasvavat ilman
rajaa: vakio sisääntulo kasvattaa ensimmäistä lineaarisesti, toista
neliöllisesti ja kolmatta kuutiollisesti. Ne vuotavat siis yli, eikä
sitä voi estää millään leveydellä. Ratkaisu on päästää ne vuotamaan:
kun kaikki laskenta tehdään samalla $B$:n bitin kahden komplementin
leveydellä, kamman vähennyslasku kumoaa integraattorien ylivuodot,
koska tulos tiedetään mahtuvan $B$ bittiin. Tämä on CIC-suotimen
toinen keskeinen idea: modulo-aritmetiikka tekee oikean tuloksen
väärien välitulosten kautta.

Analyysin viimeiset rivit näyttävät sen. 21-bittinen kiertävä
laskenta antaa saman tuloksen kuin rajattomat kokonaisluvut. Bittiä
kapeampi toteutus menee rikki täydellä askeleella, koska oikea
ulostulo ei enää mahdu. RTL-testi raportoi, kuinka monesti
integraattorit todella vuotavat yli, ja tulos on silti bittitarkka:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-cic.odotettu"}
```

Kiertävä laskenta vaatii, ettei integraattoreita saturoida. Saturoiva
summain, joka muualla on hyvä tapa, rikkoo CIC-suotimen.

Ulostulosta pudotetaan tässä viisi alinta bittiä katkaisemalla, jotta
ulostulo on 16-bittinen. Hogenauer osoitti, että bittejä voi pudottaa
jo integraattoreista ja kammoista, porras portaalta enemmän, kun
pudotusten virhe pidetään pienempänä kuin ulostulon katkaisun virhe.
Tämä *karsinta* (*pruning*) säästää rekistereitä etenkin suurilla
$R$:n arvoilla.

## Taajuusvaste ja kompensointi

CIC-suotimen taajuusvaste on sinc-funktion $N$:s potenssi.
Päästökaista ei ole tasainen: analyysin mukaan vahvistus on jo
neljänneksellä ulostulon näytetaajuudesta −2,7 dB. Tätä *taipumaa*
(*droop*) kompensoidaan desimoinnin jälkeen lyhyellä FIR-suotimella,
jonka vaste nousee kaistan reunaa kohti (*CFIR*, compensation FIR).
Kompensointisuodin toimii jo matalalla näytetaajuudella, joten se on
halpa. Usein sen perässä on vielä puolikaistasuodin, joka desimoi
kahdella ja hoitaa varsinaisen kaistanrajauksen.

Ketju on tyypillisesti:

1. CIC, $R$ = 8–1024, ei kertojia.
2. Kompensoiva FIR, desimointi 2, muutamia kymmeniä kertoimia.
3. Kanavasuodin, desimointi 2, vaatimusten mukainen jyrkkyys.

## Polyfaasidesimaattori

CIC sopii karkeaan desimointiin, mutta jyrkkä kanavasuodin on FIR.
Suora toteutus laskisi jokaisen ulostulon ja heittäisi pois $R - 1$
niistä. Polyfaasihajotelma laskee vain ne, jotka säilytetään.
Kirjoitetaan kertoimen indeksi muodossa $k = Rj + p$:

$$y[m] = \sum_{k=0}^{N-1} h_k\, x[Rm - k]
= \sum_{p=0}^{R-1} \sum_{j=0}^{N/R - 1} h_{Rj+p}\, x[R(m-j) - p].$$

Sisempi summa on *haara* $p$: se käyttää vain kertoimia $h_p, h_{p+R},
h_{p+2R}, \ldots$ ja vain näytteitä, joiden indeksi on $-p$ modulo $R$.
Jokainen sisääntulonäyte kuuluu täsmälleen yhteen haaraan. Kun näyte
saapuu, lasketaan sen haaran $N/R$ tuloa ja lisätään ne kertymään.
$R$ näytteen jälkeen kertymä on valmis ulostulo:

```{.systemverilog tiedosto="esimerkit/rtl/polyfaasi.sv" osa="kuvaus"}
```

```{.systemverilog tiedosto="esimerkit/rtl/polyfaasi.sv" osa="datapolku"}
```

16 kertoimen suodin, joka desimoi neljällä, tarvitsee neljä kertojaa
kuudentoista sijasta. Kertoimet valitaan haaran mukaan multiplekserillä
`K[(M*j + vaihe1)*KW +: KW]`: haara vaihtuu joka näytteellä.
Viivelinjasta luetaan joka neljäs paikka, joten se pysyy yhtenä
viivelinjana eikä hajoa neljäksi.

Malli ei tiedä haaroista mitään. Se laskee suoran FIR-suotimen ja
valitsee joka neljännen ulostulon:

```{.python tiedosto="esimerkit/malli/suotimet.py" osa="desimoi"}
```

Tämä on tarkoituksellista. Referenssin kuuluu olla yksinkertaisin
oikea kuvaus, ei toteutuksen kopio: jos malli ja RTL käyttäisivät
samaa hajotelmaa, sama indeksivirhe voisi olla molemmissa. Testi
vertaa polyfaasirakennetta suoraan määritelmään:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-polyfaasi.odotettu"}
```

## Interpolointi

Interpolointi on desimoinnin peilikuva: näytetaajuus kasvatetaan
$L$-kertaiseksi lisäämällä näytteiden väliin nollia ja suodattamalla.
Nollilla kertominen on turhaa, ja polyfaasihajotelma poistaa sen:
jokainen ulostulon vaihe $p$ lasketaan kertoimilla $h_p, h_{p+L},
\ldots$ ja *todellisista* näytteistä. Kertojia tarvitaan $N/L$, ja
ne laskevat ulostulon näytetaajuudella. CIC-interpolaattorissa
järjestys kääntyy: kammat ensin matalalla taajuudella, sitten
integraattorit korkealla.

Rationaalinen muunnos $L/M$, esimerkiksi 44,1 kHz → 48 kHz, on
interpolaattori ja desimaattori yhdessä polyfaasirakenteessa, jossa
haara valitaan laskurilla, joka etenee $M$ askelta $L$:n
modulossa.

## Käytännössä

- Desimoi heti, kun kaista sallii: jokainen myöhempi vaihe toimii
  pienemmällä näytetaajuudella ja on halvempi.
- Käytä CIC-suodinta karkeaan desimointiin suurilla $R$:n arvoilla
  ja kompensoi sen taipuma FIR-suotimella.
- Mitoita CIC:n sisäinen leveys Hogenauerin säännöllä ja päästä
  integraattorit kiertämään. Älä saturoi niitä.
- Toteuta FIR-desimaattori polyfaasirakenteena: kertojia on $N/R$
  eikä $N$.
- Kirjoita malli määritelmästä, ei toteutuksesta. Suora suodin ja
  valinta on parempi referenssi polyfaasirakenteelle kuin toinen
  polyfaasitoteutus.

## Itsearviointi

- Osaat selittää CIC-suotimen rakenteen ja johtaa sen siirtofunktion.
- Osaat laskea CIC:n sisäisen leveyden ja perustella, miksi
  integraattorien ylivuoto ei haittaa.
- Osaat kertoa, miksi CIC tarvitsee kompensointisuotimen ja missä
  kohtaa ketjua se on.
- Osaat johtaa polyfaasihajotelman ja toteuttaa desimaattorin, jossa
  on $N/R$ kertojaa.
- Osaat perustella, miksi referenssimalli ei saa käyttää samaa
  hajotelmaa kuin RTL.

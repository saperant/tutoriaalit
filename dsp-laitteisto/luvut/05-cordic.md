# CORDIC

Sini, kosini, arkustangentti ja vektorin pituus ovat signaalinkäsittelyn
arkipäivää: sekoittimet, vaiheen ja amplitudin ilmaisimet,
koordinaattimuunnokset. Prosessori laskee ne kirjastofunktiolla.
Laitteistossa kertojakin on kallis, saati sarjakehitelmä. CORDIC
(*COordinate Rotation DIgital Computer*, Volder 1959) laskee nämä
funktiot pelkillä siirroilla, yhteenlaskuilla ja pienellä
kulmataulukolla. Jokainen kierros tuottaa noin yhden bitin tarkkuutta.

## Kierto siirroilla

Vektorin $(x, y)$ kierto kulmalla $\theta$ on

$$x' = x \cos\theta - y \sin\theta, \qquad
y' = y \cos\theta + x \sin\theta.$$

Kun $\cos\theta$ otetaan yhteiseksi tekijäksi, jäljelle jää
$\tan\theta$. Jos kulmat valitaan niin, että $\tan\theta_i = 2^{-i}$,
kertolasku luvulla $\tan\theta_i$ on siirto oikealle $i$ bittiä.
Mikä tahansa kulma voidaan koota summana $\sum_i d_i \theta_i$, jossa
$d_i = \pm 1$ valitaan kierros kierrokselta:

$$x_{i+1} = x_i - d_i\, y_i\, 2^{-i}, \qquad
y_{i+1} = y_i + d_i\, x_i\, 2^{-i}, \qquad
z_{i+1} = z_i - d_i \arctan 2^{-i}.$$

Pois jätetty tekijä $\cos\theta_i$ kertautuu kaikista kierroksista
vahvistukseksi

$$K = \prod_i \sqrt{1 + 2^{-2i}} \approx 1.6468.$$

Koska $d_i = \pm 1$, $|\cos(d_i\theta_i)|$ ei riipu suunnasta, ja $K$ on
vakio. Se kompensoidaan kerran: aloitetaan pisteestä $(1/K, 0)$,
jolloin tulos on suoraan $(\cos z, \sin z)$, tai skaalataan tulos
lopuksi.

## Rotaatio ja vektori

Suunta $d_i$ valitaan kahdella tavalla:

| Tila | Valinta | Tulos | Käyttö |
|------|---------|-------|--------|
| rotaatio | $d_i = \mathrm{sign}(z_i)$, kohti $z = 0$ | $(x, y)$ kierrettynä kulmalla $z$, kertaa $K$ | sin, cos, sekoitin, kiertomatriisi |
| vektori | $d_i = -\mathrm{sign}(y_i)$, kohti $y = 0$ | $x = K\sqrt{x^2+y^2}$, $z = \mathrm{atan2}(y, x)$ | vaihe, amplitudi, polaarimuunnos |

Yksi kierros bittitarkkana mallina:

```{.python tiedosto="esimerkit/malli/cordic.py" osa="iteraatio"}
```

Kierrosten kulmien summa on noin 99,9 astetta, joten CORDIC suppenee
vain, kun kierrettävä kulma on tätä pienempi. Toinen ja kolmas
neljännes käsitellään *esikierrolla*: vektori käännetään puoli
kierrosta vaihtamalla molempien komponenttien etumerkki, ja kulmaan
lisätään $\pi$. Vektoritilassa sama tehdään, kun $x < 0$:

```{.python tiedosto="esimerkit/malli/cordic.py" osa="alku"}
```

Kulmat esitetään *binäärikulmina*: täysi kierros on $2^{16}$
sisääntulossa ja $2^{18}$ sisäisesti. Kulmien yhteenlasku kiertää
luonnostaan oikein, koska $2\pi$ vastaa kahden komplementin
ylivuotoa. Neljännes nähdään kahdesta ylimmästä bitistä. Radiaanit
olisivat huono valinta, koska $2\pi$ ei ole kahden potenssi.

Sisäiset $x$ ja $y$ ovat muotoa Q3.17: kaksi bittiä lisää alueeseen
vahvistuksen $K$ ja vektoritilan pituuden $\sqrt 2$ takia, ja kaksi
murtobittiä lisää pyöristysvirheiden kertymistä vastaan. Koko CORDIC
on esikierto ja kierrokset:

```{.python tiedosto="esimerkit/malli/cordic.py" osa="cordic"}
```

## Tarkkuus

Kierros $i$ kiertää kulmalla $\arctan 2^{-i} \approx 2^{-i}$, joten
viimeisen kierroksen jälkeen jäljellä oleva kulmavirhe on noin
$2^{-n}$ radiaania. Jokainen kierros tuo yhden bitin, kunnes sanaleveys
rajoittaa:

```{.python tiedosto="esimerkit/analyysit/cordic_tarkkuus.py" osa="tarkkuus"}
```

```{.tuloste tiedosto="esimerkit/odotetut/cordic_tarkkuus.odotettu"}
```

Kymmeneen kierrokseen asti tarkkuus kasvaa täsmälleen bitin
kierrosta kohden. Sen jälkeen kasvu hidastuu, koska jokainen siirto
pudottaa alimmat bitit ja nämä katkaisuvirheet kertyvät, ja 16
kierroksella tarkkuus on 13 bittiä. Vahvistus $K$ muuttuu kymmenen
kierroksen jälkeen enää kuudennessa desimaalissa, joten sen
kompensoinnin voi laskea yhdellä vakiolla, kunhan kierroksia on
riittävästi. Nyrkkisääntö: $n$ bitin
tarkkuuteen tarvitaan noin $n$ kierrosta ja $\log_2 n$ ylimääräistä
murtobittiä.

## Iteratiivinen toteutus

Iteratiivinen CORDIC käyttää yhtä kiertovaihetta kierros kerrallaan.
Siirron määrä vaihtuu joka kierroksella, joten vaiheessa on muuttuva
siirtäjä (*barrel shifter*) ja kulmataulukko, jota osoitetaan
kierroslaskurilla:

```{.systemverilog tiedosto="esimerkit/rtl/cordic_iter.sv" osa="iteraatio"}
```

Kulmataulukko on `malli/generoi.py`:n tuottama funktio, jonka
synteesi toteuttaa pienenä ROM:ina. Tulos valmistuu 16 jaksossa, ja
uusi syöte otetaan vasta sen jälkeen.

## Liukuhihnoitettu toteutus

Alla oleva kuva vertaa rakenteita: iteratiivinen toteutus kierrättää
tilaa saman vaiheen läpi, liukuhihnoitettu kopioi vaiheen jokaiselle
kierrokselle.

```{.dot otsikko="Iteratiivinen ja liukuhihnoitettu CORDIC"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  node [height=0.4];
  subgraph cluster_lh { label="liukuhihnoitettu"; fontsize=9;
    style="rounded,dashed"; color="#9aa7ab";
    la [label="x, y, z", shape=plaintext, style=""];
    v0 [label="vaihe 0\nsiirto 0"]; v1 [label="vaihe 1\nsiirto 1"];
    vd [label="…", shape=plaintext, style=""];
    v15 [label="vaihe 15\nsiirto 15"];
    la -> v0 -> v1 -> vd -> v15; }
  subgraph cluster_iter { label="iteratiivinen"; fontsize=9;
    style="rounded,dashed"; color="#9aa7ab";
    ia [label="x, y, z", shape=plaintext, style=""];
    iv [label="kiertovaihe\nsiirto i, kulma[i]"];
    ir [label="rekisterit"];
    ia -> iv -> ir; ir -> iv [label=" i = 0…15", constraint=false]; }
}
```

Liukuhihnoitetussa CORDICissa jokainen kierros on oma vaiheensa.
Siirron määrä on vaiheessa vakio, joten siirto on pelkkää johdotusta,
ja kulma on vakio. Vaiheita on 16 ja jokaisessa kolme summainta, mutta
uusi syöte voidaan ottaa joka jaksolla:

```{.systemverilog tiedosto="esimerkit/rtl/cordic_lh.sv" osa="vaiheet"}
```

Tila (`tila`) kulkee datan rinnalla vaiheesta toiseen, joten rotaatio
ja vektori voivat vuorotella näyte näytteeltä. Molemmat toteutukset
antavat bitilleen saman tuloksen kuin malli:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-cordic-lh.odotettu"}
```

Testi kiertää alkupistettä $(1/K, 0)$ kulmilla ympäri kierroksen,
neljännesten rajat mukaan lukien, ja vertaa tulosta myös tarkkoihin
arvoihin. Suurin virhe 14,5 LSB:tä muodossa Q3.17 on 3,6 LSB:tä
muodossa Q1.15 eli noin 13 bitin tarkkuus, kuten analyysi ennusti.
Vektoritilan testi laskee kulman ja pituuden satunnaisille
pisteille.

| Toteutus | Läpäisy | Latenssi | Resurssit |
|----------|---------|----------|-----------|
| iteratiivinen | 1 / 17 jaksoa | 17 | yksi vaihe, siirtäjä, ROM, laskuri |
| liukuhihnoitettu | 1 / jakso | 17 | 16 vaihetta, ei siirtäjiä |
| avattu yhdistelmälogiikka | 1 / jakso | 1 | 16 vaihetta ilman rekistereitä; hidas |

Luvussa 10 liukuhihnoitettu versio vie noin viisinkertaisen määrän
logiikkasoluja ja toimii suuremmalla kellotaajuudella.
Kompromisseja on monta: kaksi kierrosta vaihetta kohden, tai muutama
iteratiivinen yksikkö rinnakkain.

## Muunnelmat

- **Kertojan kanssa.** Kun piirissä on DSP-lohkoja, sini lasketaan
  usein taulukosta ja Taylorin korjauksesta. CORDIC on edullisin,
  kun kertojia ei ole tai ne on varattu muuhun.
- **Vahvistuksen poisto.** Jos tulosta käytetään vain vaiheena
  (vektoritilan $z$), vahvistusta ei tarvitse kompensoida lainkaan.
- **Hyperbolinen ja lineaarinen CORDIC.** Samalla rakenteella
  lasketaan myös $\exp$, $\ln$, $\sqrt{\ }$ ja jakolasku vaihtamalla
  iteraatioyhtälön etumerkki ja kulmataulukko.
- **Ennustettu suunta.** Viimeisten kierrosten suunnat voidaan laskea
  kerralla jäljellä olevasta kulmasta, mikä lyhentää liukuhihnaa.

## Käytännössä

- Käytä binäärikulmia: täysi kierros on kahden potenssi, ja kulmien
  ylivuoto on oikea kiertyminen.
- Valitse kierrosten määrä tarkkuusvaatimuksesta (noin bitti
  kierrosta kohden) ja lisää sisäiseen leveyteen kaksi bittiä
  alueelle ja $\log_2 n$ murtobittiä.
- Kompensoi vahvistus alkupisteessä, jos alkupiste on vakio. Silloin
  kompensointi ei maksa mitään.
- Valitse iteratiivinen toteutus, kun näytetaajuus on paljon
  kellotaajuutta pienempi, ja liukuhihnoitettu, kun tarvitaan tulos
  joka jaksolla.
- Testaa neljännesten rajat ja täyden asteikon vektorit erikseen:
  niissä esikierron ja sisäisen alueen virheet näkyvät.

## Itsearviointi

- Osaat johtaa CORDIC-iteraation kiertomatriisista ja selittää,
  mistä vahvistus $K$ tulee.
- Osaat käyttää rotaatiotilaa sinin ja kosinin ja vektoritilaa
  kulman ja pituuden laskemiseen.
- Osaat toteuttaa esikierron ja selittää, miksi CORDIC ei suppene
  ilman sitä.
- Osaat mitoittaa kierrosten määrän ja sisäisen sanaleveyden
  tarkkuusvaatimuksesta.
- Osaat verrata iteratiivista ja liukuhihnoitettua toteutusta
  läpäisyn, latenssin ja resurssien osalta.

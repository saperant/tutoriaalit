# Tilakoneet

Tilakone (finite state machine, FSM) on ohjauslogiikan perusmuoto:
tilarekisteri, kombinaatiologiikka, joka laskee seuraavan tilan, ja
ulostulologiikka. Digitaalitekniikasta tutut Moore- ja Mealy-koneet
kirjoitetaan SystemVerilogilla muutamalla vakiintuneella mallilla.
Tässä luvussa rakennetaan kaksi oikeaa lohkoa: UART-lähetin ja
painonapin värähtelyn vaimennin.

## Tilat luettelotyyppinä

Tilat määritellään `enum`-tyyppinä. Nimet näkyvät simulaattorin
aaltomuodoissa ja tulosteissa, ja kääntäjä tarkistaa, ettei tilamuuttujaan
sijoiteta muuta kuin tiloja. Perustyyppi (`logic [1:0]`) määrää
tilarekisterin leveyden. Arvot voi jättää työkalun valittaviksi,
jolloin synteesi voi valita koodauksen itse.

| Koodaus | Kiikkuja (N tilaa) | Ominaisuudet |
|---------|--------------------|--------------|
| binääri | log2(N) | vähiten kiikkuja, enemmän dekoodauslogiikkaa |
| one-hot | N | nopea ja yksinkertainen dekoodaus, yleinen FPGA:ssa |
| Gray | log2(N) | vain yksi bitti vaihtuu peräkkäisissä tiloissa |

## Kelvollinen/valmis-kättely

Ennen ensimmäistä lohkoa tarvitaan tapa, jolla kaksi lohkoa sopii
datan siirrosta. Tämän tutoriaalin kaikki virtarajapinnat käyttävät
*kelvollinen/valmis-kättelyä* (valid/ready), joka on myös AXI-väylien
perusta. Tuottaja nostaa `kelvollinen`-signaalin, kun sillä on dataa.
Kuluttaja nostaa `valmis`-signaalin, kun se voi ottaa datan vastaan.
Säännöt ovat:

1. Sana siirtyy sillä kellon reunalla, jolla sekä `kelvollinen` että
   `valmis` ovat ykkösiä. Muilla reunoilla ei tapahdu mitään.
2. Kun tuottaja on nostanut `kelvollinen`-signaalin, se ei saa perua
   sitä eikä muuttaa dataa ennen kuin siirto on tapahtunut.
3. `kelvollinen` ei saa riippua `valmis`-signaalista. Tuottaja ei jää
   odottamaan, että kuluttaja on valmis, ennen kuin tarjoaa dataa.
   Kuluttaja saa odottaa `kelvollinen`-signaalia.

Kolmas sääntö estää lukkiutuman, jossa kumpikin odottaa toista, ja
kombinatorisen silmukan (luku 11). Kumpi tahansa osapuoli voi hidastaa
siirtoa: tuottaja laskemalla `kelvollinen`-signaalin siirtojen välillä,
kuluttaja pitämällä `valmis`-signaalin alhaalla. Jälkimmäinen on
*vastapaine* (backpressure), johon palataan luvussa 7.

## Kaksiprosessityyli: UART-lähetin

UART lähettää tavun sarjamuotoisena: aloitusbitti 0, kahdeksan databittiä
vähiten merkitsevä ensin ja lopetusbitti 1. Lepotilassa linja on 1.
Lähetin on tilakone, jossa on neljä tilaa ja kaksi laskuria: jakson
sisäinen laskuri mittaa bittiajan ja bittilaskuri kertoo, monesko
databitti on menossa.

```{.dot otsikko="UART-lähettimen tilakone"}
digraph {
  rankdir=LR; nodesep=0.4;
  LEPO [shape=circle, width=0.8, fixedsize=true];
  ALKU [shape=circle, width=0.8, fixedsize=true];
  DATA [shape=circle, width=0.8, fixedsize=true];
  LOPPU [shape=circle, width=0.8, fixedsize=true];
  LEPO -> ALKU [label="kelvollinen"];
  ALKU -> DATA [label="bitti ohi"];
  DATA -> DATA [label="bitti ohi,\nbitti < 7"];
  DATA -> LOPPU [label="bitti ohi,\nbitti = 7"];
  LOPPU -> LEPO [label="bitti ohi"];
}
```

Kaksiprosessityylissä tilakone jaetaan kahteen lohkoon. Kombinatorinen
lohko laskee kaikkien rekisterien seuraavat arvot (`_d`), ja kellotettu
lohko tallentaa ne (`_q`). Jälkiliitteet kertovat lukijalle heti,
kummalla puolella kiikkua signaali on.

```{.systemverilog tiedosto="esimerkit/06-uart-tx/uart_tx.sv" osa="tilat"}
```

Seuraavan tilan logiikka alkaa oletussijoituksilla: pysy tilassa,
kasvata laskuria, pidä linja ykkösenä. Kukin tila muuttaa vain sen,
mikä siinä poikkeaa oletuksesta.

```{.systemverilog tiedosto="esimerkit/06-uart-tx/uart_tx.sv" osa="seuraava"}
```

Lähetin on kättelyn kuluttaja: se nostaa `valmis`-signaalin vain
lepotilassa, ja tavu siirtyy sillä reunalla, jolla myös `kelvollinen`
on ykkönen.

Kellotettu lohko on pelkkä rekisterijoukko. Myös `tx` kulkee kiikun
kautta. Rekisteröity ulostulo ei näytä kombinaatiologiikan piikkejä,
mikä on tärkeää, koska linja lähtee piiriltä ulos ja vastaanottaja
näytteistää sitä omalla kellollaan.

```{.systemverilog tiedosto="esimerkit/06-uart-tx/uart_tx.sv" osa="rekisterit"}
```

Koko moduuli on tiedostossa `06-uart-tx/uart_tx.sv`. Bittiaika lasketaan
parametreista käännösaikana (`KELLO_HZ / BAUD`).

Testipenkki toimii kuin oikea vastaanotin: se odottaa aloitusbitin
laskevaa reunaa, siirtyy puoli bittiaikaa eteenpäin ja näytteistää
jokaisen bitin keskeltä.

```{.systemverilog tiedosto="esimerkit/06-uart-tx/testipenkki.sv" osa="vastaanotin"}
```

Lähettävä ja vastaanottava osa ajetaan rinnakkain `fork`–`join`-
rakenteella. Lähettäjä pitää `kelvollinen`-signaalia ylhäällä, kunnes
kättely onnistuu:

```{.systemverilog tiedosto="esimerkit/06-uart-tx/testipenkki.sv" osa="lahetys"}
```

```{.tuloste tiedosto="esimerkit/06-uart-tx.odotettu"}
```

Alla oleva kaavio on piirretty samasta simulaatiosta, mutta näyte on
otettu kerran bittiajassa bitin keskeltä, kuten vastaanotin tekee.
Ensimmäinen merkki on R (52 heksana, 0101 0010), joka kulkee linjalla
vähiten merkitsevä bitti ensin. Tila on numeroina: 1 = `ALKU`,
2 = `DATA` ja 3 = `LOPPU`. Kaavion lopussa seuraavan merkin
aloitusbitti alkaa heti lopetusbitin jälkeen.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/06-uart-tx.json" otsikko="UART-kehys: aloitusbitti, kahdeksan databittiä ja lopetusbitti"}
```

Kättely näkyy samasta simulaatiosta kellojakson tarkkuudella. Kaaviossa
testipenkki tarjoaa merkkiä T (54) ja pitää `kelvollinen`-signaalin
ja datan paikallaan, kunnes edellisen merkin lopetusbitti on lähetetty.
Lähetin palaa tilaan `LEPO` ja nostaa `valmis`-signaalin yhdeksi
jaksoksi. Merkki siirtyy sen jakson lopun reunalla, ja testipenkki
vaihtaa heti tarjolle seuraavan merkin L (4C).

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/06-kattely.json" otsikko="Kättely: merkki siirtyy reunalla, jolla kelvollinen ja valmis ovat ylhäällä"}
```

## Yksiprosessityyli: värähtelyn vaimennin

Mekaaninen kytkin värähtelee painettaessa: kosketus aukeaa ja sulkeutuu
useita kertoja muutaman millisekunnin ajan. Vaimennin hyväksyy uuden
tason vasta, kun se on pysynyt samana riittävän kauan. Raaka signaali
on asynkroninen, joten se tahdistetaan ensin kahdella kiikulla
(luku 10).

Tämä tilakone on kirjoitettu yksiprosessityylillä: tila, laskuri ja
ulostulopulssi päivitetään samassa `always_ff`-lohkossa. Malli on
tiivis, kun ulostulot ovat rekisteröityjä ja seuraava tila riippuu
yksinkertaisesti nykyisestä.

```{.systemverilog tiedosto="esimerkit/06-vaimennin.sv" osa="vaimennin"}
```

Välitilat `PAINUU` ja `NOUSEE` odottavat vakautta. Jos signaali palaa
takaisin ennen kuin laskuri täyttyy, tila palaa lähtötilaan.

```{.dot otsikko="Värähtelyn vaimentimen tilakone"}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.9;
  node [shape=ellipse];
  YLHAALLA -> PAINUU [label="nappi"];
  PAINUU -> YLHAALLA [label="!nappi"];
  PAINUU -> ALHAALLA [label="vakaa\n/ painallus"];
  ALHAALLA -> NOUSEE [label="!nappi"];
  NOUSEE -> ALHAALLA [label="nappi"];
  NOUSEE -> YLHAALLA [label="vakaa"];
}
```

Testipenkki syöttää kaksi värähtelevää painallusta ja yhden liian
lyhyen häiriön:

```{.tuloste tiedosto="esimerkit/06-vaimennin.odotettu"}
```

Alla on testipenkin ensimmäinen painallus puolen kellojakson
tarkkuudella. Raaka tulo värähtelee, mutta tahdistin näytteistää sen
vain kellon reunoilla, ja tahdistettu `nappi` pysyy ylhäällä vasta
värähtelyn loputtua. Tilakone odottaa tilassa `PAINUU` kahdeksan
jaksoa (`VAKAA = 8`) ja antaa sitten yhden jakson `painallus`-pulssin.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/06-vaimennin.json" otsikko="Vaimennin: värähtelevä tulo, tahdistettu taso ja yksi painalluspulssi"}
```

## Käytännössä

- **Kaksi- vai yksiprosessityyli.** Kaksiprosessityyli (`_d`/`_q`)
  sopii tilakoneisiin, joissa on paljon kombinatorisia ulostuloja ja
  monimutkainen seuraavan tilan logiikka: kaikki päätökset ovat yhdessä
  paikassa, ja rekisterit ovat triviaaleja. Yksiprosessityyli sopii
  pieniin koneisiin, joiden kaikki ulostulot ovat rekisteröityjä.
  Kolmiprosessityylissä ulostulot erotetaan vielä omaan lohkoonsa.
  Valinta on tyylikysymys, mutta yhden projektin sisällä kannattaa
  pitäytyä yhdessä.
- **Oletukset ensin.** Kombinatorisen lohkon alussa `tila_d = tila_q`
  ja ulostulojen lepoarvot. Ilman oletuksia jokainen haara joutuu
  sijoittamaan kaiken, ja yksikin unohdus tuottaa salvan.
- **Turvallinen paluu.** Jos tiloja on vähemmän kuin
  tilarekisterin koodeja, käyttämättömät koodit ohjataan
  `default`-haaralla lepotilaan. Säteily tai jännitekuoppa voi kääntää
  bitin. Turvallisuuskriittisissä suunnitelmissa synteesityökalulle
  kerrotaan lisäksi, ettei se saa optimoida paluulogiikkaa pois.
- **Rekisteröidyt ulostulot rajapinnoille.** Piiriltä ulos lähtevä tai
  toiseen kellotusalueeseen menevä signaali tulee suoraan kiikusta.
  Mealy-ulostulo, joka riippuu syötteestä kombinatorisesti, pidentää
  ajoituspolkua ja voi muodostaa silmukan (luku 11).
- **Kättely jokaiseen rajapintaan, jossa jompikumpi voi hidastaa.**
  Kelvollinen/valmis-kättelyn kolme sääntöä riittävät kytkemään
  minkä tahansa tuottajan mihin tahansa kuluttajaan ilman tietoa
  toisen ajoituksesta. Rajapinta, joka olettaa "data tulee kolmen
  jakson päästä", hajoaa, kun jompaakumpaa lohkoa muutetaan.
- **Tilakone ja datapolku erikseen.** Laskurit, siirtorekisterit ja
  vertailijat ovat *datapolkua*, ja tilakone ohjaa niitä. Rakenne
  tunnetaan nimellä FSMD (FSM with datapath). Tilakoneen tilojen määrä
  pysyy pienenä, kun laskenta ei ole tiloissa.

## Itsearviointi

- Osaat määritellä tilat `enum`-tyyppinä ja valita tilakoodauksen.
- Osaat kirjoittaa tilakoneen kaksiprosessityylillä (`_d`/`_q`) ja
  yksiprosessityylillä ja perustella valinnan.
- Osaat toteuttaa kelvollinen/valmis-kättelyn ja selittää sen säännöt.
- Osaat jakaa ohjauksen tilakoneeseen ja datapolkuun (FSMD).
- Osaat kirjoittaa testipenkin, joka purkaa sarjamuotoisen ulostulon
  oikean vastaanottimen tavoin.

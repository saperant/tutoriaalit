# Synteesi ja koodaustyyli

Synteesityökalu tunnistaa RTL:stä rakenteita, kuten muisteja,
kertojia, laskureita ja tilakoneita, ja kuvaa ne piirin palikoihin.
Tunnistus perustuu malleihin: jos kuvaus noudattaa mallia, tulos on
tehokas, ja jos ei, sama toiminta rakentuu logiikkasoluista. Luku
näyttää kaksi tärkeintä tapausta, muistin ja kertojan.

## Muistin päättely

Lohko-RAM on synkroninen: luettu tieto tulee ulos kellon reunan
jälkeen. Synteesi voi käyttää lohko-RAMia vain, jos kuvaus lukee
muistia samalla tavalla:

```{.systemverilog tiedosto="esimerkit/04-muisti/muisti.sv" osa="muisti"}
```

Muuttuja `sisalto` on taulukko, johon kirjoitetaan kellotetussa
lohkossa. Synteesi tunnistaa sen muistiksi ja katsoo sitten lukuportin:
rekisteröity luku sopii lohko-RAMiin, kombinatorinen ei.

```{.tuloste tiedosto="esimerkit/raportit/muisti-synk.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/muisti-komb.odotettu"}
```

Synkroninen versio käyttää yhden lohko-RAMin ja 41 logiikkasolua.
Kombinatorinen versio vie 3 920 logiikkasolua, yli 70 % piiristä:
2 048 kiikkua muistibiteille ja suuren multiplekserin lukuosoitteelle.
Toiminnaltaan versiot eroavat vain yhdellä kellojaksolla.

Synkroninen luku näkyy testipenkissä: tulos vaihtuu vasta reunan
jälkeen.

```{.systemverilog tiedosto="esimerkit/04-muisti/testipenkki.sv" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-muisti.odotettu"}
```

Muistin päättelyssä on muitakin sääntöjä:

- **Nollaus.** Lohko-RAMia ei voi nollata kerralla. Jos muistille
  kirjoittaa nollaussilmukan, synteesi rakentaa sen kiikuista.
  Alkuarvon voi antaa alustuksella (`initial` tai `$readmemh`), jolloin
  arvot päätyvät bittivirtaan.
- **Porttien määrä.** iCE40:n lohko-RAMissa on yksi luku- ja yksi
  kirjoitusportti. Kaksi lukuporttia vaatii kaksi kopiota muistista.
- **Lukuportin rekisteri.** Osoitteen rekisteröinti
  (`osoite_r <= osoite; tieto <= sisalto[osoite_r];`) ja tiedon
  rekisteröinti (`tieto <= sisalto[osoite];`) ovat molemmat malleja,
  jotka Yosys tunnistaa.

## Kertojan päättely

Kertolasku `a * b` on synteesille yksi operaatio, jonka voi toteuttaa
DSP-lohkolla tai logiikkasoluilla. `synth_ice40` käyttää DSP-lohkoja
vain valinnalla `-dsp`:

```{.systemverilog tiedosto="esimerkit/04-kertoja/kertoja.sv" osa="kertoja"}
```

```{.tuloste tiedosto="esimerkit/raportit/kertoja-dsp.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/kertoja-lut.odotettu"}
```

DSP-lohkolla kertoja vie kaksi logiikkasolua, ilman sitä 157
logiikkasolua ja 10 kantoketjua. Kahdeksan DSP-lohkoa on kuitenkin
nopeasti käytetty. Vakiolla kertominen ei tarvitse DSP-lohkoa:
`x * 5` on `(x << 2) + x`, ja synteesi tekee muunnoksen itse.

Testipenkki käy läpi kaikki 65 536 tuloa. Kahdeksan bitin tulot ovat
niin pieni joukko, että kattava testi on halvempi kuin sen
miettiminen, mitkä tapaukset riittäisivät:

```{.systemverilog tiedosto="esimerkit/04-kertoja/testipenkki.sv" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-kertoja.odotettu"}
```

## Muita malleja

| Kuvaus | Synteesin tulos iCE40:ssä |
|--------|---------------------------|
| `always_ff` ilman nollausta, alkuarvo `= '0` | kiikku, alkuarvo bittivirrassa |
| synkroninen nollaus | `SB_DFFSR`: nollaus kiikun omaan tuloon |
| asynkroninen nollaus | `SB_DFFR`; nollaussignaali yleensä globaaliin verkkoon |
| `if (sallittu) q <= d;` | `SB_DFFE`: sallinta kiikun tuloon, ei multiplekseriä |
| summain, vähennys, vertailu | LUT:t ja kantoketju |
| `case` tilakoneessa | Yosys voi uudelleenkoodata tilat (`fsm`) |
| kombinatorinen silmukka | virhe tai salpa; ajoitusanalyysi ei toimi |

Valmistajat dokumentoivat omat mallinsa (AMD:llä "HDL coding
guidelines", Intelillä "Recommended HDL Coding Styles"). Mallit ovat
pääpiirteissään samoja kuin tässä, mutta yksityiskohdat, kuten
lohko-RAMin lukutilat ja DSP:n rekisterit, vaihtelevat piireittäin.

## Synteesin tarkistaminen

Synteesi onnistuu lähes aina; virheet ovat hiljaisia. Siksi tulos
tarkistetaan:

- **Solutyypit.** `stat` kertoo, päätyikö muisti lohko-RAMiin ja
  kertoja DSP:hen. Esimerkkien vuo testaa tämän jokaisessa ajossa.
- **Varoitukset.** Yosys varoittaa esimerkiksi ajamattomista
  signaaleista ja kombinatorisista silmukoista. Lokin varoitukset
  käydään läpi ja joko korjataan tai perustellaan.
- **Poistettu logiikka.** Jos lähtöä ei käytetä, synteesi poistaa sitä
  tuottavan logiikan. Hämmästyttävän pieni solumäärä tarkoittaa usein,
  että jotain on jäänyt kytkemättä.

## Käytännössä

- **Kirjoita muisti malliin.** Rekisteröity luku, ei nollausta, yksi
  kirjoitusportti. Tarkista synteesin tilastoista, että lohko-RAM
  syntyi.
- **Ota DSP-lohkot käyttöön ja laske ne.** Kertolaskut ovat
  ensimmäinen resurssi, joka loppuu. Vakiolla kertominen ja kahden
  potensseilla skaalaaminen eivät tarvitse DSP:tä.
- **Vältä tarpeettomia nollauksia.** FPGA:ssa alkuarvo tulee
  bittivirrasta. Nollaa vain se, mikä on nollattava myös
  käynnistyksen jälkeen (tilakoneet, kelpaa-liput); datapolun rekisterit
  eivät yleensä tarvitse nollausta, ja ilman sitä synteesi voi käyttää
  DSP- ja RAM-lohkojen sisäisiä rekistereitä.
- **Testaa resurssit.** Jos jokin luku on suunnittelun kannalta
  olennainen (DSP-lohkojen määrä, lohko-RAMien määrä), tee siitä testi.

## Itsearviointi

- Osaat kirjoittaa muistin niin, että synteesi käyttää lohko-RAMia, ja
  selittää, miksi kombinatorinen luku estää sen.
- Osaat ohjata kertojan DSP-lohkoon ja arvioida, mitä se maksaa
  logiikkasoluina ilman DSP:tä.
- Osaat kertoa, mihin kiikun primitiiviin synkroninen nollaus, sallinta
  ja alkuarvo päätyvät.
- Osaat tarkistaa synteesin tuloksen tilastoista ja lokista.

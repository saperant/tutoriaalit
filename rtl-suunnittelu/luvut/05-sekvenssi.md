# Sekvenssilogiikka

Sekvenssilogiikassa on muisti: kiikut tallentavat arvon kellon
reunalla ja pitävät sen seuraavaan reunaan. Synkronisessa
suunnittelussa kaikki kiikut päivittyvät saman kellon samalla
reunalla, ja niiden välissä on kombinaatiologiikkaa. Tämä rakenne,
rekisteri–logiikka–rekisteri, on RTL:n ydin.

## always_ff ja ei-estävä sijoitus

Kiikut kuvataan `always_ff`-lohkolla. Herkkyyslistassa on kellon reuna
ja mahdollisen asynkronisen nollauksen reuna. Lohkossa sijoitetaan
*ei-estävällä* sijoituksella `<=`. Tämä on tavallisin kiikkumalli:
asynkroninen nollaus ja sallinta. Ote on pikaoppaan esimerkistä, jossa
sallintasignaalin nimi on `alku`: rekisteri ottaa uuden arvon vain
jaksolla, jolla `alku` on ykkönen.

```{.systemverilog tiedosto="esimerkit/pikaopas.sv" osa="rekisteri"}
```

Ei-estävä sijoitus toimii kahdessa vaiheessa. Ensin kaikkien
`always_ff`-lohkojen oikeat puolet lasketaan reunaa edeltävistä
arvoista, ja vasta sitten kaikki vasemmat puolet päivitetään yhtä aikaa.
Juuri näin kiikut toimivat: kaikki näytteistävät syötteensä samalla
hetkellä. Siksi lohkojen järjestyksellä ei ole merkitystä, ja
`a <= b; b <= a;` vaihtaa kahden rekisterin arvot.

## Rekisterit ja siirtorekisterit

Edellä rekisteri ei päivity joka jaksolla, vaan vain kun
*sallinta* on päällä. Synteesi tekee tästä kiikun, jonka edessä on
multiplekseri, tai käyttää kiikun omaa sallintatuloa. Kun sallinta ei
ole päällä, rekisteri pitää arvonsa: haaraa `else q <= q;` ei tarvita.

Siirtorekisteri syntyy liitoksesta: `tavu <= {bitti, tavu[7:1]}`
siirtää kaikkia bittejä yhden alaspäin ja tuo uuden bitin ylös.
Seuraava sarja–rinnakkaismuunnin kokoaa kahdeksan bittiä tavuksi ja
ilmoittaa yhden jakson pulssilla, kun tavu on valmis:

```{.systemverilog tiedosto="esimerkit/05-sarjamuunnin.sv" osa="siirtorekisteri"}
```

`valmis` on pulssi: sen oletusarvo 0 sijoitetaan joka jaksolla, ja
ehto nostaa sen vain yhdeksi jaksoksi. Sama oletussijoitusten malli
kuin `always_comb`-lohkossa toimii myös kellotetuissa lohkoissa.
Tällöin oletuksen puuttuminen ei kuitenkaan tuota salpaa, vaan
rekisteri yksinkertaisesti pitää arvonsa.

Vertailu `laskuri == 3'd7` käyttää laskurin vanhaa arvoa, koska kaikki
oikeat puolet luetaan ennen päivitystä. Kun kahdeksas bitti tulee,
laskuri on 7, ja `valmis` nousee samalla reunalla, kun viimeinen bitti
siirtyy paikalleen.

Alla oleva kaavio on piirretty testipenkin simulaatiosta (testipenkki
lähettää tavun A5 vähiten merkitsevä bitti ensin). Jokainen bitti
tulee rekisterin yläpäähän ja valuu jakso jaksolta alaspäin, ja
`valmis` on ylhäällä täsmälleen sen jakson, jolla `tavu` on valmis.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/05-sarjamuunnin.json" otsikko="Sarja–rinnakkaismuunnin vastaanottaa tavun A5"}
```

## Reunantunnistus

Signaalin muutos tunnistetaan vertaamalla sitä yhden jakson viivästettyyn
kopioonsa. Nouseva reuna on `signaali & ~edellinen`. Tämä on
kellotetun suunnittelun tapa reagoida tapahtumaan. Herkkyyslistaan ei
koskaan kirjoiteta muuta signaalia kuin kello ja nollaus.

```{.systemverilog tiedosto="esimerkit/05-sarjamuunnin.sv" osa="reuna"}
```

Testipenkki lähettää kaksi tavua bitti kerrallaan ja laskee
bittivirran nousevat reunat:

```{.tuloste tiedosto="esimerkit/05-sarjamuunnin.odotettu"}
```

## Estävä sijoitus kellotetussa lohkossa

Yleisin aloittelijan virhe on estävä sijoitus `=` kiikuissa. Estävä
sijoitus päivittää muuttujan heti, joten seuraava rivi näkee jo uuden
arvon. Kahden kiikun viivelinja romahtaa yhdeksi kiikuksi, ja
simuloinnin tulos voi riippua siitä, missä järjestyksessä simulaattori
suorittaa eri lohkot. Verilator hylkää estävän sijoituksen
`always_ff`-lohkossa (`BLKSEQ`):

```{.systemverilog tiedosto="esimerkit/05-estava.ei-kaanny.sv"}
```

```{.tuloste tiedosto="esimerkit/05-estava.odotettu"}
```

Korjatussa versiossa `vaihe2` saa `d`:n arvon kahden reunan kuluttua.
Virheellisessä versiossa se saisi sen jo ensimmäisellä reunalla. Alla
molemmat on simuloitu samalla syötteellä (lint-virhe on ohitettu
kaaviota varten): `oikea` seuraa syötettä kahden jakson ja `estava`
yhden jakson viiveellä.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/05-estava.json" otsikko="Viivelinja ei-estävillä (oikea) ja estävillä (estava) sijoituksilla"}
```

## Simulointisemantiikka lyhyesti

Simulaattori käsittelee jokaisen aika-askeleen alueittain. Ensin
*aktiivisella alueella* suoritetaan herätetyt lohkot ja estävät
sijoitukset sekä lasketaan ei-estävien sijoitusten oikeat puolet.
Sitten *NBA-alueella* (nonblocking assignment) päivitetään
ei-estävien sijoitusten kohteet. Päivitykset voivat herättää uusia
`always_comb`-lohkoja, ja kierrosta jatketaan, kunnes mikään ei enää
muutu.

Testipenkin kannalta tämä tarkoittaa, että samalla kellon reunalla
tehty syötteen muutos kilpailee kiikkujen näytteistyksen kanssa.
Siksi esimerkkien testipenkit muuttavat syötteitä hetki reunan jälkeen
(`@(posedge clk); #1;`). Ammattimaiset testipenkit käyttävät samaan
tarkoitukseen kellotettuja lohkoja (`clocking block`), joita käsitellään
taidossa *Laitteiston verifiointi*.

## Ajoitus

Kiikku toimii oikein vain, jos sen syöte on vakaa *asetusajan* (setup)
ennen reunaa ja *pitoajan* (hold) reunan jälkeen. Alla olevassa
periaatekuvassa data saa muuttua vain ikkunoiden ulkopuolella:

```{.ajoituskaavio otsikko="Periaatekuva: asetus- ja pitoaika kellon nousevan reunan ympärillä"}
{"signal": [
  {"name": "clk", "wave": "0...1...0...1..."},
  {"name": "d", "wave": "x.=.....x.=.....",
   "data": ["vakaa", "seuraava"]},
  {"name": "ikkuna", "wave": "z.=.=.z...=.=.z.",
   "data": ["asetus", "pito", "asetus", "pito"]},
  {"name": "q", "wave": "=....=.......=..",
   "data": ["", "vakaa", "seuraava"]}
], "config": {"hscale": 0.7}}
```

Kahden kiikun välisen kombinaatiologiikan viive ja kiikun oma viive
määräävät pienimmän kellojakson: lähtevän kiikun viiveen, logiikan
viiveen ja vastaanottavan kiikun asetusajan on mahduttava yhteen
jaksoon. Pisin tällainen polku on *kriittinen polku*.

```{.dot otsikko="Rekisteri–logiikka–rekisteri-polku ja sen viiveet"}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.9;
  r1 [shape=box, label="kiikku\nD   Q"];
  l  [shape=ellipse, label="kombinaatio-\nlogiikka"];
  r2 [shape=box, label="kiikku\nD   Q"];
  r1 -> l [label="kiikun viive"];
  l -> r2 [label="logiikan viive\n+ asetusaika"];
}
```

Synteesi- ja sijoittelutyökalun ajoitusanalyysi kertoo, riittääkö
jakso, ja RTL-suunnittelija vaikuttaa tulokseen päättämällä, kuinka
paljon logiikkaa rekisterien väliin tulee (luku 7). Pitoaikaa
suunnittelija ei yleensä korjaa käsin: työkalu lisää viivettä liian
nopeille poluille.

## Käytännössä

- **Kaksi sääntöä, ei poikkeuksia.** Kellotetussa lohkossa käytetään
  `<=`, kombinatorisessa `=`. Sääntö tunnetaan Clifford Cummingsin
  artikkelista *Nonblocking Assignments in Verilog Synthesis*, ja
  se poistaa koko simulointikilpailujen luokan.
- **Yksi signaali, yksi lohko.** Jokainen rekisteri sijoitetaan vain
  yhdessä `always_ff`-lohkossa. Toisiinsa liittyvät rekisterit voi
  koota samaan lohkoon, mutta kahdesta lohkosta ajettu rekisteri ei
  ole synteesikelpoinen.
- **Pulssi oletussijoituksella.** Yhden jakson ilmoitukset (valmis,
  virhe, keskeytyspyyntö) kirjoitetaan mallilla `x <= 1'b0;` lohkon
  alussa ja `x <= 1'b1;` ehdossa. Kuluttaja voi luottaa siihen, että
  pulssi kestää täsmälleen yhden jakson.
- **Reunantunnistus kellotettuna.** Tapahtumaan reagoidaan
  vertaamalla signaalia sen viivästettyyn kopioon, ei lisäämällä
  signaalia herkkyyslistaan. Jälkimmäinen tekisi signaalista kellon.
  Asynkroninen syöte tahdistetaan ensin (luku 10).
- **Rekisteröi ulostulot.** Moduulin ulostulo suoraan kiikusta on
  vakaa koko jakson, eikä siinä näy logiikan piikkejä. Se myös
  katkaisee ajoituspolun moduulien välillä, mikä helpottaa
  ajoitusanalyysiä ja uudelleenkäyttöä.

## Itsearviointi

- Osaat kuvata rekisterin, jolla on asynkroninen nollaus ja sallinta.
- Osaat selittää ei-estävän sijoituksen kaksivaiheisen semantiikan ja
  sen, miksi `a <= b; b <= a;` vaihtaa arvot.
- Osaat rakentaa siirtorekisterin liitoksella ja reunantunnistimen
  viivästetyllä kopiolla.
- Osaat tunnistaa estävän sijoituksen kellotetussa lohkossa ja kertoa,
  mitä siitä seuraa.
- Osaat selittää, miksi testipenkki muuttaa syötteitä vasta reunan
  jälkeen.

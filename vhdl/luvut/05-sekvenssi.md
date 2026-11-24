# Sekvenssilogiikka, signaalit ja muuttujat

Sekvenssilogiikassa on muisti: kiikut tallentavat arvon kellon
reunalla. Tämä luku näyttää VHDL:n kellotetun prosessin mallit ja
selittää simulointisemantiikan, joka erottaa signaalin ja muuttujan.
Ero on VHDL:n tärkein yksittäinen käsite, ja suurin osa
aloittelijan virheistä johtuu siitä. Synkronisen suunnittelun
periaatteet, ajoitus ja nollausstrategiat käsitellään taidossa
*RTL-suunnittelu SystemVerilogilla* (luvut 5 ja 9).

## Kellotettu prosessi

Kiikku kuvataan prosessilla, jonka herkkyyslistassa on kello ja
jonka koko sisältö on ehdon `rising_edge(clk)` sisällä. Esimerkiksi
luvun 7 PWM-lohkon vapaasti pyörivä laskuri synkronisella
nollauksella:

```{.vhdl tiedosto="esimerkit/07-pwm.vhd" osa="laskenta"}
```

Jokaisesta prosessissa sijoitetusta signaalista tulee rekisteri.
Kun mikään ehto ei sijoita signaalia, rekisteri pitää arvonsa;
kellotetussa prosessissa puuttuva sijoitus ei siis tuota salpaa vaan
sallinnan. `rising_edge` tarkistaa, että kello todella nousi
nollasta ykköseen. Vanhaa muotoa `clk'event and clk = '1'` ei enää
tarvita.

*Synkroninen nollaus* on tavallinen ehto kellon sisällä. Esimerkiksi
AMD:n (Xilinx) FPGA-ohjeet suosittelevat sitä, ja luvun 10
vertailuesimerkkiä lukuun ottamatta tämän tutoriaalin esimerkit
käyttävät sitä. *Asynkroninen nollaus* kirjoitetaan
herkkyyslistaan ja ennen kellon ehtoa (luku 10). FPGA:ssa signaalin
alkuarvo, kuten `signal tila : tila_t := LEPO;`, ladataan kiikkuun
konfiguroinnissa, joten pelkkä alkuarvo riittää monelle
rekisterille. ASIC-piirissä alkuarvoja ei ole, ja jokainen ohjaava
rekisteri tarvitsee nollauksen.

## Esimerkki: kvadratuurikooderi

Kiertoanturi antaa kaksi neliöaaltoa A ja B, joiden vaihe-ero kertoo
suunnan. Dekooderi tahdistaa piirin ulkopuolelta tulevat signaalit,
vertaa nykyistä tilaa edelliseen ja laskee askeleita:

```{.vhdl tiedosto="esimerkit/05-kvadratuuri.vhd" osa="kooderi"}
```

Tahdistin on kaksi kiikkua peräkkäin. Se suojaa metastabiilisuudelta,
kun asynkroninen signaali näytteistetään (ks. *RTL-suunnittelu*,
kellotusalueiden ylitys). Siirtorekisteri syntyy liitoksesta
`a_tahd(0) & a`. Lausekkeen `ab_ed & ab` tyyppi ei ole yksiselitteinen,
koska liitos voisi tuottaa minkä tahansa vektorityypin. *Tarkennettu
lauseke* `std_logic_vector'(...)` kertoo kääntäjälle tyypin, jotta
`case` voi tarkistaa valinnat.

Testipenkki pyörittää anturia kolme kierrosta eteen ja kaksi askelta
taakse:

```{.vhdl tiedosto="esimerkit/05-kvadratuuri.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/05-kvadratuuri.odotettu"}
```

Alla oleva kaavio on piirretty saman simulaation aaltomuodoista,
yksi sarake askelta kohden. Eteenpäin pyöriessä A johtaa B:tä
neljänneksen jaksolla, ja jokainen reuna kummassa tahansa kanavassa on
yksi askel. Lopussa järjestys kääntyy, B johtaa, ja asento pienenee.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/05-kvadratuuri.json" otsikko="Kvadratuurikanavat ja dekoodattu asento, yksi sarake askelta kohden"}
```

Kello luodaan rinnakkaisella sijoituksella `clk <= not clk after
JAKSO / 2 when ajossa;`. Kun testi asettaa `ajossa`-signaalin
epätodeksi, kello pysähtyy, tapahtumat loppuvat ja simulointi päättyy
itsestään. Toinen tapa on `std.env.finish` (luku 9).

## Simulointisemantiikka: deltasyklit

VHDL-simulaattori toimii tapahtumista. Signaaliin sijoittaminen ei
muuta signaalia heti, vaan *ajastaa* sille uuden arvon. Simulointi
etenee näin:

1. Herätetyt prosessit suoritetaan, kunnes kukin pysähtyy
   (`wait` tai herkkyyslistan loppu). Prosessit näkevät signaalien
   vanhat arvot koko suorituksen ajan.
2. Kaikki ajastetut signaalit päivitetään yhtä aikaa.
3. Jos jokin signaali muuttui, siitä riippuvat prosessit herätetään,
   ja palataan kohtaan 1 samalla simulointiajan hetkellä.

```{.dot otsikko="Simulointikierros: deltasyklit toistuvat samalla hetkellä, kunnes mikään ei muutu"}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.3;
  aika [label="aika etenee seuraavaan tapahtumaan"];
  suoritus [label="herätetyt prosessit suoritetaan (vanhat arvot)"];
  paivitys [label="ajastetut signaalit päivitetään yhtä aikaa"];
  muuttui [label="muuttuiko jokin?", shape=diamond];
  aika -> suoritus -> paivitys -> muuttui;
  muuttui -> suoritus [label=" kyllä: uusi deltasykli"];
  muuttui -> aika [label=" ei"];
}
```

Yksi kierros on *deltasykli*. Samalla simulointihetkellä voi olla monta
deltasykliä, ja aika etenee vasta, kun mikään ei enää muutu. Tämä
takaa, että kaikki kiikut näytteistävät reunalla tulonsa ennen kuin
yksikään päivittyy, eikä prosessien suoritusjärjestys vaikuta
tulokseen. VHDL:ssä ei siksi ole Verilogin estävän ja ei-estävän
sijoituksen kilpailutilanteita, mutta deltasykleillä on omat
sudenkuoppansa, jotka esitellään alla.

## Signaali ja muuttuja

| Ominaisuus | Signaali `s <= x;` | Muuttuja `v := x;` |
|---------------------|-----------------------|-----------------------|
| Missä esitellään | arkkitehtuurissa, paketissa, porttina | prosessissa tai aliohjelmassa |
| Milloin arvo muuttuu | deltasyklin lopussa | heti |
| Näkyvyys | kaikille prosesseille | vain omalle prosessille |
| Laitteistossa | johto tai rekisteri | välitulos (johto) tai rekisteri |
| Aaltomuodoissa | aina | yleensä ei |

Muuttuja on oikea työkalu välituloksiin, jotka lasketaan ja käytetään
saman prosessin sisällä. Fletcher-16-tarkistussummassa toinen summa
kasvaa ensimmäisen summan *uuden* arvon verran. Muuttuja antaa uuden
arvon käyttöön heti:

```{.vhdl tiedosto="esimerkit/05-fletcher.vhd" osa="fletcher"}
```

```{.tuloste tiedosto="esimerkit/05-fletcher.odotettu"}
```

Jos sama kirjoitetaan pelkillä signaaleilla, toinen summa lukee
ensimmäisen summan vanhan arvon:

```{.vhdl tiedosto="esimerkit/05-signaali.kaatuu.vhd" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/05-signaali.virhe"}
```

Kumpikin versio on synteesikelpoinen, ja molemmat tuottavat laitteiston,
mutta eri laitteiston: signaaliversiossa summa1:n rekisterin lähtö
kytkeytyy summa2:n summaimeen, muuttujaversiossa summa1:n summaimen
lähtö. Simulaattori näyttää tarkalleen saman kuin piiri, joten virhe
on suunnittelun, ei työkalun.

Muuttuja kellotetussa prosessissa voi myös tuottaa rekisterin: jos
muuttujaa luetaan ennen kuin siihen sijoitetaan, sen on muistettava
arvonsa edelliseltä reunalta. Tämä on sallittua mutta vaikealukuista,
ja rekisteri ei näy aaltomuodoissa. Hyvä sääntö: muuttujaan
sijoitetaan aina ennen lukemista, ja rekisterit ovat signaaleja.

## Deltasyklit ja kellot

Kellon kopio sijoituksella `clk_b <= clk` näyttää harmittomalta
uudelleennimeämiseltä, mutta se viivästää kelloa yhden deltasyklin.
Ensimmäinen kiikku ehtii päivittyä ennen kuin toisen kiikun kello
nousee, ja data ohittaa yhden vaiheen:

```{.vhdl tiedosto="esimerkit/05-deltakello.kaatuu.vhd" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/05-deltakello.virhe"}
```

Laitteistossa viivelinja toimisi, koska johdon viive on paljon kiikun
viivettä lyhyempi. Simulointi ja laitteisto eroavat, ja virhe on
erityisen hankala, kun kello kulkee hierarkian läpi porttien ja
sijoitusten kautta. Sääntö: kelloon ei tehdä sijoituksia eikä
logiikkaa. Kello kulkee portista porttiin sellaisenaan, ja kellojen
jakaminen ja portittaminen tehdään valmistajan kellopuskureilla tai
sallintasignaaleilla.

Testipenkissä deltasyklit ovat hyödyllisiä. Kun testipenkki sijoittaa
tulon heti `wait until rising_edge(clk)` -lauseen jälkeen, testattava
kiikku näkee samalla reunalla vielä vanhan arvon, joten tulo vaihtuu
"reunan jälkeen" ilman erillistä viivettä. Sama mekanismi yllättää,
jos testipenkki lukee signaalin heti sijoituksen jälkeen: `tarve <=
'1'; if tarve = '1'` näkee vielä vanhan arvon.

## Käytännössä

- **Kellotetun prosessin malli on vakio.** `process (clk)` ja `if
  rising_edge(clk)`, nollaus ensimmäisenä ehtona. Poikkeamat mallista
  vaikeuttavat synteesiä ja lukemista.
- **Rekisterit signaaleina, välitulokset muuttujina.** Muuttujaan
  sijoitetaan ennen lukemista. Jos tarvitaan rekisteri, se on signaali,
  jolloin se näkyy aaltomuodoissa ja muissa prosesseissa.
- **Ei sijoituksia kelloon.** Kello ei kulje logiikan tai
  `clk_b <= clk` -tyyppisten sijoitusten läpi. Kellon sallinta tehdään
  sallintasignaalilla.
- **Nollaa vain se, mikä tarvitsee nollauksen.** Ohjauslogiikka (tilat,
  laskurit, kelpo-liput) nollataan; datapolun rekisterit, kuten
  siirtorekisterit ja muistit, eivät yleensä tarvitse nollausta, ja
  ilman sitä ne mahtuvat FPGA:n tehokkaampiin resursseihin.
- **Asynkroniset tulot tahdistetaan.** Jokainen piirin ulkopuolelta tai
  toisesta kellotusalueesta tuleva bitti kulkee kahden kiikun
  tahdistimen läpi ennen käyttöä.

## Itsearviointi

- Osaat kirjoittaa kellotetun prosessin synkronisella nollauksella ja
  sallinnalla.
- Osaat selittää deltasyklin ja sen, miksi prosessi näkee
  sijoittamansa signaalin vanhan arvon.
- Osaat valita signaalin ja muuttujan välillä ja kertoa, millaista
  laitteistoa kumpikin tuottaa.
- Osaat kertoa, miksi kelloon ei tehdä sijoituksia.

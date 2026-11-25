# AXI4 ja AXI4-Lite

Arm julkaisi AMBA-väyläperheen (Advanced Microcontroller Bus
Architecture) vuonna 1996, ja siitä tuli järjestelmäpiirien
tosiasiallinen standardi myös muiden kuin Arm-ytimien piireissä.
Määrittelyt ovat ladattavissa maksutta Armin sivuilta. Perheen
tärkeimmät jäsenet ovat:

| Väylä | Käyttö | Ominaisuudet |
|-------|--------|--------------|
| AXI4 | suorittimet, muistit, kiihdyttimet | purskeet, tunnisteet, useita avoimia siirtoja |
| AXI4-Lite | rekisteriliitännät | yksi sana kerrallaan, ei purskeita eikä tunnisteita |
| AXI4-Stream | datavirrat (DSP, verkko) | ei osoitteita, vain VALID/READY ja data |
| AHB | vanhemmat ja pienet järjestelmät | liukuhihnoitettu jaettu väylä |
| APB | hitaat oheislaitteet | yksinkertainen, kaksivaiheinen |
| ACE, CHI | moniydinjärjestelmät | välimuistien koherenssi |

## Viisi kanavaa

AXI jakaa siirron viiteen itsenäiseen kanavaan:

| Kanava | Suunta | Sisältö |
|--------|--------|---------|
| AR (read address) | isäntä → orja | lukuosoite ja ominaisuudet |
| R (read data) | orja → isäntä | luettu data ja vastaus |
| AW (write address) | isäntä → orja | kirjoitusosoite |
| W (write data) | isäntä → orja | data ja tavukohtaiset luvat (WSTRB) |
| B (write response) | orja → isäntä | kirjoituksen vastaus |

Luku ja kirjoitus ovat erillään, joten ne voivat olla käynnissä yhtä
aikaa. Osoite ja data ovat erillään, joten osoitteen voi lähettää ennen
dataa ja orja voi aloittaa työnsä ennen kuin data on perillä.
Pikku-SoC:n väylätyypit kokoavat kanavien signaalit kahteen
rakenteeseen suunnan mukaan:

```{.systemverilog tiedosto="esimerkit/rtl/vaylat.sv" osa="axil"}
```

Vastauskoodeja on neljä: OKAY, EXOKAY (onnistunut atominen
yksinoikeussiirto, vain AXI4), SLVERR (orja tunnisti virheen, esimerkiksi
kirjoituksen vain luettavaan rekisteriin) ja DECERR (osoitteessa ei ole
orjaa; tyypillisesti kytkimen oletusorjan vastaus).

## Kättely

Jokaisella kanavalla on sama kättely: lähettäjä nostaa VALID-signaalin,
kun sisältö on voimassa, ja vastaanottaja nostaa READY-signaalin, kun
se voi ottaa sen vastaan. Siirto tapahtuu sillä kellojaksolla, jolla
molemmat ovat ylhäällä.

```{.ajoituskaavio otsikko="Lukusiirto: osoitteen kättely jaksolla 4, data siirtyy jaksolla 5"}
{"signal": [
  {"name": "ACLK", "wave": "P...."},
  {"name": "ARVALID", "wave": "01..0"},
  {"name": "ARADDR", "wave": "x=..x", "data": ["A"]},
  {"name": "ARREADY", "wave": "0..10"},
  {"name": "RVALID", "wave": "0...1"},
  {"name": "RREADY", "wave": "1...."}
]}
```

Kaaviossa jakso 1 on vasemmalla. Osoite pysyy samana, kunnes kättely
tapahtuu jaksolla 4, jolla sekä `ARVALID` että `ARREADY` ovat ylhäällä.

Määrittelyn tärkeimmät säännöt ovat:

1. **Kun VALID on noussut, se pysyy ylhäällä kättelyyn asti, ja
   sisältö pysyy samana.** Lähettäjä ei saa perua eikä muuttaa
   tarjoustaan.
2. **VALID ei saa odottaa READYä.** Lähettäjän on nostettava VALID
   READYstä riippumatta. Vastaanottaja saa odottaa VALIDia ennen READYn
   nostamista. Jos molemmat odottaisivat toisiaan, väylä lukkiutuisi.
3. **Kanavien väliset riippuvuudet on rajattu.** Esimerkiksi orja saa
   odottaa sekä AW- että W-kanavaa ennen kuin se hyväksyy kumpaakaan,
   mutta isäntä ei saa odottaa AWREADYä ennen W-kanavan
   tarjoamista. Lukuvastaus ei saa tulla ennen osoitteen kättelyä.

Sääntö 2 on yleisin integrointivirheiden lähde: kahden lohkon, joista
kumpikin on erikseen oikein testattu, yhdistelmä lukkiutuu, jos
toinen odottaa READYä ja toinen VALIDia. Luvun 12 protokollatarkistin
valvoo sääntöä 1.

## Isäntä: ytimen silta

`silta.sv` muuntaa ytimen pyynnön yhdeksi AXI4-Lite-siirroksi.
Kanavien signaalit muodostetaan sillan tilasta:

```{.systemverilog tiedosto="esimerkit/rtl/silta.sv" osa="kanavat"}
```

Kirjoituksessa AW- ja W-kanava tarjotaan samalla jaksolla, ja kumpikin
pidetään ylhäällä oman kättelynsä loppuun (`osoite_tehty`, `w_tehty`).
Orja saa hyväksyä ne eri jaksoilla. `RREADY` ja `BREADY` ovat ylhäällä
koko odotuksen ajan, koska silta voi aina ottaa vastauksen vastaan.

## Orja: RAM

RAM-orja vastaa lukuun seuraavalla kellojaksolla ja hyväksyy
kirjoituksen, kun sekä osoite että data ovat tarjolla:

```{.systemverilog tiedosto="esimerkit/rtl/ram.sv" osa="orja"}
```

Lukemisessa `ARREADY` on ylhäällä aina, kun edellinen vastaus on
kuitattu. Näin orja ei ota uutta pyyntöä, jota se ei voi palvella.
Kirjoituksessa `WSTRB` valitsee kirjoitettavat tavut; ytimen tavu- ja
puolisanakirjoitukset (`sb`, `sh`) eivät siksi tarvitse
luku–muokkaus–kirjoitus-sykliä.

## Täysi AXI4: purskeet ja tunnisteet

AXI4-Lite on AXI4:n osajoukko: jokainen siirto on yksi enintään
väylän levyinen sana. Täydessä AXI4:ssä on lisäksi:

- **Purskeet.** Yksi osoitesiirto kuljettaa jopa 256 datasiirtoa
  (`AxLEN` = siirtojen määrä − 1, `AxSIZE` = siirron koko). Purskeen
  tyyppi on INCR (kasvava osoite, tavallisin), WRAP (kiertävä,
  välimuistirivin täyttöön) tai FIXED (sama osoite, FIFO-rekisterille).
  Purske ei saa ylittää 4 KiB:n rajaa, jotta se ei koskaan osu kahteen
  orjaan. Viimeinen datasiirto merkitään `xLAST`-signaalilla.
- **Tunnisteet ja järjestys.** Jokaisella siirrolla on tunniste
  (`AxID`). Saman tunnisteen siirrot valmistuvat pyyntöjärjestyksessä;
  eri tunnisteiden siirrot saavat valmistua missä järjestyksessä
  tahansa. Hidas DRAM-luku ei siksi pysäytä nopeaa SRAM-lukua, jos
  niillä on eri tunnisteet.
- **Useita avoimia siirtoja.** Isäntä voi lähettää uusia osoitteita
  ennen kuin edelliset vastaukset ovat tulleet. Muistin viive
  piilotetaan putkittamalla pyyntöjä.
- **Ominaisuudet.** `AxCACHE` (välimuistitettavuus), `AxPROT`
  (etuoikeus, turvallisuus, käsky vai data), `AxLOCK` (yksinoikeus),
  `AxQOS` ja `AxREGION`.

Purskeet ovat syy, miksi suuret datasiirrot kannattaa tehdä AXI4:llä:
yksi osoite ja kättely kuljettavat esimerkiksi 64 tavun välimuistirivin,
kun AXI4-Lite tarvitsisi 16 erillistä siirtoa. Luvun 10 DMA käyttää
AXI4-Liteä, ja sen kopiointinopeudessa näkyy tämä hinta.

## Purske mitattuna

Pikku-SoC:n kytkin on AXI4-Lite, joten pursketta kokeillaan sen
ulkopuolella omassa testipenkissään. `rtl/ram_purske.sv` on AXI4-orja,
joka tukee INCR-purskeita. Osoitekättely tallentaa aloitusindeksin ja
siirtojen määrän, ja sen jälkeen orja laskee osoitteen itse:

```{.systemverilog tiedosto="esimerkit/rtl/ram_purske.sv" osa="purske"}
```

Lukukanavalla orja antaa sanan joka jaksolla niin kauan kuin isäntä
pitää `RREADY`n ylhäällä, ja `RLAST` merkitsee viimeisen.
Kirjoituksessa vastaus `B` tulee kerran koko purskeesta, ei jokaisesta
sanasta. Testipenkin isäntä on kaksi tehtävää:

```{.systemverilog tiedosto="esimerkit/tb/tb_purske.sv" osa="isanta"}
```

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/purske.json" otsikko="Neljän sanan purske simulaatiosta: luku (AR, neljä R-siirtoa, RLAST) ja kirjoitus (AW, neljä W-siirtoa, WLAST, yksi B). Arvot on näytetty sellaisina kuin ne ovat kellon nousevalla reunalla."}
```

Purskeessa on kaksi sääntöä, joita AXI4-Litessä ei ole, ja ne
kannattaa antaa tarkistimen valvottaviksi (luku 12):

```{.systemverilog tiedosto="esimerkit/rtl/axi_purske_tarkistin.sv" osa="saannot"}
```

Testipenkki kopioi samat 64 sanaa kahdesti: ensin sana kerrallaan
(`AxLEN` = 0, kuten AXI4-Lite) ja sitten 16 sanan purskeina. Lopuksi se
tekee kaksi tahallista virhettä:

```{.tuloste tiedosto="esimerkit/odotettu/purske.odotettu"}
```

Sana kerrallaan kopio vie viisi jaksoa sanaa kohden: lukuosoite ja
data sekä kirjoitusosoite, data ja vastaus. Purskeina sama kopio vie
140 jaksoa eli 2,2 jaksoa sanaa kohden, koska osoite ja vastaus
maksetaan kerran 16 sanasta. Loput erosta ihanteeseen (yksi jakso
sanaa kohden) tulee siitä, että tämä isäntä lukee purskeen kokonaan
ennen kuin alkaa kirjoittaa. Oikea DMA lukisi ja kirjoittaisi yhtä
aikaa FIFOn läpi. Tarkistin huomasi molemmat virheet: purskeen, joka
alkaa osoitteesta `0xFF8` ja jatkuu sivun rajan yli, sekä `WLAST`in,
joka nousi toisessa siirrossa eikä neljännessä.

Mittaus on lohkotason tulos, ei Pikku-SoC:n: purskeiden tuominen
järjestelmään vaatisi kytkimen, joka välittää purskeen kokonaisena, ja
sillan AXI4-Lite-orjille. Se on integroinnin tavallinen kompromissi:
nopea väylä muisteille ja kevyt väylä rekistereille (luku 5).

## Käytännössä

- **AXI4-Lite rekistereille, AXI4 datalle.** Rekisteriliitännät
  eivät hyödy purskeista, ja AXI4-Lite-orja on murto-osa täyden
  AXI4-orjan logiikasta. Sillan (AXI4 → AXI4-Lite) hinta maksetaan
  kerran.
- **Rekisteröi kättelysignaalit.** Pitkä kombinatorinen polku
  `READY`-signaalista lähettäjän kautta takaisin rikkoo ajoituksen.
  *Rekisteriviipale* (register slice, skid buffer) katkaisee polut
  ja lisää vain jakson viivettä.
- **VALID ei koskaan odota READYä.** Säännön voi tarkistaa jokaisesta
  lohkosta ennen integrointia: tarkistin, joka pitää READYn alhaalla
  satunnaisia jaksoja, paljastaa virheen nopeasti.
- **Vastaa aina.** Jokaiseen hyväksyttyyn pyyntöön on vastattava,
  myös virheeseen. Orja, joka ei vastaa tuntemattomaan osoitteeseen,
  jumittaa isännän ja usein koko kytkimen.
- **Hyödynnä avoimia siirtoja.** Suorituskyky tulee siitä, että
  isäntä lähettää seuraavan pyynnön ennen edellisen vastausta.
  Pikku-SoC:n ydin ja silta eivät tee niin, mikä on yksi syy luvun 3
  pitkään rekisteriviiveeseen.

## Itsearviointi

- Osaat nimetä AXI:n viisi kanavaa ja kertoa niiden suunnan ja
  sisällön.
- Osaat selittää VALID/READY-kättelyn ja sen kolme sääntöä sekä
  sen, miksi VALID ei saa odottaa READYä.
- Osaat toteuttaa AXI4-Lite-isännän ja -orjan, joka hyväksyy AW- ja
  W-kanavan eri jaksoilla.
- Osaat kertoa, mitä purskeet, tunnisteet ja avoimet siirrot tuovat
  täyteen AXI4:ään ja milloin niitä tarvitaan.
- Osaat lukea INCR-purskeen ajoituskaaviosta ja laskea, montako jaksoa
  sama kopio vie sana kerrallaan ja purskeina.
- Osaat nimetä purskeen kaksi lisäsääntöä (4 KiB:n raja ja `xLAST`) ja
  tarkistaa ne simulaatiossa.
- Osaat valita oikean vastauskoodin (OKAY, SLVERR, DECERR)
  virhetilanteeseen.

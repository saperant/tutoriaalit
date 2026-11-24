# Resurssit ja ajoitus FPGA:lla

Edellisissä luvuissa rakenteita verrattiin paperilla: kertojien määrä,
rekisterit, kriittinen polku. Tässä luvussa ne syntetisoidaan Lattice
iCE40 UP5K -piirille ja luetaan, mitä työkalut sanovat. Vuo on sama
kuin taidossa *FPGA-toteutus*: Yosys syntetisoi, nextpnr sijoittelee ja
reitittää, ja raporteista poimitaan solujen määrät ja suurin
kellotaajuus.

## Vuo

Jokainen suunnitelma ajetaan samalla skriptillä. Yosysin
`synth_ice40 -dsp` käyttää piirin DSP-lohkoja; ilman valitsinta
kertojat rakennetaan logiikkasoluista:

```{.bash tiedosto="esimerkit/tyokalut/vuo.sh" osa="vuo"}
```

Make-kohde tiivistää raportit riveiksi ja vertaa niitä tallennettuihin.
Solujen tarkka määrä ja kellotaajuus vaihtelevat työkalujen versioiden
ja sijoittelun siemenen mukaan, joten ne tarkistetaan raja-arvoja
vasten. DSP-lohkojen ja kantoketjun solujen määrät tulostetaan
sellaisinaan, koska ne ovat synteesin deterministinen tulos:

```{.makefile tiedosto="esimerkit/Makefile" osa="synteesi"}
```

```{.tuloste tiedosto="esimerkit/raportit/fir-suora.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/fir-suora-lut.odotettu"}
```

UP5K-kotelossa on 39 nastaa. FIR-suotimien liitännät mahtuvat
niihin, mutta CORDIC (49 sisääntulobittiä ja 58 ulostulobittiä) ja
NCO (24-bittinen taajuussana) eivät. Niille on synteesikääre, joka
siirtää sisääntulot sarjamuotoisesti ja taittaa ulostulot XOR:lla
kahdeksaan nastaan. Jokainen bitti vaikuttaa ulostuloon, joten synteesi
ei voi poistaa logiikkaa:

```{.systemverilog tiedosto="esimerkit/synteesi/kaare.sv" osa="kaare"}
```

## DSP-lohkot

UP5K-piirissä on kahdeksan SB_MAC16-lohkoa. Kukin laskee 16 × 16
-bitin kertolaskun ja voi kerätä tuloja 32-bittiseen kertymään.
Suurempien piirien DSP-lohkot ovat leveämpiä ja monipuolisempia:

| Piiri | Lohko | Kertoja | Esisummain | Kertymä | Kaskadi |
|------------------------------|-----------------------|----------------|------------|---------|----------------|
| Lattice iCE40 UltraPlus | SB_MAC16 | 16 × 16 | ei | 32 | vain kantoketju |
| Lattice ECP5 | MULT18X18D + ALU54B | 18 × 18 | ei | 54 | kyllä |
| AMD 7-sarja | DSP48E1 | 25 × 18 | kyllä | 48 | kyllä |
| AMD UltraScale | DSP48E2 | 27 × 18 | kyllä | 48 | kyllä |
| Intel Cyclone V, Arria 10 | Variable Precision | 18 × 19, 27 × 27 | kyllä | 64 | kyllä |

Lohkon leveys ratkaisee usein sanaleveydet. 16 × 16 -kertojalla
Q1.15-kertoimet ja 12-bittiset näytteet mahtuvat yhteen lohkoon; 17
bitin kerroin veisi kaksi tai neljä lohkoa. Siksi luvun 2
sanaleveydet kannattaa valita vasta, kun kohdepiiri tiedetään.

## Tulokset

Taulukko kokoaa tämän tutoriaalin kirjoittajan ajon (Yosys 0.33,
nextpnr-ice40 0.6, siemen 1). Sarake "DSP" on synteesi DSP-lohkoilla
ja sarake "LUT" ilman niitä:

| Lohko | SB_MAC16 | Soluja, DSP | Soluja, LUT | Fmax, LUT |
|-------|----------|-------------|-------------|-----------|
| FIR suora | 8 | 477 | 1591 | 23 MHz |
| FIR transponoitu | 4 | 270 | 821 | 37 MHz |
| FIR symmetrinen | 4 | 318 | 979 | 27 MHz |
| FIR jaettu | 1 | 247 | 825 | 16 MHz |
| polyfaasi, 16 kerrointa / 4 | 4 | 445 | – | – |
| IIR-lohko | 5 | 319 | 1323 | 13 MHz |
| CIC, N = 3, R = 8 | – | – | 258 | 46 MHz |
| CORDIC iteratiivinen (kääre) | – | – | 642 | 30 MHz |
| CORDIC liukuhihna (kääre) | – | – | 3334 | 52 MHz |
| NCO (kääre), 1 lohko-RAM | – | – | 115 | 73 MHz |

Taulukosta näkyy viisi asiaa, jotka eivät näy RTL:stä suoraan.

**Transponoitu muoto käytti vain neljä DSP-lohkoa.** Transponoidussa
muodossa jokainen kertoja saa saman sisääntulon $x[n]$. Koska
kertoimet ovat symmetriset, tulot $h_k x$ ja $h_{N-1-k} x$ ovat samat,
ja Yosys yhdisti ne. Symmetria hyödynnettiin siis ilmaiseksi. Suorassa
muodossa kertojat saavat eri näytteet, eikä yhdistäminen ole
mahdollista ilman esisummainta.

**Vakiokertoimet ovat halpoja logiikkasoluina.** LUT-sarakkeessa
jaettu suodin on lähes yhtä suuri kuin transponoitu, vaikka siinä on
yksi kertoja kahdeksan sijasta. Rinnakkaisten rakenteiden kertojat
kertovat *vakiolla*, ja vakiolla kertominen on muutama siirto ja
yhteenlasku: kertoimen 14133 binääriesityksessä on yhdeksän ykköstä,
ja etumerkillisinä numeroina (CSD-esitys) se on seitsemän osittaisen
tulon summa.
Jaetun suotimen kertoja kertoo *muuttujalla*, joten se on yleinen
12 × 16 -kertoja, ja sen eteen tulevat lisäksi kerroin- ja
näytemultiplekserit. Sama selittää jaetun suotimen hitauden
LUT-toteutuksena.

**IIR-lohko on hitain.** Takaisinkytkentä kulkee kertojan, viiden
termin summan ja saturoinnin läpi yhdessä jaksossa (luku 4).
Kellotaajuus on noin puolet FIR-suotimien taajuudesta, eikä
liukuhihnoitus auta.

**Liukuhihnoitettu CORDIC on viisi kertaa suurempi ja kaksi kertaa
nopeampi.** Se ottaa uuden syötteen joka jaksolla; iteratiivinen
tarvitsee 17 jaksoa. Läpäisy kasvaa siis lähes 30-kertaiseksi
viisinkertaisella pinta-alalla.

**NCO on pieni, koska taulukko on lohko-RAMissa.** 256 × 11 bitin
taulukko logiikkasoluina veisi arviolta parisataa solua; lohko-RAMissa
se ei vie yhtään.

## DSP-lohkojen ajoitus

Taulukossa ei ole kellotaajuutta DSP-toteutuksille. Syy näkyy, kun
IIR-lohkon DSP-version kriittinen polku avataan nextpnr:n raportista:
polku kulkee kättelylogiikan läpi, ei kertojien. nextpnr-ice40 ei
mallinna SB_MAC16-lohkon sisäisiä viiveitä, joten DSP-lohkon läpi
kulkevat polut puuttuvat ajoitusanalyysistä, ja raportoitu Fmax (yli
80 MHz) on liian optimistinen. Siksi kellotaajuus luetaan
LUT-toteutuksesta, jonka kaikki polut on mallinnettu, ja DSP-versiosta
luetaan vain resurssit.

Tämä on avoimen työkaluketjun tunnettu rajoitus, ja vastaavia on
kaupallisissakin työkaluissa. Opetus on yleinen: ajoitusraportin
lukuun ei pidä luottaa katsomatta, mitä kriittinen polku sisältää. Jos
polku ei kulje sen logiikan läpi, jonka tiedät hitaimmaksi, raportti
ei näe sitä. Oikealla piirillä asia ratkaistaan mittaamalla tai
käyttämällä DSP-lohkon omia rekistereitä, jolloin lohkon sisäinen
viive ei ole rekisterien välissä.

## Mitä luvuista seuraa

- 64 kertoimen suora FIR ei mahdu UP5K-piiriin (8 DSP-lohkoa), mutta
  aikamultipleksoituna se mahtuu yhteen lohkoon, jos kellojaksoja on
  näytettä kohden vähintään 64.
- Neljännen asteen IIR-suodin kahtena DF1-lohkona tarvitsee 10
  kertojaa eikä mahdu DSP-lohkoihin. Yksi jaettu lohko tai
  LUT-kertojat ratkaisevat sen.
- Symmetrinen tai transponoitu muoto puolittaa DSP-lohkot
  lineaarivaiheiselle suotimelle.
- Pinta-alan ja läpäisyn suhde on CORDICissa lähes lineaarinen.
  Valinta tehdään näytetaajuuden perusteella, ei pinta-alan.

## Käytännössä

- Syntetisoi vaihtoehtoiset rakenteet varhain ja lue raportit. Luvut
  ovat usein yllättäviä: vakiokertoimet, symmetria ja muistien
  tunnistus muuttavat kustannuksia.
- Lue kriittinen polku, ei vain Fmax-lukua. Tarkista, että polku
  kulkee sen logiikan läpi, jonka odotat olevan hitain.
- Tarkista raporteista DSP-lohkojen ja lohko-RAMien määrä. Jos
  muisti tai kertoja ei tunnistunut, RTL on kirjoitettava uudelleen
  työkalun tunnistamaan muotoon.
- Tarkista nastamäärä ennen kuin luet tuloksia; tarvittaessa käytä
  kääreitä, jotka eivät salli synteesin poistaa logiikkaa.
- Testaa raportteja raja-arvoja vasten. Tarkat luvut kuuluvat
  raporttitiedostoihin, rajat testeihin.

## Itsearviointi

- Osaat syntetisoida lohkon DSP-lohkoilla ja ilman niitä ja lukea
  raporteista solujen, DSP-lohkojen ja muistien määrän sekä Fmax:n.
- Osaat selittää, miksi transponoitu symmetrinen FIR voi käyttää
  puolet kertojista ja miksi vakiokertoimet ovat logiikkasoluina
  halpoja.
- Osaat arvioida, mahtuuko suodin piirin DSP-lohkoihin, ja valita
  rakenteen sen mukaan.
- Osaat tunnistaa, milloin ajoitusraportin kriittinen polku ei
  sisällä todellista hitainta polkua.

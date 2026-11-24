# Resurssien ja ajoituksen optimointi

FPGA-suunnitelmalla on kolme mittaa: kuinka paljon piiriä se vie,
kuinka nopealla kellolla se toimii ja kuinka paljon työtä se tekee
jaksossa. Ne vaihtuvat toisiinsa. Luku näyttää vaihtokaupan yhdellä
esimerkillä ja kokoaa keinot, joilla kutakin mittaa parannetaan.

## Läpäisy, kello ja pinta-ala

Suunnitelman **läpäisy** (throughput) on

$$\text{läpäisy} = \frac{f_{\text{kello}}}{\text{jaksoja tulosta kohden}}$$

Samaan läpäisyyn pääsee kahdella tavalla: paljon rinnakkaista
laitteistoa hitaalla kellolla tai vähän laitteistoa, jota käytetään
monta kertaa nopealla kellolla. Ensimmäinen kuluttaa piiriä, toinen
vaatii lyhyitä polkuja. Kumpi on parempi, riippuu siitä, mikä
resurssi loppuu ensin.

## Esimerkki: FIR-suodin

Neljän kertoimen FIR-suodin laskee jokaiselle näytteelle neljä
kertolaskua ja summan. Kertoimet kirjoitetaan ajon aikana, joten
synteesi ei voi korvata kertojia vakiokertoimilla:

```{.systemverilog tiedosto="esimerkit/09-jakaminen/suodin.sv" osa="suodin"}
```

**Rinnakkainen** versio laskee kaikki neljä tuloa samalla jaksolla.
Se ottaa vastaan uuden näytteen joka jaksolla ja käyttää neljä
kertojaa:

```{.systemverilog tiedosto="esimerkit/09-jakaminen/suodin.sv" osa="rinnakkain"}
```

**Jaettu** versio käyttää yhtä kertojaa neljällä peräkkäisellä
jaksolla. Multiplekseri valitsee kullekin vaiheelle kertoimen ja
näytteen, ja summa kertyy rekisteriin. Uusi näyte otetaan vastaan
joka viidennellä jaksolla:

```{.systemverilog tiedosto="esimerkit/09-jakaminen/suodin.sv" osa="jaettu"}
```

Testipenkki ajaa molemmat versiot samoilla näytteillä ja vertaa
tuloksia. Jaettu versio ilmoittaa signaalilla `valmis`, milloin se voi
ottaa seuraavan näytteen:

```{.systemverilog tiedosto="esimerkit/09-jakaminen/testipenkki.sv" osa="nayte"}
```

```{.tuloste tiedosto="esimerkit/09-jakaminen.odotettu"}
```

Impulssi (1, 0, 0, 0) tuottaa kertoimet 3, 5, 7 ja 9, ja askel
(10, 10, 10, 10) niiden kertyvät summat. Kahdeksan näytettä vie 44
jaksoa: neljä jaksoa kertoimien kirjoittamiseen ja viisi jaksoa
näytettä kohden.

## Mitä jakaminen maksoi

```{.tuloste tiedosto="esimerkit/raportit/suodin-rinnakkain.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/suodin-jaettu.odotettu"}
```

| Versio | DSP | Logiikkasoluja | Fmax | Jaksoja näytteelle |
|--------|-----|----------------|------|--------------------|
| rinnakkain | 4 | 115 | (ks. teksti) | 1 |
| jaettu | 1 | 168 | 62,5 MHz | 5 |

Jakaminen säästi kolme DSP-lohkoa, mutta kaikki muu huononi:

- **Logiikkasoluja tarvittiin enemmän.** Multiplekseri, vaihelaskuri,
  ohjaus ja ylimääräinen näyterekisteri maksavat enemmän kuin kolme
  DSP-lohkoon piilotettua kertojaa säästävät logiikkasoluja.
- **Kello hidastui.** Kriittinen polku kulkee nyt multiplekserin ja
  kertojan kautta kertymärekisteriin. Rinnakkaisessa versiossa
  kertojien tulot tulevat suoraan rekistereistä.
- **Läpäisy putosi viidennekseen** samalla kellolla.

Rinnakkaisen version raportoitu Fmax on yli 200 MHz, mikä on liian
hyvää ollakseen totta: nextpnr ei mallinna DSP-lohkon sisäisiä polkuja
(luku 6), joten luku kertoo vain lohkon ympäristöstä. Todellinen raja
on DSP-lohkon datalehdessä.

Jakaminen kannattaa, kun jaettava resurssi on kallis ja niukka
verrattuna multiplekseriin ja ohjaukseen: DSP-lohkot ovat loppumassa,
tai jaettava lohko on suuri (jakaja, liukulukuyksikkö, kokonainen
suodinkaista). Jos piirissä on vapaita DSP-lohkoja ja läpäisyä
tarvitaan, rinnakkainen versio on parempi kaikilla mittareilla.

## Keinot mittareittain

| Tavoite | Keino | Hinta |
|---------|-------|-------|
| Vähemmän piiriä | resurssien jakaminen | läpäisy, ohjauslogiikka |
| | kapeammat bittileveydet | tarkkuus; laske tarvittava leveys |
| | vakiokertoimet siirroiksi ja summiksi | joustavuus |
| | taulukot ja puskurit lohko-RAMiin | latenssi (synkroninen luku) |
| Nopeampi kello | liukuhihnoitus (luku 6) | latenssi, rekisterit |
| | uudelleenajoitus (`synth_ice40 -retime`) | rekisterit, ennustettavuus |
| | DSP- ja kantologiikka aritmetiikalle | erikoislohkojen määrä |
| | rekisterin kopiointi suurelle tuulettuvuudelle | kiikut |
| Suurempi läpäisy | rinnakkaisuus | piiri |
| | liukuhihnoitus, uusi tulo joka jaksolla | latenssi |

Taulukon keinot ovat RTL-tason keinoja. Niitä suurempi vaikutus on
algoritmilla ja arkkitehtuurilla: suodin, jonka kertoimet ovat
symmetriset, tarvitsee vain puolet kertojista, ja algoritmi, joka ei
tarvitse jakolaskua, ei tarvitse jakajaa. Työkalun valinnat
(`-retime`, siemen, `--freq`) tulevat viimeisenä ja tuovat
prosentteja, eivät kertoimia.

## Synteesin oma jakaminen

Yosys jakaa resursseja myös itse. Komento `share` (osa
`synth_ice40`:aa) yhdistää operaatiot, jotka eivät koskaan ole
käytössä yhtä aikaa: jos `case`-lauseen eri haaroissa on kertolasku,
synteesi voi rakentaa yhden kertojan ja multiplekserin. Jakaminen
onnistuu vain, kun synteesi pystyy todistamaan haarojen
poissulkevuuden. Jaksojen yli tapahtuvaa jakamista, kuten tämän luvun
suotimessa, synteesi ei tee: se muuttaisi toiminnan ajoitusta.

## Teho

iCE40 on pienitehoinen piiri, ja FPGA:n teho riippuu ennen kaikkea
kellotaajuudesta ja kytkeytyvien signaalien määrästä. Samat keinot
kuin pinta-alan säästössä auttavat usein myös tehoon: vähemmän
logiikkaa kytkeytyy vähemmän. Lisäksi

- **sallinnat**: rekisteri, joka ei päivity, ei kuluta dynaamista
  tehoa;
- **hitaampi kello**: jos läpäisy riittää, matalampi taajuus säästää
  suoraan;
- **sammutettavat lohkot**: PLL, oskillaattorit ja SPRAM voidaan
  sammuttaa, kun niitä ei tarvita.

Valmistajien työkaluissa on tehoarvio, joka käyttää simulaation
aktiivisuustietoja samaan tapaan kuin ASIC-vuossa.

## Käytännössä

- **Selvitä, mikä resurssi loppuu.** DSP-lohkot, lohko-RAM, IO vai
  logiikkasolut. Optimoi niukkaa resurssia, älä kaikkia.
- **Laske läpäisy ennen arkkitehtuuria.** Montako tulosta sekunnissa
  tarvitaan ja millä kellolla: siitä seuraa, montako jaksoa tulosta
  kohden on varaa ja paljonko laitteistoa tarvitaan.
- **Mittaa, älä arvaa.** Jakaminen tai liukuhihnoitus voi kasvattaa
  solumäärää. Aja vuo molemmille versioille ja vertaa raportteja.
- **Arkkitehtuuri ensin, työkalun valinnat viimeisenä.** Algoritmin
  muutos tuo kertoimia, työkalun valinnat prosentteja.

## Itsearviointi

- Osaat laskea suunnitelman läpäisyn kellotaajuudesta ja jaksoista
  tulosta kohden.
- Osaat toteuttaa saman laskennan rinnakkaisena ja jaettuna ja
  vertailla niiden resurssit ja nopeuden raporteista.
- Osaat arvioida, milloin resurssien jakaminen kannattaa ja milloin se
  maksaa enemmän kuin säästää.
- Osaat valita keinon sen mukaan, onko tavoitteena pienempi pinta-ala,
  nopeampi kello vai suurempi läpäisy.

# Ydin ja ohjelmisto

Integroijan on tunnettava suoritinytimestä sen rajapinnat, ei sen
sisäistä toteutusta: mitä väyliä ydin käyttää, mistä se käynnistyy,
mitä keskeytyssignaaleja se ottaa vastaan ja millaista koodia sille
käännetään. Tämä luku käy läpi Pikku-SoC:n ytimen ulkoisen kuvan ja
ohjelmiston polun lähdekoodista RAMiin.

## Ytimen rajapinta

`ydin.sv` toteuttaa RISC-V:n perusjoukon RV32I, CSR-käskyt (Zicsr) ja
M-tilan ansat. Ydin on monivaiheinen: jokainen käsky haetaan, suoritetaan
ja tarvittaessa tehdään muistiviittaus, ennen kuin seuraava käsky
haetaan. Ratkaisu on hidas, mutta väyläliikenne on helppo seurata,
eikä ytimessä ole liukuhihnan riippuvuuksia, jotka eivät kuulu tämän
tutoriaalin aiheeseen (ks. *Tietokonearkkitehtuuri*).

Ytimen väylä on yksinkertainen pyyntö–valmis-liitäntä:

```{.systemverilog tiedosto="esimerkit/rtl/ydin.sv" osa="vayla"}
```

Sama väylä kuljettaa sekä käskyhaut että datan (von Neumann
-rakenne). Monissa ytimissä on erilliset käsky- ja dataväylät
(Harvard-rakenne), jolloin haku ja datan siirto voivat tapahtua yhtä
aikaa. Integroijalle ero näkyy kytkimen isäntien määränä.

Ytimen väylä ei ole standardiväylä, joten `silta.sv` muuntaa sen
AXI4-Liteksi (luku 4). Tämä on yleinen rakenne: ytimen sisäinen
liitäntä on optimoitu ytimen tarpeisiin, ja reunalla oleva sovitin
puhuu järjestelmän väylää. Esimerkiksi avoin PicoRV32-ydin tarjoaa
oman muistiliitäntänsä ja erilliset sovittimet AXI4-Litelle ja
Wishbonelle.

Ydin tarvitsee järjestelmältä lisäksi:

- **Nollausvektorin**: Pikku-SoC:ssa osoite 0.
- **Keskeytyssignaalit**: ajastinkeskeytys (MTIP) CLINTiltä ja ulkoinen
  keskeytys (MEIP) PLICiltä (luku 9).
- **Väylävirheen**: väylän virhevastaus muuttuu ytimessä poikkeukseksi
  (luku 12).

### Debug-liitäntä

Tuotantoytimellä on vielä yksi rajapinta, jota Pikku-SoC:n ytimessä ei
ole: debug. RISC-V:n debug-määrittelyssä piirin ulkopuolinen debuggeri
puhuu JTAG-nastojen kautta *siirtomoduulille* (DTM), joka välittää
rekisterilukuja ja -kirjoituksia *debug-moduulille* (DM). Debug-moduuli
on integroijan kytkettävä lohko, ja sillä on kolme liitäntää
järjestelmään:

- **Pysäytys- ja jatkopyynnöt ytimelle.** Pysäytetty ydin suorittaa
  debug-moduulin antamia käskyjä, joilla debuggeri lukee ja kirjoittaa
  rekistereitä.
- **Väyläisäntä (system bus access).** Debuggeri voi lukea ja
  kirjoittaa muistia ja oheislaitteita suoraan kytkimen kautta
  pysäyttämättä ydintä. Kytkimeen tulee siis yksi isäntä lisää.
- **Nollaus.** Debuggeri voi nollata järjestelmän mutta ei itseään,
  joten debug-logiikalla on oma nollausalueensa (luku 11).

Integroinnin kannalta tärkein seuraus on, että debuggeri on isäntä,
joka lukee rekistereitä silloinkin, kun ohjelmisto ei niitä lue.
Muistinäkymä, joka näyttää oheislaitteen rekisterit, lukee ne kaikki.
Jos lukemisella on sivuvaikutus (FIFOn tyhjeneminen, lipun nollaus),
debuggeri muuttaa järjestelmän tilaa pelkästään katsomalla. Tästä
syystä luku 8 suosittelee kuittausta kirjoittamalla (W1C) lukemisen
sijaan.

## Käännösketju

Ohjelmisto käännetään ristikääntäjällä, joka tuottaa koodia ytimen
käskykannalle:

```{.makefile tiedosto="esimerkit/Makefile" osa="kaannos"}
```

Valitsimet kertovat järjestelmästä paljon:

- `-march=rv32i_zicsr -mabi=ilp32` vastaa ytimen käskykantaa. Ydin ei
  osaa kerto- ja jakolaskukäskyjä (laajennus M), joten kääntäjä kutsuu
  jakolaskussa libgcc:n aliohjelmia, ja linkitykseen lisätään `-lgcc`.
  Väärä `-march` tuottaisi käskyjä, joita ydin pitää laittomina.
- `-ffreestanding -fno-builtin` kertoo, ettei käytössä ole
  käyttöjärjestelmää eikä C-kirjastoa. `-fno-tree-loop-distribute-patterns`
  estää kääntäjää muuttamasta silmukoita `memset`- ja `memcpy`-kutsuiksi
  silloin, kun niitä toteutetaan.
- `-nostdlib -nostartfiles -T sw/soc.ld` jättää pois kääntäjän oman
  käynnistyskoodin ja kirjastot ja käyttää omaa linkkeriskriptiä.

Linkitetty ELF-tiedosto muunnetaan muotoon, jonka testipenkki lataa
RAMiin `$readmemh`-funktiolla:

```{.makefile tiedosto="esimerkit/Makefile" osa="ohjelma"}
```

Valitsin `--verilog-data-width=4` tuottaa 32-bittisiä sanoja, joiden
osoitteet ovat sanaosoitteita, kuten RAMin taulukko `muisti[]` olettaa.
Oikeassa piirissä samassa kohdassa tuotettaisiin flash-muistiin
kirjoitettava kuva tai käynnistys-ROMin sisältö.

## Linkkeriskripti

Linkkeriskripti kertoo, missä muistit ovat ja mihin ohjelman osiot
sijoitetaan:

```{.text tiedosto="esimerkit/sw/soc.ld"}
```

Skriptin `MEMORY`-lohko on ohjelmiston näkemä muistikartta, ja sen on
vastattava laitteistoa. Jos RAMia kasvatetaan laitteistossa mutta ei
skriptissä, ohjelma ei käytä uutta muistia; jos skripti lupaa enemmän
kuin laitteisto antaa, pino osuu kartoittamattomaan osoitteeseen ja
ensimmäinen aliohjelmakutsu kaatuu väylävirheeseen.

## Käynnistyskoodi

Ennen `main`-funktiota tarvitaan muutama käsky, joita C:llä ei voi
kirjoittaa:

```{.gnuassembler tiedosto="esimerkit/sw/start.S" osa="start"}
```

Pino-osoitin asetetaan muistin loppuun, ansavektori (`mtvec`)
osoittamaan ansakäsittelijään ja `.bss`-osio nollataan, koska C:n
alustamattomat staattiset muuttujat ovat nollia. Kun `main` palaa, sen
paluuarvo välitetään funktiolle `lopeta`, joka kirjoittaa sen
SYSCONin LOPETA-rekisteriin; testipenkki päättää simulaation.
Mikrokontrollerin käynnistyskoodi tekee samat asiat ja lisäksi
kopioi alustetun datan flash-muistista RAMiin (*Mikrokontrollerit ja bare-metal-ohjelmointi*).

## Laiteajurit: muistiin kuvattu I/O

Ohjelmisto käyttää oheislaitteita lukemalla ja kirjoittamalla niiden
rekistereitä tavallisilla muistikäskyillä (memory-mapped I/O, MMIO).
Rekisterit kuvataan C:ssä rakenteena, jonka kentät ovat `volatile`:

```{.c tiedosto="esimerkit/sw/tuki.c" osa="uart"}
```

`volatile` kieltää kääntäjää poistamasta, yhdistämästä tai järjestämästä
uudelleen rekisteriviittauksia. Ilman sitä kääntäjä saisi lukea
TILA-rekisterin kerran ennen silmukkaa ja jäädä pyörimään ikuisesti,
koska sen näkökulmasta muistipaikka ei muutu silmukassa.

Rekisterikäyttö on kallista verrattuna muistiin. Tämän SoC:n ydin
mittaa sen itse `mcycle`-CSR:llä:

```{.c tiedosto="esimerkit/sw/kaynnistys.c" osa="jaksot"}
```

```{.tuloste tiedosto="esimerkit/odotettu/kaynnistys.odotettu"}
```

Yksi CLINTin rekisterin luku kesti 21 kellojaksoa: ytimen
monivaiheisuus, AXI-kytkin, APB-sillan kaksi vaihetta ja paluu samaa
reittiä. Nopeassakin piirissä oheislaitteen rekisterin luku kestää
kymmeniä tai satoja jaksoja, koska se ei voi tulla välimuistista.

## Käytännössä

- **Rakenne, ei osoitelaskuja.** `UART->TILA` on luettavampi ja
  tyyppiturvallisempi kuin `*(volatile uint32_t *)(0x10000004)`.
  Kenttien siirrot kannattaa varmistaa `_Static_assert`-tarkistuksilla,
  kuten generoidut otsakkeet tekevät (luku 8).
- **`volatile` ei ole synkronointia.** Se pakottaa kääntäjän tekemään
  viittaukset, mutta ei estä suoritinta tai väylää järjestämästä niitä
  uudelleen. Suorittimissa, joiden muistimalli on heikko, tarvitaan
  muistiesteitä (RISC-V:ssä `fence`, Armissa `dmb`/`dsb`) esimerkiksi
  DMA:n käynnistyksen ja puskurin kirjoittamisen välissä.
- **Laitteiston ja ohjelmiston muistikartta samasta lähteestä.**
  Linkkeriskripti, C-otsake ja RTL:n osoiteparametrit kannattaa
  generoida yhdestä kuvauksesta. Jos se ei ole mahdollista, testi, joka
  lukee jokaisen laitteen tunnisterekisterin, paljastaa ristiriidat
  heti.
- **Ytimen versiot ja laajennukset ovat sopimus.** Kääntäjän `-march`
  on kirjoitettava ytimen todellisten ominaisuuksien mukaan. RISC-V:n
  `misa`-CSR kertoo laajennukset ajonaikana, ja käynnistyskoodi voi
  tarkistaa sen.

## Itsearviointi

- Osaat kertoa, mitä liitäntöjä debug-moduuli tarvitsee järjestelmään
  ja miksi debuggeri tekee lukemisen sivuvaikutuksista ongelman.
- Osaat kuvata ytimen ulkoiset liitännät: väylät, nollausvektorin,
  keskeytykset ja virhevasteen.
- Osaat valita ristikääntäjän `-march`- ja `-mabi`-valitsimet ytimen
  ominaisuuksien mukaan ja kertoa, miksi RV32I tarvitsee libgcc:n.
- Osaat lukea linkkeriskriptin ja kertoa, miten se liittyy
  muistikarttaan.
- Osaat kirjoittaa käynnistyskoodin, joka asettaa pinon, ansavektorin
  ja nollaa `.bss`-osion.
- Osaat kirjoittaa MMIO-ajurin `volatile`-rakenteella ja perustella,
  miksi `volatile` tarvitaan.

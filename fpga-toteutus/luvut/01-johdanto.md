# Johdanto {.runko-johdanto}

FPGA (field-programmable gate array) on piiri, jonka logiikka määrätään
vasta käyttöpaikalla. Piirissä on tuhansia samanlaisia logiikkasoluja,
muisteja ja kertojia sekä ohjelmoitava reititysverkko. Konfiguraatio,
*bittivirta*, kertoo jokaiselle solulle, mitä se laskee, ja jokaiselle
kytkimelle, mitkä johtimet yhdistetään. Sama piiri voi olla tänään
UART-ohjain ja huomenna videokooderi.

Tämä tutoriaali vie RTL-kuvauksen FPGA:lle: synteesi, sijoittelu,
reititys, ajoitusanalyysi ja bittivirta.

## Esitiedot ja rajaus

Esitietona on taito *RTL-suunnittelu SystemVerilogilla*. Synteesin ja
staattisen ajoitusanalyysin periaatteet standardisoluille käsitellään
taidossa *ASIC-toteutus*; täällä keskitytään siihen, mikä on FPGA:lla
toisin.

## FPGA, ASIC vai mikrokontrolleri

| | Mikrokontrolleri | FPGA | ASIC |
|--|--|--|--|
| Logiikka | ohjelma suorittimella | konfiguroitava laitteisto | kiinteä laitteisto |
| Rinnakkaisuus | yksi tai muutama ydin | kaikki logiikka yhtä aikaa | kaikki logiikka yhtä aikaa |
| Kellotaajuus | 10–500 MHz | 50–500 MHz | 1–5 GHz |
| Kehityskustannus | pieni | pieni–kohtalainen | miljoonia euroja |
| Kappalehinta | euroja | euroja–tuhansia euroja | senttejä suurissa erissä |
| Muutos kentällä | ohjelmistopäivitys | uusi bittivirta | ei mahdollinen |

FPGA kannattaa, kun tarvitaan tarkkaa ajoitusta, suurta rinnakkaisuutta
tai omia rajapintoja, mutta sarja on liian pieni ASICille: radiot ja
signaalinkäsittely, videon käsittely, verkkolaitteet, testilaitteet ja
ASIC-prototyypit. FPGA on myös ASIC-suunnittelijan työkalu: sama RTL
ajetaan FPGA-prototyypillä oikeilla nopeuksilla ennen piirin
valmistusta.

## Piiri ja työkalut

Esimerkit toteutetaan Latticen **iCE40 UltraPlus** -piirille (iCE40UP5K,
kotelo SG48). Se on pieni ja edullinen: 5 280 logiikkasolua, 30
lohko-RAMia, 8 DSP-lohkoa, 128 kt yksiporttista RAMia, yksi PLL ja
sisäiset oskillaattorit. Sen etu opetuksessa on avoin työkaluketju:

| Vaihe | Työkalu | Tuotos |
|-------|---------|--------|
| Simulointi | Verilator | toiminnan tarkistus |
| Synteesi | Yosys (`synth_ice40`) | piirin primitiiveistä koottu netlista (JSON) |
| Sijoittelu ja reititys | nextpnr (`nextpnr-ice40`) | sijoiteltu piiri (ASC) ja ajoitusraportti |
| Bittivirta | IceStorm (`icepack`) | bittivirta (BIN) |
| Lataus | `iceprog` | konfiguroitu piiri |

Kaikki työkalut ovat Ubuntun paketeissa (`yosys`, `nextpnr-ice40`,
`fpga-icestorm`, `verilator`), ja kehityskontissa ne ovat valmiina.
Valmistajien omat työkalut (AMD Vivado, Intel Quartus, Lattice Radiant)
tekevät samat vaiheet suljetusti ja suuremmille piireille; käsitteet ja
raporttien lukeminen siirtyvät niihin suoraan.

Esimerkkien kortti on **iCEBreaker**, avoin kehityskortti, jossa on
iCE40UP5K, 12 MHz:n kide, ledejä, painikkeita ja USB-sarjaportti.
Korttia ei tarvita tutoriaalin seuraamiseen. Kaikki esimerkit
simuloidaan ja viedään bittivirraksi asti ilman korttia, ja luvussa 10
kortti korvataan mallilla: suunnitelma ajetaan simuloidulla kortilla,
jossa on painikkeet, ledit, sarjaportti ja näyttö. Oikea kortti on
valinnainen viimeinen askel (luku 11).

## Ensimmäinen suunnitelma

Ledin vilkutus on FPGA:n "hei maailma": se todistaa, että kello,
synteesi, nastojen kytkentä ja lataus toimivat.

```{.systemverilog tiedosto="esimerkit/01-vilkku/vilkku.sv" osa="vilkku"}
```

Laskurilla ei ole nollausta. FPGA:n kiikut saavat alkuarvonsa
konfiguroinnissa, joten alustus `= '0` päätyy bittivirtaan. ASICissa
samanlainen kuvaus jättäisi laskurin tuntemattomaan tilaan, ja
nollaus olisi pakollinen.

Ennen synteesiä suunnitelma simuloidaan. Testipenkki käyttää kolmen
bitin laskuria, jotta ledi vaihtaa tilaa neljän jakson välein:

```{.systemverilog tiedosto="esimerkit/01-vilkku/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/01-vilkku.odotettu"}
```

Nastat kerrotaan sijoittelulle rajoitetiedostossa (PCF, physical
constraints file):

```{tiedosto="esimerkit/01-vilkku/icebreaker.pcf"}
```

Luvussa 3 käydään läpi, miten tästä syntyy bittivirta, ja mitä
raporttiin kirjoitetaan:

```{.tuloste tiedosto="esimerkit/raportit/vilkku.odotettu"}
```

24-bittinen laskuri vie 28 logiikkasolua (alle 1 % piiristä), ja piiri
toimisi noin 80 MHz:n kellolla, vaikka kortin kello on 12 MHz.
Bittivirran koko ei riipu suunnitelmasta: se kattaa aina koko piirin.

## Mitä ajetaan ja miten

| Esimerkkien osa | Työkalu | Tarkistus |
|---|---|---|
| Toiminta | Verilator | testipenkki tulostaa tulokset, verrataan odotettuun |
| Resurssit | Yosys, nextpnr | solutyyppien määrät ja raja-arvot, verrataan odotettuun |
| Ajoitus | nextpnr | saavutettu Fmax yli raja-arvon |
| Bittivirta | icepack | syntyy ja on oikean kokoinen |
| Simuloitu kortti | Verilator, C++-malli | ledit, sarjaportti ja näytön kehykset, verrataan odotettuun |
| Bittivirta takaisin | icebox_vlog, Verilator | bittivirrasta palautettu piiri toimii kuten RTL |
| Kortilla ajo | iceprog | kuvataan tekstinä, ei testata |

Tarkat solumäärät ja maksimitaajuudet vaihtelevat työkaluversioittain.
Siksi testit vertaavat niitä väljiin raja-arvoihin ja tulostavat tarkat
luvut vain raporttitiedostoihin. Tekstissä mainitut luvut ovat Ubuntu
24.04:n versioista (Yosys 0.33, nextpnr 0.6).

Raporttien luvut on myös piirretty kuviksi: resurssien käyttö,
kriittisen polun viiveet ja sijoittelu. Kuvat tuottaa skripti
`kuvat/piirra.py` samoista raporteista, jotka testit tarkistavat
(`make kuvat`), joten ne voi piirtää uudelleen omasta suunnitelmasta.

## Tutoriaalin rakenne

Luku 2 esittelee FPGA:n rakennuspalikat ja luku 3 työkaluketjun.
Luvut 4–6 käsittelevät synteesiä, sijoittelua ja ajoitusta: miten
kuvaus muuttuu resursseiksi ja kuinka nopea siitä tulee. Luvut 7 ja 8
koskevat kelloja, nollauksia ja kellotusalueita, luku 9 resurssien ja
nopeuden vaihtokauppaa. Luvussa 10 kokonainen suunnitelma ajetaan
simuloidulla kortilla ja sen bittivirta todennetaan ilman laitteistoa,
ja luku 11 käsittelee testausta oikealla kortilla. Viimeinen luku
kokoaa nyrkkisäännöt ja lähteet.

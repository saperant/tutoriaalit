# Johdanto {.runko-johdanto}

Järjestelmäpiiri (system on chip, SoC) on piiri, johon on koottu
kokonainen tietokone: yksi tai useampi suoritin, muistit, väylät,
oheislaitteet, kello- ja nollauslogiikka sekä usein erikoistuneita
kiihdyttimiä. Puhelimen sovellussuoritin, mikrokontrolleri,
verkkokortin ohjainpiiri ja autojen ohjausyksiköiden piirit ovat
kaikki järjestelmäpiirejä.

Harva SoC suunnitellaan tyhjästä. Tyypillisesti suurin osa lohkoista
on valmiita: suoritinydin ostetaan tai otetaan avoimesta lähteestä,
muistiohjain ja liitännät (USB, PCIe, Ethernet) hankitaan IP-lohkoina,
ja oma suunnittelu keskittyy tuotteen erottaviin osiin. Siksi
*integrointi* on oma ammattitaitonsa: lohkot on kytkettävä yhteen
oikeilla väylillä, osoitteistettava, saatettava keskeyttämään
suoritinta, kellotettava ja nollattava oikein, ja koko kokonaisuuden on
toimittava ohjelmiston kanssa.

Tämä tutoriaali opettaa integroinnin kokoamalla pienen mutta
täydellisen järjestelmäpiirin. Esitietona on taito *RTL-suunnittelu
SystemVerilogilla*: moduulit, kellotettu logiikka, tilakoneet, FIFOt ja
kellotusalueiden ylitys oletetaan tutuiksi, eikä niitä kerrata. Taito
*Tietokonearkkitehtuuri* (käskykanta, datapolku, muistihierarkia,
keskeytykset) on hyödyllinen tausta; tarvittavat asiat kerrotaan
lyhyesti.

## Pikku-SoC

Esimerkkien järjestelmäpiiri, *Pikku-SoC*, koostuu seuraavista
lohkoista:

| Lohko | Tiedosto | Tehtävä |
|-------|----------|---------|
| Ydin | `rtl/ydin.sv` | RV32I-suoritin, CSR:t ja ansat |
| Silta | `rtl/silta.sv` | ytimen väylä → AXI4-Lite |
| DMA | `rtl/dma.sv` | muistista muistiin -kopiointi |
| Kytkin | `rtl/kytkin.sv` | AXI4-Lite, 2 isäntää, 2 orjaa |
| RAM | `rtl/ram.sv` | 16 KiB ohjelmalle ja datalle |
| APB-silta | `rtl/apb_silta.sv` | hitaiden oheislaitteiden väylä |
| UART | `rtl/uart.sv` | sarjaportin lähetin |
| SYSCON | `gen/syscon_regs.sv` | tunniste ja simulaation lopetus |
| GPIO | `rtl/gpio.sv` | tulot, lähdöt ja reunakeskeytys |
| CLINT | `rtl/clint.sv` | ajastin ja ajastinkeskeytys |
| PLIC | `rtl/plic.sv` | ulkoisten keskeytysten ohjain |

Lohkot on kirjoitettu tätä tutoriaalia varten, ja ne ovat tarkoituksella
pieniä: ydin on monivaiheinen ilman liukuhihnaa, kytkin välittää yhden
siirron kerrallaan ja oheislaitteissa on vain välttämättömät
rekisterit. Rakenne ja rajapinnat ovat kuitenkin samat kuin oikeissa
piireissä, ja jokaisen luvun *Käytännössä*-osio kertoo, miten
tuotantolaatuinen ratkaisu eroaa.

Ensimmäinen ohjelma tunnistaa järjestelmän: se lukee SYSCONin
tunnisterekisterin ja ytimen `misa`-CSR:n ja tulostaa ne UARTiin:

```{.c tiedosto="esimerkit/sw/kaynnistys.c" osa="tunnistus"}
```

Ohjelma käännetään RISC-V-ristikääntäjällä, ladataan simuloidun SoC:n
RAMiin ja ajetaan Verilatorilla. Testipenkin UART-vastaanotin purkaa
sarjalinjan bitit merkeiksi:

```{.tuloste tiedosto="esimerkit/odotettu/kaynnistys.odotettu"}
```

Kaikki rivit kulkivat koko järjestelmän läpi: ydin haki käskyt RAMista
AXI-kytkimen kautta, kirjoitti merkit UARTin rekisteriin APB-sillan
kautta, ja UART lähetti ne bitti kerrallaan sarjalinjalle.

## Työkalut

| Tehtävä | Tässä | Muita |
|---------|-------|-------|
| RTL-simulointi | Verilator 5.020 | Questa, VCS, Xcelium |
| Lohkotestit (luku 13) | cocotb 2.1 ja Icarus Verilog 12 | Verilator ≥ 5.036, kaupalliset simulaattorit |
| Ristikääntäjä | GCC 13 (`riscv64-unknown-elf`) | LLVM/Clang |
| Rekisterigeneraattori | oma (`gen/rekisterit.py`) | PeakRDL, Kactus2 |
| Integrointi | käsin SystemVerilogilla | IP-XACT-työkalut, FuseSoC |

Ubuntu 24.04:n paketti `gcc-riscv64-unknown-elf` sisältää
RV32-kirjastot, vaikka nimessä on 64: valitsimet
`-march=rv32i_zicsr -mabi=ilp32` tuottavat 32-bittistä koodia.
Kehityskontti (`.devcontainer/soc-integraatio`) sisältää kaikki
työkalut.

## Esimerkkien ajaminen

Esimerkit ovat yksi kokonaisuus, jonka `esimerkit/Makefile` rakentaa ja
testaa:

```text
make -C esimerkit            # kaikki tarkistukset ja simulaatiot
make -C esimerkit aja-dma    # yksi ohjelma simulaatiossa
make -C esimerkit generoi    # rekisterilohkot kuvauksista
make -C esimerkit siivoa     # poistaa build/-hakemiston
```

`make` tekee seuraavat:

1. tarkistaa, että generoidut rekisterilohkot vastaavat kuvauksiaan
   (luku 8);
2. kääntää ohjelmat `sw/*.c` ja muuntaa ne `$readmemh`-muotoon;
3. kääntää SoC:n ja testipenkin Verilatorilla (`-Wall --assert`:
   jokainen varoitus on virhe ja väittämät ovat päällä);
4. ajaa jokaisen ohjelman ja vertaa UARTin tulosteen odotettuun;
5. ajaa protokollatarkistimen ja tehoalueen omat testipenkit.

Simulaatio on täysin deterministinen: sama ohjelma tuottaa joka kerta
saman tulosteen, ja myös kellojaksojen määrät ovat samat. Siksi
tulosteessa voi näyttää esimerkiksi keskeytysten järjestyksen ja
DMA-siirron keston.

## Lukuohje

Luvut 2–3 esittelevät järjestelmän kokonaisuutena: lohkot,
muistikartan ja sen, miten ohjelmisto pääsee laitteistoon käsiksi.
Luvut 4–6 käsittelevät väyliä ja kytkentää, luvut 7–8 valmiiden ja
generoitujen lohkojen käyttöä ja luvut 9–11 järjestelmän palveluja:
keskeytyksiä, DMA:ta sekä kello-, nollaus- ja tehoalueita. Luku 12
kokoaa virhetilanteet ja niiden tarkistamisen.

Kokenut lukija voi lukea kunkin luvun lopussa olevan itsearvioinnin ja
ohittaa luvun, jos hallitsee sen väitteet. Pikaoppaassa on
muistikartta, väylien kättelysäännöt ja ansojen CSR:t tiiviisti.

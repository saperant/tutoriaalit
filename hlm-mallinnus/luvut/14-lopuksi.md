# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Valitse karkein taso, joka vastaa kysymykseen.** Algoritmimalli
   bittileveyksille, LT ohjelmistolle, AT väylän suorituskyvylle, RTL
   toteutukselle. Tarkempi malli on hitaampi ja valmistuu myöhemmin.
2. **Prosessit puhuvat kanavien kautta.** Jaettu muuttuja kahden
   prosessin välillä on kilpailutilanne, vaikka simulaattori on
   yksisäikeinen.
3. **Tila ensin, tapahtuma sitten.** Tapahtumalla ei ole muistia.
   Odota `while (!ehto) wait(e);` -muodossa.
4. **Nimeä kaikki.** Moduulit, portit, kanavat ja socketit saavat
   nimen, jotta virheilmoitukset ja lokit kertovat paikan.
5. **Bittitarkka malli on määrittely.** Leveydet, pyöristys ja
   saturaatio kirjataan ja tarkistetaan pahimman tapauksen herätteellä.
6. **Kohde annotoi, aloittaja odottaa.** `b_transport` lisää viiveen
   eikä kutsu `wait()`-funktiota. Ajasta riippuva kohde käyttää aikaa
   `sc_time_stamp() + viive`.
7. **Tarkista generic payloadin kaikki kentät.** Tukematon ominaisuus
   palauttaa virhetilan, ei jää huomiotta.
8. **Kvantti on kompromissi.** Suuri kvantti on nopea ja epätarkka.
   Synkronoi ennen jaettua tilaa, ja tarkista, ettei tulos riipu
   kvantista.
9. **DMI muistille, debug-liikenne työkaluille.** DMI:n viiveet lisätään
   aloittajan aikaan; debug-liikenteellä ei ole aikaa eikä
   sivuvaikutuksia.
10. **Keskeytys on signaali, ja sen lukija synkronoi.** Laite ajoittaa
    linjan reunat annotoidun ajan mukaan. Prosessori synkronoi
    odottaessaan (`wfi`) ja ennen kuin lukee linjan, jonka se on juuri
    kuitannut; kvantti pidetään lyhintä keskeytysjaksoa pienempänä.
11. **Vertaa RTL:ää malliin bitti bitiltä.** Jono viiveen yli,
    suunnatut ja satunnaiset herätteet kiinteällä siemenellä.

## Vianetsintä oireen mukaan

| Oire | Todennäköinen syy | Korjaus |
|----------------------------------------|------------------------------|------------------------------|
| `undefined reference to sc_api_version_...` | eri C++-standardi kuin kirjastolla | sama `-std` kuin kirjaston käännöksessä |
| `'sc_fixed' does not name a type` | `SC_INCLUDE_FX` puuttuu | `-DSC_INCLUDE_FX` ennen `<systemc>`ia |
| `complete binding failed: port not bound` | portti kytkemättä | kytke portti tai käytä valinnaista porttia |
| `wait() is only allowed in SC_THREADs` | `wait()` metodissa | säie tai `next_trigger()` |
| `cannot have more than one driver` | kaksi kirjoittajaa signaalille | yksi ajuri tai erillinen valitsin |
| simulointi jumittuu, aika ei etene | säie ilman `wait()`-kutsua | odotus silmukkaan |
| simulointi päättyy liian aikaisin | tapahtumat loppuivat | aikaraja `sc_start`ille tai kello |
| tulos muuttuu, kun moduulien järjestys muuttuu | prosessit jakavat muuttujan tai välitön ilmoitus | kanava tai delta-ilmoitus |
| alkuarvoissa välkettä ajassa 0 | alustusajo | `dont_initialize()` kellotetuille prosesseille |
| viive katoaa pieneksi | aikatarkkuus liian karkea | `sc_set_time_resolution` ensimmäisenä |
| ajastin tai tila näyttää väärää aikaa | kohde käyttää pelkkää `sc_time_stamp()`ia | annotoitu aika |
| ohjelmisto toimii vain pienellä kvantilla | odotussilmukka tai ajoitusoletus | synkronointi ennen jaettua tilaa |
| sama keskeytys käsitellään kahdesti | linja luetaan ennen kuin kuittaus on ehtinyt simulaatioaikaan | synkronointi käsittelijästä palatessa |
| ohjelmiston kello jätättää suurella kvantilla | tikkejä katoaa: kvantti ylittää keskeytysjakson | pienempi kvantti tai `wfi` |
| AT-malli liian nopea | poissulkemissääntö rikki | protokollatarkistin |
| muisti sotkeutuu satunnaisesti | vanhentunut DMI-osoitin | mitätöinti ja aluetarkistus |
| RTL ja malli eroavat yhdellä LSB:llä | pyöristys- tai kerroinero | impulssivaste ja määrittely |

## Mallinnuksen työnkulku

Tyypillisessä piiriprojektissa mallit syntyvät tässä järjestyksessä:

1. Algoritmimalli (C++, Python tai MATLAB) todentaa toiminnon.
2. Bittitarkka malli kiinnittää leveydet ja toimii myöhemmin RTL:n
   referenssinä.
3. LT-virtuaaliprototyyppi kootaan valmiista ISS:stä ja oheislaitemalleista
   keskeytyslinjoineen; ohjelmistokehitys alkaa.
4. AT-mallit tutkivat väylän, muistiohjaimen ja kiihdyttimien
   suorituskyvyn ja mitoittavat puskurit.
5. RTL toteutetaan käsin tai HLS:llä mallista, ja sitä verrataan
   bittitarkkaan malliin.
6. Virtuaaliprototyyppiin vaihdetaan RTL-lohkoja transaktorien kautta, ja
   sama ohjelmisto ajetaan FPGA-prototyypillä ja lopulta piirillä.

## Jatkotaidot

- *Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen*: malleilla tehtävä suorituskyvyn ja
  tehonkulutuksen analyysi, kuormien karakterisointi, parametrien
  läpikäynti ja laitteisto–ohjelmisto-jako.
- *Korkean tason synteesi*: C++-mallin muuntaminen RTL:ksi,
  silmukoiden liukuhihnoitus ja muistirajapinnat; bittitarkat tyypit ja
  `SC_CTHREAD`-tyyli ovat HLS-työkalujen syötettä.
- *SoC-integraatio*: oikeat väylät (AXI, AHB, APB), osoitekartat ja
  niiden generointi yhdestä lähteestä sekä keskeytysten viive
  kellojakson tarkkuudella RTL:stä mitattuna.
- *Mikrokontrollerit ja bare-metal-ohjelmointi*: keskeytykset,
  käsittelijät ja kriittiset osiot ohjelmoijan näkökulmasta.
- *Laitteiston verifiointi*: referenssimallit UVM- ja cocotb-testipenkeissä,
  kattavuus ja satunnaistettu heräte.

## Lähteet

Standardit ja referenssitoteutus:

- *IEEE 1666-2023, Standard for Standard SystemC Language Reference
  Manual.* SystemC:n ja TLM-2.0:n määrittely; saatavilla maksutta IEEE
  GET -ohjelman kautta. <https://standards.ieee.org/ieee/1666/>.
- Accellera Systems Initiative: *SystemC*-referenssitoteutus, TLM-2.0,
  esimerkit ja base protocol checker.
  <https://github.com/accellera-official/systemc>.
- Accellera: *SystemC Configuration, Control and Inspection (CCI)*.
  Mallien parametrointi ja tarkastelu.
  <https://www.accellera.org/downloads/standards/systemc>.
- *The RISC-V Instruction Set Manual, Volume I: Unprivileged ISA* ja
  *Volume II: Privileged Architecture*. Käskymuodot ja RV32I sekä
  konetilan rekisterit, keskeytykset, `mret` ja `wfi`.
  <https://riscv.org/specifications/>.
- Verilator, käyttöopas, erityisesti luku *Connecting to SystemC*.
  <https://verilator.org/guide/latest/>.

Kirjat:

- Black, D. C., Donovan, J., Bunton, B. ja Keist, A.: *SystemC: From
  the Ground Up*, 2. painos. Springer, 2010.
- Grötker, T., Liao, S., Martin, G. ja Swan, S.: *System Design with
  SystemC*. Kluwer, 2002.
- Ghenassia, F. (toim.): *Transaction-Level Modeling with SystemC: TLM
  Concepts and Applications for Embedded Systems*. Springer, 2005.
- Leupers, R. ja Temam, O. (toim.): *Processor and System-on-Chip
  Simulation*. Springer, 2010.

Avoimet mallit ja työkalut:

- QEMU, nopea prosessori- ja järjestelmäemulaattori.
  <https://www.qemu.org/>.
- Spike, RISC-V:n referenssi-ISS.
  <https://github.com/riscv-software-src/riscv-isa-sim>.
- GTKWave, VCD-aaltomuotojen katselu. <https://gtkwave.sourceforge.net/>.

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
-lisenssillä (CC BY-SA 4.0). Esimerkkikoodit ovat saman lisenssin
alaisia.

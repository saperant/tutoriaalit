# Lopuksi {.runko-kaytannot .runko-lahteet}

## Nyrkkisäännöt

- **Yksi lähde, kaikki muu tuotetaan.** RTL, C-otsake, dokumentaatio,
  UVM-malli, IP-XACT, SVD ja laitepuu syntyvät samasta kuvauksesta, eikä
  tuotettuja tiedostoja muokata käsin.
- **SystemRDL rekisterien lähteeksi.** Se kuvaa myös laitteiston
  käyttäytymisen, jota IP-XACT ja SVD eivät kanna.
- **Kuvaa käyttäytyminen, ei vain bittejä.** W1C, lukemalla nollautuva
  kenttä, kertapulssi, laskuri ja keskeytys sallintoineen kuuluvat
  kuvaukseen.
- **Osoitteet ja taulukon askeleet näkyviin.** Lisäys kuvaukseen ei
  silloin siirrä vanhoja osoitteita.
- **Kääntäjä on tarkistin.** Aja se jokaisessa muutoksessa ja käytä sen
  Python-rajapintaa omiin generaattoreihin ja tarkistuksiin.
- **Vakaat nimet.** Hierarkiaan perustuvat tyyppinimet pitävät
  tuotetut nimet samoina, kun kuvausta muutetaan.
- **Testaa tuotteet kuluttajan työkalulla.** RTL simuloidaan, otsake
  käännetään ajurissa, SVD luetaan kuten debuggeri sen lukee, laitepuu
  käännetään `dtc`:llä ja muunnokset testataan edestakaisin.
- **CI tarkistaa tahdin.** Tallennetut tuotteet verrataan tuoreisiin
  ennen simulointia, ja generaattorien versiot on lukittu.
- **Rekisterikartta on rajapinta.** Se versioidaan, ja muutokset
  luokitellaan yhteensopiviin ja yhteensopimattomiin.

## Työkaluista

PeakRDL on hyvä lähtökohta, koska sen liitännäisrajapinta antaa saman
mallin omille generaattoreille, ja sen tuotokset ovat luettavia.
Muita avoimia vaihtoehtoja ovat OpenTitanin `regtool` (Hjson-kuvaukset)
ja Kactus2 (IP-XACT-editori ja integraatio). Kaupallisissa ympäristöissä
rekisterityökalut ovat usein osa IP-katalogia ja integraatiotyökalua,
ja ne lukevat ja kirjoittavat SystemRDL:ää ja IP-XACT:ia.

Työkalua valittaessa kannattaa kokeilla samaa kuin tässä taidossa:
kuvaus yhdelle oikealle lohkolle, kaikki tarvittavat tuotteet,
tuotetun RTL:n simulointi ja tuotteiden vertailu edestakaisin. Puute
näkyy nopeimmin kentän käyttäytymisessä ja tuotettujen nimien
vakaudessa.

## Mihin tästä

- **Laitteiston verifiointi**: UVM-testipenkin rakenne, johon
  tuotettu rekisterimalli liitetään, ja kattavuus rekistereille.
- **SoC-integraatio**: lohkojen kytkeminen väyliin ja piirin
  muistikartta, jonka tuotettu SVD ja laitepuu kuvaavat.
- **Linux-laiteajurit** ja **Mikrokontrollerit ja bare-metal-
  ohjelmointi**: tuotettujen otsakkeiden ja laitepuun käyttäjät.
- **ASIC-toteutus** ja **FPGA-toteutus**: SDC-, UPF-, Liberty- ja
  LEF/DEF-kuvaukset vuon osina.

## Lähteet ja lisälukemista

- Accellera: *SystemRDL 2.0 Register Description Language*.
  Standardi on ladattavissa Accelleran sivustolta:
  <https://www.accellera.org/>
- systemrdl-compiler (MIT): kääntäjän ja Python-rajapinnan
  dokumentaatio: <https://systemrdl-compiler.readthedocs.io/>
- PeakRDL (LGPL-3.0) ja liitännäiset regblock, cheader ja uvm
  (LGPL-3.0) sekä ipxact (GPL-3.0): <https://peakrdl.readthedocs.io/>
  ja lähdekoodi <https://github.com/SystemRDL>
- IEEE 1685-2022: *IP-XACT, Standard Structure for Packaging,
  Integrating, and Reusing IP within Tool Flows*.
- IEEE 1800.2: *Universal Verification Methodology Language Reference
  Manual* (rekisterikerros: luku Register Layer).
- Arm: *CMSIS-SVD* -määrittely, osa CMSIS-dokumentaatiota.
- Devicetree Specification: <https://www.devicetree.org/>
- IEEE 1801: *Unified Power Format (UPF)*.
- Verilatorin käyttöohje, varoituskoodit ja konfiguraatiotiedostot:
  <https://verilator.org/guide/latest/>
- Pythonin `xml.etree.ElementTree` ja `tomllib`:
  <https://docs.python.org/3/library/>

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien kuvaukset,
testipenkit, generaattorit ja tarkistimet on kirjoitettu tätä
tutoriaalia varten. Hakemiston `tuotettu/` tiedostot on tuotettu
PeakRDL:llä ja esimerkkien omilla generaattoreilla.

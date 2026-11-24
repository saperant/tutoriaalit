# Lopuksi {.runko-kaytannot .runko-lahteet}

## Menetelmät ja viat

Kirjan esimerkit ajoivat samat viat monella menetelmällä. Taulukko
kokoaa tulokset (✓ löytyi, – ei löytynyt, luku suluissa):

| Menetelmä | `TYHJA` | `SAMANAIKAINEN` | `TAYSI` | `KIINTEA` | `KAKSI` |
|-----------|---------|-----------------|---------|-----------|---------|
| ohjattu testi (1, 7) | – | – | ✓ | | |
| kerroksellinen SV-testipenkki (3) | ✓ | ✓ | ✓ | | |
| kohtelias satunnaistesti, siemen 1 (7) | – | ✓ | ✓ | | |
| kulmatesti (7) | ✓ | – | ✓ | | |
| SVA-väitteet satunnaisärsykkeellä (6) | ✓ | ✓ | ✓ | | |
| formaali BMC (8) | ✓ | ✓ | ✓ | ✓ | ✓ |
| UVM-tyylinen ympäristö, satunnainen (9) | | | | ✓ | ✓ |
| UVM-tyylinen ympäristö, kuormitus (9) | | | | ✓ | ✓ |

Yksikään simulointitesti ei löytänyt kaikkia FIFOn vikoja, ja
koodikattavuus oli täynnä jo ohjatulla testillä, joka päästi läpi
kaksi vikaa. Kattavuusmalli kertoi etukäteen, mitkä viat kukin testi
saattoi päästää läpi. Formaali tarkistus löysi kaikki viat, mutta vain
siksi, että joku kirjoitti oikeat ominaisuudet. Menetelmät eivät kilpaile
keskenään; ne peittävät toistensa aukkoja.

## Nyrkkisäännöt

1. **Suunnitelma ensin.** Ominaisuudet, tarkistukset ja
   kattavuuskohteet kirjataan määrittelystä ennen testipenkkiä.
2. **Kaksi riippumatonta tulkintaa.** Referenssimalli kirjoitetaan
   määrittelystä, ei RTL:stä, eikä se lue DUT:n tilaa.
3. **Vain ajuri ja monitori tuntevat signaalit.** Kaikki muu puhuu
   transaktioista.
4. **Satunnaista laajasti, rajoita vain laiton.** Jokainen
   ylimääräinen rajoite on paikka, johon vika piiloutuu.
5. **Siemen kirjataan aina.** Ajo, jota ei voi toistaa, ei ole tulos.
6. **Kattavuus kertoo, mitä testattiin.** Toiminnallinen kattavuus
   määrittelystä, koodikattavuus RTL:stä, ja molempien aukot käydään
   läpi.
7. **Väite jokaisesta oletuksesta, kattavuus jokaisesta esiehdosta.**
   Tyhjästi tosi väite ei tarkista mitään.
8. **Formaali pienille lohkoille ja säännöille.** BMC ensin, induktio
   ja invariantit sen jälkeen, ja jokaiselle oletukselle
   kattavuuskohde.
9. **Istuta vika jokaiselle tarkistukselle.** Tarkistus, jota ei ole
   nähty epäonnistuvan, ei ole todistettu toimivaksi.
10. **Regressio on verifioinnin tulos.** Toistettava, rinnakkainen,
    luokiteltava, ja jokainen korjattu vika lukitaan siihen.

## Mallit ja niiden paikat

| Malli | Tässä tutoriaalissa |
|-------|---------------------|
| kerroksellinen testipenkki | `03-penkki/testipenkki.sv`, `pythonpenkit/fifo_ymparisto.py` |
| jonomalli referenssinä | `malli[$]` (SV), `FifoMalli` (Python) |
| ajuri laskevalla reunalla, monitori nousevalla | `FifoAjuri`, `FifoMonitori` |
| kattavuuspiste, lokerot ja risti | `pythonpenkit/kattavuus.py` |
| väitemoduuli ja `bind` | `06-sva/fifo_sva.sv` |
| alkutilan oletus formaalissa | `alku`-rekisteri, `assume (rst)` |
| invariantti induktiolle | `rtl/fifo.sv`, osa `INVARIANTTI` |
| rajattu reiluus apulaskurilla | `rtl/arbiteri.sv`, lohko `reilu` |
| UVM-arkkitehtuuri cocotb:llä | `pythonpenkit/arbiteri_ymparisto.py` |
| konekielinen verifiointisuunnitelma | `suunnitelma/fifo.toml`, `tyokalut/suunnitelma.py` |
| vikamatriisi ja luokittelu | `tyokalut/regressio.py` |
| istutetut viat | `BUGI_*`-makrot ja `--virhe`-kohteet |

## Jatkotaidot

- *DSP-algoritmien laitteistototeutus*: bittitarkat referenssimallit
  Pythonilla ja suodattimien verifiointi niitä vasten.
- *EDA-työkalujen skriptaus*: regressioiden, raporttien ja
  työkaluketjujen automatisointi.
- *ASIC-toteutus*: ekvivalenssitarkistus, porttitason simulointi ja
  testattavuus.
- *SoC-integraatio*: väyläprotokollien tarkistimet ja
  järjestelmätason testipenkit.
- *FPGA-toteutus*: verifioidun RTL:n vieminen piirille ja testaus
  kortilla.

## Lähteet

Standardit ja määrittelyt:

- IEEE 1800-2023: *SystemVerilog – Unified Hardware Design,
  Specification, and Verification Language*. Luvut 16 (väitteet),
  18 (satunnaistus) ja 19 (toiminnallinen kattavuus). Maksutta
  IEEE GET -ohjelman kautta.
- IEEE 1800.2-2020: *Standard for Universal Verification Methodology
  Language Reference Manual*.
- Accellera: *UVM 1.2 User's Guide* ja UVM-kirjaston
  referenssitoteutus. Apache 2.0. accellera.org
- Accellera: *Unified Coverage Interoperability Standard* (UCIS) 1.0.

Työkalujen dokumentaatio:

- cocotb: dokumentaatio ja esimerkit. BSD. docs.cocotb.org
- Verilator: käyttöopas, erityisesti luvut väitteistä ja
  kattavuudesta. LGPL/Artistic. verilator.org
- Icarus Verilog. GPL. steveicarus.github.io/iverilog
- Yosys ja SymbiYosys. ISC. yosyshq.readthedocs.io: dokumentaatio ja
  formaalin verifioinnin esimerkit.
- Z3. MIT. github.com/Z3Prover/z3
- pyuvm: UVM Pythonilla cocotb:n päällä. Apache 2.0.
  github.com/pyuvm/pyuvm
- cocotbext-axi ja muut cocotbext-kirjastot. MIT.
  github.com/alexforencich: valmiit väyläkomponentit.

Kirjat ja artikkelit:

- Spear, Tumbush: *SystemVerilog for Verification*. 3. painos,
  Springer, 2012.
- Cerny, Dudani, Havlicek, Korchemny: *SVA: The Power of Assertions
  in SystemVerilog*. 2. painos, Springer, 2015.
- Seligman, Schubert, Kumar: *Formal Verification: An Essential
  Toolkit for Modern VLSI Design*. 2. painos, Morgan Kaufmann, 2023.
- Salemi: *The UVM Primer*. Boston Light Press, 2013.
- Wile, Goss, Roesner: *Comprehensive Functional Verification*.
  Morgan Kaufmann, 2005.
- Gisselquist: formaalin verifioinnin opetusaineisto ja
  blogikirjoitukset Yosysilla. zipcpu.com
- Sutherland, Mills: *Synthesizing SystemVerilog: Busting the Myth
  that SystemVerilog is only for Verification*. SNUG 2013. Hyvä
  katsaus siihen, mikä SystemVerilogissa on suunnittelua ja mikä
  verifiointia.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0). FIFO,
arbiteri ja työkalut on kirjoitettu tätä tutoriaalia varten.

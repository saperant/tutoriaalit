# Lopuksi {.runko-lahteet}

Signaalinkäsittelyalgoritmin vieminen laitteistoksi on sarja
päätöksiä, joista jokainen näkyy biteissä: sanaleveydet,
pyöristykset, rajaukset, rakenne ja ajoitus. Bittitarkka malli tekee
päätökset näkyviksi ennen RTL:ää ja muuttaa RTL:n testauksen
vertailuksi. Tämä luku kokoaa nyrkkisäännöt, esimerkkien hakemiston
ja lähteet.

## Nyrkkisäännöt

Malli ja sanaleveydet:

- Kirjoita bittitarkka malli ennen RTL:ää. Jokainen rajaus on mallissa
  ja RTL:ssä samassa kohdassa ja samalla nimellä.
- Tulon leveys on tekijöiden summa, $N$ termin summa kasvaa $\lceil
  \log_2 N \rceil$ bittiä, ja tarkka raja tulee kertoimien
  itseisarvojen summasta.
- Pyöristä lähimpään yhdellä summaimella. Katkaisu maksaa puolen
  LSB:n tasavirtavirheen ja 6 dB SNR:ää.
- Saturoi ulostulot ja aina takaisinkytkentään menevä arvo. Kierrä
  vain silloin, kun lopputulos tiedetään mahtuvan (CIC).
- Pidä kertoimet versionhallinnassa kokonaislukuina ja generoi RTL:n
  vakiot niistä.

Rakenteet:

- FIR: transponoitu tai systolinen muoto pitkille suotimille,
  symmetria aina kun kertoimet ovat symmetriset.
- IIR: toisen asteen lohkot DF1-muodossa, vahvistus jaettuna
  lohkoille. Takaisinkytkentää ei voi liukuhihnoittaa.
- CORDIC: bitti kierrosta kohden, binäärikulmat, vahvistus
  alkupisteessä.
- NCO: neljännesjakson taulukko, 6 dB vaihebittiä kohden.
- Desimointi: CIC suurille suhteille, polyfaasi-FIR kanavasuotimeksi.
- Laske kellojaksot näytettä kohden ja valitse rinnakkaisuus sen
  mukaan.

Verifiointi ja toteutus:

- Vertaa jokaista näytettä malliin. Toleranssi kuuluu vain
  toiminnallisiin testeihin.
- Testaa rajat suunnatuilla testeillä ja raportoi, vaikuttiko
  saturaatio.
- Testaa liitäntä satunnaisilla tauoilla ja vastapaineella.
- Testaa malli erikseen.
- Lue synteesiraporteista DSP-lohkot, muistit ja kriittinen polku,
  ei vain Fmax.

## Esimerkkien hakemisto

| Asia | Tiedosto |
|------|----------|
| kiinteän pilkun perusoperaatiot | `malli/kiintea.py`, `rtl/kavenna.sv` |
| kertoimet ja RTL-vakiot | `malli/kertoimet.py`, `malli/generoi.py` |
| FIR, IIR, CIC ja polyfaasi mallina | `malli/suotimet.py` |
| CORDIC ja NCO mallina | `malli/cordic.py` |
| suora, transponoitu, symmetrinen FIR | `rtl/fir_suora.sv` ja muut |
| aikamultipleksoitu FIR | `rtl/fir_jaettu.sv` |
| IIR-lohko ja kaskadi | `rtl/biquad.sv`, `rtl/sos.sv` |
| CORDIC | `rtl/cordic_iter.sv`, `rtl/cordic_lh.sv` |
| NCO | `rtl/nco.sv`, `rtl/nco_sini.hex` |
| CIC ja polyfaasi | `rtl/cic.sv`, `rtl/polyfaasi.sv` |
| cocotb-ajuri ja vertailu | `penkit/virta.py`, `penkit/test_*.py` |
| Verilator-testipenkki | `verilator/paa.cpp` |
| mallin testit | `testit/test_malli.py` |
| sanaleveys- ja tarkkuusanalyysit | `analyysit/*.py` |
| synteesi ja raportit | `tyokalut/vuo.sh`, `tyokalut/raportti.py` |
| istutetut viat | `BUGI_KATKAISU`, `BUGI_KIERTO` |

## Jatkotaidot

- *Ohjelmistoradio*: NCO, sekoitin, CIC ja polyfaasisuotimet
  kokonaisena vastaanotinketjuna.
- *Digitaalinen tiedonsiirto*: pulssinmuokkaus, symbolien ajoitus ja
  kantoaallon synkronointi, joiden laitteistototeutus käyttää tämän
  tutoriaalin lohkoja.
- *ASIC-toteutus*: samat rakenteet piirinä, jossa kertoja on vielä
  kalliimpi ja pinta-ala mitataan neliömillimetreinä.
- *Korkean tason synteesi*: samat päätökset tehtyinä C++:sta
  pragmoilla ja `ap_fixed`-tyypeillä.

## Lähteet

Kirjat:

- Parhi: *VLSI Digital Signal Processing Systems: Design and
  Implementation*. Wiley, 1999. Liukuhihnoitus, rinnakkaistus,
  taittaminen, ennakointi ja retiming signaalinkäsittelyn
  näkökulmasta.
- Meyer-Baese: *Digital Signal Processing with Field Programmable
  Gate Arrays*. 4. painos, Springer, 2014. FIR-, IIR-, CORDIC- ja
  monitaajuusrakenteet FPGA:lle.
- Kuo, Lee, Tian: *Real-Time Digital Signal Processing:
  Fundamentals, Implementations and Applications*. 3. painos, Wiley,
  2013.
- Harris: *Multirate Signal Processing for Communication Systems*.
  2. painos, River Publishers, 2021. Polyfaasisuotimet ja
  näytetaajuuden muunnos.
- Oppenheim, Schafer: *Discrete-Time Signal Processing*. 3. painos,
  Pearson, 2010. Luku 6 kvantisoinnin vaikutuksista ja
  rakenteista.

Artikkelit:

- Volder: The CORDIC Trigonometric Computing Technique. *IRE
  Transactions on Electronic Computers*, EC-8(3), 1959.
- Andraka: A survey of CORDIC algorithms for FPGA based computers.
  *FPGA '98*, ACM, 1998. Käytännön katsaus CORDICin toteutuksiin.
- Hogenauer: An economical class of digital filters for decimation
  and interpolation. *IEEE Transactions on Acoustics, Speech, and
  Signal Processing*, 29(2), 1981. CIC-suodin, bittikasvu ja
  karsinta.
- Tierney, Rader, Gold: A Digital Frequency Synthesizer. *IEEE
  Transactions on Audio and Electroacoustics*, 19(1), 1971. NCO ja
  vaiheen katkaisun virheet.
- Lyons: Understanding cascaded integrator-comb filters. *Embedded
  Systems Programming*, 2005. Helppolukuinen johdatus CIC-suotimiin.

Valmistajien dokumentaatio:

- Lattice: *iCE40 DSP Function Usage Guide* (TN1295) ja *iCE40
  UltraPlus Family Data Sheet*. SB_MAC16-lohkon toiminta.
- AMD: *UltraScale Architecture DSP Slice User Guide* (UG579).
  Esisummain, kaskadit ja systoliset FIR-rakenteet.
- Analog Devices: *A Technical Tutorial on Digital Signal Synthesis*.
  NCO:n spektri, vaiheen katkaisu ja dither.

Työkalut:

- cocotb. BSD. docs.cocotb.org
- Icarus Verilog. GPL. steveicarus.github.io/iverilog
- Verilator. LGPL/Artistic. verilator.org
- Yosys ja nextpnr. ISC. yosyshq.net ja github.com/YosysHQ/nextpnr
- NumPy ja SciPy. BSD. numpy.org, scipy.org

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0). Mallit,
RTL ja työkalut on kirjoitettu tätä tutoriaalia varten; synteesivuon
skriptit pohjautuvat taidon *FPGA-toteutus* esimerkkeihin.

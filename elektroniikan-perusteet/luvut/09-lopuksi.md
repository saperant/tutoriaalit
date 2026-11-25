# Lopuksi {.runko-lahteet}

Tutoriaali kulki Ohmin laista CMOS-invertteriin. Jokainen piiri
laskettiin käsin ja simuloitiin, ja Python vertasi tuloksia. Tämä
kaksinkertainen tarkistus on tutoriaalin tärkein opetus: kaava kertoo,
*miksi* piiri käyttäytyy niin kuin käyttäytyy, ja simulaattori kertoo,
*kuinka paljon*, myös silloin kun kaavan oletukset eivät enää päde.

## Nyrkkisäännöt

| Asia | Nyrkkisääntö |
|------|--------------|
| vastuksen teho | tehonkesto vähintään kaksinkertainen häviöön nähden |
| jakajan kuormitus | jakajan virta vähintään kymmenkertainen kuormaan nähden |
| mittaus | mittarin tuloimpedanssi vähintään satakertainen piiriin nähden |
| aikavakio | 63 % yhdessä, 99 % viidessä aikavakiossa |
| nousuaika 30...70 % | $0{,}85\,RC$ |
| desibelit | −3 dB = puolet tehosta, −20 dB/dekadi yhden RC:n jälkeen |
| piidiodi | 0,6...0,7 V; +60...120 mV jokaista virran kymmenkertaistumista kohden |
| lineaarisäädin | häviö $(U_\text{sisään} - U_\text{ulos})\,I$; tulo vähintään lähtö + pudotusjännite |
| LEDin etuvastus | $(U - U_F) / I$, pyöristys ylöspäin |
| BJT-kytkin | pakotettu vahvistus 10...20 |
| MOSFET-kytkin | $R_{DS(on)}$ datalehdestä käytetyllä hilajännitteellä |
| lämpö | $T_j = T_a + P R_{\theta JA}$, piillä enintään noin 150 °C |
| logiikkatasot | lähdön $U_{OH}$ yli tulon $U_{IH}$:n ja $U_{OL}$ alle $U_{IL}$:n |
| induktiivinen kuorma | aina vapaakäyntidiodi |
| hitaat reunat | Schmitt-tulo |

## Jatkotaidot

Jatkotaito *Analogiaelektroniikka* rakentaa tämän päälle:
transistorivahvistimet ja toimintapiste, operaatiovahvistimet,
aktiiviset suodattimet, takaisinkytkentä ja stabiilisuus, AD- ja
DA-muuntimet sekä kohina. Se tarvitsee myös taitoa *Differentiaaliyhtälöt
ja Laplace-muunnos*, koska suodattimien ja säätöpiirien käyttäytyminen
kuvataan siirtofunktioilla.

Muita läheisiä taitoja:

- *Digitaalitekniikka*: logiikkaportit, kiikut ja tilakoneet; luvun 7
  CMOS-invertteri ja logiikkatasot ovat niiden sähköinen pohja.
- *Mikrokontrollerit ja bare-metal-ohjelmointi* sekä *Oheislaiteväylät*:
  GPIO, vetovastukset ja väylien sähköiset tasot luvun 4 ja 7 pohjalta.
- *RTL-suunnittelu SystemVerilogilla* ja *FPGA-toteutus*: luvun 4
  kosketinvärähtelyn suodatus ja luvun 7 PWM digitaalisena logiikkana.
- *ASIC-toteutus*: CMOS-piirien viive ja teho suuressa mittakaavassa.
- *Differentiaaliyhtälöt ja Laplace-muunnos*: luvun 4 ja 5 RC- ja
  RLC-vasteet yhtälöistä johdettuina.

Elektroniikkaa oppii parhaiten rakentamalla. Koekytkentälevy, muutama
vastus, kondensaattori, LED, transistori ja yleismittari riittävät
tämän tutoriaalin piirien kokeilemiseen. Kun oikea piiri ja simulointi
eroavat, ero on aina opettavainen.

## Lähteet

- Horowitz, P. ja Hill, W. *The Art of Electronics*. 3. painos.
  Cambridge University Press, 2015. Käytännönläheinen perusteos.
- Sedra, A. S. ja Smith, K. C. *Microelectronic Circuits*. Oxford
  University Press. Puolijohteet ja transistorimallit.
- Rabaey, J. M., Chandrakasan, A. ja Nikolić, B. *Digital Integrated
  Circuits: A Design Perspective*. 2. painos. Prentice Hall, 2003.
  CMOS-invertterin kynnys ja viive.
- Shockley, W. "The Theory of p-n Junctions in Semiconductors and p-n
  Junction Transistors". *Bell System Technical Journal* 28(3), 1949.
- Nagel, L. W. *SPICE2: A Computer Program to Simulate Semiconductor
  Circuits*. Memorandum ERL-M520, University of California, Berkeley, 1975.
- ngspice-projekti. *Ngspice User's Manual*. <https://ngspice.sourceforge.io/>
- IEC 60063. *Preferred number series for resistors and capacitors*.
- NXP Semiconductors. *UM10204: I2C-bus specification and user manual*.
  Nousuaikojen ja vetovastusten raja-arvot.
- KiCad-projekti. <https://www.kicad.org/>
- schemdraw-kirjaston dokumentaatio. <https://schemdraw.readthedocs.io/>
- Texas Instruments. *HCMOS Design Considerations* (SCLA007) ja
  74HC- ja 74HCT-sarjojen datalehdet. Logiikkatasot ja
  kohinamarginaalit.
- JEDEC JESD8C. *Interface Standard for Nominal 3 V/3.3 V Supply
  Digital Integrated Circuits*. 3,3 V:n logiikan tasot.
- Taitopuun muut tutoriaalit: *Matematiikan perusteet ohjelmallisesti*,
  *Kompleksiluvut ja Fourier-analyysi*, *Digitaalitekniikka* ja
  *Oheislaiteväylät*.

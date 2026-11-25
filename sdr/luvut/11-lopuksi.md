# Lopuksi {.runko-lahteet}

Tutoriaali rakensi ohjelmistoradion vastaanotinketjun IQ-näytteistä
valmiiseen ääneen ja dataan. Ensin tallenteet luettiin oikein ja
laitteen epäideaalisuudet korjattiin. Sitten kanava valittiin
NCO:lla ja vaiheittaisella desimoinnilla, ja FM-stereo, RDS-tyyppinen
data ja GFSK-paketit purettiin. Lopuksi raskain osa siirrettiin
lohkoittain toimivaan C++-koodiin. Jokainen vaihe on testattu
synteettisellä tallenteella, jonka sisältö tunnetaan, joten
vastaanottimen jokaisesta luvusta tiedetään, onko se oikein.

## Nyrkkisäännöt

| Tilanne | Sääntö |
|------------------|----------------------------------------------|
| kaista | kompleksinen $f_s$ = kaista; luota keskimmäisiin 75–80 %:iin |
| cu8 | $(x - 127{,}5)/127{,}5$; I ja Q vuorotellen |
| metatiedot | SigMF: datatyyppi, näytetaajuus, keskitaajuus |
| ADC | SQNR $6{,}02N + 1{,}76$ dB; kapea signaali hyötyy FFT:n vahvistuksesta |
| vahvistus | voimakkain signaali muutama dB täyden skaalan alle |
| tasakomponentti | viritä ohi 100–250 kHz tai DC-esto $a = 0{,}999$ |
| IQ-epätasapaino | IRR kaavasta; sokea korjaus Gram–Schmidtillä |
| kide | ppm × taajuus; mittaa tunnetusta kantoaallosta |
| NCO | 32 bitin akkumulaattori; noin 6 dB SFDR:ää taulukon bittiä kohti |
| desimointi | vaiheittain; ensimmäinen esto laskostuvan kaistan mukaan |
| monta kanavaa | polyfaasipankki: osasuotimet ja IFFT |
| FM-ilmaisin | $\arg(z[n]\,z^*[n-1])$; vaste $\text{sinc}(f/f_s)$ |
| FM-kynnys | noin 10 dB CNR; yläpuolella $+1{,}5(\Delta f/W)^2 B/W$ |
| jälkikorostus | 50 µs Euroopassa, 75 µs Amerikassa |
| stereo | PLL pilottiin; sama suodin summalle ja erotukselle |
| RDS | 57 kHz, 1187,5 bit/s; lohkoraja syndroomasta |
| pakettihaku | normitettu korrelaatio alkuosaan ja tahdistussanaan |
| taajuusvirhe | alkuosan ilmaisinlähdön keskiarvo |
| lohkot | tila säilyy; lohkoittain = kerralla bitilleen |
| läpäisy | mittaa reaaliaikakertoimena; desimoi lähellä ADC:tä |
| lähetys | vain luvalla tai luvasta vapaan käytön ehdoin |

## Jatkotaidot

Ohjelmistoradio on taitopuun roolin *Signaalinkäsittelyn ja
ohjelmistoradion kehittäjä* viimeinen taito. Sitä täydentävät:

- *DSP-algoritmien laitteistototeutus* toteuttaa NCO:n, desimoivat
  suotimet ja CIC-rakenteet kiinteän pilkun laitteistona, kuten
  SDR-laitteiden FPGA:issa.
- *Tietoliikennetekniikka* ja *Tietoverkot* jatkavat siitä, mihin
  pakettivastaanotin jäi: kehyksistä protokolliin.
- *Sulautettujen järjestelmien tietoturva* käsittelee
  langattomien laitteiden uhkia ja suojauksia.

## Lähteet ja lisälukemista

- Marc Lichtman: *PySDR: A Guide to SDR and DSP using Python*.
  Verkossa <https://pysdr.org/> (CC BY-NC-SA). Erinomainen
  johdatus samoihin aiheisiin Pythonilla.
- Travis F. Collins, Robin Getz, Di Pu ja Alexander M. Wyglinski:
  *Software-Defined Radio for Engineers*. Artech House, 2018.
  Verkossa ilmaiseksi Analog Devicesin sivuilla; käyttää
  PlutoSDR:ää.
- Fredric J. Harris: *Multirate Signal Processing for Communication
  Systems*, 2. painos. River Publishers, 2021. Polyfaasisuotimet ja
  kanavapankit.
- Richard G. Lyons: *Understanding Digital Signal Processing*,
  3. painos. Prentice Hall, 2010. Muun muassa FM-ilmaisimet ja
  DC-esto.
- IEC 62106: *Radio data system (RDS) – VHF/FM sound broadcasting in
  the frequency range from 64,0 MHz to 108,0 MHz*.
- ITU-R BS.450: *Transmission standards for FM sound broadcasting at
  VHF*. FM-yleisradion ja stereon parametrit.
- SigMF-määrittely, <https://github.com/sigmf/SigMF>.
- GNU Radion dokumentaatio, <https://wiki.gnuradio.org/>.
- `librtlsdr` ja `rtl_sdr`, <https://osmocom.org/projects/rtl-sdr>.
- SoapySDR, <https://github.com/pothosware/SoapySDR>.
- Liikenne- ja viestintävirasto Traficom: radiotaajuudet ja
  luvasta vapaat radiolähettimet, <https://www.traficom.fi/>.
- Laki sähköisen viestinnän palveluista (917/2014),
  <https://www.finlex.fi/>.
- Euroopan parlamentin ja neuvoston direktiivi 2014/53/EU
  (radiolaitedirektiivi).

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
Lähdeteosten tekstiä ei ole kopioitu; niihin viitataan lisälukemistona.

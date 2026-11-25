# Lopuksi {.runko-lahteet}

Tutoriaali kulki transistorin toimintapisteestä operaatiovahvistimiin,
suodattimiin, takaisinkytkennän stabiilisuuteen, muuntimiin ja kohinaan.
Jokainen piiri laskettiin mallilla ja simuloitiin, ja Python vertasi
tuloksia. Matkan varrella erot opettivat eniten: transistorin vahvistus
toimintapisteessä, lähtöresistanssin vaikutus kaistanleveyteen,
toleranssien eri vaikutus kulma- ja rajataajuuteen ja nousunopeuden
taakse piiloutunut epävakaus. Analogiasuunnittelu on mallien ja niiden
oletusten tuntemista.

## Nyrkkisäännöt

| Asia | Nyrkkisääntö |
|------|--------------|
| BJT:n toimintapiste | jakaja ja emitterivastus, jonka yli vähintään 1 V |
| transkonduktanssi | $g_m = I_C / 25{,}9$ mV, 1 mA: noin 39 mS |
| vahvistus ja kaista | $GBW$ on vakio: kaista = $GBW$ / vahvistus |
| nousunopeus | siniaalto siisti, kun $2\pi f \hat U < SR$ |
| offset | vahvistuu ei-invertoivalla vahvistuksella $1 + R_2/R_1$ |
| differentiaalipari | $A_d = g_m R_c/2$, $A_{cm} \approx R_c/(2R_{ee})$; virtalähde häntänä |
| CMRR | erovahvistimen vastusten epäsovitus $\varepsilon$: $A_{cm} \approx \varepsilon/2$ |
| suodattimen vahvistin | $GBW > 100\,f_0 Q$ |
| Butterworth / Bessel | $Q$ = 0,707 / 0,577; ylitys 4,3 % / 0,4 % |
| vaihevara | vähintään 45 ... 60 astetta; tarkista pienellä signaalilla |
| kapasitiivinen kuorma | eristysvastus 20 ... 100 Ω |
| vertailija | hystereesi suurempi kuin tulon kohina huipusta huippuun |
| PWM-DA-muunnin | rippeli $U D (1-D) T/\tau$, asettuminen $\tau \ln 2^{N+1}$ |
| kvantisointi | SNR = 6,02 N + 1,76 dB |
| näytteenotto | asettuminen $RC \ln 2^{N+1}$, 12 bittiä: 9 RC |
| sigma-delta | 1. kertaluku: +9 dB ylinäytteistyksen kaksinkertaistusta kohden |
| terminen kohina | 1 kΩ: 4 nV/√Hz; RC: $\sqrt{kT/C}$ |
| siirtolinja | kun viive yli 1/6 nousuajasta; piirilevyllä 15 cm/ns |
| ohitus | 100 nF jokaiseen käyttöjännitenastaan |

## Jatkotaidot

Tästä edetään taitopuussa seuraaviin taitoihin:

- *Digitaalinen signaalinkäsittely* jatkaa siitä, mihin AD-muunnin
  jättää: suodatus, desimointi ja spektri luvuilla.
- *Lukujen esitys ja kiinteän pilkun aritmetiikka* käsittelee
  kvantisoinnin ja sananpituuden laskennan puolella.
- *Mikrokontrollerit ja bare-metal-ohjelmointi* ja *Oheislaiteväylät*
  käyttävät AD- ja DA-muuntimia, vertailijoita ja väyliä, joiden
  sähköinen puoli käsiteltiin tässä.
- *Ohjelmistoradio* käsittelee radiovastaanottimen signaalinkäsittelyn;
  luvun 7 siirtolinjat ovat sen analogisen etupään lähtökohta.
- *ASIC-toteutus* esittelee integroidun piirin digitaalisen puolen.
- *Numeeriset menetelmät* selittää, miten SPICE ratkaisee piirin
  yhtälöt.

Analogiaelektroniikka on laaja ala, ja osa sen jatkosuunnista on tämän
taitopuun ulkopuolella. Tehoelektroniikassa (jännitteensäätimet,
hakkuriteholähteet, moottoriohjaimet) luvun 5 stabiilisuusanalyysi on
keskeinen työkalu. Radiotaajuuspiireissä tarvitaan impedanssisovitusta,
Smithin karttaa ja s-parametreja. Piirilevysuunnittelussa (esimerkiksi
KiCad) maatasot, impedanssikontrolloidut johtimet ja EMC ratkaisevat,
toimiiko tässä simuloitu piiri myös levyllä. Lähdeluettelon teokset
kattavat nämä.

Elektroniikkaa oppii parhaiten rakentamalla. Koekytkentälevy,
operaatiovahvistin (esimerkiksi rail-to-rail-tyyppi 5 V:n syötöllä),
muutama vastus ja kondensaattori, signaaligeneraattori ja oskilloskooppi
riittävät tämän tutoriaalin kytkentöjen kokeilemiseen. Kun mitattu ja
simuloitu eroavat, etsi se, mitä malli ei sisällä.

## Lähteet

- Horowitz, P. ja Hill, W. *The Art of Electronics*. 3. painos.
  Cambridge University Press, 2015. Käytännönläheinen perusteos,
  erityisesti luvut transistoreista, operaatiovahvistimista ja kohinasta.
- Sedra, A. S. ja Smith, K. C. *Microelectronic Circuits*. Oxford
  University Press. Piensignaalimallit ja vahvistinasteet.
- Franco, S. *Design with Operational Amplifiers and Analog Integrated
  Circuits*. 4. painos. McGraw-Hill, 2015. Operaatiovahvistinkytkennät,
  suodattimet ja stabiilisuus.
- Kester, W. (toim.). *The Data Conversion Handbook*. Analog Devices,
  2005. AD- ja DA-muuntimien arkkitehtuurit ja määritelmät (SNR, ENOB,
  INL, DNL).
- Schreier, R. ja Temes, G. C. *Understanding Delta-Sigma Data
  Converters*. Wiley-IEEE Press, 2005.
- Johnson, H. ja Graham, M. *High-Speed Digital Design: A Handbook of
  Black Magic*. Prentice Hall, 1993. Siirtolinjat ja päättäminen.
- Ott, H. W. *Electromagnetic Compatibility Engineering*. Wiley, 2009.
  Maadoitus, ohitus ja kytkeytyminen.
- Johnson, J. B. "Thermal Agitation of Electricity in Conductors" ja
  Nyquist, H. "Thermal Agitation of Electric Charge in Conductors".
  *Physical Review* 32, 1928. Termisen kohinan alkuperäiset artikkelit.
- Sallen, R. P. ja Key, E. L. "A Practical Method of Designing RC Active
  Filters". *IRE Transactions on Circuit Theory* 2(1), 1955.
- ngspice-projekti. *Ngspice User's Manual*. <https://ngspice.sourceforge.io/>
- SciPy-, SymPy- ja schemdraw-kirjastojen dokumentaatiot.
- Taitopuun muut tutoriaalit: *Elektroniikan perusteet ja SPICE*,
  *Differentiaaliyhtälöt ja Laplace-muunnos*, *Signaalit ja järjestelmät*,
  *Digitaalinen signaalinkäsittely* ja *Oheislaiteväylät*.

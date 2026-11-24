# GNU Radio

GNU Radio on avoimen lähdekoodin ohjelmistoradiokehys (GPLv3), joka
on alan yleisin. Siinä vastaanotin kootaan **lohkoista**, kuten
laitelähteestä, suotimista, ilmaisimista ja äänilähdöstä, jotka
yhdistetään **lohkokaavioksi** (*flowgraph*). Ajastin siirtää
näytteitä lohkojen välillä puskureissa ja kutsuu lohkoja, kun niillä
on dataa. Lohkoja on satoja valmiina, ja omat voi kirjoittaa
Pythonilla tai C++:lla.

GNU Radio ei ole tämän tutoriaalin testiympäristössä, koska se on
suuri asennus ja tarvitsee graafisen ympäristön. Luvun GNU Radio
-tiedostot ja -kääreet on siksi merkitty **testaamattomiksi**. Lohkon
logiikka on kuitenkin tavallista Pythonia, joka testataan ilman
GNU Radiota. Samaa erottelua kannattaa käyttää muutenkin.

## Lohkokaavio

GNU Radio Companion (GRC) on graafinen editori, joka tallentaa kaavion
YAML-muotoiseen `.grc`-tiedostoon ja tuottaa siitä Python-ohjelman.
Luvun 5 monovastaanotin näyttäisi GRC:ssä seuraavalta. Lohkojen
tunnisteet noudattavat GNU Radio 3.10:tä, ja ote on lyhennetty:
siitä puuttuvat muun muassa `options`-osa ja lohkojen sijainnit
(testaamaton):

```yaml
blocks:
- name: lahde
  id: soapy_rtlsdr_source
  parameters: {center_freq: '98.0e6', samp_rate: '912e3', gain: '20'}
- name: kanava
  id: freq_xlating_fir_filter_xxx
  parameters:
    type: ccc
    decim: '4'
    center_freq: '200e3'
    taps: firdes.low_pass(1.0, 912e3, 100e3, 20e3)
- name: ilmaisin
  id: analog_wfm_rcv
  parameters: {quad_rate: '228e3', audio_decimation: '1'}
- name: naytetaajuus
  id: rational_resampler_xxx
  parameters: {type: fff, interp: '4', decim: '19'}
- name: aani
  id: audio_sink
  parameters: {samp_rate: '48000'}
connections:
- [lahde, '0', kanava, '0']
- [kanava, '0', ilmaisin, '0']
- [ilmaisin, '0', naytetaajuus, '0']
- [naytetaajuus, '0', aani, '0']
```

Lohkot vastaavat suoraan tämän tutoriaalin funktioita:

| GNU Radion lohko | Tutoriaalin vastine | Luku |
|------------------|---------------------|------|
| `soapy_rtlsdr_source` | `lue_cu8` | 2 |
| `freq_xlating_fir_filter_xxx` | `valitse_kanava` | 4, 5 |
| `analog_wfm_rcv` | `fm_ilmaisin` ja jälkikorostus | 5 |
| `rational_resampler_xxx` | `resample_poly(x, 4, 19)` | 6 |
| `analog_pll_refout_cc` | `Pll.lukitse` | 6 |
| `digital_correlate_access_code_bb` | `hae` (pakettihaku) | 7 |

`freq_xlating_fir_filter` tekee siirron, suodatuksen ja desimoinnin
yhdessä lohkossa, kuten luvun 8 C++-ketju. GNU Radion valmiit
WBFM-lohkot sisältävät myös stereodekooderin, ja RDS-purkuun on
erillinen moduuli (`gr-rds`).

## Lohkon sopimus

GNU Radion lohkotyyppejä on muutama:

- `sync_block`: yksi lähtönäyte jokaista tulonäytettä kohti,
  esimerkiksi sekoitin ja ilmaisin
- `decim_block`: yksi lähtö $N$ tulonäytettä kohti,
  esimerkiksi desimoiva suodin
- `interp_block`: $N$ lähtöä yhtä tuloa kohti
- `basic_block`: vapaa suhde, kuten pakettihaku, joka tuottaa
  lähtöä vain löytäessään paketin

Ajastin kutsuu lohkon `work`-metodia aina, kun tuloa ja lähtötilaa on
saatavilla. Palan koko vaihtelee kutsusta toiseen, ja se riippuu
puskurien täyttöasteesta, eikä lohko voi valita sitä. Siksi luvun 8
sääntö pätee täälläkin: lohkon on säilytettävä tilansa kutsujen
välillä.

Esimerkin lohko mittaa tehon desibeleinä, ja se desimoi sadalla.
Lohkossa on eksponentiaalinen keskiarvo, jonka tila säilyy:

```{.python tiedosto="esimerkit/09-lohko.py" osa="lohko"}
```

Ajastinta jäljittelevä funktio syöttää lohkolle paloja annettujen
kokojen mukaan. Testi ajaa saman signaalin kerralla ja hyvin pieninä
vaihtelevina paloina:

```{.python tiedosto="esimerkit/09-lohko.py" osa="ajastin"}
```

```{.python tiedosto="esimerkit/09-lohko.py" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/09-lohko.odotettu"}
```

Lähdöt ovat samat palojen koosta riippumatta, ja taso seuraa
signaalin kolmea tasoa (−37, −17 ja −27 dBFS) muutaman lähdön
viiveellä.

## Lohkon kääre GNU Radioon

GRC:n *Embedded Python Block* -lohko tai erillinen moduuli tarvitsee
kääreen, joka periytyy GNU Radion lohkoluokasta ja välittää
kutsun logiikalle. Kääre on muutaman rivin mittainen, eikä siinä ole
signaalinkäsittelyä (testaamaton):

```text
import numpy as np
from gnuradio import gr


class blk(gr.decim_block):
    """Tehomittari: yksi dBFS-arvo jokaista 'desimointi' naytetta kohti."""

    def __init__(self, desimointi=100, alfa=0.1):
        gr.decim_block.__init__(self, name="Tehomittari",
                                in_sig=[np.complex64],
                                out_sig=[np.float32], decim=desimointi)
        self.logiikka = TehoMittari(desimointi, alfa)

    def work(self, input_items, output_items):
        return self.logiikka.work(input_items, output_items)
```

Kun lohko on valmis, se voidaan siirtää Pythonista C++:aan
(`gr_modtool`) ilman, että lohkokaavio muuttuu. Usein Python riittää,
koska raskaat operaatiot tehdään NumPyllä taulukoille eikä näyte
kerrallaan. Esimerkin lohko käy kuitenkin palat läpi
Python-silmukassa, joten suurilla näytetaajuuksilla C++ on tarpeen.

## Muita GNU Radion ominaisuuksia

- **Tagit** (*stream tags*) liittävät näytevirran tiettyyn kohtaan
  metatietoa, kuten "paketti alkaa tästä" tai "taajuus vaihtui".
  Lohkot välittävät ne eteenpäin.
- **Viestiportit** (*message ports*) välittävät asynkronisia
  viestejä, kuten purettuja paketteja tai ohjauskomentoja.
- **Hierarkkiset lohkot** kokoavat osakaavion yhdeksi lohkoksi.
- **VOLK** (*Vector-Optimized Library of Kernels*) valitsee ajossa
  prosessorille nopeimman SIMD-toteutuksen.
- **SigMF-tuki**: tallenteet ja metatiedot luvun 2 muodossa
  (`gr-sigmf` ja File Meta Sink).

## Käytännössä

- **Erota logiikka kääreestä.** Pidä signaalinkäsittely tavallisena
  luokkana tai funktiona, jonka voi testata ilman GNU Radiota ja
  laitetta. Kääre vain välittää kutsut.
- **Testaa palojen koko.** Aja lohko yhden näytteen paloina ja
  kokonaisena ja vertaa. Ajastin tuottaa kaikkia kokoja.
- **Aloita valmiista lohkoista.** GRC:llä FM-vastaanotin syntyy
  muutamassa minuutissa. Omia lohkoja tarvitaan vasta, kun valmis ei
  riitä.
- **Versionhallitse `.grc` ja generoitu Python.** GRC:n YAML on
  luettavaa, ja muutokset näkyvät erotuksina. Generoitu Python
  kertoo tarkat parametrit myös ilman GRC:tä.
- **Mittaa ylivuodot.** GNU Radion laitelähteet tulostavat
  ylivuodosta merkin `O` (*overrun*). Jos merkkejä tulee, kaavio on
  liian raskas laitteen näytetaajuudelle.

## Itsearviointi

- Osaat selittää GNU Radion lohkokaavion, ajastimen ja lohkotyypit
  `sync_block`, `decim_block`, `interp_block` ja `basic_block`.
- Osaat kirjoittaa lohkon logiikan niin, että sen voi testata ilman
  GNU Radiota ja että tulos ei riipu palojen koosta.
- Osaat koota FM-vastaanottimen GNU Radion valmiista lohkoista ja
  yhdistää ne tämän tutoriaalin vaiheisiin.
- Osaat selittää tagien, viestiporttien ja VOLK-kirjaston tehtävät.

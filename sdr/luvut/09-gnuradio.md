# GNU Radio

Tähän asti vastaanottimet on kirjoitettu itse: funktiot ottavat
taulukon ja palauttavat taulukon, ja luvun 8 C++-ketju käsittelee
virtaa paloina omassa silmukassaan. GNU Radio on avoimen lähdekoodin
ohjelmistoradiokehys (GPLv3), joka antaa saman rakenteen valmiina.
Vastaanotin kootaan **lohkoista**, jotka yhdistetään
**lohkokaavioksi** (*flowgraph*), ja kehys huolehtii puskureista,
säikeistä ja näytteiden siirrosta. Lohkoja on satoja valmiina, ja omat
voi kirjoittaa Pythonilla tai C++:lla.

Tässä luvussa luvun 5 monovastaanotin kootaan GNU Radion lohkoista,
sen tulosta verrataan tutoriaalin omaan vastaanottimeen ja kaavioon
lisätään oma lohko, jolla on GNU Radion tapaan kirjoitettu
yksikkötesti. Kaikki ajetaan ilman radiota, äänikorttia ja näyttöä:
lähteenä on tiedosto ja nieluina tiedostot.

## Asennus ja kaksi Pythonia

Ubuntussa GNU Radio asennetaan jakelun paketista (24.04:ssä versio
3.10.9, noin 300 megatavua riippuvuuksineen):

```text
sudo apt-get install gnuradio
```

Graafista ympäristöä ei tarvita. Sitä käyttävät vain GRC-editori ja
näyttölohkot, ja Python-ohjelmana kirjoitettu lohkokaavio ajetaan
päätteessä.

Asennuksessa on yksi sudenkuoppa. GNU Radion Python-kirjasto on
käännetty jakelun omaa Pythonia ja NumPya vasten. Jos `pip` on
asentanut uudemman NumPyn, kuten tämän tutoriaalin muut esimerkit
edellyttävät, moduulin `gnuradio` lataus epäonnistuu. Siksi luvun
GNU Radio -ohjelmat ajetaan pienellä käynnistimellä, joka valitsee
jakelun Pythonin ja antaa sille vain jakelun paketit:

```{.bash tiedosto="esimerkit/gnuradio/gr-python" alkaen="set -eu"}
```

Tutoriaalin oma koodi ajetaan edelleen tavallisella `python3`:lla.
Kaksi ympäristöä vaihtavat tietoja tiedostoina, mikä on muutenkin
luonteva raja: tallenne menee sisään ja ääni tulee ulos.

## Lohkot, virrat ja ajastin

Lohkolla on tyypitettyjä portteja, ja portit yhdistetään toisiinsa
**virroilla**. Virran alkio on esimerkiksi kompleksinen näyte
(`complex64`), liukuluku tai tavu. Lohkotyyppejä on neljä:

- `sync_block`: yksi lähtönäyte jokaista tulonäytettä kohti,
  esimerkiksi sekoitin ja ilmaisin
- `decim_block`: yksi lähtö $N$ tulonäytettä kohti,
  esimerkiksi desimoiva suodin
- `interp_block`: $N$ lähtöä yhtä tuloa kohti
- `basic_block`: vapaa suhde, kuten pakettihaku, joka tuottaa
  lähtöä vain löytäessään paketin

Kehys ei tunne näytetaajuutta. Se tietää vain lohkojen suhteet
(tämä lohko desimoi neljällä), ja näytetaajuus on luku, jonka
suunnittelija antaa parametrina niille lohkoille, jotka sitä
tarvitsevat. Väärä luku ei aiheuta virhettä, vaan suodin vain osuu
väärään taajuuteen.

Jokaisen yhteyden takana on puskuri, ja jokainen lohko ajetaan omassa
säikeessään. **Ajastin** (*scheduler*) kutsuu lohkon `work`-metodia,
kun tulopuskurissa on dataa ja lähtöpuskurissa tilaa. Kun
lähtöpuskuri on täynnä, lohkoa ei kutsuta: hidas lohko pysäyttää
edeltäjänsä, eikä näytteitä katoa ketjun sisällä. Tämä **vastapaine**
ulottuu lähteeseen asti. Tiedostolähde vain odottaa, mutta radio ei
voi odottaa, ja silloin näytteitä hukkuu laitteen päässä (luku 8).

Erot tutoriaalin omiin toteutuksiin ovat siis nämä:

| | Oma Python-funktio | Luvun 8 C++-ketju | GNU Radio |
|---|---|---|---|
| Datan muoto | koko tallenne taulukkona | kiinteän kokoiset palat | vaihtelevan kokoiset palat |
| Kuka kutsuu | ohjelma itse | oma silmukka | ajastin |
| Rinnakkaisuus | ei | ei | säie lohkoa kohti |
| Tila kutsujen välillä | ei tarvita | lohkon jäsenissä | lohkon jäsenissä |

Palan koko vaihtelee kutsusta toiseen puskurien täyttöasteen mukaan,
eikä lohko voi valita sitä. Luvun 8 sääntö pätee siksi täälläkin:
lohkon on säilytettävä tilansa kutsujen välillä, eikä tulos saa
riippua siitä, mihin kohtaan palojen rajat osuvat.

## Vastaanotin lohkokaaviona

Luvun 5 monovastaanotin on GNU Radiossa kuuden lohkon ketju. Samaan
kaavioon on kytketty tämän luvun oma lohko, joka mittaa kanavan tasoa.

```{.dot otsikko="FM-monovastaanotin lohkokaaviona. Paksut nuolet ovat kompleksisia virtoja ja ohuet liukulukuvirtoja; lohkoissa on näytetaajuus ennen ja jälkeen. Tehomittari on tämän luvun oma lohko."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.4;
  node [shape=box, style="rounded,filled", fillcolor="#EEF3F3",
        fontsize=9, margin="0.08,0.05"];
  t [label="asema.cu8", shape=note, fillcolor=white];
  l [label="Cu8Lahde\n912 kS/s"];
  k [label="freq_xlating_fir\n912 → 228 kS/s"];
  i [label="quadrature_demod"];
  d [label="fm_deemph"];
  r [label="rational_resampler\n228 → 48 kS/s"];
  a [label="gr.f32", shape=note, fillcolor=white];
  m [label="Tehomittari\n228 kS/s → 100 /s", fillcolor="#D8ECEA"];
  s [label="taso.f32", shape=note, fillcolor=white];
  { rank=same; t -> l; l -> k [penwidth=2]; }
  { rank=same; i -> d; d -> r; r -> a; }
  { rank=same; m -> s; }
  k -> i [penwidth=2];
  k -> m [penwidth=2];
  i -> m [style=invis];
}
```

GNU Radiossa ei ole valmista lukijaa RTL-SDR:n `cu8`-muodolle, joten
lähde kootaan peruslohkoista. **Hierarkkinen lohko** (`hier_block2`)
paketoi osakaavion yhdeksi lohkoksi, jolla on omat porttinsa:

```{.python tiedosto="esimerkit/gnuradio/lohkokaavio/fm_mono.py" osa="lahde"}
```

Itse vastaanotin on luokka, joka periytyy luokasta `top_block`.
Muodostin luo lohkot ja yhdistää ne; signaalinkäsittelyä siinä ei ole.

```{.python tiedosto="esimerkit/gnuradio/lohkokaavio/fm_mono.py" osa="kaavio"}
```

Lohkot vastaavat suoraan aiempien lukujen funktioita:

| GNU Radion lohko | Tutoriaalin vastine | Luku |
|------------------|---------------------|------|
| `Cu8Lahde` (oma hierarkkinen lohko) | `lue_cu8` | 2, 5 |
| `freq_xlating_fir_filter_ccc` | `valitse_kanava` | 4, 5 |
| `quadrature_demod_cf` | `fm_ilmaisin` | 5 |
| `fm_deemph` | `jalkikorostus` | 5 |
| `rational_resampler_fff` | alipäästö ja `resample_poly(x, 4, 19)` | 6 |
| `analog_pll_refout_cc` | `Pll.lukitse` | 6 |
| `digital_correlate_access_code_bb` | `hae` (pakettihaku) | 7 |

Nimistä kannattaa huomata yksi asia. GNU Radion `quadrature_demod`
laskee peräkkäisten näytteiden vaihe-eron arkustangentilla, joten se
on luvun 5 termein polaari-ilmaisin eikä siniapproksimaatiota käyttävä
kvadratuuri-ilmaisin. Nimen päätteet kertovat porttien tyypit: `ccc`
on kompleksinen tulo, kompleksinen lähtö ja kompleksiset kertoimet,
`cf` kompleksinen tulo ja liukulukulähtö.

Kaavio käynnistetään metodilla `run`, joka palaa, kun lähde on
loppunut ja puskurit ovat tyhjentyneet:

```{.python tiedosto="esimerkit/gnuradio/lohkokaavio/fm_mono.py" osa="aja"}
```

GNU Radio Companion (GRC) on graafinen editori samalle asialle. Se
tallentaa kaavion YAML-muotoiseen `.grc`-tiedostoon ja tuottaa siitä
Python-ohjelman, joka on rakenteeltaan samanlainen kuin yllä: luokka,
jonka muodostin luo ja yhdistää lohkot. GRC:tä ei ajeta tässä, koska
se tarvitsee näytön. Kaavion voi piirtää GRC:llä ja ajaa tuotetun
Python-tiedoston palvelimella, tai kirjoittaa kaavion suoraan
Pythonilla, kuten tässä.

## Sama tallenne, kaksi vastaanotinta

Vertailussa on kolme vaihetta, ja ne ovat esimerkkien Makefilen
kohteessa `gnuradio`. Tutoriaalin oma koodi tekee tallenteen ja
viiteäänen, GNU Radio ajaa lohkon yksikkötestin ja lohkokaavion, ja
lopuksi tuloksia verrataan:

```{.makefile tiedosto="esimerkit/Makefile" osa="gnuradio"}
```

Viite on luvun 5 monoketju aiempien lukujen funktioista:

```{.python tiedosto="esimerkit/gnuradio/oma/valmistele.py" osa="viite"}
```

Kahta ääntä ei voi verrata näyte näytteeltä sellaisenaan, koska
ketjujen suotimet ovat eripituisia ja viiveet siksi erilaiset.
Vertailu etsii viiveen ristikorrelaatiolla, poistaa sen ja
vahvistuseron ja mittaa, mitä jää jäljelle:

```{.python tiedosto="esimerkit/gnuradio/oma/vertaa.py" osa="kohdista"}
```

```{.tuloste tiedosto="esimerkit/gnuradio/vertailu.odotettu"}
```

![Sama tallenne tutoriaalin omalla vastaanottimella ja GNU Radion
lohkokaaviolla. Vasemmalla äänen spektri, oikealla viiden
millisekunnin ote, josta GNU Radion ääni on siirretty viiveen
verran.](kuvat/gnuradio.png){width=100%}

Testiäänten amplitudit ovat samat kolmen desimaalin tarkkuudella, ja
tehomittarilohkon näyttämä kanavan taso on sama kuin omasta
kanavasuotimesta laskettu. Erot selittyvät suotimilla:

- **Viive.** GNU Radion ääni on 38 näytettä eli 0,8 millisekuntia
  omaa edellä. Kumpikaan ketju ei poista kaikkia suodinviiveitään, ja
  suotimet ovat eripituisia.
- **Kohina.** GNU Radion ketjussa kohinaa on kaistan yläpäässä
  desibelin verran enemmän. Syy on jälkikorostus: GNU Radio tekee sen
  228 kHz:n näytetaajuudella, viite 48 kHz:llä. Bilineaarimuunnos
  vääristää taajuusakselia Nyquistin taajuutta lähestyttäessä, joten
  viitteen suodin vaimentaa 10 kHz:ssä 1,3 dB ja 14 kHz:ssä 2,9 dB
  enemmän kuin analoginen esikuvansa. GNU Radion suodin noudattaa
  esikuvaa tarkemmin.
- **Pilotti.** Spektrissä näkyy GNU Radion äänessä 19 kHz:n pilotin
  jäännös noin 80 dB testiäänten alapuolella. Kaavion äänisuodin
  vaimentaa 19 kHz:ssä 60 dB, viitteen 255 kertoimen suodin 78 dB.
  Suotimen siirtymäkaista (4 kHz) on valinta nopeuden ja vaimennuksen
  välillä.
- **Jäännös.** Kohdistuksen jälkeen aaltomuodot eroavat noin 2 %
  (−34 dB). Viive on poistettu vain kokonaisen näytteen tarkkuudella,
  ja jälkikorostus on tehty eri näytetaajuudella, joten vaiheet eivät
  osu täsmälleen kohdakkain.

Yksi ero ei näy tulosteessa. GNU Radion lähtö ei ole bitilleen sama
ajosta toiseen: peräkkäisten ajojen äänitiedostot erosivat
mittauksessa enimmillään noin $10^{-7}$. Todennäköinen syy on, että
ajastin jakaa virran joka ajossa eri kokoisiin paloihin ja osa
lohkoista pyöristyy palojen rajoilla hieman eri tavoin. Siksi testi
vertaa tuloksesta laskettuja suureita eikä tiedostojen tavuja.

## Lohkon sopimus

Oman lohkon ydin on `work`-metodi. Ajastin antaa sille tulopuskurit ja
lähtöpuskurit, ja metodi palauttaa tuottamiensa lähtönäytteiden
määrän. Esimerkin lohko mittaa tehon desibeleinä ja desimoi. Siinä on
eksponentiaalinen keskiarvo, jonka tila säilyy kutsusta toiseen. Lohkon
logiikka on tavallinen luokka, joka ei tuo GNU Radiota:

```{.python tiedosto="esimerkit/09-lohko/tehomittari.py" osa="lohko"}
```

Logiikan voi siksi testata tavallisella `python3`:lla. Ajastinta
jäljittelevä funktio syöttää lohkolle paloja annettujen kokojen
mukaan, ja testi ajaa saman signaalin kerralla ja hyvin pieninä
vaihtelevina paloina:

```{.python tiedosto="esimerkit/09-lohko/main.py" osa="ajastin"}
```

```{.python tiedosto="esimerkit/09-lohko/main.py" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/09-lohko.odotettu"}
```

Lähdöt ovat samat palojen koosta riippumatta, ja taso seuraa
signaalin kolmea tasoa (−37, −17 ja −27 dBFS) muutaman lähdön
viiveellä.

## Oma lohko GNU Radiossa

GNU Radion lohkoksi logiikka muuttuu kääreellä, joka periytyy
lohkoluokasta, kertoo porttien tyypit ja desimointisuhteen ja
välittää `work`-kutsun. Signaalinkäsittelyä kääreessä ei ole:

```{.python tiedosto="esimerkit/gnuradio/lohkokaavio/tehomittari_gr.py" osa="kaare"}
```

GNU Radion lohkot testataan pienellä lohkokaaviolla: lähteenä on
vektori, nieluna vektori, ja kaavio ajetaan loppuun. Moduuli
`gr_unittest` on Pythonin `unittest` GNU Radion lisäyksillä.

```{.python tiedosto="esimerkit/gnuradio/lohkokaavio/test_tehomittari.py" osa="testi"}
```

Ensimmäinen testi on sama väite kuin edellä, mutta nyt palojen koot
valitsee oikea ajastin. Tuloksen on oltava bitilleen sama kuin
logiikalla, joka saa koko signaalin kerralla. Tässä bittitarkkuus
pätee, koska lohkon tulo tulee suoraan vektorista eikä toisesta
liukulukulohkosta.

Testin kommentti viitteestä on sudenkuoppa, joka kaataa ohjelman
ilman virheilmoitusta: jos Python-lohko luodaan suoraan
`connect`-kutsun argumenttina, Pythonin roskienkeruu voi vapauttaa
olion, vaikka kaavio käyttää sitä vielä. Lohkokaavion luokassa lohko
talletetaan siksi jäseneen (`self.mittari`).

Kun lohko on valmis, sen voi siirtää Pythonista C++:aan
(`gr_modtool`) ilman, että lohkokaavio muuttuu. Usein Python riittää,
koska raskaat operaatiot tehdään NumPyllä taulukoille eikä näyte
kerrallaan. Esimerkin lohko käy kuitenkin palat läpi
Python-silmukassa, joten suurilla näytetaajuuksilla C++ on tarpeen.

## Tagit, viestit ja muut ominaisuudet

- **Tagit** (*stream tags*) liittävät näytevirran tiettyyn kohtaan
  metatietoa, kuten "paketti alkaa tästä" tai "taajuus vaihtui".
  Lohkot välittävät ne eteenpäin, ja nopeutta muuttava lohko siirtää
  tagin paikan suhteensa mukaan.
- **Viestiportit** (*message ports*) välittävät asynkronisia
  viestejä, kuten purettuja paketteja tai ohjauskomentoja. Ne eivät
  kulje näytevirran tahdissa.
- **VOLK** (*Vector-Optimized Library of Kernels*) valitsee ajossa
  prosessorille nopeimman SIMD-toteutuksen.
- **SigMF-tuki**: tallenteet ja metatiedot luvun 2 muodossa
  (`gr-sigmf` ja File Meta Sink).
- **Lisämoduulit**: valmiit WBFM-lohkot sisältävät stereodekooderin,
  ja RDS-purkuun on erillinen moduuli (`gr-rds`).

## GNU Radio vai oma koodi

GNU Radio kannattaa, kun vastaanotin koostuu tavallisista vaiheista
ja sitä halutaan kokeilla nopeasti oikealla radiolla. Laitelähteet,
uudelleennäytteistys, säikeistys ja vastapaine tulevat valmiina, ja
kaavion rakenne on nähtävissä yhdellä silmäyksellä. Hinta on suuri
riippuvuus, kehyksen oma Python-ympäristö ja se, että virhe näkyy
usein vasta ajossa: väärä näytetaajuus tai väärän tyyppinen portti ei
jää kiinni ennen kuin kaavio käynnistetään.

Oma koodi kannattaa, kun algoritmi on itse tutkimuksen kohde, kun
tulos pitää toistaa bitilleen tai kun vastaanotin upotetaan
tuotteeseen, jossa riippuvuuksien määrä ja muistinkulutus ratkaisevat.
Usein käytetään molempia: algoritmi kehitetään ja testataan tallenteilla
tavallisena koodina, kuten tässä tutoriaalissa, ja kääritään lohkoksi
vasta, kun se kytketään radioon.

## Käytännössä

- **Erota logiikka kääreestä.** Pidä signaalinkäsittely tavallisena
  luokkana tai funktiona, jonka voi testata ilman GNU Radiota ja
  laitetta. Kääre vain välittää kutsut.
- **Testaa palojen koko.** Aja lohko yhden näytteen paloina ja
  kokonaisena ja vertaa. Ajastin tuottaa kaikkia kokoja.
- **Vertaa suureita, älä tavuja.** Kokonaisen kaavion lähtö voi erota
  ajosta toiseen viimeisissä biteissä. Testaa amplitudi, taajuus,
  kohinataso ja viive, ja pidä bittitarkat testit yksittäisen lohkon
  tasolla.
- **Aja kaavio ensin tiedostosta.** Tiedostolähteellä ja -nielulla
  kaavio on toistettava ja sen voi ajaa testeissä. Laitelähde
  vaihdetaan tilalle vasta, kun tulos on oikea.
- **Pidä viite Python-lohkoihin.** Talleta jokainen itse kirjoitettu
  lohko muuttujaan tai jäseneen niin kauan kuin kaavio on käytössä.
- **Älä sekoita Python-ympäristöjä.** Aja GNU Radio jakelun
  Pythonilla ja pidä muut työkalut omassa ympäristössään. Tiedosto on
  hyvä rajapinta niiden välillä.
- **Mittaa ylivuodot.** GNU Radion laitelähteet tulostavat
  ylivuodosta merkin `O` (*overrun*). Jos merkkejä tulee, kaavio on
  liian raskas laitteen näytetaajuudelle.

## Itsearviointi

- Osaat selittää GNU Radion lohkokaavion, ajastimen ja vastapaineen
  sekä lohkotyypit `sync_block`, `decim_block`, `interp_block` ja
  `basic_block`.
- Osaat koota FM-vastaanottimen GNU Radion lohkoista Python-ohjelmana,
  ajaa sen tiedostosta tiedostoon ja yhdistää lohkot tämän tutoriaalin
  vaiheisiin.
- Osaat verrata kahden vastaanottimen tulosta: poistaa viiveen ja
  vahvistuseron ja selittää jäljelle jäävät erot suotimilla.
- Osaat kirjoittaa lohkon logiikan niin, että sen voi testata ilman
  GNU Radiota ja että tulos ei riipu palojen koosta.
- Osaat kääriä logiikan GNU Radion lohkoksi ja testata sen
  vektorilähteellä ja -nielulla.
- Osaat selittää, miksi GNU Radio ajetaan jakelun omalla Pythonilla,
  ja tagien, viestiporttien ja VOLK-kirjaston tehtävät.

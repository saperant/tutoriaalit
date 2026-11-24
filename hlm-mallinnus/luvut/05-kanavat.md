# Kanavat ja rajapinnat

Signaali on yksi kanava monista. SystemC:n yleinen kytkentämalli on
*rajapintametodin kutsu* (*interface method call*, IMC): portti on
osoitin rajapintaan, ja moduuli kutsuu portin kautta kanavan metodeja
kuin tavallisia C++-funktioita. Kun `Laskuri` kirjoittaa
`arvo.write(tila)`, se kutsuu signaalin metodia rajapinnan
`sc_signal_out_if` kautta. Tämä luku rakentaa oman kanavan, rajallisen
FIFO-jonon, ja näyttää, miten sama periaate johtaa TLM:n socketeihin.

## Rajapinta, portti ja kanava

Rajapinta on abstrakti luokka, joka periytyy virtuaalisesti luokasta
`sc_interface`. Jonolle tehdään kaksi rajapintaa, jotta kirjoittaja ei
voi lukea eikä lukija kirjoittaa:

```{.cpp tiedosto="esimerkit/06-jono/jono.hpp" osa="rajapinnat"}
```

Virtuaalinen periytyminen on tarpeen, koska sama kanava toteuttaa
molemmat rajapinnat, ja kanavassa saa olla vain yksi `sc_interface`-
kantaluokka. Portti `sc_port<JonoKirjoitus<int>>` hyväksyy kytkennän
mihin tahansa kanavaan, joka toteuttaa rajapinnan; moduuli ei tiedä,
onko toisessa päässä oma jono, SystemC:n `sc_fifo` vai testipenkin
mallikanava.

## Primitiivikanava

Kanavia on kahdenlaisia. *Primitiivikanava* periytyy luokasta
`sc_prim_channel` ja voi osallistua päivitysvaiheeseen: se pyytää
`request_update()`-kutsulla, että simulaattori kutsuu sen `update()`-
metodia arviointivaiheen jälkeen. *Hierarkkinen kanava* on moduuli, joka
toteuttaa rajapinnan; sillä voi olla omia prosesseja ja alimoduuleja,
mutta ei päivitysvaihetta. TLM:n väylämallit ovat hierarkkisia kanavia.

Jono noudattaa signaalin sääntöä: kirjoitettu alkio näkyy lukijalle vasta
päivitysvaiheen jälkeen.

```{.cpp tiedosto="esimerkit/06-jono/jono.hpp" osa="kanava"}
```

Kirjoittaja odottaa, jos jono on täynnä, ja lukija, jos se on tyhjä.
Molemmat odotukset on kirjoitettu `while`-silmukoiksi, koska herätys ei
takaa, että tilaa tai dataa on: kaksi kirjoittajaa voi herätä samasta
tapahtumasta. Laskurit `uudet_` ja `poistetut_` pitävät kirjaa
muutoksista, jotka eivät vielä näy. Ilman niitä lukija voisi lukea
samassa delta-syklissä kirjoitetun alkion, jos simulaattori sattuisi
ajamaan kirjoittajan ensin, ja tulos riippuisi taas ajojärjestyksestä.

Kanavan metodit `kirjoita` ja `lue` kutsuvat `wait()`-funktiota, joten
niitä voi kutsua vain säikeestä. Tämä on *estävä* (*blocking*)
rajapinta. `sc_fifo` tarjoaa lisäksi estämättömät `nb_read` ja `nb_write`,
jotka palauttavat tiedon onnistumisesta, sekä tapahtumat, joita metodit
voivat odottaa.

## Kytkentä ja toiminta

Tuottaja ja kuluttaja näkevät jonon vain porttiensa kautta:

```{.cpp tiedosto="esimerkit/06-jono/main.cpp" osa="moduulit"}
```

Operaattori `->` kutsuu portin kautta kanavan metodia. Kytkentä on sama
kuin signaalille:

```{.cpp tiedosto="esimerkit/06-jono/main.cpp" osa="kytkenta"}
```

```{.tuloste tiedosto="esimerkit/06-jono/odotettu"}
```

Näytteistin tuottaa 10 ns:n välein ja suodin kuluttaa 25 ns:n välein,
joten jono täyttyy. Kahden alkion jonoon mahtuvat näytteet 3 ja 4;
näytteistin pysähtyy kirjoittamaan viidettä 50 ns:n kohdalla ja pääsee
jatkamaan vasta 60 ns:n kohdalla, kun suodin lukee näytteen 3. Siitä
eteenpäin tuottaja kulkee kuluttajan tahdissa: tämä on *vastapaine*
(*backpressure*), jonka rajallinen puskuri aiheuttaa. Simulointi päättyy,
kun suotimen viimeinen odotus päättyy eikä uusia tapahtumia ole.

Jonon syvyys on tyypillinen arkkitehtuuriparametri, jota mallilla
tutkitaan: syvempi jono tasoittaa purskeita mutta maksaa pinta-alaa.
Malli kertoo, kuinka syvä jonon on oltava, jotta tuottaja ei koskaan
pysähdy annetulla kuormalla.

## Valmiit kanavat

| Kanava | Rajapinta | Käyttö |
|----------------|------------------------------------|------------------------------|
| `sc_signal<T>` | `sc_signal_in_if`, `sc_signal_inout_if` | johdin, rekisterin lähtö |
| `sc_buffer<T>` | sama | tapahtuma jokaisesta kirjoituksesta |
| `sc_fifo<T>` | `sc_fifo_in_if`, `sc_fifo_out_if` | rajallinen jono, estävä tai ei |
| `sc_mutex` | `sc_mutex_if` | yhteisen resurssin varaus |
| `sc_semaphore` | `sc_semaphore_if` | rajallinen määrä resursseja |
| `sc_clock` | `sc_signal_in_if<bool>` | kello |

## Portit, exportit ja hierarkia

Hierarkiassa portti voidaan kytkeä ylemmän moduulin porttiin, jolloin
kutsu kulkee läpi kanavaan asti. Vastakkaiseen suuntaan toimii
`sc_export<IF>`: moduuli julkaisee sisällään olevan kanavan rajapinnan,
ja ulkopuolinen portti kytketään exportiin. Näin moduuli voi tarjota
rajapinnan ilman, että käyttäjä tietää sen toteuttavan kanavan.

TLM:n *socket* yhdistää molemmat: aloittajan socketissa on portti, jolla
se kutsuu kohdetta, ja export, jonka kautta kohde voi kutsua takaisin.
Kun luvussa 7 aloittaja kutsuu `socket->b_transport(...)`, se on sama
rajapintametodin kutsu kuin `ulos->kirjoita(nayte)` tässä luvussa.

## Käytännössä

- **Kanava rajapinnan takana.** Moduulit riippuvat rajapinnasta, eivät
  kanavasta. Silloin jonon voi vaihtaa malliin, joka kerää tilastoja tai
  injektoi virheitä, eikä moduuleihin tarvitse koskea.
- **Päivitysvaihe, jos kanava välittää tietoa samalla hetkellä.** Jos
  kanavan tilaa voi lukea ja kirjoittaa samassa delta-syklissä,
  primitiivikanava ja `request_update` tekevät tuloksesta
  deterministisen. Jos kanava aina viivästää tiedon ajastetusti, kuten
  väylämalli, päivitysvaihetta ei tarvita.
- **Estävä vai estämätön.** Estävä rajapinta tekee kutsujasta
  yksinkertaisen, mutta vaatii säikeen. Estämätön rajapinta sopii myös
  metodeille, ja sen avulla mallinnetaan laitteiston kättely
  (*valid/ready*). TLM-2.0 tarjoaa molemmat (luvut 7 ja 10).
- **`sc_fifo` riittää usein.** Oma kanava kannattaa, kun tarvitaan
  jotain, mitä valmiissa ei ole: tilastot, prioriteetit, tyhjennys tai
  rajapinta, joka vastaa tulevan laitteiston kättelyä.

## Itsearviointi

- Osaat määritellä rajapinnan, toteuttaa sen kanavassa ja kytkeä
  moduulin portin kanavaan.
- Osaat selittää primitiivikanavan ja hierarkkisen kanavan eron ja
  milloin `request_update()` tarvitaan.
- Osaat tulkita jonon täyttymisen vastapaineena ja käyttää mallia jonon
  syvyyden valintaan.
- Osaat kertoa, miten `sc_port`, `sc_export` ja TLM:n socket liittyvät
  toisiinsa.

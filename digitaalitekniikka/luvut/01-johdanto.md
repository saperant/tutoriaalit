# Johdanto {.runko-johdanto}

Digitaalitekniikka on oppi siitä, miten kahdesta jännitetasosta
rakennetaan laskevia ja muistavia koneita. Jokainen suoritin,
muistipiiri, verkkokortti ja FPGA koostuu samoista rakennuspalikoista:
porteista, jotka laskevat Boolen funktioita, ja kiikuista, jotka
muistavat bitin kellon reunalta seuraavalle. Tämä tutoriaali käy ne läpi
alhaalta ylös: lukujen esityksestä portteihin, porteista summaimiin ja
ALUun, kiikuista rekistereihin ja tilakoneisiin, ja lopuksi siihen,
mikä rajoittaa piirin kellotaajuutta.

Tutoriaali on laitteistoalueen perusta. Se valmistaa seuraaviin
taitoihin:

- *RTL-suunnittelu SystemVerilogilla* ja *RTL-suunnittelu VHDL:llä*:
  suurten piirien kuvaaminen rekisterinsiirtotasolla ja
  synteesikelpoinen koodaustyyli.
- *Assembly* ja *Tietokonearkkitehtuuri*: miten käskyt suoritetaan
  datapolussa, jonka rakennuspalikat opitaan tässä.
- *Miten tietokone laskee*: lukujen esitys ohjelmoijan näkökulmasta.
  Tässä samat asiat nähdään laitteiston kannalta: miksi kahden
  komplementti on summaimelle helppo ja mistä ylivuotolippu tulee.

## Esitiedot ja rajaus

Esitietona on *Diskreetti matematiikka*: propositiologiikka, joukot ja
induktio. Ohjelmointitaitoa tarvitaan sen verran, että Python-
esimerkkien lukeminen onnistuu.

Tutoriaali pysyy porttien ja rekisterien tasolla. Sen ulkopuolelle
jäävät:

- SystemVerilogin syntaksi ja synteesikelpoinen koodaustyyli, muistit,
  FIFOt ja kellotusalueiden ylitys: taidot *RTL-suunnittelu
  SystemVerilogilla* ja *RTL-suunnittelu VHDL:llä*
- synteesi, sijoittelu ja ajoitusanalyysi oikeilla työkaluilla:
  *FPGA-toteutus* ja *ASIC-toteutus*
- transistorin sähköinen toiminta, jännitteet ja virrat: *Elektroniikan
  perusteet ja SPICE*
- liukuluvut, kertolaskun ja jakolaskun algoritmit sekä pyöristys:
  *Miten tietokone laskee*.

## Abstraktiotasot

Digitaalinen järjestelmä kuvataan usealla tasolla. Jokainen taso
piilottaa alemman tason yksityiskohdat ja tarjoaa ylemmälle
yksinkertaisemman mallin.

| Taso | Rakennuspalikat | Esimerkki |
|------|-----------------|-----------|
| Järjestelmä | suorittimet, muistit, väylät | järjestelmäpiiri |
| Arkkitehtuuri | käskykanta, rekisterit | RISC-V |
| Rekisterinsiirto (RTL) | rekisterit ja niiden välinen logiikka | ALU ja ohjaus |
| Porttitaso | AND, OR, NOT, kiikut | täyssummain |
| Piiritaso | transistorit, jännitteet | CMOS-NAND-portti |
| Fysiikka | puolijohteet, johtimet | piisiru |

Tämä tutoriaali liikkuu porttitason ja rekisterinsiirtotason välillä ja
käväisee piiritasolla luvussa 3. Kahden tason välinen siirtymä on
taidon ydin: porttitason ymmärrys kertoo, miksi RTL-kuvaus on nopea tai
hidas, suuri tai pieni.

Digitaalinen abstraktio on itsessään malli. Todellisuudessa jännite on
jatkuva suure, ja portin lähdön muuttuminen vie aikaa. Porttimalli
toimii, koska portit *palauttavat* tason: kohinainen, hieman väärä
jännite tulossa tuottaa lähtöön puhtaan nollan tai ykkösen. Malli
pettää vain, kun signaali muuttuu juuri silloin, kun sitä luetaan.
Siihen palataan luvussa 8 (metastabiilisuus).

## Työkalut ja esimerkit

Tutoriaalin esimerkit ovat kahta lajia:

- **Python-mallit** näyttävät periaatteen: totuustaulut, Boolen algebran
  lait, Quine–McCluskeyn sieventäminen, ajoitusanalyysi ja oma pieni
  *tapahtumapohjainen porttisimulaattori*, joka näyttää viiveet ja
  hasardit. Ne tarkistetaan ruffilla ja mypyllä (`--strict`).
- **SystemVerilog-toteutukset** ovat oikeaa laitteistonkuvausta, joka
  simuloidaan Verilatorilla. Jokaisella on itsetarkistava testipenkki,
  joka vertaa piiriä toisella tavalla laskettuun viitteeseen.

SystemVerilogin syntaksi opetetaan perusteellisesti taidossa
*RTL-suunnittelu SystemVerilogilla*. Tässä riittää lukutaito:
`module` on piirilohko, `assign` ja `always_comb` kuvaavat
kombinaatiologiikkaa, `always_ff @(posedge clk)` kiikkuja, ja
`testipenkki`-moduuli syöttää piirille arvoja ja tarkistaa vastaukset.

Kaikki esimerkit ajetaan kehityskontissa (`.devcontainer/digitaalitekniikka`):

```text
make -C digitaalitekniikka testaa
```

Ensimmäinen esimerkki näyttää, mistä tutoriaalissa on kyse. Kolme
invertteriä on ketjussa, ja jokaisen viive on kaksi aikayksikköä. Kun
tulo `a` muuttuu hetkellä 2, muutos näkyy lähdössä `d` vasta hetkellä 8.

```{.python tiedosto="esimerkit/porttisim.py" osa="ketju"}
```

```{.tuloste tiedosto="esimerkit/porttisim.odotettu"}
```

Totuustaulun mukaan `d` on yksinkertaisesti `a`:n komplementti. Ajan
kanssa tarkasteltuna se on komplementti *kuuden aikayksikön
viiveellä*, ja välissä se on hetken väärin. Juuri tämä ero
totuustaulun ja todellisuuden välillä tekee digitaalisuunnittelusta
insinöörityötä.

## Lukuohje

Luvut 2–4 ovat perusta: luvut bitteinä, portit ja Boolen algebra.
Luvut 5 ja 6 rakentavat niistä kombinaatiologiikkaa summaimiin ja
ALUun asti. Luku 7 tuo mukaan ajan: viiveet ja hasardit. Luvut 8–10
käsittelevät muistia: salvat, kiikut, rekisterit ja tilakoneet. Luku 11
yhdistää kaiken ajoitusanalyysiksi, ja luku 12 kokoaa muistit ja
datapolun pieneksi laskevaksi koneeksi.

Jokaisen luvun lopussa on *Käytännössä*-osio, joka kertoo, miten
suunnittelijat asiaa työssään käyttävät, ja *Itsearviointi*, jonka
väitteistä näkee, voiko luvun ohittaa.

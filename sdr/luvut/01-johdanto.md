# Johdanto {.runko-johdanto}

Perinteisessä radiovastaanottimessa jokainen toiminto on oma
piirinsä: viritin valitsee kanavan, välitaajuussuotimet rajaavat sen,
ilmaisin purkaa modulaation ja stereodekooderi erottaa kanavat.
**Ohjelmistoradiossa** (*software-defined radio*, SDR) laitteisto
tekee vain välttämättömän eli vahvistaa, sekoittaa halutun kaistan
lähelle nollataajuutta ja näytteistää sen. Kaikki muu on ohjelmistoa,
joka käsittelee kompleksisia **IQ-näytteitä**. Sama 30 euron
USB-tikku voi siksi olla FM-radio, lentokoneiden ADS-B-vastaanotin,
sääanturien kuuntelija tai spektrianalysaattori.

Tutoriaali rakentaa ohjelmistoradion vastaanotinketjut alusta
loppuun. Ketjut ovat FM-stereovastaanotin RDS-tyyppisine
datakanavineen ja digitaalinen pakettivastaanotin ISM-kaistan
anturiradioille. Laskenta tehdään ensin Pythonilla, ja ketjun
raskain osa toteutetaan sen jälkeen lohkoittain C++:lla.

## Ohjelmistoradion rakenne

Tyypillisen SDR-vastaanottimen laitteisto on suoramuunnosvastaanotin
(*zero-IF*):

1. **Antenni ja etuaste.** Pienikohinainen vahvistin (*LNA*) ja
   kaistanpäästösuodin. Etuasteen kohinaluku määrää herkkyyden
   (luku 10).
2. **IQ-sekoitin.** Paikallisoskillaattori viritetään
   keskitaajuudelle $f_c$, ja sekoitin tuottaa kaksi haaraa, joiden
   oskillaattorit ovat 90 asteen vaihe-erossa. Haarat ovat I ja Q.
3. **Alipäästösuotimet ja ADC.** Molemmat haarat näytteistetään
   samalla taajuudella $f_s$, ja näytteet kulkevat USB:llä
   tietokoneelle.

```{.dot otsikko="Suoramuunnosvastaanotin. Ylärivi on laitteisto, alarivi ohjelmisto, jota tämä tutoriaali käsittelee."}
digraph sdr {
  rankdir=TB; nodesep=0.3; ranksep=0.35;
  node [shape=box, fontsize=10];
  antenni [label="antenni", shape=plaintext];
  lna [label="LNA ja\nkaistanpäästö"];
  sekoitin [label="IQ-sekoitin\n(oskillaattori fc)"];
  adc [label="alipäästö ja\nADC (fs), USB"];
  luku [label="IQ-näytteet"];
  kanava [label="kanavan\nvalinta"];
  ilmaisin [label="ilmaisin"];
  ulos [label="ääni\ntai bitit", shape=plaintext];
  { rank=same; antenni -> lna -> sekoitin -> adc; }
  adc -> luku;
  { rank=same; ulos -> ilmaisin -> kanava -> luku [dir=back]; }
}
```

Kompleksinen näyte $z[n] = I[n] + iQ[n]$ kuvaa kaistaa
$f_c - f_s/2 \ldots f_c + f_s/2$. Negatiiviset taajuudet ovat
keskitaajuuden alapuolella olevia signaaleja, eivät peilikuvia
(taito *Digitaalinen tiedonsiirto*). Laitteiston epäideaalisuudet
näkyvät suoraan näytteissä: tasakomponentti, haarojen epätasapaino,
kiteen taajuusvirhe ja 8 bitin kvantisointi. Ne käsitellään
luvuissa 2 ja 3.

## Synteettiset tallenteet

Kaikki tutoriaalin IQ-tallenteet tuotetaan ohjelmalla. Oikea
radiotallenne riippuisi paikasta, ajasta, antennista ja laitteesta,
eikä sen sisältöä voisi tarkistaa. Lisäksi tallenne voi sisältää
viestintää, jota ei saa levittää (luku 10). Synteettinen tallenne on
toistettava ja testattava. Lähetin on tehty samoin parametrein kuin
oikea lähetys, joten vastaanotin toimii sellaisenaan oikean laitteen
näytteillä, kun tallennusmuoto ja näytetaajuus täsmäävät.

## Ensimmäinen esimerkki: mitä kaistalla on?

RTL-SDR-tikku on viritetty 98,0 MHz:iin, ja näytetaajuus on
912 kS/s. Tallenteessa on kaksi FM-asemaa ja kapea kantoaalto.
Asemien ohjelmana on kaistarajoitettu kohina, joka muistuttaa
spektriltään musiikkia.

```{.python tiedosto="esimerkit/01-spektri.py" osa="tallenne"}
```

Ensimmäinen askel on aina spektri. Welchin menetelmä keskiarvoistaa
lyhyiden FFT-ikkunoiden spektrit. Tulos on kohinaisempaa kuin yksi
pitkä FFT, mutta tehotiheyden vaihtelu tasoittuu. Kohinalattiaksi
otetaan mediaani, koska suurin osa kaistasta on tyhjää.

```{.python tiedosto="esimerkit/01-spektri.py" osa="spektri"}
```

Kun signaalit erottuvat lattiasta, ne voi etsiä automaattisesti.
Kynnyksen ylittävät taajuusbinnit yhdistetään kaistoiksi, ja kaistan
keskitaajuus lasketaan tehopainotettuna keskiarvona.

```{.python tiedosto="esimerkit/01-spektri.py" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/01-spektri.odotettu"}
```

![Synteettisen tallenteen tehospektri. Vahva FM-asema on 98,2 MHz:ssä,
heikompi 97,75 MHz:ssä ja kapea kantoaalto 97,94 MHz:ssä. Kohinalattia
on tasainen, koska tallenteessa ei ole RTL-SDR:n tasakomponenttia eikä
suotimen reunoja (luku 3).](kuvat/kaista.png){width=100%}

Vahvan aseman kaista on noin 210 kHz, mikä vastaa FM-yleisradion
200 kHz:n kanavaväliä. Kantoaalto on yhden binnin levyinen. Heikompi
asema on 20 dB vahvaa heikompi, mutta erottuu silti selvästi: 8
bitin näytteillä dynamiikka-alue riittää tähän (luku 2).

## Esitiedot ja rajaus

| Luku | Aihe |
|------|------|
| 2 | IQ-näytteet, tallennusmuodot, SigMF ja ADC:n dynamiikka |
| 3 | Tasakomponentti, IQ-epätasapaino, AGC ja kiteen virhe |
| 4 | NCO, sekoitus, monivaiheinen desimointi ja suodinpankit |
| 5 | FM-ilmaisimet, kynnysilmiö ja monovastaanotin |
| 6 | Stereo, pilotin vaihelukko ja RDS-tyyppinen data |
| 7 | GFSK-pakettivastaanotin: haku, taajuusvirhe, ajoitus ja CRC |
| 8 | Reaaliaikainen lohkokäsittely C++:lla ja vertailu Pythoniin |
| 9 | GNU Radio: lohkokaaviot ja omat lohkot |
| 10 | Laitteet, herkkyys ja radiolupasäännöt |

Esitietoina oletetaan taito *Digitaalinen tiedonsiirto*, jossa
käsitellään IQ-esitys, modulaatiot, symbolitahdistus ja
kanavakoodaus, sekä *Digitaalinen signaalinkäsittely*, jossa
käsitellään suotimien suunnittelu ja monitaajuuskäsittely. Tässä
tutoriaalissa niitä ei johdeta uudelleen, vaan niistä kootaan
toimivia vastaanottimia ja niihin lisätään oikean radion
käytännöt.

Lähetin on mukana vain tallenteiden tuottajana: lähetinketjun omat
kysymykset (spektrimaski, tehovahvistin, D/A-muunnos) rajataan pois.
Radiotekniikka antenneineen ja etenemismalleineen on taidossa
*Tietoliikennetekniikka*, ja vastaanottimen toteutus FPGA:lla taidossa
*DSP-algoritmien laitteistototeutus*.

Esimerkit tarvitsevat Python 3.12:n, NumPyn ja SciPyn. C++-esimerkit
käännetään C++23:lla (GCC 14 tai Clang 20). Jokainen esimerkki
ajetaan testeissä kiinteällä satunnaissiemenellä, ja tulostetta
verrataan tallennettuun. Hakemistojen `fm/` ja `paketti/` ohjelmilla
on lisäksi pytest-testit. Yksittäinen esimerkki ajetaan komennolla
`python3 esimerkit/01-spektri.py` ja hakemistoesimerkki komennolla
`python3 esimerkit/fm/main.py`.

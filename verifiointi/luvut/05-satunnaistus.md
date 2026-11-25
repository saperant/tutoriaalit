# Satunnaistus ja siemenet

Neljän paikan FIFOssa on vähän tiloja, mutta jo sen ohjatussa testissä
jäi huomaamatta samanaikainen kirjoitus ja luku. Todellisessa lohkossa
on kymmeniä tuloja ja tuhansia tiloja, eikä kukaan pysty luettelemaan
kaikkia kiinnostavia yhdistelmiä käsin. *Rajoitettu satunnaistus*
(constrained random) kääntää työnjaon: verifioija kuvaa, millainen
ärsyke on sallittua ja mitä halutaan painottaa, ja kone arpoo
yhdistelmät. Luvun 3 testipenkki löysi kaikki kolme FIFOn vikaa
juuri siksi, että generaattori tuotti tilanteita, joita kukaan ei
kirjoittanut erikseen. Tässä luvussa satunnaistus lisätään myös
luvun 4 Python-ympäristöön.

## Rajoitteet ja painot

Satunnaistuksen kaksi työkalua ovat *rajoitteet*, jotka rajaavat pois
laittoman ärsykkeen, ja *painot*, jotka ohjaavat jakaumaa kohti
kiinnostavia tilanteita. Luvun 3 generaattori käyttää painoja:
40 % kirjoituksia, 30 % lukuja, 20 % molempia ja 10 %
tyhjäkäyntiä. Kirjoituksia on enemmän kuin lukuja, joten jono täyttyy
usein, ja samanaikaisia toimenpiteitä on tarpeeksi, jotta
`BUGI_SAMANAIKAINEN` löytyy heti.

SystemVerilogissa rajoitteet kirjoitetaan tavallisesti luokan
`constraint`-lohkoon, ja ratkaisija arpoo arvot, jotka toteuttavat ne
kaikki:

```text
class toimenpide;
    rand bit       push, pop;
    rand bit [7:0] data;
    constraint painot  { push dist {1 := 6, 0 := 4}; }
    constraint ei_tyhjasta { tyhja -> !pop; }
endclass
...
if (!t.randomize() with { data inside {[8'h10:8'h1f]}; }) $fatal;
```

Rajoitteet voivat viitata toisiinsa, ja ratkaisija löytää
ratkaisun, vaikka rajoitteita on kymmeniä. Kaupalliset simulaattorit
tukevat rajoitteita täysin. Tämän tutoriaalin Verilator 5.020 arpoo
luokan `rand`-kentät, mutta jättää rajoitteet huomiotta ja varoittaa
siitä (CONSTRAINTIGN). Uudemmat versiot ratkaisevat rajoitteita
ulkoisella SMT-ratkaisijalla. Siksi esimerkit arpovat arvot funktioilla
`$urandom` ja `$urandom_range` ja kirjoittavat rajoitteet tavallisina
ehtoina. Pythonissa tilanne on sama: `random`-moduuli arpoo, ja
rajoitteet ovat koodia. Monimutkaisiin rajoitteisiin on
Python-kirjasto PyVSC.

## Laillinen ja laiton ärsyke

Rajoitteiden tehtävä on estää ärsyke, jota oikea ympäristö ei koskaan
tuota. Väylän isäntä ei esimerkiksi peru siirtoa kesken kättelyn, joten
sellaista ei arvota. Jos rajoite on kuitenkin tiukempi kuin määrittely,
se piilottaa vikoja. FIFOn määrittely sallii lukemisen tyhjästä jonosta
(luku jätetään huomiotta), joten luku tyhjästä on laillinen ja tärkeä
testattava tilanne.

Python-ympäristön generaattori jäljittelee yleistä virhettä: se on
"kohtelias" eikä lue jonosta, jonka se arvioi tyhjäksi. Arvio on oma
laskuri, koska generaattori ei näe DUT:n tilaa:

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="generaattori"}
```

Testi `satunnaistettu` ajaa generaattorin tuottamat 500 toimenpidettä
luvun 4 apufunktiolla:

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="satunnainen"}
```

Kun FIFOssa on vika `BUGI_SAMANAIKAINEN`, ohjattu testi menee läpi
mutta satunnaistettu testi kaatuu, koska vain se kirjoittaa ja lukee
yhtä aikaa osittain täyteen jonoon. Raportin loppu kertoo
ensimmäisen virheen (kolmas testi `kulmat` esitellään seuraavassa
luvussa):

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-samanaikainen.odotettu" alkaen="läpi 2"}
```

Ylirajoitettu generaattori ei kuitenkaan koskaan tuota tilannetta,
jossa `BUGI_TYHJA` näkyy, ja se vika jää löytymättä, vaikka testi ajaa
satoja jaksoja. Luku 6 näyttää, miten kattavuus paljastaa tällaisen
aukon.

Laskurissa on lisäksi oma vikansa: kun jono on täynnä ja generaattori
kirjoittaa ja lukee yhtä aikaa, FIFO hylkää kirjoituksen, mutta arvio
ei vähene. Arvio jää todellista suuremmaksi, ja generaattori lukee
myöhemmin tyhjästä jonosta, vaikka sen ei pitänyt. Siksi testin
tulos riippuu siemenestä, mikä nähdään luvun 10 regressiossa:
siemenellä 1 tyhjästä ei lueta koskaan, muilla siemenillä muutaman
kerran.

## Siemenet

Tietokoneen satunnaisluvut ovat näennäissatunnaisia: generaattori
tuottaa aina saman jonon samasta alkuarvosta, *siemenestä*. Se on
verifioinnille välttämätöntä. Kun satunnaistesti löytää vian, sama
siemen toistaa saman ajon jaksolleen, ja vian voi tutkia, korjata ja
todeta korjatuksi. Testi, jota ei voi toistaa, on lähes hyödytön.

Esimerkkien testipenkki lukee siemenen argumentista ja alustaa sillä
säikeen satunnaislukugeneraattorin:

```text
void'($value$plusargs("siemen=%d", siemen));
void'($urandom(siemen));
```

Python-testeissä siemen tulee ympäristömuuttujasta `SIEMEN`, ja testi
luo oman generaattorin `random.Random(siemen)`. Oma olio on parempi
kuin moduulin yhteinen generaattori, koska muut kirjastot eivät voi
kuluttaa sen lukuja ja muuttaa jonoa.

Sama siemen tuottaa saman ajon. Kohde `siemenet` ajaa siemenen 2
kahdesti ja vertaa molemmat samaan odotettuun tulosteeseen:

```{.tuloste tiedosto="esimerkit/odotetut/siemen-2.odotettu"}
```

Toinen siemen tuottaa toisenlaisen ajon:

```{.tuloste tiedosto="esimerkit/odotetut/siemen-3.odotettu"}
```

Regressio ajaa saman testin monella siemenellä (luku 10). Siemen
tulostetaan aina lokiin, jotta epäonnistuneen ajon voi toistaa.
Siemenen voi valita kiinteästi (toistettava regressio) tai esimerkiksi
kellonajasta (uusia tilanteita joka yö), mutta molemmissa tapauksissa
se kirjataan.

## Satunnaisstabiilisuus

Siemen toistaa ajon vain, jos testipenkki pysyy samana. Jos testiin
lisätään yksi `$urandom`-kutsu, kaikki sen jälkeiset luvut siirtyvät,
ja sama siemen tuottaa eri ajon. SystemVerilog lieventää ongelmaa
*satunnaisstabiilisuudella* (random stability): jokaisella säikeellä
ja luokan oliolla on oma generaattorinsa, joka alustetaan
luontijärjestyksen mukaan. Uuden olion lisääminen ei siksi muuta
olemassa olevien olioiden lukuja. Pythonissa saman saa aikaan
antamalla jokaiselle generaattorille oman `random.Random`-olion, jonka
siemen johdetaan testin siemenestä.

Käytännön seuraus: kun testipenkkiä muutetaan, vanhan vian toistanut
siemen ei välttämättä enää toista sitä. Siksi löydetylle vialle
kirjoitetaan usein ohjattu testi tai kattavuuskohde, joka varmistaa,
että tilanne syntyy jatkossakin siemenestä riippumatta.

## Jakauman muoto

Tasainen satunnaisuus tuottaa harvoin äärimmäisiä tiloja. Jos 1024
paikan FIFOa kirjoitetaan ja luetaan kumpaakin todennäköisyydellä
puolet, jonon määrä on satunnaiskulku. Alla olevassa simulaatiossa se
ei 200 000 jakson aikana käy kertaakaan täynnä, kun taas
täyttö- ja tyhjennysvaiheista rakennettu generaattori käy molemmissa
päissä kymmeniä kertoja.

![Jonon täyttöaste 1024 paikan FIFOssa: tasainen satunnaisuus pysyy
kaukana täydestä, vaiheistettu generaattori käy toistuvasti
kummassakin päässä (`kuvat/piirra.py`).](kuvat/tayttoaste.png){width=85%}

Siksi generaattori rakennetaan usein *vaiheista* tai *sekvensseistä*:

- täyttövaihe, jossa kirjoitetaan, kunnes jono on täynnä, ja
  tyhjennysvaihe vastaavasti;
- purskeet, joissa sama toimenpide toistuu satunnaisen määrän kertoja;
- painojen vaihtaminen testin aikana tai testikohtaisesti.

Seuraavan luvun testi `kulmat` on tällainen: se täyttää jonon yli
rajan, kirjoittaa ja lukee täyteen jonoon ja lukee tyhjästä jonosta,
ja satunnaisuus vaikuttaa vain määriin ja dataan. UVM:ssä (luku 9)
sekvenssit ovat juuri tätä varten omia luokkiaan, joita testi voi
yhdistellä.

## Käytännössä

- **Rajoitteet määrittelystä, ei toteutuksesta.** Rajoite saa kieltää
  vain sen, mitä oikea ympäristö ei voi tehdä. Jokainen ylimääräinen
  rajoite on paikka, jossa vika voi piiloutua.
- **Painot kulmiin.** Täysi ja tyhjä jono, maksimiarvot, samanaikaiset
  tapahtumat ja nollaus kesken toiminnan saavat enemmän painoa kuin
  niiden luonnollinen osuus.
- **Siemen lokiin ja komentoriville.** Ajo, jonka siementä ei tiedetä,
  ei ole toistettavissa. Siemenen ja testin nimen on riitettävä ajon
  toistamiseen.
- **Oma generaattori jokaiselle virralle.** Kun datalla, toimenpiteillä
  ja viiveillä on omat generaattorinsa, yhden muuttaminen ei siirrä
  muiden lukuja.
- **Löydetty vika ohjatuksi testiksi tai kattavuuskohteeksi.**
  Siemen voi lakata toistamasta vikaa, kun testipenkki muuttuu.
- **Satunnaistus ei korvaa ajattelua.** Generaattori tuottaa vain sitä,
  mitä sen jakauma sallii. Kattavuus (luku 6) kertoo, mitä se
  todella tuotti.

## Itsearviointi

- Osaat selittää, mitä rajoitteet ja painot tekevät ja miten
  ylirajoitettu generaattori piilottaa vikoja.
- Osaat erottaa laillisen ja laittoman ärsykkeen määrittelyn
  perusteella.
- Osaat tehdä satunnaistestistä toistettavan siemenen avulla ja
  kirjata siemenen niin, että ajo voidaan toistaa.
- Osaat selittää satunnaisstabiilisuuden ja sen, miksi testipenkin
  muutos voi muuttaa saman siemenen ajon.
- Osaat muotoilla generaattorin jakauman niin, että harvinaiset tilat
  syntyvät.

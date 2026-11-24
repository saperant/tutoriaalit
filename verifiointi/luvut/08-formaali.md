# Formaali verifiointi

Simulointi tarkistaa ne tilanteet, jotka ärsyke tuottaa. Formaali
verifiointi kysyy toisin päin: onko olemassa *mitään* syötejonoa, joka
rikkoo väitteen? Työkalu muuntaa suunnitelman ja väitteet
loogiseksi kaavaksi, ja SAT- tai SMT-ratkaisija etsii kaavalle
ratkaisua. Jos ratkaisu löytyy, se on vastaesimerkki: syötejono, joka
vie suunnitelman virhetilaan. Jos ratkaisua ei ole, väite pätee
kaikilla syötteillä.

Formaali tarkistus löytää kulmatapaukset, joita kukaan ei keksinyt, ja
antaa lyhimmän mahdollisen polun vikaan. Sen hinta on laskennan määrä:
tilojen määrä kasvaa eksponentiaalisesti rekisterien määrän mukana,
joten menetelmä sopii lohkoille ja ominaisuuksille, ei koko piirille.

## Väite, oletus ja kattavuus

Formaalissa tarkistuksessa ominaisuuksilla on kolme roolia:

| Rooli | Lause | Ratkaisijalle |
|-------|-------|---------------|
| väite | `assert` | todista, että tämä pätee aina |
| oletus | `assume` | käytä vain syötteitä, joilla tämä pätee |
| kattavuus | `cover` | etsi syötejono, jolla tämä toteutuu |

Oletukset ovat formaalin tarkistuksen rajoitteita: ne kuvaavat
ympäristöä, kuten "pyyntö pysyy voimassa, kunnes se myönnetään".
Ilman oletuksia ratkaisija käyttää myös syötteitä, joita oikea
ympäristö ei tuota, ja löytää vääriä vastaesimerkkejä. Liian tiukka
oletus taas sulkee pois oikeita tilanteita ja tekee väitteestä
tyhjästi toden. Siksi oletusten rinnalle kirjoitetaan
kattavuuskohteita: jos `cover` ei toteudu, oletukset ovat liian tiukat.

Samassa lohkossa väite ja oletus vaihtavat rooleja: kun lohko
verifioidaan, sen syötteitä koskevat säännöt ovat oletuksia; kun sitä
käyttävä lohko verifioidaan, samat säännöt ovat väitteitä. Tämä on
*oletus–takuu*-päättely (assume–guarantee).

## Kolme tarkistusta

**Rajattu mallintarkistus** (bounded model checking, BMC) purkaa
suunnitelman k kellojakson mittaiseksi kaavaksi alkutilasta lähtien
ja kysyy, rikkoutuuko jokin väite millään näistä jaksoista. BMC löytää
kaikki viat, jotka näkyvät k jakson kuluessa nollauksesta, ja
vastaesimerkki on aina lyhin mahdollinen. Se ei kerro mitään
syvemmistä tiloista.

**Induktio** (k-induktio, *prove*) todistaa väitteen kaikille
syvyyksille kahdessa osassa. Perustapaus on BMC k jaksoon. Induktioaskel
kysyy: jos väitteet pätevät *missä tahansa* k peräkkäisessä tilassa,
voivatko ne rikkoutua seuraavassa? Askeleen tila ei ala nollauksesta
vaan mistä tahansa tilasta, myös sellaisesta, johon nollauksesta ei
voi päästä. Jos askel onnistuu, väite pätee aina.

**Kattavuus** (*cover*) etsii lyhimmän syötejonon, joka toteuttaa
kunkin `cover`-ehdon. Se osoittaa, että tila on saavutettavissa, ja
tuottaa samalla valmiin esimerkkiajon, jota voi katsoa
aaltomuotona.

## Työkalut

Avoimen lähdekoodin formaali ketju on Yosys: se lukee
SystemVerilogin, muuntaa sen SMT2-kaavaksi, ja yosys-smtbmc ajaa
ratkaisijaa (Z3, Yices, Boolector, Bitwuzla). Tavallinen käyttöliittymä
on SymbiYosys (`sby`), joka lukee tehtävätiedoston:

```{.ini tiedosto="esimerkit/formaali/fifo.sby"}
```

Ubuntu 24.04:ssä ei ole SymbiYosys-pakettia, joten esimerkit tekevät
saman kahdella komennolla. Yosys lukee lähteen valitsimella
`-formal`, joka määrittelee makron `FORMAL` ja ottaa käyttöön
lauseet `assume` ja `cover`. `prep` muodostaa suunnitelman, `async2sync`
ja `dffunmap` muuntavat rekisterit SMT-mallille sopiviksi, ja
`write_smt2` kirjoittaa kaavan:

```{.python tiedosto="esimerkit/tyokalut/formaali.py" osa="yosys"}
```

yosys-smtbmc ajaa ratkaisijaa valitussa tilassa (oletus BMC, `-i`
induktio, `-c` kattavuus) ja kirjoittaa vastaesimerkin VCD-tiedostoon:

```{.python tiedosto="esimerkit/tyokalut/formaali.py" osa="smtbmc"}
```

Työkalu lyhentää tulosteen ja tulostaa jäljen taulukkona, jossa on
yksi rivi kellojaksoa kohden. Taulukko on luettava kuin aaltomuoto:
jokaisella rivillä näkyvät syötteet ja rekisterien arvot ennen
jakson lopun reunaa.

Kaupallisilla työkaluilla (Jasper, VC Formal, Questa Formal) ja
Yosysin kaupallisella versiolla on täysi SVA-tuki. Avoin Yosys 0.33
ymmärtää välittömät väitteet ja `$past`- ja `$stable`-funktiot, mutta
ei kellotettuja `assert property` -lauseita. Siksi tämän luvun
ominaisuudet on kirjoitettu `always`-lohkoihin.

## Alkutila

Simulaattorissa rekisterit alkavat arvosta `x`, ja testipenkki
nollaa lohkon. Formaalissa mallissa rekisterien alkuarvot ovat
vapaita: ratkaisija saa valita ne. Ilman rajoitusta ratkaisija aloittaa
esimerkiksi tilasta, jossa `maara` on 7, ja väite rikkoutuu heti.
Siksi ominaisuudet aloitetaan oletuksella, että ensimmäisellä jaksolla
nollaus on päällä. Rekisteri `alku` on ainoa, jolle annetaan alkuarvo
(Yosys käyttää alustusta mallin alkutilana), ja väitteet tarkistetaan
vasta sen jälkeen.

## FIFOn ominaisuudet

FIFOn ominaisuudet ovat sen lähteessä `ifdef FORMAL` -lohkossa, jonka
simulaattorit ohittavat:

```{.systemverilog tiedosto="esimerkit/rtl/fifo.sv" osa="formaali"}
```

Syötteistä ei oleteta mitään nollauksen jälkeen, koska FIFOn
määrittely sallii kaiken: kirjoituksen täyteen ja luvun tyhjään.
Ehjä FIFO läpäisee BMC:n kymmeneen jaksoon:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-bmc.odotettu"}
```

Kymmenen jaksoa riittää täyttämään jonon ja kierrättämään osoittimet
ympäri, joten kaikki FIFOn toiminnot tulevat käytetyiksi. Syvempiä
tiloja BMC ei kuitenkaan tarkista; ne käsitellään induktiolla.

## Vastaesimerkit

Jokainen istutettu vika löytyy, ja jokaisen vastaesimerkki on lyhin
mahdollinen. `BUGI_TAYSI` vaatii kolme kirjoitusta, jotta lippu nousee
liian aikaisin:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-taysi.odotettu"}
```

`BUGI_TYHJA` vaatii vain yhden luvun tyhjästä jonosta. Viimeisellä
rivillä `rst` on 1, mutta sillä ei ole merkitystä: väite koskee
jakson alun tilaa, ja ratkaisija valitsee viimeisen jakson syötteet
vapaasti.

```{.tuloste tiedosto="esimerkit/odotetut/formaali-tyhja.odotettu"}
```

`BUGI_SAMANAIKAINEN` näkyy askeleella 3, jolla määrä on 2, vaikka
edellisellä jaksolla kirjoitettiin ja luettiin yhtä aikaa. Kellotetun
lohkon väite tarkistetaan kellon reunalla, ja yosys-smtbmc ilmoittaa
sen seuraavalla askeleella, joten jäljessä on vielä askel 4.

```{.tuloste tiedosto="esimerkit/odotetut/formaali-samanaikainen.odotettu"}
```

Vertaa vastaesimerkkejä simulaation tuloksiin. Ohjattu testi ei
löytänyt tätä vikaa lainkaan, ja satunnaistesti löysi sen, koska
generaattori sattui tuottamaan samanaikaisia toimenpiteitä. Formaali
työkalu ei tarvinnut kumpaakaan: se antoi suoraan neljän jakson
syötejonon, joka toistaa vian.

## Induktio ja invariantit

BMC ei todista mitään yli kymmenen jakson. Täysi todistus tehdään
induktiolla, ja ensimmäinen yritys epäonnistuu:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-induktio.odotettu"}
```

Jäljen ensimmäinen tila on mahdoton: jonossa on neljä alkiota, mutta
kirjoitusosoitin on 2 ja lukuosoitin 3. Nollauksesta ei pääse tällaiseen
tilaan, mutta induktioaskel ei tiedä sitä, koska kaikki väitteet
(määrä enintään 4, liput oikein) pätevät siinä. Kahdeksan jakson
päästä jono on tyhjä ja osoittimet eroavat, ja väite rikkoutuu.
Syvyyden kasvattaminen ei auta, koska ratkaisija voi pitää jonon
puolillaan kuinka kauan tahansa.

Väite on tosi, mutta se ei ole *induktiivinen*: se ei yksin rajaa
tilajoukkoa niin, että askel säilyttää sen. Ratkaisu on *invariantti*,
lisäväite, joka kuvaa tilojen välisen yhteyden, jonka suunnittelija
tietää mutta jota mikään väite ei sanonut: osoittimien erotus vastaa
määrää.

```{.systemverilog tiedosto="esimerkit/rtl/fifo.sv" osa="invariantti"}
```

Invariantti on itsekin väite, joten työkalu tarkistaa sen
perustapauksessa. Väärä invariantti ei siis voi tuottaa väärää
todistusta; se vain epäonnistuu. Invariantin kanssa induktio onnistuu:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-invariantti.odotettu"}
```

Induktion epäonnistuminen on siis eri asia kuin BMC:n
epäonnistuminen. BMC:n vastaesimerkki alkaa nollauksesta ja on aina
aito vika. Induktion vastaesimerkki voi alkaa mahdottomasta tilasta,
ja silloin se kertoo puuttuvasta invariantista. Ensimmäinen kysymys
induktion jäljestä on aina: onko alkutila saavutettavissa?

## Kattavuuskohteet

`cover`-tila etsii lyhimmän ajon kumpaankin FIFOn kattavuuskohteeseen.
Jono täyttyy neljällä kirjoituksella, ja täyteen jonoon voidaan
kirjoittaa ja lukea yhtä aikaa:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-cover.odotettu"}
```

Kattavuuskohde suojaa tyhjästi toden todistuksen vaaralta. Jos
oletukset estäisivät jonon täyttymisen, kaikki täyttä jonoa koskevat
väitteet olisivat tosia mutta merkityksettömiä, ja `cover (taysi)`
epäonnistuisi.

## Reiluus apulogiikalla

Arbiterin tärkein ominaisuus on reiluus: pyytäjä saa vuoron rajatussa
ajassa. "Lopulta" on formaalisti *elävyysominaisuus* (liveness), jonka
tarkistaminen vaatii erityistekniikoita. Rajattu muoto "neljän jakson
kuluessa" on *turvallisuusominaisuus* (safety), ja sen voi kirjoittaa
apulogiikalla: jokaiselle pyytäjälle laskuri, joka kasvaa, kun pyyntö
odottaa, ja väite, että laskuri ei ylitä rajaa. Reiluus pätee vain, jos
ympäristö ei peru pyyntöä ennen myöntöä, joten se kirjoitetaan
oletukseksi:

```{.systemverilog tiedosto="esimerkit/rtl/arbiteri.sv" osa="formaali"}
```

BMC ja induktio onnistuvat. Induktio ei tarvitse invarianttia, koska
arbiterin tila (viimeisin pyytäjä ja myöntö) on niin pieni, että
kuusi jaksoa rajaa sen:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-arbiteri-bmc.odotettu"}
```

```{.tuloste tiedosto="esimerkit/odotetut/formaali-arbiteri-prove.odotettu"}
```

Kattavuus osoittaa, että raja 4 on tiukka: odotus voi todella kestää
neljä jaksoa jokaisella pyytäjällä. Jos raja olisi löysä, väite
hyväksyisi myös huonomman arbiterin.

```{.tuloste tiedosto="esimerkit/odotetut/formaali-arbiteri-cover.odotettu"}
```

Kiinteä etusija näkyy nääntymisenä: kaikki pyytävät, mutta pyytäjä 0
saa myönnön joka jakso, kunnes se luopuu pyynnöstään, ja pyytäjän 1
laskuri ylittää rajan. Väite epäonnistuu jokaisella kolmella
häviäjällä, mikä näkyy merkintänä `(3 kertaa)`.

```{.tuloste tiedosto="esimerkit/odotetut/formaali-arbiteri-kiintea.odotettu"}
```

Kahden myönnön vika vaatii, että kaikki neljä pyytävät yhtä aikaa.
Ratkaisija löysi tilanteen ensimmäisellä mahdollisella jaksolla:

```{.tuloste tiedosto="esimerkit/odotetut/formaali-arbiteri-kaksi.odotettu"}
```

## Ratkaisijat ja syvyys

Ratkaisijan valinta vaikuttaa nopeuteen, ei tulokseen. Z3 on
monipuolinen ja helposti saatavilla. Yices 2 ja Bitwuzla ovat usein
nopeampia bittivektorikaavoissa. Ubuntu 24.04:n Boolector-paketti on
vanha versio 1.5, joka ei ymmärrä yosys-smtbmc:n komentoja; uudempi
Boolector tai sen seuraaja Bitwuzla on asennettava lähteistä.
SymbiYosysissa on lisäksi menetelmiä, jotka todistavat ilman
syvyysrajaa (`abc pdr`, IC3), ja ne onnistuvat usein ilman käsin
kirjoitettuja invariantteja.

BMC:n syvyys valitaan niin, että se kattaa suunnitelman syvimmän
kiinnostavan tilan: FIFOlle jonon täyttymisen ja osoittimien
kierroksen, laskurille sen koko arvoalueen. Ajoaika kasvaa syvyyden
mukana nopeasti. Siksi formaaleissa tarkistuksissa käytetään usein
pienennettyjä parametreja: neljän paikan FIFO todistaa saman logiikan
kuin 1024 paikan FIFO, jos koodi on parametrinen. Isot lohkot
jaetaan osiin, ja osien rajapinnat kuvataan oletuksina.

Formaalin verifioinnin muita käyttötapoja ovat *ekvivalenssitarkistus*
(onko synteesin jälkeinen verkkolista sama kuin RTL; ks. taito
*ASIC-toteutus*), kytkentöjen tarkistus (onko jokainen signaali
kytketty oikeaan paikkaan) ja `x`-arvojen leviämisen tarkistus.

## Käytännössä

- **Aloita BMC:llä.** Se löytää viat nopeasti ja antaa aidon
  vastaesimerkin. Induktio kannattaa vasta, kun BMC on puhdas.
- **Lue induktion jälki alkutilasta.** Jos alkutila on mahdoton,
  puuttuu invariantti; jos se on mahdollinen, kyse on oikeasta viasta.
- **Jokaiselle oletukselle kattavuuskohde.** Liian tiukka oletus on
  formaalin verifioinnin vaarallisin virhe, koska se tuottaa vihreän
  tuloksen ilman sisältöä.
- **Pienennä parametrit.** Formaali tarkistus ajetaan pienimmillä
  parametreilla, jotka käyttävät kaikkea logiikkaa.
- **Kirjoita reiluus rajattuna.** "Neljän jakson kuluessa" on
  turvallisuusominaisuus ja helppo todistaa; "lopulta" vaatii
  erityistekniikoita.
- **Formaali ja simulointi yhdessä.** Samat väitteet kannattaa ajaa
  myös simulaatiossa; formaali kattaa lohkon kaikki tilat,
  simulointi järjestelmän kokonaisuuden.

## Itsearviointi

- Osaat selittää, mitä BMC, induktio ja kattavuustila tarkistavat ja
  mitä ne eivät kerro.
- Osaat kirjoittaa formaalit ominaisuudet: alkutilan oletuksen,
  väitteet ja kattavuuskohteet.
- Osaat lukea vastaesimerkin jäljen ja selittää, miten se johtaa
  väitteen rikkoutumiseen.
- Osaat tunnistaa induktion vastaesimerkin mahdottomasta alkutilasta
  ja kirjoittaa invariantin, joka korjaa sen.
- Osaat kirjoittaa reiluuden kaltaisen ominaisuuden apulogiikalla ja
  ympäristön oletuksilla.

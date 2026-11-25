# SPICE syvemmin

SPICE (*Simulation Program with Integrated Circuit Emphasis*) syntyi
Berkeleyssä 1970-luvulla, ja lähes kaikki piirisimulaattorit
perustuvat siihen. Netlist-kieli on vakiintunut: sama piiri toimii
pienin muutoksin ngspicessä, LTspicessä, Xycessä ja kaupallisissa
simulaattoreissa. Tämä luku kokoaa aiempien lukujen SPICE-käytön ja
lisää aliohjelmat, parametrit, silmukat, Monte Carlo -analyysin sekä
simuloinnin rajat.

## Netlistin rakenne

Netlistin ensimmäinen rivi on aina otsikko, ja viimeinen `.end`.
Komponenttirivin ensimmäinen kirjain kertoo lajin:

| Kirjain | Komponentti | Muoto |
|----------|----------------------------------|--------------------------------------|
| R, C, L | vastus, kondensaattori, kela | `R1 a b 4.7k` |
| V, I | jännite- ja virtalähde | `V1 a 0 DC 5 AC 1` |
| D | diodi | `D1 anodi katodi malli` |
| Q | bipolaaritransistori | `Q1 c b e malli` |
| M | MOSFET | `M1 d g s runko malli W=1u L=0.18u` |
| X | aliohjelma | `X1 a b nimi parametri=arvo` |
| E, G | jänniteohjattu jännite- tai virtalähde | `E1 ulos 0 plus miinus 10` |

Lähteillä on aaltomuotoja: `PULSE`, `SIN(offset amplitudi taajuus)` ja
`PWL(aika arvo ...)`. Jatkorivi alkaa `+`-merkillä, kommenttirivi
`*`-merkillä ja rivin loppukommentti `;`-merkillä. Lukujen etuliitteet
ovat `f p n u m k Meg G`. Muista, että `M` on milli.

Virran etumerkki on sovittu: SPICE ilmoittaa virran, joka kulkee
komponentin *ensimmäisestä* solmusta toiseen komponentin läpi.
Syöttävän jännitelähteen virta on siksi negatiivinen, kuten luvun 1
ensimmäisessä esimerkissä.

## Analyysit

| Komento | Analyysi | Tulos |
|------------------------|------------------------------|----------------------------|
| `op` | toimintapiste | tasajännitteet ja -virrat |
| `dc V1 0 5 0.1` | DC-pyyhkäisy | toimintapiste lähteen arvon funktiona |
| `ac dec 50 10 1Meg` | piensignaali taajuustasossa | vahvistus ja vaihe |
| `tran 1u 5m` | transientti | aaltomuodot ajan funktiona |
| `noise`, `four`, `sens` | kohina, Fourier, herkkyys | jatkotaidoissa |

Analyysit kirjoitetaan tässä tutoriaalissa `.control`-lohkoon, joka on
ngspicen komentokieltä. Lohkossa voi ajaa useita analyyseja, laskea
uusia vektoreita (`let`), mitata (`meas`), tulostaa (`print`) ja kirjoittaa
dataa tiedostoon (`wrdata`). Vaihtoehto on klassinen tapa, jossa
analyysi annetaan pisteellä alkavana rivinä (`.tran 1u 5m`) ja tulokset
`.print`- tai `.meas`-riveillä; se on siirrettävämpi simulaattorien
välillä, mutta `.control` on joustavampi.

`meas` on tärkein työkalu automaattiseen tarkistukseen:

| Muoto | Mittaa |
|--------------------------------------------------------|--------------------------|
| `meas tran t1 WHEN v(x)=2.5 RISE=1` | hetken, jolloin taso ohitetaan |
| `meas tran u1 FIND v(x) AT=1m` | arvon annettuna hetkenä |
| `meas tran m MAX v(x) FROM=1m TO=2m` | suurimman arvon välillä |
| `meas tran d TRIG v(a) VAL=0.9 RISE=1 TARG v(b) VAL=0.9 FALL=1` | viiveen |
| `meas ac f WHEN vdb(x)=-3.0103 FALL=1` | rajataajuuden |

## Aliohjelmat, parametrit ja silmukat

`.subckt` määrittelee uudelleenkäytettävän piirin, jolla voi olla
parametreja. `.param` antaa nimetyn arvon, jota käytetään
aaltosulkeissa lausekkeina. `.control`-lohkon `foreach`-silmukka ja
`alterparam` muuttavat parametria ja ajavat analyysin uudelleen;
`reset` lukee piirin uudelleen uusilla arvoilla. Luvun 6
lineaarisäädin oli jo aliohjelma; sen `B`-lähde on *käyttäytymislähde*,
jonka jännite tai virta annetaan lausekkeena muista solmuista.

```{.spice tiedosto="esimerkit/08-alipiiri.cir"}
```

Python laskee saman ketjun tarkasti impedansseilla. Ketjun asteet
kuormittavat toisiaan, joten rajataajuus ei ole kolmen erillisen
suotimen tulos:

```{.python tiedosto="esimerkit/08-alipiiri.py" osa="tarkka"}
```

```{.python tiedosto="esimerkit/08-alipiiri.py" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/08-alipiiri.odotettu"}
```

Vaikka jokainen aste on kymmenkertaisella impedanssilla edelliseen
nähden, kuormitus pienentää rajataajuutta noin 10 %. Tämä on tyypillinen
tilanne, jossa käsinlaskun yksinkertaistus ja simulointi eroavat, ja
tarkka vertailu kertoo, kumpi on väärässä.

## Monte Carlo -analyysi

Luvun 2 huonoimman tapauksen analyysi kertoi tuloksen äärirajat. Monte
Carlo -analyysi kertoo *jakauman*: komponenttien arvot arvotaan
toleranssien sisältä, piiri simuloidaan monta kertaa, ja tuloksista
lasketaan tilastot. ngspicessä on omat satunnaisfunktiot (`agauss`,
`aunif`), mutta Python on joustavampi: se tuottaa netlistin, jossa on
500 itsenäistä jakajaa, ja simulaattori ratkaisee ne kerralla.

```{.python tiedosto="esimerkit/08-montecarlo.py" osa="netlist"}
```

```{.python tiedosto="esimerkit/08-montecarlo.py" osa="tilasto"}
```

```{.tuloste tiedosto="esimerkit/08-montecarlo.odotettu"}
```

![500 simuloidun jakajan lähtöjännitteet. Katkoviivat ovat luvun 2
huonoimman tapauksen rajat ja musta viiva nimellisarvo.](kuvat/montecarlo.png){width=78%}

Tulokset jäävät huonoimman tapauksen rajojen sisään, ja suurin osa on
lähellä nimellistä. Jakauma riippuu oletuksesta: tässä vastusten
arvot ovat tasajakautuneita toleranssin sisällä. Valmistajien vastukset
ovat usein normaalijakautuneita ja keskittyneitä, mutta toisinaan
valmistaja on lajitellut tarkimmat osat erikseen, jolloin 5 %:n
vastuksista puuttuu juuri keskeltä. Kiinteä siemen tekee analyysista
toistettavan; taito *Todennäköisyys ja tilastot* käsittelee jakaumat.

## Konvergenssi ja simuloinnin rajat

SPICE ratkaisee epälineaarisen piirin Newtonin menetelmällä: se arvaa
toimintapisteen, linearisoi komponentit sen ympäriltä ja toistaa, kunnes
ratkaisu ei enää muutu. Transienttianalyysi tekee saman jokaisella
aika-askeleella ja pienentää askelta, kun muutos on nopea. Kun
ratkaisua ei löydy, ngspice ilmoittaa *timestep too small* tai
*singular matrix*. Tavallisimmat syyt ovat:

- **Solmu ilman tasavirtareittiä maahan.** Kelluva muuntajan toisio,
  pelkän kondensaattorin takana oleva solmu tai kytkemätön transistorin
  hila. Korjaus: suuri vastus (esimerkiksi 10 MΩ) maahan.
- **Ideaaliset komponentit, jotka vaativat äärettömän virran.**
  Ideaalinen jännitelähde suoraan kondensaattoriin tai johtavaan
  diodiin. Korjaus: realistinen sarjaresistanssi, kuten luvun 6
  tasasuuntaajan käämin resistanssi.
- **Liian nopeat reunat.** Nollan nousuaika tai epäjatkuvuus PWL-lähteessä.
  Korjaus: realistinen nousuaika (nanosekunteja).

Konvergenssiongelma kertoo usein, että malli on fysikaalisesti
mahdoton. Siksi ensimmäinen korjaus on aina lisätä puuttuva
todellinen ilmiö, ei säätää simulaattorin toleransseja.

Simulointi on vain niin hyvä kuin mallit. Tämän tutoriaalin mallit ovat
yksinkertaisia: taso 1 -MOSFET ei kuvaa lyhytkanavailmiöitä, diodimalli ei
kuvaa lämpenemistä, eikä yksikään malli kuvaa piirilevyn johtimien
induktanssia tai kapasitanssia. Valmistajien mallit ovat parempia
mutta kattavat nekin vain osan ilmiöistä; datalehti kertoo, mitä on
mitattu. Hyvä käytäntö on käyttää simulointia ymmärtämiseen ja
vaihtoehtojen vertailuun ja varmistaa tulos prototyypillä.

## Työkalut

ngspice on avointa lähdekoodia (BSD-tyyppinen lisenssi) ja toimii
eräajona, mikä tekee siitä sopivan automaattisiin testeihin ja
jatkuvaan integraatioon. **KiCad**, avoimen lähdekoodin
piirilevysuunnitteluohjelma, käyttää ngspiceä simulaattorinaan:
piirikaavio piirretään ja simuloidaan samassa ohjelmassa, ja sama
kaavio jatkaa piirilevyksi. **LTspice** on Analog Devicesin ilmainen
(mutta suljettu) simulaattori, jossa on laajat mallikirjastot. **Xyce**
on Sandia National Laboratoriesin rinnakkaislaskentaan kykenevä
avoin simulaattori suurille piireille. Kaikki lukevat SPICE-netlistejä,
joten tämän tutoriaalin piirit siirtyvät niihin pienin muutoksin.

Tulosten käsittely Pythonilla on tämän tutoriaalin perusmalli: simulaattori
kirjoittaa datan (`wrdata` tai raakatiedosto `-r`), ja Python vertaa,
sovittaa ja piirtää. Paketin kuvat on tehty skriptillä `kuvat/piirra.py`
samoista netlisteistä, ja piirikaaviot piirretään avoimella
`schemdraw`-kirjastolla (MIT-lisenssi).

## Käytännössä

- Kirjoita netlist kuten koodi: kommentoi piirin tarkoitus, nimeä
  solmut kuvaavasti ja pidä mallit erillisessä kirjastossa.
- Tarkista simuloinnin tulos käsinlaskulla tai yksinkertaisemmalla
  mallilla. Jos tulokset eroavat, selvitä syy ennen kuin luotat
  kumpaankaan.
- Käytä `meas`-komentoja ja Python-vertailuja regressiotesteinä: kun
  piiri muuttuu, testit kertovat, mikä muuttui.
- Tee toleranssi- ja lämpötila-analyysi kriittisille piireille. SPICEssä
  lämpötilan voi asettaa (`.temp` tai `.options temp=85`), ja mallit
  muuttuvat sen mukaan.
- Simuloi vain sitä, mitä mallit kuvaavat. Nopeat reunat, piirilevyn
  johtimet ja lämpö vaativat omat mallinsa.

## Itsearviointi

- Osaat kirjoittaa netlistin, jossa on lähteitä, passiivikomponentteja,
  puolijohteita ja aliohjelmia.
- Osaat valita oikean analyysin (op, dc, ac, tran) ja mitata tuloksista
  `meas`-komennoilla.
- Osaat käyttää parametreja ja silmukoita ja käsitellä tulokset
  Pythonilla.
- Osaat tehdä Monte Carlo -toleranssianalyysin ja tulkita sen tuloksen.
- Osaat tunnistaa tavallisimmat konvergenssiongelmat ja korjata ne
  lisäämällä puuttuvan fysikaalisen ilmiön.

# Johdanto {.runko-johdanto}

Arkkitehtuurin tärkeimmät päätökset tehdään ennen kuin riviäkään RTL:ää
on kirjoitettu. Paljonko ytimiä ja kuinka suuria? Kuinka suuri
välimuisti ja kuinka monta muistikanavaa? Kannattaako suodin tehdä
kiihdyttimeksi vai ohjelmistoksi? Millä jännitteellä siru ajetaan?
Kun RTL on valmis, näiden muuttaminen maksaa kuukausia. Siksi
vaihtoehdot arvioidaan *malleilla*: yksinkertaistetuilla kuvauksilla,
jotka ennustavat suorituskyvyn, pinta-alan ja tehon riittävän hyvin
vertailuun.

*Suunnittelutilan tutkiminen* (*design space exploration*, DSE) on
järjestelmällistä vaihtoehtojen läpikäyntiä: määritellään parametrit ja
niiden sallitut arvot, arvioidaan vaihtoehdot malleilla ja valitaan
tavoitteiden ja rajoitteiden perusteella. Tämä paketti opettaa mallit ja
menetelmät:

- **Kuormien karakterisointi** (luku 2): mitä ohjelma tekee laitteistolle,
  kun sitä mitataan riippumatta koneesta. Käskyjakaumat, muistijäljet,
  uudelleenkäyttöetäisyys ja hutikäyrät.
- **Analyyttiset mallit** (luvut 3 ja 4): Amdahl, Hill ja Marty,
  roofline, Littlen laki, CPI-pino ja jonoteoria. Ne vastaavat
  sekunnin murto-osassa ja kertovat, mikä on mahdollista.
- **Simulaattorit** (luvut 5 ja 6): tapahtuma- ja syklipohjainen
  simulointi SystemC:llä, intervallimalli ja näytteistys. Ne ovat
  hitaampia mutta näkevät kilpailun, riippuvuudet ja limityksen.
- **Laitteisto–ohjelmisto-jako** (luku 7): milloin kiihdytin kannattaa,
  analyyttisesti ja virtuaaliprototyypillä.
- **Pinta-ala ja teho** (luku 8): dynaaminen teho ja vuoto, jännitteen
  ja taajuuden skaalaus, energia operaatiota kohden, välimuistin koon
  vaikutukset.
- **Suunnittelutilan läpikäynti** (luku 9): ruudukko, satunnainen otanta,
  latinalainen hyperkuutio, Pareto-rintama ja herkkyysanalyysi.
- **Validointi ja raportointi** (luku 10): luottamusvälit, kalibrointi,
  toistettavuus.

## Mallien tarkkuustasot

Mallia valitessa vaihdetaan nopeutta tarkkuuteen. Mitä aiemmin
suunnittelussa ollaan, sitä useampi vaihtoehto on auki ja sitä nopeampi
mallin on oltava.

| Taso | Mitä mallinnetaan | Nopeus (suuruusluokka) | Käyttö |
|--------------|------------------|----------------------|-------------------------|
| analyyttinen | kaavat keskiarvoista | miljoonia arvioita sekunnissa | rajojen hahmotus, laaja tutkiminen |
| jälkipohjainen | muistijälki, käskyvirta | miljoonia viittauksia sekunnissa | välimuistit, ennustimet |
| toiminnallinen, LT | käskyt ja transaktiot, ei ajoitusta | satoja miljoonia käskyjä sekunnissa | ohjelmistokehitys, kuormien keruu |
| syklilikimääräinen | tapahtumat ja niiden hinnat | miljoonia käskyjä sekunnissa | moniytimien tutkiminen |
| syklitarkka | jokainen kellojakso | satojatuhansia käskyjä sekunnissa | mikroarkkitehtuurin yksityiskohdat |
| RTL-simulointi | jokainen signaali | tuhansia jaksoja sekunnissa | toteutuksen verifiointi |

Taulukon nopeudet ovat suuntaa antavia, ja ne riippuvat mallista ja
koneesta. Olennaista on, että tasojen välillä on kertaluokkia. Kun
analyyttinen malli arvioi miljoona vaihtoehtoa sekunnissa, syklitarkka
simulaattori tarvitsee yhden vaihtoehdon yhden sekunnin ajoon tunteja.

Tarkkuustasot eivät kilpaile vaan täydentävät toisiaan. Tyypillinen
työnkulku käy laajan tilan läpi analyyttisillä malleilla, karsii
lupaavimmat simulaattorilla ja tarkistaa muutaman RTL:llä tai
prototyypillä. Mallit myös tarkistavat toisiaan: jos analyyttinen malli
ja simulaattori ovat eri mieltä, toisessa on virhe tai oletus, jota
kannattaa ymmärtää. Luvuissa 5–7 tehdään näin: sama järjestelmä
mallinnetaan kahdella tavalla, ja tuloksia verrataan.

## Ensimmäinen suunnittelukysymys

Kuinka suuri L1-datavälimuistin pitäisi olla? Suurempi välimuisti osuu
useammin, mutta sen osumaviive on pidempi, ja se vie enemmän pinta-alaa.
Yksinkertaisin malli on CPI-pino (luku 3): perus-CPI, johon lisätään
latausten viiveet. Hutiosuus pienenee kokemusperäisen
neliöjuurisäännön mukaan (luku 8):

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="malli"}
```

```{.python tiedosto="esimerkit/01-ensimmainen.py" osa="ehdokkaat"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

Mallin mukaan 16 KiB:n välimuisti kahden jakson viiveellä on yhtä nopea
kuin 32 KiB:n välimuisti kolmen jakson viiveellä, ja se vie puolet
pinta-alasta. Johtopäätös on kuitenkin vain niin hyvä kuin oletukset:
neliöjuurisääntö, piilotuksen osuus 70 % ja latausten osuus 25 %. Ennen
päätöstä tarvitaan kolme asiaa, jotka tämä paketti opettaa:

1. **Kuorman tiedot** omista ohjelmista eikä oletuksista (luku 2).
2. **Mallin validointi**: piilottaako ydin todella 70 % viiveestä? Se
   selviää simulaattorilla (luvut 5 ja 6).
3. **Herkkyysanalyysi**: muuttuuko valinta, jos oletus on 20 % väärin
   (luku 9)?

## Työkalut

Esimerkit käyttävät kahta kieltä. Python sopii analyyttisiin malleihin,
jälkien analyysiin ja tulosten käsittelyyn. C++ ja SystemC sopivat
simulaattoreihin, joissa nopeus on tärkeää. Esimerkkien Python-kirjasto
`esimerkit/arkki/` kokoaa mallit moduuleiksi, joita lukujen esimerkit
käyttävät.

Oikeissa projekteissa käytetään valmiita työkaluja, joiden periaatteet
tämä paketti opettaa:

| Työkalu | Tehtävä | Luku |
|----------------------|----------------------------------------------|------|
| Pin, DynamoRIO, Valgrind | käskyjakaumat ja muistijäljet binääreistä | 2 |
| gem5 | syklitarkka täyden järjestelmän simulointi | 5 |
| Sniper | intervallimalliin perustuva moniydinsimulaattori | 6 |
| SimPoint | edustavien intervallien valinta | 6 |
| Ramulator, DRAMSim3 | DRAM-muistin syklitarkka malli | 5 |
| CACTI | välimuistien viive, energia ja pinta-ala | 8 |
| McPAT | suorittimen teho ja pinta-ala | 8 |
| Timeloop ja Accelergy | kiihdyttimien tietovuot ja energia | 7, 8 |

## Esitiedot ja rajaus

Paketti olettaa kolme taitoa. *Korkean tason mallinnus (SystemC/TLM)*
opettaa
SystemC:n ja TLM-2.0:n, joilla luvun 5 ja 7 mallit on kirjoitettu.
*Suorituskyvyn analyysi ja optimointi* esittelee Amdahlin lain ja
roofline-mallin ohjelmiston näkökulmasta; tässä niitä käytetään
arkkitehtuurin mitoittamiseen. *Todennäköisyys ja tilastot* antaa
jakaumat, odotusarvot ja luottamusvälit, joita jonoteoria ja
simulointitulosten tulkinta tarvitsevat. Lisäksi *Tietokonearkkitehtuuri*
on hyödyllinen: välimuistit, liukuhihnat ja epäjärjestyssuoritus ovat
niitä rakenteita, joita tässä mallinnetaan.

Paketti ei käsittele mallien muuntamista toteutukseksi. Synteesi,
ajoitusanalyysi ja tehon mittaaminen toteutuksesta ovat paketissa
*ASIC-toteutus*, ja C++-mallin kääntäminen laitteistoksi on paketissa
*Korkean tason synteesi*.

## Esimerkit

Esimerkit ovat hakemistossa `esimerkit/`. Python-esimerkit ovat
tiedostoja `NN-nimi.py`, ja C++- ja SystemC-esimerkit hakemistoja
`NN-nimi/`. Tuloste verrataan aina tallennettuun, joten jokainen
kirjassa näkyvä luku on testattu:

```text
make testaa   # ruff, mypy --strict, pytest, ShellCheck ja esimerkit
make pdf      # tämä dokumentti ja pikaopas
make kuvat    # kuvat uudelleen (matplotlib)
```

Kaikki satunnaisuus tulee kiinteistä siemenistä, ja SystemC-mallit
raportoivat simuloitua aikaa eivätkä seinäkelloaikaa, joten tulokset
ovat samat joka koneella. Tämä on myös hyvä käytäntö oikeissa
tutkimuksissa (luku 10).

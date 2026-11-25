# Mallin ja RTL:n vastaavuus

Malli on hyödyllinen vain niin kauan kuin se kuvaa samaa laitetta kuin
toteutus. Kun RTL valmistuu, sitä verrataan malliin, ja malli muuttuu
*referenssimalliksi* (*golden model*): testipenkki syöttää samat
herätteet molemmille ja vertaa tuloksia. Bittitarkka malli tekee
vertailusta tarkan: jokaisen ulostulon jokaisen bitin on täsmättävä.
Tämä luku kääntää luvun 6 FIR-suotimen RTL-toteutuksen Verilatorilla
SystemC-moduuliksi ja vertaa sitä malliin samassa simulaatiossa.

## Vastaavuuden tarkistustavat

| Tapa | Miten | Kattavuus |
|------------------|----------------------------------------------|------------------------------|
| tulosvertailu | malli ja RTL ajetaan samoilla herätteillä, tulokset verrataan | herätteiden mukainen |
| yhteissimulointi | RTL käännetään SystemC-moduuliksi ja vertaillaan samassa ajossa | herätteiden mukainen, nopea vianetsintä |
| testipenkin referenssi | malli kytketään UVM- tai cocotb-testipenkin vertailijaksi | herätteiden ja kattavuusmittausten mukainen |
| formaali vastaavuus | työkalu todistaa C++-mallin ja RTL:n vastaavuuden (*C-to-RTL*, *SLEC*) | kaikki syötteet rajatulle syvyydelle |

Tulosvertailu tiedostojen kautta on yksinkertaisin: malli kirjoittaa
odotetut ulostulot tiedostoon ja RTL-testipenkki lukee ne. Se ei vaadi
yhteistä simulaattoria, mutta virheen syyn selvittäminen vaatii kahden
ajon vertailua. Yhteissimuloinnissa molemmat ovat samassa ohjelmassa,
ja ensimmäinen ero pysäyttää ajon oikeaan kohtaan. Formaalit työkalut
ovat kaupallisia ja vaativat mallin, joka on kirjoitettu niiden
hyväksymällä C++:n osajoukolla.

## RTL-toteutus

Suodin on SystemVerilogia (taito *RTL-suunnittelu SystemVerilogilla*). Se ottaa vastaan
yhden näytteen kellojaksossa ja antaa tuloksen jakson viiveellä:

```{.systemverilog tiedosto="esimerkit/15-vastaavuus/fir.sv" osa="rtl"}
```

Kiinteän pilkun aritmetiikka on kirjoitettu kokonaisluvuilla: Q1.15-
tulot ovat 16-bittisiä, tulot ja summa 35-bittisiä, pyöristys lisää
puolikkaan LSB:n (2^14^) ennen aritmeettista siirtoa 15 bittiä oikealle,
ja saturaatio rajaa tuloksen 16 bittiin. Nämä ovat täsmälleen mallin
`SC_RND`- ja `SC_SAT`-tilat. Kertoimet ovat mallin kertoimia
katkaistuina, kuten `sc_fixed<16, 1>` ne katkaisee: esimerkiksi
−0,02 · 2^15^ = −655,36 katkeaa kohti miinus ääretöntä lukuun −656.
Parametri `PYORISTYS` tuottaa tarkoituksella virheellisen version, jossa
pyöristys puuttuu.

## Verilator ja SystemC

Verilator kääntää RTL:n C++:ksi. Valitsimella `--sc` se tuottaa
SystemC-moduulin `Vfir`, jonka portit vastaavat RTL:n portteja:
yksibittiset ovat `bool`-tyyppisiä ja enintään 32-bittiset
`uint32_t`-tyyppisiä. Etumerkillinen 16-bittinen arvo kulkee siis
32-bittisen etumerkittömän kentän alimmissa biteissä, ja testipenkki
tekee muunnokset itse.

Herätemoduuli syöttää näytteet laskevalla reunalla, kuten luvun 2
testipenkki, ja laskee jokaiselle näytteelle odotetun tuloksen mallilla
heti, kun näyte syötetään:

```{.cpp tiedosto="esimerkit/15-vastaavuus/testipenkki.cpp" osa="herate"}
```

Herätteet ovat kolmea lajia. Impulssi tuottaa ulostuloon kertoimet
yksi kerrallaan, joten väärä kerroin näkyy heti. Pahimman tapauksen
herätteet saturoivat ulostulon. Satunnaiset näytteet kiinteällä
siemenellä kattavat loput; joka neljäs jakso on tauko, jotta myös
`sisaan_kelpaa`-signaalin käsittely tulee testatuksi. `std::mt19937`:n
tulosjono on standardin määräämä, joten sama siemen antaa samat
näytteet kaikilla alustoilla.

Vertailija lukee RTL:n ulostulon nousevalla reunalla ja vertaa sitä
odotettujen jonon kärkeen. Jono tekee vertailusta riippumattoman RTL:n
viiveestä: vertailija ei tiedä, montako jaksoa RTL tarvitsee, vain sen,
että tulokset tulevat samassa järjestyksessä.

```{.cpp tiedosto="esimerkit/15-vastaavuus/testipenkki.cpp" osa="vertailija"}
```

Pääohjelma kytkee Verilatorin moduulin `Vfir` porteistaan signaaleihin
kuten minkä tahansa SystemC-moduulin, luo herätteen ja vertailijan ja
antaa niille saman jonon. Simuloinnin jälkeen kutsutaan `dut.final()`,
joka ajaa RTL:n `final`-lohkot, ja paluuarvo kertoo, löytyikö eroja.
Ajoskripti kääntää kaksi versiota, oikean ja virheellisen:

```{.bash tiedosto="esimerkit/15-vastaavuus/aja.sh"}
```

`--exe --build` kääntää RTL:n, testipenkin ja Verilatorin
ajonaikaisen kirjaston yhdeksi ohjelmaksi. `-CFLAGS` välittää
testipenkin käännökselle samat asetukset kuin muissa esimerkeissä,
myös kiinteän pilkun tyypit. `-Wall` tekee Verilatorin varoituksista
virheitä: esimerkiksi parametrin leveysvaroitus pysäyttää käännöksen,
mikä on oikein, koska leveysvirheet ovat RTL:n yleisimpiä vikoja.

```{.tuloste tiedosto="esimerkit/15-vastaavuus/odotettu"}
```

Oikea versio vastaa mallia kaikissa 2025 näytteessä. Virheellinen versio
eroaa jo impulssivasteessa: kerroin 5570 · 32767 / 32768 = 5569,83 pitää
pyöristää 5570:een, mutta katkaisu antaa 5569. Ero on yksi LSB, ja puolet
kaikista näytteistä eroaa. Liukulukumalliin vertaava testi hyväksyisi
molemmat versiot, jos toleranssi olisi yksi LSB; bittitarkka vertailu
pysähtyy ensimmäiseen poikkeavaan näytteeseen.

## Transaktorit

Tässä luvussa testipenkki kytkeytyi RTL:ään signaalitasolla. Isommassa
järjestelmässä RTL-lohko kytketään TLM-malliin *transaktorilla*:
moduulilla, joka muuntaa TLM-transaktion väylän signaaleiksi ja
takaisin. TLM–AXI-transaktori ottaa vastaan `b_transport`-kutsun, ajaa
AXI-kättelyn RTL:ää vasten ja palauttaa vastauksen. Näin yksi
oheislaite voidaan vaihtaa virtuaaliprototyypissä RTL-toteutukseensa,
ja oikea ohjelmisto testaa oikeaa RTL:ää. Simulointi hidastuu RTL:n
nopeuteen vain sen lohkon osalta.

## Käytännössä

- **Sama aritmetiikka, kirjattuna.** Mallin ja RTL:n bittileveydet,
  pyöristykset ja saturaatiot kirjataan määrittelyyn. Jos RTL:n
  suunnittelija joutuu arvaamaan, malli ja toteutus eroavat jo ennen
  ensimmäistä testiä.
- **Vertaa bitit, ei toleranssia.** Bittitarkan mallin ja RTL:n vertailu
  on tarkka yhtäsuuruus. Toleranssi kuuluu vain liukulukuviitteen ja
  bittitarkan mallin väliin (luku 6).
- **Jono viiveen yli.** Vertailija, joka odottaa tulosta tietyllä
  syklillä, rikkoutuu, kun RTL:ään lisätään liukuhihnavaihe.
  Järjestyksessä toimiva jono, tai tunnisteilla sovitettu vertailu
  järjestyksestä poikkeaville vastauksille, kestää mikroarkkitehtuurin
  muutokset.
- **Suunnatut ja satunnaiset herätteet.** Impulssi, askel ja pahin
  tapaus löytävät tyypilliset virheet nopeasti ja helposti
  tulkittavasti; satunnaiset herätteet kiinteällä siemenellä löytävät
  loput toistettavasti. Kattavuuden mittaaminen (taito *Laitteiston verifiointi*)
  kertoo, milloin herätteitä on tarpeeksi.
- **Malli elää.** Kun määrittely muuttuu, malli päivitetään ensin ja RTL
  sen jälkeen. Jos RTL:ää korjataan mallin ohi, referenssi menettää
  arvonsa.

## Itsearviointi

- Osaat kääntää RTL-moduulin Verilatorilla SystemC-moduuliksi ja kytkeä
  sen testipenkkiin.
- Osaat kirjoittaa vertailijan, joka vertaa RTL:n tuloksia bittitarkan
  mallin tuloksiin RTL:n viiveestä riippumatta.
- Osaat valita suunnatut ja satunnaiset herätteet niin, että ne
  löytävät kerroin-, pyöristys- ja saturaatiovirheet.
- Osaat selittää transaktorin roolin TLM-mallin ja RTL:n välillä.

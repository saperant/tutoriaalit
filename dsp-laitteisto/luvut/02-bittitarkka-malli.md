# Bittitarkka malli referenssinä

Liukulukumalli kertoo, mitä suodin tekee periaatteessa. Laitteisto
tekee jotakin muuta: se pyöristää jokaisen tuloksen, rajaa jokaisen
summan ja kiertää ylivuodossa, jos suunnittelija ei ole päättänyt
toisin. *Bittitarkka malli* laskee saman kuin laitteisto mutta
ohjelmana. Se on suunnittelun työkalu, koska sanaleveydet voi kokeilla
sillä nopeasti, ja verifioinnin referenssi, koska RTL:n ulostulon on
oltava sama kuin mallin jokaisella bitillä.

## Mallin säännöt

Malli on kirjoitettu Pythonilla. Pythonin kokonaisluvut ovat
rajattomia, mikä on mallille hyvä ominaisuus: mikään ei vuoda yli
huomaamatta, vaan jokainen leveyden rajaus on kirjoitettava näkyviin.
Mallit noudattavat neljää sääntöä:

1. Datapolussa on vain kokonaislukuja. Liukulukuja käytetään vain
   suunnitteluun ja tulosten arviointiin.
2. Jokainen leveyden rajaus on oma funktiokutsunsa: `saturoi`,
   `kierra`, `pyorista` tai `katkaise`. Rajauksen paikka on sama kuin
   RTL:ssä.
3. Tila (viivelinja, takaisinkytkentä, integraattorit) alkaa nollasta,
   kuten RTL nollauksen jälkeen.
4. Malli laskee näytteen kerrallaan samassa järjestyksessä kuin RTL.
   Jos RTL käyttää edellisen jakson arvoa, myös malli käyttää sitä.

Neljäs sääntö koskee vain tilaa, ei laskujärjestystä. Kokonaislukujen
yhteenlasku on liitännäinen, joten summan voi laskea missä
järjestyksessä tahansa, kunhan välitulokset eivät vuoda yli. Siksi
yksi FIR-malli kelpaa referenssiksi neljälle eri rakenteelle
luvussa 3.

Mallin ulkopuolelle jää ajoitus: kuinka monta jaksoa lasku kestää ja
milloin näyte otetaan vastaan. Malli kertoo, *mitä* ulostulojonossa
on; testipenkki huolehtii siitä, *milloin* näytteet liikkuvat.

## Rajaukset

Saturaatio, kierto ja pyöristystavat ovat tuttuja taidosta *Lukujen
esitys ja kiinteän pilkun aritmetiikka*. Tässä ja seuraavassa osiossa
ne kirjoitetaan funktioiksi, joita sekä malli että RTL käyttävät, ja
kerrataan vain se, mikä vaikuttaa toteutukseen.

Etumerkillisen $b$-bittisen luvun alue on
$[-2^{b-1}, 2^{b-1} - 1]$. Ylivuodossa on kaksi vaihtoehtoa: arvo
jää alueen reunalle (saturaatio) tai ylimmät bitit vain pudotetaan
(kahden komplementin kierto). Laitteistossa kierto on ilmainen, koska
se on pelkkää johdotusta, ja saturaatio maksaa vertailun ja
multiplekserin.

```{.python tiedosto="esimerkit/malli/kiintea.py" osa="alue"}
```

Kierto on oikea valinta silloin, kun lopputulos mahtuu leveyteen,
vaikka välitulokset eivät mahtuisi. Kahden komplementin yhteenlasku on
modulo-aritmetiikkaa: jos lopullinen summa mahtuu alueelle, välillä
tapahtuneet ylivuodot kumoutuvat. Luvun 7 CIC-suodin perustuu tähän.
Muualla ylivuoto on virhe, ja ulostulo saturoidaan.

## Pyöristys

Kun alimmat $s$ bittiä pudotetaan, tulos pyöristyy kohti miinus
ääretöntä. Pyöristys lähimpään saadaan lisäämällä ensin puolikas eli
$2^{s-1}$:

```{.python tiedosto="esimerkit/malli/kiintea.py" osa="pyoristys"}
```

Puolikkaat pyöristyvät ylöspäin, myös negatiiviset: $-2{,}5$ pyöristyy
lukuun $-2$. Tämä on laitteistossa halvin pyöristys lähimpään, koska
siihen riittää yksi summain. Symmetrinen pyöristys (puolikkaat
poispäin nollasta) ja konvergentti pyöristys (puolikkaat parilliseen)
tarvitsevat lisäksi etumerkin tai alimman bitin tarkistuksen. Valinta
on tehtävä tietoisesti ja kirjattava malliin, koska jokainen tapa
antaa eri bitit.

Pyöristys ja rajaus yhdistetään funktioksi, joka kaventaa leveän
summan ulostulon leveyteen:

```{.python tiedosto="esimerkit/malli/kiintea.py" osa="ulostulo"}
```

Sama asia RTL:nä on moduuli `kavenna`, jota kaikki suotimet
käyttävät:

```{.systemverilog tiedosto="esimerkit/rtl/kavenna.sv" osa="kavenna"}
```

Saturaation tunnistaa siitä, että pudotettavat ylimmät bitit ja uuden
etumerkkibitin paikka eivät ole kaikki samoja. Tämä on halvempi kuin
vertailu suurimpaan ja pienimpään arvoon, koska vertailu tarvitsisi
kaksi täysleveää vähennyslaskua. `ifdef`-lohkot ovat tarkoituksella
istutettuja vikoja, joita käytetään luvuissa 4 ja 9: `BUGI_KATKAISU`
unohtaa puolikkaan ja `BUGI_KIERTO` saturaation.

## Bittikasvu

Kahden luvun tulo on yhtä leveä kuin tekijöiden leveydet yhteensä:
Q1.11 kertaa Q1.15 on Q2.26, 28 bittiä. Summa kasvaa yhdellä
bitillä jokaista summattavien määrän kaksinkertaistumista kohden, eli
$N$ termin summaan tarvitaan $\lceil \log_2 N \rceil$ lisäbittiä.
Esimerkkien FIR-suotimessa on kahdeksan kerrointa:

```{.python tiedosto="esimerkit/analyysit/bittikasvu.py" osa="kasvu"}
```

```{.tuloste tiedosto="esimerkit/odotetut/bittikasvu.odotettu"}
```

Yleinen sääntö antaa 31 bittiä, mutta näiden kertoimien tarkka
pahin tapaus mahtuu 28 bittiin. Tarkka raja lasketaan kertoimien
itseisarvojen summasta: suurin mahdollinen ulostulo saadaan, kun
jokainen näyte on täysi arvo oman kertoimensa etumerkillä, jolloin
vahvistus on $\sum_k |h_k| = 1{,}1122$. Kaksi johtopäätöstä:

- Summaimen kolme lisäbittiä ovat varmuusvaraa, jota nämä kertoimet
  eivät tarvitse. Synteesi ei osaa poistaa niitä, koska se ei tiedä,
  että kertoimet ovat vakioita tämän rajan sisällä, joten leveyden voi
  rajata käsin. Esimerkeissä käytetään yleistä sääntöä, jotta RTL
  toimii millä tahansa kertoimilla.
- Ulostulo voi ylittää alueen 11 %. Ylitys on mahdollinen mutta
  harvinainen, joten saturaatio on pakollinen, ja sen testaamiseen
  tarvitaan erityinen sisääntulo (luku 9).

## Kertoimet

Kertoimet suunnitellaan liukulukuina ja kvantisoidaan. Esimerkkien
FIR-suodin on `signal.firwin(8, 0.5)`, alipäästö, jonka rajataajuus
on neljännes näytetaajuudesta:

```{.python tiedosto="esimerkit/analyysit/suunnittelu.py" osa="fir"}
```

```{.tuloste tiedosto="esimerkit/odotetut/suunnittelu.odotettu"}
```

Kvantisoidut kertoimet kirjoitetaan malliin kokonaislukuina. Ne ovat
suunnitelman osa: jos SciPyn seuraava versio laskisi viimeisen
desimaalin toisin, kertoimet eivät saa muuttua huomaamatta. Siksi
`analyysit/suunnittelu.py` tarkistaa, että suunnittelu tuottaa yhä
samat luvut, ja malli ja RTL lukevat kertoimet samasta lähteestä:

```{.python tiedosto="esimerkit/malli/kertoimet.py" osa="fir"}
```

RTL:n puolelle kertoimet tuottaa `malli/generoi.py`. Se pakkaa
kertoimet yhdeksi vakioksi, josta RTL poimii alkion $i$
lausekkeella `K[i*KW +: KW]`:

```{.python tiedosto="esimerkit/malli/generoi.py" osa="pakkaa"}
```

```{.verilog tiedosto="esimerkit/rtl/kertoimet.svh"}
```

Generoitu tiedosto on versionhallinnassa, jotta RTL:n voi lukea ja
syntetisoida ilman Pythonia. Testi `make generoidut` varmistaa, että
tiedosto vastaa mallia; muuten käsin muokattu kerroin voisi jäädä
RTL:ään eri arvoisena kuin mallissa.

## Pyöristys vai katkaisu

Katkaisu säästää summaimen, joten se on houkutteleva. Mallilla
hinnan voi mitata: suodatetaan 20 000 satunnaista näytettä
molemmilla tavoilla ja verrataan tarkkaan tulokseen.

```{.python tiedosto="esimerkit/analyysit/sanaleveys.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/odotetut/sanaleveys.odotettu"}
```

Katkaisun virheen keskiarvo on puoli LSB:tä alaspäin. Se on
tasavirtapoikkeama, joka summautuu jokaisessa seuraavassa lohkossa,
ja SNR huononee 6 dB eli yhden bitin verran. Pyöristyksen virhe on
keskimäärin nolla. Yksi summain on halvempi kuin yksi lisäbitti
koko datapolussa, joten pyöristys kannattaa lähes aina.

Kertoimien bittimäärä vaikuttaa toisin: se ei lisää kohinaa vaan
siirtää taajuusvastetta. Taulukon jälkimmäinen osa kvantisoi 32
kertoimen alipäästön eri leveyksiin ja mittaa estokaistan suurimman
vahvistuksen. Jokainen bitti parantaa vaimennusta noin 5–6 dB,
kunnes vaimennus saavuttaa liukulukusuunnittelun oman rajan
(−63 dB). Sen jälkeen lisäbitit eivät auta. Esimerkkien 16-bittiset
kertoimet ovat tälle suotimelle reilusti riittävät. Sama ilmiö
taajuusvasteen kuvana on taidossa *Lukujen esitys ja kiinteän pilkun
aritmetiikka*.

## Käytännössä

- Bittitarkka malli kirjoitetaan ennen RTL:ää. Sillä valitaan
  sanaleveydet ja pyöristystavat, ja sen jälkeen RTL:n testaus on
  pelkkää vertailua.
- Jokainen rajaus nimetään ja kirjoitetaan sekä malliin että RTL:ään
  samaan kohtaan. Yksi yhteinen kaventava moduuli (`kavenna`) on
  helpompi tarkistaa kuin kymmenen käsin kirjoitettua.
- Kertoimet ovat dataa, joka kuuluu versionhallintaan
  kokonaislukuina. Generoitu RTL-vakio tarkistetaan testissä.
- Pahin tapaus lasketaan kertoimien itseisarvojen summasta. Jos summa
  on yli 1, saturaatio on pakollinen ja sille tarvitaan oma testi.
- Katkaisu on halvempi mutta tuottaa puolen LSB:n tasavirtavirheen.
  Valinta kirjataan suunnitelmaan perusteluineen.
- Teollisuudessa sama malli tehdään usein MATLABin `fi`-tyypeillä,
  C++:n `ac_fixed`- tai SystemC:n `sc_fixed`-tyypeillä. Periaate on
  sama: malli, jonka jokainen bitti on määritelty.

## Itsearviointi

- Osaat selittää, miksi bittitarkka malli tarvitaan liukulukumallin
  lisäksi ja mitä se jättää ajoituksen osalta pois.
- Osaat laskea tulon ja $N$ termin summan leveyden sekä tarkan
  pahimman tapauksen kertoimien itseisarvojen summasta.
- Osaat toteuttaa pyöristyksen lähimpään ja saturaation sekä
  Pythonilla että SystemVerilogilla ja tiedät, mitä kumpikin maksaa.
- Osaat perustella, milloin kahden komplementin kierto on sallittu ja
  milloin ulostulo on saturoitava.
- Osaat pitää kertoimet yhtenä lähteenä, josta sekä malli että RTL
  lukevat, ja tarkistaa generoidun tiedoston testissä.

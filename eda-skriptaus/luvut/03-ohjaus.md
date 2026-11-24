# Työkalujen ohjaus

EDA-työkalut on tehty sekä interaktiiviseen että eräkäyttöön. Vuo
käyttää aina eräajoa: työkalu käynnistetään komentoriviltä skriptin ja
valitsimien kanssa, se kirjoittaa lokin ja päättyy paluuarvoon. Tämä
luku käy läpi, mitä eräajossa voi mennä pieleen ja miten ajoa
ohjaava koodi kirjoitetaan niin, ettei virhe katoa.

## Komento, loki ja paluuarvo

Kaikki tämän taidon työkaluajot kulkevat yhden funktion kautta:

```{.python tiedosto="esimerkit/vuo/ajo.py" osa="ajo"}
```

Funktio tekee viisi asiaa, joista jokainen on opittu jonkin virheen
kautta:

- **Loki tiedostoon, ei muistiin.** Synteesin tai sijoittelun loki voi
  olla satoja megatavuja. Tiedostoon kirjoitettu loki säilyy myös, jos
  vuo itse kaatuu, ja se voidaan liittää CI:n artefakteihin.
- **Virhetuloste samaan lokiin.** Kun `stderr` ohjataan `stdout`:iin,
  virheilmoitus on lokissa oikealla paikallaan muiden viestien
  joukossa. Erillisistä tiedostoista järjestystä ei saa enää selville.
- **Komento lokin ensimmäiselle riville.** Lokin lukija voi toistaa
  ajon käsin kopioimalla rivin.
- **Aikakatkaisu.** Jumiin jäänyt simulointi tai lisenssiä odottava
  työkalu pysäyttäisi muuten koko vuon. Aikakatkaisu ei ole poikkeus
  vaan oma paluuarvonsa, jonka kutsuja käsittelee kuten muutkin
  virheet.
- **Ulomman Maken muuttujat pois.** Kun vuota ajetaan Makesta
  (`make -j4`), ympäristössä on `MAKEFLAGS`, jossa on rinnakkaisuus ja
  jobserverin tiedostokuvaajat. Verilator ajaa käännöksensä omalla
  Makellaan, joka lukisi nämä asetukset. Pahimmillaan se varoittaa
  puuttuvasta jobserverista tai jumittuu odottamaan sitä.

## Paluuarvo ei kerro kaikkea

Käännöksen ja synteesin paluuarvoon voi yleensä luottaa: nolla
tarkoittaa, että työkalu sai työnsä tehtyä. Simuloinnissa näin ei ole.
Simulaattori palauttaa nollan, kun simulointi päättyy `$finish`-
kutsuun, olipa testi mennyt läpi tai ei. Testin tuloksen kertoo vasta
testipenkin oma tulosrivi.

```{.python tiedosto="esimerkit/03-ohjaus.py" osa="paluuarvo"}
```

Kolmannessa ajossa testipenkki saa valitsimen `+jumita`, jolloin se
jää ikuiseen silmukkaan. Aikaraja on tässä sekunti:

```{.tuloste tiedosto="esimerkit/03-ohjaus.odotettu"}
```

Kolme ensimmäistä riviä ovat tässä tärkeät. Yosys palauttaa
puuttuvasta tiedostosta arvon 1, ja lokissa on `ERROR:`-rivi.
Viallisen ALU:n simulointi palauttaa nollan, vaikka testipenkki
löysi kolme virhettä. Jumiin jäänyt simulointi katkaistaan, ja
paluuarvo -1 erottaa sen muista virheistä.

Siksi testipenkki tulostaa aina tulosrivin `TESTI OK` tai
`TESTI EPÄONNISTUI`, ja jäsennin (luku 5) tulkitsee kaiken muun
virheeksi. Jos lokista puuttuu tulosrivi, simulaattori on kaatunut tai
testipenkki on päättynyt kesken, eikä sellaista ajoa saa koskaan
tulkita onnistuneeksi. Testipenkki voi myös lopettaa `$fatal`-
kutsulla, jolloin moni simulaattori palauttaa nollasta poikkeavan
arvon. Tulosrivi on silti tarpeen, koska vain se erottaa
onnistuneen testin testistä, joka ei koskaan päässyt tarkistuksiin
asti.

## Työkalun versio

Työkalun versio kuuluu ajon tietoihin. Uusi Yosys voi tuottaa eri
netlistan samasta RTL:stä, ja uusi Verilator voi löytää uusia
varoituksia. Versiokysely on jokaisessa työkalussa erilainen:

```{.python tiedosto="esimerkit/vuo/ajo.py" osa="versio"}
```

```{.python tiedosto="esimerkit/vuo/kulku.py" osa="versiot"}
```

Versio luetaan kerran kustakin työkalusta (`functools.cache`). Vuo
lisää sen vaiheen leimaan, joten työkalun päivitys ajaa vaiheet
uudelleen. Versiotieto tallennetaan myös manifestiin. Kaupallisissa
työkaluissa version lisäksi kannattaa tallentaa käytetyt lisenssit ja
mahdolliset korjauspäivitykset, koska niiden numerointi vaihtelee.

## Kaksi simulaattoria, yksi rajapinta

Projekti käyttää usein useampaa simulaattoria: nopeaa Verilatoria
regressioihin, tapahtumapohjaista simulaattoria aaltomuotojen
tutkimiseen ja kaupallista simulaattoria allekirjoitusta varten. Vuon
ei pitäisi tietää, mikä niistä on käytössä. Rajapinta kuvataan
protokollana:

```{.python tiedosto="esimerkit/vuo/simulaattorit.py" osa="rajapinta"}
```

```{.python tiedosto="esimerkit/vuo/simulaattorit.py" osa="toteutukset"}
```

Toteutukset eroavat komentoriveiltään. Verilator kääntää testipenkin
C++-ohjelmaksi ja ajaa sen. Icarus-toteutus on samanlainen: se kääntää
komennolla `iverilog -g2012` välikoodiksi, jonka `vvp` tulkitsee. Makrot annetaan kummallekin samalla valitsimella `-D`, ja
plusargit (`+siemen=3`) välitetään ajon komentoriville sellaisinaan.
Valitsin `-n` estää Icarusta jäämästä odottamaan käyttäjän komentoa,
jos simulointi pysähtyy `$stop`-kutsuun.

Simulaattoririippumattomuus on hyödyllistä myös tarkistuksena. Jos
kaksi simulaattoria antaa samasta testipenkistä eri tuloksen, joko
testipenkissä on kilpatilanne tai toinen simulaattori tulkitsee
kieltä eri tavalla:

```{.python tiedosto="esimerkit/03-ohjaus.py" osa="simulaattorit"}
```

Tuloksen kolme viimeistä riviä ovat tästä. Molemmat simulaattorit
löytävät samat kolme virhettä ja laskevat saman kattavuuden. Icarus
kuitenkin ilmoittaa käännöksessä rajoituksistaan (`sorry: ... are not
currently supported`). Ne eivät ole virheitä vaan tietoa siitä, mitä
kielen ominaisuuksia työkalu ei tue täysin. Tässä se jättää
huomiotta `unique`-määreen tarkistuksen. Luku 6 luokittelee
tällaiset ilmoitukset omaksi vakavuusluokakseen.

## Käytännössä

- **Ei kuorta.** Komento listana, `subprocess.run` ilman
  `shell=True`-asetusta. Uudelleenohjaukset ja putket tehdään
  Pythonissa.
- **Jokaisella ajolla aikaraja.** Raja valitaan sen mukaan, kuinka
  kauan ajo normaalisti kestää. Esimerkiksi kymmenkertainen
  tavanomainen kesto erottaa jumin hitaasta ajosta.
- **Simuloinnin tulos testipenkin tulosrivistä.** Puuttuva tulosrivi
  on virhe. Sama koskee kaikkia työkaluja, jotka päättyvät nollaan
  myös epäonnistuessaan.
- **Loki säilytetään, vaikka ajo onnistuisi.** Onnistuneen ajon lokista
  luetaan varoitukset, resurssit ja ajoitus.
- **Interaktiivinen tila vain tutkimiseen.** Kun ongelma on löydetty
  interaktiivisesti, korjattu ajo kirjoitetaan skriptiksi ja ajetaan
  eräajona.

## Itsearviointi

- Osaat ajaa EDA-työkalun eräajona niin, että loki, paluuarvo ja
  aikakatkaisu käsitellään eikä virhe katoa.
- Osaat selittää, miksi simulaattorin paluuarvo ei kerro testin
  tulosta, ja tulkita tuloksen lokista luotettavasti.
- Osaat piilottaa simulaattorin protokollan taakse ja vertailla kahden
  simulaattorin tuloksia.
- Osaat kertoa, miksi ulomman Maken `MAKEFLAGS` on poistettava
  työkalun omista Make-kutsuista.

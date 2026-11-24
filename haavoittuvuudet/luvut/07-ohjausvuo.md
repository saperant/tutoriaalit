# Ohjausvuon eheys

NX esti suorittamasta dataa, mutta ohjelmassa ja sen kirjastoissa on
valmiiksi paljon suoritettavaa koodia. Jos muistivirhe antaa vallan
paluuosoitteisiin tai funktio-osoittimiin, ohjelman oma koodi voidaan
suorittaa väärässä järjestyksessä. Tätä tekniikkaa kutsutaan
*paluuorientoituneeksi ohjelmoinniksi* (*return-oriented programming*,
ROP). Tämä luku selittää periaatteen sen verran kuin on tarpeen
suojausten ymmärtämiseksi ja näyttää, miten *ohjausvuon eheyden*
(*control-flow integrity*, CFI) suojaukset katkaisevat sen.

## Periaate

```{.text tiedosto="esimerkit/07-ohjausvuo/kaavio.txt"}
```

Tavallisessa paluussa `ret` ottaa pinosta osoitteen, jonka `call`
sinne tallensi. Jos pino on korruptoitunut, `ret` hyppää minne
tahansa. Jokainen funktion loppu ja moni muukin käskyjono päättyy
`ret`-käskyyn, joten pinoon kirjoitettu osoitesarja voi ketjuttaa
lyhyitä olemassa olevia käskyjonoja peräkkäin. Uutta koodia ei
tarvita, joten NX ei yksin auta. Samaa ajatusta voi käyttää myös
epäsuorilla hypyillä ja kutsuilla (*jump-oriented programming*).

Ketjun rakentaminen vaatii, että osoitteet tunnetaan (ASLR estää), että
paluuosoite voidaan ylikirjoittaa huomaamatta (kanari estää jatkuvan
ylivuodon) ja että `ret` ja epäsuorat hypyt voivat mennä minne tahansa.
Viimeistä vastaan on kaksi suojausperhettä:

- **Takaisinpäin suuntautuvan** ohjausvuon (*backward edge*, paluut)
  suojaus: paluuosoite tarkistetaan suojattua kopiota tai
  allekirjoitusta vasten. Varjopino (Intel CET SHSTK, Armin GCS) ja
  Armin osoitintunnisteet (PAC).
- **Eteenpäin suuntautuvan** ohjausvuon (*forward edge*, epäsuorat
  kutsut ja hypyt) suojaus: kohteen on oltava sallittu. Clangin CFI
  tarkistaa tyypin, Intel IBT ja Armin BTI sallivat hypyn vain
  merkittyyn kohtaan.

## Clangin CFI

Lisäosarekisteri tallentaa funktiot yleisinä osoittimina. Haku
väärällä nimellä palauttaa funktion, jonka tyyppi on eri kuin kutsujan
olettama:

```{.c tiedosto="esimerkit/07-ohjausvuo/lisaosat.c" osa="kutsu"}
```

C sallii muunnoksen funktio-osoitintyyppien välillä, mutta kutsu
väärällä tyypillä on määrittelemätöntä käytöstä. Tavallisesti
`celsius` saisi `double`-argumenttinsa rekisteristä, johon kutsuja ei
laittanut mitään, ja palauttaisi roskaa. Clangin CFI lisää jokaiseen
epäsuoraan kutsuun tarkistuksen: kohteen on oltava funktio, jonka tyyppi
vastaa osoittimen tyyppiä.

```{.bash tiedosto="esimerkit/07-ohjausvuo/aja.sh" osa="cfi"}
```

```{.tuloste tiedosto="esimerkit/07-ohjausvuo/odotettu" osa="t1"}
```

Oikeantyyppiset kutsut toimivat, myös `celsius` silloin, kun se
kutsutaan oikealla tyypillä. Väärä kutsu pysähtyi ennen hyppyä. CFI
vaatii koko ohjelman näkymän, joten se käännetään linkitysaikaisella
optimoinnilla (`-flto`) ja piilotetulla näkyvyydellä
(`-fvisibility=hidden`); linkkerinä on LLVM:n lld. Valitsin
`-fno-sanitize-trap=cfi` tuottaa luettavan virheilmoituksen.
Tuotannossa käytetään oletusta, joka on pelkkä `ud2`-keskeytys ilman
ajonaikaista kirjastoa. Kevyempi tarkistus ilman LTO:ta on
`-fsanitize=function`.

Androidin ydin ja Chrome käyttävät Clangin CFI:tä tuotannossa.
Microsoftin vastaava on *Control Flow Guard*.

## CET: varjopino ja IBT

Intelin *Control-flow Enforcement Technology* on prosessorin tuki
kummallekin suunnalle:

- **Varjopino** (*shadow stack*, SHSTK): `call` tallentaa paluuosoitteen
  sekä tavalliseen pinoon että erilliseen suojattuun pinoon, ja `ret`
  vertaa niitä. Ero aiheuttaa poikkeuksen. Ohjelma ei voi kirjoittaa
  varjopinoon tavallisilla käskyillä.
- **IBT** (*indirect branch tracking*): epäsuoran hypyn tai kutsun
  kohteessa on oltava `endbr64`-käsky, muuten prosessori aiheuttaa
  poikkeuksen.

GCC lisää merkinnät valitsimella `-fcf-protection=full`, joka on
Ubuntun oletus:

```{.c tiedosto="esimerkit/07-ohjausvuo/laske.c"}
```

```{.bash tiedosto="esimerkit/07-ohjausvuo/aja.sh" osa="cet"}
```

```{.tuloste tiedosto="esimerkit/07-ohjausvuo/odotettu" osa="t2"}
```

Funktio alkaa `endbr64`-käskyllä, joka on vanhemmilla prosessoreilla
tyhjä käsky. Objektitiedoston huomautus kertoo, että koodi tukee IBT:tä
ja varjopinoa; linkkeri merkitsee ohjelman yhteensopivaksi vain, jos
kaikki sen osat tukevat niitä. Suojaus on käytössä vasta, kun prosessori,
ydin ja C-kirjasto ottavat sen päälle: Linux tukee käyttäjätilan
varjopinoa versiosta 6.6 alkaen, ja glibc ottaa sen käyttöön asetuksella.
Tämän paketin ympäristössä sitä ei ajeta, joten merkinnät näytetään
staattisesti.

## PAC ja BTI

ARMv8.3:n *pointer authentication* (PAC) allekirjoittaa paluuosoitteen
ennen sen tallentamista ja tarkistaa allekirjoituksen ennen paluuta.
Allekirjoitus sijoitetaan osoitteen käyttämättömiin ylimpiin bitteihin,
ja avain on prosessorin rekisterissä, johon ohjelma ei pääse. BTI
(*branch target identification*, ARMv8.5) vastaa IBT:tä:

```{.bash tiedosto="esimerkit/07-ohjausvuo/aja.sh" osa="pac"}
```

```{.tuloste tiedosto="esimerkit/07-ohjausvuo/odotettu" osa="t3"}
```

`paciasp` allekirjoittaa paluuosoitteen (`x30`) pinon osoittimen
kanssa ja `autiasp` tarkistaa sen. Käskyt on koodattu `hint`-käskyinä,
jotta ne ovat vanhemmilla prosessoreilla tyhjiä. Erillistä `bti c`
-käskyä ei tarvita, koska `paciasp` kelpaa myös BTI:n kohdemerkinnäksi.
Applen ARM-prosessorit ja Androidin uudet laitteet käyttävät PAC:ia.

## Käytännössä

- **Ota CET- ja PAC/BTI-merkinnät käyttöön** (`-fcf-protection=full`,
  `-mbranch-protection=standard`): niiden hinta on pieni, ja suojaus
  tulee käyttöön, kun alusta tukee sitä.
- **Harkitse Clangin CFI:tä** ohjelmissa, joissa on paljon epäsuoria
  kutsuja ja ulkoista syötettä. Se löytää myös tyyppivirheitä
  testeissä.
- **Älä muunna funktio-osoittimia tyyppien välillä.** Rekisterit, jotka
  tallentavat funktioita yleisinä osoittimina, ovat juuri CFI:n
  löytämien virheiden lähde; tallenna tyyppi mukaan tai käytä
  `union`ia, jonka jäsen valitaan tunnisteella.
- **Muista suojauksen ehdot**: ohjausvuon eheys ei estä tietovuotoa
  eikä muistivirhettä, joka muuttaa vain dataa.

## Itsearviointi

- Osaat selittää paluuorientoituneen ohjelmoinnin periaatteen ja sen,
  miksi NX ei yksin estä sitä.
- Osaat erottaa takaisin- ja eteenpäin suuntautuvan ohjausvuon
  suojaukset ja nimetä kummankin toteutuksia.
- Osaat kääntää ohjelman Clangin CFI:llä ja tulkita sen virheilmoituksen.
- Osaat tunnistaa CET-, PAC- ja BTI-merkinnät konekielestä.

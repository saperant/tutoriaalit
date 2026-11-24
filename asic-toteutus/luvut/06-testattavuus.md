# Testattavuus

Verifiointi kertoo, että suunnitelma on oikein. Tuotantotesti kertoo,
että juuri tämä piiri valmistui oikein: kiekolla on aina hiukkasia,
oikosulkuja ja katkoksia, ja jokainen piiri testataan ennen
toimitusta. Testi on tehtävä nopeasti (testerin sekunti maksaa) ja
kattavasti (viallinen piiri asiakkaalla maksaa enemmän). Testattavuus
(design for testability, DFT) on siksi suunnittelun osa, ei
jälkikäteinen lisä.

## Vikamalli ja vikasimulointi

Fyysisiä vikoja ei voi luetella, joten testi kohdistetaan malliin.
Yleisin on juuttumisvika (stuck-at): johdin on pysyvästi 0 tai 1.
Testivektori *havaitsee* vian, jos piirin lähtö eroaa virheettömän
piirin lähdöstä. Vikakattavuus on havaittujen vikojen osuus kaikista.

```{.python tiedosto="esimerkit/06-vikasim.py" osa="piiri"}
```

```{.python tiedosto="esimerkit/06-vikasim.py" osa="vikasimulointi"}
```

```{.python tiedosto="esimerkit/06-vikasim.py" osa="kattavuus"}
```

```{.tuloste tiedosto="esimerkit/06-vikasim.odotettu"}
```

Satunnaiset vektorit löytävät helpot viat nopeasti, mutta viimeiset
prosentit vaativat paljon vektoreita. ATPG-työkalu (automatic test
pattern generation) etsii jokaiselle jäljellä olevalle vialle vektorin
algoritmisesti (D-algoritmi, PODEM): se asettaa vikapaikan vastakkaiseen
arvoon ja etsii polun, jota pitkin ero näkyy lähdössä. Tiivistys
yhdistää vektoreita, koska testiaika on suoraan verrannollinen niiden
määrään. Tuotannossa tavoite on tyypillisesti yli 99 %:n
juuttumisvikakattavuus sekä viiveviat (transition fault), jotka
havaitaan kahdella peräkkäisellä vektorilla oikealla kellotaajuudella.

## Scan-ketju

Sekvenssipiirin sisäinen tila ei näy tuloista ja lähdöistä. Scan-ketju
ratkaisee ongelman: jokainen kiikku vaihdetaan scan-kiikuksi, jossa on
multiplekseri, ja kiikut ketjutetaan siirtorekisteriksi. Testitilassa
(SE=1) tila siirretään sisään ja ulos sarjamuodossa; toimintatilassa
(SE=0) piiri toimii normaalisti yhden jakson. Kombinaatiologiikka
testataan näin kuin ilman muistia.

```{.python tiedosto="esimerkit/06-scan.py" osa="ketju"}
```

Testipenkki siirtää laskuriin tilan, ajaa yhden toiminnallisen jakson
ja siirtää tuloksen ulos. Juuttumisvika estää laskurin kasvamisen:

```{.python tiedosto="esimerkit/06-scan.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/06-scan.odotettu"}
```

Scan maksaa pinta-alaa (SDFF_X1 on 31 % suurempi kuin DFF_X1), yhden
multiplekserin viiveen kriittiselle polulle ja kolme nastaa. Suurissa
piireissä ketjuja on satoja, ja testidata pakataan piirin sisällä
(test compression), jotta testeri syöttää vain murto-osan biteistä.

## BIST ja JTAG

Muistit ja suuret lohkot testaavat itsensä: sisäänrakennettu itsetesti
(built-in self-test, BIST) tuottaa vektorit LFSR:llä ja tiivistää
vasteet MISR:llä allekirjoitukseksi, jota verrataan tunnettuun
arvoon.

```{.systemverilog tiedosto="esimerkit/06-bist.sv" osa="lfsr"}
```

```{.systemverilog tiedosto="esimerkit/06-bist.sv" osa="misr"}
```

```{.systemverilog tiedosto="esimerkit/06-bist.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/06-bist.odotettu"}
```

Muistien BIST käyttää satunnaisvektorien sijaan algoritmisia
March-testejä, jotka löytävät myös solujen väliset kytkeytymisviat.
JTAG (IEEE 1149.1) on piirin standardi testiportti: neljän johtimen
tilakone (TAP), jonka kautta luetaan tunnisteet, ohjataan scan-
ketjuja ja BIST-lohkoja ja testataan piirilevyn juotokset
reunarekisterillä (boundary scan). Sama portti toimii usein myös
suorittimen debug-yhteytenä.

## Käytännössä

- **DFT-säännöt RTL:ään asti.** Scan vaatii, että kiikkujen kello ja
  nollaus ovat testitilassa testerin ohjattavissa. Sisäisesti
  generoidut kellot ja asynkroniset nollaukset tarvitsevat
  ohitusmultiplekserit.
- **Scan-ketjut uudelleenjärjestetään sijoittelun jälkeen.** Ketjun
  järjestys valitaan fyysisen läheisyyden mukaan, jotta ketju ei
  lisää johdinpituutta; testivektorit generoidaan uudelleen.
- **Pitoaika scan-ketjussa.** Ketjun kiikkujen välissä ei ole
  logiikkaa, joten ne ovat klassinen pitorikkeiden lähde (luku 4).
- **Kattavuus on sopimuskysymys.** Autoteollisuus vaatii korkeampaa
  kattavuutta ja käytönaikaisia testejä (ISO 26262) kuin
  kulutuselektroniikka.

## Itsearviointi

- Osaat selittää juuttumisvikamallin, vikasimuloinnin ja
  vikakattavuuden.
- Osaat kuvata scan-ketjun rakenteen ja testijakson: siirto, kaappaus
  ja siirto ulos.
- Osaat kertoa, miten LFSR ja MISR toteuttavat itsetestauksen.
- Osaat kertoa JTAG:n tehtävät piirin ja piirilevyn testauksessa.

# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. Kahden komplementti etumerkillisille luvuille. Sama summain laskee
   kummatkin, ja vähennys on yhteenlasku käännetyllä luvulla.
2. Kuvaa funktio selkeästi ja anna työkalun sieventää. Kerro
   yhdentekevät syötteet.
3. Testaa pieni kombinaatiologiikka tyhjentävästi ja vertaa
   viitteeseen, joka on kirjoitettu eri tavalla.
4. Totuustaulu kertoo, mihin piiri asettuu, ei mitä se tekee matkalla.
   Hasardit ovat todellisia, mutta synkroninen suunnittelu piilottaa
   ne.
5. Kiikut, ei salpoja. Yksi kello, sallinta hitaaseen toimintaan.
6. Jokainen asynkroninen syöte kulkee kahden kiikun tahdistimen läpi.
7. Kriittinen polku määrää kellotaajuuden. Lyhennä sitä rakenteella,
   liukuhihnalla tai hitaammalla kellolla, ja korjaa pitorikkeet aina.
8. Tilakone suunnitellaan tauluna ennen koodia, ja taulu on
   testipenkin viitemalli.

## Mallit

| Malli | Ongelma, jonka se ratkaisee | Luku |
|-------|-----------------------------|------|
| Vähennys summaimella ($a + \bar{b} + 1$) | yksi summain kahteen laskuun | 2, 6 |
| Gray-koodi | välitilat luettaessa toisen kellon tahdissa | 2, 9 |
| Yhdentekevät arvot | pienempi logiikka | 4 |
| Kelvollisuusbitti | onko data merkityksellistä | 5 |
| Avoin nielu ja ylösveto | monta lähettäjää yhdellä johtimella | 3 |
| Generoi ja välitä | nopea muistibitti | 6 |
| Konsensustermi | staattinen hasardi | 7 |
| Kahden kiikun tahdistin | metastabiilisuus | 8 |
| Sallinta ja synkroninen nollaus | rekisterin ohjaus yhdellä kellolla | 9 |
| Kaksiosainen tilakone | luettava seuraavan tilan logiikka | 10 |
| Liukuhihna | pitkä kriittinen polku | 11 |
| Datapolku ja ohjaus erikseen | suuren piirin jäsentäminen | 12 |

## Jatkotaidot

- *RTL-suunnittelu SystemVerilogilla* ja *RTL-suunnittelu VHDL:llä*:
  tämän tutoriaalin rakenteet synteesikelpoisena koodina, muistit ja
  FIFOt, nollaukset ja kellotusalueiden ylitys.
- *Assembly* ja *Tietokonearkkitehtuuri*: käskykanta, liukuhihna,
  välimuistit ja virtuaalimuisti luvun 12 datapolun jatkeena.
- *Miten tietokone laskee*: kokonaisluku- ja liukulukuaritmetiikka
  ohjelmoijan näkökulmasta, kertolaskun ja jakolaskun algoritmit.
- *Lukujen esitys ja kiinteän pilkun aritmetiikka*: luvut ja pyöristys
  signaalinkäsittelyn laitteistossa.
- *FPGA-toteutus* ja *ASIC-toteutus*: synteesi, sijoittelu ja
  ajoitusanalyysi oikeilla työkaluilla.
- *Elektroniikan perusteet ja SPICE*: transistori ja portti
  sähköisenä piirinä.
- *Oheislaiteväylät*: avoin nielu ja siirtorekisteri käytännön
  väylissä (I2C, SPI, UART).

## Lähteet ja lisälukemista

- Harris, D. M. & Harris, S. L.: *Digital Design and Computer
  Architecture*, RISC-V Edition. Morgan Kaufmann, 2021. Tämän
  tutoriaalin aihepiiri yhdessä kirjassa, suorittimeen asti.
- Wakerly, J. F.: *Digital Design: Principles and Practices*. 5. painos,
  Pearson, 2018. Perusteellinen käsikirja kombinaatio- ja
  sekvenssilogiikasta.
- Weste, N. & Harris, D.: *CMOS VLSI Design: A Circuits and Systems
  Perspective*. 4. painos, Addison-Wesley, 2010. CMOS-portit,
  viiveet ja ajoitus piiritasolla.
- Patterson, D. A. & Hennessy, J. L.: *Computer Organization and
  Design*, RISC-V Edition. Morgan Kaufmann. Datapolusta suorittimeen.
- Ginosar, R.: *Metastability and Synchronizers: A Tutorial*. IEEE
  Design & Test of Computers, 2011. Tahdistimien MTBF ja sudenkuopat.
- McCluskey, E. J.: *Minimization of Boolean Functions*. Bell System
  Technical Journal 35(6), 1956. Quine–McCluskeyn menetelmän
  alkuperäinen kuvaus.
- Verilatorin dokumentaatio: <https://verilator.org/guide/latest/>.
- IEEE 1800-2023, *SystemVerilog*. Kielen standardi.

Tämä tutoriaali on kirjoitettu itsenäisesti; lähteitä on käytetty
tarkistukseen, eikä niistä ole kopioitu tekstiä.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkikoodia saa
käyttää ja muokata saman lisenssin ehdoin.

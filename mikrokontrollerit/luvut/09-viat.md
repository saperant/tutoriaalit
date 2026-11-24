# Viat ja vikakäsittelijät

Kun Cortex-M ei voi suorittaa käskyä, se ei kaadu hiljaa vaan aiheuttaa
*vikapoikkeuksen*. Lukeminen osoitteesta, jossa ei ole mitään,
tuntematon käsky, jako nollalla tai hyppy osoitteeseen ilman
Thumb-bittiä päätyvät kaikki käsittelijään, joka saa tietää syyn ja
tarkan paikan. Tavallisessa ohjelmassa vikakäsittelijä on ikuinen
silmukka, ja laite jähmettyy. Hyvä vikakäsittelijä on sen sijaan
ohjelman arvokkain vianetsintätyökalu.

## Vikapoikkeukset

| Poikkeus | Tyypillinen syy | Sallittava |
|------------|----------------------------------------|------------------------|
| HardFault | eskaloitunut vika, vika vektorin luvussa | aina päällä |
| MemManage | MPU:n suojaama alue, suoritus XN-alueelta | SHCSR.MEMFAULTENA |
| BusFault | osoite, jossa ei ole laitetta tai muistia | SHCSR.BUSFAULTENA |
| UsageFault | tuntematon käsky, Thumb-bitti, jako nollalla, tasaus | SHCSR.USGFAULTENA |

Kolme jälkimmäistä ovat resetin jälkeen pois päältä, jolloin niiden
viat *eskaloituvat* HardFaultiksi. Eskaloituminen tapahtuu myös, jos
vika sattuu käsittelijässä, jonka prioriteetti estää vikakäsittelijän
ajon. Jos vika sattuu HardFault-käsittelijässä itsessään, prosessori
menee *lukkotilaan* (lockup) ja pysähtyy; monet piirit resetoituvat
silloin automaattisesti. Cortex-M0+:ssa on vain HardFault.

## Syy ja paikka

Syy on SCB:n tilarekistereissä:

| Rekisteri | Sisältö |
|----------------------|----------------------------------------------------------|
| CFSR, bitit 0–7 (MMFSR) | MemManage: IACCVIOL, DACCVIOL, MSTKERR, MMARVALID |
| CFSR, bitit 8–15 (BFSR) | BusFault: IBUSERR, PRECISERR, IMPRECISERR, STKERR, BFARVALID |
| CFSR, bitit 16–31 (UFSR) | UsageFault: UNDEFINSTR, INVSTATE, INVPC, NOCP, UNALIGNED, DIVBYZERO |
| HFSR | FORCED: eskaloitunut; VECTTBL: vektorin luku epäonnistui |
| MMFAR, BFAR | vian osoite, jos vastaava VALID-bitti on asetettu |

Paikka on pinossa. Poikkeuksen alussa tallennettu kehys sisältää PC:n,
joka osoittaa vian aiheuttaneeseen käskyyn, ja LR:n, joka kertoo,
mistä funktio kutsuttiin. Käsittelijän on siis ensin löydettävä kehys,
mikä tehdään samalla kolmen käskyn assemblyllä kuin SVC-käsittelijässä
luvussa 2.

```{.c tiedosto="esimerkit/10-viat/main.c" osa="kehys"}
```

```{.c tiedosto="esimerkit/10-viat/main.c" osa="stub"}
```

Kaikki neljä vikapoikkeusta ohjataan samaan koodiin aliaksilla.
C-osa tulostaa poikkeuksen nimen IPSR:n perusteella, avaa CFSR:n bitit
ja osoiterekisterit ja kuittaa tilabitit kirjoittamalla ne takaisin.

```{.c tiedosto="esimerkit/10-viat/main.c" osa="bitit"}
```

```{.c tiedosto="esimerkit/10-viat/main.c" osa="kasittely"}
```

Tämän esimerkin käsittelijä jatkaa ohjelmaa siirtämällä kehyksen
PC:n vian aiheuttaneen käskyn ohi, jotta kaikki tapaukset nähdään
samassa ajossa. Käskyn pituus päätellään sen ensimmäisistä biteistä:
Thumb-2:n 32-bittiset käskyt alkavat bittikuvioilla `11101`, `11110`
ja `11111`. INVSTATE-vian kohdalla PC on hypyn kohde, joten
käsittelijä palaa kutsujaan LR:n kautta ja palauttaa T-bitin.
Tuotantolaitteessa vian ohittaminen olisi vaarallista; siellä
käsittelijä tallentaa tiedot ja käynnistää laitteen uudelleen.

## Esimerkki: seitsemän vikaa

Vian aiheuttavat käskyt on kirjoitettu inline-assemblynä ja nimetty
globaalilla nimiöllä, jotta käsittelijä voi kertoa tarkan kohdan
vertaamalla kehyksen PC:tä nimiön osoitteeseen. Oikeassa ohjelmassa
sama tieto saadaan työkalulla: `arm-none-eabi-addr2line -e ohjelma.elf
0x1234` kertoo osoitetta vastaavan tiedoston ja rivin.

```{.c tiedosto="esimerkit/10-viat/main.c" osa="viat"}
```

Seitsemäs vika tulee muistinsuojausyksiköstä MPU:sta, joka asetetaan
luvun lopussa. Ajo:

```{.c tiedosto="esimerkit/10-viat/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/10-viat.odotettu"}
```

Tapaukset yksi kerrallaan:

1. **Kuvaamaton osoite.** Väylä palauttaa virheen, ja koska BusFault
   ei ole sallittu, vika eskaloituu: HardFault, HFSR.FORCED ja silti
   CFSR:ssä alkuperäinen syy ja BFAR:ssa osoite.
2. **Sama vikakäsittelijät sallittuina.** Nyt syy näkyy jo
   poikkeuksesta. Vikojen salliminen käynnistyksessä on halpa tapa
   nopeuttaa vianetsintää.
3. **Jako nollalla ilman ansaa.** Cortex-M3:n `udiv` palauttaa nollan
   eikä aiheuta vikaa. Hiljainen väärä tulos on pahempi kuin vika.
4. **DIV_0_TRP.** CCR-rekisterin bitti muuttaa jaon nollalla
   UsageFaultiksi. Se kannattaa pitää päällä kehityksessä.
5. **Tuntematon käsky.** Syynä on yleensä hyppy dataan tai
   ylikirjoitettu paluuosoite pinossa.
6. **Thumb-bitti nolla.** Funktio-osoitin, jonka alin bitti on
   nolla, eli yleensä alustamaton tai ylikirjoitettu osoitin.
7. **MPU.** Kirjoitus vain luettavaksi merkitylle alueelle, MMFAR
   kertoo osoitteen.

BusFault voi olla myös *epätarkka* (IMPRECISERR): prosessori on
puskuroinut kirjoituksen ja jatkanut, ja vika tulee väylältä vasta
myöhemmin, jolloin PC osoittaa jonnekin myöhemmäksi eikä BFAR ole
voimassa. Vianetsinnän ajaksi kirjoituspuskurin voi Cortex-M3:ssa ja
-M4:ssä kytkeä pois (ACTLR.DISDEFWBUF), jolloin viat muuttuvat
tarkoiksi.

## Tavallisimmat syyt

- **Pinon ylivuoto.** Pino kasvaa muuttujien päälle, ylikirjoittaa
  paluuosoitteen, ja funktio palaa satunnaiseen osoitteeseen. Oireena
  on UNDEFINSTR, INVSTATE tai IBUSERR, ja paikka on jossain aivan muualla
  kuin syy.
- **Alustamaton funktio-osoitin.** Nolla-osoitteeseen hyppy antaa
  INVSTATEn. Nollaosoittimen *luku* sen sijaan ei aiheuta vikaa, koska
  osoitteessa 0 on vektoritaulu; se palauttaa pinon alkuarvon.
- **Keskeytys ilman käsittelijää**, jolloin oletuskäsittelijä
  laukeaa, tai käsittelijän väärin kirjoitettu nimi.
- **Liukulukuyksikkö sallimatta** (NOCP) Cortex-M4F:llä tai -M7:llä.
- **Tasaamaton monisanainen käsky.** `ldrd`, `strd`, `ldm` ja `stm`
  vaativat tasatun osoitteen, vaikka tavallinen `ldr` hyväksyy
  tasaamattoman Cortex-M3:lla. Pakattujen rakenteiden (`packed`) kenttiin
  osoittavat osoittimet tuottavat näitä.
- **Oheislaitteen kello pois päältä.** Useimmissa piireissä rekisterit
  vain lukevat nollaa, mutta joissakin (esimerkiksi NXP:n Kinetis)
  viittaus aiheuttaa BusFaultin.

## Muistinsuojausyksikkö

MPU (Memory Protection Unit) ei käännä osoitteita kuten
muistinhallintayksikkö, mutta se voi asettaa osoitealueille oikeudet:
luku, kirjoitus, suoritus ja etuoikeudet. ARMv7-M:n MPU:ssa on
tyypillisesti kahdeksan aluetta, joiden koko on kahden potenssi
(vähintään 32 tavua) ja alku tasattu koon mukaan. ARMv8-M:ssä alue
määritellään alku- ja loppuosoitteella 32 tavun tarkkuudella.

```{.c tiedosto="esimerkit/10-viat/main.c" osa="mpu"}
```

PRIVDEFENA tarkoittaa, että etuoikeutettu koodi saa käyttää muuta
muistia oletusmuistikartan mukaisesti, joten riittää määritellä vain
poikkeukset. Bare-metal-ohjelmassakin MPU kannattaa ottaa käyttöön
kolmeen tarkoitukseen:

1. **Pinon vartija.** 32 tavun alue pinon pohjalla ilman oikeuksia
   muuttaa hiljaisen ylivuodon välittömäksi MemManage-viaksi. Koska
   vikakäsittelijäkin tarvitsee pinoa, sen kannattaa vaihtaa omaan
   pieneen pinoonsa.
2. **RAM ilman suoritusoikeutta** (XN). Hyökkääjän tai virheen RAMiin
   kirjoittama data ei ole suoritettavaa koodia.
3. **Flash ilman kirjoitusoikeutta** ja vakiotaulukot vain luettaviksi.

Ilman MPU:ta pinon voi sijoittaa RAMin alkuun, jolloin ylivuoto kirjoittaa
RAMin alapuolelle osoitteeseen, jossa ei ole muistia, ja aiheuttaa
BusFaultin muuttujien ylikirjoittamisen sijaan.

## Tuotannon vikakäsittelijä

Kentällä vikakäsittelijä ei voi tulostaa päätteeseen, eikä ohjelmaa
voi jatkaa. Hyvä käsittelijä

1. tallentaa CFSR:n, HFSR:n, osoiterekisterit ja kehyksen
   `.noinit`-alueelle tarkistesumman kanssa
2. käynnistää laitteen uudelleen (AIRCR.SYSRESETREQ)
3. lähettää tallennetun raportin seuraavassa käynnistyksessä
   lokiin tai palvelimelle.

Näin jokainen kaatuminen kentällä tuottaa paikan ja syyn. Laajempi
versio, *ydinvedos* (core dump), tallentaa myös pinon tai koko RAMin
flashiin, josta gdb voi myöhemmin ladata sen. Zephyr, Memfault ja
monet valmistajien SDK:t tarjoavat tämän valmiina.

## Käytännössä

- **Salli MemManage, BusFault ja UsageFault** käynnistyksessä ja
  kehityksessä myös DIV_0_TRP.
- **Kirjoita vikakäsittelijä ensimmäisenä**, ennen kuin tarvitset
  sitä. Ikuinen silmukka vikakäsittelijänä hukkaa jokaisen vian.
- **Tulkitse kehyksen PC ja LR** `addr2line`-työkalulla tai gdb:llä
  (`info symbol`, `list *0x1234`).
- **Käytä MPU:ta pinon vartijana** ja estä suoritus RAMista.
- **Tallenna vikaraportti resetin yli** ja kerää ne kentältä.

## Itsearviointi

- Osaat luetella neljä vikapoikkeusta, niiden tyypilliset syyt ja
  eskaloitumisen ehdot.
- Osaat kirjoittaa vikakäsittelijän, joka löytää kehyksen oikeasta
  pinosta ja tulostaa PC:n, LR:n, CFSR:n ja osoiterekisterit.
- Osaat tulkita CFSR:n bitit ja erottaa tarkan ja epätarkan
  väylävirheen.
- Osaat määritellä MPU-alueen ja käyttää sitä pinon vartijana tai
  vain luettavana alueena.
- Osaat suunnitella tuotannon vikakäsittelijän, joka säilyttää
  vikatiedot uudelleenkäynnistyksen yli.

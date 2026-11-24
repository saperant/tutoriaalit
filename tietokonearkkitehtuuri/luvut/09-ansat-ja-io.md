# Poikkeukset, keskeytykset ja I/O

Suoritin ei elä yksin. Sen on reagoitava virheisiin (laiton käsky,
sivuvirhe), ohjelmien pyyntöihin (järjestelmäkutsu) ja ulkomaailman
tapahtumiin (ajastin, verkkokortti, näppäimistö), ja sen on voitava
siirtää dataa laitteille ja laitteilta. Tämä luku käsittelee
mekanismit, joilla käskyjen virta katkaistaan hallitusti, ja keinot,
joilla ohjelma puhuu oheislaitteille.

## Ansat

RISC-V kutsuu yhteisellä nimellä **ansaksi** (*trap*) kaikkia tilanteita,
joissa suoritus siirtyy käsittelijään:

- **Poikkeus** (*exception*) on synkroninen: sen aiheuttaa tietty käsky,
  ja se toistuu, jos käsky suoritetaan uudelleen. Laiton käsky,
  kohdistamaton osoite, sivuvirhe, `ecall`, `ebreak`.
- **Keskeytys** (*interrupt*) on asynkroninen: se tulee käskyvirran
  ulkopuolelta ja voi osua minkä tahansa kahden käskyn väliin.
  Ajastin, ohjelmistokeskeytys toiselta ytimeltä, ulkoinen laite.

Ansan sattuessa laitteisto tekee neljä asiaa yhdessä jaksossa:

1. `mepc` ← keskeytetyn käskyn osoite (poikkeuksessa aiheuttaja itse,
   keskeytyksessä seuraavaksi suoritettava käsky).
2. `mcause` ← syykoodi. Ylin bitti on 1 keskeytyksille.
3. `mstatus.MPIE` ← `mstatus.MIE` ja `MIE` ← 0: keskeytykset estetään,
   ja vanha tila tallennetaan. `MPP` saa edellisen etuoikeustason.
4. `pc` ← `mtvec`.

Lisäksi `mtval` saa poikkeukseen liittyvän arvon, esimerkiksi virheellisen
osoitteen. Käsittelijä palaa käskyllä `mret`, joka palauttaa `MIE`:n ja
etuoikeustason ja hyppää osoitteeseen `mepc`. Simulaattori toteuttaa
vain M-tilan, joten `MPP`-kenttää ei tarvita:

```{.cpp tiedosto="esimerkit/yhteinen/kone.hpp" osa="ansa"}
```

```{.cpp tiedosto="esimerkit/yhteinen/kone.hpp" osa="mret"}
```

| mcause | Syy | Mitä käsittelijä yleensä tekee |
|--------|-----|--------------------------------|
| 2 | laiton käsky | emuloi (esim. puuttuva laajennus) tai lopettaa ohjelman |
| 4 | kohdistamaton lataus | emuloi tavu kerrallaan tai lopettaa |
| 8 / 11 | `ecall` U- / M-tilasta | järjestelmäkutsu |
| 12, 13, 15 | sivuvirhe nouto / lataus / talletus | luku 8 |
| 0x8000'0003 | ohjelmistokeskeytys | toisen ytimen pyyntö (IPI) |
| 0x8000'0007 | ajastinkeskeytys | ajoitus, aikakatkaisut |
| 0x8000'000b | ulkoinen keskeytys | kysy keskeytysohjaimelta, mikä laite |

## Esimerkki: käsittelijä

Ohjelma asentaa käsittelijän, aiheuttaa kolme poikkeusta, sallii
ajastinkeskeytyksen ja odottaa kolmea keskeytystä. Käsittelijä kirjaa
jokaisen ansan syyn ja osoitteen muistiin:

```{.cpp tiedosto="esimerkit/09-ansat.cpp" osa="ohjelma"}
```

```{.cpp tiedosto="esimerkit/09-ansat.cpp" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/09-ansat.odotettu"}
```

Huomioita:

- Poikkeuksessa `mepc` osoittaa aiheuttajaan. Jos käsittelijä ei
  kasvattaisi sitä neljällä, `mret` palaisi samaan käskyyn ja ansa
  toistuisi loputtomasti. Sivuvirheessä halutaan juuri tämä: ydin
  korjaa sivutaulun ja käsky suoritetaan uudelleen.
- Keskeytyksessä `mepc` on käsky, jota *ei vielä* suoritettu, joten siihen
  palataan sellaisenaan. Keskeytykset osuvat odotussilmukan eri
  käskyihin (`blt` tai `li`): asynkronisuus näkyy.
- Ajastimen vertailuarvo `mtimecmp` on muistiinkuvattu rekisteri, ja
  käsittelijä siirtää sitä eteenpäin. Muuten keskeytys laukeaisi heti
  uudelleen, koska ehto `mtime >= mtimecmp` on yhä tosi.
- Esimerkin käsittelijä käyttää rekistereitä t5 ja t6 tallentamatta niitä.
  Oikea käsittelijä tallentaa kaikki käyttämänsä rekisterit. Tavallinen
  keino on `csrrw sp, mscratch, sp`: vaihdetaan pinoksi käsittelijän oma
  pino, jonka osoite on `mscratch`-rekisterissä, ja tallennetaan
  rekisterit sinne.

## Etuoikeustasot ja delegointi

RISC-V:ssä on kolme tasoa: M (*machine*, laiteohjelmisto), S
(*supervisor*, käyttöjärjestelmän ydin) ja U (*user*, sovellukset).
Kaikki ansat menevät oletuksena M-tilaan, mutta `medeleg`- ja
`mideleg`-rekistereillä M-tilan ohjelmisto (esimerkiksi OpenSBI) voi
delegoida esimerkiksi sivuvirheet ja U-tilan `ecall`-kutsut suoraan
S-tilan käsittelijälle (`stvec`, `sepc`, `scause`). Järjestelmäkutsu on
siis vain poikkeus, jonka sovellus aiheuttaa tarkoituksella.

## Tarkat poikkeukset liukuhihnassa

Liukuhihnassa on samaan aikaan viisi käskyä eri vaiheissa. Jos lataus
aiheuttaa sivuvirheen MEM-vaiheessa, sitä seuraava käsky on jo EX:ssä ja
seuraavat sen takana. **Tarkka poikkeus** (*precise exception*)
tarkoittaa, että käsittelijä näkee tilan, jossa kaikki aiheuttajaa
edeltävät käskyt ovat valmiita eikä yksikään sen jälkeinen ole
muuttanut rekistereitä tai muistia.

Toteutus: poikkeus ei laukea heti, vaan se merkitään käskyn mukana
kulkevaan bittiin. Kun käsky saapuu viimeiseen vaiheeseen, jossa tila
muuttuu peruuttamattomasti (WB tai epäjärjestyksessä suorittavan ytimen
poistovaihe, luku 11), ansa otetaan ja kaikki nuoremmat käskyt
hylätään samalla mekanismilla kuin väärin ennustetun haaran jälkeen.
Ilman tarkkoja poikkeuksia sivuvirheen jälkeinen uudelleensuoritus ja
virtuaalimuisti olisivat käytännössä mahdottomia.

## Muistiinkuvattu I/O

Oheislaitteiden rekisterit näkyvät suorittimelle tavallisina
muistiosoitteina (*memory-mapped I/O*, MMIO). Esimerkin UART on
osoitteessa 0x1000'0000: talletus siihen lähettää merkin. Erillisiä
I/O-käskyjä (x86:n `in` ja `out`, *port-mapped I/O*) RISC-V:ssä ei ole.

MMIO-osoitteet poikkeavat tavallisesta muistista kolmella tavalla:

- **Ei välimuistia.** Laitteen tilarekisteri voi muuttua milloin vain, ja
  kirjoituksen on mentävä laitteelle heti. Alue merkitään välimuistin
  ohittavaksi (RISC-V:n PMA-attribuutit, x86:n MTRR ja PAT).
- **Sivuvaikutukset.** Lukeminen voi tyhjentää vastaanottopuskurin tai
  kuitata keskeytyksen. Spekulatiivista tai toistettua lukua ei saa
  tehdä.
- **Järjestys.** Laitteen ohjaus vaatii usein, että kirjoitukset
  saapuvat tietyssä järjestyksessä (ensin data, sitten
  käynnistyskomento). RISC-V:ssä `fence` erottaa muisti- ja
  I/O-operaatiot (`fence w, o`), ja C/C++-koodissa osoitin on
  `volatile`, jotta kääntäjä ei poista tai yhdistä viitteitä.

Laitteiden sijoittelu, väyläliitännät ja keskeytysohjain (PLIC, CLINT)
käydään läpi piirisuunnittelijan näkökulmasta taidossa
*SoC-integraatio*.

## Kysely, keskeytys ja DMA

Kun laite tuottaa dataa, suoritin voi hoitaa siirron kolmella tavalla:

| Tapa | Miten | Hinta |
|------|-------|-------|
| Kysely (*polling*) | luetaan tilarekisteriä silmukassa | ydin on varattu koko ajan |
| Keskeytys | laite keskeyttää, kun dataa on | 1–5 µs per keskeytys (tallennus, käsittelijä, paluu) |
| DMA | laite kirjoittaa muistiin itse, keskeyttää lopussa | yksi keskeytys per puskuri |

Esimerkkilaskelma: 10 Gbit/s verkko tuottaa 1 500 tavun kehyksiä
yli 800 000 sekunnissa. Jos jokainen kehys aiheuttaisi 2 µs:n
keskeytyksen ja kopioinnin, yksi ydin kuluisi kokonaan pelkkään
vastaanottoon. Siksi verkkokortit käyttävät **DMA:ta** (*direct memory
access*): ajuri antaa kortille kehän (*ring*) puskurikuvaajia, kortti
kirjoittaa kehykset suoraan muistiin, ja keskeytykset yhdistetään
(*interrupt coalescing*). Hyvin suurilla nopeuksilla palataan
kyselyyn: Linuxin NAPI ja DPDK kyselevät kehää silmukassa, kun liikennettä
on paljon, koska keskeytyksen hinta ylittää kyselyn hinnan.

DMA tuo esiin kaksi arkkitehtuurin kysymystä:

- **Koherenssi.** Laite kirjoittaa keskusmuistiin, mutta suorittimen
  välimuistissa voi olla vanha kopio samasta osoitteesta, ja
  takaisinkirjoittavassa välimuistissa voi olla uudempi data, jota laite
  ei näe. Palvelinsuorittimissa DMA on koherentti (laite osallistuu
  välimuistiprotokollaan, luku 10). Monissa sulautetuissa järjestelmissä
  ei ole, ja ajurin on tyhjennettävä (*clean*) välimuistin rivit ennen
  lähetystä ja mitätöitävä (*invalidate*) ne ennen vastaanotetun datan
  lukemista.
- **Suojaus.** DMA:ta käyttävä laite voi kirjoittaa mihin tahansa
  fyysiseen osoitteeseen. **IOMMU** tekee laitteiden osoitteille saman
  kuin MMU prosessien osoitteille: muuntaa ja rajaa ne. Ilman IOMMU:ta
  haitallinen laite (tai vaikka Thunderbolt-liitäntään kytketty
  tikku) voi lukea koko muistin.

## Väylät

Suoritinta, muistia ja laitteita yhdistää **väylä** tai
**yhdysverkko** (*interconnect*). Väyläsiirto koostuu osoitevaiheesta
(kuka, mihin, lukeako vai kirjoittaa) ja datavaiheesta. Suorituskykyyn
vaikuttavat:

- **Purskeet** (*burst*): välimuistin lohko siirretään yhdellä
  osoitteella ja usealla peräkkäisellä datasanalla.
- **Jaetut siirrot** (*split transactions*): väylä vapautuu osoitteen
  jälkeen, ja vastaus tulee myöhemmin. Monta siirtoa voi olla yhtä aikaa
  kesken, ja vastaukset voivat tulla eri järjestyksessä (AXI:n
  tunnisteet).
- **Topologia**: jaettu väylä (yksi siirto kerrallaan, kaikki
  kuulevat, luonteva nuuskivalle koherenssille), ristikytkin
  (*crossbar*, rinnakkaiset siirrot eri kohteisiin) ja piirin sisäinen
  verkko (*network on chip*, rengas tai verkko suurissa moniytimissä).

## Käytännössä

- **Käsittelijä lyhyeksi.** Keskeytyskäsittelijä kuittaa laitteen ja
  siirtää työn muualle (Linuxin *bottom half*, työjono, RTOS:n tehtävä).
  Pitkä käsittelijä viivästää kaikkia muita keskeytyksiä.
- **`volatile` ei ole synkronointia.** Se estää kääntäjää poistamasta
  MMIO-viitteitä, mutta ei estä laitteistoa järjestämästä niitä
  uudelleen. Käytä alustan I/O-funktioita (`readl`, `writel`) tai
  `fence`-käskyjä.
- **Mittaa keskeytysten määrä.** `/proc/interrupts` ja `perf stat -e
  irq:*` kertovat, jos keskeytykset vievät merkittävän osan ajasta.
- **Muista välimuisti DMA-puskureissa.** Ei-koherentilla alustalla
  unohtunut tyhjennys tai mitätöinti tuottaa virheen, joka näkyy vain
  joskus, riippuen siitä, mitä välimuistissa sattui olemaan.

## Itsearviointi

- Osaat erottaa poikkeuksen ja keskeytyksen ja kertoa, mihin `mepc`
  osoittaa kummassakin.
- Osaat luetella, mitä laitteisto tekee ansan sattuessa ja mitä `mret`
  palauttaa.
- Osaat kirjoittaa ajastinkeskeytyksen käsittelijän, joka siirtää
  `mtimecmp`:tä, ja selittää, miksi rekisterit on tallennettava.
- Osaat selittää tarkat poikkeukset liukuhihnassa.
- Osaat verrata kyselyä, keskeytyksiä ja DMA:ta ja kertoa, mitä
  DMA vaatii välimuistilta ja muistinsuojaukselta.

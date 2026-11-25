# Käynnistyskoodi ja linkkeriskripti

Kun piiriin kytketään virta tai sen reset-nasta vapautuu, Cortex-M
tekee laitteistolla kaksi asiaa: lukee osoitteesta `0x00000000`
pino-osoittimen alkuarvon MSP:hen ja osoitteesta `0x00000004`
ensimmäisen suoritettavan funktion osoitteen PC:hen. Muuta ei tapahdu.
Kellot käyvät oletustaajuudella, RAMin sisältö on satunnainen ja
oheislaitteet ovat pois päältä. Kaikki, mitä C-ohjelma olettaa
ympäristöltään, on käynnistyskoodin tehtävä.

Osoite 0 on vektoritaulun oletuspaikka. Rekisteri VTOR (Vector Table
Offset Register) voi siirtää taulun muualle, mitä käynnistin käyttää
siirtäessään ohjauksen sovellukselle. Monissa piireissä osoitteeseen 0
voidaan myös peilata eri muisteja käynnistysnastojen mukaan; esimerkiksi
STM32-piirin BOOT0-nasta valitsee flashin tai piirin oman ROM-käynnistimen.

## Vektoritaulu C:llä

Vektoritaulu on vakiotaulukko, joka sijoitetaan omaan osioonsa
`.vektorit`. Linkkeriskripti vie sen flashin alkuun.

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="vektorit"}
```

Ensimmäinen alkio on pinon huippu, joka ei ole funktio. Muunnos
funktio-osoittimeksi on rumaa mutta tavallista; vaihtoehto olisi
taulukko kokonaislukuja. Ulkoisten keskeytysten paikat on kirjoitettu
nimetyillä alustimilla, jolloin IRQ-numeron virhe on helppo huomata.
Taulun pituus ja järjestys tulevat piirin käyttöohjeesta: mps2-an385:ssä
on 32 ulkoista linjaa, joista esimerkit käyttävät ensimmäisiä
kuuttatoista.

Käsittelijät ovat *heikkoja aliaksia* yhteiselle oletuskäsittelijälle.
Kun ohjelma määrittelee funktion `SysTick_Handler`, linkkeri valitsee
sen; muuten taulukkoon päätyy `Oletus_Handler`. Näin vektoritaulua ei
tarvitse muokata jokaista ohjelmaa varten.

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="heikot"}
```

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="oletus"}
```

Oletuskäsittelijä on tärkeämpi kuin miltä näyttää. Jos keskeytys
sallitaan mutta sen käsittelijän nimi on kirjoitettu väärin, heikko
alias ohjaa keskeytyksen tänne. Tyhjä ikuinen silmukka olisi pahin
mahdollinen oletus: laite jähmettyy, eikä mikään kerro miksi.

## C-ajoympäristön alustus

Alla oleva kuva näyttää koko käynnistyksen nollauksesta `main`iin.
Prosessori lukee vektoritaulusta itse vain kaksi sanaa; kaikki muu on
käynnistyskoodin tehtävää.

```{.dot otsikko="Käynnistys nollauksesta mainiin"}
digraph {
  rankdir=TB; nodesep=0.4; ranksep=0.3;
  nollaus [label="nollaus", shape=plaintext, style=""];
  sp [label="laitteisto: SP := vektoritaulu[0]"];
  pc [label="laitteisto: PC := vektoritaulu[1]\n(Reset_Handler)"];
  data [label="Reset_Handler: kopioi .data\nflashista RAMiin"];
  bss [label="Reset_Handler: nollaa .bss"];
  main [label="main()", style="rounded,filled,bold"];
  loppu [label="palasi mainista:\nikuinen silmukka", style="rounded,dashed"];
  nollaus -> sp -> pc -> data -> bss -> main -> loppu;
}
```

C-standardi lupaa ohjelmalle kolme asiaa, jotka käynnistyskoodin on
toteutettava ennen `main`ia:

1. **Alustetut staattiset muuttujat** (`int x = 42;`) sisältävät
   alkuarvonsa. Ne ovat osiossa `.data`, jonka arvot tallennetaan
   flashiin, koska RAM tyhjenee virran katketessa. Käynnistyskoodi
   kopioi ne RAMiin.
2. **Alustamattomat staattiset muuttujat** ovat nollia. Ne ovat
   osiossa `.bss`, jolle ei varata flashista mitään; käynnistyskoodi
   nollaa alueen.
3. **Pino on käytettävissä.** Cortex-M:ssä tämä on jo valmiina, koska
   prosessori asettaa MSP:n vektoritaulusta.

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="reset"}
```

Rajat tulevat linkkeriskriptin symboleista. Symboli ei ole muuttuja
vaan osoite, joten se esitellään taulukkona: `_data_alku` on silloin
suoraan osoitin eikä arvo, jota pitäisi lukea.

```{.c tiedosto="esimerkit/yhteinen/kaynnistys.c" osa="symbolit"}
```

Oikean piirin käynnistyskoodissa on muutakin. Liukulukuyksikkö
(Cortex-M4F, M7, M33) on sallittava CPACR-rekisterillä ennen ensimmäistä
liukulukukäskyä, muuten käsky aiheuttaa UsageFaultin. C++-ohjelmassa
globaalien olioiden konstruktorit ajetaan kutsulla
`__libc_init_array`. CMSIS-käytännössä tämä kaikki tehdään funktiossa
`SystemInit`, jota Reset_Handler kutsuu ennen `main`ia.

Suurin puuttuva osa on kellojärjestelmä. Emuloidussa kortissa kello on
kiinteä 25 MHz, mutta oikea piiri käynnistyy sisäisellä
RC-oskillaattorilla (usein 4–16 MHz, tarkkuus prosentin luokkaa), ja
ohjelma rakentaa siitä käyttökellon itse. Tyypillinen kellopuu näyttää
tältä:

```{.dot otsikko="Tyypillinen kellopuu (periaate). Ohjelma valitsee lähteen, kertoimet ja jakajat rekistereillä; jokaisella oheislaitteella on oma kellon sallintabittinsä."}
digraph {
  rankdir=LR; nodesep=0.22; ranksep=0.4;
  node [fontsize=10];
  rc [label="sisäinen RC\n8 MHz, ±1 %"];
  kide [label="ulkoinen kide\n8 MHz, ±20 ppm"];
  lse [label="kellokide\n32,768 kHz"];
  pll [label="PLL\n× 9"];
  mux [label="valitsin", shape=trapezium, orientation=270];
  jak [label="väyläjakajat\n/1, /2"];
  cpu [label="ydin, SysTick,\nmuisti: 72 MHz", style="rounded,filled,bold"];
  per [label="oheislaitteet:\n36 tai 72 MHz", style="rounded,filled"];
  rtc [label="RTC, matalan\ntehon ajastin", style="rounded,filled"];
  rc -> mux; kide -> pll -> mux; kide -> mux [style=dashed];
  mux -> cpu; mux -> jak;
  jak -> per [label="sallinta-\nbitti"];
  lse -> rtc [minlen=3];
}
```

Kellon vaihdossa järjestys on tärkeä. Uuden lähteen on oltava
käynnissä ja vakaa ennen kuin siihen vaihdetaan (kide ja PLL
ilmoittavat valmiudestaan tilabitillä, ja käynnistyminen vie
millisekunteja). Flashin odotustilat lisätään *ennen* taajuuden
nostamista, koska flash ei ehdi vastata nopeammalle kellolle, ja
vähennetään vasta laskemisen *jälkeen*. Lopuksi päivitetään kaikki,
mikä riippuu taajuudesta: SysTickin jakso, UARTin jakaja ja
ajastimien esijakajat. Kellopuuhun palataan kahdesti: luvussa 4
oheislaitteen kello on sallittava ennen kuin sen rekistereihin voi
kirjoittaa, ja luvussa 8 lepotilat eroavat juuri siinä, mitkä puun
haarat ne pysäyttävät.

## Linkkeriskripti

Linkkeriskripti kertoo, mitä muistia piirissä on ja mihin osiot
sijoitetaan. Taito *Objektitiedostot, linkitys ja ABI* esitteli skriptin
rakenteen;
tässä keskitytään siihen, mitä mikrokontrolleri vaatii.

```{.ld tiedosto="esimerkit/yhteinen/laite.ld" osa="muisti"}
```

`MEMORY` nimeää muistialueet. Kirjaimet `rx` ja `rwx` ovat ohjeita
linkkerille: osio, jota ei ole erikseen sijoitettu, päätyy alueelle,
jonka oikeudet sopivat. `ENTRY` ei vaikuta laitteeseen, koska prosessori
käynnistyy vektoritaulusta, mutta debuggeri ja QEMU lukevat sen
ELF-tiedostosta.

```{.ld tiedosto="esimerkit/yhteinen/laite.ld" osa="osiot"}
```

Tärkeimmät kohdat:

- **`KEEP(*(.vektorit))`**. Lippu `--gc-sections` poistaa osiot, joihin
  mikään ei viittaa, eikä mikään koodi viittaa vektoritauluun. `KEEP`
  estää poiston, ja koska osio on ensimmäisenä, taulu on osoitteessa 0.
- **`> RAM AT> FLASH`**. Osiolla on kaksi osoitetta. *VMA* (virtual
  memory address) on osoite, jossa ohjelma käyttää sitä, eli RAM.
  *LMA* (load memory address) on osoite, johon sisältö tallennetaan
  ohjelmoitaessa, eli flash. `LOADADDR(.data)` antaa jälkimmäisen
  käynnistyskoodille.
- **`(NOLOAD)`**. `.bss`, `.noinit` ja pino varaavat RAMista tilaa mutta
  eivät tuota sisältöä ohjelmatiedostoon.
- **Pino omana osionaan.** Pinon koko on varattu linkkerissä, joten
  jos muuttujat ja pino eivät mahdu RAMiin, linkitys epäonnistuu
  eikä ohjelma kaadu kentällä.
- **`.noinit`**. Alue, johon käynnistyskoodi ei koske. Sen sisältö
  säilyy ohjelmallisen resetin yli, mitä käytetään esimerkiksi
  kaatumissyyn tallentamiseen seuraavaa käynnistystä varten.

## Esimerkki: käynnistyskoodi työssä

Ohjelma tulostaa alustetun ja nollatun muuttujan, muuttaa niitä ja
käynnistää laitteen uudelleen kirjoittamalla AIRCR-rekisterin
SYSRESETREQ-bitin. Laskuri `.noinit`-osiossa kertoo, monesko käynnistys
on menossa.

```{.c tiedosto="esimerkit/03-kaynnistys/main.c" osa="muuttujat"}
```

```{.c tiedosto="esimerkit/03-kaynnistys/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/03-kaynnistys.odotettu"}
```

Resetin jälkeen `alustettu` on taas 42 ja `nollattu` 0, vaikka RAMissa
oli juuri arvot 43 ja 7: käynnistyskoodi kirjoitti ne yli.
`kaynnistyksia` taas säilyi. Sama ohjelma käännettynä ilman
käynnistyskoodin silmukoita (`-DILMAN_ALUSTUSTA`):

```{.tuloste tiedosto="esimerkit/testit/03-kaynnistys-ilman.odotettu"}
```

Ensimmäisellä kerralla `alustettu` on 0, koska QEMU lataa ELF-tiedoston
segmentit niiden latausosoitteisiin (LMA) kuten ohjelmointilaite:
arvo 42 on flashissa, mutta RAMiin sitä ei kukaan kopioinut. Nolla
tulee siitä, että QEMU:n RAM on alussa nollattu; oikeassa piirissä
siinä olisi satunnaista dataa. Resetin jälkeen molemmat muuttujat
sisältävät edellisen ajon arvot. Tällainen virhe on salakavala, koska
ohjelma toimii usein ensimmäisellä käynnistyksellä ja hajoaa vasta
vahtikoiran tai ohjelmallisen resetin jälkeen.

Laskuri tunnisti ensimmäisen käynnistyksen siitä, että RAMissa ei
ollut taikalukua. Oikeassa piirissä satunnainen RAM voi sattumalta
sisältää minkä tahansa arvon, joten 32-bittisen taikaluvun lisäksi
käytetään piirin reset-syyrekisteriä, joka kertoo, oliko kyseessä
virrankytkentä, reset-nasta, vahtikoira vai ohjelmallinen reset.

## Käännöksen liput

Esimerkkien Makefilen liput, joita tavallinen ohjelma ei tarvitse:

| Lippu | Merkitys |
|-------|----------|
| `-mcpu=cortex-m3 -mthumb` | kohdeydin ja Thumb-käskyt; M4F:lle myös `-mfpu` ja `-mfloat-abi` |
| `-ffreestanding` | ei oleteta täyttä C-kirjastoa eikä `main`in erityisasemaa |
| `-ffunction-sections -fdata-sections` | jokainen funktio ja muuttuja omaan osioonsa |
| `-Wl,--gc-sections` | linkkeri poistaa osiot, joihin ei viitata |
| `-nostartfiles` | ei kirjaston omaa käynnistyskoodia (`crt0`): meillä on oma |
| `--specs=nano.specs` | pienikokoinen newlib-nano |
| `--specs=nosys.specs` | järjestelmäkutsut (`_write`, `_sbrk`) tynkinä |
| `-Wl,-Map=build/x.map` | karttatiedosto: mihin kukin symboli päätyi |

Kartta ja koko tarkistetaan työkaluilla, ja `.bin`- tai `.hex`-tiedosto
on se, mitä ohjelmointilaite kirjoittaa flashiin:

```text
arm-none-eabi-size build/03-kaynnistys.elf      # text, data, bss
arm-none-eabi-nm -n -S build/03-kaynnistys.elf  # symbolit koon kanssa
arm-none-eabi-objdump -h build/03-kaynnistys.elf  # osiot, VMA ja LMA
arm-none-eabi-objcopy -O binary build/03-kaynnistys.elf x.bin
```

`size` laskee `.data`-osion sekä flashin että RAMin kulutukseen:
flashia kuluu `text + data` ja RAMia `data + bss`.

## Käytännössä

- **Aloita valmistajan käynnistyskoodista ja linkkeriskriptistä**, mutta
  lue ne rivi riviltä. Ne ovat lyhyitä, ja niiden virheet ovat vaikeimpia
  löytää.
- **Älä luota RAMin alkuarvoon.** Kaikki, minkä pitää olla nolla, on
  `.bss`-osiossa tai alustetaan koodissa, ja `.noinit`-data tarkistetaan
  taikaluvulla ja tarkistesummalla.
- **Pidä pino omana osionaan ja mittaa sen käyttö.** Täytä pino
  käynnistyksessä tunnetulla kuviolla ja lue myöhemmin, kuinka syvälle
  kuvio on ylikirjoitettu. Pinon ylivuoto ilman MPU:ta kirjoittaa
  hiljaa muuttujien päälle.
- **Tarkista karttatiedostosta, mitä kirjasto toi mukanaan.** Yksi
  `printf` voi tuoda kymmeniä kilotavuja koodia ja liukulukumuotoilun.
- **Älä anna `main`in palata** oikeassa laitteessa. Esimerkkien
  Reset_Handler lopettaa QEMU:n; tuotannossa paluu on virhe, ja
  sen jälkeen laite käynnistetään uudelleen.

## Itsearviointi

- Osaat kertoa, mitä Cortex-M tekee resetissä laitteistolla ja mitä
  käynnistyskoodin on tehtävä ennen `main`ia.
- Osaat kirjoittaa vektoritaulun ja heikot käsittelijät C:llä ja
  selittää, miksi oletuskäsittelijä ei saa olla tyhjä silmukka.
- Osaat selittää VMA:n ja LMA:n eron ja kirjoittaa linkkeriskriptiin
  `.data`-, `.bss`- ja `.noinit`-osiot.
- Osaat tunnistaa puuttuvan `.data`-kopioinnin tai `.bss`-nollauksen
  oireista.
- Osaat perustella käännöksen liput `-ffreestanding`, `-nostartfiles` ja
  `--gc-sections` sekä `KEEP`-määreen tarpeen.

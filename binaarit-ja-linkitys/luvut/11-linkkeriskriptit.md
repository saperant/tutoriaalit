# Linkkeriskriptit ja muistikartat

Linkkeri ei päätä osioiden järjestystä ja osoitteita itse, vaan
noudattaa *linkkeriskriptiä*. Jokaisella linkityksellä on sellainen:
jos sitä ei anneta, käytetään sisäänrakennettua oletusskriptiä, jonka
`ld --verbose` tulostaa. Oletusskripti on pitkä mutta säännöllinen.
Sen alku näyttää tältä:

```text
SECTIONS
{
  PROVIDE (__executable_start = SEGMENT_START("text-segment", 0x400000));
  . = SEGMENT_START("text-segment", 0x400000) + SIZEOF_HEADERS;
  .interp         : { *(.interp) }
  .note.gnu.build-id  : { *(.note.gnu.build-id) }
  .hash           : { *(.hash) }
  ...
```

Skriptin peruskäsitteet:

| Rakenne | Merkitys |
|---------|----------|
| `.text : { *(.text .text.*) }` | tulostusosio ja syöteosiot, jotka siihen kootaan |
| `.` | sijaintilaskuri: nykyinen osoite |
| `ALIGN(n)` | seuraava `n`:llä jaollinen osoite |
| `KEEP(...)` | älä poista, vaikka `--gc-sections` olisi käytössä |
| `symboli = .;` | määrittelee symbolin nykyiseen osoitteeseen |
| `PROVIDE(s = ...)` | määrittelee, jos ohjelma ei määrittele itse |
| `/DISCARD/ : { ... }` | hylkää syöteosiot |
| `ENTRY(_start)` | aloitusosoite ELF-otsakkeeseen |
| `MEMORY { ... }` | muistialueet ja niiden koot (sulautetut) |
| `INSERT AFTER .rodata` | lisää skriptin oletusskriptiin |

Tässä luvussa on kolme tapaa käyttää linkkeriä: oma osio ilman
skriptiä, lisäys oletusskriptiin ja kokonainen oma skripti.

## Oma osio ilman skriptiä: rekisteri

Komentorivityökalussa on alikomentoja, joista jokainen on omassa
tiedostossaan. Tavallisesti pääohjelmassa olisi taulukko, johon
jokainen uusi komento lisätään käsin. Linkkeri voi koota taulukon:
jokainen tiedosto sijoittaa komennon kuvaajan samannimiseen osioon,
ja linkkeri yhdistää samannimiset osiot peräkkäin.

```{.c tiedosto="esimerkit/11-osiorekisteri/komento.h" osa="makro"}
```

```{.c tiedosto="esimerkit/11-osiorekisteri/versio.c"}
```

GNU-linkkeri määrittelee automaattisesti symbolit `__start_NIMI` ja
`__stop_NIMI` jokaiselle osiolle, jonka nimi on kelvollinen
C-tunniste. Ne ovat osion alku ja loppu, joten pääohjelma käy
taulukon läpi tuntematta sen sisältöä:

```{.c tiedosto="esimerkit/11-osiorekisteri/main.c" osa="rajat"}
```

```{.bash tiedosto="esimerkit/11-osiorekisteri/aja.sh" osa="rakennus"}
```

Linkkerikartta kertoo, mistä objektitiedostoista osio koottiin:

```{.bash tiedosto="esimerkit/11-osiorekisteri/aja.sh" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/11-osiorekisteri/odotettu"}
```

Osion koko `0x20` on kaksi 16-tavuista kuvaajaa. Sama malli on
Linuxin ytimen alustusfunktioissa (`__initcall`), testikehyksissä,
jotka keräävät testit ilman rekisteröintikoodia, ja C++:n staattisten
olioiden alustuksessa (`.init_array`, luku 12). Mallilla on kaksi
ehtoa: attribuutti `used` estää kääntäjää poistamasta muuttujaa,
johon mikään ei viittaa, ja jos tiedostot ovat staattisessa
arkistossa, ne on linkitettävä `--whole-archive`-valitsimella (luku 6).

## Lisäys oletusskriptiin

Anturilaitteen kalibrointitaulu halutaan omaan osioonsa, joka on
sivun rajalla. Silloin taulun voi korvata valmiissa ohjelmatiedostossa
(`objcopy --update-section`) tai laitteen muistissa tunnetusta
kohdasta ilman uudelleenkäännöstä. Kokonaista linkkeriskriptiä ei
tarvita: `INSERT AFTER` liittää lyhyen skriptin oletusskriptin
sisään.

```{.text tiedosto="esimerkit/11-linkkeriskripti/kalibrointi.ld" osa="insert"}
```

```{.c tiedosto="esimerkit/11-linkkeriskripti/anturi.c" osa="taulu"}
```

```{.c tiedosto="esimerkit/11-linkkeriskripti/anturi.c" osa="kaytto"}
```

```{.bash tiedosto="esimerkit/11-linkkeriskripti/aja.sh" osa="anturi"}
```

Skriptin määrittelemät symbolit ovat *osoitteita*, eivät muuttujia.
C:ssä ne esitellään taulukkoina (`extern const char
__kalibrointi_alku[];`), ja niiden arvo on taulukon osoite.
Kirjoitusasu `extern int alku;` ja `&alku` toimii myös, mutta
taulukkomuoto estää lukemasta symbolin kohdalta muistia vahingossa.

Skriptin vakio `KALIBROINTI_VERSIO = 3` on *absoluuttinen symboli*
(`nm`:ssä `A`): sen arvo on 3 riippumatta latausosoitteesta. Sen
lukeminen C:stä osoitteena toimii kiinteään osoitteeseen linkitetyssä
ohjelmassa, mutta PIE-ohjelmassa `rip`-suhteellinen viittaus lisää
siihen latausosoitteen. Tällaiset vakiot kuuluvat sulautettuihin
järjestelmiin, joissa ohjelma on kiinteässä osoitteessa; PIE-ohjelmassa
vakio välitetään tavallisena muuttujana tai makrona.

## Kokonainen oma skripti

Kun ohjelma ajetaan ilman käyttöjärjestelmän lataajaa, kuten
mikro-ohjaimessa, käynnistyslataimessa tai ytimessä, muistikartta
määrätään itse. Linuxissa sama onnistuu ohjelmalla, joka ei käytä
C-kirjastoa:

```{.c tiedosto="esimerkit/11-linkkeriskripti/irrallinen.c" osa="irrallinen"}
```

```{.text tiedosto="esimerkit/11-linkkeriskripti/irrallinen.ld" osa="oma"}
```

```{.bash tiedosto="esimerkit/11-linkkeriskripti/aja.sh" osa="irrallinen"}
```

```{.tuloste tiedosto="esimerkit/11-linkkeriskripti/odotettu"}
```

Skripti sijoittaa koodin osoitteeseen `0x400000`, ja `ENTRY(_start)`
kirjoittaa sen aloitusosoitteeksi. Valitsimet pitävät ohjelman
yksinkertaisena: `-nostdlib` jättää pois C-kirjaston ja
käynnistyskoodin, `-static` ja `-no-pie` tuottavat kiinteään
osoitteeseen linkitetyn ohjelman ilman lataajaa, ja
`-fno-stack-protector` poistaa viittaukset pinon suojauksen
tarkistuksiin, jotka ovat C-kirjastossa. `/DISCARD/` poistaa
kääntäjän merkinnät ja poikkeustaulut, joita ohjelma ei tarvitse;
koontitunniste (`--build-id=none`) poistetaan samasta syystä.

Mikro-ohjaimen skriptissä on lisäksi muistialueet. Alustetun datan
alkuarvot ovat flash-muistissa, mutta muuttujat RAM-muistissa, joten
osiolla on kaksi osoitetta: latausosoite (LMA) ja suoritusosoite
(VMA). Käynnistyskoodi kopioi datan ja nollaa `.bss`:n skriptin
symbolien avulla:

```text
MEMORY {
  FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 256K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}
SECTIONS {
  .text : { KEEP(*(.vektorit)) *(.text*) *(.rodata*) } > FLASH
  .data : { _data_alku = .; *(.data*) _data_loppu = .; } > RAM AT > FLASH
  _data_lahde = LOADADDR(.data);
  .bss  : { _bss_alku = .; *(.bss*) *(COMMON) _bss_loppu = .; } > RAM
}
```

```{.dot otsikko="Alustetulla datalla on kaksi osoitetta: alkuarvot ladataan flash-muistiin (LMA), mutta ohjelma käyttää muuttujia RAM-muistista (VMA). Käynnistyskoodi kopioi ne."}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=1.1;
  node [shape=plaintext, style=""];
  flash [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>FLASH</b> 0x08000000</td></tr>
    <tr><td bgcolor="#E4DCF0" width="150">.vektorit</td></tr>
    <tr><td bgcolor="#E4DCF0">.text</td></tr>
    <tr><td bgcolor="#EEF1F2">.rodata</td></tr>
    <tr><td bgcolor="#F1E3CC" port="d">.data:n alkuarvot<br/>_data_lahde</td></tr>
  </table>>];
  ram [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"><b>RAM</b> 0x20000000</td></tr>
    <tr><td bgcolor="#F1E3CC" width="150" port="d">.data<br/>_data_alku … _data_loppu</td></tr>
    <tr><td port="b">.bss<br/>_bss_alku … _bss_loppu</td></tr>
    <tr><td border="0"> </td></tr>
  </table>>];
  flash:d -> ram:d [label="käynnistyskoodi\nkopioi"];
  nolla [label="käynnistyskoodi\nnollaa", fontsize=10];
  nolla -> ram:b;
}
```

Tämä on taidon *Mikrokontrollerit ja bare-metal-ohjelmointi* aihe;
tässä riittää tunnistaa rakenne. Linkkeri tarkistaa alueiden koot ja ilmoittaa
`region 'RAM' overflowed by 312 bytes`, kun ohjelma ei mahdu.

## Linkkerikartta

Valitsin `-Wl,-Map=ohjelma.map` kirjoittaa linkityksen pöytäkirjan:

- arkistoista otetut jäsenet ja syyt (luku 6),
- hylätyt osiot (`Discarded input sections`), kun käytössä on
  `--gc-sections`,
- muistialueet ja niiden käyttö,
- jokaisen tulostusosion osoite ja koko sekä sen syöteosiot
  tiedostoittain ja symboleittain.

Kartta on tärkein työkalu, kun ohjelma on liian suuri tai muuttuja on
väärässä paikassa. `--print-memory-usage` tulostaa muistialueiden
käyttöasteen linkityksen lopuksi, mikä sopii sulautettujen
rakennusten tarkistukseksi.

## Käytännössä

- **Aloita ilman skriptiä.** Oma osio ja automaattiset
  `__start_`/`__stop_`-symbolit riittävät rekistereihin. `INSERT`
  riittää yksittäisen osion sijoittamiseen. Kokonainen skripti on
  tarpeen vain, kun muistikartta on itse määrättävä.
- **Lähde oletusskriptistä.** `ld --verbose` antaa toimivan pohjan,
  jota on helpompi muokata kuin kirjoittaa alusta.
- **Merkitse tarpeelliset osiot `KEEP`:llä.** Vektoritaulu ja
  rekisteriosiot, joihin mikään ei viittaa, poistuvat muuten
  `--gc-sections`-valitsimen vuoksi.
- **Lue kartta jokaisen skriptimuutoksen jälkeen.** Linkkeri ei
  varoita, jos syöteosio päätyy oletuspaikkaan, koska skriptin malli
  ei vastannut sen nimeä.

## Itsearviointi

- Osaat lukea linkkeriskriptin perusrakenteet: tulostusosiot,
  syöteosiot, sijaintilaskurin ja symbolimäärittelyt.
- Osaat koota taulukon eri tiedostoista omalla osiolla ja
  `__start_`/`__stop_`-symboleilla.
- Osaat käyttää skriptin symboleita C:stä osoitteina ja kertoa,
  miksi absoluuttiset vakiot eivät sovi PIE-ohjelmaan.
- Osaat lisätä osion oletusskriptiin `INSERT`-komennolla ja
  kirjoittaa yksinkertaisen kokonaisen skriptin.
- Osaat etsiä linkkerikartasta osion sijainnin, koon ja syötteet.

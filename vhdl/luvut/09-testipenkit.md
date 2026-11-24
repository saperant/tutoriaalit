# Testipenkit

Testipenkki on VHDL-ohjelma, joka ajaa testattavaa lohkoa ja
tarkistaa sen toiminnan. Testipenkissä saa käyttää koko kieltä:
viiveitä, tiedostoja, liukulukuja, dynaamista muistia ja suojattuja
tyyppejä. Tämä luku kokoaa itsetarkistavan testipenkin rakenteen ja
VHDL-2008:n työkalut. Verifioinnin menetelmät yleisesti, kuten
kattavuus, rajoitettu satunnaistus ja formaali verifiointi,
käsitellään taidossa *Laitteiston verifiointi*.

## Rakenne

Hyvä testipenkki jakautuu osiin, joilla on kullakin yksi tehtävä:

| Osa | Tehtävä |
|-----|---------|
| kello ja nollaus | rinnakkainen kellolause, nollausjakso alussa |
| herätteet | syöttää tulot, usein proseduurien avulla |
| malli | laskee odotetun tuloksen riippumattomasti |
| tarkistin | vertaa lähtöä malliin, raportoi poikkeamat |
| valvoja | lopettaa simuloinnin: valmis, virhe tai aikakatkaisu |

Herätteet ja tarkistus ovat eri prosesseissa, kun lohkolla on viive
tai virtauksenohjaus: herätteiden ei tarvitse tietää, milloin
vastaava tulos tulee ulos. Odotetut tulokset kulkevat niiden välillä
jonossa.

```{.dot otsikko="Testipenkin osat ja tiedon kulku"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.45;
  kello [label="kello ja\nnollaus"];
  herate [label="herätteet"];
  dut [label="testattava\nlohko", penwidth=2];
  malli [label="malli"];
  jono [label="jono", shape=box, style="filled"];
  tarkistin [label="tarkistin"];
  valvoja [label="valvoja"];
  kello -> dut; herate -> dut [label="tulot"];
  herate -> malli [label="samat tulot"];
  malli -> jono [label="odotetut"];
  dut -> tarkistin [label="lähdöt"];
  jono -> tarkistin;
  tarkistin -> valvoja [label="virheet"];
  herate -> valvoja [label="valmis", style=dashed];
}
```

## Esimerkki: liukuva keskiarvo

Testattava lohko laskee neljän viimeisen näytteen keskiarvon.
Juokseva summa päivitetään lisäämällä uusi näyte ja vähentämällä
vanhin, ja jako neljällä on aritmeettinen siirto:

```{.vhdl tiedosto="esimerkit/09-keskiarvo/keskiarvo.vhd" osa="dut"}
```

Testipenkin jaettu tila on jono. Kaksi prosessia ei voi käyttää samaa
tavallista muuttujaa, joten jono on *suojattu tyyppi* (`protected`):
olio, jonka metodit simulaattori suorittaa yksi kerrallaan.

```{.vhdl tiedosto="esimerkit/09-keskiarvo/jono.vhd" osa="jono"}
```

Testipenkin alku esittelee signaalit ja jonon jaettuna muuttujana:

```{.vhdl tiedosto="esimerkit/09-keskiarvo/testipenkki.vhd" osa="alku"}
```

Herätteet ovat satunnaisia: näytteet kattavat koko arvoalueen, ja
syötteeseen tulee satunnaisia taukoja, jotta myös `sisaan_kelpo`n
alas meno tulee testattua. `uniform` antaa tasajakautuneen luvun
välillä 0–1. Kiinteä siemen tekee ajosta toistettavan: virhe löytyy
uudelleen samalla siemenellä.

```{.vhdl tiedosto="esimerkit/09-keskiarvo/testipenkki.vhd" osa="heratteet"}
```

Malli laskee keskiarvon kokonaisluvuilla eikä toista laitteiston
rakennetta (juokseva summa ja siirto). Mallissa on yksi tärkeä
yksityiskohta: VHDL:n kokonaislukujako `/` pyöristää kohti nollaa, mutta
aritmeettinen siirto pyöristää alaspäin. Jos malli käyttäisi jakoa
`/ 4`, tarkistus pysähtyisi kahdeksanteen näytteeseen ilmoitukseen
*saatiin −140, odotettiin −139*. Kumpi on oikein, on määrittelykysymys;
testipenkki pakottaa tekemään päätöksen.

Tarkistin ja valvoja:

```{.vhdl tiedosto="esimerkit/09-keskiarvo/testipenkki.vhd" osa="tarkistin"}
```

```{.tuloste tiedosto="esimerkit/09-keskiarvo.odotettu"}
```

Tarkistin ottaa jonosta odotetun arvon aina, kun lohko ilmoittaa
tuloksen, joten järjestys ja määrä tulevat tarkistetuiksi. Valvoja
odottaa, kunnes kaikki näytteet on tarkistettu, ja varmistaa lopuksi,
ettei jonoon jäänyt odotettuja arvoja, eli ettei lohko jättänyt
tuloksia antamatta. `finish` lopettaa simuloinnin; GHDL tulostaa
lopetushetken.

## Jaettu muuttuja

VHDL-93 salli jaetut muuttujat ilman suojausta, jolloin kahden
prosessin samanaikainen päivitys oli määrittelemätöntä. VHDL-2002:sta
alkaen jaetun muuttujan on oltava suojattua tyyppiä:

```{.vhdl tiedosto="esimerkit/09-jaettu.ei-kaanny.vhd" osa="laskuri"}
```

GHDL hylkää `@virhe`-rivin ilmoituksella `type of a shared variable
must be a protected type`. Suojatulla laskurilla molemmat tarkistimet
kirjaavat virheensä:

```{.tuloste tiedosto="esimerkit/09-jaettu.odotettu"}
```

## Aikakatkaisut

Kun testipenkki odottaa lohkon vastausta, odotukselle annetaan aina
aikaraja. Muuten väärin kytketty tai jumiutunut lohko pitää simuloinnin
käynnissä ikuisesti, koska kello tuottaa tapahtumia loputtomasti. CI-
ajossa tämä näkyy vasta palvelimen aikarajana ilman tietoa syystä.
VHDL:n `wait until ehto for aika` päättyy kumpaan tahansa:

```{.vhdl tiedosto="esimerkit/09-aikakatkaisu.kaatuu.vhd" osa="odotus"}
```

Esimerkin testipenkki unohtaa nostaa kertojan sallinnan, joten
`valmis` ei nouse koskaan:

```{.tuloste tiedosto="esimerkit/09-aikakatkaisu.virhe"}
```

Ilmoitus kertoo suoraan, mitä odotettiin ja kuinka kauan. Koko
simuloinnille kannattaa lisäksi asettaa yläraja valvojaprosessilla tai
simulaattorin valitsimella (`ghdl -r ... --stop-time=1ms`).

## Raportointi ja lopetus

| Rakenne | Käyttö |
|---------|--------|
| `assert ehto report "..." severity failure;` | tarkistus; `failure` pysäyttää simuloinnin |
| `report "..." severity note;` | lokiviesti; tasot `note`, `warning`, `error`, `failure` |
| `std.env.finish` | lopettaa simuloinnin onnistuneena |
| `std.env.stop` | pysäyttää simuloinnin (interaktiivisessa simulaattorissa jatkettavissa) |
| `write(rivi, ...)`, `writeline(output, rivi)` | muotoiltu tuloste ilman lokietuliitettä |

`report` lisää viestiin tiedoston, rivin ja simulointiajan, mikä
sopii virheisiin. Tulosteisiin, joita verrataan tiedostoon, käytetään
`textio`-paketin rivejä, kuten tämän tutoriaalin esimerkeissä.
Oletuksena `error`-tason väittämä ei pysäytä simulointia; GHDL:ssä
rajaa voi muuttaa valitsimella `--assert-level=error`.

Simulaation alussa signaalit ovat `'U'`, ja `numeric_std`:n vertailut ja
`to_integer` antavat siitä varoituksia (`metavalue detected`). Ne
vältetään alustamalla testipenkin signaalit, ja hetken 0 varoitukset
voi ohittaa GHDL:n valitsimella `--ieee-asserts=disable-at-0`.
Varoituksia ei pidä vaientaa kokonaan, koska myöhemmin simuloinnissa
ne paljastavat alustamattomia rekistereitä.

## Aaltomuodot ja tiedostot

Kun tarkistus pysähtyy, syy etsitään aaltomuodoista:

```text
ghdl -r --std=08 testipenkki --wave=aallot.ghw   # GTKWave, Surfer
ghdl -r --std=08 testipenkki --vcd=aallot.vcd    # yleinen VCD-muoto
```

VCD on tekstimuotoinen, joten sitä voi käsitellä myös ohjelmallisesti.
Tämän kirjan ajoituskaaviot on tuotettu juuri näin: esimerkkien
`Makefile` ajaa testipenkin `--vcd`-valitsimella ja muuntaa valitut
signaalit kaavioksi. Kun koodi muuttuu, kaavion tarkistus huomaa
eron, joten kuva ja koodi eivät pääse erkaantumaan.

Paketin `std.textio` proseduurit `readline` ja `read` lukevat
syötevektoreita ja odotettuja tuloksia tiedostosta. Näin malli voi olla
Pythonilla tai MATLABilla tuotettu tiedosto, mikä on tavallista DSP-
lohkoissa. Tiedoston nimi annetaan generic-parametrina, jolloin
testiajo voi vaihtaa sen.

## Testikehykset

Isommissa projekteissa testipenkkien yhteinen rakenne otetaan
valmiista avoimesta kirjastosta:

| Kehys | Tarjoaa |
|-------|---------|
| VUnit | testien löytö ja ajo Python-skriptillä, rinnakkaisajo, CI-raportit, tarkistuskirjasto |
| OSVVM | tulostaulut, väyläkomponentit, rajoitettu satunnaistus, toiminnallinen kattavuus |
| UVVM | väyläkomponentit (UART, SPI, AXI...), lokitus, toiminnallinen kattavuus |
| cocotb | testipenkki Pythonilla; simulaattori ajaa VHDL:n |

VUnitin ja OSVVM:n voi yhdistää: VUnit ajaa testit ja OSVVM tarjoaa
verifiointikomponentit. Kehyksen valinta on tiimin päätös, mutta
jokin niistä kannattaa valita ennen kuin omista apuproseduureista tulee
huonompi kopio.

## Käytännössä

- **Itsetarkistava aina.** Testipenkki tietää odotetun tuloksen, eikä
  lopputulos riipu siitä, katsooko joku aaltomuotoja. Paluuarvo
  kertoo CI:lle, menikö testi läpi.
- **Malli eri tavalla kuin toteutus.** Mallin kirjoittaa toisella
  algoritmilla, toisella kielellä tai taulukosta. Sama virhe kahdesti
  kirjoitettuna menee aina läpi.
- **Satunnaisuus kiinteällä siemenellä.** Satunnaiset herätteet
  löytävät rajatapauksia, joita kukaan ei ajatellut. Siemen tulostetaan
  tai kiinnitetään, jotta virhe toistuu.
- **Aikaraja jokaiselle odotukselle.** `wait until ... for ...`
  tai valvojaprosessi; ei koskaan ehdotonta odotusta lohkon
  vastaukselle.
- **Tarkista loppu.** Testin lopussa jonojen on oltava tyhjiä ja
  odotettujen tapahtumien määrän oikea. Muuten puuttuva tulos jää
  huomaamatta.
- **Testaa virhetilanteet.** Tauot, ylivuodot, rikotut kehykset ja
  nollaus kesken toiminnan kuuluvat jokaiseen testipenkkiin.

## Itsearviointi

- Osaat jakaa testipenkin kelloon, herätteisiin, malliin,
  tarkistimeen ja valvojaan ja kertoa, miksi herätteet ja tarkistus
  ovat eri prosesseissa.
- Osaat jakaa tilaa prosessien välillä suojatulla tyypillä.
- Osaat tuottaa toistettavia satunnaisia herätteitä `uniform`-
  proseduurilla.
- Osaat estää testipenkin jumiutumisen aikarajoilla ja lopettaa
  simuloinnin `std.env.finish`-proseduurilla.

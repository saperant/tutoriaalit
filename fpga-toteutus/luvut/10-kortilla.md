# Testaus kortilla

Kortilla ajo on viimeinen vaihe, ei ensimmäinen. Kortilla näkyy vain
se, mitä nastoissa tapahtuu, ja jokainen muutos vaatii synteesin,
sijoittelun ja latauksen. Simulaatiossa näkyy jokainen signaali, ja
testi toistuu sekunneissa. Siksi tämän tutoriaalin esimerkit on
testattu simulaatiossa ja raporteilla; tämä luku kertoo, miten
suunnitelma viedään kortille ja mitä tehdään, kun se ei toimi siellä.

Kortilla ajoa ei testata automaattisesti tämän tutoriaalin vuossa,
joten luvun komennot ovat tekstiä. Virheenjäljitysydin, jota luku
käyttää, on kuitenkin simuloitu ja syntetisoitu kuten muutkin
esimerkit.

## Lataus

iCEBreakerissa on FTDI-silta, joka näkyy tietokoneelle USB-laitteena:
sen kautta ladataan bittivirta ja kulkee sarjaliikenne. Bittivirta
kirjoitetaan joko SPI-flashiin, josta piiri lukee sen jokaisessa
käynnistyksessä, tai suoraan piirin konfiguraatiomuistiin:

```text
iceprog rakennus/vilkku.bin      # flashiin, säilyy virrattomana
iceprog -S rakennus/vilkku.bin   # suoraan piiriin, katoaa virran mukana
```

Linuxissa käyttäjällä on oltava oikeus USB-laitteeseen (udev-sääntö),
ja kehityskontista laite on erikseen jaettava konttiin. Lataus kestää
muutaman sekunnin.

## Käyttöönoton järjestys

Uutta korttia tai uutta suunnitelmaa ei kannata kokeilla kerralla.
Käyttöönotto edetään vaiheittain niin, että jokainen vaihe todistaa
yhden asian:

1. **Vilkku** (luku 1). Todistaa, että bittivirta latautuu, kello
   käy ja nastat ovat oikein. Jos ledi ei vilku, vika on
   työkaluketjussa, rajoitetiedostossa tai kortissa, ei
   suunnitelmassa.
2. **Silmukka sarjaportissa.** Vastaanotettu tavu lähetetään
   takaisin. Todistaa UARTin, baudinopeuden ja tietokoneen asetukset.
3. **Virheenjäljitysydin.** Rekisterien luku ja kirjoitus
   sarjaportista. Tämän jälkeen suunnitelman sisäistä tilaa voi
   tarkkailla ja ohjata.
4. **Oma suunnitelma** ytimen rinnalla.

## Virheenjäljitysydin

Kortilla tärkein työkalu on keino nähdä suunnitelman sisälle. Pieni
ydin, joka lukee ja kirjoittaa rekistereitä sarjaportin kautta, riittää
pitkälle:

```{.systemverilog tiedosto="esimerkit/10-uart-debug/debug_ylin.sv" osa="debug"}
```

Ydin käyttää UART-vastaanotinta ja -lähetintä. Vastaanotin tahdistaa
linjan kahdella kiikulla (linja on asynkroninen tulo, luku 8), odottaa
aloitusbitin reunaa ja näytteistää bitit bittiajan keskeltä:

```{.systemverilog tiedosto="esimerkit/10-uart-debug/uart_rx.sv"}
```

Lähetin siirtää kehyksen ulos bitti kerrallaan. Ajastin laskee
bittiajan kellojaksoja, ja kehys siirtyy vain, kun ajastin on nollassa:
tämä on luvussa 7 kuvattu sallinta johdetun kellon sijaan.

```{.systemverilog tiedosto="esimerkit/10-uart-debug/uart_tx.sv"}
```

Komentojen tulkinta on pieni tilakone. Komento `L` ja osoite
palauttavat rekisterin arvon, komento `K`, osoite ja arvo kirjoittavat
rekisterin ja palauttavat kuittauksen `K`:

```{.systemverilog tiedosto="esimerkit/10-uart-debug/debug_ylin.sv" osa="tilakone"}
```

Rekisteri 5 on vakio `0x42`. Se on ensimmäinen asia, joka kortilta
luetaan: jos vastaus on oikea, sarjaportti, baudinopeus ja bittivirta
ovat kunnossa. Rekisteri 4 on vapaasti käyvä laskuri: kaksi peräkkäistä
lukua eroavat, mikä todistaa, että kello käy.

## Ydin simulaatiossa

Testipenkki toimii isäntänä samalla protokollalla, jota tietokone
käyttäisi kortin kanssa. Simulaation nopeuttamiseksi bittiaika on
kahdeksan kellojaksoa:

```{.systemverilog tiedosto="esimerkit/10-uart-debug/testipenkki.sv"}
```

```{.tuloste tiedosto="esimerkit/10-uart-debug.odotettu"}
```

Kortilla parametrina on 104 kellojaksoa bittiä kohden: 12 MHz /
115 200 baudia ≈ 104,2, eli virhe on 0,2 %, selvästi UARTin sietämän
muutaman prosentin sisällä. Synteesi ja sijoittelu ajetaan tällä
arvolla:

```{.tuloste tiedosto="esimerkit/raportit/debug.odotettu"}
```

Ydin vie noin 180 logiikkasolua, alle 4 % piiristä, joten se mahtuu
lähes minkä tahansa suunnitelman rinnalle.

Tietokoneella sarjaporttia voi käyttää millä tahansa ohjelmalla, joka
lähettää ja vastaanottaa tavuja (esimerkiksi Pythonin pyserial-kirjasto
tai `picocom`). Vaihto näyttää tältä:

```text
isäntä -> kortti   4c 05          'L', osoite 5
kortti -> isäntä   42             tunniste
isäntä -> kortti   4b 00 01       'K', osoite 0, arvo 1 (ledi päälle)
kortti -> isäntä   4b             kuittaus 'K'
```

## Sisäinen logiikka-analysaattori

Rekisterien lukeminen näyttää tilan yhdellä hetkellä. Kun on nähtävä,
mitä signaaleille tapahtuu jaksosta toiseen, käytetään **sisäistä
logiikka-analysaattoria** (integrated logic analyzer, ILA). Se on
suunnitelmaan lisättävä lohko, joka

1. tallentaa valitut signaalit joka jaksolla lohko-RAMissa olevaan
   rengaspuskuriin,
2. pysäyttää tallennuksen, kun **liipaisuehto** täyttyy (esimerkiksi
   virhelippu nousee), ja
3. lähettää puskurin tietokoneelle, joka näyttää sen aaltomuotona.

Valmistajilla on omat ILA-työkalunsa (AMD:n ILA, Intelin SignalTap),
ja avoimista vuoista esimerkiksi LiteX-kehyksessä on LiteScope.
Rakenteen voi tehdä myös itse virheenjäljitysytimen päälle: puskuri
lohko-RAMiin, liipaisu vertailijalla ja luku sarjaportin kautta.

ILA ei ole ilmainen: se vie lohko-RAMia ja logiikkaa, ja tarkkailtavat
signaalit on reititettävä siihen. Sijoittelu muuttuu, ja ajoitukseltaan
rajalla oleva suunnitelma voi alkaa toimia tai lakata toimimasta, kun
ILA lisätään. Siksi ILA on viimeinen keino, ei ensimmäinen.

## Kun kortti ei toimi

Useimmat kortilla näkyvät viat eivät ole logiikkavikoja, koska logiikka
on simuloitu. Ne ovat vikoja simuloinnin ulkopuolella:

| Oire | Tyypillinen syy | Tarkistus |
|------|-----------------|-----------|
| Mikään ei toimi | väärä nasta, puuttuva rajoite, väärä kotelo | PCF kortin kytkentäkaaviota vasten |
| Toimii joskus, ei aina | ajoitusvirhe, tahdistamaton tulo | nextpnr:n raportti: `PASS`? ylitykset luettelossa? |
| Toimii vain ensimmäisellä kerralla | nollaus puuttuu, alkuarvo vain bittivirrassa | nollaus PLL:n lukitukselle ja painikkeelle |
| Sarjaliikenne sekaisin | väärä baudinopeus, kellotaajuus väärin | tunnisterekisterin luku, PLL:n parametrit |
| Painike tuottaa monta painallusta | kosketinvärähtely | tahdistus ja suodatus: tila hyväksytään, kun se on pysynyt millisekunteja |
| Eri käytös kuin simulaatiossa | `ifdef SYNTHESIS`, `initial`-lohkot, X-arvot | synteesin varoitukset, porttitason simulaatio |

Viimeinen rivi on harvinainen mutta hankala. Kun simulaatio ja kortti
eroavat, syntetisoitu netlista voidaan simuloida: Yosys kirjoittaa sen
Verilogiksi (`write_verilog`), ja sama testipenkki ajetaan sitä vasten.
Ero RTL- ja porttitason simulaation välillä paljastaa
synteesikelvottoman kuvauksen.

## Käytännössä

- **Simulaatio ensin, aina.** Jokainen kortilla löytynyt logiikkavika
  on testi, joka puuttui simulaatiosta. Lisää se testipenkkiin ennen
  korjausta.
- **Käyttöönotto vaiheittain.** Vilkku, silmukka, virheenjäljitysydin
  ja vasta sitten oma suunnitelma.
- **Virheenjäljitys suunnitelman osaksi.** Tunnisterekisteri,
  versionumero ja tilarekisterit maksavat vähän ja säästävät päiviä.
- **ILA viimeisenä.** Se muuttaa sijoittelua ja ajoitusta; ensin
  raportit, rekisterit ja simulaatio.

## Itsearviointi

- Osaat ladata bittivirran flashiin ja suoraan piiriin ja kertoa
  niiden eron.
- Osaat suunnitella käyttöönoton järjestyksen, jossa jokainen vaihe
  todistaa yhden asian.
- Osaat lisätä suunnitelmaan UART-virheenjäljitysytimen ja testata
  sen simulaatiossa isännän protokollalla.
- Osaat kertoa, mitä sisäinen logiikka-analysaattori tekee ja mitä se
  maksaa.
- Osaat jäljittää kortilla näkyvän vian todennäköisiin syihin
  simuloinnin ulkopuolelta.

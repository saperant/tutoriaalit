# Muistit ja FIFOt

Muisti on suunnitelman kallein ja tärkein resurssi. Kiikuista
rakennettu muisti vie paljon pinta-alaa, joten suuret muistit
toteutetaan erillisinä muistilohkoina: FPGA:ssa lohkomuistina (block
RAM) ja ASIC:ssa muistigeneraattorin tuottamana makrona. RTL-
suunnittelijan tehtävä on kirjoittaa muisti niin, että synteesi
tunnistaa sen, ja rakentaa sen ympärille oikeat rajapinnat: FIFOt ja
rekisteripankit.

## RAM-päättely

Muisti kirjoitetaan pakkaamattomana taulukkona. Synteesityökalu
*päättelee* (infer) muistilohkon, kun koodi vastaa jotakin tunnettua
kuviota. Tärkein ehto on, että luku on rekisteröity: lohkomuistin
lukudata tulee aina kellon reunan jälkeen.

```{.systemverilog tiedosto="esimerkit/08-ram.sv" osa="ram"}
```

Muistia ei nollata: lohkomuistia ei voi tyhjentää yhdellä jaksolla.
Kun samaan osoitteeseen kirjoitetaan ja luetaan samalla reunalla,
tämä koodi palauttaa vanhan arvon (read-first). Uuden arvon
palauttava muoto (write-first) kirjoitetaan eri tavalla, ja synteesi
tukee molempia. Ratkaisevaa on, että simulaatio ja kohdepiiri
käyttäytyvät samoin.

ROM on muisti, jonka sisältö annetaan alustuksessa. Sisältö voidaan
laskea funktiolla käännösaikana tai lukea tiedostosta `$readmemh`-
kutsulla. Molemmat ovat synteesikelpoisia FPGA:ssa, koska alkuarvo
tallentuu konfiguraatioon.

```{.systemverilog tiedosto="esimerkit/08-ram.sv" osa="rom"}
```

```{.tuloste tiedosto="esimerkit/08-ram.odotettu"}
```

## Synkroninen FIFO

FIFO (first in, first out) on jono kahden lohkon välissä. Se tasaa
nopeuseroja ja purskeita. Synkronisessa FIFOssa kirjoitus ja luku
käyttävät samaa kelloa. Toteutus on rengaspuskuri: muisti ja kaksi
osoitinta.

Jos osoittimet ovat yhtä leveitä kuin muistin osoite, täysi ja tyhjä
jono näyttävät samalta: osoittimet ovat yhtä suuret. Ratkaisu on yksi
ylimääräinen bitti. Kun osoittimet ovat kokonaan samat, jono on tyhjä.
Kun vain ylin bitti eroaa, kirjoitusosoitin on kierroksen edellä ja
jono on täynnä.

```{.systemverilog tiedosto="esimerkit/08-fifo/fifo.sv"}
```

Tämä FIFO on *first-word fall-through* -tyyppinen: jonon ensimmäinen
sana näkyy ulostulossa jo ennen lukua, ja `lue` kuittaa sen. Luku on
kombinatorinen, joten synteesi käyttää hajautettua muistia tai
kiikkuja. Suuri FIFO tehdään rekisteröidyllä luvulla, jolloin luettu
sana tulee jakson viiveellä tai ulostuloon lisätään yhden sanan
etupuskuri.

Testipenkki käyttää SystemVerilogin jonoa (`logic [7:0] malli[$]`)
viitemallina ja vaihtelee tuottajan ja kuluttajan nopeutta, jotta
sekä täysi että tyhjä jono tulevat testatuiksi. Liput tarkistetaan joka
jaksolla mallia vasten:

```{.systemverilog tiedosto="esimerkit/08-fifo/testipenkki.sv" osa="malli"}
```

```{.tuloste tiedosto="esimerkit/08-fifo.odotettu"}
```

Tämä testipenkki on ensimmäinen, joka mittaa testin laatua:
yhteenveto kertoo, kuinka monta jaksoa jono oli täynnä ja tyhjä. Jos
kumpikaan luku olisi nolla, rajatapaus olisi jäänyt testaamatta.
Toiminnallinen kattavuus on taidon *Laitteiston verifiointi* aihe.

## Ylivuoto on kutsujan virhe

FIFO jättää kirjoituksen täyteen jonoon huomiotta, mutta tieto katoaa
silti. Kirjoitus täyteen jonoon ja luku tyhjästä ovat aina virheitä
kutsuvassa logiikassa. Siksi moduuliin kannattaa lisätä
simulaation aikainen tarkistus. Synteesityökalu jättää `$fatal`-
kutsun huomiotta, joten tarkistus ei maksa laitteistossa mitään.

Seuraavassa esimerkissä on laskuriin perustuva FIFO, joka on toinen
yleinen toteutustapa, ja tuottaja, joka ei katso `taynna`-lippua:

```{.systemverilog tiedosto="esimerkit/08-ylivuoto.kaatuu.sv" osa="tarkistus"}
```

```{.systemverilog tiedosto="esimerkit/08-ylivuoto.kaatuu.sv" osa="tuottaja"}
```

```{.tuloste tiedosto="esimerkit/08-ylivuoto.virhe"}
```

Koko esimerkki on tiedostossa `08-ylivuoto.kaatuu.sv`. SystemVerilogin
väittämät (`assert property`) ilmaisevat saman tiiviimmin. Niitä
käsitellään verifiointitaidossa.

## Rekisteripankki

Prosessori ohjaa laitteistoa *ohjausrekisterien* (control and status
registers, CSR) kautta. Rekisteripankki on väylän ja laitteiston
välinen sovitin. Jokaisella rekisterillä on osoite ja käyttötapa:

| Tyyppi | Kirjoitus | Luku | Esimerkki |
|--------|-----------|------|-----------|
| RW | tallentaa arvon | palauttaa tallennetun | asetukset |
| RO | ei vaikutusta | laitteiston tila | tila, laskurit |
| W1C | 1 nollaa bitin, 0 ei vaikuta | tapahtumabitit | keskeytykset |
| W1S | 1 asettaa bitin | – | käskyt |

W1C (write one to clear) on keskeytysten vakiokäytäntö. Ohjelmisto
kirjoittaa takaisin juuri ne bitit, jotka se käsitteli, eikä
lukea–muokkaa–kirjoita-kilpailu voi kuitata tapahtumaa, joka tuli
lukemisen ja kirjoittamisen välissä.

```{.systemverilog tiedosto="esimerkit/08-rekisteripankki.sv" osa="kartta"}
```

```{.systemverilog tiedosto="esimerkit/08-rekisteripankki.sv" osa="rekisterit"}
```

Kun laitteisto asettaa bitin samalla jaksolla, jolla ohjelmisto sen
kuittaa, asetus voittaa. Muuten uusi tapahtuma katoaisi. Tuntematon
osoite palauttaa tunnistettavan arvon, joka erottuu helposti
virheenjäljityksessä. Testipenkki käyttää väylää kahdella tehtävällä:

```{.systemverilog tiedosto="esimerkit/08-rekisteripankki.sv" osa="vayla"}
```

```{.tuloste tiedosto="esimerkit/08-rekisteripankki.odotettu"}
```

Väylä on 32-bittinen, mutta pankki käyttää vain osaa kirjoitusdatan
biteistä. Verilator varoittaa käyttämättömistä biteistä, ja varoitus
vaiennetaan `lint_off`-kommentilla, jonka vieressä kerrotaan syy.

## Käytännössä

- **Kirjoita muisti päättelykuviona.** Rekisteröity luku, ei nollausta,
  yksi kirjoitus- ja yksi lukuportti kelloa kohden. Kun koodi poikkeaa
  kuviosta, synteesi tekee muistin kiikuista, ja pinta-ala voi kasvaa
  satakertaiseksi. Synteesiraportista tarkistetaan, että muisti
  päätyi lohkomuistiin.
- **Toimittajan muistimakro vain tarvittaessa.** Valmistajakohtainen
  instanssi sitoo koodin yhteen piiriperheeseen. Päättely on
  siirrettävä, ja makroa tarvitaan vain erikoistoimintoihin, kuten
  ECC:hen tai ASIC-muisteihin.
- **FIFO kahden potenssin syvyydellä.** Ylimääräisen bitin osoittimet
  toimivat vain, kun syvyys on kahden potenssi. Muu syvyys vaatii
  laskurin tai vertailijan, ja parametrin tarkistus estää väärän
  käytön.
- **Liput laskurista vai osoittimista.** Laskuri antaa täyttöasteen
  suoraan (`maara`), mikä on hyödyllistä vuonohjauksessa (lähes täynnä
  -lippu). Osoitinvertailu on pienempi ja toimii myös asynkronisessa
  FIFOssa (luku 10).
- **Rekisterikartta yhdestä lähteestä.** Tuotannossa rekisterikartta
  kuvataan kerran (SystemRDL, IP-XACT tai taulukko), ja siitä
  generoidaan RTL, ohjelmiston otsikkotiedostot ja dokumentaatio.
  Käsin ylläpidetyt kopiot eroavat ennen pitkää toisistaan.
- **Simulaatiotarkistukset moduuliin.** Rajapinnan ehdot (ei
  kirjoitusta täyteen, ei lukua tyhjästä) tarkistetaan moduulin
  sisällä, jolloin jokainen käyttäjä hyötyy niistä ilman omaa
  testipenkkiä.

## Itsearviointi

- Osaat kirjoittaa RAM- ja ROM-muistin niin, että synteesi päättelee
  lohkomuistin, ja tiedät, mitä luku samaan osoitteeseen palauttaa.
- Osaat toteuttaa synkronisen FIFOn ylimääräisen bitin osoittimilla ja
  selittää täyden ja tyhjän ehdot.
- Osaat testata FIFOa jonomallilla ja varmistaa, että rajatapaukset
  tulevat testatuiksi.
- Osaat lisätä moduuliin simulaation aikaisen rajapintatarkistuksen.
- Osaat toteuttaa rekisteripankin RW-, RO- ja W1C-rekistereillä ja
  ratkaista samanaikaisen asetuksen ja kuittauksen.

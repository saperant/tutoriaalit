# Keskeytykset

Oheislaite kertoo suorittimelle tapahtumasta keskeytyksellä: UARTin
vastaanottopuskurissa on dataa, ajastin on lauennut, DMA-siirto on
valmis. Keskeytyksen polku kulkee oheislaitteesta keskeytysohjaimen
kautta ytimeen ja sieltä ohjelmiston käsittelijään, ja jokaisessa
vaiheessa on sopimus, joka on tehtävä oikein.

## RISC-V:n ansat

RISC-V kutsuu yhteisellä nimellä *ansaksi* (trap) sekä keskeytyksiä
(asynkronisia tapahtumia) että poikkeuksia (käskyn aiheuttamia
virheitä). M-tilan ansoja ohjaavat seuraavat CSR:t:

| CSR | Sisältö |
|-----|---------|
| `mstatus` | MIE: keskeytykset sallittu; MPIE: MIE ennen ansaa |
| `mie` | keskeytyslähteittäiset sallinnat: MTIE (ajastin), MEIE (ulkoinen), MSIE (ohjelmisto) |
| `mip` | odottavat keskeytykset (vain luku tässä ytimessä) |
| `mtvec` | ansakäsittelijän osoite |
| `mepc` | paluuosoite: keskeytetty tai virheen aiheuttanut käsky |
| `mcause` | syy; ylin bitti 1 = keskeytys, 0 = poikkeus |
| `mtval` | lisätieto: virheellinen osoite tai käsky |

Keskeytys otetaan vastaan, kun `mstatus.MIE` on päällä ja jokin
keskeytys on sekä odottava (`mip`) että sallittu (`mie`). Pikku-SoC:n
ydin tarkistaa tämän ennen jokaisen käskyn hakua:

```{.systemverilog tiedosto="esimerkit/rtl/ydin.sv" osa="keskeytys"}
```

Ansaan siirtyessään ydin tallentaa tilan ja estää uudet keskeytykset:

```{.systemverilog tiedosto="esimerkit/rtl/ydin.sv" osa="ansa"}
```

`mret` palauttaa `mepc`:n ohjelmalaskuriin ja `MPIE`:n `MIE`:hen. Koska
`MIE` on käsittelijän aikana pois päältä, keskeytykset eivät
sisäkkäisty, ellei käsittelijä salli niitä itse.

## Ohjelmiston puoli

Ansakäsittelijän sisääntulo on assemblyä, koska sen on tallennettava
rekisterit, joita keskeytetty koodi käytti. RISC-V:n kutsukonventiossa
riittää tallentaa kutsujan tallennettavat rekisterit (`ra`, `t0`–`t6`,
`a0`–`a7`); C-funktio tallentaa itse käyttämänsä `s`-rekisterit:

```{.gnuassembler tiedosto="esimerkit/sw/start.S" osa="ansa"}
```

C-funktio jakaa ansat syyn mukaan. Keskeytyksen jälkeen palataan samaan
käskyyn (`mepc` osoittaa käskyyn, jota ei vielä suoritettu); poikkeuksen
käsittelijä päättää paluuosoitteen itse:

```{.c tiedosto="esimerkit/sw/tuki.c" osa="ansa"}
```

## Ajastin: CLINT

Ajastinkeskeytys tulee CLINT-lohkosta (core-local interruptor). Siinä
on vapaasti juokseva 64-bittinen laskuri `mtime` ja vertailurekisteri
`mtimecmp`. Keskeytys on voimassa, kun laskuri on saavuttanut
vertailuarvon:

```{.systemverilog tiedosto="esimerkit/rtl/clint.sv" osa="vertailu"}
```

Keskeytys on tasoliipaistu: se pysyy voimassa, kunnes ohjelmisto
siirtää vertailuarvoa eteenpäin. Siksi käsittelijä ohjelmoi seuraavan
ajastuksen ennen paluuta:

```{.c tiedosto="esimerkit/sw/keskeytykset.c" osa="ajastin"}
```

64-bittisen rekisterin päivittäminen 32-bittisellä suorittimella
vaatii kaksi kirjoitusta, ja niiden välissä vertailuarvo on puoliksi
vanha ja puoliksi uusi. Kirjoitusjärjestys (ensin alapuolisko
maksimiin, sitten yläpuolisko, sitten alapuolisko) varmistaa, ettei
väliaikainen arvo ole pienempi kuin kumpikaan oikea arvo. Laskurin
lukeminen kahdessa osassa vaatii vastaavasti tarkistuksen, ettei
yläpuolisko vaihtunut välissä.

## Ulkoiset keskeytykset: PLIC

Oheislaitteiden keskeytykset kootaan *keskeytysohjaimeen*. RISC-V:n
PLIC (platform-level interrupt controller) ottaa vastaan jopa tuhat
lähdettä ja välittää ne ytimille. Pikku-SoC:n ohjain on yksinkertaistettu
PLIC: lähteet ovat tasoliipaistuja, ja pienin numero on korkein
prioriteetti.

```{.systemverilog tiedosto="esimerkit/rtl/plic.sv" osa="lunastus"}
```

Ohjelmisto käsittelee keskeytyksen kolmessa vaiheessa:

1. **Lunastus (claim).** Käsittelijä lukee LUNASTA-rekisterin. Ohjain
   palauttaa tärkeimmän odottavan lähteen numeron ja peittää lähteen,
   jotta sama keskeytys ei laukea uudelleen käsittelyn aikana.
2. **Käsittely.** Käsittelijä palvelee lähdettä ja kuittaa tapahtuman
   oheislaitteessa (esimerkiksi W1C-rekisterillä). Vasta tämä poistaa
   keskeytyksen syyn.
3. **Valmis (complete).** Käsittelijä kirjoittaa lähteen numeron
   takaisin. Ohjain poistaa peiton, ja jos lähde on yhä aktiivinen,
   keskeytys tulee uudelleen.

```{.c tiedosto="esimerkit/sw/keskeytykset.c" osa="ulkoinen"}
```

Oikeassa PLICissä jokaisella lähteellä on prioriteetti, jokaisella
ytimellä ja tilalla (M, S) on oma *kontekstinsa* sallintoineen ja
prioriteettikynnyksineen, ja lähteen *portti* (gateway) muuntaa
reunaliipaistut keskeytykset pyynnöiksi. Uusissa RISC-V-järjestelmissä
PLICin rinnalle on tullut AIA (advanced interrupt architecture), jossa
keskeytykset voivat olla viestejä (MSI) kuten PCIe:ssä.

## Kokonaisuus

Kuvassa on keskeytyksen polku lähteestä ytimen käsittelijään ja
kuittaukseen. Väylät eivät ole polulla: keskeytys kulkee omia
johtojaan, ja vain kuittaus tehdään rekisterikirjoituksina.

```{.dot otsikko="Ulkoisen keskeytyksen polku Pikku-SoC:ssä"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.35;
  gpio [label="GPIO\nREUNAT & SALLI"];
  dma [label="DMA\nVALMIS"];
  plic [label="PLIC\nodottavat, prioriteetit,\nkynnys"];
  ydin [label="ydin\nmip.MEIP & mie.MEIE\n& mstatus.MIE"];
  kasittelija [label="käsittelijä\n(mtvec)"];
  clint [label="CLINT\nmtime >= mtimecmp"];
  gpio -> plic [label="lähde 1"];
  dma -> plic [label="lähde 2"];
  plic -> ydin [label="MEIP"];
  clint -> ydin [label="MTIP"];
  ydin -> kasittelija [label="ansa"];
  kasittelija -> plic [label="CLAIM/COMPLETE", style=dashed, constraint=false];
  kasittelija -> gpio [label="kuittaa REUNAT", style=dashed, constraint=false];
}
```

Pääohjelma sallii keskeytykset ensin lähteittäin (`mie`) ja sitten
yleisesti (`mstatus.MIE`):

```{.c tiedosto="esimerkit/sw/keskeytykset.c" osa="salli"}
```

GPIO-keskeytys aiheutetaan testipenkin silmukalla: lähdöt on kytketty
tuloihin, joten lähdön nostaminen tuottaa tulolle nousevan reunan:

```{.c tiedosto="esimerkit/sw/keskeytykset.c" osa="gpio"}
```

```{.tuloste tiedosto="esimerkit/odotettu/keskeytykset.odotettu"}
```

Toisella kerralla molemmat bitit nousivat, ja REUNAT-rekisteri kirjasi
molemmat, vaikka vain tulon 0 keskeytys on sallittu. Tila ja sallinta
ovat erillään: ohjelmisto voi lukea tapahtumat myös kyselemällä
(polling) sallimatta keskeytyksiä.

## Käytännössä

- **Kuittaa syy, ei vain ohjainta.** Tasoliipaistu keskeytys palaa heti,
  jos oheislaitteen tilaa ei kuitata ennen PLICin valmis-kirjoitusta.
  Tämä on yleisin keskeytyskäsittelijän virhe.
- **Taso- vai reunaliipaisu, sovi se.** Tasoliipaisu ei hukkaa
  tapahtumia ja sallii keskeytyslinjojen yhdistämisen, mutta vaatii
  kuittauksen. Reunaliipaisu ei vaadi kuittausta lähteessä, mutta
  reuna, joka tulee peitetyn ajan aikana, voi hukkua. Oheislaite ja
  ohjain on konfiguroitava samaan tapaan.
- **Lyhyet käsittelijät.** Käsittelijä kuittaa ja siirtää työn
  pääohjelmalle tai tehtävälle (lippu, jono). Pitkä käsittelijä pidentää
  muiden keskeytysten viivettä, koska MIE on pois päältä.
- **Jaetut muuttujat `volatile` ja atomisesti.** Käsittelijän ja
  pääohjelman yhteinen muuttuja on `volatile`, ja jos sen päivitys vaatii
  useamman käskyn, pääohjelma estää keskeytykset päivityksen ajaksi.
- **Mittaa viive.** Keskeytyksen viive (tapahtumasta käsittelijän
  ensimmäiseen käskyyn) koostuu ohjaimen, ytimen ja sisääntulokoodin
  viiveistä. Reaaliaikajärjestelmässä se lasketaan pahimman tapauksen
  mukaan (*Reaaliaikakäyttöjärjestelmät*).

## Itsearviointi

- Osaat selittää RISC-V:n M-tilan ansa-CSR:t ja sen, mitä ydin tekee
  ansaan siirtyessään ja `mret`-käskyssä.
- Osaat kirjoittaa ansakäsittelijän sisääntulon ja jakaa ansat syyn
  mukaan.
- Osaat ohjelmoida CLINT-ajastimen ja perustella 64-bittisen
  vertailuarvon kirjoitusjärjestyksen.
- Osaat käsitellä PLIC-keskeytyksen lunastuksella, kuittauksella ja
  valmis-kirjoituksella.
- Osaat valita taso- ja reunaliipaisun välillä ja tunnistaa kummankin
  virhetavat.

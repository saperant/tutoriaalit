# Kenttien käyttäytyminen

Bittisijainti ja pääsy eivät vielä kerro, mitä kenttä *tekee*. Lippu,
jonka laitteisto asettaa ja ohjelmisto kuittaa, laskuri, joka
nollautuu luettaessa, ja käynnistysbitti, joka on ylhäällä yhden
kellojakson, ovat kaikki tavallisia rekisterikentän tyyppejä. Jos
kuvaus ei ilmaise niitä, ne kirjoitetaan käsin generoidun lohkon
ympärille, ja niiden semantiikka on taas jokaisen kuluttajan oma
tulkinta. SystemRDL:ssä käyttäytyminen on osa kuvausta.

Luvun esimerkkinä on tapahtumalaskurilohko `rdl/kayttaytyminen.rdl`,
jonka jokainen kenttä näyttää yhden käyttäytymisen. Tässä luvussa
katsotaan kuvausta ja sitä, mitä laitteiston puolelle syntyy.
Luvussa 6 lohko tuotetaan RTL:ksi ja simuloidaan.

## Ohjelmiston sivuvaikutukset

`onread` ja `onwrite` kertovat, mitä luku ja kirjoitus tekevät kentän
arvolle tallennuksen lisäksi:

| Ominaisuus | Merkitys | UVM |
|-------------------------|-----------------------------------------|----------|
| `onwrite = woclr` | ykkösen kirjoitus nollaa bitin, nollan kirjoitus ei tee mitään | W1C |
| `onwrite = woset` | ykkösen kirjoitus asettaa bitin | W1S |
| `onwrite = wzc`, `wzs` | nollan kirjoitus nollaa tai asettaa | W0C, W0S |
| `onwrite = wclr`, `wset` | mikä tahansa kirjoitus nollaa tai asettaa | WC, WS |
| `onread = rclr` | luku nollaa kentän | RC |
| `onread = rset` | luku asettaa kentän | RS |
| `singlepulse` | kirjoitettu ykkönen on lähdössä yhden jakson | (WO) |

Kertapulssi on käynnistysbitin luonteva muoto. Ohjelmisto kirjoittaa
ykkösen, laitteisto näkee pulssin, ja kenttä on taas nolla.
Käyttäytyminen on ajallista, joten se näkyy parhaiten aaltomuodosta.
Kaavio on tuotetusta lohkosta simuloituna (testipenkki esitellään
luvussa 6):

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/kertapulssi.json" otsikko="Kertapulssi simulaatiosta: APB-kirjoitus (asetus- ja siirtovaihe) osoitteeseen 0 ja sitä seuraava yhden jakson pulssi laitteistolle. Toinen siirto on luku, joka palauttaa nollan."}
```
 Lukemalla
nollautuva laskuri kertoo tapahtumat edellisen lukemisen jälkeen
ilman erillistä nollauskirjoitusta:

```{.systemverilog tiedosto="esimerkit/rdl/kayttaytyminen.rdl" osa="ohjaus"}
```

```{.systemverilog tiedosto="esimerkit/rdl/kayttaytyminen.rdl" osa="laskuri"}
```

Lukemisen sivuvaikutus on kuitenkin vaarallinen. Debuggerin
muistinäkymä, joka lukee rekisterin näytölle, nollaa laskurin, ja
samoin tekee ohjelma, joka lukee rekisterin kahdesti vahingossa.
Taidossa *SoC-integraatio* suositeltiin siksi W1C:tä. Lukemalla
nollautuvia kenttiä käytetään, kun luku ja nollaus on tehtävä
atomisesti, kuten tapahtumalaskureissa, joista ei saa kadota
tapahtumia luvun ja nollauksen välissä.

## Laitteiston toiminnot

Toinen ryhmä ominaisuuksia lisää kenttään laitteiston signaaleja:

| Ominaisuus | Laitteiston puolelle syntyy | Käyttö |
|------------------|-----------------------------------|----------------------|
| `hwset`, `hwclr` | tulo, joka asettaa tai nollaa kentän | tilaliput |
| `counter` | tulo `incr` (ja `decr`), tarvittaessa ylivuoto- ja kynnyslähdöt | tapahtumalaskurit |
| `incrsaturate` | laskuri pysähtyy suurimpaan arvoon | tilastot |
| `swmod` | lähtö, joka on ylhäällä, kun ohjelmisto kirjoitti kentän | asetuksen muutoksen ilmoitus |
| `swacc` | lähtö, joka on ylhäällä, kun ohjelmisto luki kentän | jonon lukupää |
| `intr` | rekisterin keskeytyslähtö (`intr`) | keskeytysliput |

`swmod` ja `swacc` ovat tärkeitä silloin, kun rekisterin takana on
toimintaa. Näytejonon lukupää voi siirtyä seuraavaan näytteeseen heti,
kun ohjelmisto on lukenut nykyisen:

```{.systemverilog tiedosto="esimerkit/rdl/kayttaytyminen.rdl" osa="nayte"}
```

## Keskeytykset

Kenttä, jolla on ominaisuus `intr`, on keskeytyslähde. Rekisterin
keskeytyslähtö on sen keskeytyskenttien TAI. Kentälle voidaan antaa
sallinta (`enable`) tai peite (`mask`), joka viittaa toiseen kenttään:

```{.systemverilog tiedosto="esimerkit/rdl/kayttaytyminen.rdl" osa="keskeytys"}
```

Tämä on tavallinen kolmen rekisterin keskeytysrakenne: tila (W1C),
sallinta (RW) ja niistä laskettu keskeytyslähtö. Ohjelmisto voi lukea
tilan, vaikka keskeytys ei ole sallittu (pollaus), ja kuittaa
käsittelemänsä lähteet kirjoittamalla lukemansa arvon takaisin.
Kuvaus kertoo kaiken tämän, joten generaattori tuottaa tilan, sallinnan
ja keskeytyslähdön logiikan, ja UVM-malli ja dokumentaatio tietävät,
että tila on W1C.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/keskeytys.json" otsikko="Tila, sallinta ja keskeytys simulaatiosta. Laitteiston hwset-pulssi asettaa tilabitin, mutta intr nousee vasta, kun sallinta kirjoitetaan osoitteeseen 0x0C. Ykkösen kirjoitus tilarekisteriin 0x08 kuittaa bitin, ja intr laskee."}
```

Kaaviossa näkyy kolme asiaa, jotka kuvaus lupasi. Tilabitti asettuu
heti seuraavalla kellon reunalla ja pysyy, vaikka `hwset` kestää vain
jakson. Ensimmäinen siirto osoitteeseen `0x08` on luku, eikä se muuta
tilaa. Keskeytys seuraa tilan ja sallinnan JA-tuloa ilman viivettä:
se nousee samalla reunalla kuin sallinta ja laskee samalla reunalla
kuin tila.

Lisäksi `intr`-kentälle voidaan kuvata, onko keskeytys taso- vai
reunaliipaistu (`posedge`, `negedge`, `bothedge`, `level`) ja jääkö
asetettu bitti päälle (`stickybit`) vai seuraako se tuloa (`nonsticky`).
Oletus on tasoliipaistu, päälle jäävä bitti, joka on
keskeytystilarekistereissä tavallisin.

## Malli ja laitteiston liitäntä

Esimerkki `03-kayttaytyminen.py` tulostaa jokaisen kentän pääsyn ja
toiminnot sekä regblockin tuottaman luettelon laitteiston puolen
signaaleista:

```{.python tiedosto="esimerkit/03-kayttaytyminen.py" osa="hwif"}
```

```{.tuloste tiedosto="esimerkit/03-kayttaytyminen.odotettu"}
```

Luettelo on lohkon *laitteistorajapinta*, ja se on yhtä tärkeä kuin
ohjelmistorajapinta. Se kertoo, mitä lohkoa käyttävän logiikan on
ohjattava (`hwif_in`) ja mitä se saa (`hwif_out`). Laskuri tarvitsee
vain `incr`-tulon, lippu `hwset`-tulon, ja keskeytys tulee valmiina
lähtönä. Kenttä, jolla ei ole laitteiston pääsyä tai toimintoja, ei
näy luettelossa lainkaan.

## Käytännössä

- **Kuvaa käyttäytyminen kenttään.** W1C, kertapulssi, laskuri ja
  keskeytys kuuluvat kuvaukseen, eivät generoidun lohkon ympärille
  käsin kirjoitettuun logiikkaan.
- **Vältä lukemisen sivuvaikutuksia,** ellei atomisuus sitä vaadi.
  Kirjoita perustelu kentän `desc`-kuvaukseen, jotta ajurin
  kirjoittaja tietää, ettei rekisteriä saa lukea turhaan.
- **Käytä keskeytyksille kolmen rekisterin rakennetta:** tila (W1C),
  sallinta (RW) ja kuvauksesta laskettu lähtö.
- **Lue laitteistorajapinta.** Tuotettu signaaliluettelo on paras
  tarkistus sille, että kuvaus vastaa sitä, mitä lohkon logiikka
  tarvitsee.

## Itsearviointi

- Osaat valita kentälle oikean luku- ja kirjoitussivuvaikutuksen
  (`woclr`, `rclr`, `singlepulse`) ja perustella valinnan.
- Osaat kuvata tapahtumalaskurin, tilalipun ja kirjoitus- tai
  lukuilmoituksen ja kertoa, mitä signaaleja niistä syntyy laitteistolle.
- Osaat kuvata keskeytyslähteen sallintoineen ja selittää tila-,
  sallinta- ja keskeytysrakenteen.
- Osaat lukea lohkon laitteistorajapinnan tuotetusta raportista.
- Osaat lukea kertapulssin ja keskeytysrakenteen toiminnan
  ajoituskaaviosta.

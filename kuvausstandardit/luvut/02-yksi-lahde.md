# Yksi totuuden lähde

Rekisterikartta on harvinainen rajapinta: sitä käyttävät samaan aikaan
laitteistosuunnittelija, verifioija, ajurin kirjoittaja, dokumentoija,
debuggeri ja käyttöjärjestelmä. Jokainen tarvitsee sen eri muodossa.
Tässä luvussa katsotaan, miksi muodot tuotetaan yhdestä kuvauksesta ja
miksi kuvauksen kannattaa olla standardimuotoinen.

## Kuluttajat

| Kuluttaja | Muoto | Mitä se tarvitsee kuvauksesta |
|----------------|-------------------|-----------------------------------|
| RTL | SystemVerilog, VHDL | kentät, nollausarvot, käyttäytyminen, väyläliitäntä |
| ajuri | C-otsake, Rust-ruutu | osoitteet, bittisijainnit, maskit |
| käsikirja | HTML, PDF, Markdown | nimet, kuvaukset, pääsytavat |
| verifiointi | UVM-rekisterimalli | pääsytavat, nollausarvot, osoitekartta |
| debuggeri | CMSIS-SVD | oheislaitteet, rekisterit, kenttien nimet |
| käyttöjärjestelmä | laitepuu | perusosoite, koko, keskeytys, yhteensopivuus |
| integraatiotyökalu | IP-XACT | väyläliitännät, muistikartat, portit |

```{.dot otsikko="Yksi lähde ja sen kuluttajat tämän taidon työkaluilla. Jokainen generaattori lukee saman käännetyn mallin ja tuottaa yhden tiedoston. CI tuottaa kaiken uudelleen ja vertaa tallennettuihin (luku 11)."}
digraph {
  rankdir=LR; nodesep=0.12; ranksep=0.5;
  node [shape=box, fontsize=10];
  rdl [label="ajastin.rdl", shape=ellipse];
  malli [label="systemrdl-compiler\n(malli ja tarkistukset)"];
  rdl -> malli;
  g1 [label="PeakRDL-regblock\najastin.sv"];
  g2 [label="PeakRDL-cheader\najastin.h"];
  g3 [label="PeakRDL-uvm\najastin_uvm.sv"];
  g4 [label="PeakRDL-ipxact\najastin.xml"];
  g5 [label="omat generaattorit\najastin.md, soc.svd, soc.dtsi"];
  malli -> g1; malli -> g2; malli -> g3; malli -> g4; malli -> g5;
  k1 [label="simulointi ja synteesi", shape=plaintext];
  k2 [label="ajuri (C)", shape=plaintext];
  k3 [label="UVM-ympäristö", shape=plaintext];
  k4 [label="integraatiotyökalu", shape=plaintext];
  k5 [label="käsikirja, debuggeri,\nkäyttöjärjestelmä", shape=plaintext];
  g1 -> k1; g2 -> k2; g3 -> k3; g4 -> k4; g5 -> k5;
}
```

Kun yksi rivi kuvauksessa muuttuu, kaikki seitsemän muuttuvat
samassa muutoksessa. Käsin ylläpidettynä muutos tehdään seitsemään
paikkaan, eri ihmisten toimesta, eri aikaan. Virheet ovat tyypillisesti
pieniä ja vaikeita löytää: kenttä siirtyy RTL:ssä yhden bitin mutta ei
otsakkeessa, käsikirja kertoo vanhan nollausarvon, tai testipenkin
malli pitää kirjoitettavana kenttää, joka on muuttunut vain
luettavaksi.

## Oma muoto vai standardi

Taidossa *EDA-työkaluketjujen automatisointi* ajastimen rekisterit
kuvattiin omalla TOML-muodolla, ja satakunta riviä Pythonia tuotti
siitä RTL:n, otsakkeen, dokumentin ja testipenkin. Oma muoto on hyvä
opetusväline ja perusteltu pienessä projektissa, mutta sen rajat
tulevat nopeasti vastaan:

- **Semantiikka on omaa.** Mitä `w1c` tarkoittaa, jos kenttää
  kirjoittavat samalla jaksolla sekä laitteisto että ohjelmisto? Oma
  muoto vastaa siihen generaattorin koodissa, standardi määrittelyssä.
- **Kuluttajat ovat omia.** Jokainen uusi kuluttaja (UVM, SVD,
  laitepuu, IP-XACT) on uusi generaattori ylläpidettäväksi.
- **Ilmaisuvoima kasvaa paloittain.** Laskurit, kertapulssit,
  keskeytysten sallinta, taulukot ja parametrit lisätään yksi
  kerrallaan, ja muodosta tulee vähitellen huonompi versio jostakin
  standardista.
- **Tieto ei siirry.** IP-toimittaja toimittaa IP-XACT:ia tai
  SystemRDL:ää, ja uusi työntekijä osaa ne jo.

Esimerkki `12-siirtyma.py` muuntaa vanhan TOML-kuvauksen
SystemRDL:ksi, kääntää tuloksen ja vertaa sitä käsin kirjoitettuun
kuvaukseen `rdl/ajastin.rdl`. Muunnos on suoraviivainen, koska
TOML-muodon kolme pääsytapaa vastaavat SystemRDL:n ominaisuuksia:

```{.python tiedosto="esimerkit/12-siirtyma.py" osa="muunnos"}
```

```{.tuloste tiedosto="esimerkit/12-siirtyma.odotettu"}
```

Osoitteet, bitit, pääsytavat ja nollausarvot ovat samat. Käsin
kirjoitetussa SystemRDL-kuvauksessa on kuitenkin tietoa, jota
TOML-muoto ei pystynyt ilmaisemaan: `VALMIS`-lipun asettaa laitteisto
(`hwset`), se on keskeytyslähde (`intr`), ja keskeytys on sallittu vain,
kun `CTRL.IE` on päällä. Nämä ominaisuudet käydään läpi luvuissa 3
ja 4; tässä riittää havainto, että ne ovat kuvauksessa. Omassa muodossa tämä logiikka kirjoitettiin
käsin generoidun lohkon ympärille. SystemRDL:ssä se on osa kuvausta,
ja generaattori tuottaa sen.

Siirtymä kannattaa tehdä juuri näin: muunnin vanhasta muodosta
standardiin, vertailu vanhan ja uuden tuotoksen välillä ja vasta sen
jälkeen standardin lisäominaisuuksien käyttöönotto. Näin varmistetaan,
ettei siirtymä itse muuta rajapintaa.

## Standardit ja niiden roolit

Standardit eivät kilpaile keskenään, vaan ne kattavat eri osia
samasta tiedosta:

| Standardi | Ylläpitäjä | Mitä kuvaa | Tyypillinen käyttö |
|-------------|------------|----------------------|------------------------------|
| SystemRDL 2.0 | Accellera | rekisterit, kentät, osoitekartat, käyttäytyminen | rekisterien lähdekuvaus |
| IP-XACT | IEEE 1685 | IP-lohko kokonaisuudessaan: portit, väylät, muistikartat, tiedostot | tiedonsiirto työkalujen ja toimittajien välillä |
| CMSIS-SVD | Arm | mikrokontrollerin oheislaitteet ohjelmiston näkökulmasta | debuggerit, otsake- ja ruutugeneraattorit |
| laitepuu | devicetree.org | laitteet, osoitteet, keskeytykset ja kellot käyttöjärjestelmälle | Linux, Zephyr, U-Boot |
| UVM-rekisterimalli | Accellera (IEEE 1800.2) | rekisterien malli testipenkissä | verifiointi |

Tavallinen työnjako on, että rekisterit kirjoitetaan SystemRDL:llä,
ja IP-XACT, SVD, laitepuu ja UVM-malli tuotetaan siitä. IP-XACT voi
olla myös lähde, jos IP tulee toimittajalta valmiina IP-XACT-pakettina
tai jos integraatiotyökalu käyttää sitä.

Muita käytössä olevia muotoja ovat OpenTitanin Hjson-rekisterikuvaukset
ja niiden `regtool`, Rustin `svd2rust`-ekosysteemin SVD-laajennukset
sekä kaupallisten työkalujen omat muodot. Niiden idea on sama.

## Käytännössä

- **Valitse lähde ja pidä siitä kiinni.** Kaikki muut muodot
  tuotetaan, eikä niitä muokata. Tuotettuun tiedostoon tehty korjaus
  katoaa seuraavassa tuotossa ja jää lisäksi pois muista muodoista.
- **Standardi ennen omaa muotoa.** Oma muoto on perusteltu vain, jos
  tarve on todella pieni. Kun tarvitaan toinen kuluttaja tai
  ensimmäinen laskurikenttä, standardi on halvempi.
- **Siirry vaiheittain.** Muunna vanha kuvaus, vertaa tuotoksia ja
  ota uudet ominaisuudet käyttöön vasta, kun tuotokset ovat samat.
- **Kuvaa käyttäytyminen, älä vain bittejä.** Kenttä, jonka laitteisto
  asettaa ja ohjelmisto kuittaa, on eri asia kuin tavallinen
  kirjoitettava kenttä. Ero kuuluu kuvaukseen, ei käsin kirjoitettuun
  liimalogiikkaan.

## Itsearviointi

- Osaat luetella rekisterikuvauksen kuluttajat ja mitä kukin tarvitsee
  kuvauksesta.
- Osaat perustella, milloin oma kuvausmuoto riittää ja milloin
  standardi on parempi.
- Osaat kertoa SystemRDL:n, IP-XACT:n, CMSIS-SVD:n, laitepuun ja
  UVM-rekisterimallin roolit ja sen, mikä niistä on tavallisesti lähde.
- Osaat suunnitella siirtymän omasta muodosta standardiin niin, ettei
  rajapinta muutu siirtymässä.

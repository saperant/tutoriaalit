# Debug-rajapinnat

Staattinen analyysi kertoo, mitä koodi *voi* tehdä; dynaaminen analyysi
kertoo, mitä se *tekee*. Sulautetussa laitteessa dynaaminen analyysi
vaatii pääsyn laitteeseen: sarjaportin, debug-väylän tai emulaattorin.
Tämä luku käsittelee rajapinnat; emulointi QEMU:lla ja Unicornilla on
luvuissa 8 ja 9.

## Sarjakonsoli

Yksinkertaisin rajapinta on sarjaportti (UART). Monessa laitteessa on
komentokonsoli tai vähintään käynnistysviestit, jotka kertovat paljon
rakenteesta. LT-100:n konsoli emuloidaan QEMU:ssa (luku 8 selittää
ajon); tässä se vain näytetään:

```{.bash tiedosto="esimerkit/07-debug/aja.sh" osa="konsoli"}
```

```{.tuloste tiedosto="esimerkit/07-debug/odotettu" osa="s1"}
```

Käynnistysviesti kertoo käynnistyslataimen version ja sen, että
sovelluksen tarkiste tarkistettiin. `ohje`-komento listaa toiminnot.
Tuotantolaitteessa tällainen konsoli on usein tahaton tietovuoto: se
paljastaa rakenteen ja saattaa tarjota piilokomentoja (luku 10).

## JTAG ja SWD

Laitteiston debug-väylät JTAG ja SWD (*Serial Wire Debug*) antavat
suoran pääsyn prosessoriin: muistin luku ja kirjoitus, rekisterit,
katkaisukohdat ja ohjelman pysäytys. Ne ovat kehityksen
välttämättömiä, mutta tuotannossa avoin debug-portti on vakava
heikkous: se antaa täyden pääsyn laiteohjelmistoon ja muistiin.
Fyysistä JTAG/SWD-laitetta ei tässä ole, mutta QEMU tarjoaa saman
rajapinnan gdb-palvelimena, joka vastaa samaan protokollaan kuin SWD-
sovitin.

## gdb ilman symboleita

gdb liitetään QEMU:n gdb-palvelimeen, ja analyysi tehdään pelkillä
osoitteilla, jotka edellisissä luvuissa pääteltiin. Skripti pysäyttää
suorituksen käynnistyslataimen tarkistusfunktioon, lukee sen argumentit
ja paluuarvon, ja jatkaa sovelluksen alkuun:

```{.bash tiedosto="esimerkit/07-debug/istunto.gdb" osa="kelpaa"}
```

```{.bash tiedosto="esimerkit/07-debug/aja.sh" osa="gdb"}
```

```{.tuloste tiedosto="esimerkit/07-debug/odotettu" osa="s2"}
```

gdb vahvistaa staattisen analyysin: funktio `0x54` saa argumentikseen
otsakkeen osoitteen `0x10000`, jonka ensimmäinen sana on `LTAP`, ja
palauttaa nollan (kuva kelpaa). Dynaaminen ja staattinen analyysi
tukevat toisiaan: osoitteet tulevat staattisesta, niiden merkitys
varmistuu ajossa.

## Debug-lukituksen tarkistus omassa laitteessa

Puolustuksen kannalta tärkein kysymys on, onko oman tuotantolaitteen
debug-portti lukittu. Lukitus on usein asetuslohkon kenttä tai
piirin lukkobitti. LT-100:n asetuslohkossa on debug-lukituskenttä:

```{.bash tiedosto="esimerkit/07-debug/aja.sh" osa="lukitus"}
```

```{.tuloste tiedosto="esimerkit/07-debug/odotettu" osa="s3"}
```

Kenttä `0x3f01c` on `0xffffffff`: debug on auki (tyhjä flash-arvo,
tehdas ei lukinnut). Oikeassa tuotteessa tämän pitäisi olla lukitusarvo,
ja piirin oma lukkobitti (esim. STM32:n RDP taso 2 tai nRF:n APPROTECT)
asetettu. Lukituksen toteutus ja luottamusketju ovat taidossa
*Sulautettujen järjestelmien tietoturva*. Takaisinmallinnuksen rooli
tässä on auditointi: tarkistaa, että suojaus on oikeasti päällä, eikä
vain tarkoitettu päälle.

## Käytännössä

- **Katso sarjaportti ensin.** Käynnistysviestit ja mahdollinen konsoli
  antavat rakenteen ja version ilmaiseksi. Tuotteessa harkitse, mitä
  konsoli paljastaa ja pitäisikö se poistaa käytöstä.
- **gdb varmistaa staattisen analyysin.** Aseta katkaisukohta
  pääteltyyn osoitteeseen, lue argumentit ja paluuarvot. Osoitteet
  tulevat staattisesta analyysista, merkitys ajosta.
- **Auditoi oman laitteen debug-lukitus.** Tarkista sekä
  ohjelmistopuolen lukituskenttä että piirin lukkobitti. Auki jäänyt
  debug-portti mitätöi muut suojaukset.
- **Puolustus:** tuotannossa debug-portti lukitaan ja käynnistyksen
  konsolikomennot karsitaan. Lukituksen oikea toteutus on omassa
  taidossaan; takaisinmallinnus todentaa, että se pitää.

## Itsearviointi

- Osaat lukea laitteen sarjakonsolin ja päätellä siitä rakennetta ja
  version.
- Osaat selittää JTAG:n ja SWD:n roolin ja sen, miksi avoin debug-portti
  on tuotannossa heikkous.
- Osaat liittää gdb:n emuloituun laitteeseen ja tutkia funktion
  argumentteja ja paluuarvoa pelkillä osoitteilla.
- Osaat tarkistaa oman laitteen debug-lukituksen tilan.

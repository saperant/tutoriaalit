# CMSIS-SVD ja laitepuu

Ohjelmistotyökalut eivät lue SystemRDL:ää. Debuggeri näyttää
oheislaitteiden rekisterit SVD-tiedostosta, Rust-ajurien rajapinta
tuotetaan SVD:stä, ja Linux löytää laitteet laitepuusta. Molemmat
tuotetaan samasta kuvauksesta, ja tässä luvussa kirjoitetaan niille
omat pienet generaattorit.

## Piirin kuvaus

Lohkot kootaan piiriksi omassa osoitekartassaan. Samaa ajastinta
käytetään kahdesti, ja DMA-ohjain saa kanavamääränsä parametrina.
Keskeytysnumero ja laitepuun yhteensopivuusmerkkijono annetaan
luvun 5 omilla ominaisuuksilla:

```{.systemverilog tiedosto="esimerkit/rdl/soc.rdl" osa="soc"}
```

## CMSIS-SVD

SVD (System View Description) on Armin CMSIS-standardin XML-muoto.
Se kuvaa piirin oheislaitteet ohjelmiston näkökulmasta: perusosoite,
keskeytykset, rekisterit, kentät ja niiden pääsy. Mikrokontrollerien
valmistajat julkaisevat SVD-tiedostot piireilleen, ja niitä käyttävät
debuggerit (muistinäkymä kenttien niminä), `svd2rust` (Rustin
oheislaiteruudut) ja `svdconv` (C-otsakkeet ja tarkistus).

Pääsytapa ilmaistaan samoin kolmella tiedolla kuin IP-XACT:ssa:

```{.python tiedosto="esimerkit/kuvaus/svd.py" osa="paasy"}
```

Oheislaitteen generaattori hyödyntää kahta SVD:n tiivistyskeinoa.
Jos sama lohkotyyppi on piirissä useasti, toinen instanssi viittaa
ensimmäiseen (`derivedFrom`), eikä rekistereitä toisteta. Lohkon
tyyppi tunnistetaan kuvauksen alkuperäisestä tyyppinimestä
(`orig_type_name`), koska parametrit ja omat ominaisuudet muuttavat
elaboroidun tyypin nimeä:

```{.python tiedosto="esimerkit/kuvaus/svd.py" osa="oheislaite"}
```

```{.xml tiedosto="esimerkit/tuotettu/otteet/svd_ajastin1.xml"}
```

Toinen keino on klusteri (`cluster`) toistomäärineen. DMA:n
kanavataulukko kuvataan kerran, ja `dim` ja `dimIncrement` kertovat
alkioiden määrän ja välin:

```{.xml tiedosto="esimerkit/tuotettu/otteet/svd_kanava.xml"}
```

Tuotettu tiedosto tarkistetaan lukemalla se niin kuin debuggeri sen
lukisi: periytyvät oheislaitteet ja klusteritaulukot puretaan
osoitteiksi, ja osoitteita verrataan malliin:

```{.python tiedosto="esimerkit/10-svd-laitepuu.py" osa="svd"}
```

Varsinaisessa projektissa SVD tarkistetaan lisäksi Armin
`svdconv`-työkalulla tai skeemaa vastaan, ja tuotetusta tiedostosta
käännetään esimerkiksi `svd2rust`-ruutu CI:ssä.

## Laitepuu

Taidossa *Sulautettu Linux* laitepuu esiteltiin kuvauksena, josta ydin
löytää laitteet. Taidossa *Linux-laiteajurit* ajuri sidottiin
laitteeseen `compatible`-merkkijonolla ja luki osoitealueen ja
keskeytyksen solmun ominaisuuksista `reg` ja `interrupts`. Kaikki kolme
ominaisuutta ovat samassa kuvauksessa kuin rekisterit:

```{.python tiedosto="esimerkit/kuvaus/laitepuu.py" osa="solmut"}
```

```{.c tiedosto="esimerkit/tuotettu/soc.dtsi"}
```

Linuxin oma tyyli sisentää laitepuun sarkaimilla; tässä käytetään
välilyöntejä kirjan rivinleveyden vuoksi, eikä `dtc` välitä
sisennyksestä. Solmut sisällytetään piirin laitepuuhun
(`/include/ "soc.dtsi"`) väylän solmun alle, ja `dtc` kääntää ne:

```{.python tiedosto="esimerkit/10-svd-laitepuu.py" osa="laitepuu"}
```

```{.tuloste tiedosto="esimerkit/10-svd-laitepuu.odotettu"}
```

Kokonaisessa laitepuussa tarvitaan lisäksi tietoja, jotka eivät kuulu
rekisterikuvaukseen: keskeytysohjaimen viittaus (`interrupt-parent`),
keskeytyksen tyyppi, kellot ja nollaukset. Ne voi lisätä omilla
ominaisuuksilla tai kirjoittaa käsin piirin laitepuuhun, jolloin
tuotettu osa sisältää vain sen, mikä varmasti seuraa rekistereistä.
Laitepuun sidontojen (*bindings*) YAML-kuvauksia vastaan solmut
tarkistetaan `dt-schema`-työkalulla.

## Käytännössä

- **SVD ja laitepuu ovat tuotteita,** eivät lähteitä. Kun lohkon
  perusosoite tai keskeytys muuttuu, ohjelmiston näkymä päivittyy
  samassa muutoksessa.
- **Tiivistä toistuvat rakenteet.** `derivedFrom` ja klusterit pitävät
  SVD-tiedoston luettavana ja vastaavat kuvauksen taulukoita.
- **Tunnista lohkotyypit alkuperäisestä nimestä.** Elaboroitu
  tyyppinimi muuttuu parametrien ja dynaamisten sijoitusten mukana.
- **Tarkista tuotokset kuluttajan työkalulla.** SVD luetaan kuten
  debuggeri sen lukee, ja laitepuu käännetään `dtc`:llä.

## Itsearviointi

- Osaat kertoa, mitä CMSIS-SVD kuvaa ja mitkä työkalut käyttävät sitä.
- Osaat tuottaa SVD-tiedoston mallista periytyvine oheislaitteineen ja
  klusteritaulukkoineen.
- Osaat tuottaa laitepuun solmut (`compatible`, `reg`, `interrupts`)
  samasta kuvauksesta ja tarkistaa ne `dtc`:llä.
- Osaat rajata, mikä laitepuun tieto kuuluu rekisterikuvaukseen ja mikä
  piirin käsin kirjoitettuun laitepuuhun.

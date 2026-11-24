# Johdanto {.runko-johdanto}

*Laiteohjelmisto* (*firmware*) on ohjelma, joka ajetaan sulautetussa
laitteessa: mikrokontrollerissa, verkkolaitteessa, autossa tai kodin
elektroniikassa. Toisin kuin tavallinen sovellus, laiteohjelmisto on
sidoksissa laitteeseensa: se tuntee laitteen muistikartan,
oheislaitteet ja käynnistystavan, ja se toimitetaan usein pelkkänä
binäärikuvana ilman lähdekoodia, symboleita tai dokumentaatiota.

*Laiteohjelmiston takaisinmallinnus* on tällaisen binäärikuvan
purkamista, analysointia ja ajamista sen selvittämiseksi, mitä laite
tekee ja miten. Se on *Takaisinmallinnus*-taidon laajennus
sulautettuihin järjestelmiin: samat menetelmät (disassemblointi,
staattinen ja dynaaminen analyysi) pätevät, mutta kohde ei ole
käyttöjärjestelmän alla ajettava ELF-ohjelma vaan koko laitteen
muistiin ladattava kuva, joka alkaa suorittua ilman käyttöjärjestelmää.

## Mihin tätä tarvitaan

Takaisinmallinnus on työkalu, ei itsetarkoitus. Sulautetussa työssä se
ratkaisee konkreettisia ongelmia:

- **Kadonneet lähteet.** Vanhan, yhä tuotannossa olevan laitteen
  lähdekoodi tai työkaluketju on kadonnut, mutta laiteohjelmiston kuva
  on tallessa. Takaisinmallinnus kertoo, mitä laite tekee, jotta sitä
  voi ylläpitää tai korvata.
- **Vianetsintä ja suorituskyky.** Kun laite käyttäytyy väärin eikä
  vikaa löydy lähteestä, binääri kertoo, mitä prosessori oikeasti
  suorittaa. Luvussa 10 paikannetaan binääristä suorituskykyongelma,
  jonka syy on kääntäjän asetus, ei lähdekoodi.
- **Yhteentoimivuus.** Oman laitteen protokolla, tiedostomuoto tai
  tarkistusalgoritmi on selvitettävä, jotta sille voi kirjoittaa
  yhteensopivan työkalun. Luvuissa 2 ja 9 puretaan oman laitteen
  päivityspaketti ja tarkistealgoritmi.
- **Tietoturva-auditointi.** Oman tuotteen laiteohjelmistosta
  etsitään heikkouksia ennen kuin joku muu löytää ne: kovakoodatut
  avaimet, auki jätetyt debug-portit, allekirjoittamattomat
  päivitykset ja puskurin ylivuodot. Luvut 7, 9 ja 10 tekevät tämän.
- **Haittaohjelma- ja laiteanalyysi.** Tietoturvatutkija selvittää,
  mitä epäilyttävä laiteohjelmisto tekee, osana puolustustyötä.

## Vastuulauseke, laki ja etiikka

Tämä tutoriaali on tarkoitettu oppimiseen ja ammatilliseen,
puolustavaan työhön. Takaisinmallinnuksen tekniikat ovat
kaksikäyttöisiä: samalla taidolla voi ylläpitää omaa laitetta tai
murtautua toisen laitteeseen. Erottava tekijä ei ole tekniikka vaan
kohde ja lupa.

**Tekniikoita saa soveltaa vain omiin laitteisiin ja ohjelmistoihin
tai kohteisiin, joihin on nimenomainen lupa.** Tämän paketin kaikki
kohteet ovat paketin itse kääntämiä: kuvitteellinen LT-100-
lämpötilaloggeri, jonka lähdekoodi, käännös ja kaikki muunnelmat
rakennetaan hakemistossa `esimerkit/laite/`. Mitään kolmannen
osapuolen laiteohjelmistoa ei pureta eikä ladata verkosta.

Oikeudellinen tausta on sama kuin *Takaisinmallinnus*-taidossa, johon
tässä viitataan: EU:n tietokoneohjelmadirektiivi (2009/24/EY) ja Suomen
tekijänoikeuslain 25 j ja 25 k § sallivat ohjelman laillisen käyttäjän
tutkia ohjelman toimintaa ja dekompiloida sen yhteentoimivuuden
saavuttamiseksi. Sopimusehto ei voi kieltää näitä oikeuksia, mutta ne
eivät ulotu kopiosuojausten tai pääsynvalvonnan kiertämiseen.
Sulautetuissa laitteissa on lisäksi omat rajansa:

- **Käyttöehdot ja takuu.** Laiteohjelmiston muuttaminen rikkoo usein
  takuun ja voi rikkoa käyttöehtoja.
- **Radiolaitteet.** Jos laitteessa on radiolähetin, muokattu
  laiteohjelmisto ei välttämättä enää täytä
  vaatimustenmukaisuusvaatimuksia (RED-direktiivi, Traficomin
  määräykset), eikä laitetta saa silloin käyttää lähettimenä.
- **Turvakriittiset laitteet.** Lääkintälaitteen, ajoneuvon tai
  teollisuuden ohjauslaitteen muuttaminen voi olla hengenvaarallista
  ja lainvastaista.

Tietoturvaheikkouksista ilmoitetaan vastuullisesti (*coordinated
vulnerability disclosure*): valmistajalle ilmoitetaan ensin ja
julkaisulle sovitaan kohtuullinen aika. Tekijät eivät vastaa tämän
materiaalin väärinkäytöstä.

## Mitä tutoriaali kattaa

Lähtökohta on binäärikuva ilman symboleita, ja edetään rakenteesta
koodiin ja ajoon. Luvut 2–3 selvittävät kuvan muodon ja laitteen
arkkitehtuurin, luvut 4–6 lukevat koodin, luvut 7–9 ajavat laitetta
(sarjakonsoli, gdb, QEMU ja Unicorn), ja luku 10 kokoaa ammatilliset
käyttötapaukset. Puolustus kulkee mukana: jokaisessa luvussa kerrotaan,
miten näkyvä heikkous korjataan omassa laitteessa. Syvemmät suojaukset
(turvallinen käynnistys, allekirjoitetut päivitykset, debug-porttien
lukitus, salaus) ovat taidossa *Sulautettujen järjestelmien
tietoturva*, johon viitataan.

Kohde on ARM Cortex-M3 QEMU:n `mps2-an385`-kortilla, sama kuin taidossa
*Mikrokontrollerit ja bare-metal-ohjelmointi*. Linux-pohjaiset laitteet
(reitittimet, kamerat) mainitaan, mutta niiden juuritiedostojärjestelmät
(squashfs, cpio) ja käyttötila kuuluvat taitoon *Sulautettu Linux*.

## Esitiedot ja työkalut

Lukijan oletetaan osaavan *Takaisinmallinnus*-taidon perusteet
(objdump, radare2, gdb, x86-64-assembly, ELF) ja
*Mikrokontrollerit*-taidon perusteet (Cortex-M:n vektoritaulu,
linkkeriskripti, muistikartta). Objektitiedostojen ja linkityksen
osalta viitataan taitoon *Objektitiedostot, linkitys ja ABI*.

Työkalut ovat avointa lähdekoodia: GNU binutils (`arm-none-eabi-`),
radare2, gdb, QEMU sekä Pythonin kirjastot Capstone (disassemblointi)
ja Unicorn (emulointi). Ghidra on alan laajin avoin
takaisinmallinnuskehys; sitä ei ajeta tässä ympäristössä, mutta sen
rooli esitellään luvussa 11.

Esimerkit ovat hakemistossa `esimerkit/`. Laitteen rakentaa
`esimerkit/laite/Makefile`, ja analyysit ovat hakemistoja
`esimerkit/NN-nimi/`, joissa `aja.sh` ajaa analyysin laitteen
tuotteille ja vertaa tulosteen tiedostoon `odotettu`. Analyysi ei lue
laitteen lähdekoodia; ELF-tiedostoja käytetään vain vastausavaimena,
jolla päättelyt tarkistetaan. `esimerkit/testaa.sh` ajaa kaikki
analyysit, ja kehityskontti on hakemistossa
`.devcontainer/laiteohjelmiston-takaisinmallinnus`.

Laitteen PDF-dokumentti ja pikaopas ovat osoitteissa
[laiteohjelmiston-takaisinmallinnus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/laiteohjelmiston-takaisinmallinnus.pdf)
ja
[laiteohjelmiston-takaisinmallinnus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/laiteohjelmiston-takaisinmallinnus-pikaopas.pdf).

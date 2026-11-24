# Lopuksi {.runko-lahteet}

## Ghidra

Ghidra on Yhdysvaltain NSA:n julkaisema avoimen lähdekoodin (Apache
2.0) takaisinmallinnuskehys, jonka vahvuus on hyvä dekompilaattori
useille arkkitehtuureille. Sitä ei ole Ubuntun paketeissa eikä sitä
asennettu tähän ympäristöön, joten se esitellään tässä tekstinä.
Peruskäyttö:

- **Projekti ja import.** Ohjelma tuodaan projektiin, ja automaattinen
  analyysi (*auto-analysis*) löytää funktiot, viittaukset ja tyypit.
- **Listausnäkymä ja dekompilaattori** rinnakkain: vasemmalla konekieli,
  oikealla C:tä muistuttava tuloste. Nimet ja tyypit, jotka asettaa
  jompaankumpaan, päivittyvät toiseen.
- **Rakenteet ja tyypit.** Kun olion asettelu on päätelty, sen voi
  määritellä rakenteena, jolloin dekompilaattori näyttää kenttien nimet
  siirtymien sijaan. Virtuaalitaulut ja C++-luokat saa samaan tapaan.
- **Headless-tila** `analyzeHeadless` ajaa analyysin ja skriptit ilman
  käyttöliittymää. Skriptit kirjoitetaan Javalla tai Pythonilla
  (Jython/PyGhidra), ja ne pääsevät käsiksi funktioihin,
  dekompilaatioon ja ristiviittauksiin. Näin analyysin saa
  toistettavaksi samaan tapaan kuin tämän paketin skriptit.

Vastaavia työkaluja: IDA Pro (kaupallinen, alan standardi), Binary
Ninja ja Hopper (kaupallisia), radare2 ja sen graafinen Cutter
(avoimia). Dekompilaattorin tuloste on kaikissa hypoteesi, joka
tarkistetaan konekielestä.

## Muut arkkitehtuurit

Pääkohde oli x86-64, mutta periaatteet siirtyvät:

- **AArch64** (64-bittinen ARM): kiinteä 4 tavun käskyleveys, 31
  yleisrekisteriä (`x0`–`x30`, 32-bittiset `w0`–`w30`), argumentit
  `x0`–`x7`, paluu `x0`. Rekisterien kiinteä leveys helpottaa purkua:
  lineaarinen läpikäynti ei sekoa yhtä helposti.
- **ARM/Thumb** (32-bittinen): kaksi käskyjoukkoa, 4 tavun ARM ja 2–4
  tavun Thumb; tila vaihtuu ajossa, ja purkajan on tiedettävä kumpi on
  käytössä. Yleinen sulautetuissa laitteissa; *Laiteohjelmiston
  takaisinmallinnus* jatkaa tästä.
- **RISC-V**: kiinteä (tai pakattu C-laajennoksella 2 tavun) käsky,
  selkeä kutsukonventio. *Assembly* opettaa sen kirjoittamisen.

Kutsukonventio, pinokehys, hyppytaulut ja kääntäjän kuviot ovat
arkkitehtuurista riippumatta samankaltaisia; vain käskyt ja rekisterit
vaihtuvat.

## Nyrkkisäännöt

- **Havainnoi ennen kuin puret.** Merkkijonot, tuonnit, strace ja
  ltrace kertovat ohjelman tehtävän minuuteissa.
- **Etene ristiviittauksin**, älä osiota alusta loppuun. Aloita
  `main`-funktiosta tai kiinnostavasta merkkijonosta.
- **Nimeä ja kommentoi heti.** Jokainen tunnistettu funktio, muuttuja
  ja kentän siirtymä kannattaa kirjata; projektitiedosto säilyttää työn.
- **Dekompilaattori kartoittaa, konekieli ratkaisee.** Tarkista
  ehtojen suunnat, etumerkit ja osoitinaritmetiikka konekielestä.
- **Vuorottele staattista ja dynaamista.** Staattinen kattaa kaikki
  polut, dynaaminen antaa todelliset arvot; yhdessä ne tarkistavat
  toisensa.
- **Varmista hypoteesit toteutuksella.** Jäsennin, joka kirjoittaa
  tiedoston uudelleen samaksi, tai malli, joka läpäisee eroavuustestin,
  on todiste; silmämääräinen varmuus ei ole.
- **Skriptaa kaikki.** Toistettava analyysi kestää ohjelman päivityksen
  ja oman muistin pettämisen.
- **Pysy laillisella ja eettisellä alueella.** Omat ohjelmat,
  yhteentoimivuus, luvallinen tutkimus; dokumentoi, mitä teet ja miksi.

## Jatkotaidot

*Laiteohjelmiston takaisinmallinnus* käsittelee laiteohjelmistokuvia,
ARM- ja Thumb-koodia sekä emulointia (QEMU, Unicorn).
*Haavoittuvuuksien analyysi ja hyödyntäminen* rakentuu tämän ja
*Tietoturvan perusteiden* päälle: muistiturvallisuuden virheet,
suojaukset ja niiden kiertäminen. *Kääntäjätekniikka* syventää, miksi
kääntäjä tuottaa näkemäsi koodin, ja *Objektitiedostot, linkitys ja
ABI* on tämän paketin tärkein esitieto.

## Lähteet

- Intel 64 and IA-32 Architectures Software Developer's Manual, Volume
  2 (käskyviite). Myös felixcloutier.com/x86 (verkkohakemisto).
- System V Application Binary Interface, AMD64 Architecture Processor
  Supplement (kutsukonventio, rakenteiden luokittelu).
- Itanium C++ ABI (nimien koristelu, virtuaalitaulut, RTTI):
  itanium-cxx-abi.github.io/cxx-abi.
- Dennis Andriesse: *Practical Binary Analysis*. No Starch Press, 2019.
- Chris Eagle, Kara Nance: *The Ghidra Book*. No Starch Press, 2020.
- Bruce Dang, Alexandre Gazet, Elias Bachaalany: *Practical Reverse
  Engineering*. Wiley, 2014.
- radare2-dokumentaatio: book.rada.re. Ghidra: ghidra-sre.org.
- DWARF Debugging Information Format, Version 5 (`.eh_frame`,
  virheenjäljitystieto): dwarfstd.org.
- Euroopan parlamentin ja neuvoston direktiivi 2009/24/EY
  tietokoneohjelmien oikeudellisesta suojasta (13 ja 14 artikla).
- Tekijänoikeuslaki 404/1961, 25 j ja 25 k § (dekompilointi ja
  tutkiminen): finlex.fi.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.

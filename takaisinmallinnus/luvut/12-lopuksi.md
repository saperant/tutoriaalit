# Lopuksi {.runko-lahteet}

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

## Miten jatkaa laillisesti

Takaisinmallinnusta oppii tekemällä, ja kohteita on riittävästi ilman,
että kenenkään toisen ohjelmaan tarvitsee koskea luvatta:

- **Omat ohjelmat.** Käännä omaa koodiasi eri optimointitasoilla ja
  kääntäjillä ja lue tulos. Se on myös taidon tavallisin käyttö
  työssä: suorituskykyongelman tai kääntäjän virheen selvittäminen.
- **Avoimen lähdekoodin ohjelmat.** Riisu jakelun paketin ohjelma
  symboleista, analysoi se ja tarkista päätelmät lähdekoodista.
- **Harjoitustehtävät ja kilpailut.** *CTF* (*capture the flag*) on
  kilpailumuoto, jossa ratkaistaan tätä varten tehtyjä tehtäviä;
  takaisinmallinnus (*reversing*) on yksi vakiolajeista. Tehtävien
  analysointi on luvallista sääntöjen puitteissa, joten lue jokaisen
  palvelun säännöt ennen aloittamista.

| Palvelu | Mitä tarjoaa | Osoite |
|---------|--------------|--------|
| picoCTF | aloittelijoille suunnattu kilpailu ja harjoituskirjasto (Carnegie Mellon) | `picoctf.org` |
| OverTheWire | komentorivipohjaiset harjoitussarjat, myös binääritehtäviä | `overthewire.org` |
| pwn.college | yliopistotasoinen kurssimateriaali ja harjoitukset (Arizona State University) | `pwn.college` |
| CTFtime | kansainvälisten CTF-kilpailujen kalenteri ja tulokset | `ctftime.org` |

Harrastajat julkaisevat myös pieniä takaisinmallinnettaviksi
tarkoitettuja harjoitusohjelmia (*crackme*). Aja tuntemattoman tekijän
ohjelma vain eristetyssä virtuaalikoneessa.

Muiden ohjelmiin siirrytään vasta, kun oikeus on selvä: laillisen
käyttäjän oikeus tutkia ohjelmaa ja saavuttaa yhteentoimivuus
(luku 1), työnantajan tai asiakkaan kirjallinen toimeksianto tai
valmistajan haavoittuvuusohjelman säännöt.

## Jatkotaidot

*Laiteohjelmiston takaisinmallinnus* käsittelee laiteohjelmistokuvia,
ARM- ja Thumb-koodia sekä emulointia (QEMU, Unicorn).
*Haavoittuvuuksien analyysi ja torjunta* rakentuu tämän paketin
päälle: muistiturvallisuuden virheet, niiden löytäminen ja korjaaminen
sekä suojaukset, jotka rajaavat virheiden vaikutusta.
*Kääntäjätekniikka* syventää, miksi kääntäjä tuottaa näkemäsi koodin.

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
  tietokoneohjelmien oikeudellisesta suojasta (5 artiklan 3 kohta:
  tutkiminen; 6 artikla: dekompilointi).
- Tekijänoikeuslaki 404/1961, 25 j ja 25 k § (dekompilointi ja
  tutkiminen): finlex.fi.

## Lisenssi

Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0), myös esimerkit.

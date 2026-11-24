# Johdanto {.runko-johdanto}

*Takaisinmallinnus* (*reverse engineering*) on ohjelman toiminnan
selvittämistä ilman lähdekoodia: konekielestä, tiedostomuodoista,
liikenteestä ja ajonaikaisesta käytöksestä. Samoja taitoja tarvitaan
monessa tavallisessa työssä:

- **vianetsintä**, kun kaatumisraportti kertoo vain osoitteen tai kun
  kääntäjä on tuottanut jotain muuta kuin odotit
- **yhteentoimivuus**, kun laitteen tai vanhan ohjelman tiedostomuoto
  tai protokolla on dokumentoimaton
- **tietoturvatutkimus**, kun arvioit ohjelman, jonka toimittaja ei
  anna lähdekoodia, tai tarkistat, mitä päivitys oikeasti muutti
- **haittaohjelma-analyysi**, kun pitää selvittää, mitä tuntematon
  ohjelma tekee ja mihin se ottaa yhteyttä
- **oman koodin tarkastus**, kun haluat tietää, mitä optimoiva kääntäjä
  teki, tai varmistaa, ettei julkaisuun jäänyt salaisuuksia.

Tutoriaali opettaa työkalut ja ajattelutavan näihin tehtäviin. Jokainen
kohde on tämän paketin oma, itse käännetty ohjelma: lähdekoodi on
mukana, jotta päätelmät voi tarkistaa, mutta analyysi tehdään aina
käännetystä ohjelmasta.

## Lainsäädäntö ja etiikka

Takaisinmallinnus on laillista monessa tilanteessa, mutta ei kaikissa.
EU:n tietokoneohjelmadirektiivi (2009/24/EY) ja Suomen
tekijänoikeuslain 25 j ja 25 k § sallivat ohjelman laillisen käyttäjän

- tarkkailla, tutkia ja kokeilla ohjelman toimintaa sen
  periaatteiden selvittämiseksi tavallisen käytön aikana, ja
- *dekompiloida* ohjelman, kun se on välttämätöntä itsenäisesti
  luodun ohjelman yhteentoimivuuden saavuttamiseksi, eikä tietoa saa
  muuten. Saatua tietoa ei saa käyttää muuhun tarkoitukseen eikä
  samankaltaisen ohjelman tekemiseen.

Sopimusehto ei voi kieltää näitä oikeuksia. Muuhun käyttöön, kuten
kopiosuojauksen tai lisenssitarkistuksen kiertämiseen, poikkeukset
eivät ulotu, ja suojausten kiertäminen voi olla erikseen kiellettyä.
Tietoturvatutkimuksessa noudatetaan vastuullisen julkistamisen
käytäntöjä (*coordinated vulnerability disclosure*), ja vieraiden
järjestelmien testaamiseen tarvitaan aina lupa. Kun työ koskee
työnantajan tai asiakkaan ohjelmaa, sovi rajat kirjallisesti ennen
aloittamista.

Tämän tutoriaalin harjoitukset tehdään vain omille ohjelmille. Luvun
10 suojausten ohitukset ja paikkaukset kohdistuvat paketin omaan
esimerkkiohjelmaan, ja niiden tarkoitus on näyttää, miksi tällaiset
suojaukset eivät kestä: se on tärkeää tietää, kun omaa ohjelmaa
suunnitellaan.

## Mitä tutoriaali kattaa

Pääkohde on Linuxin x86-64 ja ELF-tiedostot. AArch64:ää ja RISC-V:tä
käsitellään vertailuna, laiteohjelmistot omana taitonaan (*Laiteohjelmiston
takaisinmallinnus*).

| Luku | Aihe | Työkalut |
|------|------|----------|
| 2 | x86-64-assemblyn lukeminen | `objdump` |
| 3 | Disassemblointi ja dekompilointi | `objdump`, radare2 |
| 4 | Kääntäjän tuottamat rakenteet | Python-analyysi |
| 5 | Optimoinnit konekielessä | `objdump`, Python |
| 6 | C++-ohjelmat | `c++filt`, `readelf`, gdb |
| 7 | Symbolittomat ohjelmat | `.eh_frame`, allekirjoitukset |
| 8 | Dynaaminen analyysi | gdb, strace, ltrace, `LD_PRELOAD` |
| 9 | Tiedostomuodot ja protokollat | heksavedos, entropia, Python |
| 10 | Obfuskointi ja sen purkaminen | Python, gdb |
| 11 | Kokonainen analyysi | kaikki edellä |
| 12 | Lopuksi | Ghidra, nyrkkisäännöt, lähteet |

Staattinen analyysi (luvut 2–7) lukee ohjelmaa ajamatta sitä. Se kattaa
kaikki polut, myös harvoin suoritetut, mutta vaatii tulkintaa.
Dynaaminen analyysi (luku 8) havainnoi ajossa olevaa ohjelmaa: arvot
ovat varmoja, mutta vain ajetut polut näkyvät. Käytännön työ vuorottelee
näiden välillä, kuten luvuissa 9–11.

## Esitiedot ja jatkotaidot

*Objektitiedostot, linkitys ja ABI* on tärkein esitieto: ELF:n osiot,
symbolit, relokaatiot, GOT ja PLT, C++:n nimien koristelu ja
`LD_PRELOAD`. Tässä tutoriaalissa niitä käytetään, mutta niitä ei
selitetä uudelleen. *Käyttöjärjestelmät* antaa järjestelmäkutsut ja
prosessit, joita strace näyttää, ja *Tietoturvan perusteet*
uhkamallinnuksen ja etiikan. *Assembly* opettaa RISC-V:n konekielen
kirjoittamisen; tässä luetaan x86-64:ää, ja luku 2 kokoaa tarvittavan.
*Kääntäjätekniikka* selittää, miksi kääntäjä tekee luvuissa 4 ja 5
näkyvät muunnokset.

Jatkotaitoja ovat *Laiteohjelmiston takaisinmallinnus* (laiteohjelmistokuvat,
ARM- ja Thumb-koodi, emulointi) ja *Haavoittuvuuksien analyysi ja
hyödyntäminen*.

## Työkalut ja esimerkit

Esimerkit on tehty Ubuntu 24.04:llä: GCC 14, binutils 2.42, gdb 15,
radare2 5.5, strace ja ltrace. Kehityskontti
(`.devcontainer/takaisinmallinnus`) sisältää ne. Ghidraa ei ole
Ubuntun paketeissa, joten sen käyttö esitellään luvussa 12 ja
esimerkit tehdään komentorivityökaluilla. Kaikki analyysit ovat
skriptejä, jotka voi ajaa uudelleen: hyvän takaisinmallinnustyön tulos
on toistettava, ei muistikuva siitä, mitä joskus näki ruudulla.

Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`. Siinä on
kohdeohjelman lähdekoodi, analyysiskriptit ja skripti `aja.sh`, joka
kääntää kohteen ja ajaa analyysit. `make testaa` ajaa kaikki
esimerkit ja vertaa tulosteita tiedostoihin `odotettu`. Tutoriaalin
tulosteet ovat noita tiedostoja.

Osoitteet vaihtelevat kääntäjän ja linkkerin version mukaan, joten
skriptit poistavat ne: `objdump`-tulosteessa hyppyjen kohteet näkyvät
muodossa `<funktio+0x22>` ja `rip`-suhteelliset siirtymät muodossa
`[rip+X]`, radare2:n tulosteessa osoitteet korvataan sanalla `OSOITE`.
Apufunktiot ovat tiedostossa `esimerkit/yhteinen.sh`:

```{.bash tiedosto="esimerkit/yhteinen.sh" osa="purku"}
```

Python-analyysit käyttävät yhteistä moduulia `esimerkit/tyokalut/purku.py`,
joka jäsentää `objdump`-tulosteen käskyiksi.

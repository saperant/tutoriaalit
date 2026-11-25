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

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen, omien
ohjelmien tutkimiseen ja luvalliseen ammattityöhön. Käytä tekniikoita
vain omiin ohjelmiisi tai kohteisiin, joihin sinulla on lain tai
kirjallisen luvan antama oikeus. Tämä on yleiskuvaus, ei oikeudellinen
neuvo, eivätkä tekijät vastaa materiaalin väärinkäytöstä.

Tämän tutoriaalin harjoitukset tehdään vain paketin omille, itse
käännetyille ohjelmille. Lukujen 8 ja 10 kokeet, joissa oman
esimerkkiohjelman tarkistus ohitetaan debuggerilla tai tiedostoa
muuttamalla, näyttävät, miksi asiakasohjelman omat tarkistukset eivät
ole suoja: se on tärkeää tietää, kun omaa ohjelmaa suunnitellaan.
Laillisia harjoituskohteita, kuten CTF-kilpailujen
takaisinmallinnustehtäviä, on lueteltu luvussa 12.

## Mitä tutoriaali kattaa

Pääkohde on Linuxin x86-64 ja ELF-tiedostot. AArch64:ää ja RISC-V:tä
käsitellään vertailuna, laiteohjelmistot omana taitonaan (*Laiteohjelmiston
takaisinmallinnus*).

| Luku | Aihe | Työkalut | Esimerkit |
|--|-----------------------|--------------------|--------------------|
| 2 | x86-64-assemblyn lukeminen | `objdump` | `01-x86` |
| 3 | Disassemblointi ja dekompilointi | `objdump`, radare2 | `02-purku` |
| 4 | Kääntäjän tuottamat rakenteet | Python-analyysi | `03-rakenteet` |
| 5 | Optimoinnit konekielessä | `objdump`, Python | `04-optimoinnit` |
| 6 | C++-ohjelmat | `c++filt`, `readelf`, gdb | `05-cpp` |
| 7 | Symbolittomat ohjelmat | `.eh_frame`, allekirjoitukset | `06-strip` |
| 8 | Dynaaminen analyysi | gdb, strace, ltrace, `LD_PRELOAD` | `07-gdb`, `08-jaljitys` |
| 9 | Tiedostomuodot ja protokollat | heksavedos, entropia, Python | `09-muoto`, `10-protokolla` |
| 10 | Obfuskointi ja sen purkaminen | Python, gdb | `11-xor`, `12-litistys`, `13-antidebug` |
| 11 | Kokonainen analyysi | kaikki edellä | `14-yhteentoimivuus` |
| 12 | Lopuksi | harjoituskohteet, lähteet | |

Staattinen analyysi (luvut 2–7) lukee ohjelmaa ajamatta sitä. Se kattaa
kaikki polut, myös harvoin suoritetut, mutta vaatii tulkintaa.
Dynaaminen analyysi (luku 8) havainnoi ajossa olevaa ohjelmaa: arvot
ovat varmoja, mutta vain ajetut polut näkyvät. Käytännön työ vuorottelee
näiden välillä, kuten luvuissa 9–11.

## Esitiedot ja rajaus

*Objektitiedostot, linkitys ja ABI* on tärkein esitieto: ELF:n osiot,
symbolit, relokaatiot, GOT ja PLT, C++:n nimien koristelu ja
`LD_PRELOAD`. Tässä tutoriaalissa niitä käytetään, mutta niitä ei
selitetä uudelleen. *Käyttöjärjestelmät* antaa järjestelmäkutsut ja
prosessit, joita strace näyttää, ja *Tietoturvan perusteet*
uhkamallinnuksen ja etiikan. *Assembly* opettaa RISC-V:n konekielen
kirjoittamisen; tässä luetaan x86-64:ää, ja luku 2 kokoaa tarvittavan.
*Kääntäjätekniikka* selittää, miksi kääntäjä tekee luvuissa 4 ja 5
näkyvät muunnokset.

Luku 6 olettaa lisäksi, että C++:n luokat, virtuaalifunktiot,
poikkeukset ja vakiokirjaston `std::string` ja `std::vector` ovat
tuttuja lähdekoodin tasolla (*Moderni C++*). Luku kertaa kunkin
mekanismin yhdellä virkkeellä, ja sen voi ohittaa: myöhemmät luvut
eivät nojaa siihen.

Rajauksia: kohteet ovat Linuxin ELF-ohjelmia, joten Windowsin PE- ja
macOS:n Mach-O-muotoa ei käsitellä. Haittaohjelma-analyysista
opetetaan menetelmät mutta ei oikeiden näytteiden käsittelyä; siihen
tarvitaan eristetty analyysiympäristö (luku 10). Muistivirheiden
löytäminen ja korjaaminen on oma taitonsa (*Haavoittuvuuksien analyysi
ja torjunta*), samoin laiteohjelmistot.

## Työkalut ja esimerkit

Esimerkit on tehty Ubuntu 24.04:llä: GCC 14, binutils 2.42, gdb 15,
radare2 5.5, strace ja ltrace. Kehityskontti
(`.devcontainer/takaisinmallinnus`) sisältää ne. Ghidraa ei ole
Ubuntun paketeissa, joten sen käyttö esitellään luvussa 3 tekstinä ja
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

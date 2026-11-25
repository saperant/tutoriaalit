# Vaihtoehdot ja täydentäjät

Kehityskontti ei ole ainoa tapa kuvata ympäristö koodina, eikä aina
paras. Välineet eroavat siinä, *mitä* ne eristävät: yhden kielen
paketit, työkalujen versiot, kaikki ohjelmat vai koko käyttöjärjestelmän.
Mitä enemmän eristetään, sitä toistettavampi ympäristö on ja sitä
raskaampi se on käyttää.

| Väline | Eristää | Toistettavuus | Hinta |
|------------------|----------------------------|----------------|------------------------------|
| venv, uv | Python-paketit | hyvä lukittuna | vain Python |
| asdf, mise | työkalujen versiot | kohtalainen | järjestelmäkirjastot koneelta |
| Nix | kaikki ohjelmat ja kirjastot | erittäin hyvä | jyrkkä oppimiskäyrä |
| kehityskontti | koko käyttäjätila | hyvä lukittuna | tarvitsee Dockerin |
| virtuaalikone | myös ydin | hyvä | raskas ja hidas |

## Kielikohtaiset virtuaaliympäristöt

Pythonin `venv` luo hakemiston, johon projektin paketit asennetaan
erilleen järjestelmän paketeista. Se ratkaisee yleisimmän ongelman,
kahden projektin ristiriitaiset riippuvuudet, eikä vaadi mitään
asennettavaa. `uv` tekee saman nopeammin, lukitsee riippuvuuksien
tarkat versiot tiedostoon ja asentaa tarvittaessa myös
Python-tulkin. Muilla kielillä on vastaavat: Noden `node_modules` ja
lukitustiedosto, Rustin Cargo, Go-moduulit.

Virtuaaliympäristö ei eristä mitään kielen ulkopuolelta: C-kirjastot,
tietokannat ja komentorivityökalut tulevat edelleen koneelta. Puhtaalle
yhden kielen projektille se silti riittää, ja se on kehityskontin
*sisälläkin* oikea tapa asentaa projektin riippuvuudet.

## Versionhallitsimet: asdf ja mise

`asdf` ja sen nopeampi seuraaja `mise` asentavat työkaluista
projektikohtaiset versiot. Projektin juuressa oleva tiedosto `.tool-versions` kertoo
versiot, ja oikea versio on käytössä, kun hakemistoon siirrytään:

```text
python 3.12.7
nodejs 24.1.0
```

Tämä on kevyt ratkaisu, kun ongelma on nimenomaan ”kenellä on mikäkin
Node-versio”. Työkalut kuitenkin ladataan tai käännetään isäntäkoneelle,
joten käyttöjärjestelmän kirjastot vaikuttavat tulokseen, eikä väline
auta, jos projekti tarvitsee tietokannan tai järjestelmäpaketteja.

## Nix

Nix on paketinhallinta, jossa jokainen paketti rakennetaan eristettynä
ja tallennetaan polkuun, joka sisältää tiivisteen sen kaikista
syötteistä. Projektin ympäristö kuvataan tiedostossa (`flake.nix`), ja
lukitustiedosto kiinnittää jokaisen riippuvuuden tarkan version aina
C-kirjastoihin asti. Komento `nix develop` avaa kuoren, jossa juuri nuo
ohjelmat ovat käytössä.

Nix on tämän luvun välineistä toistettavin, eikä se tarvitse kontteja:
ohjelmat ajetaan suoraan isäntäkoneella, joten levy ja editori toimivat
täydellä nopeudella. Hinta on oma kieli ja ajattelutapa, jonka
oppiminen vie aikaa, ja Windowsissa se toimii vain WSL:n kautta. Nixiä
ja kontteja voi myös yhdistää: kehityskontin kuva rakennetaan Nixillä.

## Virtuaalikoneet

Kontti jakaa isäntäkoneen ytimen. Jos projekti tarvitsee toisen
ytimen, ytimen moduuleja tai toisen käyttöjärjestelmän, tarvitaan
virtuaalikone. Vagrant kuvaa virtuaalikoneen tiedostona samaan tapaan
kuin `devcontainer.json` kuvaa kontin. Virtuaalikone käynnistyy
hitaammin ja vie enemmän muistia, joten sitä käytetään vain, kun kontti
ei riitä. Eron taustat käsittelee taito *Virtualisointi*.

## Miten valita

- **Yhden kielen kirjasto tai pieni työkalu:** kielen oma
  virtuaaliympäristö ja lukitustiedosto.
- **Useita kieliä tai järjestelmäpaketteja, tiimissä eri
  käyttöjärjestelmiä:** kehityskontti. Se on myös helpoin tarjota
  ulkopuolisille: tämän kokoelman lukija pääsee kokeilemaan selaimessa.
- **Tiukka toistettavuusvaatimus tai tiimi osaa Nixin:** Nix.
- **Ytimen tai käyttöjärjestelmän kehitys:** virtuaalikone.

Välineet eivät sulje toisiaan pois. Tavallinen yhdistelmä on
kehityskontti, jonka sisällä kielen oma väline asentaa projektin
riippuvuudet lukitustiedostosta: kontti tuo tulkin, kääntäjät ja
järjestelmäkirjastot, lukitustiedosto kirjastojen tarkat versiot.

## Käytännössä

- **Valitse kevein väline, joka ratkaisee ongelman.** Kontti Python-
  skriptille, jolla on kaksi riippuvuutta, on liikaa.
- **Lukitustiedosto on tärkeämpi kuin väline.** Ilman lukittuja
  versioita mikään näistä ei ole toistettava.
- **Yksi virallinen tapa.** Projektissa saa olla useita tapoja, mutta
  yksi niistä on se, jonka CI ajaa ja jonka toimivuus taataan.
- **Mittaa uuden kehittäjän ensimmäinen tunti.** Jos kloonauksesta
  vihreisiin testeihin kuluu yli tunti, ympäristön kuvaus kaipaa työtä.

## Itsearviointi

- Osaat kertoa, mitä virtuaaliympäristö, versionhallitsin, Nix,
  kehityskontti ja virtuaalikone kukin eristävät.
- Osaat valita projektille sopivan välineen ja perustella valinnan.
- Osaat selittää, miksi lukitustiedosto tarvitaan välineestä
  riippumatta.

# IP-XACT

IP-XACT (IEEE 1685) on XML-muoto, jolla kuvataan kokonainen IP-lohko:
sen portit ja niiden ryhmittely väyläliitännöiksi, parametrit,
muistikartat ja rekisterit sekä lähdetiedostot. Taidossa
*SoC-integraatio* kerrottiin, mihin sitä käytetään: IP-toimittaja
toimittaa lohkon IP-XACT-kuvauksineen, ja integraatiotyökalu kytkee
lohkot väyläliitäntöjen tasolla, kokoaa muistikartan ja tuottaa
ylimmän tason RTL:n. Tässä luvussa katsotaan kuvauksen rakennetta ja
käsitellään sitä ohjelmallisesti.

## Rakenne

Jokainen IP-XACT-kuvaus tunnistetaan neljällä tiedolla: toimittaja,
kirjasto, nimi ja versio (*VLNV*, vendor–library–name–version).
Kuvaukset viittaavat toisiinsa VLNV:llä, joten saman IP:n eri versiot
voivat olla samassa luettelossa.

| Kuvaus | Sisältö |
|----------------------|-------------------------------------------------|
| `component` | yksi IP-lohko: portit (`model`), väyläliitännät (`busInterfaces`), muistikartat (`memoryMaps`), parametrit ja tiedostot (`fileSets`) |
| `busDefinition` | väylätyyppi, esimerkiksi APB4, ja sen ominaisuudet |
| `abstractionDefinition` | väylän signaalit ja niiden suunnat isännällä ja orjalla |
| `design` | komponenttien instanssit ja niiden väliset kytkennät |
| `designConfiguration` | designin valinnat, esimerkiksi mikä näkymä kustakin komponentista käytetään |

Väyläliitäntä (`busInterface`) kertoo, että komponentin portit
`s_apb_psel`, `s_apb_paddr` jne. toteuttavat APB4-väylän orjapuolen,
ja kuvaa jokaisen portin väylän loogiseen signaaliin. Tämän tiedon
avulla integraatiotyökalu kytkee isännän ja orjan yhdellä
kytkennällä, eikä signaaleja tarvitse kytkeä yksitellen. Väylien
määrittelyt (`busDefinition` ja `abstractionDefinition`) ovat yleensä
väylän ylläpitäjän julkaisemia; Accellera ja Arm julkaisevat
määrittelyt esimerkiksi AMBA-väylille.

Muistikartta on IP-XACT:n osa, joka vastaa SystemRDL-kuvausta:
`memoryMap` sisältää osoitelohkoja (`addressBlock`), joissa on
rekistereitä ja kenttiä. Ajastimen `STATUS`-rekisteri PeakRDL:n
viemänä:

```{.xml tiedosto="esimerkit/tuotettu/otteet/ipxact_status.xml"}
```

Pääsy on kuvattu kolmella elementillä: perusoikeus (`access`),
kirjoituksen vaikutus (`modifiedWriteValue`, tässä `oneToClear`) ja
luvun vaikutus (`readAction`). `volatile` kertoo, että laitteisto voi
muuttaa arvoa. Luvut kirjoitetaan IP-XACT 2014:ssä
SystemVerilogin tapaan (`'h0`), mikä on otettava huomioon, kun
tiedostoa luetaan omalla ohjelmalla.

Standardista on käytössä kolme versiota: 1685-2009, 1685-2014 ja
1685-2022. Ne eroavat nimiavaruudeltaan ja osin rakenteeltaan, ja
työkalut tukevat niitä eri tavoin. PeakRDL kirjoittaa oletuksena
version 2014 ja valitsimella `--standard 2009` vanhemman.

## XML:n käsittely Pythonilla

IP-XACT on tavallista XML:ää nimiavaruuksineen, joten sen lukemiseen
riittää standardikirjaston `xml.etree.ElementTree`. Ensin xmllint
tarkistaa, että tiedosto on hyvin muodostettu. Skeemaa vastaan
validointi vaatisi Accelleran julkaisemat skeematiedostot, joita ei
ole tämän ympäristön paketeissa. CI:ssä ne kannattaa hakea kerran ja
tallentaa projektiin.

```{.python tiedosto="esimerkit/09-ipxact.py" osa="lue"}
```

## Vienti ja tuonti

PeakRDL-ipxact osaa myös tuoda IP-XACT-kuvauksen. Tuotu kuvaus
käännetään samaksi malliksi kuin SystemRDL, joten kaikki generaattorit
toimivat sille. Esimerkki `09-ipxact.py` vie kuvauksen ja tuo sen
takaisin, ja vertaa mallia alkuperäiseen:

```{.python tiedosto="esimerkit/09-ipxact.py" osa="tuonti"}
```

```{.tuloste tiedosto="esimerkit/09-ipxact.odotettu"}
```

Osoitteet, bitit, pääsytavat ja nollausarvot säilyvät, mutta
laitteiston käyttäytyminen katoaa: IP-XACT:ssa ei ole vastinetta
SystemRDL:n ominaisuuksille `hwset`, `counter`, `intr`, `singlepulse`,
`swmod` ja `swacc`. Ne ovat RTL:n toteutustietoa, eivät ohjelmiston
näkymä rekistereihin. Siksi IP-XACT ei sovellu rekisterilohkon
lähteeksi, jos lohko tuotetaan generaattorilla. Työkalut säilyttävät
lisätietoa toimittajakohtaisissa laajennuksissa
(`vendorExtensions`), mutta niitä toinen työkalu ei ymmärrä.

Tämä on tavallinen tilanne muotoja muunnettaessa. Muunnos kannattaa
aina testata edestakaisin, jotta tiedetään, mitä matkalla katoaa.

## Työkalut

Avoimen lähdekoodin työkaluista Kactus2 on graafinen IP-XACT-editori ja
integraatiotyökalu, jolla voi rakentaa designeja komponenteista ja
tuottaa niistä ylimmän tason RTL:n. Kaupallisissa
EDA-ympäristöissä IP-XACT on IP-katalogien ja integraatiotyökalujen
tiedonsiirtomuoto. Monet FPGA-valmistajien IP-paketointityökalut
käyttävät IP-XACT:ia tai sen johdannaista IP-lohkojen
kuvaamiseen.

## Käytännössä

- **SystemRDL rekisterien lähteeksi, IP-XACT tiedonsiirtoon.**
  IP-XACT:iin viety muistikartta kulkee integraatiotyökaluille ja
  toimittajille, mutta laitteiston käyttäytyminen ei kulje.
- **Testaa muunnokset edestakaisin.** Vienti ja tuonti takaisin
  paljastavat, mitä tietoa muoto ei kanna.
- **Valitse IP-XACT-versio vastaanottajan mukaan.** Työkalujen tuki
  vaihtelee, ja versiot eroavat nimiavaruudeltaan.
- **Tallenna skeemat projektiin.** Validointi skeemaa vastaan CI:ssä
  ei saa riippua verkkoyhteydestä.

## Itsearviointi

- Osaat kertoa IP-XACT:n kuvaustyypit (komponentti, väylämäärittely,
  abstraktiomäärittely, design) ja VLNV-tunnisteen merkityksen.
- Osaat lukea IP-XACT-komponentin muistikartan ja kentän pääsyn
  (`access`, `modifiedWriteValue`, `readAction`).
- Osaat käsitellä IP-XACT-tiedostoa Pythonilla nimiavaruuksineen.
- Osaat viedä SystemRDL-kuvauksen IP-XACT:iin, tuoda sen takaisin ja
  kertoa, mitä tietoa muunnoksessa katoaa.

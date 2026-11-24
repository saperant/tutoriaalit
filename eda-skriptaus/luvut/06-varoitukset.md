# Varoitukset ja laatuportit

Lint, simulaattori ja synteesi tuottavat varoituksia. Suurin osa
niistä on aiheellisia: katkeava leveys, käyttämätön signaali,
salvaksi syntetisoituva `always`-lohko. Osa on tiedettyjä ja
hyväksyttyjä, kuten tuotantotestin tulo, joka kytketään vasta piirin
ylätasolla. Jos hyväksytyt varoitukset jäävät lokiin muiden joukkoon,
kukaan ei enää lue lokia, ja uusi aiheellinen varoitus hukkuu satojen
vanhojen sekaan.

Siksi varoitukset luokitellaan. Jokaisella koodilla on vakavuus.
Hyväksytyt varoitukset kirjataan listaan perusteluineen, ja
*laatuportti* hylkää ajon, jos siinä on yksikin varoitus, jota listassa
ei ole. Tavoitteena on, että hyväksyttyjen varoitusten lista on lyhyt
ja jokainen sen kohta on jonkun tarkistama.

## Vakavuus

```{.python tiedosto="esimerkit/vuo/varoitukset.py" osa="vakavuus"}
```

Luokat ovat projektin päätös, eivät työkalun. Verilator kutsuu kaikkea
varoitukseksi, mutta projektissa salpa (`LATCH`) tai usean ajurin
signaali (`MULTIDRIVEN`) on käytännössä aina virhe. Käyttämätön signaali
taas on useimmiten tyylikysymys. Työkalun rajoitukset, kuten Icaruksen
`sorry`-ilmoitukset, ovat oma luokkansa. Ne kertovat, että simulaatio
voi poiketa standardin semantiikasta, mutta eivät kerro suunnittelun
virheestä.

Tuntematon koodi on oletuksena varoitus eikä tyyli. Uusi työkaluversio
tuo uusia koodeja, ja ne on parempi nähdä kuin piilottaa.

## Sallitut varoitukset

Hyväksytty varoitus kirjataan tiedostoon, jossa on koodi, tiedosto,
viestin tunnistava lauseke, peruste ja viimeinen voimassaolopäivä:

```{.toml tiedosto="esimerkit/asetukset/sallitut.toml"}
```

Peruste on pakollinen, koska ilman sitä listasta tulee kaatopaikka.
Voimassaolopäivä pakottaa tarkistamaan hyväksynnän uudelleen: jos
pariteettibitin piti tulla käyttöön versiossa 2, sen käyttämättömyys ei
ole enää hyväksyttävää version 2 jälkeen. Listan lukija tarkistaa
pakolliset kentät heti, ettei virheellinen kohta hyväksy mitään
vahingossa. Kohdan tietue `Sallittu` tietää itse, koskeeko se
varoitusta:

```{.python tiedosto="esimerkit/vuo/varoitukset.py" osa="koskee"}
```

Kohta tunnistaa varoituksen koodin, tiedoston ja viestin perusteella,
ei rivinumeron. Rivinumero muuttuu, kun tiedostoon lisätään rivi
yläpuolelle, ja silloin jokainen hyväksyntä vanhenisi turhaan. Lauseke
`'testi'` taas tunnistaa juuri tämän signaalin varoituksen eikä muita
saman tiedoston käyttämättömiä signaaleja.

## Luokittelu ja laatuportti

```{.python tiedosto="esimerkit/vuo/varoitukset.py" osa="luokittele"}
```

Luokittelu tuottaa neljä listaa. Uudet varoitukset ja vanhentuneet
hyväksynnät kaatavat laatuportin. Voimassa olevat hyväksynnät
raportoidaan mutta eivät kaada. Tarpeettomat hyväksynnät ovat
listan kohtia, joihin mikään varoitus ei osunut: varoitus on korjattu,
mutta hyväksyntä on jäänyt. Ne raportoidaan, jotta ne voi poistaa.
Unohdettu hyväksyntä hyväksyisi myöhemmin samannäköisen uuden
varoituksen kenenkään huomaamatta.

Ohjainlohkossa on tarkoituksella muutama lint-varoitus:

```{.systemverilog tiedosto="esimerkit/rtl/ohjain.sv"}
```

Esimerkki ajaa Verilatorin lintin ohjainlohkolle ja luokittelee
varoitukset. Päivämäärä on kiinteä, jotta tulos ei muutu ajan
kuluessa:

```{.python tiedosto="esimerkit/06-varoitukset.py" osa="lint"}
```

```{.tuloste tiedosto="esimerkit/06-varoitukset.odotettu"}
```

Ohjainlohkossa on neljä varoitusta. Katkeava leveys rivillä 16 on uusi,
ja se onkin aiheellinen: kahdeksanbittinen summa sijoitetaan
nelibittiseen tilaan. Rivin 10 varoitus `summa[7:4]` johtuu samasta
virheestä. Tuotantotestin tulo rivillä 7 on hyväksytty. Pariteettibitin
hyväksyntä vanheni lokakuussa, joten se kaataa portin, kunnes joku
joko poistaa bitin, ottaa sen käyttöön tai uusii hyväksynnän uudella
perusteella. Laskurin vanha hyväksyntä on tarpeeton, koska varoitusta
ei enää tule.

## Hyväksyntä koodissa vai listassa

Verilatorissa, kuten useimmissa lint-työkaluissa, varoituksen voi
kytkeä pois myös lähdekoodissa kommentilla
`/* verilator lint_off UNUSEDSIGNAL */`. Luvun 9 rekisterigeneraattori
tekee näin väylän datatulolle, jonka kaikkia bittejä ei käytetä.
Kummallakin tavalla on paikkansa:

| Tapa | Hyvä | Huono |
|--------------|--------------------------|--------------------|
| kommentti koodissa | näkyy koodin lukijalle, liikkuu koodin mukana | työkalukohtainen, ei voimassaoloaikaa, hajallaan |
| keskitetty lista | perusteet ja päivämäärät yhdessä paikassa, katselmoitavissa | erillään koodista |

Nyrkkisääntö: koodiin kirjoitetaan hyväksyntä, joka on rakenteellisesti
aina totta, kuten generaattorin tuottama leveä väylä. Tilapäiset ja
perusteltavat hyväksynnät kuuluvat listaan.

Toinen tapa hallita perintökoodin varoituksia on *räikkä* (ratchet):
varoitusten määrä tallennetaan, eikä se saa kasvaa. Jokainen korjaus
laskee rajaa, eikä uusia voi tulla. Räikkä on hyvä siirtymäkeino,
kun vanhassa koodissa on satoja varoituksia. Lopullinen tila on silti
lista, jossa jokaisella kohdalla on peruste.

## Käytännössä

- **Laatuportti jokaiseen ajoon.** Uusi varoitus kaataa ajon heti,
  kun se syntyy, eikä vasta kuukausia myöhemmin katselmoinnissa.
- **Hyväksynnällä on omistaja, peruste ja päivämäärä.** Lista
  katselmoidaan kuten koodi.
- **Tunnista viestistä, älä rivinumerosta.** Lauseke kohdistetaan
  signaalin nimeen tai muuhun pysyvään tunnisteeseen.
- **Tarpeettomat hyväksynnät pois.** Raportoi ne ja poista ne
  säännöllisesti.
- **Työkalun päivitys on oma muutoksensa.** Kun Verilator päivitetään,
  uudet varoitukset käsitellään samassa muutoksessa, ei
  ominaisuustyön sivussa.

## Itsearviointi

- Osaat luokitella työkalujen varoitukset projektin omiin
  vakavuusluokkiin.
- Osaat ylläpitää sallittujen varoitusten listaa, jossa on perusteet
  ja voimassaoloajat, ja tunnistaa tarpeettomat hyväksynnät.
- Osaat rakentaa laatuportin, joka hylkää uudet varoitukset ja
  vanhentuneet hyväksynnät.
- Osaat perustella, milloin hyväksyntä kuuluu koodiin ja milloin
  keskitettyyn listaan.

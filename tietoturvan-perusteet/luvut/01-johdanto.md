# Johdanto {.runko-johdanto}

Tietoturva tarkoittaa sitä, että järjestelmä tekee sen, mitä sen
kuuluu, eikä mitään muuta, silloinkin kun joku yrittää tarkoituksella
saada sen toimimaan toisin. Tavallinen ohjelmistovirhe ilmenee
satunnaisella syötteellä. Tietoturvavirheen löytää hyökkääjä, joka
etsii juuri sen syötteen, jolla ohjelma pettää. Siksi tietoturvassa ei
riitä, että ohjelma toimii tavallisilla syötteillä: on mietittävä, mitä
tapahtuu pahimmalla mahdollisella syötteellä.

Tämä tutoriaali on taitopuun tietoturva-alueen yhteinen perusta. Se
opettaa käsitteet, ajattelutavan ja yleisimmät virheluokat niin, että
lukija tunnistaa ne omasta koodistaan ja osaa korjata ne. Syventävät
taidot jatkavat tästä:

| Taito | Mitä se syventää |
|-------|------------------|
| *Kryptografia* | salausmenetelmien toiminta ja oikea käyttö |
| *Web-sovellusten tietoturva* | selain- ja palvelinhyökkäykset, OAuth, istunnot |
| *Tietoturva kehitystyössä* | salaisuudet, toimitusketju, CI-tarkistukset |
| *Sulautettujen järjestelmien tietoturva* | luottamusketju, avainten säilytys laitteessa |
| *Palveluarkkitehtuurin tietoturva* | nollaluottamus, palvelujen identiteetit |
| *Takaisinmallinnus* ja *Haavoittuvuudet* | konekielitason analyysi, muistivirheet |

## Kenelle

Lukija osaa ohjelmoida ja tuntee tietoverkkojen perusteet (taidot
*Ohjelmoinnin perusteet* ja *Tietoverkot*). Esimerkit ovat Pythonia,
mutta virheluokat ja korjaukset ovat samat kaikissa kielissä.
C-kielen muistivirheet, kuten puskurin ylivuoto, käsitellään taidossa
*Haavoittuvuudet*.

## Miten esimerkit on rakennettu

Lähes jokaisessa luvussa haavoittuva ja korjattu versio ovat
rinnakkain. Haavoittuva versio ajetaan testissä, ja tuloste näyttää
hyökkäyksen onnistuvan. Näin lukija näkee, että virhe on todellinen
eikä teoreettinen, ja että korjaus todella estää sen.

Esimerkit tarkistetaan työkaluilla, joita ammattilaiset käyttävät
samaan tarkoitukseen:

- **ruff** sääntöineen `S` (flake8-bandit) etsii tyypillisiä
  tietoturvavirheitä staattisesti, esimerkiksi `shell=True`-kutsuja ja
  merkkijonoista koottuja SQL-lauseita. Kun haavoittuvuus on
  esimerkissä tarkoituksella, rivillä on perusteltu `noqa`-kommentti.
- **mypy --strict** tarkistaa tyypit. Tyyppivirhe on usein myös
  tietoturvavirhe: `None` siellä, missä odotettiin käyttäjää.
- Jokainen esimerkki ajetaan, ja tulostetta verrataan odotettuun.

Esimerkit käyttävät vain Pythonin standardikirjastoa, ja ne toimivat
Python 3.12:lla ja uudemmilla. Niitä voi ajaa paikallisesti tai
tutoriaalin kehityskontissa.

## Mitä tietoturva ei ole

Tietoturvaa ei saavuteta yhdellä tuotteella, kuten palomuurilla tai
virustorjunnalla, eikä salaamalla kaikkea. Se on ominaisuus, joka
syntyy suunnittelusta, toteutuksesta ja ylläpidosta yhdessä. Heikoin
lenkki ratkaisee: vahva salaus ei auta, jos varmuuskopio on julkisessa
pilvisäilössä tai ylläpitäjän salasana on `admin`.

Tietoturva ei myöskään ole pelkkää estämistä. Kaikkea ei voi estää,
joten järjestelmän on myös havaittava hyökkäykset ja toivuttava niistä.
Luku *Lokitus, havaitseminen ja poikkeamat* käsittelee tätä puolta.

## Etiikka ja laki ensin

Tutoriaalin hyökkäysesimerkit kohdistuvat esimerkin omaan, paikalliseen
dataan. Toisen järjestelmään tunkeutuminen ilman lupaa on Suomessa
rikos (tietomurto, rikoslaki 38 luku 8 §), vaikka tarkoitus olisi hyvä.
Omia taitoja harjoitellaan omissa ympäristöissä ja niille tehdyissä
harjoitusalustoissa. Luku *Lainsäädäntö ja etiikka* kertoo, miten
löydetystä haavoittuvuudesta ilmoitetaan vastuullisesti.

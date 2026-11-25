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
| *Takaisinmallinnus* | käännetyn ohjelman toiminnan selvittäminen konekielestä |
| *Haavoittuvuuksien analyysi ja torjunta* | muistivirheet, niiden löytäminen ja suojaukset |
| *Laiteohjelmiston takaisinmallinnus* | laiteohjelmistokuvan analyysi ja laitteen suojaaminen |

## Esitiedot ja rajaus

Lukija osaa ohjelmoida ja tuntee tietoverkkojen perusteet (taidot
*Ohjelmoinnin perusteet (Python)* ja *Tietoverkot*). Verkoista
tarvitaan vain peruskäsitteet: HTTP-pyyntö, TLS-yhteys ja palvelujen
välinen kutsu. Esimerkit ovat Pythonia, mutta virheluokat ja korjaukset
ovat samat kaikissa kielissä.

Tutoriaali ei käsittele seuraavia aiheita muuten kuin yleiskuvana:

- **Salausmenetelmien toiminta.** Luku *Kryptografia käyttäjän
  näkökulmasta* kertoo, mitä kukin työkalu takaa. Algoritmit ja
  protokollat ovat taidossa *Kryptografia*.
- **Selaimen suojausmallit** (XSS, CSRF, evästeet, OAuth) ovat taidossa
  *Web-sovellusten tietoturva*.
- **C-kielen muistivirheet**, kuten puskurin ylivuoto. Luvussa *Syöte,
  polut ja sarjallistus* on niistä lyhyt yleiskuva, ja varsinainen
  käsittely on taidossa *Haavoittuvuuksien analyysi ja torjunta*.
- **Verkon suojaukset**, kuten palomuurit ja segmentointi, ovat
  taidossa *Verkkoinfrastruktuuri*.

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
Python 3.12:lla ja uudemmilla. Yksittäisen esimerkin voi ajaa
sellaisenaan, ja koko paketin tarkistukset ajetaan paketin
juurihakemistossa:

```text
python3 esimerkit/07-sql.py   # yksi esimerkki
make testaa                   # rakenne, ruff, mypy ja kaikkien esimerkkien ajo
make pdf                      # tämä dokumentti ja pikaopas
```

Kehityskontissa (`.devcontainer/tietoturvan-perusteet`) Python, ruff ja
mypy ovat valmiina. Kontin avaaminen neuvotaan taidossa
*Kehitysympäristöt ja Dev Containers*.

## Mitä tietoturva ei ole

Tietoturvaa ei saavuteta yhdellä tuotteella, kuten palomuurilla tai
virustorjunnalla, eikä salaamalla kaikkea. Se on ominaisuus, joka
syntyy suunnittelusta, toteutuksesta ja ylläpidosta yhdessä. Heikoin
lenkki ratkaisee: vahva salaus ei auta, jos varmuuskopio on julkisessa
pilvisäilössä tai ylläpitäjän salasana on `admin`.

Tietoturva ei myöskään ole pelkkää estämistä. Kaikkea ei voi estää,
joten järjestelmän on myös havaittava hyökkäykset ja toivuttava niistä.
Luku *Lokitus, havaitseminen ja poikkeamat* käsittelee tätä puolta.

## Vastuulauseke: etiikka ja laki ensin

Materiaali on tarkoitettu opetukseen ja oman koodin parantamiseen.
Tutoriaalin hyökkäysesimerkit kohdistuvat esimerkin omaan, paikalliseen
dataan, ja jokaisen rinnalla on korjaus.

- **Kokeile vain omiin ohjelmiisi ja järjestelmiisi** tai kohteisiin,
  joihin sinulla on omistajan kirjallinen lupa. Oman palvelun
  testaamiseen kannustetaan: juuri niin virheet löytyvät ennen
  hyökkääjää.
- **Luvaton tunkeutuminen on rikos.** Toisen järjestelmään
  tunkeutuminen ilman lupaa on Suomessa rangaistavaa (tietomurto,
  rikoslaki 38 luku 8 §), vaikka tarkoitus olisi hyvä.
- **Harjoitteluun on laillisia ympäristöjä.** Luku *Lainsäädäntö ja
  etiikka* nimeää harjoitusalustoja ja kertoo, miten löydetystä
  haavoittuvuudesta ilmoitetaan vastuullisesti.

Tekijät eivät vastaa materiaalin väärinkäytöstä.

# Kehitysympäristöt

Kehittäjän kone on hyökkääjälle houkutteleva kohde: siellä on
lähdekoodi, pääsy repositorioihin, usein tunnukset testi- tai jopa
tuotantoympäristöihin ja selain kirjautuneine istuntoineen. Jaetuissa
kehitysympäristöissä (testipalvelimet, yhteiset tietokannat,
pilvitilit) on samat riskit moninkertaisina. Tämä luku käsittelee
kolmea asiaa: toistettavat ja rajatut ympäristöt, pääsynhallinta
jaetuissa ympäristöissä ja tuotantodata kehityksessä.

## Toistettava ympäristö kehityskontissa

Kehityskontti (*dev container*) kuvaa kehitysympäristön koodina:
kuvan, työkalut versioineen ja asetukset. Tietoturvan kannalta siitä on
kolme hyötyä:

- **Toistettavuus.** Kaikilla on samat työkaluversiot. "Toimii minun
  koneellani" -ongelmat vähenevät, ja tietoturvatarkistukset (ruff,
  ShellCheck, skannerit) ovat kaikilla samat.
- **Eristys.** Projektin riippuvuudet ja niiden asennusskriptit ajetaan
  kontissa eivätkä kehittäjän koko käyttäjätilillä. Haitallinen
  riippuvuus näkee kontin, ei kotihakemistoa SSH-avaimineen.
- **Katselmoitavuus.** Ympäristön muutokset kulkevat pull requestin
  kautta kuten muukin koodi.

Eristys on kuitenkin vain niin hyvä kuin asetukset. Yleisimmät virheet
ovat oikeuksien antaminen "varmuuden vuoksi" ja salaisuuksien
kirjoittaminen asetustiedostoon. Ne voi tarkistaa koneellisesti:

```{.python tiedosto="esimerkit/04-kontti.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-kontti.odotettu"}
```

Havainnot selityksineen:

| Asetus | Riski | Parempi |
|--------|-------|---------|
| `image: ...:latest` | kuva vaihtuu huomaamatta, myös kaapattuna | kiinnitys tiivisteeseen (`@sha256:...`), päivitys pull requestilla |
| `--privileged` | kontti näkee isännän laitteet ja voi ladata ydinmoduuleja | vain tarvittavat oikeudet (`--cap-add=NET_ADMIN`) |
| Dockerin soketti kontissa | kuka tahansa kontissa voi käynnistää isännällä root-kontin | Docker-in-Docker tai rootless-ratkaisu |
| salaisuus `containerEnv`-kentässä | päätyy repositorioon ja kaikille | `${localEnv:NIMI}` tai salaisuusvarasto |
| ajo root-käyttäjänä | tiedostot ja prosessit ylioikeuksin | tavallinen käyttäjä (`remoteUser`) |

Osa tämän repositorion omista kehityskonteista tarvitsee lisäoikeuksia:
verkkotaitojen esimerkit rakentavat verkkoja Linuxin
nimiavaruuksiin ja tarvitsevat siksi `NET_ADMIN`-oikeuden. Oikeus on
annettu vain niille konteille, jotka sitä tarvitsevat, ja syy on
kirjattu tutoriaaliin. Tämä on vähimpien oikeuksien periaate
käytännössä.

## Jaetut kehitysympäristöt

Testi- ja kehitysympäristöt ovat usein heikoimmin suojattuja:
oletustunnukset, laaja pääsy kaikille kehittäjille, ei valvontaa. Silti
ne ovat usein samassa verkossa tai samalla pilvitilillä kuin tuotanto.
Hyvät käytännöt:

- **Erillinen tili tai projekti jokaiselle ympäristölle.** Kehitystilin
  tunnuksilla ei pääse tuotantotiliin. Pilvissä tili tai projekti on
  vahvin raja.
- **Henkilökohtaiset tunnukset ja kertakirjautuminen.** Ei jaettuja
  ylläpitäjätunnuksia; pääsy päättyy automaattisesti, kun henkilö
  lähtee.
- **Väliaikaiset ympäristöt.** Pull requestia varten luotu ja sen
  sulkeutuessa poistettu ympäristö ei kerää unohtuneita tunnuksia ja
  dataa.
- **Tuotantopääsy poikkeuksena.** Pääsy pyydetään tehtävää varten,
  myönnetään määräajaksi ja kirjataan (*just-in-time access*).

## Tuotantodata kehityksessä

Tuotannon tietokannan kopio kehitysympäristössä on tietosuoja-asetuksen
näkökulmasta henkilötietojen käsittelyä, ja ympäristö on usein huonommin
suojattu kuin tuotanto. Ensisijainen ratkaisu on **synteettinen data**,
joka on luotu skripteillä. Jos aitoja jakaumia tarvitaan, data
muunnetaan ennen kopiointia:

| Tieto | Esimerkki | Muunnos |
|-------|-----------|---------|
| suora tunniste | nimi, sähköposti, henkilötunnus | korvataan tai pseudonymisoidaan |
| tunniste, jolla liitetään | asiakasnumero | avaimellinen tiiviste (liitokset säilyvät) |
| epäsuora tunniste | syntymäaika, postinumero, ammatti | yleistetään (vuosi, alue) |
| vapaa teksti | asiakaspalvelun muistiinpanot | poistetaan |
| hyötydata | ostot, summat | säilyy |

```{.python tiedosto="esimerkit/04-anonymisointi.py" osa="muunnos"}
```

```{.python tiedosto="esimerkit/04-anonymisointi.py" osa="kanonymiteetti"}
```

```{.tuloste tiedosto="esimerkit/04-anonymisointi.odotettu"}
```

**k-anonymiteetti** kertoo, kuinka monen henkilön joukkoon yksilö
hukkuu epäsuorien tunnisteiden perusteella. Arvo 1 tarkoittaa, että
joku on yksilöitävissä, vaikka nimi on poistettu: ainoa vuonna 1991
syntynyt asiakas postinumerossa 00530 tunnistetaan helposti. Yleistyksen
jälkeen jokainen yhdistelmä kuuluu vähintään kahdelle henkilölle.

Kaksi varoitusta:

- **Pseudonymisoitu data on yhä henkilötietoa** tietosuoja-asetuksen
  mukaan, jos avain on olemassa. Avain kuuluu vain muunnosajolle, ja sen
  hävittäminen tekee pseudonyymeistä käytännössä anonyymejä.
- **Pelkkä tiiviste ilman avainta ei suojaa.** Asiakasnumeroiden tai
  henkilötunnusten avaruus on pieni, joten tiivisteet voi laskea
  kaikille mahdollisille arvoille. Siksi esimerkki käyttää HMAC:ia.

## Käytännössä

- **Kehitysympäristö koodina.** Kehityskontti tai vastaava kuvaus
  repositoriossa, kuvat kiinnitettyinä ja muutokset katselmoituina.
- **Vähimmät oikeudet myös kehityksessä.** Ei `--privileged`-kontteja,
  ei Dockerin sokettia, ei root-käyttäjää ilman syytä.
- **Ympäristöt erillään.** Kehityksen tunnuksilla ei pääse tuotantoon,
  ja tuotantopääsy on määräaikainen ja kirjattu.
- **Ei tuotantodataa kehitykseen.** Synteettinen data ensin;
  muunnettu data vain perustellusti ja k-anonymiteetti tarkistettuna.
- **Kehittäjän kone on osa hyökkäyspintaa.** Levyn salaus,
  päivitykset, SSH-avaimet salasanalla tai laiteavaimella, selaimen
  laajennukset harkiten.

## Itsearviointi

- Osaat kertoa, mitä kehityskontti tuo tietoturvaan ja mitkä asetukset
  vievät hyödyn.
- Osaat tarkistaa kehitysympäristön asetukset vähimpien oikeuksien
  näkökulmasta.
- Osaat järjestää jaettujen kehitysympäristöjen pääsynhallinnan.
- Osaat muuntaa tuotantodatan kehityskäyttöön ja tarkistaa
  k-anonymiteetin.

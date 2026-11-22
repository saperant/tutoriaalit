# Taitopuun ylläpito

Taitopuu on tiedostossa `opintopolut/taitopuu.toml`. Kaikki muutokset
tehdään siihen. Tämä dokumentti ja hakemiston `README.md` generoidaan
siitä.

## Uusi taito

Taito lisätään `[[taito]]`-taulukkona:

```toml
[[taito]]
id = "esimerkki-taito"          # tunniste: pienet kirjaimet, numerot, -
nimi = "Esimerkkitaito"
alue = "jarjestelmat"           # jonkin [[alue]]-taulukon id
kuvaus = "Yhden virkkeen kuvaus."
edellyttaa = ["c-kieli"]        # vain välittömät esitiedot
aiheet = ["aihe 1", "aihe 2", "aihe 3"]
laajuus = 5                     # op, 1–15
testaus = "miten esimerkit testataan"
roadmap = ["c"]                 # roadmap.sh-polkujen nimiä
amk = "Vastaava opintojakso"
```

Kun taidolle on kirjoitettu tutoriaali, siihen lisätään kenttä
`tutoriaali`, jonka arvo on tutoriaalin hakemisto repositoriossa.
Hakemiston nimi on sama kuin taidon tunniste.

Jokaisen taidon on kuuluttava vähintään yhteen rooliin, joko jonkin
tavoitteen esitietona tai valinnaisena taitona. Jos taito ei sovi
mihinkään rooliin, se on merkki siitä, että joko taito on tarpeeton tai
roolit eivät kata kaikkia tarpeita.

## Uusi rooli

Rooli lisätään `[[rooli]]`-taulukkona. Kenttä `tavoitteet` luettelee
taidot, jotka roolin on hallittava; niiden esitiedot lisätään polkuun
automaattisesti. Tavoitteisiin ei merkitä taitoa, joka on jo toisen
tavoitteen esitieto. Kenttä `valinnaiset` luettelee syventäviä taitoja,
jotka eivät kuulu pakolliseen polkuun.

## Tarkistukset

```text
make testaa    # tarkistaa taitopuun ja sen, että README on ajan tasalla
make readme    # generoi README:n uudelleen
make pdf       # generoi tämän dokumentin
```

Tarkistin hylkää taitopuun, jos

- tunniste toistuu tai viittaus osoittaa tuntemattomaan alueeseen,
  taitoon tai roadmap.sh-polkuun,
- esitietoverkossa on sykli,
- taidolla on tarpeeton esitieto, joka sisältyy jo toisen esitiedon
  esitietoihin,
- rooli luettelee tavoitteen, joka on jo toisen tavoitteen esitieto, tai
  valinnaisen taidon, joka kuuluu jo pakolliseen polkuun,
- taito ei kuulu yhteenkään rooliin, tai
- valmiiksi merkityn tutoriaalin hakemistoa ei ole.

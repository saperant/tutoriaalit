# Johdanto {.runko-johdanto}

Järjestelmäsuunnittelu (*system design*) on palvelun arkkitehtuurin
valitsemista ennen kuin koodia on paljon: montako palvelinta tarvitaan,
mihin tieto tallennetaan, mitä pidetään välimuistissa, mitkä työt
tehdään jonon kautta ja mitä tapahtuu, kun jokin osa hajoaa. Päätökset
on tehtävä arvioiden varassa, ja niitä on vaikea perua, kun palvelu on
tuotannossa ja datan määrä kasvaa. Siksi suunnittelija tarvitsee
mittaluokkia, malleja ja kokeita, ei pelkkiä kaavioita.

Tämä tutoriaali käsittelee suurten palvelujärjestelmien rakennuspalikat
yksi kerrallaan ja kokoaa ne lopuksi yhdeksi palveluksi:

1. arviot: kuinka paljon pyyntöjä, dataa ja kaistaa (luku 2),
2. suorituskyky: latenssi, persentiilit, jonot ja kapasiteetti (luku 3),
3. kuormantasaus ja palvelimen kaatuminen (luku 4),
4. avainten jako solmuille: konsistentti hajautus ja osiointi (luku 5),
5. välimuistit, invalidointi ja välimuistiryntäys (luku 6),
6. tietokannan replikointi ja lukureplikoiden viive (luku 7),
7. viestijonot ja vähintään kerran -käsittely (luku 8),
8. ylikuorma: nopeusrajoitus ja uudelleenyritysmyrskyt (luku 9),
9. saatavuuden laskeminen ja virhebudjetti (luku 10),
10. havaittavuus: metriikat, persentiilit ja jäljitys (luku 11),
11. kokonainen suunnitteluharjoitus: lyhytosoitepalvelu (luku 12).

## Menetelmä

Suunnittelutehtävä etenee samassa järjestyksessä riippumatta siitä,
onko kyse työhaastattelun harjoituksesta vai oikeasta palvelusta:

| Vaihe | Kysymys | Tulos |
|-------|---------|-------|
| Vaatimukset | Mitä palvelu tekee, kenelle, millä laadulla? | toiminnot, SLO:t, rajaukset |
| Arviot | Kuinka paljon? | pyyntöä/s, tallennus, kaista, muisti |
| Rajapinta ja tietomalli | Mitä kutsutaan, mitä tallennetaan? | API, taulut, avaimet |
| Arkkitehtuuri | Mitkä osat ja miten ne kytkeytyvät? | kaavio, tietovuot |
| Pullonkaulat | Mikä hajoaa ensin, kun kuorma kymmenkertaistuu? | mitoitus, varautuminen |

Vaiheet eivät ole vesiputous. Arvio voi kumota arkkitehtuurin (metatiedot
mahtuvat yhteen tietokantaan, joten osiointia ei tarvita), ja pullonkaula
voi palauttaa vaatimuksiin (onko vanhentunut luku hyväksyttävä?).
Olennaista on, että jokainen valinta perustellaan luvulla tai
kompromissilla, ja kompromissi nimetään.

## Esimerkkijärjestelmät

Esimerkit eivät ole kaavioita vaan ohjelmia, jotka ajetaan. Ne kuuluvat
kolmeen ryhmään:

- **Laskelmat ja simulaatiot** (Python): arviot, jonomallit,
  kuormantasausalgoritmit, osiointi ja uudelleenyritysmyrsky.
  Simulaatiot käyttävät kiinteää siementä, joten tulos on joka ajolla
  sama.
- **Oikeat palvelut prosesseina**: HAProxy, Redis ja PostgreSQL
  ajetaan oikeina ohjelmina, ja omat palvelut on kirjoitettu Pythonin
  vakiokirjastolla (`http.server`). PostgreSQLiin yhdistetään
  psycopg-kirjastolla, Redisiin pienellä omalla asiakkaalla.
- **Säiliökuvaukset**: luvun 12 palvelu on kuvattu myös Compose-
  tiedostona ja Dockerfilenä, jotka tarkistetaan skeemaa ja
  tyylisääntöjä vasten.

Tuotannossa palvelut olisivat kontteja (taito *Säiliöt ja
pilvi-infrastruktuuri*). Testeissä kontteja ei voi aina ajaa, esimerkiksi
kehityskontin sisällä, joten esimerkkien apukirjasto käynnistää saman
kokoonpanon tavallisina prosesseina. Jokainen esimerkki saa oman
väliaikaishakemiston ja käyttöjärjestelmän antamat vapaat portit, kaikki
kuuntelee vain osoitetta 127.0.0.1, ja palvelut pysäytetään aina
lopuksi, myös virheen sattuessa:

```{.python tiedosto="esimerkit/jarjestelma/ymparisto.py" osa="redis"}
```

## Mitä on testattu

| Osa | Testaus |
|-----|---------|
| Python-koodi | ruff, mypy --strict, pytest-yksikkötestit |
| Laskelmat ja simulaatiot | tuloste verrataan tallennettuun |
| HAProxy-, Redis- ja PostgreSQL-kokeet | ajetaan oikeilla palveluilla; tuloste verrataan tallennettuun |
| HAProxyn asetukset | `haproxy -c` |
| Compose ja Dockerfile | Compose-skeema, yamllint, hadolint |
| Prometheuksen hälytyssäännöt | yamllint (Prometheusta ei ajeta) |

Ajoitukset vaihtelevat koneen kuorman mukaan, joten verrattavissa
tulosteissa ei ole kestoja eikä suoritustehoja. Niissä on laskureita,
osumasuhteita ja vertailujen tuloksia ("synkroninen kirjoitus odotti
replikaa: True"). Simulaatioiden latenssit ovat simuloitua aikaa, ja ne
ovat samat joka ajolla.

Esimerkit ajetaan komennolla:

```text
make -C esimerkit                     # kaikki tarkistukset ja esimerkit
make -C esimerkit luku06/ryntays      # yksi esimerkki
```

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Hajautetut järjestelmät* (replikointi,
kvoorumit, konsistenssimallit, konsensus, CAP ja PACELC, hajautetut
transaktiot) ja *SQL ja relaatiotietokannat* (indeksit, transaktiot ja
eristystasot). Niitä ei toisteta: tässä katsotaan, miten samat ilmiöt
näkyvät, kun järjestelmä rakennetaan valmiista osista.

Lähellä olevia aiheita käsitellään muissa taidoissa:

| Aihe | Taito |
|------|-------|
| aikarajat, uudelleenyritys, katkaisija, saga, outbox | *Palveluarkkitehtuurit* |
| HTTP-palvelun rakenne, REST, idempotenssi | *Taustapalvelut* |
| kontit, Compose, Kubernetes | *Säiliöt ja pilvi-infrastruktuuri* |
| SLI, SLO ja hälytysten hygienia | *Palvelinympäristöt* |
| jonoteoria ja mallien validointi | *Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen* |
| soketit, aikakatkaisut, vastapaine | *Verkko-ohjelmointi* |
| mittaaminen ja profilointi | *Suorituskyvyn analyysi ja optimointi* |

Taitopuussa taitoon liittyy roadmap.sh-sivuston polku *System Design*.
Tutoriaali ei perustu sen sisältöön; polun nimi kertoo vain, mihin
aiheeseen taito kuuluu. Lähteet ovat luvun 13 lopussa.

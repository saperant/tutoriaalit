# Valvonta ja palvelutasot

Valvonnan tehtävä on kertoa, toimiiko palvelu käyttäjien kannalta, ja
herättää ihminen vain silloin, kun on tehtävä jotain heti. Huono
valvonta epäonnistuu molemmissa: se ei huomaa käyttäjille näkyvää
vikaa, mutta hälyttää kymmeniä kertoja yössä asioista, jotka korjaantuvat
itsestään.

## Metriikat, lokit ja jäljet

| Signaali | Mitä se kertoo | Esimerkkejä työkaluista |
|----------|----------------|-------------------------|
| Metriikat | Lukuja ajan funktiona: pyyntöjä, virheitä, viiveitä, levyn täyttöastetta | Prometheus, Grafana |
| Lokit | Yksittäiset tapahtumat yksityiskohtineen | journald, Loki, Elasticsearch |
| Jäljet | Yhden pyynnön kulku palveluiden läpi | OpenTelemetry, Jaeger |

Palvelulle kerätään vähintään neljä kultaista signaalia: **viive**,
**liikenne**, **virheet** ja **kyllästyminen** (resurssien täyttöaste).
Laitteelle kerätään käyttö, kyllästyminen ja virheet (USE-menetelmä):
suoritin, muisti, levyt ja verkko.

Lokit kerätään keskitetysti: koneelta kadonnut tai murtautujan
poistama loki on hyödytön. Keskitetyssä palvelussa lokeja voi
myös yhdistää: sama korrelaatiotunniste kulkee pyynnön mukana kaikkien
palveluiden lokeihin.

## Saatavuus

Saatavuus ilmoitetaan "yhdeksiköinä". Jokainen lisäyhdeksikkö
kymmenkertaistaa vaatimuksen:

```{.python tiedosto="esimerkit/10-saatavuus.py" osa="kaavat"}
```

```{.python tiedosto="esimerkit/10-saatavuus.py" osa="esimerkki"}
```

```{.tuloste tiedosto="esimerkit/10-saatavuus.odotettu"}
```

Kolme sarjaan kytkettyä osaa, joista jokainen on yli 99,5 %
saatavilla, antaa yhteensä vain 99,35 %. Sovelluspalvelimen
monistaminen nostaa kokonaisuuden lähelle sen heikoimman jäljellä
olevan osan, tietokannan, tasoa. Lasku olettaa vikojen olevan
riippumattomia; yhteinen sähkönsyöttö, verkko tai ohjelmistopäivitys
rikkoo oletuksen.

## SLI, SLO ja SLA

- **SLI** (service level indicator) on mittari käyttäjän kokemuksesta,
  esimerkiksi onnistuneiden pyyntöjen osuus tai alle 300 ms:ssa
  vastattujen pyyntöjen osuus.
- **SLO** (objective) on tavoite: 99,9 % pyynnöistä onnistuu 30 päivän
  aikana.
- **SLA** (agreement) on sopimus asiakkaan kanssa ja seuraukset, jos
  taso alittuu. SLA asetetaan löysemmäksi kuin sisäinen SLO, jotta
  ongelmaan ehditään reagoida ennen sopimusrikkomusta.

**Virhebudjetti** on SLO:n kääntöpuoli: 99,9 %:n tavoite sallii
0,1 % epäonnistumisia, eli noin 43 minuuttia täyttä katkoa kuukaudessa.
Budjetti on yhteinen päätöksenteon väline: kun sitä on jäljellä,
kehitys voi julkaista nopeasti; kun se on käytetty, keskitytään
luotettavuuteen.

## Hälytykset virhebudjetista

Kiinteä raja ("virheitä yli 1 %") hälyttää lyhyistä piikeistä, joilla ei
ole väliä, ja ohittaa hitaan vuodon, joka kuluttaa budjetin päivissä.
Parempi peruste on budjetin *palamisnopeus*: kuinka monta kertaa
nopeammin budjetti kuluu kuin tasaisella tahdilla:

```{.python tiedosto="esimerkit/10-virhebudjetti.py" osa="palaminen"}
```

```{.python tiedosto="esimerkit/10-virhebudjetti.py" osa="tilanteet"}
```

```{.tuloste tiedosto="esimerkit/10-virhebudjetti.odotettu"}
```

Palamisnopeus 14,4 tunnin ajan kuluttaa 2 % kuukauden budjetista;
se on syy herättää päivystäjä. Nopeus 6 kuuden tunnin ajan kuluttaa
5 %; se on tiketti seuraavalle työpäivälle. Lyhyt ikkuna (5 min tai
1 h) varmistaa, että ongelma on yhä päällä: ohimennyt piikki ei
hälytä, vaikka pitkän ikkunan keskiarvo olisi koholla. Menetelmä on
peräisin Googlen SRE-käsikirjasta, ja sama sääntö kirjoitetaan
Prometheusin hälytyssäännöksi PromQL-kielellä.

## Hälytysten hygienia

- **Jokaiseen hälytykseen on toimenpide.** Jos hälytykselle ei voi
  tehdä mitään, se on mittari kojelaudalla, ei hälytys.
- **Hälytä oireista, tutki syitä.** Käyttäjille näkyvä virheiden kasvu
  herättää; korkea suoritinkuorma näkyy kojelaudalla.
- **Ohjekirja (runbook)** jokaiselle hälytykselle: mitä tarkistaa ja
  miten korjata.
- **Hälytysten määrää seurataan.** Päivystäjä, joka saa kymmenen
  turhaa hälytystä viikossa, ei reagoi yhteentoista oikeaan.

## Käytännössä

- **Mittaa käyttäjän kokemusta.** SLI lasketaan kuormantasaajalta tai
  asiakkaalta, ei palvelimen sisältä.
- **Kirjoita SLO:t ja virhebudjetit auki** ja sovi, mitä budjetin
  loppuminen tarkoittaa.
- **Hälytä palamisnopeudesta**, monen ikkunan säännöllä.
- **Keskitetyt lokit ja korrelaatiotunnisteet**, säilytys ja
  pääsynhallinta sovittuna.
- **Valvo valvontaa.** Valvontajärjestelmän oma katko on hiljainen;
  "kuolleen miehen kytkin" -hälytys laukeaa, jos säännöllistä
  signaalia ei tule.

## Itsearviointi

- Osaat valita palvelulle ja laitteelle kerättävät metriikat ja kertoa
  metriikoiden, lokien ja jälkien erot.
- Osaat laskea sarjaan ja rinnakkain kytkettyjen osien saatavuuden ja
  sallitun katkon.
- Osaat määritellä SLI:n, SLO:n ja virhebudjetin ja selittää SLA:n
  eron niihin.
- Osaat kirjoittaa palamisnopeuteen perustuvan hälytyssäännön ja
  perustella sen hyödyt kiinteään rajaan verrattuna.

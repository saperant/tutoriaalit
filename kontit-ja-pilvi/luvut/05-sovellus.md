# Sovellus konttiin sopivaksi

Kontteja käynnistetään, pysäytetään, monistetaan ja siirretään
koneelta toiselle ilman ennakkovaroitusta. Sovellus, joka olettaa
pysyvän koneen, paikallisen levyn tai asetustiedoston tietyssä
hakemistossa, toimii kontissa huonosti. *Twelve-factor app* -periaatteet
(Herokun insinöörien kokoamat, 12factor.net) kuvaavat, millainen
sovellus toimii hyvin tällaisessa ympäristössä. Tässä luvussa ovat
ne, joilla on suurin merkitys konteille.

## Asetukset ympäristöstä

Sama kuva ajetaan kehityksessä, testissä ja tuotannossa; erot tulevat
ympäristömuuttujista. Käyntilaskurin rajapinnan kaikki asetukset
luetaan käynnistyksessä:

```{.python tiedosto="esimerkit/sovellus/api.py"}
```

Kuvaan ei rakenneta ympäristökohtaisia asetuksia eikä salaisuuksia.
Jos tuotannon tietokannan osoite on kuvassa, testattu kuva ei ole sama
kuin tuotantoon menevä. Compose antaa ympäristömuuttujat
`environment`-kentällä (luku 6), Kubernetes ConfigMapista ja Secretistä
(luku 8).

## Lokit tapahtumavirtana

Sovellus kirjoittaa lokinsa vakiotulosteeseen yhtenä rivinä
tapahtumaa kohden eikä huolehdi tiedostoista, kierrätyksestä tai
lähetyksestä. Ajoympäristö kerää virran: `docker logs`, Kubernetesin
`kubectl logs` ja keskitetty lokipalvelu (Loki, Elasticsearch,
pilvipalveluiden lokipalvelut). Rakenteinen muoto (JSON) on helppo
suodattaa kentittäin:

```{.python tiedosto="esimerkit/sovellus/yhteinen.py" osa="loki"}
```

Luvun 6 testissä api-kontin viimeinen lokirivi on
`{"taso": "INFO", "viesti": "sammutettu", "palvelu": "api"}`.

Kertakäyttöisyys (*disposability*) tarkoittaa, että prosessi
käynnistyy nopeasti ja sammuu hallitusti SIGTERMistä (luku 3). Kontteja käsitellään kuin
karjaa, ei kuin lemmikkejä: yksittäistä konttia ei korjata, vaan se
korvataan uudella.

## Tila taustapalveluihin

Kontin oma tiedostojärjestelmä katoaa kontin mukana. Pysyvä tila
kuuluu taustapalveluun (tietokanta, objektitallennus, välimuisti) tai
vähintään volyymiin. Käyntilaskurissa api on tilaton ja laskuri
tilallinen: apia voi ajaa monta rinnakkain, laskuria ei.

Laskuri kirjoittaa arvonsa niin, että kaatuminen kesken kirjoituksen ei
jätä tiedostoon puolikasta arvoa:

```{.python tiedosto="esimerkit/sovellus/laskuri.py" osa="kasvata"}
```

`os.replace` vaihtaa tiedoston yhdellä järjestelmäkutsulla; joko vanha
tai uusi arvo on levyllä, ei koskaan sekasotku. Oikeassa palvelussa
tila olisi tietokannassa, joka hoitaa samanaikaisuuden ja varmuuskopiot.

## Elävyys ja valmius

Ajoympäristö kysyy palvelulta kahta eri asiaa:

| Kysymys | Päätepiste | Jos ei | Saa riippua muista palveluista |
|---------|------------|--------|-------------------------------|
| Elääkö prosessi? (*liveness*) | `/terveys` | kontti käynnistetään uudelleen | ei |
| Voiko palvelu ottaa liikennettä? (*readiness*) | `/valmius` | liikenne ohjataan muualle | kyllä |

Erottelu on tärkeä. Jos elävyystarkistus kysyisi laskurin tilaa,
laskurin katko käynnistäisi kaikki api-kontit uudelleen, eikä se auta
mitään: uudet kontit eivät saa laskuria toimimaan. Valmiustarkistus sen
sijaan saa riippua laskurista, koska ilman sitä palvelu ei pysty
vastaamaan oikein. Rajapinnan käsittelijä yllä toteuttaa molemmat.

## Testit oikeita palvelimia vastaan

Palvelut testataan käynnistämällä oikeat HTTP-palvelimet satunnaisiin
portteihin. Testi kattaa myös vikatilanteen: kun laskuri pysähtyy,
valmius vaihtuu tilaan 503, mutta elävyys pysyy kunnossa:

```{.python tiedosto="esimerkit/sovellus/test_palvelut.py"}
```

Testit ajetaan sekä suoraan (`python3 -m unittest`) että kuvan
`testit`-vaiheessa, joten ne todistavat, että sovellus toimii myös
kuvan Pythonilla.

## Muut periaatteet lyhyesti

- **Riippuvuudet ilmoitettuina ja eristettyinä.** Kuva sisältää kaiken;
  ajoympäristöstä ei oleteta mitään asennettua.
- **Portin sidonta.** Palvelu kuuntelee itse porttia eikä tarvitse
  ulkoista sovelluspalvelinta. Kontissa se kuuntelee kaikkia
  liitäntöjä (`0.0.0.0`); rajaus tehdään portin julkaisussa.
- **Rinnakkaisuus prosesseina.** Skaalaus tehdään lisäämällä kontteja,
  ei kasvattamalla yhtä.
- **Kehityksen ja tuotannon samankaltaisuus.** Sama kuva, samat
  taustapalvelutyypit (PostgreSQL myös kehityksessä, ei SQLite), sama
  käyttöönottotapa.
- **Ylläpitotehtävät kertaluonteisina prosesseina.** Migraatiot ja
  eräajot ajetaan samasta kuvasta omina kontteinaan (Kubernetesin
  `Job`).

## Käytännössä

- **Konfiguraatio ympäristöstä, oletukset koodissa.** Oletusarvo
  kehityskäyttöön, ympäristömuuttuja kaikille muille. Puuttuva
  pakollinen asetus kaataa käynnistyksen heti selvällä virheellä.
- **Lokit rakenteisina stdoutiin.** Ei lokitiedostoja kontin sisällä:
  ne katoavat kontin mukana ja täyttävät levyn.
- **Tilattomat palvelut, tilalliset erikseen.** Tilattoman palvelun
  voi skaalata ja siirtää vapaasti. Tilallinen palvelu tarvitsee
  pysyvän levyn ja huolellisemman käyttöönoton (StatefulSet, luku 8).
- **Elävyys halvaksi, valmius rehelliseksi.** Elävyystarkistus ei
  koskaan riipu muista palveluista; valmiustarkistus kertoo, pystyykö
  palvelu oikeasti palvelemaan.

## Itsearviointi

- Osaat muuttaa sovelluksen lukemaan asetuksensa ympäristöstä ja
  kirjoittamaan lokinsa rakenteisina vakiotulosteeseen.
- Osaat toteuttaa hallitun sammutuksen ja selittää, miksi se on
  tärkeä jatkuvissa käyttöönotoissa.
- Osaat erottaa elävyys- ja valmiustarkistuksen ja kertoa, mitä
  kumpikin saa tarkistaa.
- Osaat kertoa, mihin palvelun pysyvä tila kuuluu ja miksi tilaton
  palvelu on helppo skaalata.

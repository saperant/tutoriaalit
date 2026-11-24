# Kubernetes: asetukset, tila ja tuotantokunto

Edellisen luvun Deployment käynnistää podit. Tuotannossa tarvitaan
lisäksi asetukset ja salaisuudet, koettimet, resurssirajat,
tietoturvarajaukset, pysyvä tallennus, ulkoinen liikenne ja säännöt
huoltojen ja kuormanvaihteluiden varalle. Tämä luku käy läpi
käyntilaskurin loput manifestit.

## ConfigMap ja Secret

```{.yaml tiedosto="esimerkit/k8s/10-asetukset.yaml"}
```

ConfigMap ja Secret ovat avain–arvo-pareja, jotka annetaan podille
ympäristömuuttujina (`envFrom`, `env`) tai tiedostoina volyymissa.
Secret on erillinen tyyppi pääsynhallinnan vuoksi: sen lukuoikeuden voi
rajata RBAC:llä tiukemmin, ja klusterin voi määrätä salaamaan sen
etcd:ssä. Muuten Secret on vain base64-koodattu, ei salattu: sitä ei
saa tallentaa versionhallintaan selväkielisenä. Vaihtoehdot:

- **External Secrets Operator** hakee arvot salaisuusvarastosta
  (Vault, pilvipalvelun Secret Manager) ja luo Secretit klusteriin.
- **Sealed Secrets** ja **SOPS** salaavat arvot niin, että salattu
  tiedosto voi olla versionhallinnassa ja vain klusteri avaa sen.

Ympäristömuuttujana annettu asetus luetaan vain podin käynnistyessä.
Asetuksen muutos ei siis näy käynnissä oleviin podeihin, ellei niitä
käynnistetä uudelleen; luvun 9 Helm-kaavio hoitaa sen tiivisteellä.

## Koettimet, resurssit ja tietoturva

Deploymentin konttikuvaus jatkuu koettimilla ja rajoituksilla:

```{.yaml tiedosto="esimerkit/k8s/20-api.yaml" osa="tarkistukset"}
```

**Koettimet** (*probes*) vastaavat luvun 5 kysymyksiin. Valmiuskoetin
(`readinessProbe`) ottaa podin palvelun kuormantasaukseen ja pois siitä;
elävyyskoetin (`livenessProbe`) käynnistää jumiutuneen kontin uudelleen.
Hitaasti käynnistyvälle sovellukselle lisätään käynnistyskoetin
(`startupProbe`), jottei elävyyskoetin tapa sitä kesken käynnistyksen.

**Resurssit.** Pyyntö (*request*) on se, mitä ajoittaja varaa podille
solmulta; raja (*limit*) on se, mitä pod saa enintään käyttää.

| Pyynnöt ja rajat | QoS-luokka | Muistipulassa |
|------------------|-----------|---------------|
| pyyntö = raja kaikille | Guaranteed | poistetaan viimeisenä |
| pyynnöt asetettu | Burstable | keskellä |
| ei mitään | BestEffort | poistetaan ensimmäisenä |

Muistiraja kannattaa asettaa aina, koska ylitys tappaa vain kyseisen
kontin (luku 2). Suoritinrajaa moni jättää tarkoituksella pois: raja
hidastaa palvelua silloinkin, kun solmulla olisi vapaata suoritinaikaa,
ja pyyntö riittää takaamaan osuuden.

**Tietoturvakonteksti.** `runAsNonRoot`, `allowPrivilegeEscalation:
false`, `readOnlyRootFilesystem: true` ja kaikkien
*capability*-oikeuksien pudotus ovat restricted-profiilin vaatimuksia
(luku 7). Kirjoitettavaa tilaa tarvitseva sovellus saa volyymin
(`emptyDir` väliaikaiselle, PersistentVolumeClaim pysyvälle).

## StatefulSet ja pysyvä levy

Laskurilla on tila, joten se on StatefulSet:

```{.yaml tiedosto="esimerkit/k8s/30-laskuri.yaml"}
```

- Podeilla on pysyvät nimet (`laskuri-0`, `laskuri-1`, …), ja ne
  käynnistetään ja päivitetään järjestyksessä.
- `volumeClaimTemplates` luo jokaiselle podille oman
  PersistentVolumeClaimin, jonka klusterin tallennusluokka toteuttaa
  levyksi (pilvessä verkkolevy). Levy säilyy, kun pod luodaan uudelleen,
  myös toisella solmulla.
- `fsGroup: 10001` antaa käyttäjälle kirjoitusoikeuden levyyn: sama
  ongelma kuin Composen volyymissa (luku 3), eri ratkaisu.

Tietokannat kannattaa yleensä ostaa hallittuna palveluna tai ajaa
niille tehdyllä operaattorilla (esim. CloudNativePG PostgreSQLille).
StatefulSet hoitaa levyt ja nimet, mutta ei varmuuskopioita,
replikointia eikä versiopäivityksiä.

## Ingress ja verkkopolitiikka

Ulkoinen HTTP-liikenne tulee Ingressin kautta. Ingress-ohjain (esim.
ingress-nginx, Traefik) on klusterissa ajettava välityspalvelin, joka
toteuttaa säännöt ja TLS:n:

```{.yaml tiedosto="esimerkit/k8s/40-verkko.yaml" osa="ingress"}
```

Uudempi Gateway API (`Gateway`, `HTTPRoute`) jakaa saman tehtävän
infrastruktuurin ja sovellustiimien kesken ja tukee painotettua
reititystä; uusissa klustereissa se on Ingressin seuraaja.

Oletuksena jokainen pod voi ottaa yhteyttä jokaiseen. Verkkopolitiikka
rajaa liikenteen; tässä laskuriin pääsee vain api:

```{.yaml tiedosto="esimerkit/k8s/40-verkko.yaml" osa="verkkopolitiikka"}
```

Verkkopolitiikka toimii vain, jos klusterin verkko-osa (CNI, esim.
Calico tai Cilium) toteuttaa sen.

## Saatavuus ja skaalaus

```{.yaml tiedosto="esimerkit/k8s/50-saatavuus.yaml"}
```

- **PodDisruptionBudget** estää huoltotoimia (solmun tyhjennys,
  klusterin päivitys) poistamasta liikaa podeja kerralla.
- **HorizontalPodAutoscaler** muuttaa replikoiden määrää mittarin
  mukaan. Prosentti lasketaan suhteessa suoritinpyyntöön, joten
  skaalaus toimii vain, jos pyyntö on asetettu. Kun HPA on käytössä,
  Deploymentin `replicas`-kenttää ei pidä asettaa käyttöönotossa, tai
  jokainen käyttöönotto palauttaa replikat kiinteään arvoon (luvun 9
  kaavio jättää sen pois).

## Käytännöt koodina

Manifestien rakenteen tarkistaa skeema, mutta "kontti ei saa ajaa
rootina" tai "kuvalla on oltava kiinteä versio" ovat organisaation
sääntöjä. Ne kirjoitetaan koodiksi, joka ajetaan putkessa ja
klusterissa. Tuotannossa tähän käytetään Kyvernoa, OPA Gatekeeperia
tai Conftestia; esimerkkien `politiikka.py` näyttää periaatteen
Pythonilla:

```{.python tiedosto="esimerkit/politiikka.py" osa="saannot"}
```

Edellisen kappaleen manifestit läpäisevät tarkistuksen. Tämä kelvollinen,
mutta huolimaton Deployment ei:

```{.yaml tiedosto="esimerkit/k8s-huono/deployment.yaml"}
```

```{.tuloste tiedosto="esimerkit/k8s-huono/politiikka.odotettu"}
```

Jokainen rivi on todellinen riski: `latest` vaihtuu huomaamatta,
rajaton muisti kaataa naapurit, ilman koettimia rikkinäinen pod saa
liikennettä, ja root-kontti on murtautujan helpoin reitti solmulle.

## Käytännössä

- **Asetukset ConfigMapiin, salaisuudet salaisuusvarastoon.** Secret
  ei ole salaus. Versionhallintaan menee vain salattu muoto tai viittaus.
- **Jokaiselle kontille pyynnöt, muistiraja ja koettimet.** Ilman
  pyyntöjä ajoittaja ei osaa sijoittaa podeja, ilman rajaa yksi vuoto
  kaataa solmun, ilman koettimia rikkinäinen pod saa liikennettä.
- **Restricted-profiili oletukseksi.** Poikkeukset tehdään tietoisesti
  ja nimiavaruuskohtaisesti.
- **Tila hallittuun palveluun tai operaattorille.** StatefulSet on
  rakennuspalikka, ei tietokannan ylläpitäjä.
- **Rajaa verkko.** Oletuksena kaikki puhuvat kaikille; politiikka
  tekee murtautujan liikkumisesta klusterissa vaikeaa.
- **Säännöt koodiksi.** Sama tarkistus putkeen (palaute heti) ja
  klusterin hyväksyntään (ei ohituksia).

## Itsearviointi

- Osaat antaa podille asetukset ja salaisuudet ja kertoa, miksi Secret
  ei yksin suojaa salaisuutta.
- Osaat määrittää koettimet, resurssipyynnöt ja -rajat sekä
  tietoturvakontekstin ja selittää QoS-luokat.
- Osaat ajaa tilallisen palvelun StatefulSetillä ja kertoa, mitä se ei
  tee puolestasi.
- Osaat tuoda ulkoisen liikenteen Ingressillä, rajata sisäisen
  liikenteen verkkopolitiikalla ja määrittää PodDisruptionBudgetin ja
  automaattisen skaalauksen.
- Osaat kirjoittaa organisaation säännöt koodiksi, joka tarkistaa
  manifestit ennen käyttöönottoa.

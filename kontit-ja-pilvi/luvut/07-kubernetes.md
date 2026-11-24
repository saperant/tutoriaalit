# Kubernetes: podit, Deploymentit ja palvelut

Compose ajaa kontteja yhdellä koneella. Kubernetes ajaa niitä
koneiden joukossa (*klusterissa*): se päättää, millä koneella kukin
kontti ajetaan, käynnistää kaatuneet uudelleen, siirtää ne pois
vikaantuneelta koneelta, jakaa liikenteen ja vaihtaa versiot ilman
katkoa. Kubernetes on konttien käyttöjärjestelmä pilvessä, ja kaikki
suuret pilvipalvelut tarjoavat sen hallittuna palveluna (EKS, AKS, GKE).

## Deklaratiivinen tila ja ohjaussilmukat

Kubernetesille ei anneta komentoja ("käynnistä kolme konttia"), vaan
kuvaus halutusta tilasta ("tätä palvelua ajetaan kolme kopiota").
Kuvaukset tallennetaan klusterin tietokantaan (etcd) API-palvelimen
kautta. *Ohjaimet* (*controller*) vertaavat jatkuvasti todellista tilaa
haluttuun ja korjaavat eroa: jos pod kuolee, ReplicaSet-ohjain luo
uuden. Sama malli toistuu kaikkialla Kubernetesissa ja myös luvun 9
GitOpsissa ja luvun 10 infrastruktuurissa koodina.

| Osa | Tehtävä |
|-----|---------|
| API-palvelin | ainoa rajapinta klusterin tilaan; todennus ja tarkistukset |
| etcd | hajautettu avain–arvo-tietokanta, jossa tila on |
| ajoittaja (*scheduler*) | valitsee podille solmun resurssien ja sääntöjen mukaan |
| ohjainten hallinta | Deployment-, ReplicaSet-, Job- ym. ohjaimet |
| kubelet | solmun agentti: käynnistää podin kontit konttiajoympäristöllä |
| kube-proxy tai CNI | palveluiden osoitteet ja verkkoliikenne |

## Pod

*Pod* on Kubernetesin pienin yksikkö: yksi tai useampi kontti, jotka
jakavat verkkonimiavaruuden (sama IP-osoite, `localhost`) ja voivat
jakaa volyymeja. Useimmissa podeissa on yksi kontti. Lisäkontti
(*sidecar*) on perusteltu, kun se palvelee pääkonttia: lokien lähetys,
välityspalvelin, salaisuuksien päivitys.

Podeja ei yleensä luoda suoraan, koska yksittäistä podia ei luoda
uudelleen, jos sen solmu kaatuu. Podit luo jokin ylempi resurssi:
tilattomille palveluille Deployment, tilallisille StatefulSet,
kertaluonteisille töille Job.

## Nimiavaruus

Klusteri jaetaan *nimiavaruuksiin* (*namespace*; eri asia kuin luvun 2
ytimen nimiavaruudet): sovellukset, tiimit ja ympäristöt omiinsa.
Nimiavaruus rajaa nimet, oikeudet (RBAC), resurssikiintiöt ja
tietoturvaprofiilit:

```{.yaml tiedosto="esimerkit/k8s/00-nimiavaruus.yaml"}
```

Tunniste `pod-security.kubernetes.io/enforce: restricted` ottaa
käyttöön Kubernetesin tiukimman Pod Security -profiilin: nimiavaruuteen
ei hyväksytä podia, joka ajaa rootina, pyytää lisäoikeuksia tai jättää
seccomp-profiilin pois.

## Deployment

Käyntilaskurin rajapinta on tilaton, joten se on Deployment:

```{.yaml tiedosto="esimerkit/k8s/20-api.yaml" osa="deployment"}
```

- **`replicas` ja `selector`.** Deployment pitää yllä kaksi podia,
  joiden tunnisteet täsmäävät valitsimeen. Tunnisteet ja valitsimet
  ovat Kubernetesin tapa liittää resurssit toisiinsa; nimet eivät.
- **`template`.** Podin kuvaus. Kun pohja muuttuu (uusi kuva, uusi
  ympäristömuuttuja), Deployment luo uuden ReplicaSetin ja vaihtaa
  podit vähitellen.
- **`strategy`.** Rullaava päivitys: `maxSurge: 1` sallii yhden
  ylimääräisen podin päivityksen aikana, `maxUnavailable: 0` kieltää
  vähentämästä palvelevien podien määrää. Uusi pod otetaan
  liikenteeseen vasta, kun sen valmiustarkistus onnistuu (luku 8), ja
  vasta sitten vanha poistetaan.
- **`args`.** Korvaa kuvan `CMD`-osan (`ENTRYPOINT` on `python`).
- **`envFrom` ja `env`.** Asetukset ConfigMapista ja salaisuus
  Secretistä (luku 8).

Rullaavaa päivitystä seurataan ja tarvittaessa perutaan:

```text
kubectl -n kaynnit rollout status deployment/api
kubectl -n kaynnit rollout undo deployment/api
```

## Service

Podit tulevat ja menevät, ja niiden IP-osoitteet vaihtuvat. *Service*
antaa joukolle podeja pysyvän nimen ja osoitteen ja jakaa liikenteen
valmiille podeille:

```{.yaml tiedosto="esimerkit/k8s/20-api.yaml" osa="service"}
```

Klusterin sisällä palvelu löytyy DNS-nimellä `api.kaynnit.svc` tai
saman nimiavaruuden sisältä pelkällä nimellä `api`, kuten Composessa.
`targetPort: http` viittaa kontin nimettyyn porttiin, joten portin
numeron voi muuttaa yhdessä paikassa.

| Tyyppi | Näkyy |
|--------|-------|
| `ClusterIP` (oletus) | vain klusterin sisällä |
| `NodePort` | jokaisen solmun portissa |
| `LoadBalancer` | pilvipalvelun kuormantasaajan kautta |
| ilman osoitetta (`clusterIP: None`) | DNS palauttaa podien osoitteet (StatefulSet) |

Ulkoinen HTTP-liikenne tuodaan yleensä Ingressin tai Gateway API:n
kautta (luku 8), ei jokaiselle palvelulle omalla kuormantasaajalla.

## Manifestien tarkistus ilman klusteria

Esimerkkien testi tarkistaa kaikki manifestit Kubernetes 1.35:n
skeemoja vasten (`kubernetes-validate --strict`). Tiukka tila hylkää
myös tuntemattomat kentät, joten kirjoitusvirhe jää kiinni:

```{.yaml tiedosto="esimerkit/k8s-huono/kirjoitusvirhe.yaml"}
```

```{.tuloste tiedosto="esimerkit/k8s-huono/kirjoitusvirhe.odotettu"}
```

Klusteri hylkäisi tämän manifestin tai ohittaisi kentän, jolloin
palvelussa olisi yksi pod kolmen sijaan. Sama tarkistus kuuluu putkeen
ennen käyttöönottoa (`kubectl apply --dry-run=server` tekee sen
klusterin omalla tiedolla, myös laajennusresursseille).

## Oma klusteri kokeiluun

Manifestien ajaminen vaatii klusterin. Paikallinen klusteri syntyy
Dockerin päälle kindillä tai k3d:llä; kuva ladataan klusteriin suoraan
ilman rekisteriä:

```text
kind create cluster --name kaynnit
kind load docker-image kaynnit:1.0.0 --name kaynnit
kubectl apply -f k8s/
kubectl -n kaynnit get pods
kubectl -n kaynnit port-forward service/api 8080:80
```

Esimerkkien manifestit viittaavat kuvaan `ghcr.io/esimerkki/kaynnit`,
joten paikallista kokeilua varten kuvan nimi vaihdetaan
(`kubectl set image` tai Helm-arvo, luku 9). Tämän tutoriaalin testit
eivät käynnistä klusteria.

## Käytännössä

- **Kuvaa haluttu tila, älä anna komentoja.** Manifestit ovat
  versionhallinnassa, ja klusteriin viedään vain niitä
  (`kubectl apply`, Helm, GitOps). Käsin tehdyt muutokset
  (`kubectl edit`, `scale`) katoavat seuraavassa käyttöönotossa ja
  jättävät klusterin eri tilaan kuin kuvaus.
- **Tunnisteet yhtenäisiksi.** Suositellut `app.kubernetes.io/*`
  -tunnisteet (name, instance, version, part-of) tekevät resursseista
  työkaluille ja ihmisille luettavia.
- **Rullaava päivitys ilman katkoa vaatii kolme asiaa:**
  `maxUnavailable: 0`, rehellisen valmiustarkistuksen ja hallitun
  sammutuksen. Yksikin puuttuva tarkoittaa virheitä jokaisessa
  käyttöönotossa.
- **Tarkista manifestit ennen klusteria.** Skeemavalidointi ja
  palvelinpuolen kuivaharjoitus ovat halpoja verrattuna puoliksi
  onnistuneeseen käyttöönottoon.

## Itsearviointi

- Osaat selittää Kubernetesin deklaratiivisen mallin ja ohjainten
  toiminnan sekä klusterin pääosat.
- Osaat kirjoittaa Deploymentin ja Servicen ja kertoa, miten tunnisteet
  ja valitsimet liittävät ne toisiinsa.
- Osaat määrittää rullaavan päivityksen, joka ei katkaise palvelua, ja
  perua epäonnistuneen päivityksen.
- Osaat tarkistaa manifestit skeemoja vasten ilman klusteria ja
  käynnistää paikallisen klusterin kokeiluja varten.

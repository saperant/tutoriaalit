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

```{.dot otsikko="Ohjaussilmukka. Ohjain ei suorita käskyjä kerran vaan vertaa tiloja jatkuvasti, joten kadonnut pod korvataan ilman, että kukaan pyytää sitä."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.7;
  h [label="haluttu tila\n(manifesti, etcd)"];
  o [label="ohjain:\nvertaa", penwidth=1.6];
  t [label="todellinen tila\n(podit solmuilla)"];
  h -> o [label="lue"];
  t -> o [label="havainnoi"];
  o -> t [label="korjaa ero:\nluo, poista, päivitä"];
}
```

Klusterissa on *ohjaustaso* (*control plane*), joka tekee päätökset,
ja *solmut* (*node*), joilla kontit ajetaan:

```{.dot otsikko="Klusterin osat. Kaikki kulkee API-palvelimen kautta: ohjaimet ja ajoittaja lukevat ja kirjoittavat tilaa, ja jokaisen solmun kubelet käynnistää sille osoitetut podit."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.7;
  kubectl [label="kubectl,\nHelm, GitOps", shape=plain, style=""];
  subgraph cluster_o {
    label="ohjaustaso"; style="rounded"; margin=10;
    api [label="API-palvelin", penwidth=1.6];
    etcd [label="etcd", shape=cylinder, height=0.45];
    aj [label="ajoittaja"]; oh [label="ohjainten\nhallinta"];
    api -> etcd;
    aj -> api [constraint=false]; oh -> api [constraint=false];
  }
  subgraph cluster_s1 {
    label="solmu 1"; style="rounded"; margin=10;
    k1 [label="kubelet"]; p1 [label="podit", style="rounded,dashed"];
    k1 -> p1 [label="konttiajo-\nympäristö"];
  }
  subgraph cluster_s2 {
    label="solmu 2"; style="rounded"; margin=10;
    k2 [label="kubelet"]; p2 [label="podit", style="rounded,dashed"];
    k2 -> p2;
  }
  kubectl -> api;
  api -> k1 [dir=both]; api -> k2 [dir=both];
}
```

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
uudelleen, jos sen solmu kaatuu. Podit luo jokin ylempi resurssi,
*työkuorma* (*workload*), joka valitaan sen mukaan, miten podien
halutaan elävän:

| Työkuorma | Podit | Käyttö |
|-----------|-------|--------|
| Deployment | keskenään samanlaisia, vaihdettavissa | tilattomat palvelut (tämä luku) |
| StatefulSet | pysyvä nimi ja oma levy | tilalliset palvelut (luku 8) |
| DaemonSet | yksi jokaisella solmulla | lokien keruu, valvonta-agentit, verkko-osat |
| Job | ajetaan loppuun ja päättyy | migraatiot, eräajot |
| CronJob | Job aikataululla | varmuuskopiot, raportit |

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

```{.dot otsikko="Tunnisteet liittävät resurssit toisiinsa. Deployment omistaa ReplicaSetin, joka pitää podien määrän; Service ei tunne Deploymentia vaan valitsee podit tunnisteen perusteella ja ohjaa liikenteen niistä valmiille."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.8;
  d [label="Deployment api\nreplicas: 2"];
  rs [label="ReplicaSet\n(yksi per pohjan versio)"];
  p1 [label="pod\napp…/name: api\n10.244.1.7"]; p2 [label="pod\napp…/name: api\n10.244.2.4"];
  s [label="Service api\nClusterIP, portti 80"];
  a [label="kutsuja:\nhttp://api", shape=plain, style=""];
  d -> rs [label="luo"]; rs -> p1 [label="luo"]; rs -> p2;
  a -> s;
  s -> p1 [label="selector", style=dashed, constraint=false];
  s -> p2 [style=dashed, constraint=false];
}
```

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

Ulkoinen HTTP-liikenne tuodaan yleensä Gateway API:n tai Ingressin
kautta (luku 8), ei jokaiselle palvelulle omalla kuormantasaajalla.

## Podien verkko

Servicen toiminta nojaa klusterin verkkomalliin, jossa on kolme
sääntöä:

1. **Jokaisella podilla on oma IP-osoite**, ja jokainen pod tavoittaa
   jokaisen toisen podin suoraan ilman osoitteenmuunnosta, myös toisella
   solmulla. Tämän toteuttaa klusterin verkkoliitännäinen (*CNI*,
   esimerkiksi Calico tai Cilium) reitityksellä tai kapseloinnilla.
2. **Servicen osoite on virtuaalinen.** ClusterIP ei kuulu millekään
   liitännälle. Jokaisen solmun kube-proxy (tai CNI itse) kirjoittaa
   ytimeen säännöt, jotka ohjaavat ClusterIP:hen lähetetyn yhteyden
   jollekin palvelun valmiista podeista. Podien osoitteet ovat
   *EndpointSlice*-resursseissa, joita ohjaustaso päivittää sitä mukaa
   kuin podeja syntyy, valmistuu ja poistuu.
3. **Klusterin DNS** (CoreDNS) nimeää jokaisen Servicen: nimi
   `api.kaynnit.svc` on palvelu `api` nimiavaruudessa `kaynnit`. Podin
   DNS-asetukset täydentävät lyhyen nimen, joten `api` riittää saman
   nimiavaruuden sisällä.

Kutsu `http://api` kulkee siis näin: DNS palauttaa ClusterIP:n, ydin
vaihtaa kohteeksi yhden valmiin podin osoitteen, ja paketti reititetään
sen solmulle. Kun vianetsinnässä kysytään, miksi palvelu ei vastaa,
ketjun lenkit tarkistetaan tässä järjestyksessä (luku 8).

## Manifestien tarkistus ilman klusteria

Esimerkkien testi tarkistaa kaikki manifestit Kubernetes 1.35:n
skeemoja vasten (`kubernetes-validate --strict`); versio on testiin
kiinnitetty, ja omassa käytössä valitaan klusterin versio. Tiukka tila hylkää
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
- Osaat valita työkuormatyypin (Deployment, StatefulSet, DaemonSet, Job,
  CronJob) ja selittää, miten pyyntö kulkee palvelun nimestä podiin
  (DNS, ClusterIP, podin osoite).
- Osaat määrittää rullaavan päivityksen, joka ei katkaise palvelua, ja
  perua epäonnistuneen päivityksen.
- Osaat tarkistaa manifestit skeemoja vasten ilman klusteria ja
  käynnistää paikallisen klusterin kokeiluja varten.

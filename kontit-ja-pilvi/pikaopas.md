---
title: Kontit ja pilvi-infrastruktuuri
subtitle: Pikaopas · Docker · Compose · Kubernetes 1.35 · Helm 3
---

# Docker

| Tehtävä | Komento |
|---------|---------|
| rakenna kohdevaihe | `docker build --target ajo -t nimi:1.0.0 .` |
| aja ja poista | `docker run --rm -p 127.0.0.1:8080:8080 nimi:1.0.0` |
| rajat | `--memory 256m --cpus 0.5 --read-only` |
| lokit, kuori | `docker logs -f k`, `docker exec -it k sh` |
| kuvan tiedot | `docker image inspect`, `docker history` |
| kuva ilman kuorta | `docker debug k`, `kubectl debug` |
| siivous | `docker system prune` |

# Dockerfile

```{.dockerfile tiedosto="esimerkit/sovellus/Dockerfile" osa="ajo"}
```

- Peruskuva tagilla ja digestillä, riippuvuudet ennen koodia.
- `USER` numerona, kirjoitettavat hakemistot käyttäjälle.
- Exec-muoto: `ENTRYPOINT ["…"]`, SIGTERM käsiteltävä.
- `.dockerignore` aina; ei salaisuuksia `ENV`- eikä `ARG`-arvoihin.
- `hadolint Dockerfile` ennen rakennusta.

# Compose

| Tehtävä | Komento |
|---------|---------|
| käynnistä terveenä | `docker compose up -d --wait` |
| rakenna uudelleen | `docker compose up -d --build` |
| tila, lokit | `docker compose ps`, `docker compose logs -f api` |
| lopullinen asetus | `docker compose config` |
| pysäytä ja poista data | `docker compose down -v` |

```{.yaml tiedosto="esimerkit/compose.yaml" osa="palvelut"}
```

# Kubernetes

| Resurssi | Käyttö |
|----------|--------|
| Deployment | tilaton palvelu, rullaava päivitys |
| StatefulSet | pysyvä nimi ja levy |
| Job, CronJob | kertaluonteinen ja ajastettu työ |
| Service | pysyvä nimi ja kuormantasaus |
| Ingress, Gateway | ulkoinen HTTP-liikenne |
| ConfigMap, Secret | asetukset, salaisuudet |
| HPA, PDB | skaalaus, huoltojen rajaus |
| NetworkPolicy | podien välinen liikenne |

| Tehtävä | Komento |
|---------|---------|
| ota käyttöön | `kubectl apply -f k8s/` |
| tila | `kubectl -n ns get pods,svc,deploy` |
| miksi ei käynnisty | `kubectl -n ns describe pod p`, `get events` |
| lokit | `kubectl -n ns logs -f deploy/api` |
| päivitys | `kubectl -n ns rollout status/undo deploy/api` |
| yhteys | `kubectl -n ns port-forward svc/api 8080:80` |
| tarkistus | `kubectl apply --dry-run=server -f k8s/` |

```{.yaml tiedosto="esimerkit/k8s/20-api.yaml" osa="tarkistukset"}
```

# Helm

| Tehtävä | Komento |
|---------|---------|
| tarkista | `helm lint kaavio -f arvot.yaml` |
| renderöi | `helm template nimi kaavio -f arvot.yaml` |
| asenna/päivitä | `helm upgrade --install nimi kaavio --atomic --wait` |
| historia, peruminen | `helm history nimi`, `helm rollback nimi 3` |

# Sudenkuopat

| Oire | Syy |
|------|-----|
| `Permission denied` volyymissa | hakemisto rootin; luo ja `chown` kuvassa tai `fsGroup` |
| pysäytys kestää 10–30 s | kuorimuoto tai SIGTERM käsittelemättä |
| virhekoodi 137 | muistiraja ylittyi (OOM) |
| `CrashLoopBackOff` | ohjelma kaatuu; `kubectl logs --previous` |
| `ImagePullBackOff` | kuvan nimi, tagi tai rekisterin tunnukset |
| pod ei saa liikennettä | valmiuskoetin epäonnistuu tai valitsin ei täsmää |
| asetus ei päivity | ympäristömuuttuja luetaan vain käynnistyksessä |
| HPA ei skaalaa | suoritinpyyntö puuttuu |

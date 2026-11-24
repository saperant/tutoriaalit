# Kontit ja pilvi

Kontit ja niiden ajaminen pilvessä: säiliökuvat Dockerfilellä, pienet
ja turvalliset kuvat, konttiin sopiva sovellus, Compose, Kubernetes,
Helm ja GitOps, infrastruktuuri koodina sekä CI/CD-putket. Valmis
dokumentti:
[kontit-ja-pilvi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kontit-ja-pilvi.pdf),
pikaopas:
[kontit-ja-pilvi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kontit-ja-pilvi-pikaopas.pdf).

Esitiedot: taito *Tietoverkot* sekä komentorivin peruskäyttö.

## Sisältö

1. Johdanto – esimerkkisovellus, mitä testataan ja miten
2. Mikä kontti on – nimiavaruudet, cgroups, kuvat ja kerrokset
3. Säiliökuva Dockerfilellä – monivaiheinen rakennus, ei-root,
   exec-muoto ja sammutus, välimuisti
4. Pienet ja turvalliset kuvat – distroless, staattinen binääri,
   hadolint, skannaus ja SBOM
5. Sovellus konttiin sopivaksi – twelve-factor, elävyys ja valmius
6. Monipalvelusovellus Composella
7. Kubernetes: podit, Deploymentit ja palvelut
8. Kubernetes: asetukset, tila ja tuotantokunto – koettimet,
   resurssit, StatefulSet, Ingress, verkkopolitiikka, käytännöt koodina
9. Helm ja GitOps
10. Infrastruktuuri koodina
11. CI/CD-putket palveluille
12. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

Hakemistossa `esimerkit/`:

- `sovellus/` – käyntilaskuri (Python): api, laskuri, testit ja
  Dockerfile
- `staattinen/` – Go-palvelu distroless-kuvassa
- `huono/` – Dockerfile tavallisine virheineen
- `compose.yaml` – sovellus Composella
- `k8s/`, `k8s-huono/` – Kubernetes-manifestit ja virheelliset
  esimerkit
- `helm/kaynnit/` – Helm-kaavio
- `politiikka.py` – käytännöt koodina
- `iac/` – infrastruktuuri koodina pienoismallina
- `ci/palvelu.yml` – GitHub Actions -putki

```text
make -C esimerkit              # kaikki tarkistukset ja ajot
make -C esimerkit staattiset   # ilman Dockeria
make -C esimerkit docker       # kuvat, Compose ja Helm
```

Kuvien rakennus ja ajo sekä Helm-kaavion renderöinti vaativat Dockerin;
ilman sitä ne ohitetaan ilmoituksella. Kubernetes-manifestit
tarkistetaan skeemoja vasten, mutta niitä ei ajeta klusterissa.

Lisenssi: CC BY-SA 4.0.

# Kontit ja pilvi-infrastruktuuri

Kontit ja niiden ajaminen pilvessä: konttikuvat Dockerfilellä, pienet
ja turvalliset kuvat, konttiin sopiva sovellus, Compose, Kubernetes,
Helm ja GitOps, infrastruktuuri koodina sekä CI/CD-putket. Valmis
dokumentti:
[kontit-ja-pilvi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kontit-ja-pilvi.pdf),
pikaopas:
[kontit-ja-pilvi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/kontit-ja-pilvi-pikaopas.pdf).

Esitiedot: taito *Tietoverkot* (ja sen esitietona *Komentorivi ja Linux*).

## Sisältö

1. Johdanto – esimerkkisovellus, mitä testataan ja miten
2. Mikä kontti on – nimiavaruudet, cgroups, kuvat ja kerrokset
3. Konttikuva Dockerfilellä – monivaiheinen rakennus, ei-root,
   exec-muoto ja sammutus, välimuisti
4. Pienet ja turvalliset kuvat – distroless, staattinen binääri,
   hadolint, skannaus ja SBOM
5. Sovellus konttiin sopivaksi – twelve-factor, elävyys ja valmius
6. Monipalvelusovellus Composella
7. Kubernetes: podit, Deploymentit ja palvelut – ohjaussilmukka,
   klusterin osat, työkuormatyypit, podien verkko
8. Kubernetes: asetukset, tila ja tuotantokunto – koettimet,
   resurssit, StatefulSet, Gateway API ja Ingress, verkkopolitiikka,
   käytännöt koodina, vianetsintä
9. Helm ja GitOps
10. Infrastruktuuri koodina
11. CI/CD-putket palveluille
12. Lopuksi – nyrkkisäännöt, mallit, jatkotaidot, lähteet

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
- `ci/palvelu.yml` – GitHub Actions -putki; `ci/putki_verkko.py`
  piirtää siitä luvun 11 kaavion

```text
make -C esimerkit              # kaikki tarkistukset ja ajot
make -C esimerkit staattiset   # ilman Dockeria
make -C esimerkit docker       # kuvat, Compose ja Helm
```

Kuvien rakennus ja ajo sekä Helm-kaavion renderöinti vaativat Dockerin;
ilman sitä ne ohitetaan ilmoituksella. Kubernetes-manifestit
tarkistetaan skeemoja vasten, mutta niitä ei ajeta klusterissa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
